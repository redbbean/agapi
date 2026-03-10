---
title: Materials Explorer
description: Search and explore 76K+ materials in JARVIS-DFT
tags:
  - explore
  - database
  - search
---

# Materials Explorer

Search and explore **76,000+ materials** in the JARVIS-DFT database. Filter by formula, elements, space group, band gap, formation energy, and 50+ properties.

[:material-open-in-new: Open App](https://atomgpt.org/materials_explorer){ .md-button .md-button--primary }
[:material-github: Source](https://github.com/atomgptlab/jarvis){ .md-button }

---

## Overview

The Materials Explorer provides full-text search across the JARVIS-DFT database with filters for chemical composition, crystal structure, electronic properties, and more. Each material links to its detailed JARVIS data page.

!!! info "Data Source"
    **JARVIS-DFT** (`dft_3d`) — 76,000+ materials computed with OptB88vdW functional.
    Updated from `jarvis.db.figshare.data('dft_3d')`.

## Quick Start

1. Enter a formula (e.g., `SrTiO3`) or elements (e.g., `Si, Ge`)
2. Apply filters for band gap range, formation energy, or space group
3. Click **Search** to find matching materials
4. Click any result row to view detailed properties
5. Click the JARVIS ID to open the full XML data page

## Features

- **Search by formula**: Exact or partial formula matching
- **Element filter**: ANY/ALL/EXACT mode with interactive periodic table
- **Property filters**: Band gap, formation energy, bulk/shear modulus, magnetic moment, spillage, SLME, and more
- **Results table**: Sortable by any property, paginated
- **Detail view**: Full property card with JARVIS XML link

## API Reference

### Search Materials

```
POST /materials_explorer/search
```

**Request Body:**

```json
{
  "jid": "JVASP-1002",
  "formula": "Si",
  "spacegroup": "Fd-3m",
  "elements": ["Si", "Ge"],
  "element_mode": "any",
  "bandgap_min": 0.5,
  "bandgap_max": 3.0,
  "formation_energy_min": -2.0,
  "formation_energy_max": 0.0
}
```

**Response:**

```json
{
  "total": 1234,
  "results": [
    {
      "jid": "JVASP-1002",
      "formula": "Si",
      "spg_symbol": "Fd-3m",
      "optb88vdw_bandgap": 0.611,
      "formation_energy_peratom": -0.005,
      "bulk_modulus_kv": 88.89,
      "shear_modulus_gv": 51.47,
      "magmom_oszicar": 0.0
    }
  ]
}
```

!!! note "Authentication"
    All POST endpoints require authentication. Include your token in the header:
    ```
    Authorization: Bearer YOUR_TOKEN
    ```

### Get Material Details

```
GET /materials_explorer/detail/{jid}
```

Returns full property set for a single material.

## Python Examples

=== "Search by formula"

    ```python
    import requests

    response = requests.post(
        "https://atomgpt.org/materials_explorer/search",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        json={"formula": "SrTiO3"},
    )
    data = response.json()
    print(f"Found {data['total']} materials")
    for m in data["results"][:5]:
        print(f"  {m['jid']}: {m['formula']} gap={m['optb88vdw_bandgap']} eV")
    ```

=== "Search by elements"

    ```python
    import requests

    response = requests.post(
        "https://atomgpt.org/materials_explorer/search",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        json={
            "elements": ["Ti", "O"],
            "element_mode": "all",
            "bandgap_min": 1.0,
        },
    )
    data = response.json()
    for m in data["results"][:10]:
        print(f"{m['jid']}: {m['formula']} ({m['spg_symbol']}) gap={m['optb88vdw_bandgap']}")
    ```

=== "AGAPI Agent"

    ```python
    from agapi import AtomGPTClient

    client = AtomGPTClient(api_key="YOUR_KEY")
    results = client.search_materials(
        elements=["Si", "Ge"],
        bandgap_min=0.5,
        bandgap_max=2.0,
    )
    for m in results:
        print(m.formula, m.bandgap)
    ```

=== "Direct JARVIS"

    ```python
    from jarvis.db.figshare import data

    dft = data("dft_3d")
    # Filter for Si-containing materials with gap > 1 eV
    results = [
        e for e in dft
        if "Si" in e.get("atoms", {}).get("elements", [])
        and e.get("optb88vdw_bandgap") not in (None, "na")
        and float(e["optb88vdw_bandgap"]) > 1.0
    ]
    print(f"Found {len(results)} Si materials with gap > 1 eV")
    ```

## Related Apps

- [Electronic DOS](electronic-dos.md) — View density of states for any material
- [Elastic Tensor](elastic-tensor.md) — Explore mechanical properties
- [Periodic Table](periodic-table.md) — Heatmap of properties across elements
- [OPTIMADE Explorer](optimade.md) — Query using OPTIMADE standard syntax

## References

- K. Choudhary, Comp. Mat. Sci. 259, 114063 (2025). [:material-link: DOI](https://doi.org/10.1016/j.commatsci.2025.114063)
- K. Choudhary et al., npj Comp. Mat. 6, 173 (2020). [:material-link: DOI](https://doi.org/10.1038/s41524-020-00440-1)
- JARVIS-DFT Database: [jarvis.nist.gov](https://jarvis.nist.gov)
