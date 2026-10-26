# Calculus Tools

Use the same `session_id` across all calls to share state. Symbols must be introduced with `intro` before they can appear in expression strings. See the session tools (`create_session`, `list_session_state`) for session management.

Expression strings can refer to stored results with `@key` — for example `"@expr_7 - @expr_9"` or `"diff(@expr_3, x)"` — instead of retyping them. The referenced value is used exactly as stored. An unknown key is an error. `@` directly after an operand (`A@B`) keeps its meaning of matrix multiplication; use `*` to multiply by a reference (`2*@expr_1`).

Computing tools return JSON by default: `{"key": ..., "result": ..., "latex": ...}`. `key` is the session key the result is stored under (pass it to later calls, or reference it as `@key` in an expression string), `result` is the value as a SymPy string, and `latex` is its LaTeX form. Some tools add extra fields, listed under Returns. Failures return `{"error": "..."}`. Pass `output_format="legacy"` to get the plain string these tools returned before (usually just the key).

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
- `expr_key` (str): Session key from a previous call's `key` field.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the simplified expression as a string; `key` — session key for chaining; `latex` — the result in LaTeX.

**Example:**
```
simplify_expression(session_id="s1", expr_key="expr_0")
→ {"key": "expr_1", "result": "x**2 + 2*x + 1", "latex": "x^{2} + 2 x + 1"}
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
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the integral as a string; `key` — session key for chaining; `latex` — the result in LaTeX.

**Notes:**
- If both `lower_bound` and `upper_bound` are provided, performs definite integration.
- If neither is provided, performs indefinite integration (constant of integration is implicit).
- Bounds are parsed as SymPy expressions: use `"pi"`, `"oo"` (infinity), etc.

**Example (indefinite):**
```
integrate_expression(session_id="s1", expr_key="expr_0", var_name="x")
→ {"key": "expr_1", "result": "x**3/3", "latex": "\\frac{x^{3}}{3}"}
```

**Example (definite):**
```
integrate_expression(session_id="s1", expr_key="expr_0", var_name="x", lower_bound="0", upper_bound="1")
→ {"key": "expr_1", "result": "1/3", "latex": "\\frac{1}{3}"}
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
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the derivative as a string; `key` — session key for chaining; `latex` — the result in LaTeX.

**Example:**
```
differentiate_expression(session_id="s1", expr_key="expr_0", var_name="x", order=2)
→ {"key": "expr_1", "result": "2", "latex": "2"}
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
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the limit value; `key` — session key for chaining; `latex` — the result in LaTeX.

**Example:**
```
limit_expression(session_id="s1", expr_key="expr_0", var_name="x", point="0")
→ {"key": "expr_1", "result": "1", "latex": "1"}
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
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON with
- `key` — session key storing the polynomial **without** the big-O term, for use in further calculations
- `result` / `latex` — that stored polynomial (e.g. `"-x**3/6 + x"`)
- `series` / `series_latex` — the full series **including** the big-O remainder (e.g. `"x - x**3/6 + O(x**5)"`), for display

With `output_format="legacy"`: `"<full series> [stored as <key>]"`.

**Example:**
```
series_expansion(session_id="s1", expr_key="expr_0", var_name="x", point="0", order=5)
→ {"key": "expr_1", "result": "-x**3/6 + x", "latex": "- \\frac{x^{3}}{6} + x", "series": "x - x**3/6 + O(x**5)", "series_latex": "x - \\frac{x^{3}}{6} + O\\left(x^{5}\\right)"}
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
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the closed-form sum; `key` — session key for chaining; `latex` — the result in LaTeX.

**Notes:**
- Use `"oo"` for infinite upper bound (convergent series only).
- If `upper_bound` is a symbolic variable (e.g. `"n"`), introduce it as a symbol first.

**Example:**
```
summation_expression(session_id="s1", expr_key="expr_0", var_name="k", lower_bound="1", upper_bound="n")
→ {"key": "expr_1", "result": "n*(n + 1)/2", "latex": "\\frac{n \\left(n + 1\\right)}{2}"}
```
