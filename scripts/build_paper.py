#!/usr/bin/env python3
"""Build the paper PDF from Markdown sources using Pandoc + citeproc.

Concatenates all paper sections in order, runs Pandoc with --citeproc
to resolve [@BibKey] citations against references.bib, and produces
a PDF via the selected LaTeX engine.

Prerequisites (system-level):
    - Pandoc >= 3.0     https://pandoc.org/installing.html
    - LaTeX engine      TeX Live, MiKTeX, or TinyTeX

Usage:
    python scripts/build_paper.py                   # defaults
    python scripts/build_paper.py -o my_paper.pdf   # custom output
    python scripts/build_paper.py --engine lualatex  # different engine
    python scripts/build_paper.py --dry-run          # show command only
    python scripts/build_paper.py --skip-verify      # skip verification suite
    python scripts/build_paper.py --skip-figures     # skip figure regeneration

Pre-build steps (unless skipped):
    1. Run the mathematical verification suite (scripts/run_verification.py -q).
       Build aborts if any check fails.
    2. Regenerate all figures from scripts/figures/fig_*.py.
"""

from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Paper sections in reading order.
# 00-abstract.md is excluded here — its body is passed to Pandoc as the
# `abstract` metadata variable so it renders before the Table of Contents.
PAPER_SECTIONS = [
    "01-introduction.md",
    "02-literature-review.md",
    "03-axioms-definitions.md",
    "04-rights-constraints.md",
    "05-ethics-equilibrium.md",
    "06-stress-testing.md",
    "07-applications.md",
    "08-limitations-scope-future.md",
    "09-conclusion.md",
]

BIBLIOGRAPHY = "paper/references.bib"
LATEX_PREAMBLE = "paper/latex-preamble.tex"
METADATA_FILE = "paper/metadata.yaml"

# Supplementary Appendix A files, appended after the main text.
# Pandoc will receive a raw-LaTeX \appendix marker before these so that
# LaTeX numbers them A, B, C … instead of continuing arabic section numbers.
APPENDIX_SECTIONS = [
    "supplementary/A-mathematical-derivations/lagrangian-constraints.md",
    "supplementary/A-mathematical-derivations/thermodynamic-friction.md",
    "supplementary/A-mathematical-derivations/information-negentropy.md",
    "supplementary/A-mathematical-derivations/game-theory-payoffs.md",
    "supplementary/A-mathematical-derivations/value-dynamics.md",
    "supplementary/E-conceptual-overview/conceptual-overview.md",
]

# numbersections is intentionally absent from metadata.yaml: when unset, Pandoc's
# LaTeX template emits \setcounter{secnumdepth}{-\maxdimen}, suppressing all
# auto-numbering.  Passing numbersections=false (string) is truthy in Mustache
# and re-enables it.


# ---------------------------------------------------------------------------
# Pre-build: verification and figure generation
# ---------------------------------------------------------------------------

VERIFICATION_SCRIPT = "scripts/run_verification.py"
FIGURE_GENERATION_SCRIPT = "scripts/generate_figures.py"
FIGURE_SCRIPT_GLOB = "scripts/figures/fig_*.py"


def run_verification(root: Path) -> bool:
    """Run the mathematical verification suite in quiet mode.

    Returns True if all checks pass, False otherwise.
    """
    script = root / VERIFICATION_SCRIPT
    if not script.exists():
        print(f"WARNING: {script} not found — skipping verification", file=sys.stderr)
        return True

    print("Running mathematical verification suite ...")
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, str(script), "-q"],
        cwd=root,
    )
    elapsed = time.time() - t0

    if result.returncode == 0:
        print(f"  ✓ Verification passed ({elapsed:.1f}s)")
        return True
    else:
        print(
            f"  ✗ Verification FAILED (exit code {result.returncode}, {elapsed:.1f}s)",
            file=sys.stderr,
        )
        print("  Build aborted — fix verification failures before building.", file=sys.stderr)
        return False


def generate_figures(root: Path) -> bool:
    """Regenerate all figures from pre-computed data.

    Delegates to scripts/generate_figures.py, which runs each
    scripts/figures/fig_*.py script.  Figure data (JSON) must already
    exist in output/data/.

    Returns True if all scripts succeed, False if any fail.
    """
    script = root / FIGURE_GENERATION_SCRIPT
    if not script.exists():
        # Fallback: run figure scripts directly
        print(f"WARNING: {script} not found — running figure scripts directly",
              file=sys.stderr)
        return _generate_figures_legacy(root)

    print("Generating figures ...")
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
    )
    elapsed = time.time() - t0

    if result.returncode == 0:
        return True
    else:
        print(f"  ✗ Figure generation had failures ({elapsed:.1f}s)", file=sys.stderr)
        return False


