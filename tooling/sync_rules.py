#!/usr/bin/env python3
"""Keep the portable ruleset copies in sync with AGENTS.md.

Several agent hosts read a rules file from their own path rather than a shared
one, so the same text has to exist in several places. Copies drift silently;
this catches that.

Usage:
    python tooling/sync_rules.py           # check, exit 1 if any copy is stale
    python tooling/sync_rules.py --fix     # rewrite stale copies from AGENTS.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "AGENTS.md"

# Host → path it reads its rules from.
COPIES = {
    "Cursor": ROOT / ".cursor" / "rules" / "cato.md",
    "Cline": ROOT / ".clinerules" / "cato.md",
    "GitHub Copilot": ROOT / ".github" / "copilot-instructions.md",
}


def stale() -> list[tuple[str, Path]]:
    """Return the copies that don't match the source."""
    expected = SOURCE.read_text(encoding="utf-8")
    out = []
    for host, path in COPIES.items():
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            out.append((host, path))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix", action="store_true", help="rewrite stale copies")
    args = parser.parse_args()

    if not SOURCE.exists():
        print(f"Missing source ruleset at {SOURCE}", file=sys.stderr)
        return 1

    drifted = stale()

    if not drifted:
        print(f"All {len(COPIES)} ruleset copies match AGENTS.md.")
        return 0

    if args.fix:
        text = SOURCE.read_text(encoding="utf-8")
        for host, path in drifted:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print(f"Updated {host}: {path.relative_to(ROOT)}")
        return 0

    for host, path in drifted:
        print(f"Stale: {host} — {path.relative_to(ROOT)}", file=sys.stderr)
    print("\nRun with --fix to update them.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
