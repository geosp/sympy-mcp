"""
End-to-end reproductions of the checks in the paper, through the MCP tools
(in-memory client, same code path as stdio and http).
"""

import asyncio
import json

import pytest
from fastmcp import Client

from sympy_mcp.config import AppConfig
from sympy_mcp.server import SymPyMCPServer, create_service
from sympy_mcp.state import EINSTEINPY_AVAILABLE


class Session:
    """Call tools in one session; JSON results are decoded."""

    def __init__(self, client, session_id):
        self.client = client
        self.session_id = session_id

    async def __call__(self, tool, **arguments):
        result = await self.client.call_tool(tool, {"session_id": self.session_id, **arguments})
        try:
            data = json.loads(result.data)
        except (TypeError, ValueError):
            return result.data
        if isinstance(data, dict) and "error" in data:
            raise AssertionError(f"{tool} failed: {data['error']}")
        return data


def run(scenario):
    async def main():
        config = AppConfig()
        mcp = SymPyMCPServer(config.server, create_service(config)).create_mcp_app()
        async with Client(mcp) as client:
            created = await client.call_tool("create_session", {"description": scenario.__name__})
            return await scenario(Session(client, json.loads(created.data)["session_id"]))
    return asyncio.run(main())


def test_conformal_factor_of_the_exponential_map():
    """With U = -e^{-u}: dU dU' / (U - U')^2 = du du' / (4 sinh^2((u - u')/2))."""
    async def scenario(call):
        await call("intro_many", variables=[["u", ["real"], []], ["up", ["real"], []]])
        U = await call("introduce_expression", expression="-exp(-u)")
        dU = await call("differentiate_expression", expr_key=U["key"], var_name="u")
        U_p = await call("substitute_values", expr_key=U["key"], substitutions={"u": "up"})
        dU_p = await call("substitute_values", expr_key=dU["key"], substitutions={"u": "up"})
        measure = await call(
            "introduce_expression",
            expression=f"@{dU['key']} * @{dU_p['key']} / (@{U['key']} - @{U_p['key']})**2",
        )
        return await call("check_equivalence", expr_a=measure["key"], expr_b="1/(4*sinh((u - up)/2)**2)")

    assert run(scenario)["verdict"] == "proved_equal"


def test_detailed_balance_ratio():
    """F(-omega)/F(omega) = e^{2 pi omega} for the thermal response F(omega) = omega / (2 pi (e^{2 pi omega} - 1))."""
    async def scenario(call):
        await call("intro", var_name="omega", assumptions=["positive"])
        response = await call("introduce_expression", expression="omega/(2*pi*(exp(2*pi*omega) - 1))")
        flipped = await call("substitute_values", expr_key=response["key"], substitutions={"omega": "-omega"})
        ratio = await call("introduce_expression", expression=f"@{flipped['key']} / @{response['key']}")
        simplified = await call("simplify_expression", expr_key=ratio["key"])
        verdict = await call("check_equivalence", expr_a=simplified["key"], expr_b="exp(2*pi*omega)")
        return simplified, verdict

    simplified, verdict = run(scenario)
    assert simplified["result"] == "exp(2*pi*omega)"
    assert verdict["verdict"] == "proved_equal"


def test_raychaudhuri_with_initial_condition():
    """theta' = -theta^2/2 - R, theta(0) = 0  =>  theta = -sqrt(2R) tan(sqrt(R/2) U) = -R U - R^2 U^3/6 + O(U^5)."""
    async def scenario(call):
        await call("intro", var_name="U")
        await call("intro", var_name="R", assumptions=["positive"])
        await call("introduce_function", func_name="theta")
        ode = await call(
            "introduce_equation", lhs_expression="Derivative(theta(U), U)", rhs_expression="-theta(U)**2/2 - R"
        )
        solution = await call("dsolve_ode", expr_key=ode["key"], func_name="theta", ics={"theta(0)": "0"})
        closed_form = await call(
            "check_equivalence", expr_a=solution["rhs_key"], expr_b="-sqrt(2*R)*tan(sqrt(R/2)*U)"
        )
        verified = await call("verify_ode_solution", solution_key=solution["key"], expr_key=ode["key"])
        series = await call("series_expansion", expr_key=solution["rhs_key"], var_name="U", order=5)
        expected = await call("check_equivalence", expr_a=series["key"], expr_b="-R*U - R**2*U**3/6")
        return closed_form, verified, series, expected

    closed_form, verified, series, expected = run(scenario)
    assert closed_form["verdict"] == "proved_equal"
    assert verified == {"verified": True, "residual": "0"}
    assert series["series"] == "-R*U - R**2*U**3/6 + O(U**5)"
    assert expected["verdict"] == "proved_equal"