def _generate_figures_legacy(root: Path) -> bool:
    """Fallback: run fig_*.py scripts directly without data generation step."""
    pattern = str(root / FIGURE_SCRIPT_GLOB)
    scripts = sorted(glob.glob(pattern))

    if not scripts:
        print("WARNING: No figure scripts found — skipping figure generation", file=sys.stderr)
        return True

    print(f"Regenerating {len(scripts)} figures ...")
    t0 = time.time()
    ok = True

    for script_path in scripts:
        name = Path(script_path).stem
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  ✗ {name} failed (exit code {result.returncode})", file=sys.stderr)
            if result.stderr:
                # Show last 5 lines of stderr for diagnostics
                for line in result.stderr.strip().splitlines()[-5:]:
                    print(f"    {line}", file=sys.stderr)
            ok = False
        else:
            print(f"  ✓ {name}")

    elapsed = time.time() - t0
    if ok:
        print(f"  All figures generated ({elapsed:.1f}s)")
    else:
        print(f"  Some figure scripts failed ({elapsed:.1f}s)", file=sys.stderr)

    return ok


def extract_abstract_text(root: Path) -> str:
    """Return the body of 00-abstract.md, stripped of its heading and keywords line.

    The returned text is used as Pandoc's ``abstract`` metadata variable, which
    the default LaTeX template renders *before* the Table of Contents.
    """
    abstract_path = root / "paper" / "00-abstract.md"
    if not abstract_path.exists():
        return ""

    lines = abstract_path.read_text(encoding="utf-8").splitlines()
    body: list[str] = []
    in_body = False

    for line in lines:
        # Skip the section heading
        if line.startswith("# "):
            continue
        # Stop at the Keywords line
        if line.startswith("**Keywords:"):
            break
        if line.strip() or in_body:
            in_body = True
            body.append(line)

    # Strip leading/trailing blank lines
    return "\n".join(body).strip()


def find_repo_root() -> Path:
    """Walk up from this script's location to find the repo root."""
    here = Path(__file__).resolve().parent
    # The script lives in scripts/ — go up one level
    root = here.parent
    if (root / "paper").is_dir():
        return root
    # Fallback: current working directory
    return Path.cwd()


