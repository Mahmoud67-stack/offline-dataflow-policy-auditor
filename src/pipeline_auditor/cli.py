"""Command-line interface."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .core import AnalysisError, analyze, load_json


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit a local pipeline manifest against a policy")
    parser.add_argument("manifest")
    parser.add_argument("--policy", required=True)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)
    try:
        report = analyze(load_json(args.manifest), load_json(args.policy))
    except AnalysisError as exc:
        if args.json:
            print(json.dumps({"error": str(exc)}, sort_keys=True))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(report, sort_keys=True, separators=(",", ":"))
    if args.json:
        print(text)
    else:
        print("clean" if not report["violations"] else f"{len(report['violations'])} policy violation(s)")
        for item in report["violations"]:
            print(f"{item['source']} -> {item['sink']}: {' -> '.join(item['path'])}")
    return 1 if report["violations"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