# Twelve null vectors of the Minkowski metric eta = diag(-1, 1, 1, 1): (1, +-e_i) and (sqrt 2, e_i +- e_j)
NULL_VECTORS = [
    ["1", "1", "0", "0"], ["1", "-1", "0", "0"], ["1", "0", "1", "0"],
    ["1", "0", "-1", "0"], ["1", "0", "0", "1"], ["1", "0", "0", "-1"],
    ["sqrt(2)", "1", "1", "0"], ["sqrt(2)", "1", "-1", "0"], ["sqrt(2)", "1", "0", "1"],
    ["sqrt(2)", "1", "0", "-1"], ["sqrt(2)", "0", "1", "1"], ["sqrt(2)", "0", "1", "-1"],
]
UNKNOWNS = [f"X{a}{b}" for a in range(4) for b in range(a, 4)]  # the 10 independent components


def test_null_tensor_lemma():
    """A symmetric X with X_ab k^a k^b = 0 for 12 null vectors k must be N * eta."""
    async def scenario(call):
        await call("intro_many", variables=UNKNOWNS)
        rows = [[f"X{min(a, b)}{max(a, b)}" for b in range(4)] for a in range(4)]
        X = await call("create_matrix", matrix_data=rows)
        conditions = []
        for k in NULL_VECTORS:
            column = "Matrix([" + ", ".join(f"[{c}]" for c in k) + "])"
            condition = await call(
                "introduce_expression", expression=f"expand(({column}.T * @{X['key']} * {column})[0])"
            )
            conditions.append(condition["key"])
        solution = await call("solve_linear_system", expr_keys=conditions, var_names=UNKNOWNS)
        # Rebuild X from the solution tuple; N is the remaining free component X33
        values = {name: f"@{solution['key']}.args[0][{i}]" for i, name in enumerate(UNKNOWNS)}
        solved = await call("substitute_values", expr_key=X["key"], substitutions=values)
        lemma = await call("check_equivalence", expr_a=solved["key"], expr_b="X33 * diag(-1, 1, 1, 1)")
        free = await call("introduce_expression", expression=f"@{solution['key']}.free_symbols")
        return solution, lemma, free

    solution, lemma, free = run(scenario)
    assert lemma["verdict"] == "proved_equal"
    assert free["result"] == "{X33}"  # exactly one free parameter: X is determined up to N
    assert solution["result"] == "{(-X33, 0, 0, 0, X33, 0, 0, X33, 0, X33)}"


@pytest.mark.skipif(not EINSTEINPY_AVAILABLE, reason="EinsteinPy library is not available")
def test_contracted_bianchi_identity():
    """nabla^a G_ab = 0 for -e^{2a(t,r)} dt^2 + e^{2b(t,r)} dr^2 + R(t,r)^2 dOmega^2."""
    async def scenario(call):
        for name in ("a", "b", "R"):
            await call("introduce_function", func_name=name)
        metric = await call(
            "create_custom_metric",
            components=[
                ["-exp(2*a(t, r))", "0", "0", "0"],
                ["0", "exp(2*b(t, r))", "0", "0"],
                ["0", "0", "R(t, r)**2", "0"],
                ["0", "0", "0", "R(t, r)**2*sin(theta)**2"],
            ],
            coord_symbols=["t", "r", "theta", "phi"],
        )
        einstein = await call("calculate_tensor", metric_key=metric["key"], tensor_type="EinsteinTensor", simplify=False)
        return await call("tensor_divergence", tensor_key=einstein["key"], index=0)

    divergence = run(scenario)
    assert divergence["config"] == "l"
    assert divergence["result"] == "[0, 0, 0, 0]"


def test_entropy_coefficient():
    """dA = (alpha / 2 pi) S together with S = dA / 4 gives alpha = 8 pi."""
    async def scenario(call):
        await call("intro", var_name="alpha", assumptions=["real"])
        await call("intro_many", variables=[["dA", ["positive"], []], ["S", ["positive"], []]])
        first_law = await call("introduce_equation", lhs_expression="dA", rhs_expression="alpha/(2*pi)*S")
        with_entropy = await call("substitute_values", expr_key=first_law["key"], substitutions={"S": "dA/4"})
        return await call("solve_algebraically", expr_key=with_entropy["key"], var_name="alpha", domain="real")

    assert run(scenario)["result"] == "{8*pi}"


def test_units_of_the_temperature():
    """hbar (9.81 m/s^2) / (2 pi c k_B) = 3.978e-20 K."""
    async def scenario(call):
        expr = await call(
            "introduce_expression",
            expression="hbar*(981/100*meter/second**2)/(2*pi*speed_of_light*boltzmann_constant)",
        )
        kelvin = await call("convert_to_units", expr_key=expr["key"], target_units=["kelvin"])
        return await call("evalf_expression", expr_key=kelvin["key"], n=4)

    assert run(scenario)["result"] == "3.978e-20*kelvin"
