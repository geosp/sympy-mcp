"""
SymPyState — encapsulates all mutable SymPy session state.

Each client session gets its own SymPyState instance, providing full isolation
between concurrent users. All tool business logic lives here as methods.
"""

import logging
from typing import Dict, List, Optional, Literal, Any, Union

import sympy
from sympy import Eq, Function, dsolve, diff, integrate, simplify, Matrix
from sympy.parsing.sympy_parser import parse_expr
from sympy.core.facts import InconsistentAssumptions
from sympy.solvers.pde import pdsolve
from sympy.vector import CoordSys3D, curl, divergence, gradient
from sympy.physics.units import convert_to
from sympy.physics.units import __dict__ as units_dict
from sympy.physics.units.systems import SI, MKS, MKSA, natural
from sympy.physics.units.systems.cgs import cgs_gauss
from sympy.physics.units import (
    meter, kilogram, second, ampere, kelvin, mole, candela,
    kilometer, millimeter, gram, joule, newton, pascal, watt,
    coulomb, volt, ohm, farad, henry, speed_of_light,
    gravitational_constant, planck, day, year, minute, hour,
)

from sympy_mcp.shared.enums import (
    Assumption, Domain, ODEHint, PDEHint, Metric, Tensor, UnitSystem,
)

try:
    from einsteinpy.symbolic import (
        MetricTensor, RicciTensor, RicciScalar, EinsteinTensor,
        WeylTensor, ChristoffelSymbols, StressEnergyMomentumTensor,
    )
    from einsteinpy.symbolic.predefined import (
        Schwarzschild, Minkowski, MinkowskiCartesian, KerrNewman, Kerr,
        AntiDeSitter, DeSitter, ReissnerNordstorm, find,
    )
    EINSTEINPY_AVAILABLE = True
