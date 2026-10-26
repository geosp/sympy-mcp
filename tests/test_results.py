import asyncio
import json

import sympy
from fastmcp import Client

from sympy_mcp.config import AppConfig
from sympy_mcp.results import StoredResult, format_output
from sympy_mcp.server import SymPyMCPServer, create_service
from sympy_mcp.shared.enums import Assumption
from sympy_mcp.state import SymPyState

COMPUTING_TOOLS = {
    "introduce_expression", "introduce_equation", "substitute_expression", "factor_expression",
    "expand_expression", "collect_expression", "apart_expression", "evalf_expression",
    "simplify_expression", "integrate_expression", "differentiate_expression", "limit_expression",
    "series_expansion", "summation_expression", "solve_algebraically", "solve_linear_system",
    "solve_nonlinear_system", "dsolve_ode", "dsolve_system", "pdsolve_pde", "create_vector_field",
    "calculate_curl", "calculate_divergence", "calculate_gradient", "convert_to_units",
    "quantity_simplify_units", "create_matrix", "matrix_determinant", "matrix_inverse",
    "matrix_eigenvalues", "matrix_eigenvectors", "create_predefined_metric", "calculate_tensor",
    "create_custom_metric", "create_tensor", "covariant_derivative", "tensor_divergence",
    "contract_indices", "raise_index", "lower_index", "tensor_component", "kretschmann_scalar",
    "killing_equation", "fourier_transform", "inverse_fourier_transform", "laplace_transform",
    "inverse_laplace_transform", "numeric_integrate", "rewrite_expression", "expand_log_expression",
    "trigsimp_expression", "powsimp_expression", "nsimplify_expression", "substitute_values",
    "matrix_multiply", "matrix_power", "matrix_exp", "matrix_trace", "matrix_transpose",
    "matrix_adjoint", "matrix_commutator", "matrix_rank", "matrix_nullspace",
    "normal_order_expression", "evaluate_commutator", "quantum_apply", "coherent_state_expectation",
}


class TestFormatOutput:
    def test_structured_payload(self):
        raw = StoredResult("expr_3", "expr_3", sympy.Symbol("x") ** 2, extra="value")
        assert json.loads(format_output(raw)) == {
            "key": "expr_3", "result": "x**2", "latex": "x^{2}", "extra": "value",
        }

    def test_stored_result_equals_legacy_string(self):
        raw = StoredResult("\\left\\{1\\right\\}", "expr_0", sympy.FiniteSet(1))
        assert raw == "\\left\\{1\\right\\}"
        assert format_output(raw, "legacy") == "\\left\\{1\\right\\}"
        assert type(format_output(raw, "legacy")) is str

    def test_error_string(self):
        assert json.loads(format_output("Error: nope")) == {"error": "Error: nope"}
        assert format_output("Error: nope", "legacy") == "Error: nope"

    def test_unknown_format(self):
        assert "Unknown output_format" in json.loads(format_output("x", "xml"))["error"]


class TestSolversStoreResults:
    def test_solve_algebraically(self):
        state = SymPyState()
        state.intro("x", [Assumption.REAL], [])
        eq = state.introduce_expression("Eq(x**2 - 5*x + 6, 0)")
        result = state.solve_algebraically(eq, "x")
        assert result == "\\left\\{2, 3\\right\\}"  # legacy return value unchanged
        assert state.expressions[result.key] == sympy.FiniteSet(2, 3)

    def test_solve_linear_system(self):
        state = SymPyState()
        state.intro_many(["x", "y"])
        a = state.introduce_expression("x + y - 3")
        b = state.introduce_expression("x - y - 1")
        result = state.solve_linear_system([a, b], ["x", "y"])
        assert state.expressions[result.key] == sympy.FiniteSet((2, 1))
        assert result == sympy.latex(sympy.FiniteSet((2, 1)))

    def test_solve_nonlinear_system(self):
        state = SymPyState()
        state.intro_many(["x", "y"])
        a = state.introduce_expression("x**2 - y")
        b = state.introduce_expression("y - 4")
        result = state.solve_nonlinear_system([a, b], ["x", "y"])
        assert state.expressions[result.key] == sympy.FiniteSet((-2, 4), (2, 4))

    def test_dsolve_ode(self):
        state = SymPyState()
        state.intro("x", [], [])
        state.introduce_function("f")
        ode = state.introduce_expression("Derivative(f(x), x) - f(x)")
        result = state.dsolve_ode(ode, "f")
        solution = state.expressions[result.key]
        assert isinstance(solution, sympy.Eq)
        assert result == sympy.latex(solution)

    def test_dsolve_system(self):
        state = SymPyState()
        state.intro("t", [], [])
        state.introduce_function("f")
        state.introduce_function("g")
        a = state.introduce_expression("Derivative(f(t), t) - g(t)")
        b = state.introduce_expression("Derivative(g(t), t) + f(t)")
        result = state.dsolve_system([a, b], ["f", "g"])
        assert isinstance(state.expressions[result.key], list)
        assert len(state.expressions[result.key]) == 2

    def test_pdsolve(self):
        state = SymPyState()
        state.intro_many(["x", "y"])
        state.introduce_function("u")
        pde = state.introduce_expression("Derivative(u(x, y), x) + Derivative(u(x, y), y)")
        result = state.pdsolve_pde(pde, "u")
        assert isinstance(state.expressions[result.key], sympy.Eq)

    def test_series_payload_has_display_with_order_term(self):
        state = SymPyState()
        state.intro("x", [], [])
        expr = state.introduce_expression("sin(x)")
        result = state.series_expansion(expr, "x", "0", 5)
        assert str(state.expressions[result.key]) == "-x**3/6 + x"
        assert result.extras["series"] == "x - x**3/6 + O(x**5)"

    def test_errors_stay_plain_strings(self):
        state = SymPyState()
        result = state.simplify_expression("expr_404")
        assert not isinstance(result, StoredResult)
        assert result.startswith("Error")


