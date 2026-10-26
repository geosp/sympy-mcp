import os

import pytest
import sympy

from sympy_mcp import parsing
from sympy_mcp.parsing import UnsafeExpressionError, safe_parse
from sympy_mcp.state import SymPyState

# "__" assembled at runtime, so the raw input never contains a double underscore
RUNTIME_DUNDER = "Symbol('_').name + Symbol('_').name"


@pytest.fixture
def state():
    state = SymPyState()
    state.intro("x", [], [])
    return state


@pytest.fixture
def canary(tmp_path, monkeypatch):
    """Escape attempts below try to create this file; none may succeed."""
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "CANARY"
    yield path
    assert not path.exists(), "an escape attempt created the canary file"


ESCAPES = [
    "__import__('os').system('touch CANARY')",
    "open('CANARY', 'w')",
    "().__class__.__base__.__subclasses__()",
    "x.__class__",
    "x.func.mro()",
    "eval('1 + 1')",
    "exec('import os')",
    "getattr(x, 'func')",
    "S('open')",
    "sin('open')",
    "Symbol('x', real='__import__')",
    "sympify('1')",
    "(t for t in [x]).gi_frame",
    "[t for t in [x]]",
    "(lambda: 1)()",
    "(y := 1)",
    "f'{x}'",
    "x.subs(x, 'open')",
    "Integer(1).func(Symbol('x').name)",
    f"S({RUNTIME_DUNDER} + Symbol('import').name + {RUNTIME_DUNDER})",
    f"sin({RUNTIME_DUNDER} + Symbol('import').name + {RUNTIME_DUNDER})",
]


class TestEscapesFail:
    @pytest.mark.parametrize("attack", ESCAPES)
    def test_attack_is_rejected(self, state, canary, attack):
        with pytest.raises(Exception) as excinfo:
            state.introduce_expression(attack)
        assert not isinstance(excinfo.value, (SystemExit, KeyboardInterrupt))

    def test_dunder_and_import_messages(self, state):
        with pytest.raises(UnsafeExpressionError, match="Double underscores"):
            state.introduce_expression("__import__('os')")
        with pytest.raises(UnsafeExpressionError, match="String literals"):
            state.introduce_expression("S('open')")
        with pytest.raises(UnsafeExpressionError, match="attribute 'mro'"):
            state.introduce_expression("x.func.mro()")
        with pytest.raises(UnsafeExpressionError, match="Lambda"):
            state.introduce_expression("(lambda: 1)()")

    @pytest.mark.parametrize("name", ["globals", "vars", "lambdify", "nsolve", "sympify", "open"])
    def test_python_and_excluded_names_are_inert(self, state, canary, name):
        # Unknown names become undefined SymPy functions; the Python callables are never reached
        key = state.introduce_expression(f"{name}(x)")
        value = state.expressions[key]
        assert isinstance(value, sympy.core.function.AppliedUndef)
        assert value.func.__name__ == name

    def test_runtime_string_is_parsed_with_restrictions(self, state):
        # Unrestricted, sympify("__import__") would return Python's __import__
        with pytest.raises(UnsafeExpressionError, match="Double underscores"):
            state.introduce_expression(f"S({RUNTIME_DUNDER} + Symbol('import').name + {RUNTIME_DUNDER})")

    def test_result_may_not_be_a_string(self, state):
        with pytest.raises(UnsafeExpressionError, match="may not evaluate to a string"):
            state.introduce_expression("Symbol('a').name")
        with pytest.raises(UnsafeExpressionError, match="may not evaluate to a string"):
            state.introduce_expression("[x, latex(x)]")

    def test_length_cap(self, state):
        with pytest.raises(UnsafeExpressionError, match="limit is 10000"):
            state.introduce_expression("+".join(["x"] * 6000))

    def test_other_entry_points_are_restricted(self, state, canary):
        target = state.introduce_expression("x**2")
        assert "Error" in state.integrate_expression(target, "x", "0", "open('CANARY', 'w')")
        assert "Error" in state.limit_expression(target, "x", "__import__('os').getpid()")
        assert "Error" in state.convert_to_units(target, ["__import__('os').getpid()"])
        assert "Error" in state.create_matrix([["open('CANARY', 'w')"]])
        assert "Error" in state.substitute_values(target, {"x": "open('CANARY', 'w')"})
        assert state.check_equivalence("open('CANARY', 'w')", "1").startswith("Error")

    def test_rewrite_target_must_be_a_safe_function(self, state):
        target = state.introduce_expression("cosh(x)")
        for name in ("lambdify", "__import__", "sympify", "parse_expr"):
            assert "not a SymPy function" in state.rewrite_expression(target, name)

    def test_numeric_integrate_rejects_undefined_functions(self, state):
        state.introduce_function("f")
        integrand = state.introduce_expression("f(x)")
        assert "undefined functions" in state.numeric_integrate(integrand, "x", "0", "1")

    def test_namespace_has_no_builtins_or_modules(self):
        import types
        assert parsing.SAFE_GLOBALS["__builtins__"] == {}
        for name in ("open", "eval", "exec", "__import__", "getattr", "sympify", "lambdify", "nsolve"):
            assert name not in parsing.SAFE_GLOBALS
        assert not any(isinstance(v, types.ModuleType) for v in parsing.SAFE_GLOBALS.values())

    def test_guard_only_applies_inside_restricted_parses(self):
        # Ordinary SymPy use elsewhere in the process is unaffected
        assert sympy.sympify("1 + 1") == 2
        token = parsing._restricted.set(True)
        try:
            with pytest.raises(UnsafeExpressionError):
                sympy.sympify("__import__('os').getpid()")
        finally:
            parsing._restricted.reset(token)

    def test_os_untouched(self, state):
        pid = os.getpid()
        with pytest.raises(Exception):
            state.introduce_expression("__import__('os').kill(0, 9)")
        assert os.getpid() == pid


LEGITIMATE = {
    "Symbol('y') + 1": "y + 1",
    "symbols('a b')": "(a, b)",
    "Function('g')(x)": "g(x)",
    "S(1)/2 + S.Half": "1",
    "Rational(1, 3)": "1/3",
    "1.5*x": "1.5*x",
    "x.subs(x, 2)": "2",
    "Piecewise((x, x > 0), (0, True))": "Piecewise((x, x > 0), (0, True))",
    "Eq(x, 1)": "Eq(x, 1)",
    "x!": "factorial(x)",
    "oo": "oo",
    "max(x, 2)": "Max(2, x)",
    "Matrix([[1, 2], [3, 4]]).det()": "-2",
    "integrate(x**2, (x, 0, 1))": "1/3",
    "cosh(x).rewrite(exp)": "exp(x)/2 + exp(-x)/2",
    "BosonOp('a')": "a",
    "Float('1e-3')": "0.00100000000000000",
}


class TestLegitimateInputStillWorks:
    @pytest.mark.parametrize("text,expected", list(LEGITIMATE.items()))
    def test_parses(self, state, text, expected):
        key = state.introduce_expression(text)
        assert str(state.expressions[key]) == expected

    def test_safe_parse_directly(self):
        x = sympy.Symbol("x")
        assert safe_parse("x**2 + 1", {"x": x}) == x**2 + 1
