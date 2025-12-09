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


def alignn_ff_relax(poscar: str, api_client: AGAPIClient) -> Dict[str, Any]:
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
def slakonet_bandstructure(
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
    separation: float = 2.5,
    api_client: AGAPIClient = None,
) -> Dict[str, Any]:
    """Generate heterostructure interface"""
    try:
        params = {
            "poscar_film": film_poscar,
            "poscar_subs": substrate_poscar,
            "film_indices": film_indices,
            "subs_indices": substrate_indices,
            "separations": str(separation),
        }

        result = api_client.request("generate_interface", params)

        return {
            "interface_structure": result.get("POSCAR"),
            "separation": separation,
        }
    except Exception as e:
        return {"error": str(e)}
