from agapi.agents.config import AgentConfig
from typing import Dict, Any
import httpx

from .config import AgentConfig

# In agapi/agents/client.py


class AGAPIClient:
    def __init__(
        self,
        api_key: str,
        api_base: str = "https://atomgpt.org",
        timeout: int = 60,
    ):
        self.api_key = api_key
        self.api_base = api_base
        self.timeout = timeout

    def request(self, endpoint: str, params: dict = None, method: str = "GET"):
        """
        Make HTTP request to API

        Args:
            endpoint: API endpoint (e.g., "generate_interface")
            params: Query parameters or request body
            method: HTTP method ("GET" or "POST")

        Returns:
            Response data (dict for JSON, str for text/plain)
        """
        import httpx

        url = f"{self.api_base}/{endpoint}"
        headers = {}

        # Add API key to params (not headers) for AGAPI
        if params is None:
            params = {}
        params["APIKEY"] = self.api_key

        try:
            if method == "GET":
                response = httpx.get(url, params=params, timeout=self.timeout)
            else:
                response = httpx.post(
                    url, json=params, headers=headers, timeout=self.timeout
                )

            response.raise_for_status()

            # Check content type to decide parsing
            content_type = response.headers.get("content-type", "")

            if "application/json" in content_type:
                return response.json()
            elif "text/plain" in content_type or "text/html" in content_type:
                return response.text
            else:
                # Try JSON first, fall back to text
                try:
                    return response.json()
                except:
                    return response.text

        except httpx.HTTPStatusError as e:
            raise Exception(
                f"API error ({e.response.status_code}): {e.response.text}"
            )
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")


class AGAPIClientX:
    """Low-level client for AGAPI requests"""

    def __init__(
        self, api_key: str = None, timeout: int = None, api_base: str = None
    ):
        self.api_key = api_key or AgentConfig.DEFAULT_API_KEY
        self.timeout = timeout or AgentConfig.DEFAULT_TIMEOUT
        self.api_base = api_base or AgentConfig.API_BASE

    def request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make GET request to AGAPI"""
        params["APIKEY"] = self.api_key
        url = f"{self.api_base}/{endpoint}"

        try:
            with httpx.Client(
                verify=True, timeout=self.timeout
            ) as http_client:
                response = http_client.get(url, params=params)

            if response.status_code != 200:
                raise Exception(
                    f"API error ({response.status_code}): {response.text}"
                )

            return response.json()

        except httpx.TimeoutException:
            raise Exception(f"Request timeout after {self.timeout}s")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
