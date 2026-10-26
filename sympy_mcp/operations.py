"""
Shared plumbing for the helper modules that implement SymPyState operations.

Operation functions take the state as their first argument. They raise
OperationError for problems the caller should see (unknown key, bad
argument); guard() turns that into an "Error: ..." string, the convention
all tools use.
"""

import functools
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from sympy_mcp.state import SymPyState


class OperationError(ValueError):
    """A user-facing error, reported as "Error: <message>"."""


def guard(description: str) -> Callable:
    """Decorator: report OperationError as "Error: ..." and anything else as "Error <description>: ..."."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except OperationError as e:
                return f"Error: {e}"
            except Exception as e:
                return f"Error {description}: {e}"
        return wrapper
    return decorator


def stored(state: "SymPyState", key: str) -> Any:
    if key not in state.expressions:
        raise OperationError(f"Expression with key '{key}' not found.")
    return state.expressions[key]


def symbol(state: "SymPyState", name: str) -> Any:
    if name not in state.local_vars:
        raise OperationError(f"Symbol '{name}' not found. Introduce it first.")
    return state.local_vars[name]
