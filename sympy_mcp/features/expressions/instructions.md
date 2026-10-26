# Expression Tools

Use the same `session_id` across all calls to share state. Symbols must be introduced with `intro` before they can appear in expression strings. See the session tools (`create_session`, `list_session_state`) for session management.

Expression strings can refer to stored results with `@key` — for example `"@expr_7 - @expr_9"` or `"diff(@expr_3, x)"` — instead of retyping them. The referenced value is used exactly as stored. An unknown key is an error. `@` directly after an operand (`A@B`) keeps its meaning of matrix multiplication; use `*` to multiply by a reference (`2*@expr_1`).

Computing tools return JSON by default: `{"key": ..., "result": ..., "latex": ...}`. `key` is the session key the result is stored under (pass it to later calls, or reference it as `@key` in an expression string), `result` is the value as a SymPy string, and `latex` is its LaTeX form. Some tools add extra fields, listed under Returns. Failures return `{"error": "..."}`. Pass `output_format="legacy"` to get the plain string these tools returned before (usually just the key).

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

---

## introduce_expression
Parse and store a mathematical expression string.

**When to use:**
- To enter any new symbolic expression into the session (the starting point for most computations)
- When you have a formula, equation term, or symbolic quantity that needs to be stored for further manipulation

**When NOT to use:**
- For equations with `=` — use `introduce_equation` instead (lhs = rhs)
- For defining unknown functions like `f(x)` for ODEs — use `introduce_function` first

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expression` (str): Expression string using SymPy syntax (e.g., `"x**2 + 2*x + 1"`, `"sin(x)*cos(y)"`)
- `canonicalize` (bool): If True, simplify/expand the expression. Default: `true`
- `name` (str, optional): Custom key name (default: auto-generated `"expr_N"`)
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the expression as a string; `key` — session key (e.g. `"expr_0"`) to pass as `expr_key` in subsequent calls; `latex` — the result in LaTeX.

**Example:**
```
introduce_expression(session_id="s1", expression="x**2 + 2*x + 1")
→ {"key": "expr_0", "result": "x**2 + 2*x + 1", "latex": "x^{2} + 2 x + 1"}
```

---

## introduce_equation
Parse and store an equation lhs = rhs.

**When to use:**
- When the problem involves an equality (e.g., `x**2 = 1`, `y = 3*x + 2`)
- Before calling any solve tool — solvers expect equations, not plain expressions

**When NOT to use:**
- For standalone expressions without an equality — use `introduce_expression`
- When the expression is implicitly "= 0" — you can use `introduce_expression` and pass it directly to solvers

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `lhs_expression` (str): Left-hand side expression string
- `rhs_expression` (str): Right-hand side expression string
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the equation as a string (e.g. `"Eq(x**2, 1)"`); `key` — session key for use in solve tools; `latex` — the result in LaTeX.

---

## print_latex_expression
Render a stored expression as LaTeX.

**When to use:**
- Only when you need LaTeX-formatted output for final display to the user
- When the user explicitly asks for a LaTeX rendering

**When NOT to use:**
- To inspect or read expression values — use `list_session_state` instead
- To verify intermediate computation results — use `list_session_state`
- As a routine step after every computation — it wastes a tool call

**Do NOT use this tool just to inspect or read expression values.** Use `list_session_state` instead — it shows all stored expressions and their values in a single call. Reserve `print_latex_expression` only when you specifically need LaTeX-formatted output for final display to the user.

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key from a previous call's `key` field.
- `include_assumptions` (bool, optional): Append a note listing the assumptions on each symbol, e.g. `"(where x is commutative, complex, ...)"`. Default: `true`. Set to `false` for clean LaTeX you can paste into a document.

**Returns:** The LaTeX string as plain text. With `include_assumptions=true`, a `(where ...)` note about the symbols' assumptions follows it. It is not stored in the session.

**Example:**
```
print_latex_expression(session_id="s1", expr_key="expr_0")
→ "x^{2} + 2 x + 1 (where x is commutative, complex, finite, ...)"

