"""fable_scanner scan -- lint CLAUDE.md / skills / agent configs for Fable 5 anti-patterns.

    python -m fable_scanner scan <path>
    python -m fable_scanner scan <path> --format json

Walks a file or directory, classifies each file as prompt (.md/.txt) or
config (.json/.yaml/.yml), and runs the rules in rules.py against it.
"""
import json
import sys
from pathlib import Path

from fable_scanner.rules import run_rules

PROMPT_EXTS = {".md", ".txt", ".prompt"}
CONFIG_EXTS = {".json", ".yaml", ".yml"}
IGNORE_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "dist", "build"}


def classify(path):
    ext = path.suffix.lower()
    if ext in PROMPT_EXTS:
        return "prompt"
    if ext in CONFIG_EXTS:
        return "config"
    return None


def collect_files(target):
    target = Path(target)
    if target.is_file():
        kind = classify(target)
        return [(target, kind)] if kind else []
    out = []
    for p in sorted(target.rglob("*")):
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        if p.is_file():
            kind = classify(p)
            if kind:
                out.append((p, kind))
    return out


def scan_path(target):
    """Returns {file: [findings]} for every prompt/config file under target."""
    results = {}
    for path, kind in collect_files(target):
        text = path.read_text(encoding="utf-8")
        findings = run_rules(text, kind)
        if findings:
            results[str(path)] = findings
    return results


def main(argv):
    if not argv:
        print("usage: python -m fable_scanner scan <path> [--format json]")
        return 2
    target = argv[0]
    as_json = "--format" in argv and "json" in argv[argv.index("--format") + 1 : argv.index("--format") + 2]

    if not Path(target).exists():
        print(f"scan: no such path: {target}", file=sys.stderr)
        return 2

    results = scan_path(target)

    if as_json:
        print(json.dumps(
            {f: [{"rule": h["rule"]["id"], "severity": h["rule"]["severity"],
                  "line": h["line"], "match": h["match"], "why": h["rule"]["why"],
                  "docs": h["rule"]["docs"]} for h in hits]
             for f, hits in results.items()},
            indent=2,
        ))
    else:
        errors = 0
        for f, hits in results.items():
            print(f"\n{f}")
            for h in hits:
                r = h["rule"]
                if r["severity"] == "error":
                    errors += 1
                print(f"  {h['line']:>4}  {r['severity']:<5}  {r['id']}  {r['why']}")
                print(f"        {r['docs']}")
        total = sum(len(v) for v in results.values())
        print(f"\nsummary: {len(results)} file(s) with findings, {total} total ({errors} error-severity)")
        return 1 if errors else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
