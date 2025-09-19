import argparse, sys, os, json
from .client import Agapi

def _print_json(obj):
    print(json.dumps(obj, indent=2))

def cmd_jarvis(args):
    client = Agapi()
    res = client.jarvis_dft_query(formula=args.formula, search=args.search)
    _print_json(res)

def cmd_alignn(args):
    client = Agapi()
    poscar_str = None
    if args.stdin:
        poscar_str = sys.stdin.read()
    res = client.alignn_query(file_path=args.file, poscar_string=poscar_str)
    _print_json(res)

def cmd_alignn_ff(args):
    client = Agapi()
    poscar_str = None
    if args.stdin:
        poscar_str = sys.stdin.read()
    res = client.alignn_ff_query(file_path=args.file, poscar_string=poscar_str)
    _print_json(res)

def cmd_protein(args):
    client = Agapi()
    blob = client.protein_fold_query(sequence=args.sequence, format=args.format)
    if args.format == "zip":
        out = args.out or "protein.zip"
        with open(out, "wb") as f:
            f.write(blob)
        print(f"Saved: {out}")
    else:
        _print_json(blob)

def cmd_pxrd(args):
    client = Agapi()
    res = client.pxrd_query(file_path=args.file, body_string=args.body_string)
    _print_json(res)

def main(argv=None):
    parser = argparse.ArgumentParser(prog="agapi", description="CLI for AtomGPT.org API")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("jarvis", help="Query JARVIS-DFT")
    p.add_argument("--formula", help="e.g., MoS2")
    p.add_argument("--search", help="e.g., -Mo-S")
    p.set_defaults(func=cmd_jarvis)

    p = sub.add_parser("alignn", help="Run ALIGNN")
    p.add_argument("--file", help="POSCAR path")
    p.add_argument("--stdin", action="store_true", help="read POSCAR from stdin")
    p.set_defaults(func=cmd_alignn)

    p = sub.add_parser("alignn-ff", help="Run ALIGNN-FF")
    p.add_argument("--file", help="POSCAR path")
    p.add_argument("--stdin", action="store_true", help="read POSCAR from stdin")
    p.set_defaults(func=cmd_alignn_ff)

    p = sub.add_parser("protein", help="Protein folding")
    p.add_argument("--sequence", required=True, help="amino acid sequence")
    p.add_argument("--format", default="json", choices=["json","zip"], help="response format")
    p.add_argument("--out", help="output path if format=zip")
    p.set_defaults(func=cmd_protein)

    p = sub.add_parser("pxrd", help="PXRD analysis")
    p.add_argument("--file", help="data file")
    p.add_argument("--body_string", help="raw body string instead of file")
    p.set_defaults(func=cmd_pxrd)

    args = parser.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    main()