print_latex_expression(session_id="s1", expr_key="expr_0", include_assumptions=false)
→ "x^{2} + 2 x + 1"
```

---

## substitute_expression
Substitute a variable with another stored expression, or with an expression string.

**When to use:**
- To plug a computed value or sub-expression into another expression
- When evaluating a general formula at specific symbolic values
- To compose results from multiple computation steps

**When NOT to use:**
- When you just want to evaluate numerically — use `evalf_expression` instead

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression to substitute into
- `var_name` (str): Name of the variable to replace
- `replacement_expr_key` (str): Session key of the expression to substitute in (the `key` returned by a previous call), or an expression string such as `"3"` or `"@expr_1 + 1"`. A bare name that is neither a stored key nor an introduced symbol is reported as not found.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the substituted expression as a string; `key` — session key for the new expression; `latex` — the result in LaTeX.

**Example:**
```
substitute_expression(session_id="s1", expr_key="expr_0", var_name="x", replacement_expr_key="expr_1")
→ {"key": "expr_2", "result": "4 + 2*y + y**2", "latex": "y^{2} + 2 y + 4"}
```

---

## factor_expression

Factor an expression into irreducible components over the rationals.

**When to use:**
- To find roots or factored form of polynomials
- When simplifying a polynomial expression by revealing its factors
- When checking if an expression has a clean factored form

**When NOT to use:**
- For non-polynomial expressions — use `simplify_expression` instead
- When you want to group terms by powers of a variable — use `collect_expression`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression to factor.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the factored expression (e.g. `"(x - 1)*(x + 1)"`); `key` — session key for the factored form; `latex` — the result in LaTeX.

**Example:**
```
factor_expression(session_id="s1", expr_key="expr_0")
→ {"key": "expr_1", "result": "(x - 1)*(x + 1)", "latex": "\\left(x - 1\\right) \\left(x + 1\\right)"}
```

---

## expand_expression

Expand a product or power into a sum of terms.

**When to use:**
- To distribute products (e.g., `(x+1)^2` → `x²+2x+1`)
- When you need a polynomial in expanded/standard form for further operations
- Before integrating or differentiating term-by-term

**When NOT to use:**
- When the factored form is more useful — expanding may lose structure
- When simplification is the goal — use `simplify_expression` instead

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression to expand.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the expanded expression (e.g. `"x**2 + 2*x + 1"`); `key` — session key; `latex` — the result in LaTeX.

**Example:**
```
expand_expression(session_id="s1", expr_key="expr_0")
→ {"key": "expr_1", "result": "x**2 + 2*x + 1", "latex": "x^{2} + 2 x + 1"}
```

---

## collect_expression

Collect and group terms by powers of a variable.

**When to use:**
- To organize a multivariate polynomial by powers of a specific variable
- When you need to see the coefficient structure with respect to a variable

**When NOT to use:**
- For single-variable polynomials that are already in standard form
- When you want full factorization — use `factor_expression`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression to collect.
- `var_name` (str): Variable name to collect by.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the collected expression (e.g. `"x*(y + z + x)"`); `key` — session key; `latex` — the result in LaTeX.

**Example:**
```
collect_expression(session_id="s1", expr_key="expr_0", var_name="x")
→ {"key": "expr_1", "result": "x**2 + x*(y + z)", "latex": "x^{2} + x \\left(y + z\\right)"}
```

---

## apart_expression

Decompose a rational expression into partial fractions.

**When to use:**
- Before integrating a rational function — partial fractions make integration straightforward
- When decomposing transfer functions or rational expressions in engineering problems

**When NOT to use:**
- For non-rational expressions (no denominator polynomial)
- When the expression is already in simple terms

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the rational expression.
- `var_name` (str): Variable to decompose with respect to.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — partial fraction decomposition; `key` — session key; `latex` — the result in LaTeX.

**Example:**
```
apart_expression(session_id="s1", expr_key="expr_0", var_name="x")
→ {"key": "expr_1", "result": "1/(2*(x - 1)) - 1/(2*(x + 1))", "latex": "- \\frac{1}{2 x + 2} + \\frac{1}{2 x - 2}"}
```

---

## evalf_expression

Numerically evaluate an expression to a specified number of significant digits.

**When to use:**
- After obtaining a symbolic result that needs a decimal approximation
- When the user asks "what does that equal numerically?"
- When verifying a symbolic result against expected numeric values
- For final numeric answers alongside the exact symbolic form

**When NOT to use:**
- When an exact symbolic answer is sufficient and no numeric value was requested
- To inspect symbolic expression structure — use `list_session_state`
- On expressions containing free variables (the result will still be symbolic)

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression to evaluate.
- `n` (int, optional): Number of significant digits. Default: `15`.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — numerical value as a string (e.g. `"3.14159265358979"`); `key` — session key for the numerical result (can be chained further); `latex` — the result in LaTeX.

**Example:**
```
evalf_expression(session_id="s1", expr_key="expr_0", n=10)
→ {"key": "expr_1", "result": "3.141592654", "latex": "3.141592654"}
```

---

## rewrite_expression
Rewrite an expression in terms of another function, e.g. trigonometric and hyperbolic functions in terms of `exp`, or `exp` in terms of `cos`.

**When to use:**
- To expose structure, e.g. `cosh(x)` → `exp(x)/2 + exp(-x)/2`
- Before `simplify_expression` or `check_equivalence` when two forms use different function families

**When NOT to use:**
- For general simplification — use `simplify_expression`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression.
- `target` (str): Name of a SymPy function to rewrite in terms of, e.g. `"exp"`, `"cos"`, `"sin"`, `"tan"`, `"log"`, `"sqrt"`, `"gamma"`, `"factorial"`, `"Piecewise"`, `"Heaviside"`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key`, `result`, `latex` of the rewritten expression. If no rewrite rule applied, a `note` says the expression is unchanged.

