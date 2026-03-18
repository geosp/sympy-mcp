# Symbol Introduction Tools

Use the same `session_id` across all calls to share state. See `POST /session/reset` docs for full session management guide.

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

---

## intro
Introduces a single symbolic variable into the session. The variable is then available by name in expression strings passed to other tools.

**When to use:**
- When you need to introduce exactly one variable, especially with specific assumptions
- When you want fine-grained control over a single variable's assumptions

**When NOT to use:**
- When introducing multiple variables at once — use `intro_many` for efficiency (one call vs. many)
- When the variable has already been introduced in this session

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `var_name` (str): Variable name (e.g., `"x"`, `"alpha"`, `"theta"`)
- `assumptions` (list): Assumptions that hold true (e.g., `["real", "positive"]`). Default: `[]`
- `negative_assumptions` (list): Assumptions that are explicitly false (e.g., `["complex"]`). Default: `[]`

**Returns:** `result` — the variable name confirming creation (e.g. `"x"`). No `result_key` (symbols are referenced by name, not by key).

**Example:**
```json
POST /symbols/intro
{"session_id": "s1", "var_name": "x", "assumptions": ["real"]}
→ {"success": true, "result": "x"}
```

---

## intro_many
Introduces multiple symbolic variables in a single call.

**When to use:**
- When setting up a problem that involves two or more variables — always prefer this over multiple `intro` calls
- At the start of a session to declare all needed symbols at once

**When NOT to use:**
- When each variable needs complex, different assumption sets that are hard to express in the list format — use individual `intro` calls
- When only one variable is needed — `intro` is equally fine

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `variables` (list): List of variable specs. Each can be:
  - A string: `"x"` → creates x with no assumptions
  - A list: `["x", ["real"], []]` → creates x with real assumption, no negative assumptions

**Returns:** `result` — confirmation string listing all created symbols.

**Example:**
```json
POST /symbols/intro_many
{"session_id": "s1", "variables": ["x", "y", ["z", ["positive"], []]]}
→ {"success": true, "result": "{'x': x, 'y': y, 'z': z}"}
```
