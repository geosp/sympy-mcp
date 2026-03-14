# Expression Tools

Use the same `session_id` across all calls to share state. Symbols must be introduced with `/symbols/intro` before they can appear in expression strings. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `expr_key` in subsequent calls).

---

## introduce_expression
Parse and store a mathematical expression string.

**Parameters:**
- `session_id` (str): Session identifier. Pass any string — sessions are auto-created on first use.
- `expr_str` (str): Expression string using SymPy syntax (e.g., `"x**2 + 2*x + 1"`, `"sin(x)*cos(y)"`)
- `canonicalize` (bool): If True, simplify/expand the expression. Default: `true`
- `name` (str, optional): Custom key name (default: auto-generated `"expr_N"`)

**Returns:** `result` — the expression as a string; `result_key` — session key (e.g. `"expr_0"`) to pass as `expr_key` in subsequent calls.

**Example:**
```json
POST /expressions/introduce
{"session_id": "s1", "expr_str": "x**2 + 2*x + 1"}
→ {"success": true, "result": "x**2 + 2*x + 1", "result_key": "expr_0"}
```

---

## introduce_equation
Parse and store an equation lhs = rhs.

**Parameters:**
- `session_id` (str): Session identifier.
- `lhs_str` (str): Left-hand side expression string
- `rhs_str` (str): Right-hand side expression string

**Returns:** `result` — the equation as a string (e.g. `"Eq(x**2, 1)"`); `result_key` — session key for use in solve tools.

---

## print_latex_expression
Render a stored expression as LaTeX.

**Parameters:**
- `session_id` (str): Session identifier.
- `expr_key` (str): Session key from a previous call's `result_key` field.

**Returns:** `result` — LaTeX string (e.g. `"x^{2} + 2 x + 1"`). No `result_key` — LaTeX output is not stored in the session.

---

## substitute_expression
Substitute a variable with another stored expression.

**Parameters:**
- `session_id` (str): Session identifier.
- `expr_key` (str): Session key of the expression to substitute into
- `var_name` (str): Name of the variable to replace
- `replacement_expr_key` (str): Session key of the expression to substitute in (a `result_key` from a previous call)

**Returns:** `result` — the substituted expression as a string; `result_key` — session key for the new expression.

**Example:**
```json
POST /expressions/substitute
{"session_id": "s1", "expr_key": "expr_0", "var_name": "x", "replacement_expr_key": "expr_1"}
→ {"success": true, "result": "4 + 2*y + y**2", "result_key": "expr_2"}
```
