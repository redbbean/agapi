import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    # Walk up from this file to find a .env in the Benchmarking repo root
    for parent in Path(__file__).resolve().parents:
        env_file = parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            break
except ImportError:
    pass


class AgentConfig:
    """Configuration constants for AGAPI Agent"""

    # API Configuration
    API_BASE = "https://atomgpt.org"
    DEFAULT_API_KEY = os.environ.get("AGAPI_KEY", "sk-")

    # Model Configuration
    DEFAULT_MODEL = "openai/gpt-oss-20b"
    DEFAULT_TEMPERATURE = 0.1
    DEFAULT_MAX_ITERATIONS = 15

    # Network Configuration
    DEFAULT_TIMEOUT = 300
