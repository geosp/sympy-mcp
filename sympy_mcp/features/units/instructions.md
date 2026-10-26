# Units Tools

Use the same `session_id` across all calls to share state. Physical quantity expressions must be introduced with `introduce_expression` before conversion. See the session tools (`create_session`, `list_session_state`) for session management.

Computing tools return JSON by default: `{"key": ..., "result": ..., "latex": ...}`. `key` is the session key the result is stored under (pass it to later calls, or reference it as `@key` in an expression string), `result` is the value as a SymPy string, and `latex` is its LaTeX form. Some tools add extra fields, listed under Returns. Failures return `{"error": "..."}`. Pass `output_format="legacy"` to get the plain string these tools returned before (usually just the key).

Before calling any tool, carefully read all parameter names, types, and required/optional markers in its schema. Do not guess parameter names.

Pre-loaded units available in all sessions: `meter`, `second`, `kilogram`, `ampere`, `kelvin`, `mole`, `candela`, `kilometer`, `millimeter`, `gram`, `joule`, `newton`, `pascal`, `watt`, `coulomb`, `volt`, `ohm`, `farad`, `henry`, `speed_of_light`, `gravitational_constant`, `planck`, `day`, `year`, `minute`, `hour`.

Pre-loaded physical constants: `hbar`, `boltzmann_constant`, `elementary_charge`, `electron_rest_mass`, `vacuum_permittivity`, `avogadro_number`, `planck_length` (with SymPy's SI values). Short aliases such as `c`, `k_B` or `me` are deliberately **not** defined, so they stay ordinary symbols: write `speed_of_light`, `boltzmann_constant`, `electron_rest_mass`. To use one of the constant names as a plain symbol instead, introduce it with `intro` (e.g. `intro(var_name="hbar")`), which replaces the constant in that session.

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
- `expr_key` (str): Session key of the expression to convert (the `key` returned by a previous call). The expression should be a physical quantity (e.g., a value times a unit).
- `target_units` (list of str): Unit name strings to convert to (e.g., `["meter", "second"]`).
- `unit_system` (str, optional): Unit system — `"SI"` (default), `"MKS"`, `"MKSA"`, `"natural"`, `"cgs"`.
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the converted expression as a string (e.g. `"1000*meter"`); `key` — session key for chaining; `latex` — the result in LaTeX.

**Notes:**
- Unit names must match SymPy's `sympy.physics.units` names exactly (e.g., `"meter"` not `"m"`).
- Multiple target units can be provided for compound unit conversions.

**Example:**
```
convert_to_units(session_id="s1", expr_key="expr_0", target_units=["meter"])
→ {"key": "expr_1", "result": "1000*meter", "latex": "1000 \\text{m}"}
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
- `output_format` (str, optional): `"structured"` (default) for the JSON payload, or `"legacy"` for the old plain-string return value.

**Returns:** JSON — `result` — the simplified expression as a string; `key` — session key for chaining; `latex` — the result in LaTeX.

**Example:**
```
quantity_simplify_units(session_id="s1", expr_key="expr_0")
→ {"key": "expr_1", "result": "joule", "latex": "\\text{J}"}
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
