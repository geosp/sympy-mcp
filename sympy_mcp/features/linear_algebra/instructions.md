# Linear Algebra Tools

Use the same `session_id` across all calls to share state. Symbols must be introduced with `/symbols/intro` before they can appear in matrix element strings. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `matrix_key` or `expr_key` in subsequent calls).

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

---

## create_matrix
Creates a symbolic matrix from a 2D list of expression strings.

**Parameters:**
- `session_id` (str): Session identifier. Pass any string — sessions are auto-created on first use.
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

**Parameters:**
- `session_id` (str): Session identifier.
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

**Parameters:**
- `session_id` (str): Session identifier.
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

**Parameters:**
- `session_id` (str): Session identifier.
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

**Parameters:**
- `session_id` (str): Session identifier.
- `matrix_key` (str): Session key of an existing matrix.

**Returns:** `result` — list of `(eigenvalue, multiplicity, [eigenvectors])` tuples as a string; `result_key` — session key for chaining.

**Example:**
```json
POST /linear_algebra/eigenvectors
{"session_id": "s1", "matrix_key": "matrix_0"}
→ {"success": true, "result": "[(-1, 1, [Matrix([[-1], [1]])]), (2, 1, [Matrix([[2], [3]])])]", "result_key": "expr_0"}
```
