import json
from typing import Optional, Dict, Any

from .client import AGAPIClient
from .aliases import normalize_property_name


def query_by_formula(formula: str, api_client: AGAPIClient) -> Dict[str, Any]:
    """Get all polymorphs of a chemical formula"""
    try:
        params = {"formula": formula, "limit": 100}
        result = api_client.request("jarvis_dft/query", params)

        materials = []
        for mat in result.get("results", []):
            # Prioritize MBJ bandgap, fallback to OptB88vdW
            bandgap = mat.get("mbj_bandgap") or mat.get("optb88vdw_bandgap")
            bandgap_source = (
                "mbj" if mat.get("mbj_bandgap") is not None else "optb88vdw"
            )

            materials.append(
                {
                    "jid": mat.get("jid"),
                    "formula": mat.get("formula"),
                    "spg_symbol": mat.get("spg_symbol"),
                    "formation_energy_peratom": mat.get(
                        "formation_energy_peratom"
                    ),
                    "bulk_modulus_kv": mat.get("bulk_modulus_kv"),
                    "bandgap": bandgap,  # Preferred bandgap
                    "bandgap_source": bandgap_source,  # Which method was used
                    "mbj_bandgap": mat.get(
                        "mbj_bandgap"
                    ),  # Keep both available
                    "optb88vdw_bandgap": mat.get("optb88vdw_bandgap"),
                    "ehull": mat.get("ehull"),
                }
            )

        return {"total": result.get("total", 0), "materials": materials}
    except Exception as e:
        return {"error": str(e)}


def query_by_jid(jid: str, api_client: AGAPIClient) -> Dict[str, Any]:
    """Get detailed info for a JARVIS ID including POSCAR"""
    try:
        params = {"jid": jid, "limit": 1}
        result = api_client.request("jarvis_dft/query", params)

        if result.get("results"):
            mat = result["results"][0]

            # Prioritize MBJ bandgap
            bandgap = mat.get("mbj_bandgap") or mat.get("optb88vdw_bandgap")
            bandgap_source = (
                "mbj" if mat.get("mbj_bandgap") is not None else "optb88vdw"
            )

            return {
                "jid": mat.get("jid"),
                "formula": mat.get("formula"),
                "spg_symbol": mat.get("spg_symbol"),
                "formation_energy_peratom": mat.get(
                    "formation_energy_peratom"
                ),
                "bulk_modulus_kv": mat.get("bulk_modulus_kv"),
                "bandgap": bandgap,  # Preferred bandgap
                "bandgap_source": bandgap_source,
                "mbj_bandgap": mat.get("mbj_bandgap"),
                "optb88vdw_bandgap": mat.get("optb88vdw_bandgap"),
                "hse_gap": mat.get("hse_gap"),
                "ehull": mat.get("ehull"),
                "POSCAR": mat.get("POSCAR"),
            }

        return {"error": f"Material {jid} not found"}
    except Exception as e:
        return {"error": str(e)}


def query_by_elements(
    elements: str, api_client: AGAPIClient
) -> Dict[str, Any]:
    """Get materials containing specific elements"""
    try:
        params = {"elements": elements, "limit": 100}
        result = api_client.request("jarvis_dft/query", params)

        materials = []
        for mat in result.get("results", [])[:20]:
            bandgap = mat.get("mbj_bandgap") or mat.get("optb88vdw_bandgap")
            bandgap_source = (
                "mbj" if mat.get("mbj_bandgap") is not None else "optb88vdw"
            )

            materials.append(
                {
                    "jid": mat.get("jid"),
                    "formula": mat.get("formula"),
                    "spg_symbol": mat.get("spg_symbol"),
                    "formation_energy_peratom": mat.get(
                        "formation_energy_peratom"
                    ),
                    "bulk_modulus_kv": mat.get("bulk_modulus_kv"),
                    "bandgap": bandgap,
                    "bandgap_source": bandgap_source,
                    "mbj_bandgap": mat.get("mbj_bandgap"),
                    "optb88vdw_bandgap": mat.get("optb88vdw_bandgap"),
                    "ehull": mat.get("ehull"),
                }
            )

        return {
            "total": result.get("total", 0),
            "showing": len(materials),
            "materials": materials,
        }
    except Exception as e:
        return {"error": str(e)}


