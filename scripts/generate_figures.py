#!/usr/bin/env python3
"""Generate all paper figures from pre-computed data.

Each figure script in scripts/figures/ loads its data from a JSON file
in output/data/ (produced by the corresponding verification script)
and renders a PNG to output/figures/.

Usage:
    python scripts/generate_figures.py           # render all figures
    python scripts/generate_figures.py --dry-run  # show what would run
"""

from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
import time
from pathlib import Path

FIGURE_SCRIPT_GLOB = "scripts/figures/fig_*.py"


def find_repo_root() -> Path:
    here = Path(__file__).resolve().parent
    root = here.parent
    if (root / "paper").is_dir():
        return root
    return Path.cwd()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate all paper figures from pre-computed data.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List scripts that would run without executing them",
    )
    args = parser.parse_args()

    root = find_repo_root()
    fig_scripts = sorted(Path(p) for p in glob.glob(str(root / FIGURE_SCRIPT_GLOB)))

    if not fig_scripts:
        print("WARNING: No figure scripts found matching", FIGURE_SCRIPT_GLOB,
              file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"Figure scripts ({len(fig_scripts)}):")
        for s in fig_scripts:
            ex = "✓" if s.exists() else "✗ MISSING"
            print(f"  {ex}  {s.relative_to(root)}")
        return 0

    print("=" * 60)
    print(f"  Generating {len(fig_scripts)} figures")
    print("=" * 60)

    t0 = time.time()
    ok = True

    for script in fig_scripts:
        name = script.name
        t1 = time.monotonic()
        env = os.environ.copy()
        env["PYTHONPATH"] = str(root)
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(root),
            capture_output=True,
            text=True,
            env=env,
        )
        elapsed = time.monotonic() - t1

        if result.returncode != 0:
            print(f"  ✗ {name}  FAILED ({elapsed:.1f}s)")
            if result.stderr:
                for line in result.stderr.strip().splitlines()[-5:]:
                    print(f"    {line}")
            ok = False
        else:
            print(f"  ✓ {name}  ({elapsed:.1f}s)")

    elapsed = time.time() - t0
    print()
    print("=" * 60)
    if ok:
        print(f"  ✓ All figures generated ({elapsed:.1f}s)")
    else:
        print(f"  ✗ Some figure scripts failed ({elapsed:.1f}s)")
    print("=" * 60)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
