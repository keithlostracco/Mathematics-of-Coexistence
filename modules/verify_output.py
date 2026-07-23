"""Verification output helpers — JSON + log writers for verify_*.py scripts.

Provides a lightweight `VerifyOutput` recorder that captures stdout to a log
file and accumulates structured per-check / per-result data for a JSON
summary. Designed to be embedded in self-contained verify scripts without
forcing them into a package structure.

Usage pattern in a verify_*.py script:

    from modules.verify_output import VerifyOutput
    out = VerifyOutput(
        theorem="thm-foo",
        script="verify_foo.py",
        parameters={"g": 1.0, "f": 2.0},
    )

    # Replace local check()/section() with calls that also record:
    def check(name, condition, detail=""):
        out.record_check(name, condition, detail)
        # ...usual print logic

    out.record_result("g_zero", 0.5)
    ...
    out.write("output/data")  # writes verify_thm-foo.json + verify_thm-foo.log
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from io import StringIO
from typing import Any


class _TeeStream:
    """Write to both a real stream and an in-memory buffer."""

    def __init__(self, real, buffer: StringIO) -> None:
        self._real = real
        self._buffer = buffer

    def write(self, data: str) -> int:
        self._buffer.write(data)
        return self._real.write(data)

    def flush(self) -> None:
        self._real.flush()

    def __getattr__(self, name: str):
        return getattr(self._real, name)


class VerifyOutput:
    """Recorder for verification outputs.

    Captures stdout via a tee (so the script's existing print() calls land in
    both the terminal and an in-memory log buffer) and accumulates a JSON
    payload with pass/fail counts, named numerical results, parameters, and
    a per-check trace.
    """

    def __init__(
        self,
        theorem: str,
        script: str,
        parameters: dict | None = None,
    ) -> None:
        self.theorem = theorem
        self.script = script
        self.parameters = dict(parameters or {})
        self.pass_count = 0
        self.fail_count = 0
        self.results: dict[str, Any] = {}
        self.checks: list[dict] = []
        self.timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self._log_buffer = StringIO()
        self._installed = False
        self._orig_stdout = None

    # ----- stdout capture -----

    def begin_capture(self) -> None:
        """Begin tee-ing stdout into the in-memory log buffer."""
        if self._installed:
            return
        self._orig_stdout = sys.stdout
        sys.stdout = _TeeStream(sys.stdout, self._log_buffer)
        self._installed = True

    def end_capture(self) -> None:
        """Restore the original stdout."""
        if not self._installed:
            return
        sys.stdout = self._orig_stdout
        self._installed = False

    # ----- recording -----

    def record_check(self, name: str, condition: bool, detail: str = "") -> None:
        """Record a check outcome (used alongside the script's own print())."""
        if condition:
            self.pass_count += 1
        else:
            self.fail_count += 1
        self.checks.append(
            {
                "name": name,
                "passed": bool(condition),
                "detail": detail,
            }
        )

    def record_result(self, key: str, value: Any) -> None:
        """Record a named numerical (or structured) result."""
        self.results[key] = _to_jsonable(value)

    # ----- writing -----

    def write(self, output_dir: str) -> tuple[str, str]:
        """Write `verify_<theorem>.json` and `verify_<theorem>.log`.

        Returns (json_path, log_path).
        """
        os.makedirs(output_dir, exist_ok=True)
        base = f"verify_{self.theorem}"
        json_path = os.path.join(output_dir, f"{base}.json")
        log_path = os.path.join(output_dir, f"{base}.log")

        payload = {
            "theorem": self.theorem,
            "script": self.script,
            "timestamp": self.timestamp,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "total_count": self.pass_count + self.fail_count,
            "parameters": _to_jsonable(self.parameters),
            "results": _to_jsonable(self.results),
            "checks": self.checks,
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=False)
            f.write("\n")

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(self._log_buffer.getvalue())

        return json_path, log_path


def _to_jsonable(obj: Any) -> Any:
    """Convert numpy / inf / NaN / nested containers to JSON-safe values."""
    # Late import to keep the module import-cheap if numpy is absent.
    try:
        import numpy as np  # type: ignore
    except Exception:  # pragma: no cover - numpy always available here
        np = None  # type: ignore

    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    if np is not None:
        if isinstance(obj, np.ndarray):
            return _to_jsonable(obj.tolist())
        if isinstance(obj, np.generic):
            return _to_jsonable(obj.item())
    if isinstance(obj, float):
        if obj != obj:  # NaN
            return "NaN"
        if obj == float("inf"):
            return "Infinity"
        if obj == float("-inf"):
            return "-Infinity"
        return obj
    if isinstance(obj, (int, str, bool)) or obj is None:
        return obj
    return repr(obj)