def query_by_property(
    property_name: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    elements: Optional[str] = None,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """Find materials by property range"""
    try:
        prop = normalize_property_name(property_name)

        propranges = {}
        if min_val is not None and max_val is not None:
            propranges[prop] = {"min": min_val, "max": max_val}
        elif min_val is not None:
            propranges[prop] = {"min": min_val}
        elif max_val is not None:
            propranges[prop] = {"max": max_val}

        params = {"propranges": json.dumps(propranges), "limit": 1000}
        if elements:
            params["elements"] = elements

        result = api_client.request("jarvis_dft/query", params)
        total_count = result.get("total", 0)

        materials = []
        for mat in result.get("results", [])[:20]:
            bandgap = mat.get("mbj_bandgap") or mat.get("optb88vdw_bandgap")
            bandgap_source = (
                "mbj" if mat.get("mbj_bandgap") is not None else "optb88vdw"
            )

            materials.append(
                {
                    "jid": mat.get("jid"),
                    "formula": mat.get("formula"),
                    "spg_symbol": mat.get("spg_symbol"),
                    "formation_energy_peratom": mat.get(
                        "formation_energy_peratom"
                    ),
                    "bulk_modulus_kv": mat.get("bulk_modulus_kv"),
                    "bandgap": bandgap,
                    "bandgap_source": bandgap_source,
                    "mbj_bandgap": mat.get("mbj_bandgap"),
                    "optb88vdw_bandgap": mat.get("optb88vdw_bandgap"),
                    "ehull": mat.get("ehull"),
                    prop: mat.get(prop),
                }
            )

        return {
            "total": total_count,
            "showing": len(materials),
            "property": prop,
            "range": propranges,
            "materials": materials,
        }
    except Exception as e:
        return {"error": str(e)}


def find_extreme(
    property_name: str,
    maximize: bool = True,
    elements: Optional[str] = None,
    formula: Optional[str] = None,
    min_constraint: Optional[float] = None,
    max_constraint: Optional[float] = None,
    constraint_property: Optional[str] = None,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """Find material with highest or lowest property value"""
    try:
        prop = normalize_property_name(property_name)

        params = {"limit": 1000}

        propranges = {}
        if constraint_property and (
            min_constraint is not None or max_constraint is not None
        ):
            constraint_prop = normalize_property_name(constraint_property)
            propranges[constraint_prop] = {}
            if min_constraint is not None:
                propranges[constraint_prop]["min"] = min_constraint
            if max_constraint is not None:
                propranges[constraint_prop]["max"] = max_constraint

        if propranges:
            params["propranges"] = json.dumps(propranges)

        if formula:
            params["formula"] = formula
        elif elements:
            params["elements"] = elements

        result = api_client.request("jarvis_dft/query", params)
        results = result.get("results", [])

        if not results:
            return {"error": "No materials found"}

        with_property = [m for m in results if m.get(prop) is not None]

        if not with_property:
            return {"error": f"No materials with {prop} data"}

        if maximize:
            best = max(with_property, key=lambda x: x.get(prop, -float("inf")))
        else:
            best = min(with_property, key=lambda x: x.get(prop, float("inf")))

        # Get preferred bandgap
        bandgap = best.get("mbj_bandgap") or best.get("optb88vdw_bandgap")
        bandgap_source = (
            "mbj" if best.get("mbj_bandgap") is not None else "optb88vdw"
        )

        return {
            "total_candidates": len(results),
            "property": prop,
            "mode": "maximum" if maximize else "minimum",
            "jid": best.get("jid"),
            "formula": best.get("formula"),
            "spg_symbol": best.get("spg_symbol"),
            prop: best.get(prop),
            "formation_energy_peratom": best.get("formation_energy_peratom"),
            "bulk_modulus_kv": best.get("bulk_modulus_kv"),
            "ehull": best.get("ehull"),
            "bandgap": bandgap,
            "bandgap_source": bandgap_source,
            "mbj_bandgap": best.get("mbj_bandgap"),
            "optb88vdw_bandgap": best.get("optb88vdw_bandgap"),
        }
    except Exception as e:
        return {"error": str(e)}


# ALIGNN Tools
def alignn_predict(
    poscar: str = None, jid: str = None, *, api_client: AGAPIClient = None
) -> Dict[str, Any]:
    """Predict material properties using ALIGNN machine learning models."""
    try:
        import httpx
        import urllib.parse

        # Validate input
        if not jid and not poscar:
            return {"error": "Either poscar or jid must be provided"}

        # Build URL manually to match working format
        base_url = f"{api_client.api_base}/alignn/query"

        if jid:
            # Format: ?jid=JVASP-667&APIKEY="sk-xxx"
            url = f'{base_url}?jid={jid}&APIKEY="{api_client.api_key}"'
        else:
            # Format: ?poscar="System\n..."&APIKEY="sk-xxx"
            poscar_encoded = urllib.parse.quote(poscar)
            url = f'{base_url}?poscar="{poscar_encoded}"&APIKEY="{api_client.api_key}"'

        # Make GET request
        response = httpx.get(url, timeout=120.0)
        response.raise_for_status()
        result = response.json()

        if not result:
            return {"error": "No result returned from ALIGNN"}

        if isinstance(result, dict) and "error" in result:
            return {"error": result["error"]}

        return {
            "status": "success",
            "jid": jid if jid else "custom_structure",
            "formation_energy": result.get(
                "jv_formation_energy_peratom_alignn"
            ),
            "energy_eV": result.get("jv_optb88vdw_total_energy_alignn"),
            "bandgap_optb88vdw": result.get("jv_optb88vdw_bandgap_alignn"),
            "bandgap_mbj": result.get("jv_mbj_bandgap_alignn"),
            "bandgap": result.get("jv_mbj_bandgap_alignn")
            or result.get("jv_optb88vdw_bandgap_alignn"),
            "bulk_modulus": result.get("jv_bulk_modulus_kv_alignn"),
            "shear_modulus": result.get("jv_shear_modulus_gv_alignn"),
            "piezo_max_dielectric": result.get(
                "jv_dfpt_piezo_max_dielectric_alignn"
            ),
            "Tc_supercon": result.get("jv_supercon_tc_alignn"),
        }

    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": f"ALIGNN prediction failed: {str(e)}"}


def alignn_predictX(
    poscar: str, jid: Optional[str] = None, api_client: AGAPIClient = None
) -> Dict[str, Any]:
    """Predict material properties using ALIGNN"""
    try:
        params = {"poscar": poscar} if not jid else {"jid": jid}
        result = api_client.request("alignn/query", params)

        return {
            "formation_energy": result.get(
                "jv_formation_energy_peratom_alignn"
            ),
            "energy_eV": result.get("jv_optb88vdw_total_energy_alignn"),
            "bandgap_optb88vdw": result.get("jv_optb88vdw_bandgap_alignn"),
            "bandgap_mbj": result.get("jv_mbj_bandgap_alignn"),
            "bulk_modulus": result.get("jv_bulk_modulus_kv_alignn"),
            "shear_modulus": result.get("jv_shear_modulus_gv_alignn"),
            "piezo_max_dielectric": result.get(
                "jv_dfpt_piezo_max_dielectric_alignn"
            ),
            "Tc_supercon": result.get("jv_supercon_tc_alignn"),
        }
    except Exception as e:
        return {"error": str(e)}


def alignn_ff_relaxX(
    poscar: str,
    fmax: float = 0.05,
    steps: int = 150,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """
    Relax structure using ALIGNN force field via GET endpoint.
    """
    try:
        params = {
            "poscar": poscar,
            "fmax": fmax,
            "steps": steps,
        }

        response = httpx.get(
            f"{api_client.api_base}/alignn_ff/relax",
            params=params,
            headers={"Authorization": f"Bearer {api_client.api_key}"},
            timeout=api_client.timeout,
        )

        if response.status_code == 200:
            relaxed_poscar = response.text

            return {
                "status": "success",
                "relaxed_poscar": relaxed_poscar,
                "message": f"Structure relaxed with ALIGNN-FF (fmax={fmax}, steps={steps})",
            }
        else:
            return {
                "error": f"ALIGNN-FF relaxation failed: {response.status_code}",
                "detail": response.text,
            }

    except Exception as e:
        return {"error": f"ALIGNN-FF relaxation error: {str(e)}"}


def alignn_ff_relaxX(poscar: str, api_client: AGAPIClient) -> Dict[str, Any]:
    """Relax structure using ALIGNN force field"""
    try:
        params = {"poscar": poscar}
        result = api_client.request("alignn_ff/query", params)

        return {
            "relaxed_structure": result.get("POSCAR"),
            "energy_eV": result.get("energy_eV"),
        }
    except Exception as e:
        return {"error": str(e)}


# SlakoNet Tools
def slakonet_bandstructureX(
    poscar: str,
    energy_range_min: float = -8.0,
    energy_range_max: float = 8.0,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """
    Calculate electronic band structure using SlakoNet.
    Returns both band structure image and electronic properties.
    """
    try:
        import httpx
        import base64

        # Prepare request
        data = {
            "poscar_string": poscar,
            "energy_range_min": energy_range_min,
            "energy_range_max": energy_range_max,
            "model_path": "/path/to/slakonet_v0/slakonet_v0.pt",  # Default path
        }

        # Make request with httpx to get full response
        response = httpx.post(
            f"{api_client.api_base}/slakonet/bandstructure",
            data=data,
            headers={"Authorization": f"Bearer {api_client.api_key}"},
            timeout=api_client.timeout,
        )

        if response.status_code == 200:
            # Extract properties from headers
            band_gap = response.headers.get("X-Band-Gap", "N/A")
            vbm = response.headers.get("X-VBM", "N/A")
            cbm = response.headers.get("X-CBM", "N/A")

            # Get image data
            image_data = response.content
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            # Get filename from Content-Disposition
            content_disp = response.headers.get("Content-Disposition", "")
            filename = "bandstructure.png"
            if "filename=" in content_disp:
                filename = content_disp.split("filename=")[1].strip()

            return {
                "status": "success",
                "band_gap_eV": band_gap,
                "vbm_eV": vbm,
                "cbm_eV": cbm,
                "image_base64": image_base64,
                "image_filename": filename,
                "message": f"Band structure calculated. Band gap: {band_gap} eV, VBM: {vbm} eV, CBM: {cbm} eV",
            }
        else:
            return {
                "error": f"SlakoNet request failed: {response.status_code}",
                "detail": response.text,
            }

    except Exception as e:
        return {"error": f"SlakoNet error: {str(e)}"}


def slakonet_bandstructureX(
    poscar: str = None, jid: str = None, api_client: AGAPIClient = None
) -> Dict[str, Any]:
    """Calculate band structure using SlakoNet"""
    try:
        params = {"jid": jid} if jid else {"poscar": poscar}
        result = api_client.request("slakonet/bandstructure", params)

        return {
            "band_gap_eV": result.get("band_gap_eV"),
            "vbm_eV": result.get("vbm_eV"),
            "cbm_eV": result.get("cbm_eV"),
            "note": "Band structure calculated",
        }
    except Exception as e:
        return {"error": str(e)}


def alignn_predictX(
    poscar: str = None,
    jid: str = None,
    property_name: str = "all",
    *,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """
    Predict material properties using ALIGNN ML models.

    Args:
        poscar: POSCAR format structure string (optional if jid provided)
        jid: JARVIS-ID to use directly (optional if poscar provided)
        property_name: Property to predict (default: "all")
        api_client: API client instance

    Returns:
        dict with predicted properties
    """
    try:
        # Build params - backend accepts either poscar or jid
        if jid:
            params = {"jid": jid}
        elif poscar:
            params = {"poscar": poscar}
        else:
            return {"error": "Either poscar or jid must be provided"}

        # Call ALIGNN API endpoint
        result = api_client.request("alignn/query", params, method="POST")

        if not result or (isinstance(result, dict) and "error" in result):
            return {
                "error": f"ALIGNN prediction failed: {result.get('error', 'Unknown error')}"
            }

        # Parse and structure the response
        predictions = {}

        # Formation energy
        if "jv_formation_energy_peratom_alignn" in result:
            predictions["formation_energy_peratom"] = result[
                "jv_formation_energy_peratom_alignn"
            ]

        # Total energy
        if "jv_optb88vdw_total_energy_alignn" in result:
            predictions["total_energy"] = result[
                "jv_optb88vdw_total_energy_alignn"
            ]

        # Bandgaps (prioritize MBJ)
        if "jv_mbj_bandgap_alignn" in result:
            predictions["bandgap"] = result["jv_mbj_bandgap_alignn"]
            predictions["bandgap_type"] = "MBJ (more accurate)"
        elif "jv_optb88vdw_bandgap_alignn" in result:
            predictions["bandgap"] = result["jv_optb88vdw_bandgap_alignn"]
            predictions["bandgap_type"] = "OptB88vdW"

        # Elastic properties
        if "jv_bulk_modulus_kv_alignn" in result:
            predictions["bulk_modulus_kv"] = result[
                "jv_bulk_modulus_kv_alignn"
            ]
        if "jv_shear_modulus_gv_alignn" in result:
            predictions["shear_modulus_gv"] = result[
                "jv_shear_modulus_gv_alignn"
            ]

        # Piezoelectric
        if "jv_dfpt_piezo_max_dielectric_alignn" in result:
            predictions["max_piezo_dielectric"] = result[
                "jv_dfpt_piezo_max_dielectric_alignn"
            ]

        # Superconductivity
        if "jv_supercon_tc_alignn" in result:
            predictions["supercon_tc"] = result["jv_supercon_tc_alignn"]

        # Exfoliation energy
        if "jv_exfoliation_energy_alignn" in result:
            predictions["exfoliation_energy"] = result[
                "jv_exfoliation_energy_alignn"
            ]

        return {
            "status": "success",
            "predictions": predictions,
            "jid": jid if jid else "custom_structure",
            "raw_result": result,  # Include full result for debugging
            "message": f"ALIGNN predictions completed ({len(predictions)} properties)",
        }

    except Exception as e:
        return {"error": f"ALIGNN prediction error: {str(e)}"}


def alignn_predictX(
    poscar: str, *, api_client: AGAPIClient = None
) -> Dict[str, Any]:
    """
    Predict properties using ALIGNN ML models.

    Args:
        poscar: POSCAR format structure string
        api_client: API client instance (injected by agent)
    """
    try:
        # Parse POSCAR
        from jarvis.io.vasp.inputs import Poscar

        atoms = Poscar.from_string(poscar).atoms

        if atoms.num_atoms > 50:
            return {
                "error": f"Structure too large ({atoms.num_atoms} atoms). Max: 50"
            }

        # Make request
        params = {"poscar": poscar}
        result = api_client.request("alignn/query", params)

        return {
            "status": "success",
            "predictions": result,
            "num_atoms": atoms.num_atoms,
            "formula": atoms.composition.reduced_formula,
        }
    except Exception as e:
        return {"error": f"ALIGNN prediction error: {str(e)}"}


def alignn_predictX(
    poscar: str = None,
    jid: str = None,
    property_name: str = "all",
    *,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """
    Predict material properties using ALIGNN ML models.

    Args:
        poscar: POSCAR format structure string (optional if jid provided)
        jid: JARVIS-ID to use directly (optional if poscar provided)
        property_name: Property to predict (default: "all")
        api_client: API client instance

    Returns:
        dict with predicted properties
    """
    try:
        # Build params - backend accepts either poscar or jid
        if jid:
            params = {"jid": jid}
        elif poscar:
            params = {"poscar": poscar}
        else:
            return {"error": "Either poscar or jid must be provided"}

        # Call ALIGNN API endpoint
        result = api_client.request("alignn/query", params, method="POST")
        print("resut", result)
        if not result or (isinstance(result, dict) and "error" in result):
            return {
                "error": f"ALIGNN prediction failed: {result.get('error', 'Unknown error')}"
            }

        # Parse and structure the response
        predictions = {}

        # Formation energy
        if "jv_formation_energy_peratom_alignn" in result:
            predictions["formation_energy_peratom"] = result[
                "jv_formation_energy_peratom_alignn"
            ]

        # Total energy
        if "jv_optb88vdw_total_energy_alignn" in result:
            predictions["total_energy"] = result[
                "jv_optb88vdw_total_energy_alignn"
            ]

        # Bandgaps (prioritize MBJ)
        if "jv_mbj_bandgap_alignn" in result:
            predictions["bandgap"] = result["jv_mbj_bandgap_alignn"]
            predictions["bandgap_type"] = "MBJ (more accurate)"
        elif "jv_optb88vdw_bandgap_alignn" in result:
            predictions["bandgap"] = result["jv_optb88vdw_bandgap_alignn"]
            predictions["bandgap_type"] = "OptB88vdW"

        # Elastic properties
        if "jv_bulk_modulus_kv_alignn" in result:
            predictions["bulk_modulus_kv"] = result[
                "jv_bulk_modulus_kv_alignn"
            ]
        if "jv_shear_modulus_gv_alignn" in result:
            predictions["shear_modulus_gv"] = result[
                "jv_shear_modulus_gv_alignn"
            ]

        # Piezoelectric
        if "jv_dfpt_piezo_max_dielectric_alignn" in result:
            predictions["max_piezo_dielectric"] = result[
                "jv_dfpt_piezo_max_dielectric_alignn"
            ]

        # Superconductivity
        if "jv_supercon_tc_alignn" in result:
            predictions["supercon_tc"] = result["jv_supercon_tc_alignn"]

        return {
            "status": "success",
            "predictions": predictions,
            "jid": jid if jid else "custom_structure",
            "raw_result": result,  # Include full result for debugging
            "message": f"ALIGNN predictions completed ({len(predictions)} properties)",
        }

    except Exception as e:
        return {"error": f"ALIGNN prediction error: {str(e)}"}


def alignn_predictX(
    poscar: str = None,
    jid: str = None,
    property_name: str = "all",
    *,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """
    Predict material properties using ALIGNN ML models.

    Args:
        poscar: POSCAR format structure string (optional if jid provided)
        jid: JARVIS-ID to fetch structure (optional if poscar provided)
        property_name: Property to predict. Options:
            - "all": All available properties (default)
            - "formation_energy_peratom"
            - "bandgap" (or "bandgap_mbj" for MBJ corrected)
            - "bulk_modulus"
            - "shear_modulus"
            - "elastic_tensor"
            - "exfoliation_energy"
            - "max_ir_mode"
            - "max_piezo_coeff"
            And many more...
        api_client: API client instance (injected by agent)

    Returns:
        dict with predicted properties

    Example:
        >>> alignn_predict(jid="JVASP-1002")
        >>> alignn_predict(poscar=poscar_string, property_name="bandgap")
    """
    try:
        # If jid provided, fetch the structure first
        if jid and not poscar:
            jid_result = query_by_jid(jid, api_client=api_client)
            if "error" in jid_result:
                return {
                    "error": f"Failed to fetch structure for {jid}: {jid_result['error']}"
                }
            poscar = jid_result.get("atoms")
            if not poscar:
                return {"error": f"No structure found for {jid}"}

        if not poscar:
            return {"error": "Either poscar or jid must be provided"}

        # Build request
        params = {
            "atoms": poscar,
            "property": property_name,
        }

        result = api_client.request("alignn_predict", params, method="POST")

        # Parse result
        if isinstance(result, dict):
            # Prioritize MBJ bandgap if available
            if "prediction" in result:
                predictions = result["prediction"]

                # If bandgap requested, try to get MBJ version
                if property_name in ["bandgap", "all"]:
                    if "bandgap_mbj" in predictions:
                        result["bandgap"] = predictions["bandgap_mbj"]
                        result["bandgap_type"] = "MBJ (more accurate)"
                    elif "bandgap" in predictions:
                        result["bandgap"] = predictions["bandgap"]
                        result["bandgap_type"] = "standard"

                return {
                    "status": "success",
                    "predictions": predictions,
                    "jid": jid if jid else "custom",
                    "message": f"ALIGNN predictions completed",
                }
            else:
                return result
        else:
            return {
                "error": "Unexpected response format",
                "response": str(result),
            }

    except Exception as e:
        return {"error": f"ALIGNN prediction error: {str(e)}"}


def alignn_predictX(
    poscar: str, *, api_client: AGAPIClient = None
) -> Dict[str, Any]:
    """
    Predict properties using ALIGNN ML models.

    Args:
        poscar: POSCAR format structure string
        api_client: API client instance (injected by agent)
    """
    try:
        # Parse POSCAR
        from jarvis.io.vasp.inputs import Poscar

        atoms = Poscar.from_string(poscar).atoms

        if atoms.num_atoms > 50:
            return {
                "error": f"Structure too large ({atoms.num_atoms} atoms). Max: 50"
            }

        # Make request
        params = {"poscar": poscar}
        result = api_client.request("alignn/query", params)

        return {
            "status": "success",
            "predictions": result,
            "num_atoms": atoms.num_atoms,
            "formula": atoms.composition.reduced_formula,
        }
    except Exception as e:
        return {"error": f"ALIGNN prediction error: {str(e)}"}


def alignn_ff_relax(
    poscar: str,
    fmax: float = 0.05,
    steps: int = 150,
    *,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """
    Relax structure using ALIGNN force field.

    Args:
        poscar: POSCAR format structure string
        fmax: Force convergence criterion (eV/Å)
        steps: Maximum optimization steps
        api_client: API client instance (injected by agent)
    """
    try:
        import httpx

        # Use POST endpoint (your backend has this)
        data = {
            "poscar_string": poscar,
        }

        response = httpx.post(
            f"{api_client.api_base}/alignn_ff/query",
            data=data,
            headers={"Authorization": f"Bearer {api_client.api_key}"},
            timeout=api_client.timeout,
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "status": "success",
                "original_poscar": result.get("original"),
                "relaxed_poscar": result.get("relaxed"),
                "message": "Structure optimized with ALIGNN-FF",
            }
        else:
            return {
                "error": f"ALIGNN-FF failed: {response.status_code}",
                "detail": response.text,
            }

    except Exception as e:
        return {"error": f"ALIGNN-FF error: {str(e)}"}


def slakonet_bandstructure(
    poscar: str,
    energy_range_min: float = -8.0,
    energy_range_max: float = 8.0,
    *,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """
    Calculate electronic band structure using SlakoNet.
    """
    try:
        import httpx
        import base64

        data = {
            "poscar_string": poscar,
            "energy_range_min": energy_range_min,
            "energy_range_max": energy_range_max,
        }

        response = httpx.post(
            f"{api_client.api_base}/slakonet/bandstructure",
            data=data,
            headers={"Authorization": f"Bearer {api_client.api_key}"},
            timeout=api_client.timeout,
        )

        if response.status_code == 200:
            band_gap = response.headers.get("X-Band-Gap", "N/A")
            vbm = response.headers.get("X-VBM", "N/A")
            cbm = response.headers.get("X-CBM", "N/A")

            image_data = response.content
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            content_disp = response.headers.get("Content-Disposition", "")
            filename = "bandstructure.png"
            if "filename=" in content_disp:
                filename = content_disp.split("filename=")[1].strip()

            return {
                "status": "success",
                "band_gap_eV": band_gap,
                "vbm_eV": vbm,
                "cbm_eV": cbm,
                "image_base64": image_base64,
                "image_filename": filename,
                "message": f"Band structure calculated. Band gap: {band_gap} eV",
            }
        else:
            return {
                "error": f"SlakoNet failed: {response.status_code}",
                "detail": response.text,
            }

    except Exception as e:
        return {"error": f"SlakoNet error: {str(e)}"}


# DiffractGPT Tools
def diffractgpt_predict(
    formula: str, peaks: str, api_client: AGAPIClient
) -> Dict[str, Any]:
    """Predict structure from XRD using DiffractGPT"""
    try:
        params = {"formula": formula, "peaks": peaks}
        result = api_client.request("diffractgpt/query", params)

        return {
            "predicted_structure": result.get("POSCAR"),
            "formula": formula,
        }
    except Exception as e:
        return {"error": str(e)}


def xrd_match(
    formula: str, xrd_pattern: str, api_client: AGAPIClient
) -> Dict[str, Any]:
    """Match XRD pattern to database"""
    try:
        params = {"pattern": xrd_pattern}
        result = api_client.request("pxrd/query", params)

        return {
            "matched_structure": result.get("POSCAR"),
            "formula": formula,
        }
    except Exception as e:
        return {"error": str(e)}


# Intermat Tools
def generate_interface(
    film_poscar: str,
    substrate_poscar: str,
    film_indices: str = "0_0_1",
    substrate_indices: str = "0_0_1",
    film_thickness: float = 16,
    substrate_thickness: float = 16,
    separation: float = 2.5,
    max_area: float = 300,
    *,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """
    Generate heterostructure interface between two materials.

    Args:
        film_poscar: POSCAR string for film material
        substrate_poscar: POSCAR string for substrate material
        film_indices: Miller indices for film surface (e.g., "0_0_1" for (001))
        substrate_indices: Miller indices for substrate surface
        film_thickness: Film layer thickness in Angstroms (default: 16)
        substrate_thickness: Substrate layer thickness in Angstroms (default: 16)
        separation: Interface separation distance in Angstroms (default: 2.5)
        max_area: Maximum interface area in Angstroms² (default: 300)
        api_client: API client instance (injected by agent)

    Returns:
        dict with interface structure (POSCAR format)
    """
    try:
        import httpx

        # Validate Miller indices format (should be "h_k_l" with underscores)
        if " " in film_indices or "," in film_indices:
            film_indices = film_indices.replace(" ", "_").replace(",", "_")
        if " " in substrate_indices or "," in substrate_indices:
            substrate_indices = substrate_indices.replace(" ", "_").replace(
                ",", "_"
            )

        # Build parameters matching backend API
        # Backend expects: poscar_film, poscar_subs, subs_indices (not substrate_indices)
        params = {
            "poscar_film": film_poscar,  # Map to backend param
            "poscar_subs": substrate_poscar,  # Map to backend param
            "film_indices": film_indices,
            "subs_indices": substrate_indices,  # Backend uses subs_indices
            "film_thickness": film_thickness,
            "subs_thickness": substrate_thickness,  # Backend uses subs_thickness
            "separations": str(
                separation
            ),  # Backend uses separations (string)
            "max_area": max_area,
            "APIKEY": api_client.api_key,
        }

        # Direct GET request (returns text/plain)
        response = httpx.get(
            f"{api_client.api_base}/generate_interface",
            params=params,
            timeout=300.0,
        )
        response.raise_for_status()

        interface_poscar = response.text

        # Parse basic info from POSCAR
        lines = interface_poscar.splitlines()
        elements_line = ""
        counts_line = ""
        for i, line in enumerate(lines):
            if "direct" in line.lower() or "cartesian" in line.lower():
                if i >= 2:
                    elements_line = lines[i - 2]
                    counts_line = lines[i - 1]
                break

        return {
            "status": "success",
            "heterostructure_atoms": interface_poscar,
            "film_indices": film_indices,
            "substrate_indices": substrate_indices,
            "film_thickness": film_thickness,
            "substrate_thickness": substrate_thickness,
            "separation": separation,
            "elements": elements_line.strip(),
            "atom_counts": counts_line.strip(),
            "message": f"Generated interface structure ({film_indices}/{substrate_indices}), {len(lines)} lines",
        }

    except httpx.HTTPStatusError as e:
        return {
            "error": f"API error {e.response.status_code}: {e.response.text}"
        }
    except Exception as e:
        return {"error": f"Interface generation error: {str(e)}"}


def make_supercell(
    poscar: str, scaling_matrix: list, api_client: AGAPIClient = None
) -> Dict[str, Any]:
    """
    Create a supercell from a POSCAR structure.

    Args:
        poscar: POSCAR format structure string
        scaling_matrix: List of 3 integers [nx, ny, nz] for supercell dimensions

    Returns:
        dict with supercell POSCAR and atom count
    """
    try:
        from jarvis.core.atoms import Atoms
        from jarvis.io.vasp.inputs import Poscar

        # Parse POSCAR
        atoms = Poscar.from_string(poscar).atoms

        # Create supercell
        supercell = atoms.make_supercell(scaling_matrix)

        # Convert back to POSCAR
        supercell_poscar = Poscar(supercell).to_string()

        return {
            "status": "success",
            "supercell_poscar": supercell_poscar,
            "original_atoms": atoms.num_atoms,
            "supercell_atoms": supercell.num_atoms,
            "scaling_matrix": scaling_matrix,
            "formula": supercell.composition.reduced_formula,
            "message": f"Created {scaling_matrix[0]}x{scaling_matrix[1]}x{scaling_matrix[2]} supercell with {supercell.num_atoms} atoms",
        }
    except Exception as e:
        return {"error": f"Supercell creation error: {str(e)}"}


def substitute_atom(
    poscar: str,
    element_from: str,
    element_to: str,
    num_substitutions: int = 1,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """
    Substitute atoms in a structure (e.g., replace Ga with Al).

    Args:
        poscar: POSCAR format structure string
        element_from: Element to replace (e.g., "Ga")
        element_to: Element to substitute with (e.g., "Al")
        num_substitutions: Number of atoms to substitute (default: 1)

    Returns:
        dict with modified POSCAR
    """
    try:
        from jarvis.core.atoms import Atoms
        from jarvis.io.vasp.inputs import Poscar

        # Parse POSCAR
        atoms = Poscar.from_string(poscar).atoms

        # Find indices of atoms to substitute
        indices_to_sub = []
        for i, atom in enumerate(atoms.elements):
            if atom == element_from:
                indices_to_sub.append(i)
                if len(indices_to_sub) >= num_substitutions:
                    break

        if not indices_to_sub:
            return {"error": f"No {element_from} atoms found in structure"}

        if len(indices_to_sub) < num_substitutions:
            return {
                "error": f"Only {len(indices_to_sub)} {element_from} atoms available, requested {num_substitutions}"
            }

        # Create new element list with substitutions
        new_elements = list(atoms.elements)
        for idx in indices_to_sub:
            new_elements[idx] = element_to

        # Create new atoms object with substituted elements
        new_atoms = Atoms(
            lattice_mat=atoms.lattice_mat,
            coords=atoms.coords,
            elements=new_elements,
            cartesian=atoms.cartesian,
        )

        # Convert to POSCAR
        new_poscar = Poscar(new_atoms).to_string()

        return {
            "status": "success",
            "modified_poscar": new_poscar,
            "substituted_indices": indices_to_sub,
            "num_substitutions": len(indices_to_sub),
            "original_formula": atoms.composition.reduced_formula,
            "new_formula": new_atoms.composition.reduced_formula,
            "message": f"Substituted {len(indices_to_sub)} {element_from} atoms with {element_to}",
        }
    except Exception as e:
        return {"error": f"Substitution error: {str(e)}"}


def create_vacancy(
    poscar: str,
    element: str,
    num_vacancies: int = 1,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """
    Create vacancy defects by removing atoms from a structure.

    Args:
        poscar: POSCAR format structure string
        element: Element to remove (e.g., "Ga")
        num_vacancies: Number of atoms to remove (default: 1)

    Returns:
        dict with modified POSCAR
    """
    try:
        from jarvis.core.atoms import Atoms
        from jarvis.io.vasp.inputs import Poscar

        # Parse POSCAR
        atoms = Poscar.from_string(poscar).atoms

        # Find indices of atoms to remove
        indices_to_remove = []
        for i, atom in enumerate(atoms.elements):
            if atom == element:
                indices_to_remove.append(i)
                if len(indices_to_remove) >= num_vacancies:
                    break

        if not indices_to_remove:
            return {"error": f"No {element} atoms found in structure"}

        if len(indices_to_remove) < num_vacancies:
            return {
                "error": f"Only {len(indices_to_remove)} {element} atoms available, requested {num_vacancies}"
            }

        # Create new lists without removed atoms
        new_elements = []
        new_coords = []
        for i, (elem, coord) in enumerate(zip(atoms.elements, atoms.coords)):
            if i not in indices_to_remove:
                new_elements.append(elem)
                new_coords.append(coord)

        # Create new atoms object
        new_atoms = Atoms(
            lattice_mat=atoms.lattice_mat,
            coords=new_coords,
            elements=new_elements,
            cartesian=atoms.cartesian,
        )

        # Convert to POSCAR
        new_poscar = Poscar(new_atoms).to_string()

        return {
            "status": "success",
            "modified_poscar": new_poscar,
            "removed_indices": indices_to_remove,
            "num_vacancies": len(indices_to_remove),
            "original_atoms": atoms.num_atoms,
            "new_atoms": new_atoms.num_atoms,
            "original_formula": atoms.composition.reduced_formula,
            "new_formula": new_atoms.composition.reduced_formula,
            "message": f"Created {len(indices_to_remove)} {element} vacancies ({atoms.num_atoms} → {new_atoms.num_atoms} atoms)",
        }
    except Exception as e:
        return {"error": f"Vacancy creation error: {str(e)}"}


def protein_fold(
    sequence: str, *, api_client: AGAPIClient = None
) -> Dict[str, Any]:
    """
    Predict 3D protein structure from amino acid sequence using ESMFold.

    Args:
        sequence: Amino acid sequence in one-letter codes (A, R, N, D, C, Q, E, G, H, I, L, K, M, F, P, S, T, W, Y, V)
        api_client: API client instance (injected by agent)

    Returns:
        dict with PDB structure string

    Example:
        >>> protein_fold("MKTAYIAKQRQISFVKSHFSRQ...")
    """
    try:
        import httpx

        # Validate sequence
        valid_amino_acids = set("ARNDCQEGHILKMFPSTWYV")
        sequence = sequence.upper().strip()

        invalid_chars = set(sequence) - valid_amino_acids
        if invalid_chars:
            return {
                "error": f"Invalid amino acids in sequence: {invalid_chars}. "
                f"Valid: A,R,N,D,C,Q,E,G,H,I,L,K,M,F,P,S,T,W,Y,V"
            }

        if len(sequence) < 10:
            return {"error": "Sequence too short (minimum 10 amino acids)"}

        if len(sequence) > 400:
            return {
                "error": f"Sequence too long ({len(sequence)} amino acids). Maximum: 400"
            }

        # Make request to protein folding endpoint
        params = {"sequence": sequence}

        response = httpx.get(
            f"{api_client.api_base}/protein_fold/query",
            params=params,
            headers={"Authorization": f"Bearer {api_client.api_key}"},
            timeout=120.0,  # Protein folding can take a while
        )

        if response.status_code == 200:
            pdb_structure = response.text

            # Extract some info from PDB
            lines = pdb_structure.splitlines()
            num_atoms = len([l for l in lines if l.startswith("ATOM")])
            num_residues = len(sequence)

            return {
                "status": "success",
                "pdb_structure": pdb_structure,
                "sequence_length": num_residues,
                "num_atoms": num_atoms,
                "message": f"Predicted 3D structure for {num_residues} amino acid protein ({num_atoms} atoms)",
            }
        else:
            return {
                "error": f"Protein folding failed: {response.status_code}",
                "detail": response.text,
            }

    except Exception as e:
        return {"error": f"Protein folding error: {str(e)}"}


def generate_xrd_pattern(
    poscar: str,
    wavelength: float = 1.54184,
    num_peaks: int = 20,
    theta_range: list = None,
    *,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """
    Generate powder XRD pattern description from crystal structure.

    Args:
        poscar: POSCAR format structure string
        wavelength: X-ray wavelength in Angstroms (default: 1.54184 = Cu K-alpha)
        num_peaks: Number of top peaks to report (default: 20)
        theta_range: [min, max] 2-theta range in degrees (default: [0, 90])
        api_client: API client instance (injected by agent)

    Returns:
        dict with XRD peak positions, intensities, and DiffractGPT-style description

    Example:
        >>> generate_xrd_pattern(poscar, wavelength=1.54184, num_peaks=10)
    """
    try:
        from jarvis.io.vasp.inputs import Poscar
        from jarvis.core.atoms import Atoms
        from jarvis.analysis.diffraction.xrd import XRD
        import numpy as np
        from scipy.signal import find_peaks

        # Parse structure
        atoms = Poscar.from_string(poscar).atoms
        formula = atoms.composition.reduced_formula

        # Set theta range
        if theta_range is None:
            theta_range = [0, 90]

        # Simulate XRD pattern
        xrd = XRD(wavelength=wavelength, thetas=theta_range)
        two_theta, d_spacing, intensity = xrd.simulate(atoms=atoms)

        # Normalize intensity
        intensity = np.array(intensity)
        intensity = intensity / np.max(intensity)
        two_theta = np.array(two_theta)

        # Apply Gaussian broadening for peak detection
        def gaussian_recast(x_original, y_original, x_new, sigma=0.1):
            y_new = np.zeros_like(x_new, dtype=np.float64)
            for x0, amp in zip(x_original, y_original):
                y_new += amp * np.exp(-0.5 * ((x_new - x0) / sigma) ** 2)
            return x_new, y_new

        x_new = np.arange(theta_range[0], theta_range[1], 0.1)
        two_theta_smooth, intensity_smooth = gaussian_recast(
            two_theta, intensity, x_new, sigma=0.1
        )
        intensity_smooth = intensity_smooth / np.max(intensity_smooth)

        # Find peaks
        peaks, props = find_peaks(
            intensity_smooth, height=0.01, distance=1, prominence=0.05
        )

        if len(peaks) == 0:
            return {
                "status": "warning",
                "message": f"No significant XRD peaks found for {formula}",
                "formula": formula,
                "wavelength": wavelength,
                "num_peaks_requested": num_peaks,
                "num_peaks_found": 0,
            }

        # Get top N peaks by intensity
        top_indices = np.argsort(props["peak_heights"])[::-1][:num_peaks]
        top_peaks = peaks[top_indices]
        top_peaks_sorted = top_peaks[np.argsort(two_theta_smooth[top_peaks])]

        # Create peak list with 2theta and relative intensity
        peak_list = [
            {
                "two_theta": round(float(two_theta_smooth[p]), 2),
                "intensity": round(float(intensity_smooth[p]), 2),
                "d_spacing": round(
                    float(
                        wavelength
                        / (2 * np.sin(np.radians(two_theta_smooth[p] / 2)))
                    ),
                    4,
                ),
            }
            for p in top_peaks_sorted
        ]

        # Build DiffractGPT-style description
        peak_text = ", ".join(
            [
                f"{peak['two_theta']}°({peak['intensity']})"
                for peak in peak_list
            ]
        )

        description = (
            f"The chemical formula is: {formula}.\n"
            f"The XRD pattern shows main peaks at: {peak_text}."
        )

        # Full pattern for plotting/matching
        full_pattern = [
            {
                "two_theta": round(float(tt), 2),
                "intensity": round(float(ii), 4),
            }
            for tt, ii in zip(two_theta_smooth, intensity_smooth)
        ]

        # Create markdown table for easy display
        peak_table = "| Rank | 2θ (°) | Intensity | d-spacing (Å) |\n"
        peak_table += "|------|--------|-----------|---------------|\n"
        for i, peak in enumerate(peak_list, 1):
            peak_table += f"| {i:2d}   | {peak['two_theta']:6.2f} | {peak['intensity']:5.2f}     | {peak['d_spacing']:6.4f}      |\n"

        return {
            "status": "success",
            "formula": formula,
            "wavelength": wavelength,
            "num_peaks_found": len(peaks),
            "num_peaks_reported": len(peak_list),
            "peaks": peak_list,
            "peak_table": peak_table,
            "description": description,
            "full_pattern": full_pattern[
                :1000
            ],  # Truncate to avoid huge response
            "message": f"Generated XRD pattern for {formula} with {len(peak_list)} main peaks",
        }

    except Exception as e:
        return {"error": f"XRD generation error: {str(e)}"}
