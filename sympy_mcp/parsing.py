"""
Expression parsing with references to stored session results.

`@key` in an expression string stands for the value stored under `key`
(e.g. "@expr_7 - @expr_9"). `@` directly after an operand (`A@B`) is left
alone, so it keeps its Python meaning of matrix multiplication.

parse_expr evaluates the (transformed) input as Python, and by default
with Python's builtins available. Parsing here is restricted instead:
- the global namespace holds SymPy's names only: no builtins, no modules,
  and none of SymPy's helpers that generate or evaluate code;
- the input is capped at MAX_EXPRESSION_LENGTH characters and may not
  contain "__";
- the transformed code is checked before it runs: no attributes starting
  with "_" or used for frame/code introspection, no lambdas or
  comprehensions, and string literals only as plain names in Symbol('x'),
  Function('f') and similar constructors;
- strings built at runtime and handed to sympify() by a SymPy function
  (e.g. sin(<some string>)) go through the same restricted parser, and a
  parse result may not contain strings, so none can be evaluated later.
This closes the known routes out of the expression language, but an
in-process eval is not a proven sandbox: run the server with least
privilege.
"""

import ast
import contextvars
import re
import types
from typing import Any, Dict, Mapping, Tuple

import sympy
from sympy.parsing import sympy_parser
from sympy.parsing.sympy_parser import standard_transformations, stringify_expr

_parse_expr = sympy_parser.parse_expr

REFERENCE_PATTERN = re.compile(r"@([A-Za-z_]\w*)")

MAX_EXPRESSION_LENGTH = 10_000

# SymPy names that generate code, evaluate strings, touch files or the caller's frame
_EXCLUDED_NAMES = {
    "sympify", "lambdify", "parse_expr", "var", "init_session", "init_printing",
    "preview", "test", "doctest", "python", "pycode", "ccode", "rcode", "srepr",
    "plot", "plot_implicit", "plot_parametric", "plot3d", "plot3d_parametric_line",
    "plot3d_parametric_surface", "plot_backends", "evaluate", "nsolve", "textplot",
}

# Objects defined in these modules are left out of the namespace as well
_EXCLUDED_MODULES = (
    "sympy.plotting", "sympy.utilities.lambdify", "sympy.utilities.autowrap",
    "sympy.utilities.codegen", "sympy.printing.preview", "sympy.interactive",
    "sympy.testing", "sympy.parsing",
)

# Attributes that reach frames, code objects or global namespaces without dunders
_EXCLUDED_ATTRIBUTES = {
    "gi_frame", "gi_code", "gi_yieldfrom", "cr_frame", "cr_code", "cr_await", "ag_frame",
    "ag_code", "f_globals", "f_locals", "f_builtins", "f_back", "f_code", "f_trace",
    "tb_frame", "tb_next", "co_code", "co_consts", "co_names", "func_globals", "func_code",
    "mro", "modules", "system", "popen",
}

# String literals are allowed only as the first argument of these constructors
_NAME_CONSTRUCTORS = {"Symbol", "symbols", "Function", "Dummy", "Wild", "BosonOp", "IndexedBase", "Idx"}
_NUMBER_CONSTRUCTORS = {"Float", "Integer"}
_NAME_LIST = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:[ ,]+[A-Za-z_][A-Za-z0-9_]*)*$")
_NUMBER = re.compile(r"^[0-9.eE+\-]+$")

_FORBIDDEN_NODES = (
    ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
    ast.NamedExpr, ast.JoinedStr, ast.Await, ast.Yield, ast.YieldFrom,
)


def _safe_globals() -> Dict[str, Any]:
    namespace: Dict[str, Any] = {}
    exec("from sympy import *", namespace)
    safe = {
        name: value
        for name, value in namespace.items()
        if not name.startswith("_")
        and name not in _EXCLUDED_NAMES
        and not isinstance(value, types.ModuleType)
        and not str(getattr(value, "__module__", "") or "").startswith(_EXCLUDED_MODULES)
    }
    safe["max"] = sympy.Max
    safe["min"] = sympy.Min
    safe["__builtins__"] = {}
    return safe


SAFE_GLOBALS = _safe_globals()


class UnsafeExpressionError(ValueError):
    pass


def _check_code(code: str) -> None:
    tree = ast.parse(code, mode="eval")
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    for node in ast.walk(tree):
        if isinstance(node, _FORBIDDEN_NODES):
            raise UnsafeExpressionError(f"{type(node).__name__} is not allowed in expressions.")
        if isinstance(node, ast.Attribute) and (
            node.attr.startswith("_") or node.attr in _EXCLUDED_ATTRIBUTES
        ):
            raise UnsafeExpressionError(f"Access to attribute '{node.attr}' is not allowed.")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise UnsafeExpressionError(f"The name '{node.id}' is not allowed.")
        if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
            call = parents.get(node)
            func = call.func.id if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) else None
            is_first_arg = isinstance(call, ast.Call) and bool(call.args) and call.args[0] is node
            if isinstance(node.value, str) and is_first_arg and (
                (func in _NAME_CONSTRUCTORS and _NAME_LIST.match(node.value))
                or (func in _NUMBER_CONSTRUCTORS and _NUMBER.match(node.value))
            ):
                continue
            raise UnsafeExpressionError(
                "String literals are only allowed as names, e.g. Symbol('x') or Function('f'). "
                "Use function objects instead of names in quotes, e.g. rewrite(exp)."
            )


def _contains_string(value: Any) -> bool:
    if isinstance(value, (str, bytes)):
        return True
    if isinstance(value, dict):
        return any(_contains_string(k) or _contains_string(v) for k, v in value.items())
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_contains_string(item) for item in value)
    return False


# True while a restricted parse is evaluating, so nested string parsing is restricted too
_restricted = contextvars.ContextVar("sympy_mcp_restricted_parse", default=False)


def _guarded_parse_expr(s, local_dict=None, transformations=standard_transformations,
                        global_dict=None, evaluate=True):
    """sympy_parser.parse_expr, restricted while one of our parses is running.

    sympify() looks parse_expr up on the module at call time, so a string a
    SymPy function receives during a restricted parse comes through here.
    """
    if _restricted.get():
        return safe_parse(s, local_dict or {}, evaluate=evaluate)
    return _parse_expr(s, local_dict, transformations, global_dict, evaluate)


sympy_parser.parse_expr = _guarded_parse_expr


def safe_parse(text: str, namespace: Mapping[str, Any], evaluate: bool = True) -> Any:
    """parse_expr with the restrictions described in the module docstring."""
    if not isinstance(text, str):
        raise UnsafeExpressionError("Expressions must be strings.")
    if len(text) > MAX_EXPRESSION_LENGTH:
        raise UnsafeExpressionError(
            f"Expression is {len(text)} characters long; the limit is {MAX_EXPRESSION_LENGTH}."
        )
    if "__" in text:
        raise UnsafeExpressionError("Double underscores ('__') are not allowed in expressions.")
    local_dict = dict(namespace)
    global_dict = dict(SAFE_GLOBALS)
    token = _restricted.set(True)
    try:
        _check_code(stringify_expr(text, local_dict, global_dict, standard_transformations))
        result = _parse_expr(text, local_dict=local_dict, global_dict=global_dict, evaluate=evaluate)
    finally:
        _restricted.reset(token)
    if _contains_string(result):
        raise UnsafeExpressionError("An expression may not evaluate to a string.")
    return result


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
    return safe_parse(rewritten, {**namespace, **bindings}, evaluate=evaluate)
