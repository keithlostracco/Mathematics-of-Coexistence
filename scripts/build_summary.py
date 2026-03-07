#!/usr/bin/env python3
"""Build the plain-language summary PDF from Markdown using Pandoc.

Converts supplementary/plain-language-summary.md into a reader-friendly
standalone PDF titled:

    "The Ethics Theorem: Why Cooperation Is a Law of Physics"

This is a separate build from build_paper.py — it does not run the
verification suite or regenerate figures, and it uses a simpler, more
accessible LaTeX style (larger font, generous margins, tighter ToC).

Images (if any) should be placed in:
    supplementary/plain-language-summary-images/

Usage:
    python scripts/build_summary.py                   # defaults
    python scripts/build_summary.py -o my_summary.pdf
    python scripts/build_summary.py --dry-run
    python scripts/build_summary.py --engine lualatex
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_FILE = "supplementary/ethics-theorem-guide.md"
IMAGES_DIR = "supplementary/ethics-theorem-guide-images"
LATEX_PREAMBLE = "supplementary/summary-preamble.tex"
DEFAULT_OUTPUT = "output/ethics-theorem-guide.pdf"

TITLE = "The Ethics Theorem: Why Cooperation Is a Law of Physics"
SUBTITLE = "A Plain-Language Guide to the Mathematics of Coexistence"
AUTHOR = "Keith Lostracco"

# Metadata tuned for a general-audience document: slightly larger font,
# generous margins, coloured hyperlinks, no numbered sections.
DEFAULT_METADATA: dict[str, str] = {
    "title": TITLE,
    "subtitle": SUBTITLE,
    "author": AUTHOR,
    "documentclass": "article",
    "geometry": "margin=1.25in",
    "fontsize": "12pt",
    "link-citations": "false",   # no citations in the summary
    "colorlinks": "true",
    "linkcolor": "NavyBlue",
    "urlcolor": "NavyBlue",
}


def find_repo_root() -> Path:
    here = Path(__file__).resolve().parent   # scripts/
    root = here.parent
    if (root / "supplementary").is_dir():
        return root
    return Path.cwd()


def build_pandoc_command(root: Path, output: Path, engine: str) -> list[str]:
    source = root / SOURCE_FILE
    if not source.exists():
        print(f"ERROR: {source} not found.", file=sys.stderr)
        sys.exit(1)

    cmd = ["pandoc", str(source)]

    # PDF engine
    cmd.extend([f"--pdf-engine={engine}"])

    # Output
    cmd.extend(["-o", str(output)])

    # Metadata
    for key, value in DEFAULT_METADATA.items():
        cmd.extend(["-V", f"{key}={value}"])

    # Resource path: lets Pandoc resolve images in the images directory
    images_dir = root / IMAGES_DIR
    cmd.extend([f"--resource-path=.:{images_dir}:{root}"])

    # LaTeX preamble (Unicode character mappings)
    preamble = root / LATEX_PREAMBLE
    if preamble.exists():
        cmd.extend([f"--include-in-header={preamble}"])

    # Standalone document
    cmd.append("-s")

    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the plain-language summary PDF via Pandoc.",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help=f"Output PDF path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--engine",
        default="xelatex",
        choices=["xelatex", "lualatex", "pdflatex", "tectonic"],
        help="LaTeX engine (default: xelatex)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the Pandoc command without executing it",
    )
    args = parser.parse_args()

    root = find_repo_root()

    output = Path(args.output) if args.output else root / DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)

    if not shutil.which("pandoc"):
        print("ERROR: pandoc not found on PATH.", file=sys.stderr)
        print("  Install from https://pandoc.org/installing.html", file=sys.stderr)
        return 1

    cmd = build_pandoc_command(root, output, args.engine)

    if args.dry_run:
        print("Would run:")
        print("  " + " \\\n    ".join(cmd))
        return 0

    print(f"Building {output} ...")
    print(f'  Title:  "{TITLE}"')
    print(f"  Source: {root / SOURCE_FILE}")
    print(f"  Engine: {args.engine}")
    print()

    result = subprocess.run(cmd, cwd=root)

    if result.returncode == 0:
        size_kb = output.stat().st_size / 1024
        print(f"\n✓ PDF written to {output} ({size_kb:.0f} KB)")
    else:
        print(f"\n✗ Pandoc exited with code {result.returncode}", file=sys.stderr)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
