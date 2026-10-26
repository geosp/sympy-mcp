# Relativity Tools

Use the same `session_id` across all calls to share state. See the session tools (`create_session`, `list_session_state`) for session management.

Expression strings can refer to stored results with `@key` — for example `"@expr_7 - @expr_9"` or `"diff(@expr_3, x)"` — instead of retyping them. The referenced value is used exactly as stored. An unknown key is an error. `@` directly after an operand (`A@B`) keeps its meaning of matrix multiplication; use `*` to multiply by a reference (`2*@expr_1`).

Computing tools return JSON by default: `{"key": ..., "result": ..., "latex": ...}`. `key` is the session key the result is stored under (pass it to later calls, or reference it as `@key` in an expression string), `result` is the value as a SymPy string, and `latex` is its LaTeX form. Some tools add extra fields, listed under Returns. Failures return `{"error": "..."}`. Pass `output_format="legacy"` to get the plain string these tools returned before (usually just the key).

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

---

## create_predefined_metric
Load a standard spacetime metric by name. The metric is stored in the session under a key of the form `metric_<name>`.

**When to use:**
- When the problem involves a well-known spacetime (Schwarzschild, Kerr, Minkowski, etc.)
- As the starting point for tensor calculations in general relativity

**When NOT to use:**
- When the metric is non-standard or user-defined — use `create_custom_metric`
- When you're unsure which metric to use — try `search_predefined_metrics` first

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `metric_name` (str): One of the predefined metric enum values (see table below).
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — string representation of the metric; `key` — session key (e.g. `"metric_Schwarzschild"`) for use in `calculate_tensor`; `latex` — the result in LaTeX.

