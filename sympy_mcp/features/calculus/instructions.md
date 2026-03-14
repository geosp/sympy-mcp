# Calculus Tools

Use the same `session_id` across all calls to share state. Symbols must be introduced with `/symbols/intro` before they can appear in expression strings. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `expr_key` in subsequent calls).

---

## simplify_expression
Simplifies a symbolic expression using SymPy's `simplify` function.

**Parameters:**
- `session_id` (str): Session identifier. Pass any string — sessions are auto-created on first use.
- `expr_key` (str): Session key from a previous call's `result_key` field.

**Returns:** `result` — the simplified expression as a string; `result_key` — session key for chaining.

**Example:**
```json
POST /calculus/simplify
{"session_id": "s1", "expr_key": "expr_0"}
→ {"success": true, "result": "x**2 + 2*x + 1", "result_key": "expr_1"}
```

---

## integrate_expression
Integrates an expression with respect to a variable. Supports indefinite and definite integration.

**Parameters:**
- `session_id` (str): Session identifier.
- `expr_key` (str): Session key of the expression to integrate.
- `var_name` (str): Variable to integrate with respect to (must be introduced in the session).
- `lower` (str, optional): Lower bound for definite integration (e.g., `"0"`, `"pi"`).
- `upper` (str, optional): Upper bound for definite integration (e.g., `"1"`, `"oo"`).

**Returns:** `result` — the integral as a string; `result_key` — session key for chaining.

**Notes:**
- If both `lower` and `upper` are provided, performs definite integration.
- If neither is provided, performs indefinite integration (constant of integration is implicit).
- Bounds are parsed as SymPy expressions: use `"pi"`, `"oo"` (infinity), etc.

**Example (indefinite):**
```json
POST /calculus/integrate
{"session_id": "s1", "expr_key": "expr_0", "var_name": "x"}
→ {"success": true, "result": "x**3/3", "result_key": "expr_1"}
```

**Example (definite):**
```json
POST /calculus/integrate
{"session_id": "s1", "expr_key": "expr_0", "var_name": "x", "lower": "0", "upper": "1"}
→ {"success": true, "result": "1/3", "result_key": "expr_1"}
```

---

## differentiate_expression
Differentiates an expression with respect to a variable, optionally to a specified order.

**Parameters:**
- `session_id` (str): Session identifier.
- `expr_key` (str): Session key of the expression to differentiate.
- `var_name` (str): Variable to differentiate with respect to (must be introduced in the session).
- `order` (int, optional): Order of differentiation. Default: `1`.

**Returns:** `result` — the derivative as a string; `result_key` — session key for chaining.

**Example:**
```json
POST /calculus/differentiate
{"session_id": "s1", "expr_key": "expr_0", "var_name": "x", "order": 2}
→ {"success": true, "result": "2", "result_key": "expr_1"}
```
