PROPERTY_ALIASES = {
    # Bandgap
    "bandgap": "optb88vdw_bandgap",
    "band gap": "optb88vdw_bandgap",
    "band-gap": "optb88vdw_bandgap",
    "gap": "optb88vdw_bandgap",
    "bg": "optb88vdw_bandgap",
    "mbj bandgap": "mbj_bandgap",
    "mbj_bandgap": "mbj_bandgap",
    # Formation energy
    "formation energy": "formation_energy_peratom",
    "formation_energy": "formation_energy_peratom",
    "hf": "formation_energy_peratom",
    # Mechanical
    "bulk modulus": "bulk_modulus_kv",
    "bulk_modulus": "bulk_modulus_kv",
    "shear modulus": "shear_modulus_gv",
    "shear_modulus": "shear_modulus_gv",
    # Stability
    "ehull": "ehull",
    "energy above hull": "ehull",
    "stability": "ehull",
    # Magnetic
    "magnetization": "magmom_oszicar",
    "magnetic moment": "magmom_oszicar",
    "magmom": "magmom_oszicar",
    # Superconductivity
    "tc": "Tc_supercon",
    "tc_supercon": "Tc_supercon",
    "superconducting temperature": "Tc_supercon",
    # Transport
    "n-seebeck": "n-Seebeck",
    "p-seebeck": "p-Seebeck",
    "seebeck": "n-Seebeck",
}


def normalize_property_name(prop: str) -> str:
    """Normalize property name to API field name"""
    prop_lower = prop.lower().strip()
    for word in [
        "with",
        "the",
        "materials",
        "find",
        "show",
        "get",
        "have",
        "data",
    ]:
        prop_lower = prop_lower.replace(word, "").strip()
    return PROPERTY_ALIASES.get(prop_lower, prop)
