# Linear Algebra Tools

Use the same `session_id` across all calls to share state. Symbols must be introduced with `intro` before they can appear in matrix element strings. See the session tools (`create_session`, `list_session_state`) for session management.

Expression strings can refer to stored results with `@key` — for example `"@expr_7 - @expr_9"` or `"diff(@expr_3, x)"` — instead of retyping them. The referenced value is used exactly as stored. An unknown key is an error. `@` directly after an operand (`A@B`) keeps its meaning of matrix multiplication; use `*` to multiply by a reference (`2*@expr_1`).

Computing tools return JSON by default: `{"key": ..., "result": ..., "latex": ...}`. `key` is the session key the result is stored under (pass it to later calls, or reference it as `@key` in an expression string), `result` is the value as a SymPy string, and `latex` is its LaTeX form. Some tools add extra fields, listed under Returns. Failures return `{"error": "..."}`. Pass `output_format="legacy"` to get the plain string these tools returned before (usually just the key).

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

---

## create_matrix
Creates a symbolic matrix from a 2D list of expression strings.

**When to use:**
- When a problem involves matrices, systems of equations in matrix form, or linear transformations
- As the entry point for all linear algebra operations (determinant, inverse, eigenvalues, etc.)

**When NOT to use:**
- For scalar expressions — use `introduce_expression`
- For vectors in a coordinate system (vector calculus context) — use `create_vector_field`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `matrix_data` (list of list of str): 2D list where each string is parsed as a SymPy expression. All rows must have the same length.
- `name` (str, optional): Custom key name (default: auto-generated `"matrix_N"`).
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the matrix as a string (e.g. `"Matrix([[1, 2], [3, 4]])"`); `key` — session key for chaining (e.g. `"matrix_0"`); `latex` — the result in LaTeX.

**Notes:**
- Expression strings can reference session variables (introduced with `intro`).
- Numeric strings like `"1"`, `"0"`, `"2/3"` work directly.
- Symbolic strings like `"x**2 + 1"` work if `x` is in the session.

**Example:**
```
create_matrix(session_id="s1", matrix_data=[["1", "2"], ["3", "4"]])
→ {"key": "matrix_0", "result": "Matrix([[1, 2], [3, 4]])", "latex": "\\left[\\begin{matrix}1 & 2\\\\3 & 4\\end{matrix}\\right]"}
```

---

## matrix_determinant
Calculates the determinant of a square matrix.

**When to use:**
- To check if a matrix is singular (det = 0)
- When the problem asks for the determinant explicitly
- To compute area/volume scaling factors from transformation matrices

**When NOT to use:**
- On non-square matrices (determinant is undefined)
- When you only need to know if the matrix is invertible — attempting `matrix_inverse` will tell you directly

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `matrix_key` (str): Session key of an existing matrix (the `key` returned by `create_matrix`).
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the determinant as a string (e.g. `"-2"`); `key` — session key for chaining; `latex` — the result in LaTeX.

**Example:**
```
matrix_determinant(session_id="s1", matrix_key="matrix_0")
→ {"key": "expr_0", "result": "-2", "latex": "-2"}
```

---

## matrix_inverse
Calculates the inverse of a square matrix. Fails if the matrix is singular.

**When to use:**
- When you need A⁻¹ to solve AX = B or for other algebraic manipulation
- When the problem explicitly asks for the inverse matrix

**When NOT to use:**
- On singular matrices (det = 0) — will fail
- On non-square matrices — inverse is undefined
- When solving Ax = b — `solve_linear_system` is more direct

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `matrix_key` (str): Session key of an existing matrix.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the inverse matrix as a string; `key` — session key for chaining; `latex` — the result in LaTeX.

**Example:**
```
matrix_inverse(session_id="s1", matrix_key="matrix_0")
→ {"key": "matrix_1", "result": "Matrix([[-2, 1], [3/2, -1/2]])", "latex": "\\left[\\begin{matrix}-2 & 1\\\\\\frac{3}{2} & - \\frac{1}{2}\\end{matrix}\\right]"}
```

---

## matrix_eigenvalues
Calculates the eigenvalues of a square matrix with their algebraic multiplicities.

**When to use:**
- When the problem asks for eigenvalues or characteristic values
- For stability analysis, diagonalizability checks, or spectral analysis
- When you only need eigenvalues without the corresponding eigenvectors

