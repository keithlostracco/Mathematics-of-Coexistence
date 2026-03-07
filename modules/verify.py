"""Shared verification helpers for application scripts.

Provides the check()/section()/summary() pattern used by all
verification scripts in the project.
"""

from __future__ import annotations

import sys

import numpy as np


# ---------------------------------------------------------------------------
# Global counters (module-level for simple scripts)
# ---------------------------------------------------------------------------

PASS: int = 0
FAIL: int = 0


def reset() -> None:
    """Reset global pass/fail counters."""
    global PASS, FAIL
    PASS = 0
    FAIL = 0


def check(name: str, condition: bool, detail: str = "") -> bool:
    """Report a single verification check.

    Parameters
    ----------
    name : str
        Short description of the check.
    condition : bool
        True if the check passes.
    detail : str, optional
        Extra information printed after the check name.

    Returns
    -------
    bool
        The *condition* value (for chaining).
    """
    global PASS, FAIL
    status = "PASS" if condition else "FAIL"
    if condition:
        PASS += 1
    else:
        FAIL += 1
    suffix = f"  ({detail})" if detail else ""
    print(f"  [{status}] {name}{suffix}")
    return condition


def section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 72}")
    print(f"  {title}")
    print(f"{'=' * 72}")


def summary() -> int:
    """Print final pass/fail summary and return exit code.

    Returns
    -------
    int
        0 if all checks passed, 1 otherwise.
    """
    total = PASS + FAIL
    print(f"\n{'=' * 72}")
    print(f"  TOTAL: {PASS}/{total} passed, {FAIL} failed")
    if FAIL == 0:
        print("  ✓ ALL CHECKS PASSED")
    else:
        print("  ✗ SOME CHECKS FAILED")
    print(f"{'=' * 72}\n")
    return 0 if FAIL == 0 else 1


# ---------------------------------------------------------------------------
# Numeric comparison helpers
# ---------------------------------------------------------------------------

def close(a: float, b: float, rtol: float = 0.02, atol: float = 0.0) -> bool:
    """Check whether *a* and *b* are close (default 2 % relative tolerance)."""
    return bool(np.isclose(a, b, rtol=rtol, atol=atol))


def close_abs(a: float, b: float, atol: float = 0.01) -> bool:
    """Absolute-tolerance closeness check."""
    return bool(np.isclose(a, b, rtol=0.0, atol=atol))


def order_of_magnitude(a: float, b: float, tol_decades: float = 0.5) -> bool:
    """Check that *a* and *b* agree to within *tol_decades* orders of magnitude."""
    if a <= 0 or b <= 0:
        return False
    return abs(np.log10(a) - np.log10(b)) <= tol_decades


def fmt(x: float, sig: int = 4) -> str:
    """Format a number to *sig* significant figures."""
    if x == 0:
        return "0"
    if abs(x) >= 1e4 or abs(x) < 1e-2:
        return f"{x:.{sig-1}e}"
    return f"{x:.{sig}g}"
