# Units Tools

Use the same `session_id` across all calls to share state. Physical quantity expressions must be introduced with `/expressions/introduce` before conversion. See `POST /session/reset` docs for the full session management guide.

All computation tools return `result` (the human-readable value) and `result_key` (the session key to pass as `expr_key` in subsequent calls).

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

Pre-loaded units available in all sessions: `meter`, `second`, `kilogram`, `ampere`, `kelvin`, `mole`, `candela`, `kilometer`, `millimeter`, `gram`, `joule`, `newton`, `pascal`, `watt`, `coulomb`, `volt`, `ohm`, `farad`, `henry`, `speed_of_light`, `gravitational_constant`, `planck`, `day`, `year`, `minute`, `hour`.

---

## convert_to_units
Converts a physical quantity expression to specified target units.

**When to use:**
- When changing between unit systems (e.g., kilometers to meters, joules to eV)
- When the problem asks to "express in terms of" specific units
- For compound unit conversions (e.g., m/s to km/h)

**When NOT to use:**
- On dimensionless or purely symbolic expressions — there are no units to convert
- When you want to simplify unit expressions without specifying target units — use `quantity_simplify_units`

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression to convert (a `result_key` from a previous call). The expression should be a physical quantity (e.g., a value times a unit).
- `target_units` (list of str): Unit name strings to convert to (e.g., `["meter", "second"]`).
- `unit_system` (str, optional): Unit system — `"SI"` (default), `"MKS"`, `"MKSA"`, `"natural"`, `"cgs"`.

**Returns:** `result` — the converted expression as a string (e.g. `"1000*meter"`); `result_key` — session key for chaining.

**Notes:**
- Unit names must match SymPy's `sympy.physics.units` names exactly (e.g., `"meter"` not `"m"`).
- Multiple target units can be provided for compound unit conversions.

**Example:**
```json
POST /units/convert
{"session_id": "s1", "expr_key": "expr_0", "target_units": ["meter"]}
→ {"success": true, "result": "1000*meter", "result_key": "expr_1"}
```

---

## quantity_simplify_units
Simplifies a physical quantity expression, combining and reducing units where possible.

**When to use:**
- When an expression has complex/compound units that should be reduced to standard derived units (e.g., `kg*m²/s²` → `joule`)
- When you want SymPy to automatically determine the simplest unit representation

**When NOT to use:**
- When you need a specific target unit — use `convert_to_units` with explicit targets
- On expressions without any unit quantities

**Parameters:**
- `session_id` (str): Session identifier. Must be obtained by calling `create_session` first.
- `expr_key` (str): Session key of the expression to simplify.
- `unit_system` (str, optional): Unit system context — `"SI"` (default), `"MKS"`, `"MKSA"`, `"natural"`, `"cgs"`.

**Returns:** `result` — the simplified expression as a string; `result_key` — session key for chaining.

**Example:**
```json
POST /units/simplify
{"session_id": "s1", "expr_key": "expr_0"}
→ {"success": true, "result": "joule", "result_key": "expr_1"}
```

---

## Available Unit Systems

| Value | Description |
|-------|-------------|
| `SI` | International System of Units (default) |
| `MKS` | Meter-Kilogram-Second |
| `MKSA` | Meter-Kilogram-Second-Ampere |
| `natural` | Natural units (c = hbar = 1) |
| `cgs` | Centimeter-Gram-Second (CGS-Gauss) |