**When NOT to use:**
- When you also need eigenvectors — use `matrix_eigenvectors` (it returns eigenvalues too)
- On non-square matrices

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `matrix_key` (str): Session key of an existing matrix.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — eigenvalue dictionary as a string; `key` — session key for chaining; `latex` — the result in LaTeX.

**Example:**
```
matrix_eigenvalues(session_id="s1", matrix_key="matrix_0")
→ {"key": "expr_0", "result": "{3: 1, -1: 1}", "latex": "\\left\\{ -1 : 1, \\  3 : 1\\right\\}"}
```

---

## matrix_eigenvectors
Calculates the eigenvectors of a square matrix.

**When to use:**
- When both eigenvalues and eigenvectors are needed
- For diagonalization, modal analysis, or basis transformation problems

**When NOT to use:**
- When only eigenvalues are needed — `matrix_eigenvalues` is lighter
- On non-square matrices

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `matrix_key` (str): Session key of an existing matrix.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — list of `(eigenvalue, multiplicity, [eigenvectors])` tuples as a string; `key` — session key for chaining; `latex` — the result in LaTeX.

**Example:**
```
matrix_eigenvectors(session_id="s1", matrix_key="matrix_0")
→ {"key": "expr_0", "result": "[(-1, 1, [Matrix([[-1], [1]])]), (3, 1, [Matrix([[1], [1]])])]", "latex": "..."}
```

---

## matrix_multiply
Multiply two stored matrices: `A·B`.

**When to use:**
- To compose linear maps or apply a matrix to a column vector

**When NOT to use:**
- For element-wise products — build the result with `create_matrix` and `@key` references
- For powers of one matrix — use `matrix_power`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `a_key` (str): Session key of the left matrix `A`.
- `b_key` (str): Session key of the right matrix `B`. Its row count must equal the column count of `A`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"` (the key only).

**Returns:** JSON — `key` (`"matrix_N"`), `result`, `latex` of the product.

**Example:**
```
matrix_multiply(session_id="s1", a_key="matrix_0", b_key="matrix_1")   # [[1, 2], [3, 4]] · [[0, 1], [1, 0]]
→ {"key": "matrix_2", "result": "Matrix([[2, 1], [4, 3]])", "latex": "..."}
```

---

## matrix_power
Raise a square matrix to a power. The exponent may be symbolic, e.g. an integer symbol `n`, when SymPy can compute it via the Jordan form.

**When to use:**
- For `A^n` with a fixed or symbolic integer `n`
- For negative powers of an invertible matrix

**When NOT to use:**
- For `exp(A)` — use `matrix_exp`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `matrix_key` (str): Session key of a stored matrix (from `create_matrix` or another matrix tool).
- `exponent` (str): The power as an expression string, e.g. `"3"`, `"-1"`, `"n"`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"` (the key only).

**Returns:** JSON — `key` (`"matrix_N"`), `result`, `latex` of the power.

**Example:**
```
matrix_power(session_id="s1", matrix_key="matrix_0", exponent="n")   # [[1, 1], [0, 1]], n a positive integer
→ {"key": "matrix_1", "result": "Matrix([[1, n], [0, 1]])", "latex": "..."}
```

---

## matrix_exp
Matrix exponential `exp(A)` of a square matrix.

**When to use:**
- To solve linear ODE systems `x' = A x` (`x(t) = exp(A t) x(0)`)
- To build rotations, boosts and unitary time evolution from generators

**When NOT to use:**
- For element-wise exponentials

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `matrix_key` (str): Session key of a stored matrix (from `create_matrix` or another matrix tool).
- `output_format` (str, optional): `"structured"` (default) or `"legacy"` (the key only).

**Returns:** JSON — `key` (`"matrix_N"`), `result`, `latex` of `exp(A)`.

**Example:**
```
matrix_exp(session_id="s1", matrix_key="matrix_0")   # [[0, theta], [-theta, 0]]
→ {"key": "matrix_1", "result": "Matrix([[cos(theta), sin(theta)], [-sin(theta), cos(theta)]])", "latex": "..."}
```

---

## matrix_trace
Trace (sum of the diagonal) of a square matrix.

**When to use:**
- For invariants such as `tr(A)`, or `tr(ρ)` for a density matrix

**When NOT to use:**
- For non-square matrices — the trace is undefined

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `matrix_key` (str): Session key of a stored matrix (from `create_matrix` or another matrix tool).
- `output_format` (str, optional): `"structured"` (default) or `"legacy"` (the key only).

**Returns:** JSON — `key` (`"expr_N"`), `result`, `latex` of the trace.

