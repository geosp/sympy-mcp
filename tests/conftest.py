"""
Test configuration and shared fixtures for sympy-mcp tests.

Provides a per-test SymPyState instance via the `state` fixture,
and re-exports module-level shims for backward compatibility.
"""

import pytest
from sympy_mcp.state import SymPyState


@pytest.fixture
def state():
    """Fresh SymPyState for each test."""
    return SymPyState()