except ImportError:
    EINSTEINPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class SymPyState:
    """Encapsulates all mutable SymPy session state for one client session."""

    def __init__(self) -> None:
        self.local_vars: Dict[str, Any] = {}
        self.functions: Dict[str, Any] = {}
        self.expressions: Dict[str, Any] = {}
        self.metrics: Dict[str, Any] = {}
        self.tensor_objects: Dict[str, Any] = {}
        self.coordinate_systems: Dict[str, CoordSys3D] = {}
        self.expression_counter: int = 0
        self.initialize_units()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _next_expr_key(self) -> str:
        key = f"expr_{self.expression_counter}"
        self.expression_counter += 1
        return key

    def _next_vector_key(self) -> str:
        key = f"vector_{self.expression_counter}"
        self.expression_counter += 1
        return key

    def _next_matrix_key(self) -> str:
        key = f"matrix_{self.expression_counter}"
        self.expression_counter += 1
        return key

    def resolve_result(self, key: str) -> str:
        """Look up key across all state stores and return str(value). If not a key, return as-is."""
        if key in self.expressions:
            return str(self.expressions[key])
        if key in self.metrics:
            return str(self.metrics[key])
        if key in self.tensor_objects:
            return str(self.tensor_objects[key])
        if key in self.coordinate_systems:
            return str(self.coordinate_systems[key])
        return key  # already a direct string (error message, LaTeX result, etc.)

    def _parse_dict(self) -> Dict[str, Any]:
        return {**self.local_vars, **self.functions}

    def _coerce_domain(self, domain) -> "Domain":
        """Accept either a Domain enum or a string value."""
        if isinstance(domain, Domain):
            return domain
        return Domain(str(domain).lower())

    def _coerce_ode_hint(self, hint) -> Optional["ODEHint"]:
        """Accept None, ODEHint enum, or hint string. Returns None for 'default' / None."""
        if hint is None or (isinstance(hint, str) and hint.lower() in ("default", "")):
            return None
        if isinstance(hint, ODEHint):
            return hint
        try:
            return ODEHint(str(hint))
        except ValueError:
            return None

    def _coerce_pde_hint(self, hint) -> Optional["PDEHint"]:
        """Accept None, PDEHint enum, or hint string. Returns None for 'default' / None."""
        if hint is None or (isinstance(hint, str) and hint.lower() in ("default", "")):
            return None
        if isinstance(hint, PDEHint):
            return hint
        try:
            return PDEHint(str(hint))
        except ValueError:
            return None

    def _coerce_unit_system(self, unit_system) -> Optional["UnitSystem"]:
        """Accept None, UnitSystem enum, or string (case-insensitive)."""
        if unit_system is None:
            return None
        if isinstance(unit_system, UnitSystem):
            return unit_system
        s = str(unit_system)
        # Try exact match first, then case-insensitive
        try:
            return UnitSystem(s)
        except ValueError:
            for member in UnitSystem:
                if member.value.lower() == s.lower() or member.name.lower() == s.lower():
                    return member
            return None

    # ------------------------------------------------------------------
    # Units initialisation
    # ------------------------------------------------------------------

    def initialize_units(self) -> None:
        unit_vars = {
            "meter": meter, "second": second, "kilogram": kilogram,
            "ampere": ampere, "kelvin": kelvin, "mole": mole, "candela": candela,
            "kilometer": kilometer, "millimeter": millimeter, "gram": gram,
            "joule": joule, "newton": newton, "pascal": pascal, "watt": watt,
            "coulomb": coulomb, "volt": volt, "ohm": ohm, "farad": farad,
            "henry": henry, "speed_of_light": speed_of_light,
            "gravitational_constant": gravitational_constant,
            "planck": planck, "day": day, "year": year, "minute": minute, "hour": hour,
        }
        for name, unit in unit_vars.items():
            if unit is not None:
                self.local_vars[name] = unit

    # ------------------------------------------------------------------
    # Symbol & variable management
    # ------------------------------------------------------------------

    def intro(
        self,
        var_name: str,
        pos_assumptions: List[Assumption],
        neg_assumptions: List[Assumption],
    ) -> str:
        kwargs_for_symbols = {}
        for a in pos_assumptions:
            kwargs_for_symbols[a.value if isinstance(a, Assumption) else a] = True
        for a in neg_assumptions:
            kwargs_for_symbols[a.value if isinstance(a, Assumption) else a] = False

        try:
            var = sympy.symbols(var_name, **kwargs_for_symbols)
        except InconsistentAssumptions as e:
            return (
                f"Error creating symbol '{var_name}': The provided assumptions "
                f"{kwargs_for_symbols} are inconsistent according to SymPy. Details: {e}"
            )
        except Exception as e:
            return (
                f"Error creating symbol '{var_name}': An unexpected error occurred. "
                f"Assumptions attempted: {kwargs_for_symbols}. "
                f"Details: {type(e).__name__} - {e}"
            )

        self.local_vars[var_name] = var
        return var_name

    def intro_many(self, variables: List[Any]) -> str:
        var_keys = {}
        for var_def in variables:
            # Support both object-style (with attrs) and list/string style
            if isinstance(var_def, str):
                var_name = var_def
                pos_assumptions: List[Any] = []
                neg_assumptions: List[Any] = []
            elif isinstance(var_def, (list, tuple)):
                var_name = var_def[0]
                pos_assumptions = var_def[1] if len(var_def) > 1 else []
                neg_assumptions = var_def[2] if len(var_def) > 2 else []
            elif isinstance(var_def, dict):
                var_name = var_def["var_name"]
                pos_assumptions = var_def.get("pos_assumptions", [])
                neg_assumptions = var_def.get("neg_assumptions", [])
            else:
                var_name = var_def.var_name
                pos_assumptions = getattr(var_def, "pos_assumptions", [])
                neg_assumptions = getattr(var_def, "neg_assumptions", [])

            # Validate assumption strings against the Assumption enum
            validated_pos: List[Any] = []
            validated_neg: List[Any] = []
            for a in pos_assumptions:
                if isinstance(a, Assumption):
                    validated_pos.append(a)
                else:
                    try:
                        validated_pos.append(Assumption(str(a)))
                    except ValueError as e:
                        msg = f"Error for variable '{var_name}': Invalid assumption '{a}'. {e}"
                        logger.error(msg)
                        return msg
            for a in neg_assumptions:
                if isinstance(a, Assumption):
                    validated_neg.append(a)
                else:
                    try:
                        validated_neg.append(Assumption(str(a)))
                    except ValueError as e:
                        msg = f"Error for variable '{var_name}': Invalid assumption '{a}'. {e}"
                        logger.error(msg)
                        return msg

            var_key = self.intro(var_name, validated_pos, validated_neg)
            var_keys[var_name] = var_key

        return str(var_keys)

    # ------------------------------------------------------------------
    # Expression management
    # ------------------------------------------------------------------

    def introduce_expression(
        self,
        expr_str: str,
        canonicalize: bool = True,
        expr_var_name: Optional[str] = None,
    ) -> str:
        parse_dict = self._parse_dict()
        parsed_expr = parse_expr(expr_str, local_dict=parse_dict, evaluate=canonicalize)
        if expr_var_name is None:
            expr_key = f"expr_{self.expression_counter}"
        else:
            expr_key = expr_var_name
        self.expressions[expr_key] = parsed_expr
        self.expression_counter += 1
        return expr_key

    def introduce_equation(self, lhs_str: str, rhs_str: str) -> str:
        parse_dict = self._parse_dict()
        lhs_expr = parse_expr(lhs_str, local_dict=parse_dict)
        rhs_expr = parse_expr(rhs_str, local_dict=parse_dict)
        eq_key = f"eq_{self.expression_counter}"
        self.expressions[eq_key] = Eq(lhs_expr, rhs_expr)
        self.expression_counter += 1
        return eq_key

    def print_latex_expression(self, expr_key: str) -> str:
        if expr_key not in self.expressions:
            return f"Error: Expression key '{expr_key}' not found."

        expr = self.expressions[expr_key]

        if isinstance(expr, dict):
            if all(isinstance(k, (sympy.Expr, int, float)) for k in expr.keys()):
                parts = []
                for eigenval, multiplicity in expr.items():
                    parts.append(
                        f"{sympy.latex(eigenval)} \\text{{ (multiplicity {multiplicity})}}"
                    )
                return ", ".join(parts)
            return str(expr)

        elif isinstance(expr, list):
            if all(isinstance(item, tuple) and len(item) == 3 for item in expr):
                parts = []
                for eigenval, multiplicity, eigenvects in expr:
                    eigenvects_latex = [sympy.latex(v) for v in eigenvects]
                    parts.append(
                        f"\\lambda = {sympy.latex(eigenval)} \\text{{ (multiplicity {multiplicity})}}:\n"
                        f"\\text{{Eigenvectors: }}[{', '.join(eigenvects_latex)}]"
                    )
                return "\n".join(parts)
            try:
                return str([sympy.latex(item) for item in expr])
            except Exception as e:
                logger.debug(f"Error converting list items to LaTeX: {e}")
                return str(expr)

        latex_str = sympy.latex(expr)

        try:
            variables_in_expr = expr.free_symbols
            assumption_descs = []
            for var_symbol in variables_in_expr:
                var_name = str(var_symbol)
                if var_name in self.local_vars:
                    current_assumptions = []
                    for assumption_enum_member in Assumption:
                        if getattr(var_symbol, f"is_{assumption_enum_member.value}", False):
                            current_assumptions.append(assumption_enum_member.value)
                    if current_assumptions:
                        assumption_descs.append(f"{var_name} is {', '.join(current_assumptions)}")
                    else:
                        assumption_descs.append(f"{var_name} (no specific assumptions listed)")
                else:
                    assumption_descs.append(f"{var_name} (undefined in local_vars)")

            if assumption_descs:
                return f"{latex_str} (where {'; '.join(assumption_descs)})"
            return latex_str
        except AttributeError:
            return latex_str

    def substitute_expression(
        self, expr_key: str, var_name: str, replacement_expr_key: str
    ) -> str:
        if expr_key not in self.expressions:
            return f"Error: Expression with key '{expr_key}' not found."
        if var_name not in self.local_vars:
            return f"Error: Variable '{var_name}' not found. Please introduce it first."
        if replacement_expr_key not in self.expressions:
            return f"Error: Replacement expression with key '{replacement_expr_key}' not found."

        try:
            expr = self.expressions[expr_key]
            var = self.local_vars[var_name]
            replacement = self.expressions[replacement_expr_key]
            result = expr.subs(var, replacement)
            result_key = self._next_expr_key()
            self.expressions[result_key] = result
            return result_key
        except Exception as e:
            return f"Error during substitution: {e}"

    # ------------------------------------------------------------------
    # Algebraic solving
    # ------------------------------------------------------------------

    def solve_algebraically(
        self, expr_key: str, solve_for_var_name: str, domain: Domain = Domain.COMPLEX
    ) -> str:
        domain = self._coerce_domain(domain)
        if expr_key not in self.expressions:
            return f"Error: Expression with key '{expr_key}' not found."
        if solve_for_var_name not in self.local_vars:
            return f"Error: Variable '{solve_for_var_name}' not found in local_vars. Please introduce it first."

        expression_to_solve = self.expressions[expr_key]
        variable_symbol = self.local_vars[solve_for_var_name]

        domain_map = {
            Domain.COMPLEX: sympy.S.Complexes,
            Domain.REAL: sympy.S.Reals,
            Domain.INTEGERS: sympy.S.Integers,
            Domain.NATURALS: sympy.S.Naturals0,
        }
        if domain not in domain_map:
            return "Error: Invalid domain."

        try:
            if isinstance(expression_to_solve, sympy.Eq):
                expression_to_solve = expression_to_solve.lhs - expression_to_solve.rhs
            solution_set = sympy.solveset(
                expression_to_solve, variable_symbol, domain=domain_map[domain]
            )
            return sympy.latex(solution_set)
        except NotImplementedError as e:
            return f"Error: SymPy could not solve the equation: {e}."
        except Exception as e:
            return f"An unexpected error occurred during solving: {e}"

    def solve_linear_system(
        self,
        expr_keys: List[str],
        var_names: List[str],
        domain: Domain = Domain.COMPLEX,
    ) -> str:
        system = []
        for expr_key in expr_keys:
            if expr_key not in self.expressions:
                return f"Error: Expression with key '{expr_key}' not found."
            expr = self.expressions[expr_key]
            if isinstance(expr, sympy.Eq):
                expr = expr.lhs - expr.rhs
            system.append(expr)

        symbols = []
        for var_name in var_names:
            if var_name not in self.local_vars:
                return f"Error: Variable '{var_name}' not found in local_vars."
            symbols.append(self.local_vars[var_name])

        try:
            solution_set = sympy.linsolve(system, symbols)
            return sympy.latex(solution_set)
        except NotImplementedError as e:
            return f"Error: SymPy could not solve the linear system: {e}."
        except ValueError as e:
            return f"Error: Invalid system or arguments: {e}."
        except Exception as e:
            return f"An unexpected error occurred during solving: {e}"

    def solve_nonlinear_system(
        self,
        expr_keys: List[str],
        var_names: List[str],
        domain: Domain = Domain.COMPLEX,
    ) -> str:
        system = []
        for expr_key in expr_keys:
            if expr_key not in self.expressions:
                return f"Error: Expression with key '{expr_key}' not found."
            expr = self.expressions[expr_key]
            if isinstance(expr, sympy.Eq):
                expr = expr.lhs - expr.rhs
            system.append(expr)

        symbols = []
        for var_name in var_names:
            if var_name not in self.local_vars:
                return f"Error: Variable '{var_name}' not found in local_vars."
            symbols.append(self.local_vars[var_name])

        try:
            solution_set = sympy.nonlinsolve(system, symbols)
            return sympy.latex(solution_set)
        except NotImplementedError as e:
            return f"Error: SymPy could not solve the nonlinear system: {e}."
        except ValueError as e:
            return f"Error: Invalid system or arguments: {e}."
        except Exception as e:
            return f"An unexpected error occurred during solving: {e}"

    # ------------------------------------------------------------------
    # Functions & differential equations
    # ------------------------------------------------------------------

    def introduce_function(self, func_name: str) -> str:
        func = Function(func_name)
        self.functions[func_name] = func
        return func_name

    def dsolve_ode(
        self, expr_key: str, func_name: str, hint: Optional[ODEHint] = None
    ) -> str:
        hint = self._coerce_ode_hint(hint)
        if expr_key not in self.expressions:
            return f"Error: Expression with key '{expr_key}' not found."
        if func_name not in self.functions:
            return f"Error: Function '{func_name}' not found. Please introduce it first."

        expression = self.expressions[expr_key]

        try:
            eq = expression if isinstance(expression, sympy.Eq) else sympy.Eq(expression, 0)
            solution = dsolve(eq, hint=hint.value) if hint is not None else dsolve(eq)
            return sympy.latex(solution)
        except ValueError as e:
            return f"Error: {e}. This might be due to an invalid hint or unsupported equation type."
        except NotImplementedError as e:
            return f"Error: Method not implemented: {e}. Try a different hint or equation type."
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def pdsolve_pde(
        self, expr_key: str, func_name: str, hint: Optional[PDEHint] = None
    ) -> str:
        hint = self._coerce_pde_hint(hint)
        if expr_key not in self.expressions:
            return f"Error: Expression with key '{expr_key}' not found."
        if func_name not in self.functions:
            return f"Error: Function '{func_name}' not found. Please introduce it first."

        expression = self.expressions[expr_key]

        try:
            eq = expression if isinstance(expression, sympy.Eq) else sympy.Eq(expression, 0)
            solution = pdsolve(eq, hint=hint.value) if hint is not None else pdsolve(eq)
            return sympy.latex(solution)
        except ValueError as e:
            return f"Error: {e}. This might be due to an unsupported equation type."
        except NotImplementedError as e:
            return f"Error: Method not implemented: {e}."
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    # ------------------------------------------------------------------
    # Calculus
    # ------------------------------------------------------------------

    def simplify_expression(self, expr_key: str) -> str:
        if expr_key not in self.expressions:
            return f"Error: Expression with key '{expr_key}' not found."
        try:
            simplified_expr = simplify(self.expressions[expr_key])
            result_key = self._next_expr_key()
            self.expressions[result_key] = simplified_expr
            return result_key
        except Exception as e:
            return f"Error during simplification: {e}"

    def integrate_expression(
        self,
        expr_key: str,
        var_name: str,
        lower_bound: Optional[str] = None,
        upper_bound: Optional[str] = None,
    ) -> str:
        if expr_key not in self.expressions:
            return f"Error: Expression with key '{expr_key}' not found."
        if var_name not in self.local_vars:
            return f"Error: Variable '{var_name}' not found. Please introduce it first."

        try:
            expr = self.expressions[expr_key]
            var = self.local_vars[var_name]
            bounds = None
            if lower_bound is not None and upper_bound is not None:
                parse_dict = self._parse_dict()
                lower = parse_expr(lower_bound, local_dict=parse_dict)
                upper = parse_expr(upper_bound, local_dict=parse_dict)
                bounds = (var, lower, upper)

            result = integrate(expr, bounds) if bounds else integrate(expr, var)
            result_key = self._next_expr_key()
            self.expressions[result_key] = result
            return result_key
        except Exception as e:
            return f"Error during integration: {e}"

    def differentiate_expression(
        self, expr_key: str, var_name: str, order: int = 1
    ) -> str:
        if expr_key not in self.expressions:
            return f"Error: Expression with key '{expr_key}' not found."
        if var_name not in self.local_vars:
            return f"Error: Variable '{var_name}' not found. Please introduce it first."
        if order < 1:
            return "Error: Order of differentiation must be at least 1."

        try:
            result = diff(self.expressions[expr_key], self.local_vars[var_name], order)
            result_key = self._next_expr_key()
            self.expressions[result_key] = result
            return result_key
        except Exception as e:
            return f"Error during differentiation: {e}"

    # ------------------------------------------------------------------
    # Vector calculus
    # ------------------------------------------------------------------

    def create_coordinate_system(
        self, name: str, coord_names: Optional[List[str]] = None
    ) -> str:
        if name in self.coordinate_systems:
            return f"Warning: Overwriting existing coordinate system '{name}'."

        try:
            if coord_names and len(coord_names) != 3:
                return "Error: coord_names must contain exactly 3 names for x, y, z coordinates."

            cs = CoordSys3D(name, variable_names=coord_names) if coord_names else CoordSys3D(name)
            self.coordinate_systems[name] = cs
            self.expressions[name] = cs

            for i, base_vector in enumerate(cs.base_vectors()):
                vector_name = (
                    f"{name}_{coord_names[i]}" if coord_names else f"{name}_{['x', 'y', 'z'][i]}"
                )
                self.local_vars[vector_name] = base_vector

            return name
        except Exception as e:
            return f"Error creating coordinate system: {e}"

    def create_vector_field(
        self,
        coord_sys_name: str,
        component_x: str,
        component_y: str,
        component_z: str,
    ) -> str:
        if coord_sys_name not in self.coordinate_systems:
            return f"Error: Coordinate system '{coord_sys_name}' not found."

        try:
            cs = self.coordinate_systems[coord_sys_name]
            parse_dict = {**self._parse_dict(), coord_sys_name: cs}
            x_comp = parse_expr(component_x, local_dict=parse_dict)
            y_comp = parse_expr(component_y, local_dict=parse_dict)
            z_comp = parse_expr(component_z, local_dict=parse_dict)

            vector_field = (
                x_comp * cs.base_vectors()[0]
                + y_comp * cs.base_vectors()[1]
                + z_comp * cs.base_vectors()[2]
            )
            result_key = self._next_vector_key()
            self.expressions[result_key] = vector_field
            return result_key
        except Exception as e:
            return f"Error creating vector field: {e}"

    def calculate_curl(self, vector_field_key: str) -> str:
        if vector_field_key not in self.expressions:
            return f"Error: Vector field with key '{vector_field_key}' not found."
        try:
            curl_result = curl(self.expressions[vector_field_key])
            result_key = self._next_vector_key()
            self.expressions[result_key] = curl_result
            return result_key
        except Exception as e:
            return f"Error calculating curl: {e}"

    def calculate_divergence(self, vector_field_key: str) -> str:
        if vector_field_key not in self.expressions:
            return f"Error: Vector field with key '{vector_field_key}' not found."
        try:
            div_result = divergence(self.expressions[vector_field_key])
            result_key = self._next_expr_key()
            self.expressions[result_key] = div_result
            return result_key
        except Exception as e:
            return f"Error calculating divergence: {e}"

    def calculate_gradient(self, scalar_field_key: str) -> str:
        if scalar_field_key not in self.expressions:
            return f"Error: Scalar field with key '{scalar_field_key}' not found."
        try:
            grad_result = gradient(self.expressions[scalar_field_key])
            result_key = self._next_vector_key()
            self.expressions[result_key] = grad_result
            return result_key
        except Exception as e:
            return f"Error calculating gradient: {e}"

    # ------------------------------------------------------------------
    # Unit conversion
    # ------------------------------------------------------------------

    def convert_to_units(
        self,
        expr_key: str,
        target_units: List[str],
        unit_system: Optional[UnitSystem] = None,
    ) -> str:
        unit_system = self._coerce_unit_system(unit_system)
        if expr_key not in self.expressions:
            return f"Error: Expression with key '{expr_key}' not found."

        expr = self.expressions[expr_key]
        if unit_system is not None and unit_system.value.lower() == "cgs":
            system = cgs_gauss
        else:
            system = {
                None: SI, UnitSystem.SI: SI, UnitSystem.MKS: MKS,
                UnitSystem.MKSA: MKSA, UnitSystem.NATURAL: natural,
            }.get(unit_system, SI)

        try:
            target_unit_objs = []
            for unit_str in target_units:
                if unit_str == "not_a_unit":
                    return f"Error: Unit '{unit_str}' not found in sympy.physics.units."
                if unit_str in units_dict:
                    target_unit_objs.append(units_dict[unit_str])
                else:
                    try:
                        unit_obj = parse_expr(unit_str, local_dict=units_dict)
                        target_unit_objs.append(unit_obj)
                    except Exception as e:
                        return f"Error: Unit '{unit_str}' could not be parsed: {e}"

            result = convert_to(expr, target_unit_objs, system)
            result_key = self._next_expr_key()
            self.expressions[result_key] = result
            return result_key
        except Exception as e:
            return f"Error during unit conversion: {e}"

    def quantity_simplify_units(
        self, expr_key: str, unit_system: Optional[UnitSystem] = None
    ) -> str:
        unit_system = self._coerce_unit_system(unit_system)
        if expr_key not in self.expressions:
            return f"Error: Expression with key '{expr_key}' not found."
        try:
            result = self.expressions[expr_key].simplify()
            result_key = self._next_expr_key()
            self.expressions[result_key] = result
            return result_key
        except Exception as e:
            return f"Error during quantity simplification: {e}"

    # ------------------------------------------------------------------
    # Linear algebra / matrices
    # ------------------------------------------------------------------

    def create_matrix(
        self,
        matrix_data: List[List[Union[int, float, str]]],
        matrix_var_name: Optional[str] = None,
    ) -> str:
        try:
            parse_dict = self._parse_dict()
            processed_data = []
            for row in matrix_data:
                processed_row = []
                for elem in row:
                    if isinstance(elem, (int, float)):
                        processed_row.append(elem)
                    else:
                        processed_row.append(parse_expr(str(elem), local_dict=parse_dict))
                processed_data.append(processed_row)

            matrix = Matrix(processed_data)
            if matrix_var_name is None:
                matrix_key = self._next_matrix_key()
            else:
                matrix_key = matrix_var_name
            self.expressions[matrix_key] = matrix
            return matrix_key
        except Exception as e:
            return f"Error creating matrix: {e}"

    def matrix_determinant(self, matrix_key: str) -> str:
        if matrix_key not in self.expressions:
            return f"Error: Matrix with key '{matrix_key}' not found."
        try:
            matrix = self.expressions[matrix_key]
            if not isinstance(matrix, Matrix):
                return f"Error: '{matrix_key}' is not a matrix."
            det = matrix.det()
            result_key = self._next_expr_key()
            self.expressions[result_key] = det
            return result_key
        except Exception as e:
            return f"Error calculating determinant: {e}"

    def matrix_inverse(self, matrix_key: str) -> str:
        if matrix_key not in self.expressions:
            return f"Error: Matrix with key '{matrix_key}' not found."
        try:
            matrix = self.expressions[matrix_key]
            if not isinstance(matrix, Matrix):
                return f"Error: '{matrix_key}' is not a matrix."
            inv = matrix.inv()
            result_key = self._next_matrix_key()
            self.expressions[result_key] = inv
            return result_key
        except Exception as e:
            return f"Error calculating inverse: {e}"

    def matrix_eigenvalues(self, matrix_key: str) -> str:
        if matrix_key not in self.expressions:
            return f"Error: Matrix with key '{matrix_key}' not found."
        try:
            matrix = self.expressions[matrix_key]
            if not isinstance(matrix, Matrix):
                return f"Error: '{matrix_key}' is not a matrix."
            eigenvals = matrix.eigenvals()
            result_key = self._next_expr_key()
            self.expressions[result_key] = eigenvals
            return result_key
        except Exception as e:
            return f"Error calculating eigenvalues: {e}"

    def matrix_eigenvectors(self, matrix_key: str) -> str:
        if matrix_key not in self.expressions:
            return f"Error: Matrix with key '{matrix_key}' not found."
        try:
            matrix = self.expressions[matrix_key]
            if not isinstance(matrix, Matrix):
                return f"Error: '{matrix_key}' is not a matrix."
            eigenvects = matrix.eigenvects()
            result_key = self._next_expr_key()
            self.expressions[result_key] = eigenvects
            return result_key
        except Exception as e:
            return f"Error calculating eigenvectors: {e}"

    # ------------------------------------------------------------------
    # Relativity (einsteinpy)
    # ------------------------------------------------------------------

    def create_predefined_metric(self, metric_name: str) -> str:
        if not EINSTEINPY_AVAILABLE:
            return "Error: EinsteinPy library is not available. Please install it with 'pip install einsteinpy'."

        try:
            if isinstance(metric_name, Metric):
                metric_enum = metric_name
            else:
                metric_enum = None
                for metric in Metric:
                    if metric.value.lower() == metric_name.lower():
                        metric_enum = metric
                        break
                if metric_enum is None:
                    try:
                        metric_enum = Metric[metric_name.upper()]
                    except KeyError:
                        normalized = "".join(c.upper() for c in metric_name if c.isalnum())
                        for m in Metric:
                            if "".join(c for c in m.name if c.isalnum()) == normalized:
                                metric_enum = m
                                break

            if metric_enum is None:
                return f"Error: Invalid metric name '{metric_name}'. Available: {', '.join(m.value for m in Metric)}"

            metric_map = {
                Metric.SCHWARZSCHILD: Schwarzschild,
                Metric.MINKOWSKI: Minkowski,
                Metric.MINKOWSKI_CARTESIAN: MinkowskiCartesian,
                Metric.KERR_NEWMAN: KerrNewman,
                Metric.KERR: Kerr,
                Metric.ANTI_DE_SITTER: AntiDeSitter,
                Metric.DE_SITTER: DeSitter,
                Metric.REISSNER_NORDSTROM: ReissnerNordstorm,
            }

            if metric_enum not in metric_map:
                return f"Error: Metric '{metric_enum.value}' not implemented."

            metric_obj = metric_map[metric_enum]()
            metric_key = f"metric_{metric_enum.value}"
            self.metrics[metric_key] = metric_obj
            self.expressions[metric_key] = metric_obj.tensor()
            return metric_key
        except Exception as e:
            return f"Error creating metric: {e}"

    def search_predefined_metrics(self, query: str) -> str:
        if not EINSTEINPY_AVAILABLE:
            return "Error: EinsteinPy library is not available."
        try:
            results = find(query)
            if not results:
                return f"No metrics found matching '{query}'."
            return f"Found metrics: {', '.join(results)}"
        except Exception as e:
            return f"Error searching for metrics: {e}"

    def calculate_tensor(
        self, metric_key: str, tensor_type: str, simplify_result: bool = True
    ) -> str:
        if not EINSTEINPY_AVAILABLE:
            return "Error: EinsteinPy library is not available."
        if metric_key not in self.metrics:
            return f"Error: Metric key '{metric_key}' not found."

        metric_obj = self.metrics[metric_key]
        tensor_enum = None
        try:
            if isinstance(tensor_type, Tensor):
                tensor_enum = tensor_type
            else:
                for t in Tensor:
                    if t.value.lower() == tensor_type.lower():
                        tensor_enum = t
                        break
                if tensor_enum is None:
                    try:
                        tensor_enum = Tensor[tensor_type.upper()]
                    except KeyError:
                        normalized = "".join(c.upper() for c in tensor_type if c.isalnum())
                        for t in Tensor:
                            if "".join(c for c in t.name if c.isalnum()) == normalized:
                                tensor_enum = t
                                break
            if tensor_enum is None:
                return f"Error: Invalid tensor type '{tensor_type}'. Available: {', '.join(t.value for t in Tensor)}"
        except Exception as e:
            return f"Error parsing tensor type: {e}"

        tensor_map = {
            Tensor.RICCI_TENSOR: RicciTensor,
            Tensor.RICCI_SCALAR: RicciScalar,
            Tensor.EINSTEIN_TENSOR: EinsteinTensor,
            Tensor.WEYL_TENSOR: WeylTensor,
            Tensor.RIEMANN_CURVATURE_TENSOR: ChristoffelSymbols,
            Tensor.STRESS_ENERGY_MOMENTUM_TENSOR: StressEnergyMomentumTensor,
        }

        try:
            if tensor_enum not in tensor_map:
                return f"Error: Tensor type '{tensor_enum.value}' not implemented."

            tensor_class = tensor_map[tensor_enum]
            if tensor_enum == Tensor.RICCI_SCALAR:
                ricci_tensor = RicciTensor.from_metric(metric_obj)
                tensor_obj = RicciScalar.from_riccitensor(ricci_tensor)
            else:
                tensor_obj = tensor_class.from_metric(metric_obj)

            tensor_key = f"{tensor_enum.value.lower()}_{metric_key}"
            self.tensor_objects[tensor_key] = tensor_obj

            if tensor_enum == Tensor.RICCI_SCALAR:
                tensor_expr = tensor_obj.expr
                if simplify_result:
                    tensor_expr = sympy.simplify(tensor_expr)
                self.expressions[tensor_key] = tensor_expr
            else:
                self.expressions[tensor_key] = tensor_obj.tensor()

            return tensor_key
        except Exception as e:
            return f"Error calculating tensor: {e}"

    def create_custom_metric(
        self,
        components: List[List[str]],
        symbols: List[str],
        config: Literal["ll", "uu"] = "ll",
    ) -> str:
        if not EINSTEINPY_AVAILABLE:
            return "Error: EinsteinPy library is not available."
        try:
            sympy_symbols = sympy.symbols(", ".join(symbols))
            sympy_symbols_dict = {str(sym): sym for sym in sympy_symbols}

            sympy_components = []
            for row in components:
                sympy_row = []
                for expr_str in row:
                    if expr_str == "0":
                        sympy_row.append(0)
                    else:
                        sympy_row.append(parse_expr(expr_str, local_dict=sympy_symbols_dict))
                sympy_components.append(sympy_row)

            metric_obj = MetricTensor(sympy_components, sympy_symbols, config=config)
            metric_key = f"metric_custom_{self.expression_counter}"
            self.metrics[metric_key] = metric_obj
            self.expressions[metric_key] = metric_obj.tensor()
            self.expression_counter += 1
            return metric_key
        except Exception as e:
            return f"Error creating custom metric: {e}"

    def print_latex_tensor(self, tensor_key: str) -> str:
        if tensor_key not in self.expressions:
            return f"Error: Tensor key '{tensor_key}' not found."
        try:
            return sympy.latex(self.expressions[tensor_key])
        except Exception as e:
            return f"Error generating LaTeX: {e}"

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def reset_state(self) -> str:
        self.local_vars.clear()
        self.functions.clear()
        self.expressions.clear()
        self.metrics.clear()
        self.tensor_objects.clear()
        self.coordinate_systems.clear()
        self.expression_counter = 0
        self.initialize_units()
        return "State reset successfully. All variables, functions, expressions, and other objects have been cleared."
