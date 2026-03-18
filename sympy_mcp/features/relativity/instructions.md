# Relativity Tools

Use the same `session_id` across all calls to share state. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `metric_key` or `tensor_key` in subsequent calls).

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

**Returns:** `result` — string representation of the metric; `result_key` — session key (e.g. `"metric_Schwarzschild"`) for use in `calculate_tensor`.

**Available predefined metrics:**

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
| `Minkowski` | Minkowski (flat) spacetime in spherical-like coordinates |
| `MinkowskiCartesian` | Minkowski spacetime in Cartesian coordinates |
| `MinkowskiPolar` | Minkowski spacetime in polar coordinates |
| `Kerr` | Rotating black hole (Kerr) |
| `KerrNewman` | Rotating charged black hole (Kerr–Newman) |
| `ReissnerNordstorm` | Charged non-rotating black hole (Reissner–Nordstrom) |
| `Schwarzschild` | Spherically symmetric vacuum black hole |

**Example:**
```json
POST /relativity/metric/predefined
{"session_id": "s1", "metric_name": "Schwarzschild"}
→ {"success": true, "result": "...", "result_key": "metric_Schwarzschild"}
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

**Returns:** `result` — list of matching metric names as a string.

---

## calculate_tensor
Compute a curvature tensor from a stored metric.

**When to use:**
- For computing Ricci scalar, Ricci tensor, Riemann tensor, Einstein tensor, Weyl tensor, etc.
- When the problem involves curvature, geodesics, or field equations in GR

**When NOT to use:**
- Before creating a metric — you must have a stored metric first
- For non-GR tensor operations (e.g., stress tensors in classical mechanics)

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `metric_key` (str): Session key of a stored metric (a `result_key` from `create_predefined_metric` or `create_custom_metric`).
- `tensor_type` (str): One of the tensor type enum values (see table below).
- `simplify` (bool, optional): Whether to simplify the result with `sympy.simplify`. Default: `true`. Set to `false` for large metrics.

**Returns:** `result` — string representation of the tensor; `result_key` — session key (e.g. `"ricciscalar_metric_Schwarzschild"`) for use in `print_latex_tensor`.

**Available tensor types:**

| Enum value | Description |
|---|---|
| `RicciScalar` | Ricci scalar (trace of Ricci tensor) — scalar expression |
| `RicciTensor` | Ricci curvature tensor |
| `RiemannCurvatureTensor` | Riemann curvature tensor (via Christoffel symbols) |
| `SchoutenTensor` | Schouten tensor |
| `StressEnergyMomentumTensor` | Stress-energy-momentum tensor |
| `WeylTensor` | Weyl conformal tensor |
| `EinsteinTensor` | Einstein tensor |

**Example:**
```json
POST /relativity/tensor/calculate
{"session_id": "s1", "metric_key": "metric_Schwarzschild", "tensor_type": "RicciScalar"}
→ {"success": true, "result": "0", "result_key": "ricciscalar_metric_Schwarzschild"}
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
- `components` (list of list of str): 2D list of SymPy expression strings (e.g. `[["1", "0"], ["0", "r**2"]]`). Use `"0"` for zero components.
- `coord_symbols` (list of str): Coordinate variable names (e.g. `["r", "theta"]`).
- `config` (str, optional): Index configuration — `"ll"` for covariant (default) or `"uu"` for contravariant.

**Returns:** `result` — string representation of the metric; `result_key` — session key (e.g. `"metric_custom_0"`) for use in `calculate_tensor`.

**Example (flat 2D polar metric):**
```json
POST /relativity/metric/custom
{"session_id": "s1", "components": [["1", "0"], ["0", "r**2"]], "coord_symbols": ["r", "theta"], "config": "ll"}
→ {"success": true, "result": "...", "result_key": "metric_custom_0"}
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
- `tensor_key` (str): Session key of a stored tensor or metric (a `result_key` from any previous call).

**Returns:** `result` — LaTeX string. No `result_key` — LaTeX output is not stored in the session.