**Available predefined metrics** (all 19 are implemented; names keep einsteinpy's spelling, e.g. `ReissnerNordstorm`, `BarriolaVilekin`):

| Enum value | Description |
|---|---|
| `AlcubierreWarp` | Alcubierre warp-drive metric |
| `BarriolaVilekin` | Barriola–Vilekin global monopole |
| `BertottiKasner` | Bertotti–Kasner metric |
| `BesselGravitationalWave` | Bessel gravitational wave |
| `CMetric` | C-metric (accelerating black holes) |
| `Davidson` | Davidson metric |
| `AntiDeSitter` | Anti-de Sitter space |
| `AntiDeSitterStatic` | Static Anti-de Sitter |
| `DeSitter` | De Sitter space |
| `Ernst` | Ernst metric |
| `Godel` | Godel universe |
| `JanisNewmanWinicour` | Janis–Newman–Winicour metric |
| `Minkowski` | Minkowski (flat) spacetime in Cartesian coordinates (same as `MinkowskiCartesian`) |
| `MinkowskiCartesian` | Minkowski spacetime in Cartesian coordinates |
| `MinkowskiPolar` | Minkowski spacetime in polar coordinates |
| `Kerr` | Rotating black hole (Kerr) |
| `KerrNewman` | Rotating charged black hole (Kerr–Newman) |
| `ReissnerNordstorm` | Charged non-rotating black hole (Reissner–Nordstrom) |
| `Schwarzschild` | Spherically symmetric vacuum black hole |

**Example:**
```
create_predefined_metric(session_id="s1", metric_name="Schwarzschild")
→ {"key": "metric_Schwarzschild", "result": "[[1 - r_s/r, 0, 0, 0], [0, -1/(c**2*(1 - r_s/r)), 0, 0], ...]", "latex": "..."}
```

---

## search_predefined_metrics
Search for available metrics by keyword.

**When to use:**
- When you're unsure of the exact metric name or want to explore what's available
- When the user describes a spacetime by informal name and you need to find the matching enum value

**When NOT to use:**
- When you already know the exact metric enum name — use `create_predefined_metric` directly

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `query` (str): Search keyword (delegated to `einsteinpy.symbolic.predefined.find`).

**Returns:** Plain text listing the matching metric names. Every name returned can be passed to `create_predefined_metric`.

---

## calculate_tensor
Compute a curvature tensor from a stored metric.

**When to use:**
- For computing Christoffel symbols, Ricci scalar, Ricci tensor, Riemann tensor, Schouten tensor, Einstein tensor, Weyl tensor, etc.
- When the problem involves curvature, geodesics, or field equations in GR

**When NOT to use:**
- Before creating a metric — you must have a stored metric first
- For non-GR tensor operations (e.g., stress tensors in classical mechanics)

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `metric_key` (str): Session key of a stored metric (the `key` returned by `create_predefined_metric` or `create_custom_metric`).
- `tensor_type` (str): One of the tensor type enum values (see table below).
- `simplify` (bool, optional): Whether to apply `sympy.simplify` to every component of the result (or to the scalar, for `RicciScalar`). Default: `true`. Set to `false` for large metrics such as Kerr or Kerr–Newman, where simplifying every component can take a long time.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — string representation of the tensor; `key` — session key (e.g. `"ricciscalar_metric_Schwarzschild"`) for use in `print_latex_tensor`; `latex` — the result in LaTeX.

**Available tensor types:**

| Enum value | Description |
|---|---|
| `ChristoffelSymbols` | Christoffel symbols of the second kind, index config `ull` (Γ^a_bc) |
| `RicciScalar` | Ricci scalar (trace of Ricci tensor) — scalar expression |
| `RicciTensor` | Ricci curvature tensor |
| `RiemannCurvatureTensor` | Riemann curvature tensor, index config `ulll` (R^a_bcd) |
| `SchoutenTensor` | Schouten tensor |
| `StressEnergyMomentumTensor` | Stress-energy-momentum tensor |
| `WeylTensor` | Weyl conformal tensor |
| `EinsteinTensor` | Einstein tensor |

**Example:**
```
calculate_tensor(session_id="s1", metric_key="metric_Schwarzschild", tensor_type="RicciScalar")
→ {"key": "ricciscalar_metric_Schwarzschild", "result": "0", "latex": "0"}
```

---

## create_custom_metric
Define a metric from an explicit component array.

**When to use:**
- When the spacetime metric is non-standard and not in the predefined list
- For user-defined or parameterized metrics
- For lower-dimensional toy metrics (e.g., 2D surfaces)

**When NOT to use:**
- For standard metrics like Schwarzschild or Kerr — use `create_predefined_metric` (less error-prone)
- When you're unsure of the components — check the predefined list first

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `components` (list of list of str): 2D list of SymPy expression strings (e.g. `[["1", "0"], ["0", "r**2"]]`). Use `"0"` for zero components. Components can use any symbol introduced with `intro`/`intro_many` (with its assumptions) and any function introduced with `introduce_function`, e.g. `"-exp(2*a(t, r))"`.
- `coord_symbols` (list of str): Coordinate variable names (e.g. `["r", "theta"]`). If a name matches a symbol already introduced in the session, that symbol (and its assumptions) is used as the coordinate.
- `config` (str, optional): Index configuration — `"ll"` for covariant (default) or `"uu"` for contravariant.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — string representation of the metric; `key` — session key (e.g. `"metric_custom_0"`) for use in `calculate_tensor`; `latex` — the result in LaTeX.

**Example (flat 2D polar metric):**
```
create_custom_metric(session_id="s1", components=[["1", "0"], ["0", "r**2"]], coord_symbols=["r", "theta"], config="ll")
→ {"key": "metric_custom_0", "result": "[[1, 0], [0, r**2]]", "latex": "\\left[\\begin{matrix}1 & 0\\\\0 & r^{2}\\end{matrix}\\right]"}
```

---

## print_latex_tensor
Render a stored tensor or metric as a LaTeX string.

**When to use:**
- Only for final display of tensor/metric results to the user in LaTeX format
- When the user explicitly requests LaTeX output for a tensor

**When NOT to use:**
- To inspect tensor values — use `list_session_state`
- As a routine step after every tensor computation

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `tensor_key` (str): Session key of a stored tensor or metric (the `key` returned by any previous call).

**Returns:** The LaTeX string as plain text. It is not stored in the session. (Computing tools already include `latex` in their JSON payload, so this is only needed for metrics or tensors created with `output_format="legacy"`.)

---

## create_tensor
Create a tensor from explicit components in the coordinates of a stored metric, e.g. a vector field, a one-form, or a stress-energy tensor.

**When to use:**
- To define a vector or tensor field you want to differentiate, contract or take the divergence of
- To build a stress-energy tensor to compare with the Einstein tensor

**When NOT to use:**
- For a metric — use `create_custom_metric`
- For curvature tensors — use `calculate_tensor`
- For a Killing-vector check — `killing_equation` takes the components directly

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `metric_key` (str): The metric whose coordinates (and index raising/lowering) the tensor uses.
- `components` (nested list of str): One level of nesting per index, each with one entry per coordinate. A vector is `["r", "0"]`, a rank-2 tensor `[["1", "0"], ["0", "r**2"]]`. Entries may use the metric's coordinates, session symbols and functions, and `@key` references.
- `config` (str): Index positions, one letter per index: `"u"` (contravariant) or `"l"` (covariant), e.g. `"u"`, `"ll"`, `"ul"`.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the key only.

**Returns:** JSON — `key` (e.g. `"tensor_5"`), `result` / `latex` — the components; `config` — the index configuration.

**Example:**
```
# V = d/dr in flat polar coordinates (metric_custom_0: [[1, 0], [0, r**2]], coordinates r, theta)
create_tensor(session_id="s1", metric_key="metric_custom_0", components=["1", "0"], config="u")
→ {"key": "tensor_1", "result": "[1, 0]", "latex": "...", "config": "u"}
```

---

## covariant_derivative
Covariant derivative of a stored tensor or metric. The derivative index is appended as the **last** index: for `T` with config `"ul"`, the result has config `"ull"` and component `[a, b, c]` is `∇_c T^a_b`.

**When to use:**
- To differentiate a tensor field on a curved background
- As a building block for conservation laws, geodesic deviation, Killing equations

**When NOT to use:**
- For a divergence `∇_a T^{a...}` — use `tensor_divergence`, which also does the contraction
- On Christoffel symbols — they are not a tensor, and the tool rejects them

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `tensor_key` (str): A stored tensor (from `calculate_tensor`, `create_tensor` or another tensor tool) or a metric key.
- `metric_key` (str, optional): The metric to use. Default: the tensor's own metric.
- `simplify` (bool, optional): Simplify every component. Default: `true`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key` (e.g. `"tensor_6"`), `result` / `latex` — the components; `config` — the new index configuration.

**Example:**
```
covariant_derivative(session_id="s1", tensor_key="tensor_1")
→ {"key": "tensor_2", "result": "[[0, 0], [0, 1/r]]", "latex": "...", "config": "ul"}
```

---

## tensor_divergence
Divergence of a stored tensor on one index: `∇_a T^{...a...}`. If that index is covariant, it is raised with the metric first, so for the Einstein tensor `G_ab` with `index=0` this computes `∇^a G_ab`.

**When to use:**
- To check conservation laws such as `∇^a G_ab = 0` (contracted Bianchi identity) or `∇^a T_ab = 0`
- To compute the divergence of a vector field on a curved space

**When NOT to use:**
- For vector fields in flat 3D Cartesian space — `calculate_divergence` is simpler
- When you want the full derivative without contracting — use `covariant_derivative`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `tensor_key` (str): A stored tensor or metric key.
- `index` (int, optional): Position (0-based) of the index to contract with the derivative. Default: `0`.
- `metric_key` (str, optional): The metric to use. Default: the tensor's own metric.
- `simplify` (bool, optional): Simplify every component. Default: `true`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — for a rank ≥ 2 tensor, `key` (e.g. `"tensor_7"`), the remaining components and `config`; for a vector, the scalar divergence stored as an expression (`"expr_N"`).

**Example:**
```
tensor_divergence(session_id="s1", tensor_key="einsteintensor_metric_custom_0", index=0)
→ {"key": "tensor_3", "result": "[0, 0, 0, 0]", "latex": "...", "config": "l"}
```

---

## contract_indices
Contract two indices of a stored tensor. If both are upper (or both lower), one is lowered (raised) with the metric first.

**When to use:**
- To take traces, e.g. `R = R^a_a` from the Ricci tensor, or `T = T^a_a`
- To build scalars from tensors

**When NOT to use:**
- For the divergence of a tensor — use `tensor_divergence`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `tensor_key` (str): A stored tensor or metric key.
- `index_a` (int): Position (0-based) of the first index.
- `index_b` (int): Position (0-based) of the second index.
- `metric_key` (str, optional): The metric to use. Default: the tensor's own metric.
- `simplify` (bool, optional): Simplify the result. Default: `true`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — the contracted tensor (`"tensor_N"` with `config`), or, if no indices remain, a scalar stored as `"expr_N"`.

**Example:**
```
contract_indices(session_id="s1", tensor_key="riccitensor_metric_custom_0", index_a=0, index_b=1)
→ {"key": "expr_4", "result": "...", "latex": "..."}
```

---

## raise_index
Raise one index of a stored tensor with the inverse metric (`T^a = g^{ab} T_b`).

**When to use:**
- To change index positions before comparing tensors or reading mixed components such as `T^a_b`

**When NOT to use:**
- Before `contract_indices` or `tensor_divergence` — they raise or lower as needed

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `tensor_key` (str): A stored tensor or metric key.
- `index` (int): Position (0-based) of the index to raise. It must currently be lower.
- `metric_key` (str, optional): The metric to use. Default: the tensor's own metric.
- `simplify` (bool, optional): Simplify every component. Default: `true`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key` (`"tensor_N"`), the components and the new `config`.

**Example:**
```
raise_index(session_id="s1", tensor_key="riccitensor_metric_Schwarzschild", index=0)
→ {"key": "tensor_5", "result": "...", "latex": "...", "config": "ul"}
```

---

## lower_index
Lower one index of a stored tensor with the metric (`T_a = g_{ab} T^b`).

**When to use:**
- To get covariant components, e.g. turning the Riemann tensor `R^a_bcd` into `R_abcd`

**When NOT to use:**
- Before `contract_indices` or `tensor_divergence` — they raise or lower as needed

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `tensor_key` (str): A stored tensor or metric key.
- `index` (int): Position (0-based) of the index to lower. It must currently be upper.
- `metric_key` (str, optional): The metric to use. Default: the tensor's own metric.
- `simplify` (bool, optional): Simplify every component. Default: `true`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key` (`"tensor_N"`), the components and the new `config`.

**Example:**
```
lower_index(session_id="s1", tensor_key="riemanncurvaturetensor_metric_Schwarzschild", index=0)
→ {"key": "tensor_6", "result": "...", "latex": "...", "config": "llll"}
```

---

## tensor_component
Store one component of a tensor or metric as an expression, so it can be simplified, solved, series-expanded or compared.

**When to use:**
- To read off a specific component such as `G_vv` or `R^t_{rtr}`
- To feed a component into `check_equivalence`, `solve_algebraically` or `series_expansion`

**When NOT to use:**
- To see all components — the tensor's own `result` already lists them

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `tensor_key` (str): A stored tensor or metric key.
- `indices` (list of int or str): One entry per index, either a 0-based position or a coordinate name, e.g. `[0, 0]` or `["v", "v"]`.
- `simplify` (bool, optional): Simplify the component. Default: `true`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key` (`"expr_N"`), `result`, `latex` — the component.

**Example:**
```
tensor_component(session_id="s1", tensor_key="einsteintensor_metric_custom_0", indices=["v", "v"])
→ {"key": "expr_7", "result": "2*Derivative(m(v), v)/r**2", "latex": "..."}
```

---

## kretschmann_scalar
Compute the Kretschmann scalar `R_abcd R^abcd` of a stored metric.

**When to use:**
- To tell genuine curvature singularities from coordinate singularities (e.g. `48 M²/r⁶` for Schwarzschild blows up only at `r = 0`)

**When NOT to use:**
- For the Ricci scalar — use `calculate_tensor` with `RicciScalar`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `metric_key` (str): A stored metric.
- `simplify` (bool, optional): Simplify the result. Default: `true`. Large metrics (e.g. Kerr) can take a long time to simplify.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key` (`"expr_N"`), `result`, `latex` — the scalar.

**Example:**
```
kretschmann_scalar(session_id="s1", metric_key="metric_custom_0")
→ {"key": "expr_8", "result": "48*M**2/r**6", "latex": "\\frac{48 M^{2}}{r^{6}}"}
```

---

## killing_equation
Evaluate Killing's equation `∇_(a ξ_b) = (∇_a ξ_b + ∇_b ξ_a) / 2` for a vector field `ξ` on a stored metric. `ξ` is a Killing vector (an isometry) exactly when every component is zero.

**When to use:**
- To check whether a vector field generates a symmetry, e.g. a boost `V ∂_V - U ∂_U` in flat null coordinates
- To find the conditions a candidate Killing vector must satisfy (the nonzero components)

**When NOT to use:**
- For conformal Killing vectors — this checks the ordinary Killing equation only

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `metric_key` (str): A stored metric.
- `vector` (list of str): One component per coordinate, in the metric's coordinate order, e.g. `["-U", "V", "0", "0"]` for `V ∂_V - U ∂_U` in coordinates `(U, V, y, z)`.
- `vector_config` (str, optional): `"u"` if the components are `ξ^a` (default), `"l"` if they are `ξ_a`.
- `simplify` (bool, optional): Simplify every component. Default: `true`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key` (`"tensor_N"`), the symmetric tensor `∇_(a ξ_b)` (`config` `"ll"`), and `satisfied`: `true` if every component is zero, `false` if not, or `null` when `simplify=false` left components that might still be zero.

**Example:**
```
killing_equation(session_id="s1", metric_key="metric_custom_0", vector=["-U", "V", "0", "0"])
→ {"key": "tensor_9", "result": "[[0, 0, 0, 0], ...]", "latex": "...", "config": "ll", "satisfied": true}
```
