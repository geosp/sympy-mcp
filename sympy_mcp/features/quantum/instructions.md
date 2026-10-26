# Quantum Operator Tools

Use the same `session_id` across all calls to share state. Introduce bosonic annihilation operators with `introduce_boson_operator`; the creation operator is `Dagger(a)`. Expression strings can use `Dagger`, `Commutator`, `AntiCommutator`, `BosonOp`, `BosonCoherentKet`, `BosonCoherentBra`, `Ket`, `Bra`, `InnerProduct`, `qapply`, `normal_order` and `normal_ordered_form` (from `sympy.physics.quantum`), and stored results via `@key`.

Each operator satisfies `[a, a†] = 1`. Operators with different names are independent modes and commute with each other.

Computing tools return JSON by default: `{"key": ..., "result": ..., "latex": ...}`. `key` is the session key the result is stored under, `result` is the value as a SymPy string, and `latex` is its LaTeX form. Failures return `{"error": "..."}`. Pass `output_format="legacy"` to get just the key.

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

---

## introduce_boson_operator
Introduce a bosonic annihilation operator `a` that can be used by name in expression strings. Its creation operator is `Dagger(a)`.

**When to use:**
- Before building expressions with ladder operators, e.g. `(a + Dagger(a))**2`
- Once per mode: introduce `a` and `b` for two independent modes

**When NOT to use:**
- For ordinary commuting symbols — use `intro`
- For finite matrices such as Pauli matrices — use `create_matrix`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `name` (str): The operator name, e.g. `"a"`.

**Returns:** The operator name as plain text (not JSON).

**Example:**
```
introduce_boson_operator(session_id="s1", name="a")
→ "a"
```

---

## normal_order_expression
Put an operator expression in normal order: all creation operators `a†` to the left of all annihilation operators `a`.

**When to use:**
- `mode="symbol"` for the normal-ordering symbol `:X:` — the operators are reordered **without** commutator terms, so `:a a†: = a† a`
- `mode="commute"` to rewrite the same operator in normal order using `[a, a†] = 1`, so `a a† = a† a + 1`

**When NOT to use:**
- To evaluate a commutator — use `evaluate_commutator`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the operator expression.
- `mode` (str, optional): `"symbol"` (default) or `"commute"`, as above.
- `timeout_seconds` (float, optional): Time limit for this call in seconds. Default: the server's limit (`SYMPY_TIMEOUT`, 30 s unless configured); `0` means no limit. A call that runs out of time returns a timeout error and changes nothing else.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"` (the key only).

**Returns:** JSON — `key`, `result`, `latex` of the normal-ordered expression.

**Example:**
```
normal_order_expression(session_id="s1", expr_key="expr_0", mode="symbol")   # expr_0 = (a + Dagger(a))**2
→ {"key": "expr_1", "result": "2*Dagger(a)*a + Dagger(a)**2 + a**2", "latex": "..."}
```

---

## evaluate_commutator
Evaluate the commutator `[A, B] = AB - BA` of two operator expressions, simplified with `[a, a†] = 1` and written in normal order.

**When to use:**
- For ladder-operator algebra, e.g. `[a, a†²] = 2a†`
- To check canonical commutation relations

**When NOT to use:**
- For finite matrices — use `matrix_commutator`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_a` (str): A stored key or an expression string, e.g. `"a"`.
- `expr_b` (str): A stored key or an expression string, e.g. `"Dagger(a)**2"`.
- `timeout_seconds` (float, optional): Time limit for this call in seconds. Default: the server's limit (`SYMPY_TIMEOUT`, 30 s unless configured); `0` means no limit. A call that runs out of time returns a timeout error and changes nothing else.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"` (the key only).

**Returns:** JSON — `key`, `result`, `latex` of the evaluated commutator.

**Example:**
```
evaluate_commutator(session_id="s1", expr_a="a", expr_b="Dagger(a)**2")
→ {"key": "expr_0", "result": "2*Dagger(a)", "latex": "2 {{a}^\\dagger}"}
```

---

## quantum_apply
Apply the operators in an expression to the kets and bras next to them (SymPy's `qapply`), e.g. `a|α⟩ = α|α⟩` for a coherent state.

**When to use:**
- To act with operators on explicit states built with `BosonCoherentKet`, `Ket`, …

**When NOT to use:**
- For coherent-state expectation values — `qapply` does not move `a†` onto a bra (`⟨α|a† = ᾱ⟨α|`), so use `coherent_state_expectation`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of an expression containing operators and states.
- `timeout_seconds` (float, optional): Time limit for this call in seconds. Default: the server's limit (`SYMPY_TIMEOUT`, 30 s unless configured); `0` means no limit. A call that runs out of time returns a timeout error and changes nothing else.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"` (the key only).

**Returns:** JSON — `key`, `result`, `latex` of the expression after applying operators.

**Example:**
```
quantum_apply(session_id="s1", expr_key="expr_0")   # expr_0 = a*BosonCoherentKet(alpha)
→ {"key": "expr_1", "result": "alpha*|alpha>", "latex": "..."}
```

---

## coherent_state_expectation
Expectation value `⟨α| X |α⟩` of an operator expression in a coherent state `|α⟩` of one mode. `X` is first rewritten in normal order with `[a, a†] = 1`. Then `⟨α| f(a†, a) |α⟩ = f(ᾱ, α)` holds exactly, because `a|α⟩ = α|α⟩` and `⟨α|a† = ᾱ⟨α|`.

**When to use:**
- For `⟨α| X |α⟩` with `X` any polynomial in `a`, `a†`
- For `⟨α| :X: |α⟩`: normal-order with `normal_order_expression(mode="symbol")` first, then pass that key

**When NOT to use:**
- For expressions with operators of other modes left over — take one mode at a time

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the operator expression `X`.
- `operator_name` (str): The annihilation operator of the mode, e.g. `"a"` (from `introduce_boson_operator`).
- `alpha` (str): The coherent-state eigenvalue, e.g. `"alpha"` (an introduced symbol, complex by default).
- `timeout_seconds` (float, optional): Time limit for this call in seconds. Default: the server's limit (`SYMPY_TIMEOUT`, 30 s unless configured); `0` means no limit. A call that runs out of time returns a timeout error and changes nothing else.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"` (the key only).

**Returns:** JSON — `key`, `result`, `latex` of the expectation value; `normal_ordered` — the normal-ordered form of `X` that was evaluated.

**Example:**
```
# <alpha| :(a + a†)^2: |alpha>, with expr_1 = normal_order_expression(expr_0, mode="symbol")
coherent_state_expectation(session_id="s1", expr_key="expr_1", operator_name="a", alpha="alpha")
→ {"key": "expr_2", "result": "alpha**2 + 2*alpha*conjugate(alpha) + conjugate(alpha)**2", "latex": "...", "normal_ordered": "..."}
```
