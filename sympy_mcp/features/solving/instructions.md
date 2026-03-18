# Solving Tools

Use the same `session_id` across all calls to share state. Symbols must be introduced with `/symbols/intro` and expressions with `/expressions/introduce` before solving. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `expr_key` in subsequent calls).

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
- `expr_key` (str): Session key of the stored expression or equation (a `result_key` from a previous call).
- `var_name` (str): Name of the variable to solve for.
- `domain` (str, optional): Solution domain — `"complex"` (default), `"real"`, `"integer"`, `"natural"`.

**Returns:** `result` — solution set as a string (e.g. `"[-1, 1]"`); `result_key` — session key for chaining.

**Example:**
```json
POST /solving/algebraic
{"session_id": "s1", "expr_key": "expr_0", "var_name": "x", "domain": "real"}
→ {"success": true, "result": "[-1, 1]", "result_key": "expr_1"}
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
- `expr_keys` (list of str): List of session keys for the equations/expressions to solve (each a `result_key` from a previous call).
- `var_names` (list of str): List of variable names to solve for.
- `domain` (str, optional): Solution domain — `"complex"` (default), `"real"`, `"integer"`, `"natural"`.

**Returns:** `result` — solution as a string (e.g. `"{x: 1, y: 2}"`); `result_key` — session key for chaining.

**Example:**
```json
POST /solving/linear_system
{"session_id": "s1", "expr_keys": ["expr_0", "expr_1"], "var_names": ["x", "y"]}
→ {"success": true, "result": "{x: 1, y: 2}", "result_key": "expr_2"}
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

**Returns:** `result` — solution set as a string; `result_key` — session key for chaining.

**Example:**
```json
POST /solving/nonlinear_system
{"session_id": "s1", "expr_keys": ["expr_0", "expr_1"], "var_names": ["x", "y"]}
→ {"success": true, "result": "[(-1, 0), (1, 0)]", "result_key": "expr_2"}
```
