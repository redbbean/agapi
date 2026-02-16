"""
AGAPI - Python client for AtomGPT.org API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A comprehensive Python client for interacting with AtomGPT.org endpoints.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, Union, List, Tuple
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

__version__ = "2026.2.6"
__all__ = ["Agapi", "AgapiError", "AgapiAuthError", "AgapiValidationError", "AgapiTimeoutError", "AgapiServerError"]

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://atomgpt.org"
DEFAULT_TIMEOUT = 120  
DEFAULT_RETRIES = 3


# ============================================================================
# Exceptions
# ============================================================================

class AgapiError(Exception):
    """Base exception for AGAPI errors."""
    pass


class AgapiAuthError(AgapiError):
    """Authentication/authorization error."""
    pass


class AgapiValidationError(AgapiError):
    """Request validation error."""
    pass


class AgapiTimeoutError(AgapiError):
    """Request timeout error."""
    pass


class AgapiServerError(AgapiError):
    """Server-side error (5xx)."""
    pass


# ============================================================================
# Session Factory
# ============================================================================

class _SessionFactory:
    """Factory for creating configured requests sessions."""
    
    @staticmethod
    def build_session(
        timeout: int = DEFAULT_TIMEOUT,
        total_retries: int = DEFAULT_RETRIES,
        backoff_factor: float = 0.5,
    ) -> requests.Session:
        """Build a requests Session with retry logic."""
        session = requests.Session()
        
        retries = Retry(
            total=total_retries,
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset([
                "GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"
            ]),
        )
        
        adapter = HTTPAdapter(
            max_retries=retries,
            pool_connections=10,
            pool_maxsize=20,
        )
        
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session


# ============================================================================
# Main Client
# ============================================================================

class Agapi:
    """Python client for AtomGPT.org API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        session: Optional[requests.Session] = None,
        verbose: bool = False,
    ):
        # Setup API key
        self.api_key = api_key or os.getenv("AGAPI_API_KEY") or os.getenv("ATOMGPT_API_KEY")
        if not self.api_key:
            raise AgapiAuthError(
                "Missing API key. Provide api_key= or set AGAPI_API_KEY environment variable. "
                "Get your key at: https://atomgpt.org"
            )

        # Setup base URL
        self.base_url = (
            base_url or os.getenv("AGAPI_BASE_URL") or DEFAULT_BASE_URL
        ).rstrip("/")
        
        # Setup session
        self.timeout = timeout
        self.session = session or _SessionFactory.build_session(
            timeout=timeout, 
            total_retries=retries
        )
        
        # Configure logging
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        
        logger.debug(f"Initialized AGAPI client: base_url={self.base_url}")

    # ========================================================================
    # Internal helpers
    # ========================================================================

    def _headers(
        self,
        content_type: Optional[str] = None,
        accept: str = "application/json",
    ) -> Dict[str, str]:
        """Build request headers."""
        headers = {
            "Accept": accept,
            "User-Agent": f"agapi-python/{__version__}",
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        return f"{self.base_url}{path}"

    def _add_api_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add API key to parameters."""
        if params is None:
            params = {}
        params["APIKEY"] = self.api_key  # CRITICAL FIX: API key goes in query params
        return params

    def _handle_response(
        self, 
        resp: requests.Response, 
        accept: str = "application/json"
    ) -> Any:
        """Handle API response and raise appropriate exceptions."""
        # Success
        if 200 <= resp.status_code < 300:
            if accept == "application/json":
                try:
                    return resp.json()
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON: {resp.text[:500]}")
                    raise AgapiError(f"Invalid JSON response: {e}")
            else:
                return resp.content
        
        # Extract error details
        try:
            error_detail = resp.json()
            if isinstance(error_detail, dict):
                message = error_detail.get("detail", str(error_detail))
            else:
                message = str(error_detail)
        except:
            message = resp.text[:500]
        
        # Raise appropriate exception
        if resp.status_code == 401 or resp.status_code == 403:
            raise AgapiAuthError(f"Authentication failed: {message}")
        elif resp.status_code == 400 or resp.status_code == 422:  # Added 422
            raise AgapiValidationError(f"Invalid request: {message}")
        elif resp.status_code == 404:
            raise AgapiError(f"Resource not found: {message}")
        elif resp.status_code >= 500:
            raise AgapiServerError(f"Server error ({resp.status_code}): {message}")
        else:
            raise AgapiError(f"HTTP {resp.status_code}: {message}")

    def _get(
        self, 
        path: str, 
        params: Optional[Dict[str, Any]] = None,
        accept: str = "application/json",
    ) -> Any:
        """Execute GET request."""
        url = self._build_url(path)
        params = self._add_api_key(params)  # CRITICAL FIX
        logger.debug(f"GET {url} with params={params}")
        
        try:
            resp = self.session.get(
                url,
                headers=self._headers(accept=accept),
                params=params,
                timeout=self.timeout,
            )
        except requests.Timeout as e:
            raise AgapiTimeoutError(f"Request timed out after {self.timeout}s: {e}")
        except requests.RequestException as e:
            raise AgapiError(f"Request failed: {e}")
        
        return self._handle_response(resp, accept=accept)

    def _post_json(
        self,
        path: str,
        payload: Dict[str, Any],
        accept: str = "application/json",
    ) -> Any:
        """Execute POST request with JSON payload."""
        url = self._build_url(path)

        # CRITICAL: Add API key to the JSON body for POST requests
        payload_with_key = {**payload, "APIKEY": self.api_key}

        logger.debug(f"POST {url} with payload keys={list(payload.keys())}")

        try:
            resp = self.session.post(
                url,
                headers=self._headers(content_type="application/json", accept=accept),
                json=payload_with_key,  # API key goes in body
                timeout=self.timeout,
            )
        except requests.Timeout as e:
            raise AgapiTimeoutError(f"Request timed out after {self.timeout}s: {e}")
        except requests.RequestException as e:
            raise AgapiError(f"Request failed: {e}")

        return self._handle_response(resp, accept=accept)


    def _post_multipart(
        self,
        path: str,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        accept: str = "application/json",
    ) -> Any:
        """Execute POST request with multipart/form-data."""
        url = self._build_url(path)
        
        # Add API key to form data
        if data is None:
            data = {}
        data["APIKEY"] = self.api_key
        
        logger.debug(f"POST {url} (multipart)")
        
        try:
            resp = self.session.post(
                url,
                headers=self._headers(accept=accept),
                files=files or {},
                data=data,
                timeout=self.timeout,
            )
        except requests.Timeout as e:
            raise AgapiTimeoutError(f"Request timed out after {self.timeout}s: {e}")
        except requests.RequestException as e:
            raise AgapiError(f"Request failed: {e}")
        
        return self._handle_response(resp, accept=accept)
    # ========================================================================
    # Database Queries
    # ========================================================================


    def jarvis_dft_query(
        self,
        *,
        formula: Optional[str] = None,
        jid: Optional[str] = None,
        elements: Optional[Union[str, List[str]]] = None,
        propranges: Optional[Dict[str, Dict[str, float]]] = None,
        limit: int = 100,
        offset: int = 0,
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Query JARVIS-DFT database."""
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }

        if formula:
            params["formula"] = formula
        if jid:
            params["jid"] = jid
        if elements:
            if isinstance(elements, list):
                params["elements"] = ",".join(elements)
            else:
                params["elements"] = elements
        if propranges:
            # Convert propranges dict to query param format
            params["propranges"] = json.dumps(propranges)
        if fields:
            if isinstance(fields, list):
                params["fields"] = ",".join(fields)
            else:
                params["fields"] = fields

        if not any([formula, jid, elements, propranges]):
            raise AgapiValidationError(
                "Provide at least one filter: formula, jid, elements, or propranges"
            )

        # FIXED: Use GET instead of POST
        return self._get("/jarvis_dft/query", params=params)
    def jarvis_dft_columns(self) -> List[str]:
        """Get available JARVIS-DFT column names."""
        result = self._get("/jarvis_dft/columns")
        return result.get("columns", [])

    def materials_project_query(
        self,
        *,
        formula: str,
        page_limit: int = 100,
        page_offset: int = 0,
        fields: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query Materials Project via OPTIMADE."""
        params = {
            "formula": formula,
            "page_limit": min(page_limit, 500),
            "page_offset": page_offset,
        }
        if fields:
            params["fields"] = fields
        
        return self._get("/mp/query", params=params)

    # ========================================================================
    # ML Predictions
    # ========================================================================

    def alignn_predict(
        self,
        *,
        jid: Optional[str] = None,
        poscar: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """Get ALIGNN property predictions."""
        if jid:
            return self._get("/alignn/query", params={"jid": jid})
        
        if file_path:
            file_path = Path(file_path)
            if not file_path.exists():
                raise AgapiValidationError(f"File not found: {file_path}")
            with open(file_path, "r") as f:
                poscar = f.read()
        
        if poscar:
            return self._get("/alignn/query", params={"poscar": poscar})
        
        raise AgapiValidationError("Provide jid, poscar, or file_path")

    def alignn_ff_energy(
        self,
        *,
        poscar: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """Calculate energy, forces, and stress with ALIGNN-FF."""
        if file_path:
            file_path = Path(file_path)
            if not file_path.exists():
                raise AgapiValidationError(f"File not found: {file_path}")
            with open(file_path, "r") as f:
                poscar = f.read()
        
        if not poscar:
            raise AgapiValidationError("Provide poscar or file_path")
        
        return self._get("/alignn_ff/query", params={"poscar": poscar})

    def alignn_ff_relax(
        self,
        *,
        poscar: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        fmax: float = 0.05,
        steps: int = 50,
    ) -> str:
        """Relax structure with ALIGNN-FF."""
        if file_path:
            file_path = Path(file_path)
            if not file_path.exists():
                raise AgapiValidationError(f"File not found: {file_path}")
            with open(file_path, "r") as f:
                poscar = f.read()
        
        if not poscar:
            raise AgapiValidationError("Provide poscar or file_path")
        
        result = self._get(
            "/alignn_ff/relax",
            params={"poscar": poscar, "fmax": fmax, "steps": steps},
            accept="text/plain"
        )
        
        # Decode bytes to string if needed
        if isinstance(result, bytes):
            return result.decode('utf-8')
        return result
    def xrd_analyze_with_refinement(self, **kwargs):
        """XRD refinement is only available through the web interface at https://atomgpt.org"""
        raise NotImplementedError(
            "XRD refinement is only available through the web interface at https://atomgpt.org"
        )

    def alignn_ff_optimize(self, **kwargs):
        """Geometry optimization is only available through the web interface at https://atomgpt.org"""
        raise NotImplementedError(
            "Geometry optimization is only available through the web interface at https://atomgpt.org"
        )

    def alignn_ff_molecular_dynamics(self, **kwargs):
        """Molecular dynamics is only available through the web interface at https://atomgpt.org"""
        raise NotImplementedError(
            "Molecular dynamics is only available through the web interface at https://atomgpt.org"
        )

    def alignn_ff_optimize_TODO(
        self,
        *,
        poscar: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        fmax: float = 0.05,
        steps: int = 200,
        optimizer: str = "FIRE",
        relax_cell: bool = True,
    ) -> Dict[str, Any]:
        """Run geometry optimization with ALIGNN-FF."""
        if file_path:
            file_path = Path(file_path)
            if not file_path.exists():
                raise AgapiValidationError(f"File not found: {file_path}")
            with open(file_path, "r") as f:
                poscar = f.read()
        
        if not poscar:
            raise AgapiValidationError("Provide poscar or file_path")
        
        payload = {
            "poscar": poscar,
            "fmax": fmax,
            "steps": steps,
            "optimizer": optimizer,
            "relax_cell": relax_cell,
        }
        
        return self._post_json("/alignn_ff/optimize", payload)

    def alignn_ff_molecular_dynamics_TODO(
        self,
        *,
        poscar: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        temperature: float = 300.0,
        timestep: float = 0.5,
        steps: int = 50,
        interval: int = 5,
    ) -> Dict[str, Any]:
        """Run molecular dynamics with ALIGNN-FF."""
        if file_path:
            file_path = Path(file_path)
            if not file_path.exists():
                raise AgapiValidationError(f"File not found: {file_path}")
            with open(file_path, "r") as f:
                poscar = f.read()
        
        if not poscar:
            raise AgapiValidationError("Provide poscar or file_path")
        
        payload = {
            "poscar": poscar,
            "temperature": temperature,
            "timestep": timestep,
            "steps": steps,
            "interval": interval,
        }
        
        return self._post_json("/alignn_ff/md", payload)

    def slakonet_bandstructure(
        self,
        *,
        jid: Optional[str] = None,
        poscar: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        energy_range_min: float = -8.0,
        energy_range_max: float = 8.0,
    ) -> bytes:
        """Calculate band structure with SlakoNet."""
        params = {
            "energy_range_min": energy_range_min,
            "energy_range_max": energy_range_max,
        }
        
        if jid:
            params["jid"] = jid
        elif file_path:
            file_path = Path(file_path)
            if not file_path.exists():
                raise AgapiValidationError(f"File not found: {file_path}")
            with open(file_path, "r") as f:
                params["poscar"] = f.read()
        elif poscar:
            params["poscar"] = poscar
        else:
            raise AgapiValidationError("Provide jid, poscar, or file_path")
        
        return self._get(
            "/slakonet/bandstructure",
            params=params,
            accept="image/png"
        )

    # ========================================================================
    # Analysis Tools
    # ========================================================================

    def xrd_analyze(
        self,
        *,
        formula: str,
        pattern: str,
        wavelength: float = 1.54184,
        method: str = "pattern_matching",
    ) -> Dict[str, Any]:
        """Analyze powder XRD pattern."""
        return self._get(
            "/pxrd/query",
            params={
                "pattern": pattern,
                "formula": formula,
                "wavelength": wavelength,
                "method": method,
            }
        )

    def xrd_analyze_with_refinement_TODO(
        self,
        *,
        formula: str,
        xrd_data: str,
        wavelength: float = 1.54184,
        method: str = "pattern_matching",
        run_refinement: bool = True,
        run_alignn: bool = False,
        run_slakonet: bool = False,
    ) -> Dict[str, Any]:
        """Analyze XRD pattern with optional Rietveld refinement."""
        payload = {
            "formula": formula,
            "xrd_data": xrd_data,
            "wavelength": wavelength,
            "method": method,
            "run_refinement": run_refinement,
            "run_alignn": run_alignn,
            "run_slakonet": run_slakonet,
        }
        
        return self._post_json("/xrd/analyze_with_refinement", payload)

    def diffractgpt_predict(
        self,
        *,
        formula: str,
        peaks: str,
        max_new_tokens: int = 1024,
    ) -> str:
        """Predict crystal structure from XRD peaks using DiffractGPT."""
        result = self._get(
            "/diffractgpt/query",
            params={
                "formula": formula,
                "peaks": peaks,
                "max_new_tokens": max_new_tokens,
            },
            accept="text/plain"
        )
        
        if isinstance(result, bytes):
            return result.decode('utf-8')
        return result

    def protein_fold(
        self,
        sequence: str,
    ) -> str:
        """Predict protein structure from amino acid sequence."""
        if not sequence:
            raise AgapiValidationError("sequence is required")
        
        result = self._get(
            "/protein_fold/query",
            params={"sequence": sequence},
            accept="text/plain"
        )
        
        if isinstance(result, bytes):
            return result.decode('utf-8')
        return result

    def weather(
        self,
        location: str,
        units: str = "imperial",
    ) -> Dict[str, Any]:
        """Get weather data for a location."""
        return self._get(
            "/weather",
            params={"location": location, "units": units}
        )

    # ========================================================================
    # Literature Search
    # ========================================================================

    def arxiv_search(
        self,
        query: str,
        max_results: int = 10,
    ) -> Dict[str, Any]:
        """Search arXiv for papers."""
        return self._get(
            "/arxiv",
            params={"query": query, "max_results": min(max_results, 100)}
        )

    def crossref_search(
        self,
        query: str,
        rows: int = 10,
    ) -> Dict[str, Any]:
        """Search CrossRef for publications."""
        return self._get(
            "/crossref",
            params={"query": query, "rows": rows}
        )

    # ========================================================================
    # Structure Manipulation
    # ========================================================================

    def jarvis_atoms_query(
        self,
        *,
        jid: Optional[str] = None,
        poscar: Optional[str] = None,
        cif: Optional[str] = None,
        supercell: Optional[str] = None,
        get_primitive: bool = False,
        get_conventional: bool = False,
        vacancy_atom: Optional[str] = None,  # ADDED
        substitution_atom: Optional[str] = None,  # ADDED
        neighbors_cutoff: Optional[float] = None,  # ADDED
        surface_index: Optional[str] = None,
        properties: Optional[str] = None,
        output_format: str = "poscar",
    ) -> Dict[str, Any]:
        """Query and manipulate atomic structures."""
        params = {"output_format": output_format}
        
        if jid:
            params["jid"] = jid
        elif poscar:
            params["poscar"] = poscar
        elif cif:
            params["cif"] = cif
        else:
            raise AgapiValidationError("Provide jid, poscar, or cif")
        
        if supercell:
            params["supercell"] = supercell
        if get_primitive:
            params["get_primitive_cell"] = "true"
        if get_conventional:
            params["get_conventional_cell"] = "true"
        if vacancy_atom:  # ADDED
            params["vacancy_atom"] = vacancy_atom
        if substitution_atom:  # ADDED
            params["substitution_atom"] = substitution_atom
        if neighbors_cutoff:  # ADDED
            params["neighbors_cutoff"] = neighbors_cutoff
        if surface_index:
            params["surface_index"] = surface_index
        if properties:
            params["properties"] = properties
        
        return self._get("/jarvis_atoms/query", params=params)

    # ========================================================================
    # Conversational Interface
    # ========================================================================

    def ask(
        self,
        question: str,
        model: str = "openai/gpt-oss-20b",
        stream: bool = False,
    ) -> Union[str, Any]:
        """Ask a question using the conversational interface."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI SDK required for ask(). Install: pip install openai"
            )
        
        openai_client = OpenAI(
            api_key=self.api_key,
            base_url=f"{self.base_url}/api"
        )
        
        response = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}],
            stream=stream,
        )
        
        if stream:
            return response
        else:
            return response.choices[0].message.content

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        try:
            columns = self.jarvis_dft_columns()
            return {
                "status": "healthy",
                "base_url": self.base_url,
                "available_columns": len(columns),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "base_url": self.base_url,
                "error": str(e),
            }

    def __repr__(self) -> str:
        """String representation."""
        return f"Agapi(base_url='{self.base_url}', timeout={self.timeout})"

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session."""
        self.session.close()
