# Solving Tools

Use the same `session_id` across all calls to share state. Symbols must be introduced with `intro` and expressions with `introduce_expression` before solving. See the session tools (`create_session`, `list_session_state`) for session management.

Computing tools return JSON by default: `{"key": ..., "result": ..., "latex": ...}`. `key` is the session key the result is stored under (pass it to later calls, or reference it as `@key` in an expression string), `result` is the value as a SymPy string, and `latex` is its LaTeX form. Some tools add extra fields, listed under Returns. Failures return `{"error": "..."}`. Pass `output_format="legacy"` to get the plain string these tools returned before (usually just the key).

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

---

## solve_algebraically
Solve a single equation or expression for one variable.

**When to use:**
- For solving a single equation for one unknown (e.g., `x² - 1 = 0`)
- When the expression is implicitly equal to zero and you want to find roots
- When the problem says "solve for x" with one equation

**When NOT to use:**
- For systems of equations (2+ equations) — use `solve_linear_system` or `solve_nonlinear_system`
- For differential equations — use `dsolve_ode` or `pdsolve_pde`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the stored expression or equation (the `key` returned by a previous call).
- `var_name` (str): Name of the variable to solve for.
- `domain` (str, optional): Solution domain — `"complex"` (default), `"real"`, `"integer"`, `"natural"`.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the solution set (a SymPy set such as `"{-1, 1}"`, or `ImageSet`/`ConditionSet` for non-finite solutions); `key` — session key the set is stored under; `latex` — the set in LaTeX. With `output_format="legacy"`: the LaTeX string only.

**Example:**
```
solve_algebraically(session_id="s1", expr_key="expr_0", var_name="x", domain="real")
→ {"key": "expr_1", "result": "{-1, 1}", "latex": "\\left\\{-1, 1\\right\\}"}
```

---

## solve_linear_system
Solve a system of linear equations.

**When to use:**
- For systems where all equations are linear in the unknowns (e.g., `2x + 3y = 5`, `x - y = 1`)
- When you know the system is linear — this solver is optimized for such cases

**When NOT to use:**
- For a single equation — use `solve_algebraically`
- When any equation is nonlinear (contains `x²`, `xy`, `sin(x)`, etc.) — use `solve_nonlinear_system`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_keys` (list of str): List of session keys for the equations/expressions to solve (each the `key` returned by a previous call).
- `var_names` (list of str): List of variable names to solve for.
- `domain` (str, optional): Solution domain — `"complex"` (default), `"real"`, `"integer"`, `"natural"`.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the solution set of tuples, in the order of `var_names` (e.g. `"{(1, 2)}"`); `key` — session key the set is stored under; `latex` — the set in LaTeX. With `output_format="legacy"`: the LaTeX string only.

**Example:**
```
solve_linear_system(session_id="s1", expr_keys=["expr_0", "expr_1"], var_names=["x", "y"])
→ {"key": "expr_2", "result": "{(1, 2)}", "latex": "\\left\\{\\left( 1, \\  2\\right)\\right\\}"}
```

---

## solve_nonlinear_system
Solve a system of nonlinear equations symbolically.

**When to use:**
- For systems with nonlinear terms (`x²`, `xy`, `sin(x)`, etc.)
- When `solve_linear_system` is not applicable because the equations are not all linear

**When NOT to use:**
- For purely linear systems — use `solve_linear_system` (more efficient)
- For a single equation — use `solve_algebraically`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_keys` (list of str): List of session keys for the equations/expressions to solve.
- `var_names` (list of str): List of variable names to solve for.
- `domain` (str, optional): Solution domain — `"complex"` (default), `"real"`, `"integer"`, `"natural"`.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the solution set of tuples, in the order of `var_names`; `key` — session key the set is stored under; `latex` — the set in LaTeX. With `output_format="legacy"`: the LaTeX string only.

**Example:**
```
solve_nonlinear_system(session_id="s1", expr_keys=["expr_0", "expr_1"], var_names=["x", "y"])
→ {"key": "expr_2", "result": "{(-1, 0), (1, 0)}", "latex": "\\left\\{\\left( -1, \\  0\\right), \\left( 1, \\  0\\right)\\right\\}"}
```