def build_pandoc_command(
    root: Path,
    output: Path,
    engine: str,
    abstract_file: Path | None = None,
    appendix_marker: Path | None = None,
    extra_args: list[str] | None = None,
) -> list[str]:
    """Construct the full Pandoc command."""
    cmd = ["pandoc"]

    # Input files (in order)
    for section in PAPER_SECTIONS:
        section_path = root / "paper" / section
        if not section_path.exists():
            print(f"WARNING: {section_path} not found — skipping", file=sys.stderr)
            continue
        cmd.append(str(section_path))

    # Appendix sections (supplementary A), preceded by \appendix marker
    if appendix_marker and appendix_marker.exists():
        cmd.append(str(appendix_marker))
    for section in APPENDIX_SECTIONS:
        section_path = root / section
        if not section_path.exists():
            print(f"WARNING: {section_path} not found — skipping", file=sys.stderr)
            continue
        cmd.append(str(section_path))

    # Bibliography and citation processing
    cmd.extend([
        "--citeproc",
        f"--bibliography={root / BIBLIOGRAPHY}",
    ])

    # PDF engine
    cmd.extend([f"--pdf-engine={engine}"])

    # Output
    cmd.extend(["-o", str(output)])

    # Paper metadata (title, author, DOI, formatting) from metadata.yaml
    metadata_path = root / METADATA_FILE
    if metadata_path.exists():
        cmd.extend([f"--metadata-file={metadata_path}"])
    else:
        print(f"WARNING: {metadata_path} not found — title page will be empty",
              file=sys.stderr)

    # Abstract metadata (renders before TOC in Pandoc's default LaTeX template)
    if abstract_file and abstract_file.exists():
        cmd.extend([f"--metadata-file={abstract_file}"])

    # LaTeX preamble (section page-breaks etc.)
    preamble = root / LATEX_PREAMBLE
    if preamble.exists():
        cmd.extend([f"--include-in-header={preamble}"])

    # Figure resource path — lets Pandoc resolve output/figures/*.png references
    cmd.extend([f"--resource-path=.:{root / 'output' / 'figures'}"])

    # Table of contents
    cmd.append("--toc")

    # Standalone document
    cmd.append("-s")

    # Extra user-supplied arguments
    if extra_args:
        cmd.extend(extra_args)

    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the paper PDF from Markdown via Pandoc + citeproc.",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output PDF path (default: output/paper.pdf)",
    )
    parser.add_argument(
        "--engine",
        default="xelatex",
        choices=["xelatex", "lualatex", "pdflatex", "tectonic"],
        help="LaTeX engine for Pandoc (default: xelatex)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the Pandoc command without executing it",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip the mathematical verification suite",
    )
    parser.add_argument(
        "--skip-figures",
        action="store_true",
        help="Skip figure regeneration",
    )
    parser.add_argument(
        "extra",
        nargs="*",
        help="Extra arguments passed directly to Pandoc",
    )

    args = parser.parse_args()

    root = find_repo_root()

    # Determine output path
    if args.output:
        output = Path(args.output)
    else:
        output = root / "output" / "paper.pdf"

    # Ensure output directory exists
    output.parent.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Pre-build steps: verification and figure generation
    # -----------------------------------------------------------------------
    if not args.dry_run:
        if not args.skip_verify:
            if not run_verification(root):
                return 1
        else:
            print("Skipping verification (--skip-verify)")

        if not args.skip_figures:
            if not generate_figures(root):
                print(
                    "WARNING: Some figures failed to generate — continuing build",
                    file=sys.stderr,
                )
        else:
            print("Skipping figure generation (--skip-figures)")

        print()  # visual separator before Pandoc output

    # Check Pandoc is installed
    if not shutil.which("pandoc"):
        print("ERROR: pandoc not found on PATH.", file=sys.stderr)
        print("  Install from https://pandoc.org/installing.html", file=sys.stderr)
        return 1

    # Extract abstract and write to a temp YAML metadata file
    abstract_text = extract_abstract_text(root)
    tmp_dir = tempfile.mkdtemp()
    abstract_file: Path | None = None
    if abstract_text:
        abstract_file = Path(tmp_dir) / "abstract.yaml"
        # Replace blank lines (paragraph breaks) with explicit LaTeX \par\medskip
        # so spacing survives the abstract environment regardless of \parskip.
        paragraphs = [p.strip() for p in abstract_text.split("\n\n") if p.strip()]
        joined = "\n\n`\\par\\medskip`{=latex}\n\n".join(paragraphs)
        # YAML literal block scalar preserves LaTeX math and line breaks correctly
        yaml_lines = ["abstract: |"]
        for line in joined.splitlines():
            yaml_lines.append(f"  {line}" if line.strip() else "  ")
        abstract_file.write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")

    # Write a raw-LaTeX appendix marker injected before supplementary sections
    appendix_marker = Path(tmp_dir) / "appendix-marker.md"
    appendix_marker.write_text(
        "`\\appendix`{=latex}\n",
        encoding="utf-8",
    )

    # Build and run the command
    cmd = build_pandoc_command(root, output, args.engine, abstract_file, appendix_marker, args.extra or None)

    if args.dry_run:
        print("Would run:")
        print("  " + " \\\n    ".join(cmd))
        # Clean up temp files
        if abstract_file and abstract_file.exists():
            abstract_file.unlink()
        appendix_marker.unlink(missing_ok=True)
        os.rmdir(tmp_dir)
        return 0

    print(f"Building {output} ...")
    print(f"  Engine: {args.engine}")
    print(f"  Sections: {len(PAPER_SECTIONS)} main + {len(APPENDIX_SECTIONS)} appendix (abstract via metadata)")
    print()

    result = subprocess.run(cmd, cwd=root)

    # Clean up temp files
    if abstract_file and abstract_file.exists():
        abstract_file.unlink()
    appendix_marker.unlink(missing_ok=True)
    os.rmdir(tmp_dir)

    if result.returncode == 0:
        size_kb = output.stat().st_size / 1024
        print(f"\n✓ PDF written to {output} ({size_kb:.0f} KB)")
    else:
        print(f"\n✗ Pandoc exited with code {result.returncode}", file=sys.stderr)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
