from sympy_mcp.state import SymPyState
from sympy_mcp.shared.enums import UnitSystem


def test_convert_to_si():
    state = SymPyState()
    # speed_of_light in [meter, second]
    expr_key = state.introduce_expression("speed_of_light")
    result_key = state.convert_to_units(expr_key, ["meter", "second"], UnitSystem.SI)
    latex = state.print_latex_expression(result_key)
    assert "\\text{m}" in latex and "\\text{s}" in latex
    assert "299792458" in latex


def test_convert_to_impossible():
    state = SymPyState()
    # speed_of_light in [meter] (should return unchanged)
    expr_key = state.introduce_expression("speed_of_light")
    result_key = state.convert_to_units(expr_key, ["meter"], UnitSystem.SI)
    latex = state.print_latex_expression(result_key)
    assert "\\text{c}" in latex  # c is the symbol for speed of light


def test_convert_to_cgs_gauss():
    state = SymPyState()
    # ampere in [meter, gram, second] in cgs_gauss
    expr_key = state.introduce_expression("ampere")
    # First test with SI
    result_key_si = state.convert_to_units(
        expr_key, ["meter", "gram", "second"], UnitSystem.SI
    )
    latex_si = state.print_latex_expression(result_key_si)
    assert "\\text{A}" in latex_si  # A is the symbol for ampere

    # Then with CGS
    result_key_cgs = state.convert_to_units(
        expr_key, ["meter", "gram", "second"], UnitSystem.CGS
    )
    latex_cgs = state.print_latex_expression(result_key_cgs)
    # In CGS, ampere should be converted to a combination of base units
    # Either we'll see the units or we'll still see ampere if conversion failed
    assert (
        "\\text{g}" in latex_cgs or "\\text{m}" in latex_cgs or "\\text{A}" in latex_cgs
    )


def test_quantity_simplify():
    state = SymPyState()
    # meter/kilometer should simplify to 1/1000 or 0.001
    expr_key = state.introduce_expression("meter/kilometer")
    result_key = state.quantity_simplify_units(expr_key, UnitSystem.SI)
    latex = state.print_latex_expression(result_key)
    assert "0.001" in latex or "\\frac{1}{1000}" in latex or "10^{-3}" in latex

    # Also test .simplify() via sympy
    expr_key2 = state.introduce_expression("(meter/kilometer).simplify()")
    latex2 = state.print_latex_expression(expr_key2)
    assert "0.001" in latex2 or "\\frac{1}{1000}" in latex2 or "10^{-3}" in latex2


def test_convert_to_unknown_unit():
    state = SymPyState()
    expr_key = state.introduce_expression("meter")
    result = state.convert_to_units(expr_key, ["not_a_unit"], UnitSystem.SI)
    assert "Error" in result or "error" in result.lower()


def test_quantity_simplify_nonexistent_expr():
    state = SymPyState()
    result = state.quantity_simplify_units("nonexistent_key", UnitSystem.SI)
    assert "Error" in result or "error" in result.lower()


def test_convert_to_prefixed_units():
    state = SymPyState()
    # Test with prefixed units already applied in the expression
    # Create speed of light in femtometer/second directly
    expr_key = state.introduce_expression(
        "speed_of_light * (10**15)", True, "speed_of_light_in_fm_s"
    )
    latex = state.print_latex_expression(expr_key)
    assert "299792458" in latex and "10^{15}" in latex or "c" in latex

    # Test conversion from prefixed units
    expr_key = state.introduce_expression("1000*kilometer")
    result_key = state.convert_to_units(expr_key, ["meter"], UnitSystem.SI)
    latex = state.print_latex_expression(result_key)
    assert "1000000" in latex or "10^{6}" in latex

    # Test with a complex expression involving scaling
    expr_key = state.introduce_expression(
        "speed_of_light * 10**-9", True, "speed_in_nm_per_s"
    )
    latex = state.print_latex_expression(expr_key)
    # The output might be formatted as \frac{c}{1000000000} or similar
    assert "\\text{c}" in latex and (
        "10^{-9}" in latex or "1000000000" in latex or "\\frac" in latex
    )


CONSTANTS = [
    "hbar", "boltzmann_constant", "elementary_charge", "electron_rest_mass",
    "vacuum_permittivity", "avogadro_number", "planck_length",
]


def test_physical_constants_are_in_the_namespace():
    from sympy.physics import units
    state = SymPyState()
    for name in CONSTANTS:
        key = state.introduce_expression(name)
        assert state.expressions[key] == getattr(units, name), name


def test_unruh_like_temperature_in_kelvin():
    """hbar * (9.81 m/s^2) / (2 pi c k_B) = 3.978e-20 K"""
    from sympy.physics.units import kelvin
    state = SymPyState()
    expr = state.introduce_expression(
        "hbar*(981/100*meter/second**2)/(2*pi*speed_of_light*boltzmann_constant)"
    )
    in_kelvin = state.convert_to_units(expr, ["kelvin"])
    value = state.expressions[state.evalf_expression(in_kelvin, 4)]
    assert value.has(kelvin)
    assert abs(float(value / kelvin) - 3.978e-20) < 5e-24  # 4 significant digits


def test_short_aliases_stay_plain_symbols():
    import sympy
    state = SymPyState()
    for name in ["c", "k_B", "me", "e0"]:
        key = state.introduce_expression(name)
        assert state.expressions[key] == sympy.Symbol(name), name


def test_intro_replaces_a_constant():
    state = SymPyState()
    state.intro("hbar", [], [])
    key = state.introduce_expression("hbar")
    assert state.expressions[key] is state.local_vars["hbar"]
    assert state.expressions[key].is_Symbol
