# Symbol Introduction Tools

Use the same `session_id` across all calls to share state. See `POST /session/reset` docs for full session management guide.

---

## intro
Introduces a single symbolic variable into the session. The variable is then available by name in expression strings passed to other tools.

**Parameters:**
- `session_id` (str): Session identifier. Pass any string — sessions are auto-created on first use, or call `POST /sessions` to get one.
- `var_name` (str): Variable name (e.g., `"x"`, `"alpha"`, `"theta"`)
- `pos_assumptions` (list): Positive assumptions (e.g., `["real", "positive"]`). Default: `[]`
- `neg_assumptions` (list): Negative assumptions (e.g., `["complex"]`). Default: `[]`

**Returns:** `result` — the variable name confirming creation (e.g. `"x"`). No `result_key` (symbols are referenced by name, not by key).

**Example:**
```json
POST /symbols/intro
{"session_id": "s1", "var_name": "x", "pos_assumptions": ["real"]}
→ {"success": true, "result": "x"}
```

---

## intro_many
Introduces multiple symbolic variables in a single call.

**Parameters:**
- `session_id` (str): Session identifier.
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
