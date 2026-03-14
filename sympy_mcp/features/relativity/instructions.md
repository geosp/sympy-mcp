# Relativity Tools

Use the same `session_id` across all calls to share state. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `metric_key` or `tensor_key` in subsequent calls).

> **Note:** This feature requires the optional `einsteinpy` package. Install it with:
> ```
> pip install einsteinpy
> ```
> If `einsteinpy` is not installed, all tools will return an error string indicating the missing dependency.

---

## create_predefined_metric
Load a standard spacetime metric by name. The metric is stored in the session under a key of the form `metric_<name>`.

**Parameters:**
- `session_id` (str): Session identifier. Pass any string — sessions are auto-created on first use.
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

**Parameters:**
- `session_id` (str): Session identifier.
- `query` (str): Search keyword (delegated to `einsteinpy.symbolic.predefined.find`).

**Returns:** `result` — list of matching metric names as a string.

---

## calculate_tensor
Compute a curvature tensor from a stored metric.

**Parameters:**
- `session_id` (str): Session identifier.
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

**Parameters:**
- `session_id` (str): Session identifier.
- `components` (list of list of str): 2D list of SymPy expression strings (e.g. `[["1", "0"], ["0", "r**2"]]`). Use `"0"` for zero components.
- `symbols` (list of str): Coordinate variable names (e.g. `["r", "theta"]`).
- `config` (str, optional): Index configuration — `"ll"` for covariant (default) or `"uu"` for contravariant.

**Returns:** `result` — string representation of the metric; `result_key` — session key (e.g. `"metric_custom_0"`) for use in `calculate_tensor`.

**Example (flat 2D polar metric):**
```json
POST /relativity/metric/custom
{"session_id": "s1", "components": [["1", "0"], ["0", "r**2"]], "symbols": ["r", "theta"], "config": "ll"}
→ {"success": true, "result": "...", "result_key": "metric_custom_0"}
```

---

## print_latex_tensor
Render a stored tensor or metric as a LaTeX string.

**Parameters:**
- `session_id` (str): Session identifier.
- `tensor_key` (str): Session key of a stored tensor or metric (a `result_key` from any previous call).

**Returns:** `result` — LaTeX string. No `result_key` — LaTeX output is not stored in the session.
