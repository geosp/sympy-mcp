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