def _call(tool_calls):
    """Run a sequence of (tool, args) calls in one session; return the decoded results."""
    async def run():
        config = AppConfig()
        mcp = SymPyMCPServer(config.server, create_service(config)).create_mcp_app()
        async with Client(mcp) as client:
            created = await client.call_tool("create_session", {"description": "results"})
            session_id = json.loads(created.data)["session_id"]
            out = []
            for name, args in tool_calls:
                result = await client.call_tool(name, {"session_id": session_id, **args})
                out.append(result.data)
            return out
    return asyncio.run(run())


class TestToolOutput:
    def test_structured_is_default(self):
        _, expr, simplified = _call([
            ("intro", {"var_name": "x"}),
            ("introduce_expression", {"expression": "sin(x)**2 + cos(x)**2"}),
            ("simplify_expression", {"expr_key": "expr_0"}),
        ])
        assert json.loads(expr) == {
            "key": "expr_0", "result": "sin(x)**2 + cos(x)**2", "latex": "\\sin^{2}{\\left(x \\right)} + \\cos^{2}{\\left(x \\right)}",
        }
        assert json.loads(simplified) == {"key": "expr_1", "result": "1", "latex": "1"}

    def test_legacy_output(self):
        _, expr, solved, series = _call([
            ("intro", {"var_name": "x"}),
            ("introduce_expression", {"expression": "x**2 - 1", "output_format": "legacy"}),
            ("solve_algebraically", {"expr_key": "expr_0", "var_name": "x", "output_format": "legacy"}),
            ("series_expansion", {"expr_key": "expr_0", "var_name": "x", "output_format": "legacy"}),
        ])
        assert expr == "expr_0"
        assert solved == "\\left\\{-1, 1\\right\\}"
        assert series == "x**2 - 1 [stored as expr_2]"

    def test_solver_result_can_be_chained(self):
        _, _, solved, total = _call([
            ("intro", {"var_name": "x"}),
            ("introduce_expression", {"expression": "x**2 - 3*x + 2"}),
            ("solve_algebraically", {"expr_key": "expr_0", "var_name": "x"}),
            ("introduce_expression", {"expression": "Add(*@expr_1)"}),
        ])
        assert json.loads(solved)["key"] == "expr_1"
        assert json.loads(total)["result"] == "3"

    def test_series_structured(self):
        _, _, series = _call([
            ("intro", {"var_name": "x"}),
            ("introduce_expression", {"expression": "exp(x)"}),
            ("series_expansion", {"expr_key": "expr_0", "var_name": "x", "order": 3}),
        ])
        payload = json.loads(series)
        assert payload["key"] == "expr_1"
        assert payload["result"] == "x**2/2 + x + 1"
        assert payload["series"] == "1 + x + x**2/2 + O(x**3)"

    def test_errors(self):
        (missing,) = _call([("simplify_expression", {"expr_key": "expr_9"})])
        assert json.loads(missing) == {"error": "Error: Expression with key 'expr_9' not found."}

    def test_every_computing_tool_takes_output_format(self):
        async def run():
            config = AppConfig()
            mcp = SymPyMCPServer(config.server, create_service(config)).create_mcp_app()
            async with Client(mcp) as client:
                return await client.list_tools()
        tools = {tool.name: tool for tool in asyncio.run(run())}
        assert COMPUTING_TOOLS <= set(tools)
        for name in COMPUTING_TOOLS:
            schema = tools[name].input_schema["properties"]
            assert schema["output_format"]["default"] == "structured", name
