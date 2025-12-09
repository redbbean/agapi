from agapi.agents.config import AgentConfig
from typing import Dict, Any
import httpx

from .config import AgentConfig


class AGAPIClient:
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
