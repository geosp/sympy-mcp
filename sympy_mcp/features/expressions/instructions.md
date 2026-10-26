# Expression Tools

Use the same `session_id` across all calls to share state. Symbols must be introduced with `/symbols/intro` before they can appear in expression strings. See `POST /session/reset` docs for the full session management guide.

Expression strings can refer to stored results with `@key` — for example `"@expr_7 - @expr_9"` or `"diff(@expr_3, x)"` — instead of retyping them. The referenced value is used exactly as stored. An unknown key is an error. `@` directly after an operand (`A@B`) keeps its meaning of matrix multiplication; use `*` to multiply by a reference (`2*@expr_1`).

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `expr_key` in subsequent calls).

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

**Returns:** `result` — the expression as a string; `result_key` — session key (e.g. `"expr_0"`) to pass as `expr_key` in subsequent calls.

**Example:**
```json
POST /expressions/introduce
{"session_id": "s1", "expression": "x**2 + 2*x + 1"}
→ {"success": true, "result": "x**2 + 2*x + 1", "result_key": "expr_0"}
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

**Returns:** `result` — the equation as a string (e.g. `"Eq(x**2, 1)"`); `result_key` — session key for use in solve tools.

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
- `expr_key` (str): Session key from a previous call's `result_key` field.

**Returns:** `result` — LaTeX string (e.g. `"x^{2} + 2 x + 1"`). No `result_key` — LaTeX output is not stored in the session.

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
- `replacement_expr_key` (str): Session key of the expression to substitute in (a `result_key` from a previous call), or an expression string such as `"3"` or `"@expr_1 + 1"`. A bare name that is neither a stored key nor an introduced symbol is reported as not found.

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

**Returns:** `result` — numerical value as a string (e.g. `"3.14159265358979"`); `result_key` — session key for the numerical result (can be chained further).

**Example:**
```json
POST /expressions/evalf
{"session_id": "s1", "expr_key": "expr_0", "n": 10}
→ {"success": true, "result": "3.141592654", "result_key": "expr_1"}
```
