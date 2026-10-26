# Verification Tools

Use the same `session_id` across all calls to share state. Operands can be stored keys (e.g. `"expr_7"`) or expression strings, and expression strings can refer to stored results with `@key` (e.g. `"2*@expr_3"`).

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

---

## check_equivalence
Decide whether two expressions are equal: first by trying to prove `a - b = 0` symbolically, then by evaluating both at random points that respect each symbol's assumptions.

The symbolic stage tries `simplify(a - b)`, then each of `rewrite(exp)`, `expand_log(force=True)`, `trigsimp`, `expand` and `together` followed by `simplify`. `expand_log(force=True)` ignores branch cuts, so a proof that needs it is always checked numerically too, and a numeric counterexample overrides it.

Sample points are exact random values chosen to satisfy each symbol's assumptions: a `positive` symbol gets positive values, an `integer` symbol gets integers, and a symbol with no assumptions gets complex values. Points where either side is singular are skipped. The sample sequence is fixed, so the same check always gives the same answer.

**When to use:**
- To confirm that a derived result matches an expected closed form
- To check that two stored results (e.g. from different derivation routes) agree
- Before reporting that an identity holds

**When NOT to use:**
- To compare equations — compare `lhs - rhs` of each instead
- When you need the simplified form itself — use `simplify_expression`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_a` (str): A stored key or an expression string. Matrices are compared element by element.
- `expr_b` (str): A stored key or an expression string.
- `numeric_samples` (int, optional): Number of non-singular sample points to check when no symbolic proof is found. Default: `20`. `0` skips the numeric stage.

**Returns:** JSON with a `verdict`:
- `proved_equal` — with `method`, the transformation that reduced the difference to 0. If that was `expand_log(force=True)`, a `caveat` is included as well.
- `numerically_equal` — no symbolic proof, but equal within a relative tolerance of 1e-10 (at 30 significant digits) at every sample point. Includes `samples`, `max_error` and `max_relative_error`.
- `not_equal` — with a `counterexample` (symbol → value) and `value_a` / `value_b` at that point, or a `reason` (e.g. different matrix shapes).
- `inconclusive` — with a `reason`, e.g. the expressions contain undefined functions, so they can't be evaluated numerically.

**Example:**
```
check_equivalence(session_id="s1", expr_a="tanh(x)", expr_b="(exp(2*x) - 1)/(exp(2*x) + 1)")
→ {"verdict": "proved_equal", "method": "rewrite(exp)"}

check_equivalence(session_id="s1", expr_a="atan(x) + atan(1/x)", expr_b="pi/2")   # x positive
→ {"verdict": "numerically_equal", "samples": 20, "max_error": "...", "max_relative_error": "...", "note": "..."}

check_equivalence(session_id="s1", expr_a="sqrt(x**2)", expr_b="x")               # x real
→ {"verdict": "not_equal", "counterexample": {"x": "-1.234"}, "value_a": "1.234...", "value_b": "-1.234..."}
```