**Example:**
```
matrix_trace(session_id="s1", matrix_key="matrix_0")   # [[1, 2], [2, 4]]
→ {"key": "expr_1", "result": "5", "latex": "5"}
```

---

## matrix_transpose
Transpose of a matrix, `Aᵀ`.

**When to use:**
- To turn rows into columns, or to check symmetry against `check_equivalence`

**When NOT to use:**
- For the conjugate transpose of a complex matrix — use `matrix_adjoint`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `matrix_key` (str): Session key of a stored matrix (from `create_matrix` or another matrix tool).
- `output_format` (str, optional): `"structured"` (default) or `"legacy"` (the key only).

**Returns:** JSON — `key` (`"matrix_N"`), `result`, `latex` of the transpose.

**Example:**
```
matrix_transpose(session_id="s1", matrix_key="matrix_0")   # [[1, 2, 3]]
→ {"key": "matrix_1", "result": "Matrix([[1], [2], [3]])", "latex": "..."}
```

---

## matrix_adjoint
Hermitian adjoint (conjugate transpose) `A†` of a matrix. This is **not** the classical adjugate (matrix of cofactors).

**When to use:**
- To check whether a matrix is Hermitian or unitary
- For quantum-mechanical operators in a finite basis

**When NOT to use:**
- For the plain transpose — use `matrix_transpose`
- For the inverse — use `matrix_inverse`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `matrix_key` (str): Session key of a stored matrix (from `create_matrix` or another matrix tool).
- `output_format` (str, optional): `"structured"` (default) or `"legacy"` (the key only).

**Returns:** JSON — `key` (`"matrix_N"`), `result`, `latex` of `A†`.

**Example:**
```
matrix_adjoint(session_id="s1", matrix_key="matrix_0")   # [[1, I], [0, 2]]
→ {"key": "matrix_1", "result": "Matrix([[1, 0], [-I, 2]])", "latex": "..."}
```

---

## matrix_commutator
Commutator `[A, B] = A·B - B·A` of two square matrices of the same size.

**When to use:**
- For Lie-algebra relations such as `[σx, σy] = 2i σz`
- To check whether two operators commute

**When NOT to use:**
- For abstract operators (e.g. bosonic `a`, `a†`) — use `evaluate_commutator`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `a_key` (str): Session key of `A`.
- `b_key` (str): Session key of `B`.
- `output_format` (str, optional): `"structured"` (default) or `"legacy"` (the key only).

**Returns:** JSON — `key` (`"matrix_N"`), `result`, `latex` of the commutator.

**Example:**
```
matrix_commutator(session_id="s1", a_key="matrix_0", b_key="matrix_1")   # Pauli σx, σy
→ {"key": "matrix_2", "result": "Matrix([[2*I, 0], [0, -2*I]])", "latex": "..."}
```

---

## matrix_rank
Rank of a matrix (the number of linearly independent rows or columns).

**When to use:**
- To check whether a system of linear equations is degenerate
- To find the dimension of the image of a linear map

**When NOT to use:**
- To get the null vectors themselves — use `matrix_nullspace`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `matrix_key` (str): Session key of a stored matrix (from `create_matrix` or another matrix tool).
- `output_format` (str, optional): `"structured"` (default) or `"legacy"` (the key only).

**Returns:** JSON — `key` (`"expr_N"`), `result`, `latex` of the rank.

**Example:**
```
matrix_rank(session_id="s1", matrix_key="matrix_0")   # [[1, 2], [2, 4]]
→ {"key": "expr_1", "result": "1", "latex": "1"}
```

---

## matrix_nullspace
Basis of the nullspace (kernel) of a matrix: the vectors `v` with `A·v = 0`.

**When to use:**
- To find the solutions of a homogeneous linear system
- To find eigenvectors of a known eigenvalue λ, as the nullspace of `A - λI`

**When NOT to use:**
- For the inhomogeneous system `A·x = b` — use `solve_linear_system`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `matrix_key` (str): Session key of a stored matrix (from `create_matrix` or another matrix tool).
- `output_format` (str, optional): `"structured"` (default) or `"legacy"` (the key only).

**Returns:** JSON — `key` (`"expr_N"`), `result`, `latex` of the list of basis column vectors; `dimension` — how many there are.

**Example:**
```
matrix_nullspace(session_id="s1", matrix_key="matrix_0")   # [[1, 2], [2, 4]]
→ {"key": "expr_1", "result": "[Matrix([[-2], [1]])]", "latex": "...", "dimension": 1}
```
