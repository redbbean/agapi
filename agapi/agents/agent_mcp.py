"""
agent_mcp.py
------------
LangGraph agent that consumes tools via MCP (Model Context Protocol).

Compared to agent_langgraph.py, tools are NOT imported directly from
functions.py. Instead, agent_mcp_server.py is launched as a subprocess
and its tools are discovered at runtime via the MCP stdio transport.
This is the key architectural difference: the agent loop and tool
implementations run in separate processes.

What this tests:
- Whether MCP's JSON-RPC serialisation changes how the model perceives
  tool schemas (vs direct Pydantic schemas)
- Whether structured MCP error responses affect agent behaviour
- IPC overhead vs direct Python call latency

Install:
    pip install mcp langchain-mcp-adapters langchain langchain-openai langgraph

Usage:
    from agapi.agents.agent_mcp import AGAPIAgentMCP
    agent = AGAPIAgentMCP()
    response, tools = agent.query_sync_benchmark("What is the bandgap of GaN?")
"""

import asyncio
import json
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    trim_messages,
)
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

try:
    from dotenv import load_dotenv
    for _parent in Path(__file__).resolve().parents:
        _env = _parent / ".env"
        if _env.exists():
            load_dotenv(_env)
            break
except ImportError:
    pass

from .config import AgentConfig
from .agent import SYSTEM_PROMPT

# Path to the MCP server script (same directory as this file)
_SERVER_PATH = Path(__file__).parent / "agent_mcp_server.py"


# ─────────────────────────────────────────────────────────────────────────────
# Main agent class
# ─────────────────────────────────────────────────────────────────────────────

