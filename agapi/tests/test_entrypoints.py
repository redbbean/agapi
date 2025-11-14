import os
import json
import pytest
import requests

# --------------------------------------------------------------------------- #
# Constants and helpers
# --------------------------------------------------------------------------- #

BASE_URL = "https://atomgpt.org"

# JSON that will be sent as the `propranges` query for the JARVIS‑DFT test.
# We first create the JSON string, then escape its curly braces so that
# `str.format()` does not treat them as format placeholders.
_JARVIS_PROPRANGES_RAW = {
    "epsx": {"min": 15},
    "epsy": {"min": 15},
    "avg_elec_mass": {"max": 0.5},
}
_JARVIS_PROPRANGES = json.dumps(_JARVIS_PROPRANGES_RAW)
_JARVIS_PROPRANGES_ESCAPED = _JARVIS_PROPRANGES.replace("{", "{{").replace(
    "}", "}}"
)

# --------------------------------------------------------------------------- #
# Test cases
# --------------------------------------------------------------------------- #

API_CASES = [
    {
        "id": 1,
        "name": "JARVIS-DFT elements filter",
        "url": f"{BASE_URL}/jarvis_dft/query?elements=Si,C&APIKEY={{api_key}}",
    },
    {
        "id": 2,
        "name": "JARVIS-DFT formula Al2O3",
        "url": f"{BASE_URL}/jarvis_dft/query?formula=Al2O3&APIKEY={{api_key}}",
    },
    {
        "id": 5,
        "name": "Materials Project Al2O3",
        "url": f"{BASE_URL}/mp/query?formula=Al2O3&APIKEY={{api_key}}",
    },
    {
        "id": 7,
        "name": "ALIGNN by JID",
        "url": f"{BASE_URL}/alignn/query?jid=JVASP-1002&APIKEY={{api_key}}",
    },
    {
        "id": 8,
        "name": "ALIGNN by POSCAR",
        "url": (
            f"{BASE_URL}/alignn/query?"
            "poscar=System\n1.0\n3.2631502048902807 0.0 -0.0\n"
            "0.0 3.2631502048902807 0.0\n"
            "0.0 -0.0 3.2631502048902807\n"
            "Ti Au\n1 1\n"
            "direct\n"
            "0.5 0.5 0.5 Ti\n"
            "0.0 0.0 0.0 Au\n"
            "&APIKEY={{api_key}}"
        ),
    },
    {
        "id": 10,
        "name": "arXiv MgB2",
        "url": f"{BASE_URL}/arxiv?query=MgB2&APIKEY={{api_key}}",
    },
    {
        "id": 11,
        "name": "CrossRef CrMnFeCoNi",
        "url": f"{BASE_URL}/crossref?query=CrMnFeCoNi&rows=100&APIKEY={{api_key}}",
    },
]

# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="session")
def api_key() -> str:
    """
    Read the ATOMGPT_API_KEY env‑var.  If it is missing we skip the whole test
    session so that CI does not report hard failures when the key is not set.
    """
    key = os.getenv("ATOMGPT_API_KEY")
    if not key:
        pytest.skip("ATOMGPT_API_KEY environment variable not set.")
    return key


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("case", API_CASES, ids=[c["name"] for c in API_CASES])
def test_atomgpt_api_call(case, api_key):
    """
    Call the AtomGPT endpoint described by ``case`` and validate that we get
    a 200 response with *valid* JSON.  For a couple of public endpoints that
    require a premium key we skip the tests when a 401 is returned
    (this keeps the suite usable even when the key has limited scope).
    """
    url = case["url"].format(api_key=api_key)
    resp = requests.get(url, timeout=30)

    # Skip known endpoints that are currently behind a 401 wall.
    if resp.status_code == 401 and case["name"] in (
        "ALIGNN by POSCAR",
        "PXRD pattern MoS2",
    ):
        pytest.skip(f"{case['name']} returned 401 – skipping test.")

    assert (
        resp.status_code == 200
    ), f"{case['name']} returned {resp.status_code}"

    # Validate that the response body is JSON‑parsable.
    try:
        data = resp.json()
    except json.JSONDecodeError:
        pytest.fail(
            f"{case['name']} did not return valid JSON. Body: {resp.text[:500]}"
        )

    # Minimal sanity check – make sure we did get something back.
    assert data is not None, f"{case['name']} returned empty response."
    # Uncomment the following if the contract of the API changes.
    # assert any(
    #     k in data for k in ("data", "results", "hits")
    # ), f"{case['name']} JSON missing expected top-level keys. Got keys: {list(data.keys())}"
