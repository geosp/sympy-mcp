# Calculus Tools

Use the same `session_id` across all calls to share state. Symbols must be introduced with `/symbols/intro` before they can appear in expression strings. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `expr_key` in subsequent calls).

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

---

## simplify_expression
Simplifies a symbolic expression using SymPy's `simplify` function.

**When to use:**
- To reduce a complex expression to its simplest form
- After algebraic manipulations that may have introduced redundant terms
- When the result of a computation looks more complex than expected

**When NOT to use:**
- When you need a specific transformation (factoring, expanding, collecting) — use the dedicated tool instead
- On expressions that are already in their simplest or desired form

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
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

**When to use:**
- For computing antiderivatives (indefinite integrals)
- For computing definite integrals over a specific interval (e.g., work, area, probability)
- When a problem involves ∫ notation or asks for "the integral of"

**When NOT to use:**
- For summations (discrete sums) — use `summation_expression`
- When you need a numerical-only answer for a difficult integral — try symbolically first, then `evalf_expression` on the result

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression to integrate.
- `var_name` (str): Variable to integrate with respect to (must be introduced in the session).
- `lower_bound` (str, optional): Lower bound for definite integration (e.g., `"0"`, `"pi"`).
- `upper_bound` (str, optional): Upper bound for definite integration (e.g., `"1"`, `"oo"`).

**Returns:** `result` — the integral as a string; `result_key` — session key for chaining.

**Notes:**
- If both `lower_bound` and `upper_bound` are provided, performs definite integration.
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
{"session_id": "s1", "expr_key": "expr_0", "var_name": "x", "lower_bound": "0", "upper_bound": "1"}
→ {"success": true, "result": "1/3", "result_key": "expr_1"}
```

---

## differentiate_expression
Differentiates an expression with respect to a variable, optionally to a specified order.

**When to use:**
- For computing derivatives, partial derivatives, or higher-order derivatives
- When a problem involves rates of change, slopes, or d/dx notation

**When NOT to use:**
- For solving ODEs — use `dsolve_ode` after setting up the equation
- For gradient/curl/divergence of vector fields — use the vector calculus tools

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
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

---

## limit_expression

Compute the limit of an expression as a variable approaches a point.

**When to use:**
- For evaluating limits (L'Hôpital's rule situations, indeterminate forms)
- When a function is undefined at a point but has a well-defined limit
- For one-sided limits (left-hand or right-hand)

**When NOT to use:**
- When simple substitution works — use `substitute_expression` or `evalf_expression`
- For limits at infinity that are obvious from the expression's structure

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression.
- `var_name` (str): Variable approaching the limit point (must be introduced in the session).
- `point` (str): The limit point as a SymPy expression string (e.g. `"0"`, `"oo"`, `"pi/2"`).
- `direction` (str, optional): `"+"` for right-hand limit, `"-"` for left-hand limit. Default: `"+"`.

**Returns:** `result` — the limit value; `result_key` — session key for chaining.

**Example:**
```json
POST /calculus/limit
{"session_id": "s1", "expr_key": "expr_0", "var_name": "x", "point": "0"}
→ {"success": true, "result": "1", "result_key": "expr_1"}
```
(For `sin(x)/x` as `x → 0`)

---

## series_expansion

Compute the Taylor/Maclaurin series expansion of an expression around a point.

**When to use:**
- For Taylor or Maclaurin series approximations
- When linearizing or approximating a function near a specific point
- For power series representations of transcendental functions

**When NOT to use:**
- When only the first derivative at a point is needed — use `differentiate_expression`
- When you need the exact closed-form expression, not an approximation

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression.
- `var_name` (str): Variable to expand in (must be introduced in the session).
- `point` (str, optional): Expansion point. Default: `"0"` (Maclaurin series).
- `order` (int, optional): Number of terms (truncation order). Default: `6`.

**Returns:**
- `result` — the full series including the big-O remainder term (e.g. `"x - x**3/6 + O(x**5)"`) — useful for display
- `result_key` — session key storing the polynomial without the big-O term, for use in further calculations

**Example:**
```json
POST /calculus/series
{"session_id": "s1", "expr_key": "expr_0", "var_name": "x", "point": "0", "order": 5}
→ {"success": true, "result": "x - x**3/6 + O(x**5)", "result_key": "expr_1"}
```

---

## summation_expression

Compute a symbolic or numerical summation over a variable range.

**When to use:**
- For finite or infinite series (∑ notation)
- When computing closed-form sums (e.g., arithmetic/geometric series, telescoping sums)
- For convergence of infinite series

**When NOT to use:**
- For continuous integration — use `integrate_expression`
- When the sum is trivially computed (e.g., sum of 3 explicit numbers)

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the summand expression.
- `var_name` (str): Summation variable (must be introduced in the session).
- `lower_bound` (str): Lower bound as a SymPy expression string (e.g. `"1"`, `"0"`).
- `upper_bound` (str): Upper bound as a SymPy expression string (e.g. `"n"`, `"oo"`, `"10"`).

**Returns:** `result` — the closed-form sum; `result_key` — session key for chaining.

**Notes:**
- Use `"oo"` for infinite upper bound (convergent series only).
- If `upper_bound` is a symbolic variable (e.g. `"n"`), introduce it as a symbol first.

**Example:**
```json
POST /calculus/summation
{"session_id": "s1", "expr_key": "expr_0", "var_name": "k", "lower_bound": "1", "upper_bound": "n"}
→ {"success": true, "result": "n*(n + 1)/2", "result_key": "expr_1"}
```
