import pytest
import sympy

from sympy_mcp.shared.enums import Tensor
from sympy_mcp.state import EINSTEINPY_AVAILABLE, SymPyState

pytestmark = pytest.mark.skipif(not EINSTEINPY_AVAILABLE, reason="EinsteinPy library is not available")

SPHERE = ["t", "r", "theta", "phi"]


def flat(state, key):
    return sympy.flatten(state.expressions[key].tolist())


@pytest.fixture
def general_spherical():
    """-e^{2a(t,r)} dt^2 + e^{2b(t,r)} dr^2 + R(t,r)^2 dOmega^2"""
    state = SymPyState()
    for name in ("a", "b", "R"):
        state.introduce_function(name)
    metric = state.create_custom_metric(
        [
            ["-exp(2*a(t, r))", "0", "0", "0"],
            ["0", "exp(2*b(t, r))", "0", "0"],
            ["0", "0", "R(t, r)**2", "0"],
            ["0", "0", "0", "R(t, r)**2*sin(theta)**2"],
        ],
        SPHERE,
    )
    return state, metric


class TestCovariantDerivative:
    def test_metric_is_covariantly_constant(self, general_spherical):
        state, metric = general_spherical
        key = state.covariant_derivative(metric)
        assert key.extras["config"] == "lll"
        assert all(c == 0 for c in flat(state, key))

    def test_vector_in_polar_coordinates(self):
        # V = d/dr in flat polar coordinates: nabla_theta V^theta = Gamma^theta_{theta r} = 1/r
        state = SymPyState()
        metric = state.create_custom_metric([["1", "0"], ["0", "r**2"]], ["r", "theta"])
        vector = state.create_tensor(metric, ["1", "0"], "u")
        derivative = state.covariant_derivative(vector)
        assert derivative.extras["config"] == "ul"
        r = state.metrics[metric].syms[0]
        assert state.expressions[derivative] == sympy.Array([[0, 0], [0, 1 / r]])

    def test_raising_metric_index_gives_delta(self):
        state = SymPyState()
        metric = state.create_custom_metric([["1", "0"], ["0", "r**2"]], ["r", "theta"])
        mixed = state.raise_index(metric, 0)
        assert mixed.extras["config"] == "ul"
        assert state.expressions[mixed] == sympy.Array([[1, 0], [0, 1]])

    def test_rejects_christoffel_symbols(self, general_spherical):
        state, metric = general_spherical
        gamma = state.calculate_tensor(metric, Tensor.CHRISTOFFEL_SYMBOLS, simplify_result=False)
        assert "not a tensor" in state.covariant_derivative(gamma)


class TestDivergence:
    def test_contracted_bianchi_identity(self, general_spherical):
        """nabla^a G_ab = 0 for -e^{2a}dt^2 + e^{2b}dr^2 + R^2 dOmega^2."""
        state, metric = general_spherical
        einstein = state.calculate_tensor(metric, Tensor.EINSTEIN_TENSOR, simplify_result=False)
        div = state.tensor_divergence(einstein, index=0)
        assert div.extras["config"] == "l"
        assert flat(state, div) == [0, 0, 0, 0]

    def test_nonzero_divergence(self):
        # nabla_a V^a for V = r d/dr in flat polar coordinates is (1/r) d_r(r * r) = 2
        state = SymPyState()
        metric = state.create_custom_metric([["1", "0"], ["0", "r**2"]], ["r", "theta"])
        vector = state.create_tensor(metric, ["r", "0"], "u")
        div = state.tensor_divergence(vector, 0)
        assert state.expressions[div.key] == 2

    def test_divergence_of_lower_index_raises_it(self):
        state = SymPyState()
        metric = state.create_custom_metric([["1", "0"], ["0", "r**2"]], ["r", "theta"])
        covector = state.create_tensor(metric, ["r", "0"], "l")  # V_r = r, same field as above
        assert state.expressions[state.tensor_divergence(covector, 0).key] == 2


class TestCreateTensor:
    def test_rank_two(self, general_spherical):
        state, metric = general_spherical
        key = state.create_tensor(metric, [["a(t, r)", "0", "0", "0"]] + [["0"] * 4] * 3, "ll")
        assert key.extras["config"] == "ll"
        t, r = state.metrics[metric].syms[:2]
        assert state.expressions[key][0, 0] == state.functions["a"](t, r)

    def test_shape_mismatch(self, general_spherical):
        state, metric = general_spherical
        assert "Each index needs 4 entries" in state.create_tensor(metric, ["1", "0"], "u")
        assert "deeper" in state.create_tensor(metric, [["1"] * 4] * 4, "u")

    def test_bad_config(self, general_spherical):
        state, metric = general_spherical
        assert "config must be" in state.create_tensor(metric, ["1"] * 4, "x")


