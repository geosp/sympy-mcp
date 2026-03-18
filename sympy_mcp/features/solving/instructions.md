# Solving Tools

Use the same `session_id` across all calls to share state. Symbols must be introduced with `/symbols/intro` and expressions with `/expressions/introduce` before solving. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `expr_key` in subsequent calls).

---

## solve_algebraically
Solve a single equation or expression for one variable.

**Parameters:**
- `session_id` (str): Session identifier. Pass any string — sessions are auto-created on first use.
- `expr_key` (str): Session key of the stored expression or equation (a `result_key` from a previous call).
- `solve_for_var_name` (str): Name of the variable to solve for.
- `domain` (str, optional): Solution domain — `"complex"` (default), `"real"`, `"integer"`, `"natural"`.

**Returns:** `result` — solution set as a string (e.g. `"[-1, 1]"`); `result_key` — session key for chaining.

**Example:**
```json
POST /solving/algebraic
{"session_id": "s1", "expr_key": "expr_0", "solve_for_var_name": "x", "domain": "real"}
→ {"success": true, "result": "[-1, 1]", "result_key": "expr_1"}
```

---

## solve_linear_system
Solve a system of linear equations.

**Parameters:**
- `session_id` (str): Session identifier.
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

**Parameters:**
- `session_id` (str): Session identifier.
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
