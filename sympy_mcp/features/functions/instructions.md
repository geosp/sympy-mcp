# Function and Differential Equation Tools

Use the same `session_id` across all calls to share state. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `expr_key` in subsequent calls).

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

---

## introduce_function
Introduce a symbolic function for use in differential equations.

**Parameters:**
- `session_id` (str): Session identifier. Pass any string — sessions are auto-created on first use.
- `func_name` (str): Name of the function (e.g., `"f"`, `"g"`, `"u"`).

**Returns:** `result` — the function name confirming creation (e.g. `"f"`). No `result_key` — functions are referenced by name, not by key.

**Example:**
```json
POST /functions/introduce
{"session_id": "s1", "func_name": "f"}
→ {"success": true, "result": "f"}
```

---

## dsolve_ode
Solve an ordinary differential equation.

**Parameters:**
- `session_id` (str): Session identifier.
- `expr_key` (str): Session key of the ODE expression (the equation, which should equal 0).
- `func_name` (str): Name of the function to solve for (must be introduced with `introduce_function`).
- `hint` (str, optional): ODE solver hint. Default: `"default"`.

**Returns:** `result` — the solution as a string (e.g. `"Eq(f(x), C1*exp(x))"`); `result_key` — session key for chaining.

**Example:**
```json
POST /functions/dsolve
{"session_id": "s1", "expr_key": "expr_0", "func_name": "f"}
→ {"success": true, "result": "Eq(f(x), C1*exp(x))", "result_key": "expr_1"}
```

---

## pdsolve_pde
Solve a partial differential equation.

**Parameters:**
- `session_id` (str): Session identifier.
- `expr_key` (str): Session key of the PDE expression.
- `func_name` (str): Name of the function to solve for (must be introduced with `introduce_function`).
- `hint` (str, optional): PDE solver hint. Default: `"default"`.

**Returns:** `result` — the solution as a string; `result_key` — session key for chaining.

**Example:**
```json
POST /functions/pdsolve
{"session_id": "s1", "expr_key": "expr_0", "func_name": "u"}
→ {"success": true, "result": "Eq(u(x, y), F(x + y))", "result_key": "expr_1"}
```
