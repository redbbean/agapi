TOOLS_SCHEMA = [
    # JARVIS-DFT
    {
        "type": "function",
        "function": {
            "name": "query_by_formula",
            "description": "Get all polymorphs of a chemical formula from JARVIS-DFT (e.g., SiC, GaN, MgB2)",
            "parameters": {
                "type": "object",
                "properties": {
                    "formula": {
                        "type": "string",
                        "description": "Chemical formula",
                    }
                },
                "required": ["formula"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_by_elements",
            "description": "Find materials containing specific elements (e.g., 'Si,C')",
            "parameters": {
                "type": "object",
                "properties": {
                    "elements": {
                        "type": "string",
                        "description": "Comma-separated elements",
                    }
                },
                "required": ["elements"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_by_jid",
            "description": "Get detailed info for a JARVIS ID (e.g., 'JVASP-1002')",
            "parameters": {
                "type": "object",
                "properties": {
                    "jid": {"type": "string", "description": "JARVIS ID"}
                },
                "required": ["jid"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_by_property",
            "description": "Find materials by property range (e.g., bandgap 2-3 eV)",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_name": {"type": "string"},
                    "min_val": {"type": "number"},
                    "max_val": {"type": "number"},
                    "elements": {"type": "string"},
                },
                "required": ["property_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_extreme",
            "description": "Find material with max/min property value",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_name": {"type": "string"},
                    "maximize": {"type": "boolean"},
                    "elements": {"type": "string"},
                    "formula": {"type": "string"},
                    "constraint_property": {"type": "string"},
                    "min_constraint": {"type": "number"},
                    "max_constraint": {"type": "number"},
                },
                "required": ["property_name"],
            },
        },
    },
    # ALIGNN
    {
        "type": "function",
        "function": {
            "name": "alignn_predict",
            "description": "Predict properties using ALIGNN ML model (formation energy, bandgap, moduli)",
            "parameters": {
                "type": "object",
                "properties": {
                    "poscar": {
                        "type": "string",
                        "description": "POSCAR structure",
                    },
                    "jid": {
                        "type": "string",
                        "description": "JARVIS ID (alternative)",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "alignn_ff_relax",
            "description": "Relax structure using ALIGNN force field",
            "parameters": {
                "type": "object",
                "properties": {"poscar": {"type": "string"}},
                "required": ["poscar"],
            },
        },
    },
    # SlakoNet
    {
        "type": "function",
        "function": {
            "name": "slakonet_bandstructure",
            "description": "Calculate electronic band structure and density of states using SlakoNet tight-binding model. Returns band gap, VBM, CBM values AND a band structure plot image. Works best for structures with ≤10 atoms.",
            "parameters": {
                "type": "object",
                "properties": {
                    "poscar": {
                        "type": "string",
                        "description": "POSCAR format structure string",
                    },
                    "energy_range_min": {
                        "type": "number",
                        "description": "Minimum energy for plot in eV (default: -8.0)",
                        "default": -8.0,
                    },
                    "energy_range_max": {
                        "type": "number",
                        "description": "Maximum energy for plot in eV (default: 8.0)",
                        "default": 8.0,
                    },
                },
                "required": ["poscar"],
            },
        },
    },
    # DiffractGPT
    {
        "type": "function",
        "function": {
            "name": "diffractgpt_predict",
            "description": "Predict structure from XRD peaks (format: '30.42(1.0),49.02(0.49)')",
            "parameters": {
                "type": "object",
                "properties": {
                    "formula": {"type": "string"},
                    "peaks": {
                        "type": "string",
                        "description": "XRD peaks as '2theta(intensity),...'",
                    },
                },
                "required": ["formula", "peaks"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "xrd_match",
            "description": "Match experimental XRD to database",
            "parameters": {
                "type": "object",
                "properties": {
                    "formula": {"type": "string"},
                    "xrd_pattern": {"type": "string"},
                },
                "required": ["formula", "xrd_pattern"],
            },
        },
    },
    # Intermat
    {
        "type": "function",
        "function": {
            "name": "generate_interface",
            "description": "Generate heterostructure interface",
            "parameters": {
                "type": "object",
                "properties": {
                    "film_poscar": {"type": "string"},
                    "substrate_poscar": {"type": "string"},
                    "film_indices": {
                        "type": "string",
                        "description": "Miller indices (e.g., '0_0_1')",
                    },
                    "substrate_indices": {"type": "string"},
                    "separation": {"type": "number"},
                },
                "required": ["film_poscar", "substrate_poscar"],
            },
        },
    },
]