class AGAPIAgentMCP:
    """
    AGAPI agent using LangGraph + MCP tool transport.

    Supports two MCP server modes:
      - local (default): spawns agent_mcp_server.py as a subprocess via stdio.
        Tools are the same 28 AGAPI functions, run in-process on the same machine.
      - remote: connects to a running MCP server over HTTP/SSE (e.g. the public
        AtomGPT MCP server at https://atomgpt.org/mcp). No subprocess needed;
        the server is always-on and network-accessible.

    Usage:
        # Local subprocess (default)
        agent = AGAPIAgentMCP()

        # Remote AtomGPT MCP server
        agent = AGAPIAgentMCP(server_url="https://atomgpt.org/mcp")

        response, tools_called = agent.query_sync_benchmark("What is GaN's bandgap?")
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = None,
        max_iterations: int = None,
        timeout: int = None,
        api_base: str = None,
        system_prompt: str = None,
        server_url: str = None,
    ):
        self.api_key        = api_key        or AgentConfig.DEFAULT_API_KEY
        self.model          = model          or AgentConfig.DEFAULT_MODEL
        self.temperature    = temperature    if temperature is not None else AgentConfig.DEFAULT_TEMPERATURE
        self.max_iterations = max_iterations or AgentConfig.DEFAULT_MAX_ITERATIONS
        self.timeout        = timeout        or AgentConfig.DEFAULT_TIMEOUT
        self.api_base       = api_base       or AgentConfig.API_BASE
        self.system_prompt  = system_prompt  or SYSTEM_PROMPT
        # None → local subprocess; a URL string → remote SSE server
        self.server_url     = server_url

        self._llm = ChatOpenAI(
            base_url=f"{self.api_base}/api",
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
        )

        self._memory = MemorySaver()
        self._graph  = None   # built after MCP connection is ready
        self._mcp_client = None

        self.last_intermediate_steps: List[Dict[str, Any]] = []

        # Start a persistent background event loop in a daemon thread.
        # All async work (MCP connection + graph invocations) runs here.
        self._loop   = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._loop.run_forever, daemon=True, name="mcp-agent-loop"
        )
        self._thread.start()

        # Connect to MCP server synchronously before returning from __init__
        future = asyncio.run_coroutine_threadsafe(self._connect(), self._loop)
        future.result(timeout=30)   # raise if server doesn't start within 30 s

    # ── Async setup ────────────────────────────────────────────────────────────

    async def _connect(self):
        """
        Connect to the MCP server (local subprocess or remote SSE) and build
        the LangGraph create_react_agent. Called once from __init__.
        """
        from langchain_mcp_adapters.client import MultiServerMCPClient

        if self.server_url:
            # Remote MCP server over Streamable HTTP — no subprocess needed.
            # AtomGPT requires the AGAPI key as a Bearer token.
            server_config = {
                "agapi": {
                    "url": self.server_url,
                    "transport": "streamable_http",
                    "headers": {"Authorization": f"Bearer {self.api_key}"},
                }
            }
        else:
            # Local MCP server spawned as a subprocess via stdio
            server_config = {
                "agapi": {
                    "command": sys.executable,
                    "args":    [str(_SERVER_PATH)],
                    "transport": "stdio",
                }
            }

        self._mcp_client = MultiServerMCPClient(server_config)
        raw_tools = await self._mcp_client.get_tools()
        tools = [self._stringify_tool(t) for t in raw_tools]

        self._graph = create_react_agent(
            model=self._llm,
            tools=tools,
            prompt=self._build_state_modifier(),
            checkpointer=self._memory,
        )

    @staticmethod
    def _stringify_tool(tool):
        """
        Wrap an MCP-derived tool so its output is always a plain string.

        langchain-mcp-adapters returns tool results as a list of MCP
        TextContent objects (e.g. [TextContent(type='text', text='...')]).
        The AGAPI server rejects ToolMessages whose content is not a string,
        so we normalise here before the result enters the LangGraph state.
        """
        from langchain_core.tools import StructuredTool

        original_coroutine = tool.coroutine

        def _to_str(result):
            if isinstance(result, str):
                return result
            if isinstance(result, list):
                parts = []
                for item in result:
                    if isinstance(item, dict):
                        parts.append(item.get("text", json.dumps(item)))
                    else:
                        text = getattr(item, "text", None)
                        parts.append(text if text is not None else str(item))
                return "\n".join(parts)
            if isinstance(result, dict):
                return json.dumps(result)
            return str(result)

        async def wrapped(**kwargs):
            result = await original_coroutine(**kwargs)
            return _to_str(result)

        return StructuredTool(
            name=tool.name,
            description=tool.description,
            args_schema=tool.args_schema,
            coroutine=wrapped,
            response_format="content",
        )

    def _build_state_modifier(self):
        """Prepend system prompt and trim message history (mirrors agent_langgraph.py)."""
        system_msg = SystemMessage(content=self.system_prompt)

        def modifier(state):
            trimmed = trim_messages(
                state["messages"],
                strategy="last",
                token_counter=len,
                max_tokens=18,
                start_on="human",
                include_system=False,
            )
            return [system_msg] + trimmed

        return modifier

    # ── Async query ────────────────────────────────────────────────────────────

    async def _ainvoke(self, query: str) -> dict:
        config = {
            "configurable": {"thread_id": str(uuid4())},
            "recursion_limit": self.max_iterations * 4 + 1,
        }
        return await self._graph.ainvoke(
            {"messages": [HumanMessage(content=query)]},
            config=config,
        )

    # ── Result extraction (same logic as agent_langgraph.py) ──────────────────

    def _extract_steps(self, result: dict) -> List[Dict[str, Any]]:
        tool_results: Dict[str, str] = {}
        for msg in result.get("messages", []):
            if isinstance(msg, ToolMessage):
                tool_results[msg.tool_call_id] = msg.content

        steps = []
        for msg in result.get("messages", []):
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    steps.append({
                        "tool":   tc["name"],
                        "args":   tc["args"],
                        "result": tool_results.get(tc["id"]),
                    })
        return steps

    @staticmethod
    def _extract_text(content) -> str:
        if not content:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [b["text"] if isinstance(b, dict) and b.get("type") == "text"
                     else b for b in content if isinstance(b, (str, dict))]
            return " ".join(str(p) for p in parts if p)
        return str(content)

    def _get_final_text(self, result: dict) -> str:
        for msg in reversed(result.get("messages", [])):
            if isinstance(msg, AIMessage):
                candidate = self._extract_text(msg.content)
                if candidate.strip():
                    return candidate
        return "No response generated."

    # ── Public API ─────────────────────────────────────────────────────────────

    def query_sync_benchmark(self, query: str) -> tuple:
        """
        Benchmark interface — runs query and returns (response_text, tools_called).

        Returns:
            response_text (str):  Final answer from the agent.
            tools_called  (list): Ordered list of tool names called.
        """
        future = asyncio.run_coroutine_threadsafe(self._ainvoke(query), self._loop)
        result = future.result(timeout=self.timeout * 2)

        steps        = self._extract_steps(result)
        self.last_intermediate_steps = steps
        tools_called = [s["tool"] for s in steps]
        final_text   = self._get_final_text(result)

        return final_text, tools_called

    def query_sync(
        self,
        query: str,
        verbose: bool = False,
        render_html: bool = False,
        **kwargs,
    ) -> str:
        """Original-style synchronous interface."""
        response, _ = self.query_sync_benchmark(query)
        return response

    # ── Cleanup ────────────────────────────────────────────────────────────────

    def close(self):
        """Stop the background event loop (MCP client manages its own lifecycle)."""
        self._loop.call_soon_threadsafe(self._loop.stop)

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass