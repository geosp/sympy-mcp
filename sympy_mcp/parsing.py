"""
Expression parsing with references to stored session results.

`@key` in an expression string stands for the value stored under `key`
(e.g. "@expr_7 - @expr_9"). `@` directly after an operand (`A@B`) is left
alone, so it keeps its Python meaning of matrix multiplication.
"""

import re
from typing import Any, Dict, Mapping, Tuple

from sympy.parsing.sympy_parser import parse_expr

REFERENCE_PATTERN = re.compile(r"@([A-Za-z_]\w*)")


def substitute_references(
    text: str, stored: Mapping[str, Any], namespace: Mapping[str, Any]
) -> Tuple[str, Dict[str, Any]]:
    """Replace each `@key` with a placeholder name bound to the stored value.

    Returns the rewritten text and the placeholder bindings to add to the
    parse namespace. Raises ValueError for a reference to an unknown key.
    """
    bindings: Dict[str, Any] = {}

    def replace(match: re.Match) -> str:
        before = text[: match.start()].rstrip()
        if before and (before[-1].isalnum() or before[-1] in "_)]"):
            return match.group(0)  # binary @ (matrix multiplication)
        key = match.group(1)
        if key not in stored:
            raise ValueError(f"Unknown reference '@{key}': no stored result has that key.")
        placeholder = f"_ref_{key}"
        while placeholder in namespace and placeholder not in bindings:
            placeholder += "_"
        bindings[placeholder] = stored[key]
        return placeholder

    return REFERENCE_PATTERN.sub(replace, text), bindings


def parse_expression(
    text: str,
    namespace: Mapping[str, Any],
    stored: Mapping[str, Any],
    evaluate: bool = True,
) -> Any:
    """Parse `text` with `namespace` as local names, resolving `@key` references from `stored`."""
    rewritten, bindings = substitute_references(text, stored, namespace)
    return parse_expr(rewritten, local_dict={**namespace, **bindings}, evaluate=evaluate)