**Example:**
```
rewrite_expression(session_id="s1", expr_key="expr_0", target="exp")   # expr_0 = cosh(x)
→ {"key": "expr_1", "result": "exp(x)/2 + exp(-x)/2", "latex": "\\frac{e^{x}}{2} + \\frac{e^{- x}}{2}"}
```

---

## expand_log_expression
Expand logarithms: `log(x*y)` → `log(x) + log(y)`, `log(x**n)` → `n*log(x)`.

**When to use:**
- To split logarithms of products, quotients and powers

**When NOT to use:**
- To combine logarithms — use `simplify_expression`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression.
- `force` (bool, optional): Expand even when the symbols' assumptions don't guarantee it is valid. Default: `false`, which only expands what holds for the declared assumptions (e.g. positive symbols). `force=true` ignores branch cuts, so the result may be wrong for negative or complex values.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key`, `result`, `latex`; a `note` if nothing could be expanded.

**Example:**
```
expand_log_expression(session_id="s1", expr_key="expr_0", force=true)   # expr_0 = log(x*y)
→ {"key": "expr_1", "result": "log(x) + log(y)", "latex": "\\log{\\left(x \\right)} + \\log{\\left(y \\right)}"}
```

---

## trigsimp_expression
Simplify using trigonometric (and hyperbolic) identities.

**When to use:**
- For expressions built from `sin`, `cos`, `tan`, `sinh`, … that `simplify_expression` leaves in an awkward form

**When NOT to use:**
- For expressions without trigonometric functions — use `simplify_expression`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key`, `result`, `latex`; a `note` if the expression is unchanged.

**Example:**
```
trigsimp_expression(session_id="s1", expr_key="expr_0")   # expr_0 = sin(x)**4 - 2*cos(x)**2*sin(x)**2 + cos(x)**4
→ {"key": "expr_1", "result": "cos(4*x)/2 + 1/2", "latex": "..."}
```

---

## powsimp_expression
Combine powers with the same base or exponent: `x**a * x**b` → `x**(a + b)`.

**When to use:**
- To collect exponentials and powers into a single power

**When NOT to use:**
- To expand powers — use `expand_expression`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression.
- `force` (bool, optional): Combine even when assumptions don't guarantee it (e.g. `sqrt(x)*sqrt(y)` → `sqrt(x*y)` for complex `x`, `y`). Default: `false`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key`, `result`, `latex`; a `note` if the expression is unchanged.

**Example:**
```
powsimp_expression(session_id="s1", expr_key="expr_0")   # expr_0 = x**a * x**2
→ {"key": "expr_1", "result": "x**(a + 2)", "latex": "x^{a + 2}"}
```

---

## nsimplify_expression
Find a simple exact expression that matches a floating-point number, e.g. `0.3333333333` → `1/3`, `1.41421356` → `sqrt(2)`.

**When to use:**
- To recognise a numeric result as a closed form
- With `constants`, to look for combinations of `pi`, `E`, `sqrt(2)`, …

**When NOT to use:**
- As proof: the match is only as good as the precision of the input. Confirm with `check_equivalence` if it matters.

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the numeric expression.
- `constants` (list of str, optional): Constants the closed form may contain, e.g. `["pi", "E"]`.
- `tolerance` (float, optional): Maximum allowed difference. Default: based on the number's precision.
- `rational` (bool, optional): Only look for a rational number. Default: `false`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key`, `result`, `latex` of the exact expression found (or the input, if none).

**Example:**
```
nsimplify_expression(session_id="s1", expr_key="expr_0", constants=["pi"])   # expr_0 = 3.14159265358979
→ {"key": "expr_1", "result": "pi", "latex": "\\pi"}
```

---

## substitute_values
Substitute several symbols at once, with numbers or expressions, without storing each value first. The substitution is simultaneous, so `{"x": "y", "y": "x"}` swaps `x` and `y`.

**When to use:**
- To evaluate a formula at given parameter values
- To plug in several results at once with `@key` references

**When NOT to use:**
- For a single substitution of a stored expression — `substitute_expression` also works

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression.
- `substitutions` (dict[str, str]): Map from what to replace (a symbol name, or an expression such as `"f(x)"`) to its replacement (an expression string, which may use `@key` references). Example: `{"x": "3", "y": "1/2", "m": "@expr_4"}`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"`.

**Returns:** JSON — `key`, `result`, `latex` of the substituted expression.

**Example:**
```
substitute_values(session_id="s1", expr_key="expr_0", substitutions={"x": "3", "y": "1/2"})   # expr_0 = x**2 + y
→ {"key": "expr_1", "result": "19/2", "latex": "\\frac{19}{2}"}
```
