"""Helper for saving and loading figure data produced by verification scripts.

Verification scripts call ``save_figure_data(name, **arrays)`` to persist
NumPy arrays to ``output/data/fig_<name>.json``.  Figure scripts call
``load_figure_data(name)`` to retrieve them.

Data is stored as human-readable JSON so that results can be inspected
directly.  NumPy arrays are round-tripped through nested Python lists;
scalars (including 0-d arrays) are stored as plain numbers.

This ensures that every plotted curve comes from the *same* code and
parameters that the verification suite validated — no duplicated formulas
or risk of parameter drift.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

# Resolve the project root (two levels above modules/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DATA_DIR = _PROJECT_ROOT / "output" / "data"


def _to_serialisable(obj: Any) -> Any:
    """Recursively convert numpy types to JSON-friendly Python types."""
    if isinstance(obj, np.ndarray):
        if obj.ndim == 0:
            return obj.item()
        return obj.tolist()
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def save_figure_data(name: str, **arrays: Any) -> Path:
    """Save arrays to ``output/data/fig_<name>.json``.

    Parameters
    ----------
    name : str
        Short identifier (e.g. ``"reward_hacking_friction"``).
    **arrays
        Keyword arguments — NumPy arrays, scalars, or Python lists.

    Returns
    -------
    Path
        The path to the saved file.
    """
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = _DATA_DIR / f"fig_{name}.json"

    payload = {k: _to_serialisable(v) for k, v in arrays.items()}
    with open(path, "w") as f:
        json.dump(payload, f, indent=1)

    print(f"  [DATA] Saved figure data → {path.relative_to(_PROJECT_ROOT)}")
    return path


def load_figure_data(name: str) -> dict[str, np.ndarray]:
    """Load arrays from ``output/data/fig_<name>.json``.

    Parameters
    ----------
    name : str
        Same identifier used in :func:`save_figure_data`.

    Returns
    -------
    dict[str, np.ndarray]
        Mapping of array name → NumPy array (lists are converted back).

    Raises
    ------
    FileNotFoundError
        If the data file does not exist.  The error message tells the user
        which verification script to run first.
    """
    path = _DATA_DIR / f"fig_{name}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Figure data not found: {path.relative_to(_PROJECT_ROOT)}\n"
            f"Run the corresponding verification script first to generate it."
        )
    with open(path) as f:
        raw = json.load(f)
    # Convert lists back to numpy arrays; leave scalars as-is
    return {k: np.asarray(v) for k, v in raw.items()}
