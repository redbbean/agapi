# agapi

A tiny Python SDK + CLI for the AtomGPT.org API (AGAPI).

## Install (dev)

```bash
pip install agapi jarvis-tools
```

Set your key once (recommended):

Website: https://atomgpt.org/

Profile >> Settings >> Account >> API Keys >> Show



## Quickstart

```python
from agapi import Agapi

client = Agapi(api_key="sk-")  # reads env vars
# JARVIS-DFT by formula
r = client.jarvis_dft_query(formula="MoS2")
print(r)

# JARVIS-DFT by search
r = client.jarvis_dft_query(search="-Mo-S")
print(r)

# ALIGNN from POSCAR path
r = client.alignn_query(file_path="POSCAR")
print(r.keys())

# ALIGNN-FF from POSCAR string
r = client.alignn_ff_query(poscar_string=open("POSCAR").read())
print(r)

# Protein fold (returns binary content if format=zip)
zbytes = client.protein_fold_query(sequence="AAAAA", format="zip")
open("protein.zip", "wb").write(zbytes)

# PXRD from a data file
r = client.pxrd_query(file_path="Lab6data.dat")
print(r)
```

# TODO
## CLI

```bash
# JARVIS-DFT by formula
agapi jarvis --formula MoS2

# JARVIS-DFT by search
agapi jarvis --search "-Mo-S"

# ALIGNN (file or stdin)
agapi alignn --file POSCAR
cat POSCAR | agapi alignn --stdin

# ALIGNN-FF
agapi alignn-ff --file POSCAR

# Protein fold
agapi protein --sequence AAAAA --format zip --out protein.zip

# PXRD
agapi pxrd --file Lab6data.dat
```
