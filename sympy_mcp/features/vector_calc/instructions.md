# Vector Calculus Tools

Use the same `session_id` across all calls to share state. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `vector_field_key` or `scalar_field_key` in subsequent calls).

---

## create_coordinate_system
Creates a 3D Cartesian coordinate system. After creation, the basis vectors are available in the session as `{name}_x`, `{name}_y`, `{name}_z`.

**Parameters:**
- `session_id` (str): Session identifier. Pass any string — sessions are auto-created on first use.
- `name` (str): Name for the coordinate system (e.g., `"R"`).
- `coord_names` (list of str, optional): Exactly 3 names for the coordinate axes (e.g., `["x", "y", "z"]`). Defaults to `x`, `y`, `z`.

**Returns:** `result` — the coordinate system name (e.g. `"R"`); `result_key` — session key (same as name) for use in `create_vector_field`.

**Example:**
```json
POST /vector/coordinate_system
{"session_id": "s1", "name": "R"}
→ {"success": true, "result": "R", "result_key": "R"}
```

---

## create_vector_field
Creates a vector field in a previously created coordinate system.

**Parameters:**
- `session_id` (str): Session identifier.
- `coord_sys_name` (str): Name of an existing coordinate system.
- `x` (str): Expression string for the x-component.
- `y` (str): Expression string for the y-component.
- `z` (str): Expression string for the z-component.

**Returns:** `result` — the vector field as a string; `result_key` — session key for chaining (e.g. `"vector_0"`).

**Notes:**
- Component expressions can reference session variables and coordinate scalars (e.g. `"R.x"`, `"R.y"`).

**Example:**
```json
POST /vector/field
{"session_id": "s1", "coord_sys_name": "R", "x": "R.x", "y": "R.y", "z": "0"}
→ {"success": true, "result": "R.x*R.i + R.y*R.j", "result_key": "vector_0"}
```

---

## calculate_curl
Calculates the curl of a vector field.

**Parameters:**
- `session_id` (str): Session identifier.
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

**Parameters:**
- `session_id` (str): Session identifier.
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

**Parameters:**
- `session_id` (str): Session identifier.
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
