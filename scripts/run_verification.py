#!/usr/bin/env python3
"""Run all verification scripts and print a consolidated final report.

Executes each core verify_*.py script in turn, captures its output,
parses the per-script pass/fail totals, and prints a single summary
table at the end.

Usage:
    python scripts/run_verification.py            # run all, summary table only
    python scripts/run_verification.py -v         # verbose — show per-check output
    python scripts/run_verification.py --dry-run  # list scripts that would run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 output on Windows so the runner's own output is clean
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Script discovery
# ---------------------------------------------------------------------------

# Folders to scan for verify_*.py scripts, relative to repo root.
# Scripts are discovered automatically — just drop a new file in the folder.
SCRIPT_DIRS = [
    "scripts/simulations/derivations",
    "scripts/simulations/applied",
    # "scripts/simulations/applied_extras",
]

# Add script filenames here to exclude them from the suite.
# Example:  SKIP = {"verify_experimental.py"}
SKIP: set[str] = set()


def discover_scripts(root: Path) -> list[str]:
    """Scan SCRIPT_DIRS for verify_*.py and return sorted relative paths."""
    found: list[str] = []
    for d in SCRIPT_DIRS:
        folder = root / d
        if not folder.is_dir():
            continue
        for f in sorted(folder.glob("verify_*.py")):
            if f.name not in SKIP:
                found.append(str(f.relative_to(root)))
    return found

# Matches any of the summary formats the scripts use:
#   SUMMARY: 90 passed, 0 failed
#   FINAL RESULT: 107 passed, 0 failed, 107 total -- 100% PASS
#   FINAL RESULTS: 107 passed, 1 failed, 108 total
#   TOTAL: 90/90 passed, 0 failed
_TOTAL_RE = re.compile(
    r"(\d+)\s+passed,\s*(\d+)\s+failed(?:[,\s]+(\d+)\s+total)?",
    re.IGNORECASE,
)

# Matches individual check lines:  [PASS] Check name  (detail)
_CHECK_RE = re.compile(
    r"\[(PASS|FAIL)\]\s+(.+?)(?:\s{2,}\((.*)\))?\s*$",
)


def parse_checks(output: str) -> list[dict]:
    """Extract individual [PASS]/[FAIL] check results from script output."""
    checks = []
    for line in output.splitlines():
        m = _CHECK_RE.search(line)
        if m:
            checks.append({
                "status": m.group(1),
                "name": m.group(2).strip(),
                "detail": m.group(3).strip() if m.group(3) else None,
            })
    return checks


def find_repo_root() -> Path:
    here = Path(__file__).resolve().parent
    root = here.parent
    if (root / "modules").is_dir():
        return root
    return Path.cwd()


# ---------------------------------------------------------------------------
# Colour helpers (Windows Terminal / Unix)
# ---------------------------------------------------------------------------

def _supports_colour() -> bool:
    try:
        import os
        return (hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and os.name != "nt") or (
            os.name == "nt" and bool(os.environ.get("WT_SESSION"))
        )
    except Exception:
        return False


_USE_COLOUR = _supports_colour()

def _green(s: str) -> str:  return f"\033[32m{s}\033[0m" if _USE_COLOUR else s
def _red(s: str) -> str:    return f"\033[31m{s}\033[0m" if _USE_COLOUR else s
def _yellow(s: str) -> str: return f"\033[33m{s}\033[0m" if _USE_COLOUR else s
def _bold(s: str) -> str:   return f"\033[1m{s}\033[0m"  if _USE_COLOUR else s
def _dim(s: str) -> str:    return f"\033[90m{s}\033[0m" if _USE_COLOUR else s


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_script(script: Path, root: Path) -> tuple[int, int, int, float, str]:
    """Run a single verification script.

    Returns (passed, failed, total, elapsed_sec, output_text).
    """
    t0 = time.monotonic()
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(root),
        env=env,
    )
    elapsed = time.monotonic() - t0
    output = result.stdout + (result.stderr if result.stderr else "")

    # Parse summary line from output
    m = _TOTAL_RE.search(output)
    if m:
        passed = int(m.group(1))
        failed = int(m.group(2))
        total  = int(m.group(3)) if m.group(3) else passed + failed
    elif result.returncode != 0:
        # Script crashed before printing TOTAL
        passed, total, failed = 0, 0, 1
    else:
        # Script ran cleanly but didn't print TOTAL — treat as 0/0
        passed, total, failed = 0, 0, 0

    return passed, failed, total, elapsed, output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all verification scripts and print a consolidated report.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show full per-check output for each script (default: summary only)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List scripts that would run without executing them",
    )
    args = parser.parse_args()

    root = find_repo_root()
    script_paths = discover_scripts(root)
    scripts = [root / s for s in script_paths]

    if not scripts:
        print("No verification scripts found.")
        return 1

    # ── Dry run ─────────────────────────────────────────────────────────────
    if args.dry_run:
        print("Scripts that would run:")
        for s in scripts:
            exists = "OK" if s.exists() else "X MISSING"
            print(f"  {exists}  {s.relative_to(root)}")
        return 0

    # ── Header ───────────────────────────────────────────────────────────────
    print(_bold("=" * 72))
    print(_bold("  The Mathematics of Coexistence — Verification Suite"))
    print(_bold("=" * 72))
    print()

    # ── Prepare data directory ────────────────────────────────────────────────
    data_dir = root / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    run_timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # ── Run scripts ──────────────────────────────────────────────────────────
    results: list[tuple[str, int, int, int, float, bool]] = []
    # (name, passed, failed, total, elapsed, ok)
    per_script_data: list[dict] = []

    for script in scripts:
        name = script.name
        if not script.exists():
            print(f"  {_red('MISSING')}  {name}")
            results.append((name, 0, 1, 1, 0.0, False))
            per_script_data.append({
                "script": name,
                "passed": 0, "failed": 1, "total": 1,
                "elapsed_s": 0.0, "ok": False,
                "error": "script file not found",
                "checks": [],
            })
            continue

        print(f"  Running {name} ...", end="", flush=True)
        passed, failed, total, elapsed, output = run_script(script, root)
        ok = (failed == 0 and total > 0)

        status = _green("PASS") if ok else _red("FAIL")
        print(f"\r  [{status}]  {name:<48}  {passed:>3}/{total:<3}  ({elapsed:.1f}s)")

        if args.verbose or not ok:
            # Show script's own output (always show on failure)
            for line in output.splitlines():
                print(f"    {line}")
            print()

        results.append((name, passed, failed, total, elapsed, ok))

        # ── Save per-script data ─────────────────────────────────────────────
        checks = parse_checks(output)
        script_data = {
            "script": name,
            "timestamp": run_timestamp,
            "passed": passed,
            "failed": failed,
            "total": total,
            "elapsed_s": round(elapsed, 3),
            "ok": ok,
            "checks": checks,
        }
        per_script_data.append(script_data)

        # Write individual JSON  (e.g. verify_lagrangian_constraints.json)
        stem = script.stem  # e.g. "verify_lagrangian_constraints"
        out_path = data_dir / f"{stem}.json"
        out_path.write_text(
            json.dumps(script_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Write raw log
        log_path = data_dir / f"{stem}.log"
        log_path.write_text(output, encoding="utf-8")

    # ── Final report ─────────────────────────────────────────────────────────
    total_passed = sum(r[1] for r in results)
    total_failed = sum(r[2] for r in results)
    total_checks = sum(r[3] for r in results)
    total_time   = sum(r[4] for r in results)
    all_ok       = all(r[5] for r in results)

    print()
    print(_bold("=" * 72))
    print(_bold("  FINAL REPORT"))
    print(_bold("=" * 72))

    col_w = 48
    print(f"  {'Script':<{col_w}}  {'Passed':>6}  {'Failed':>6}  {'Time':>6}")
    print(f"  {'-'*col_w}  {'------':>6}  {'------':>6}  {'------':>6}")

    for name, passed, failed, total, elapsed, ok in results:
        status_icon = _green("OK") if ok else _red("X")
        failed_str  = _red(str(failed)) if failed else str(failed)
        print(f"  {status_icon} {name:<{col_w-2}}  {passed:>6}  {failed_str:>6}  {elapsed:>5.1f}s")

    print(f"  {'-'*col_w}  {'------':>6}  {'------':>6}  {'------':>6}")

    total_failed_str = _red(str(total_failed)) if total_failed else str(total_failed)
    print(f"  {'TOTAL':<{col_w}}  {total_passed:>6}  {total_failed_str:>6}  {total_time:>5.1f}s")

    print()
    if all_ok:
        print(_bold(_green(f"  ALL {total_passed}/{total_checks} CHECKS PASSED")))
    else:
        print(_bold(_red(f"  {total_failed} CHECK(S) FAILED  ({total_passed}/{total_checks} passed)")))

    print(_bold("=" * 72))
    print()

    # ── Save consolidated summary ────────────────────────────────────────────
    summary = {
        "timestamp": run_timestamp,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_checks": total_checks,
        "total_time_s": round(total_time, 3),
        "all_ok": all_ok,
        "scripts": per_script_data,
    }
    summary_path = data_dir / "verification_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  Data saved to {data_dir.relative_to(root)}/")
    print()

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
