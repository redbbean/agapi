import os
import io
import json
from typing import Optional, Dict, Any, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# from dotenv import load_dotenv

DEFAULT_BASE_URL = "https://atomgpt.org"


class _SessionFactory:
    @staticmethod
    def build_session(
        timeout: int = 120, total_retries: int = 3
    ) -> requests.Session:
        s = requests.Session()
        retries = Retry(
            total=total_retries,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(
                ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]
            ),
        )
        adapter = HTTPAdapter(max_retries=retries)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        s.request_timeout = timeout
        return s


class Agapi:
    """Minimal Python client for AtomGPT.org endpoints."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 120,
        retries: int = 3,
        session: Optional[requests.Session] = None,
    ):
        # load_dotenv()
        if not api_key:
            self.api_key = os.getenv("AGAPI_API_KEY")
        else:
            self.api_key = api_key
        if not self.api_key:
            raise ValueError(
                "Missing AGAPI_API_KEY. Set env var or pass api_key=..."
            )

        self.base_url = (
            base_url or os.getenv("AGAPI_BASE_URL") or DEFAULT_BASE_URL
        ).rstrip("/")
        self.timeout = timeout
        self.session = session or _SessionFactory.build_session(
            timeout=timeout, total_retries=retries
        )

    # ---- helpers ----
    def _headers(
        self,
        content_type: Optional[str] = None,
        accept: str = "application/json",
    ) -> Dict[str, str]:
        h = {
            "Authorization": f"Bearer {self.api_key}",
            "accept": accept,
        }
        if content_type:
            h["Content-Type"] = content_type
        return h

    def _post_json(self, path: str, payload: Dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"
        resp = self.session.post(
            url,
            headers=self._headers(content_type="application/json"),
            json=payload,
            timeout=self.timeout,
        )
        return self._handle_response(resp)

    def _post_multipart(
        self,
        path: str,
        files: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None,
        accept: str = "application/json",
    ) -> Any:
        url = f"{self.base_url}{path}"
        resp = self.session.post(
            url,
            headers=self._headers(accept=accept),
            files=files,
            data=data or {},
            timeout=self.timeout,
        )
        return self._handle_response(resp, accept=accept)

    def _post_raw(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        accept: str = "application/json",
    ) -> Any:
        url = f"{self.base_url}{path}"
        resp = self.session.post(
            url,
            headers=self._headers(accept=accept),
            params=params or {},
            data=data or b"",
            timeout=self.timeout,
        )
        return self._handle_response(resp, accept=accept)

    def _handle_response(
        self, resp: requests.Response, accept: str = "application/json"
    ) -> Any:
        if resp.status_code >= 400:
            # Try to extract JSON error if available
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise requests.HTTPError(
                f"HTTP {resp.status_code}: {detail}", response=resp
            )

        if accept == "application/json":
            return resp.json()
        else:
            return resp.content

    # ---- Endpoints ----

    # /jarvis_dft/query (POST JSON)
    def jarvis_dft_query(
        self, *, formula: Optional[str] = None, search: Optional[str] = None
    ) -> Any:
        """Query JARVIS-DFT:
        - by formula: jarvis_dft_query(formula="MoS2")
        - by search:  jarvis_dft_query(search="-Mo-S")
        """
        payload: Dict[str, Any] = {}
        if formula is not None:
            payload["formula"] = formula
        if search is not None:
            payload["search"] = search
        if not payload:
            raise ValueError("Provide formula= or search=")
        return self._post_json("/jarvis_dft/query", payload)

    # /alignn/query (multipart)
    def alignn_query(
        self,
        *,
        file_path: Optional[str] = None,
        poscar_string: Optional[str] = None,
    ) -> Any:
        files = {}
        data = {}
        if file_path:
            files["file"] = (
                os.path.basename(file_path),
                open(file_path, "rb"),
            )
        if poscar_string is not None:
            data["poscar_string"] = poscar_string
        if not files and "poscar_string" not in data:
            raise ValueError("Provide file_path= or poscar_string=")
        try:
            return self._post_multipart(
                "/alignn/query", files=files, data=data
            )
        finally:
            # close file handles if opened
            if "file" in files and hasattr(files["file"][1], "close"):
                files["file"][1].close()

    # /alignn_ff/query (multipart)
    def alignn_ff_query(
        self,
        *,
        file_path: Optional[str] = None,
        poscar_string: Optional[str] = None,
    ) -> Any:
        files = {}
        data = {}
        if file_path:
            files["file"] = (
                os.path.basename(file_path),
                open(file_path, "rb"),
            )
        if poscar_string is not None:
            data["poscar_string"] = poscar_string
        if not files and "poscar_string" not in data:
            raise ValueError("Provide file_path= or poscar_string=")
        try:
            return self._post_multipart(
                "/alignn_ff/query", files=files, data=data
            )
        finally:
            if "file" in files and hasattr(files["file"][1], "close"):
                files["file"][1].close()

    # /protein_fold/query (POST with query params, returns json or zip)
    def protein_fold_query(
        self, *, sequence: str, format: str = "json"
    ) -> Any:
        if not sequence:
            raise ValueError("sequence is required")
        accept = "application/json" if format != "zip" else "application/zip"
        return self._post_raw(
            "/protein_fold/query",
            params={"sequence": sequence, "format": format},
            data=b"",
            accept=accept,
        )

    def ask(self, question: str, model: str = "openai/gpt-oss-20b") -> str:
        """Simple question-answer interface."""
        from openai import OpenAI

        client = OpenAI(
            api_key=self.api_key, base_url="https://atomgpt.org/api"
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}],
        )
        resp = resp.choices[0].message.content
        return resp

    # /pxrd/query (multipart)
    def pxrd_query(
        self,
        *,
        file_path: Optional[str] = None,
        body_string: Optional[str] = None,
    ) -> Any:
        files = {}
        data = {}
        if file_path:
            files["file"] = (
                os.path.basename(file_path),
                open(file_path, "rb"),
            )
        if body_string is not None:
            data["body_string"] = body_string
        if not files and "body_string" not in data:
            raise ValueError("Provide file_path= or body_string=")
        try:
            return self._post_multipart("/pxrd/query", files=files, data=data)
        finally:
            if "file" in files and hasattr(files["file"][1], "close"):
                files["file"][1].close()
