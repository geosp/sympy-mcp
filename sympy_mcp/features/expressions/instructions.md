# Expression Tools

Use the same `session_id` across all calls to share state. Symbols must be introduced with `/symbols/intro` before they can appear in expression strings. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `expr_key` in subsequent calls).

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

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

---

## factor_expression

Factor an expression into irreducible components over the rationals.

**Parameters:**
- `session_id` (str): Session identifier.
- `expr_key` (str): Session key of the expression to factor.

**Returns:** `result` — the factored expression (e.g. `"(x - 1)*(x + 1)"`); `result_key` — session key for the factored form.

**Example:**
```json
POST /expressions/factor
{"session_id": "s1", "expr_key": "expr_0"}
→ {"success": true, "result": "(x - 1)*(x + 1)", "result_key": "expr_1"}
```

---

## expand_expression

Expand a product or power into a sum of terms.

**Parameters:**
- `session_id` (str): Session identifier.
- `expr_key` (str): Session key of the expression to expand.

**Returns:** `result` — the expanded expression (e.g. `"x**2 + 2*x + 1"`); `result_key` — session key.

**Example:**
```json
POST /expressions/expand
{"session_id": "s1", "expr_key": "expr_0"}
→ {"success": true, "result": "x**2 + 2*x + 1", "result_key": "expr_1"}
```

---

## collect_expression

Collect and group terms by powers of a variable.

**Parameters:**
- `session_id` (str): Session identifier.
- `expr_key` (str): Session key of the expression to collect.
- `var_name` (str): Variable name to collect by.

**Returns:** `result` — the collected expression (e.g. `"x*(y + z + x)"`); `result_key` — session key.

**Example:**
```json
POST /expressions/collect
{"session_id": "s1", "expr_key": "expr_0", "var_name": "x"}
→ {"success": true, "result": "x**2 + x*(y + z)", "result_key": "expr_1"}
```

---

## apart_expression

Decompose a rational expression into partial fractions.

**Parameters:**
- `session_id` (str): Session identifier.
- `expr_key` (str): Session key of the rational expression.
- `var_name` (str): Variable to decompose with respect to.

**Returns:** `result` — partial fraction decomposition; `result_key` — session key.

**Example:**
```json
POST /expressions/apart
{"session_id": "s1", "expr_key": "expr_0", "var_name": "x"}
→ {"success": true, "result": "1/(2*(x - 1)) - 1/(2*(x + 1))", "result_key": "expr_1"}
```

---

## evalf_expression

Numerically evaluate an expression to a specified number of significant digits.

**Parameters:**
- `session_id` (str): Session identifier.
- `expr_key` (str): Session key of the expression to evaluate.
- `n` (int, optional): Number of significant digits. Default: `15`.

**Returns:** `result` — numerical value as a string (e.g. `"3.14159265358979"`); `result_key` — session key for the numerical result (can be chained further).

**Example:**
```json
POST /expressions/evalf
{"session_id": "s1", "expr_key": "expr_0", "n": 10}
→ {"success": true, "result": "3.141592654", "result_key": "expr_1"}
```
