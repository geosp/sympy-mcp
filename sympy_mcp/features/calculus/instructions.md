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

---

## fourier_transform
Compute the Fourier transform with SymPy's convention `F(k) = ∫ f(x) e^{-2πi x k} dx` (unitary, ordinary frequency).

**When to use:**
- To transform a function of `x` into frequency space `k`
- To check a transform pair, together with `check_equivalence`

**When NOT to use:**
- When your source uses another convention (e.g. `e^{-i k x}` with angular frequency): rescale `k → k/(2π)` and the prefactor yourself, or substitute afterwards with `substitute_values`
- For one-sided transforms of causal signals — use `laplace_transform`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of `f(x)`.
- `var_name` (str): The variable `x` (an introduced symbol).
- `k_name` (str): The frequency variable `k` (an introduced symbol).
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key`, `result`, `latex` of `F(k)`. If SymPy cannot evaluate the transform, the result is an unevaluated `FourierTransform(...)` and a `note` says so.

**Example:**
```
fourier_transform(session_id="s1", expr_key="expr_0", var_name="x", k_name="k")   # expr_0 = exp(-x**2)
→ {"key": "expr_1", "result": "sqrt(pi)*exp(-pi**2*k**2)", "latex": "\\sqrt{\\pi} e^{- \\pi^{2} k^{2}}"}
```

---

## inverse_fourier_transform
Compute the inverse Fourier transform `f(x) = ∫ F(k) e^{2πi x k} dk` (SymPy's convention, matching `fourier_transform`).

**When to use:**
- To go back from frequency space to `x`
- To check that a transform round-trips

**When NOT to use:**
- For inverse Laplace transforms — use `inverse_laplace_transform`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of `F(k)`.
- `k_name` (str): The frequency variable `k`.
- `var_name` (str): The variable `x` of the result.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key`, `result`, `latex` of `f(x)`, with a `note` if SymPy could not evaluate it.

**Example:**
```
inverse_fourier_transform(session_id="s1", expr_key="expr_1", k_name="k", var_name="x")
→ {"key": "expr_2", "result": "exp(-x**2)", "latex": "e^{- x^{2}}"}
```

---

## laplace_transform
Compute the Laplace transform `F(s) = ∫_0^∞ f(t) e^{-st} dt`.

**When to use:**
- To solve linear ODEs with initial conditions by transform methods
- To find transfer functions or the transform of a causal signal

**When NOT to use:**
- For two-sided transforms over the whole real line — use `fourier_transform`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of `f(t)`.
- `t_name` (str): The time variable `t`.
- `s_name` (str): The transform variable `s`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key`, `result`, `latex` of `F(s)`; `convergence_abscissa` — the transform converges for `Re(s)` greater than this; `conditions` — any extra conditions SymPy reports. If SymPy cannot evaluate the transform, the result is unevaluated and a `note` says so.

**Example:**
```
laplace_transform(session_id="s1", expr_key="expr_0", t_name="t", s_name="s")   # expr_0 = exp(-a*t), a > 0
→ {"key": "expr_1", "result": "1/(a + s)", "latex": "\\frac{1}{a + s}", "convergence_abscissa": "-a", "conditions": "True"}
```

---

## inverse_laplace_transform
Compute the inverse Laplace transform. The result is multiplied by `Heaviside(t)`, since it is defined for `t ≥ 0`.

**When to use:**
- To go back to the time domain after solving in `s`

**When NOT to use:**
- For inverse Fourier transforms — use `inverse_fourier_transform`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of `F(s)`.
- `s_name` (str): The transform variable `s`.
- `t_name` (str): The time variable `t` of the result.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key`, `result`, `latex` of `f(t)`, with a `note` if SymPy could not evaluate it.

**Example:**
```
inverse_laplace_transform(session_id="s1", expr_key="expr_0", s_name="s", t_name="t")   # expr_0 = 1/(s + 1)
→ {"key": "expr_1", "result": "exp(-t)*Heaviside(t)", "latex": "e^{- t} \\theta\\left(t\\right)"}
```

---

## numeric_integrate
Evaluate a definite integral numerically with mpmath quadrature (tanh-sinh / Gauss-Legendre) at a chosen precision. Infinite limits are supported.

**When to use:**
- When `integrate_expression` cannot find a closed form, or is too slow
- To check a symbolic result numerically, to many digits
- For integrals over infinite ranges such as `(-oo, oo)`

**When NOT to use:**
- When you need an exact symbolic answer — use `integrate_expression`
- When the integrand has free parameters — substitute numbers for them first (`substitute_values`); the tool reports any symbols other than the integration variable

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the integrand.
- `var_name` (str): The integration variable.
- `lower_bound` (str): Lower limit, e.g. `"0"`, `"-oo"`, `"pi/2"`, `"@expr_3"`.
- `upper_bound` (str): Upper limit, e.g. `"1"`, `"oo"`.
- `precision` (int, optional): Number of significant digits, 1–1000. Default: `15`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key`, `result`, `latex` of the numeric value (a Float with `precision` digits); `precision`; `error_estimate` — mpmath's estimate of the quadrature error.

**Example:**
```
numeric_integrate(session_id="s1", expr_key="expr_0", var_name="x", lower_bound="-oo", upper_bound="oo", precision=30)   # expr_0 = exp(-x**2)
→ {"key": "expr_1", "result": "1.77245385090551602729816748334", "latex": "...", "precision": 30, "error_estimate": "1.0e-37"}
```
