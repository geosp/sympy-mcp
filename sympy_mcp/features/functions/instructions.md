# Function and Differential Equation Tools

Use the same `session_id` across all calls to share state. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `expr_key` in subsequent calls).

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

---

## introduce_function
Introduce a symbolic function for use in differential equations.

**When to use:**
- Before setting up an ODE or PDE that involves an unknown function (e.g., `f(x)`, `u(x,t)`)
- When you need `f(x)` notation in expression strings for `dsolve_ode` or `pdsolve_pde`

**When NOT to use:**
- For symbolic variables (plain `x`, `y`) — use `intro` or `intro_many`
- For known/explicit functions like `sin(x)` — these are built into SymPy and don't need introduction

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
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

**When to use:**
- For ODEs involving an unknown function of one variable (e.g., `f''(x) + f(x) = 0`)
- When the problem asks to "solve the differential equation" with ordinary derivatives

**When NOT to use:**
- For PDEs (partial differential equations) — use `pdsolve_pde`
- For algebraic equations (no derivatives) — use `solve_algebraically`
- When you haven't yet introduced the function with `introduce_function`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
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

## dsolve_system
Solve a coupled system of ordinary differential equations.

**When to use:**
- For 2+ coupled ODEs sharing the same independent variable (e.g., `dh1/dt = ...`, `dh2/dt = ...`)
- When `dsolve_ode` would require manually reducing to a single higher-order equation

**When NOT to use:**
- For a single ODE — use `dsolve_ode`
- For PDEs — use `pdsolve_pde`
- When functions haven't been introduced with `introduce_function`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_keys` (list[str]): Session keys of the ODE expressions (each should equal 0 or be an `Eq`).
- `func_names` (list[str]): Names of the functions to solve for (each must be introduced with `introduce_function`).

**Returns:** `result` — comma-separated LaTeX solutions, one per equation; `result_key` — not returned (chain via `introduce_expression` if needed).

**Example:**
```json
POST /functions/dsolve-system
{"session_id": "s1", "expr_keys": ["expr_0", "expr_1"], "func_names": ["h1", "h2"]}
→ {"success": true, "result": "Eq(h_{1}(t), ...), Eq(h_{2}(t), ...)"}
```

---

## pdsolve_pde
Solve a partial differential equation.

**When to use:**
- For PDEs involving an unknown function of multiple variables (e.g., `u_xx + u_yy = 0`)
- When partial derivatives appear in the equation

**When NOT to use:**
- For ODEs (one independent variable) — use `dsolve_ode`
- For algebraic systems — use solving tools

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
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
