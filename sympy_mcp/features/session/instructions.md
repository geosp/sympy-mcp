# Session Management

A **session** is an isolated in-memory namespace that stores your symbolic variables, expressions, functions, matrices, and tensors. All tools share state through a common `session_id`.

---

## Getting a session_id

**Option A — Create explicitly:**
```
POST /sessions
→ {"session_id": "abc-123-uuid"}
```

**Option B — Use any string (auto-create):**
Sessions are created automatically on first use. You can pass any unique string as `session_id` (e.g. `"my-session"`, `"user-42"`) without calling `POST /sessions` first.

---

## Typical workflow

Multi-step computations build up state across calls using the same `session_id`:

```
1. POST /symbols/intro          {session_id, var_name: "x"}
2. POST /expressions/introduce  {session_id, expr_str: "x**2"}
   → {result: "x**2", result_key: "expr_0"}
3. POST /calculus/differentiate {session_id, expr_key: "expr_0", var_name: "x"}
   → {result: "2*x", result_key: "expr_1"}
4. POST /calculus/integrate     {session_id, expr_key: "expr_1", var_name: "x"}
   → {result: "x**2", result_key: "expr_2"}
```

Symbols introduced with `/symbols/intro` are referenced by name in expression strings. Expressions are referenced by their `result_key` in subsequent computation calls.

---

## result vs result_key

All computation endpoints return two fields:

- `result` — the human-readable computed value (e.g. `"2*x"`, `"Matrix([[1, 0], [0, 1]])"`)
- `result_key` — the session key (e.g. `"expr_1"`) for use as `expr_key` in subsequent calls

Symbol introduction (`/symbols/intro`) returns only `result` (the variable name). Solve and LaTeX endpoints return only `result` (the formatted output). Only computation endpoints that store a new object in the session return a `result_key`.

---

## reset_state

Clears all session data and returns the session to its initial state.

**What is cleared:**
- All symbolic variables (`local_vars`)
- All defined functions (`functions`)
- All stored expressions, equations, and matrices (`expressions`)
- All stored metrics (`metrics`)
- All stored tensor objects (`tensor_objects`)
- All coordinate systems (`coordinate_systems`)
- The expression counter (reset to 0)

Unit constants (meter, second, kilogram, etc.) are re-initialized automatically after the reset.

**Parameters:**
- `session_id` (str): The session to reset.

**Returns:** `"State reset successfully. All variables, functions, expressions, and other objects have been cleared."`

Useful when starting a new problem within the same session, or to free memory from large intermediate expressions.
