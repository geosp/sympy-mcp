# Function and Differential Equation Tools

Use the same `session_id` across all calls to share state. See the session tools (`create_session`, `list_session_state`) for session management.

Computing tools return JSON by default: `{"key": ..., "result": ..., "latex": ...}`. `key` is the session key the result is stored under (pass it to later calls, or reference it as `@key` in an expression string), `result` is the value as a SymPy string, and `latex` is its LaTeX form. Some tools add extra fields, listed under Returns. Failures return `{"error": "..."}`. Pass `output_format="legacy"` to get the plain string these tools returned before (usually just the key).

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

**Returns:** The function name as plain text (e.g. `"f"`). Functions are referenced by name in expression strings, not by key.

**Example:**
```
introduce_function(session_id="s1", func_name="f")
→ "f"
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
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the solution as an equation (e.g. `"Eq(f(x), C1*exp(x))"`), or a list of equations when there are several branches; `key` — session key the solution is stored under; `latex` — the solution in LaTeX. With `output_format="legacy"`: the LaTeX string only.

**Example:**
```
dsolve_ode(session_id="s1", expr_key="expr_0", func_name="f")
→ {"key": "expr_1", "result": "Eq(f(x), C1*exp(x))", "latex": "f{\\left(x \\right)} = C_{1} e^{x}"}
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
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the list of solution equations, one per function; `key` — session key the list is stored under; `latex` — the list in LaTeX. With `output_format="legacy"`: comma-separated LaTeX solutions only.

**Example:**
```
dsolve_system(session_id="s1", expr_keys=["expr_0", "expr_1"], func_names=["h1", "h2"])
→ {"key": "expr_2", "result": "[Eq(h1(t), C1*sin(t) + C2*cos(t)), Eq(h2(t), C1*cos(t) - C2*sin(t))]", "latex": "..."}
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
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the solution as an equation; `key` — session key the solution is stored under; `latex` — the solution in LaTeX. With `output_format="legacy"`: the LaTeX string only.

**Example:**
```
pdsolve_pde(session_id="s1", expr_key="expr_0", func_name="u")
→ {"key": "expr_1", "result": "Eq(u(x, y), F(x - y))", "latex": "u{\\left(x,y \\right)} = F{\\left(x - y \\right)}"}
```
