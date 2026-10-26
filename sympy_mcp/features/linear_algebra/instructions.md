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
