"""
Return values of computing tools.

Computing tools return a JSON payload by default:
    {"key": <session key the result is stored under>,
     "result": <str() of the stored value>,
     "latex": <LaTeX of the stored value>, ...extras}
and {"error": <message>} on failure. output_format="legacy" returns the
plain string each tool returned before the payload existed.
"""

import json
from typing import Any, Callable, Dict, Optional

import sympy

from sympy_mcp import timeouts

OUTPUT_FORMATS = ("structured", "legacy")


class StoredResult(str):
    """A computing method's legacy return string, carrying what it stored.

    It compares and hashes as the legacy string (usually the key itself), so
    callers that expect the old return value are unaffected.
    """

    key: str
    value: Any
    extras: Dict[str, Any]

    def __new__(cls, legacy: str, key: str, value: Any, **extras: Any) -> "StoredResult":
        obj = super().__new__(cls, legacy)
        obj.key = key
        obj.value = value
        obj.extras = extras
        return obj


def payload(result: StoredResult) -> Dict[str, Any]:
    return {
        "key": result.key,
        "result": str(result.value),
        "latex": sympy.latex(result.value),
        **result.extras,
    }


def format_output(raw: str, output_format: str = "structured") -> str:
    """Render a computing method's return value for the requested output format."""
    if output_format == "legacy":
        return str(raw)
    if output_format != "structured":
        return json.dumps({
            "error": f"Unknown output_format '{output_format}'. Use one of: {', '.join(OUTPUT_FORMATS)}."
        })
    if isinstance(raw, StoredResult):
        return json.dumps(payload(raw))
    return json.dumps({"error": str(raw)})


def run_tool(
    call: Callable[[], str], output_format: str = "structured", timeout_seconds: Optional[float] = None
) -> str:
    """Run a computing method under the time limit and format its return value."""
    return format_output(timeouts.run_limited(call, timeout_seconds), output_format)
