# Session Management

A **session** is an isolated in-memory namespace that stores your symbolic variables, expressions, functions, matrices, and tensors. All tools share state through a common `session_id`.

---

## create_session

Before calling any other tool, you **must** create a session using `create_session`. The server generates a unique session ID (UUID) and returns it. You then pass this ID as `session_id` to all subsequent tool calls.

**When to use:**
- As the very first step before any symbolic computation
- When starting a new, independent problem (create a fresh session rather than reusing an old one)

**When NOT to use:**
- When a session already exists for the current problem — reuse the existing `session_id`

**Parameters:**
- `description` (str): A short description of the session's purpose (e.g., `"Hooke's law spring work integral"`).

**Returns:** JSON with `session_id` (the generated UUID), `description`, and `created_at`.

**Example:**
```
create_session(description="Hooke's law spring work integral")
→ {"session_id": "a1b2c3d4-...", "description": "Hooke's law spring work integral", "created_at": "..."}
```

**Do NOT invent your own session IDs.** Only IDs returned by `create_session` are valid. Any tool call with an unknown `session_id` will be rejected with an error.

---

## list_sessions

Use `list_sessions` to see all active sessions with their descriptions and timestamps. This is useful when resuming work or checking what sessions exist on the server.

**When to use:**
- When resuming a previous conversation and you need to find an existing session ID
- To check whether a session from an earlier interaction is still alive

**When NOT to use:**
- During normal computation flow — you already have the `session_id` from `create_session`

**Parameters:** None.

**Returns:** JSON with `sessions` (list of session objects) and `count`.

---

## Typical workflow

Multi-step computations build up state across calls using the same `session_id`:

```
1. create_session(description="differentiation example")
   → session_id = "a1b2c3d4-..."
2. intro(session_id, var_name="x")
3. introduce_expression(session_id, expression="x**2")
   → stored as expr_0
4. differentiate_expression(session_id, expr_key="expr_0", var_name="x")
   → stored as expr_1, value: 2*x
5. list_session_state(session_id)
   → shows all symbols and expression values at a glance
```

Symbols introduced with `intro` are referenced by name in expression strings. Expressions are referenced by their stored key (e.g. `expr_0`) in subsequent computation calls.

**Tip:** Use `list_session_state` to inspect computed values directly. Avoid calling `print_latex_expression` on each result individually just to read values — the state listing already shows every stored expression and its current value.

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
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.

**Returns:** `"State reset successfully. All variables, functions, expressions, and other objects have been cleared."`

**When to use:**
- When pivoting to a completely different problem within the same session
- To free memory from large intermediate expressions that are no longer needed
- When accumulated state is causing confusion or naming conflicts

**When NOT to use:**
- Between related sub-problems that share variables — you will lose all symbols and expressions
- Just to "clean up" after getting a final answer — it destroys useful state

---

## list_session_state

**This is the primary tool for inspecting computed values and session contents.**

Inspect all stored items in the current session. Returns a JSON object showing:
- `symbols` — user-introduced variable names (e.g. `["x", "y"]`)
- `expressions` — stored expression keys and their current values (e.g. `{"expr_0": "x**2 + 1"}`)
- `functions` — defined symbolic functions (e.g. `["f"]`)
- `coordinate_systems` — 3D coordinate system names
- `metrics` — relativity metric names
- `tensors` — computed tensor names

Returns `{}` if the session is empty.

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.

**Returns:** JSON string. Use this when you need to know what `expr_key` values are available before chaining calls, or to recover state in a long session.

**When to use:**
- After any computation to verify/inspect the result — this is your go-to inspection tool
- To see what `expr_key` or `matrix_key` values are available before chaining calls
- To recover context in a long session or after multiple steps
- When you need to read expression values — always prefer this over `print_latex_expression`

**When NOT to use:**
- There is no reason to avoid this tool; call it liberally whenever you need to check state

**Prefer this tool for inspecting results.** Rather than calling `print_latex_expression` on each expression key to see its value, call `list_session_state` once to see all stored expressions and their values. Reserve `print_latex_expression` for when you specifically need LaTeX-formatted output for display.

---

## delete_stored_key

Delete a single stored item by key. Searches all stores (expressions, functions, coordinate_systems, metrics, tensors) and removes the first match.

**When to use:**
- To remove specific intermediate results that clutter the session without resetting everything
- When a stored key has the wrong value and you want to recompute it cleanly

**When NOT to use:**
- To clear the entire session — use `reset_state` instead
- When the stored result might be needed later in the computation chain

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `key` (str): The key to delete (e.g. `"expr_2"`, `"f"`, `"R"`).

**Returns:** Confirmation string on success, or an error if the key is not found.
