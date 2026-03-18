# Linear Algebra Tools

Use the same `session_id` across all calls to share state. Symbols must be introduced with `/symbols/intro` before they can appear in matrix element strings. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `matrix_key` or `expr_key` in subsequent calls).

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

**Returns:** `result` — the matrix as a string (e.g. `"Matrix([[1, 2], [3, 4]])"`); `result_key` — session key for chaining (e.g. `"matrix_0"`).

**Notes:**
- Expression strings can reference session variables (introduced with `intro`).
- Numeric strings like `"1"`, `"0"`, `"2/3"` work directly.
- Symbolic strings like `"x**2 + 1"` work if `x` is in the session.

**Example:**
```json
POST /linear_algebra/matrix
{"session_id": "s1", "matrix_data": [["1", "2"], ["3", "4"]]}
→ {"success": true, "result": "Matrix([[1, 2], [3, 4]])", "result_key": "matrix_0"}
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
- `matrix_key` (str): Session key of an existing matrix (a `result_key` from `create_matrix`).

**Returns:** `result` — the determinant as a string (e.g. `"-2"`); `result_key` — session key for chaining.

**Example:**
```json
POST /linear_algebra/determinant
{"session_id": "s1", "matrix_key": "matrix_0"}
→ {"success": true, "result": "-2", "result_key": "expr_0"}
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

**Returns:** `result` — the inverse matrix as a string; `result_key` — session key for chaining.

**Example:**
```json
POST /linear_algebra/inverse
{"session_id": "s1", "matrix_key": "matrix_0"}
→ {"success": true, "result": "Matrix([[-2, 1], [3/2, -1/2]])", "result_key": "matrix_1"}
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

**Returns:** `result` — eigenvalue dictionary as a string; `result_key` — session key for chaining.

**Example:**
```json
POST /linear_algebra/eigenvalues
{"session_id": "s1", "matrix_key": "matrix_0"}
→ {"success": true, "result": "{-1: 1, 2: 1}", "result_key": "expr_0"}
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

**Returns:** `result` — list of `(eigenvalue, multiplicity, [eigenvectors])` tuples as a string; `result_key` — session key for chaining.

**Example:**
```json
POST /linear_algebra/eigenvectors
{"session_id": "s1", "matrix_key": "matrix_0"}
→ {"success": true, "result": "[(-1, 1, [Matrix([[-1], [1]])]), (2, 1, [Matrix([[2], [3]])])]", "result_key": "expr_0"}
```
