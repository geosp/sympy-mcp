import pytest
from sympy_mcp.state import SymPyState
from sympy_mcp.shared.enums import Assumption


class TestDifferentiateExpressionTool:
    def test_differentiate_polynomial(self):
        state = SymPyState()
        # Introduce a variable
        state.intro("x", [Assumption.REAL], [])

        # Create an expression: x^3
        expr_key = state.introduce_expression("x**3")

        # First derivative
        first_deriv_key = state.differentiate_expression(expr_key, "x")
        first_deriv_latex = state.print_latex_expression(first_deriv_key)

        # Should be 3x^2
        assert "3" in first_deriv_latex
        assert "x^{2}" in first_deriv_latex

        # Second derivative
        second_deriv_key = state.differentiate_expression(expr_key, "x", 2)
        second_deriv_latex = state.print_latex_expression(second_deriv_key)

        # Should be 6x
        assert "6" in second_deriv_latex
        assert "x" in second_deriv_latex

        # Third derivative
        third_deriv_key = state.differentiate_expression(expr_key, "x", 3)
        third_deriv_latex = state.print_latex_expression(third_deriv_key)

        # Should be 6
        assert "6" in third_deriv_latex

    def test_differentiate_trigonometric(self):
        state = SymPyState()
        # Introduce a variable
        state.intro("x", [Assumption.REAL], [])

        # Create sin(x) expression
        sin_key = state.introduce_expression("sin(x)")

        # Derivative of sin(x) is cos(x)
        deriv_key = state.differentiate_expression(sin_key, "x")
        deriv_latex = state.print_latex_expression(deriv_key)

        assert "\\cos" in deriv_latex

    def test_nonexistent_expression(self):
        state = SymPyState()
        state.intro("x", [Assumption.REAL], [])
        result = state.differentiate_expression("nonexistent_key", "x")
        assert "error" in result.lower()

    def test_nonexistent_variable(self):
        state = SymPyState()
        state.intro("x", [Assumption.REAL], [])
        expr_key = state.introduce_expression("x**2")
        result = state.differentiate_expression(expr_key, "y")
        assert "error" in result.lower()


class TestIntegrateExpressionTool:
    def test_indefinite_integral_polynomial(self):
        state = SymPyState()
        # Introduce a variable
        state.intro("x", [Assumption.REAL], [])

        # Create expression: x^2
        expr_key = state.introduce_expression("x**2")

        # Integrate
        integral_key = state.integrate_expression(expr_key, "x")
        integral_latex = state.print_latex_expression(integral_key)

        # Should be x^3/3
        assert "x^{3}" in integral_latex
        assert "3" in integral_latex

    def test_indefinite_integral_trigonometric(self):
        state = SymPyState()
        # Introduce a variable
        state.intro("x", [Assumption.REAL], [])

        # Create expression: cos(x)
        expr_key = state.introduce_expression("cos(x)")

        # Integrate
        integral_key = state.integrate_expression(expr_key, "x")
        integral_latex = state.print_latex_expression(integral_key)

        # Should be sin(x)
        assert "\\sin" in integral_latex

    def test_nonexistent_expression(self):
        state = SymPyState()
        state.intro("x", [Assumption.REAL], [])
        result = state.integrate_expression("nonexistent_key", "x")
        assert "error" in result.lower()

    def test_nonexistent_variable(self):
        state = SymPyState()
        state.intro("x", [Assumption.REAL], [])
        expr_key = state.introduce_expression("x**2")
        result = state.integrate_expression(expr_key, "y")
        assert "error" in result.lower()


class TestVectorOperations:
    def test_create_coordinate_system(self):
        state = SymPyState()
        # Create coordinate system
        result = state.create_coordinate_system("R")
        assert result == "R"
        assert "R" in state.coordinate_systems

    def test_create_custom_coordinate_system(self):
        state = SymPyState()
        # Create coordinate system with custom names
        result = state.create_coordinate_system("C", ["rho", "phi", "z"])
        assert result == "C"
        assert "C" in state.coordinate_systems

    def test_create_vector_field(self):
        state = SymPyState()
        # Create coordinate system
        state.create_coordinate_system("R")

        # Introduce variables to represent components
        state.intro("x", [Assumption.REAL], [])
        state.intro("y", [Assumption.REAL], [])
        state.intro("z", [Assumption.REAL], [])

        # Create vector field F = (y, -x, z)
        vector_field_key = state.create_vector_field("R", "y", "-x", "z")

        # The key might be an error message if the test is failing
        if "error" not in vector_field_key.lower():
            assert vector_field_key.startswith("vector_")
        else:
            assert False, f"Failed to create vector field: {vector_field_key}"

    def test_calculate_curl(self):
        state = SymPyState()
        # Create coordinate system
        state.create_coordinate_system("R")

        # Introduce variables
        state.intro("x", [Assumption.REAL], [])
        state.intro("y", [Assumption.REAL], [])

        # Create a simple vector field for curl calculation
        vector_field_key = state.create_vector_field("R", "y", "-x", "0")

        # Check if vector field was created successfully
        if "error" in vector_field_key.lower():
            assert False, f"Failed to create vector field: {vector_field_key}"

        # Calculate curl
        curl_key = state.calculate_curl(vector_field_key)

        # Check if curl calculation was successful
        if "error" not in curl_key.lower():
            assert curl_key.startswith("vector_")
        else:
            assert False, f"Failed to calculate curl: {curl_key}"

    def test_calculate_divergence(self):
        state = SymPyState()
        # Create coordinate system
        state.create_coordinate_system("R")

        # Introduce variables
        state.intro("x", [Assumption.REAL], [])
        state.intro("y", [Assumption.REAL], [])
        state.intro("z", [Assumption.REAL], [])

        # Create a simple identity vector field
        vector_field_key = state.create_vector_field("R", "x", "y", "z")

        # Check if vector field was created successfully
        if "error" in vector_field_key.lower():
            assert False, f"Failed to create vector field: {vector_field_key}"

        # Calculate divergence - should be 0 because symbols have no dependency on coordinates
        div_key = state.calculate_divergence(vector_field_key)

        # Check if divergence calculation was successful
        if "error" in div_key.lower():
            assert False, f"Failed to calculate divergence: {div_key}"

        div_latex = state.print_latex_expression(div_key)

        # Check result - should be 0
        assert "0" in div_latex

    def test_calculate_gradient(self):
        state = SymPyState()
        # Create coordinate system
        state.create_coordinate_system("R")

        # Introduce variables
        state.intro("x", [Assumption.REAL], [])
        state.intro("y", [Assumption.REAL], [])
        state.intro("z", [Assumption.REAL], [])

        # Create a simple scalar field
        scalar_field_key = state.introduce_expression("x**2 + y**2 + z**2")

        # Calculate gradient
        grad_key = state.calculate_gradient(scalar_field_key)

        # Check if gradient calculation was successful
        if "error" not in grad_key.lower():
            assert grad_key.startswith("vector_")
        else:
            assert False, f"Failed to calculate gradient: {grad_key}"

    def test_nonexistent_coordinate_system(self):
        state = SymPyState()
        result = state.create_vector_field("NonExistent", "x", "y", "z")
        assert "error" in result.lower()

    def test_nonexistent_vector_field(self):
        state = SymPyState()
        result = state.calculate_curl("nonexistent_key")
        assert "error" in result.lower()
