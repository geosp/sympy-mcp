# Vector Calculus Tools

Use the same `session_id` across all calls to share state. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `vector_field_key` or `scalar_field_key` in subsequent calls).

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

---

## create_coordinate_system
Creates a 3D Cartesian coordinate system. After creation, the basis vectors are available in the session as `{coord_sys_name}_x`, `{coord_sys_name}_y`, `{coord_sys_name}_z`.

**When to use:**
- As the first step before any vector calculus operation (gradient, curl, divergence)
- When a problem involves vector fields in 3D space

**When NOT to use:**
- When doing scalar calculus (differentiation, integration) — use calculus tools directly
- A coordinate system has already been created in this session

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `coord_sys_name` (str): Name for the coordinate system (e.g., `"R"`).
- `coord_names` (list of str, optional): Exactly 3 names for the coordinate axes (e.g., `["x", "y", "z"]`). Defaults to `x`, `y`, `z`.

**Returns:** `result` — the coordinate system name (e.g. `"R"`); `result_key` — session key (same as name) for use in `create_vector_field`.

**Example:**
```json
POST /vector/coordinate_system
{"session_id": "s1", "coord_sys_name": "R"}
→ {"success": true, "result": "R", "result_key": "R"}
```

---

## create_vector_field
Creates a vector field in a previously created coordinate system.

**When to use:**
- To define a vector field for curl, divergence, or other vector calculus operations
- When the problem specifies a field like `F = (x², xy, z)`

**When NOT to use:**
- For scalar fields — use `introduce_expression` (gradient takes a scalar key)
- For matrices or column vectors in linear algebra — use `create_matrix`
- Before creating a coordinate system — one must exist first

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `coord_sys_name` (str): Name of an existing coordinate system.
- `comp_x` (str): Expression string for the x-component.
- `comp_y` (str): Expression string for the y-component.
- `comp_z` (str): Expression string for the z-component.

**Returns:** `result` — the vector field as a string; `result_key` — session key for chaining (e.g. `"vector_0"`).

**Notes:**
- Component expressions can reference session variables and coordinate scalars (e.g. `"R.x"`, `"R.y"`).

**Example:**
```json
POST /vector/field
{"session_id": "s1", "coord_sys_name": "R", "comp_x": "R.x", "comp_y": "R.y", "comp_z": "0"}
→ {"success": true, "result": "R.x*R.i + R.y*R.j", "result_key": "vector_0"}
```

---

## calculate_curl
Calculates the curl of a vector field.

**When to use:**
- To determine if a vector field is conservative (curl = 0)
- When the problem asks for ∇ × F
- In electromagnetism (Faraday's law, Ampère's law)

**When NOT to use:**
- For scalar fields — curl operates on vector fields only
- For 2D problems where only divergence matters

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `vector_field_key` (str): Session key of an existing vector field (a `result_key` from `create_vector_field`).

**Returns:** `result` — the curl as a string; `result_key` — session key for chaining.

**Example:**
```json
POST /vector/curl
{"session_id": "s1", "vector_field_key": "vector_0"}
→ {"success": true, "result": "0", "result_key": "vector_1"}
```

---

## calculate_divergence
Calculates the divergence of a vector field, producing a scalar expression.

**When to use:**
- To check if a field is solenoidal (div = 0)
- When the problem asks for ∇ · F
- In fluid dynamics (continuity equation) or electromagnetism (Gauss's law)

**When NOT to use:**
- For scalar fields — divergence operates on vector fields only
- When you need gradient (scalar → vector) rather than divergence (vector → scalar)

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `vector_field_key` (str): Session key of an existing vector field.

**Returns:** `result` — the divergence as a string (scalar); `result_key` — session key for chaining.

**Example:**
```json
POST /vector/divergence
{"session_id": "s1", "vector_field_key": "vector_0"}
→ {"success": true, "result": "2", "result_key": "expr_0"}
```

---

## calculate_gradient
Calculates the gradient of a scalar field, producing a vector field.

**When to use:**
- When computing ∇f for a scalar function f
- To find the direction of steepest ascent
- In physics for force fields derived from potentials (F = -∇V)

**When NOT to use:**
- On vector fields — use curl or divergence instead
- For ordinary derivatives of 1D functions — use `differentiate_expression`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `scalar_field_key` (str): Session key of an existing scalar expression (a `result_key` from a previous call).

**Returns:** `result` — the gradient as a string (vector); `result_key` — session key for chaining.

**Notes:**
- The scalar field must be defined within a coordinate system context for the gradient to be computed correctly.

**Example:**
```json
POST /vector/gradient
{"session_id": "s1", "scalar_field_key": "expr_0"}
→ {"success": true, "result": "R.i + R.j", "result_key": "vector_1"}
```
