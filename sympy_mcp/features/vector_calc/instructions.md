# Vector Calculus Tools

Use the same `session_id` across all calls to share state. See the session tools (`create_session`, `list_session_state`) for session management.

Expression strings can refer to stored results with `@key` — for example `"@expr_7 - @expr_9"` or `"diff(@expr_3, x)"` — instead of retyping them. The referenced value is used exactly as stored. An unknown key is an error. `@` directly after an operand (`A@B`) keeps its meaning of matrix multiplication; use `*` to multiply by a reference (`2*@expr_1`).

Computing tools return JSON by default: `{"key": ..., "result": ..., "latex": ...}`. `key` is the session key the result is stored under (pass it to later calls, or reference it as `@key` in an expression string), `result` is the value as a SymPy string, and `latex` is its LaTeX form. Some tools add extra fields, listed under Returns. Failures return `{"error": "..."}`. Pass `output_format="legacy"` to get the plain string these tools returned before (usually just the key).

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

**Returns:** The coordinate system name as plain text (e.g. `"R"`). It is also its session key: pass it as `coord_sys_name`, or reference it as `@R` in expression strings.

**Example:**
```
create_coordinate_system(session_id="s1", coord_sys_name="R")
→ "R"
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
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the vector field as a string; `key` — session key for chaining (e.g. `"vector_0"`); `latex` — the result in LaTeX.

**Notes:**
- Component expressions can reference session variables and coordinate scalars (e.g. `"R.x"`, `"R.y"`).

**Example:**
```
create_vector_field(session_id="s1", coord_sys_name="R", comp_x="R.x", comp_y="R.y", comp_z="0")
→ {"key": "vector_0", "result": "R.x*R.i + R.y*R.j", "latex": "\\left(\\mathbf{{x}_{R}}\\right)\\mathbf{\\hat{i}_{R}} + \\left(\\mathbf{{y}_{R}}\\right)\\mathbf{\\hat{j}_{R}}"}
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
- `vector_field_key` (str): Session key of an existing vector field (the `key` returned by `create_vector_field`).
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the curl as a string; `key` — session key for chaining; `latex` — the result in LaTeX.

**Example:**
```
calculate_curl(session_id="s1", vector_field_key="vector_0")
→ {"key": "vector_1", "result": "0", "latex": "\\mathbf{\\hat{0}}"}
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
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the divergence as a string (scalar); `key` — session key for chaining; `latex` — the result in LaTeX.

**Example:**
```
calculate_divergence(session_id="s1", vector_field_key="vector_0")
→ {"key": "expr_0", "result": "2", "latex": "2"}
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
- `scalar_field_key` (str): Session key of an existing scalar expression (the `key` returned by a previous call).
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the gradient as a string (vector); `key` — session key for chaining; `latex` — the result in LaTeX.

**Notes:**
- The scalar field must be defined within a coordinate system context for the gradient to be computed correctly.

**Example:**
```
calculate_gradient(session_id="s1", scalar_field_key="expr_0")
→ {"key": "vector_1", "result": "R.i + R.j", "latex": "\\mathbf{\\hat{i}_{R}} + \\mathbf{\\hat{j}_{R}}"}
```