class TestContractAndIndices:
    def test_trace_of_metric_is_dimension(self, general_spherical):
        state, metric = general_spherical
        trace = state.contract_indices(metric, 0, 1)
        assert state.expressions[trace.key] == 4

    def test_ricci_scalar_from_contraction(self, general_spherical):
        state, metric = general_spherical
        ricci = state.calculate_tensor(metric, Tensor.RICCI_TENSOR, simplify_result=False)
        scalar = state.calculate_tensor(metric, Tensor.RICCI_SCALAR)
        contracted = state.contract_indices(ricci, 0, 1)
        assert sympy.simplify(state.expressions[contracted.key] - state.expressions[scalar]) == 0

    def test_raise_then_lower_round_trips(self, general_spherical):
        state, metric = general_spherical
        ricci = state.calculate_tensor(metric, Tensor.RICCI_TENSOR)
        up = state.raise_index(ricci, 1)
        assert up.extras["config"] == "lu"
        down = state.lower_index(up, 1)
        assert down.extras["config"] == "ll"
        diff = [sympy.simplify(a - b) for a, b in zip(flat(state, down), flat(state, ricci))]
        assert diff == [0] * 16

    def test_index_already_in_position(self, general_spherical):
        state, metric = general_spherical
        assert "already lower" in state.lower_index(metric, 0)


class TestTensorComponent:
    def test_vaidya_einstein_tensor(self):
        """Vaidya: the only nonzero component of G_ab is G_vv = 2 m'(v) / r^2."""
        state = SymPyState()
        state.introduce_function("m")
        metric = state.create_custom_metric(
            [
                ["-(1 - 2*m(v)/r)", "1", "0", "0"],
                ["1", "0", "0", "0"],
                ["0", "0", "r**2", "0"],
                ["0", "0", "0", "r**2*sin(theta)**2"],
            ],
            ["v", "r", "theta", "phi"],
        )
        einstein = state.calculate_tensor(metric, Tensor.EINSTEIN_TENSOR)
        g_vv = state.tensor_component(einstein, ["v", "v"])
        v, r = state.metrics[metric].syms[:2]
        m = state.functions["m"]
        assert sympy.simplify(state.expressions[g_vv.key] - 2 * sympy.diff(m(v), v) / r**2) == 0
        others = [c for i, c in enumerate(flat(state, einstein)) if i != 0]
        assert others == [0] * 15

    def test_integer_indices(self):
        state = SymPyState()
        metric = state.create_predefined_metric("Schwarzschild")
        g_tt = state.tensor_component(metric, [0, 0])
        r, r_s = sympy.symbols("r r_s")
        assert sympy.simplify(state.expressions[g_tt.key] - (1 - r_s / r)) == 0

    def test_wrong_number_of_indices(self):
        state = SymPyState()
        metric = state.create_predefined_metric("Schwarzschild")
        assert "rank 2" in state.tensor_component(metric, [0])


class TestKretschmann:
    def test_schwarzschild(self):
        state = SymPyState()
        metric = state.create_custom_metric(
            [
                ["-(1 - 2*M/r)", "0", "0", "0"],
                ["0", "1/(1 - 2*M/r)", "0", "0"],
                ["0", "0", "r**2", "0"],
                ["0", "0", "0", "r**2*sin(theta)**2"],
            ],
            SPHERE,
        )
        k = state.kretschmann_scalar(metric)
        M, r = sympy.Symbol("M"), state.metrics[metric].syms[1]
        assert sympy.simplify(state.expressions[k.key] - 48 * M**2 / r**6) == 0


class TestKillingEquation:
    def test_boost_in_null_coordinates(self):
        """V d_V - U d_U is a Killing vector of -2 dU dV + dy^2 + dz^2."""
        state = SymPyState()
        metric = state.create_custom_metric(
            [["0", "-1", "0", "0"], ["-1", "0", "0", "0"], ["0", "0", "1", "0"], ["0", "0", "0", "1"]],
            ["U", "V", "y", "z"],
        )
        result = state.killing_equation(metric, ["-U", "V", "0", "0"])
        assert result.extras["satisfied"] is True
        assert flat(state, result) == [0] * 16

    def test_non_killing_vector(self):
        state = SymPyState()
        metric = state.create_custom_metric(
            [["0", "-1", "0", "0"], ["-1", "0", "0", "0"], ["0", "0", "1", "0"], ["0", "0", "0", "1"]],
            ["U", "V", "y", "z"],
        )
        result = state.killing_equation(metric, ["U", "V", "0", "0"])  # dilation, not an isometry
        assert result.extras["satisfied"] is False

    def test_rotation_on_sphere(self, general_spherical):
        state, metric = general_spherical
        assert state.killing_equation(metric, ["0", "0", "0", "1"]).extras["satisfied"] is True

    def test_wrong_number_of_components(self, general_spherical):
        state, metric = general_spherical
        assert "needs 4 components" in state.killing_equation(metric, ["1"])
