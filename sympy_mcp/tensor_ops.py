"""
Session operations for the tensor-calculus tools.

Each function takes the SymPyState, resolves its operands (stored metrics
and tensors), runs the array math in tensor_calculus, and stores the result.
Tensor results are stored under "tensor_N" (as an einsteinpy
BaseRelativityTensor plus its component array); scalar results under "expr_N".
"""

from typing import TYPE_CHECKING, Any, List, Optional, Tuple

import sympy
from einsteinpy.symbolic import BaseRelativityTensor

from sympy_mcp import tensor_calculus as tc
from sympy_mcp.operations import guard
from sympy_mcp.results import StoredResult

if TYPE_CHECKING:
    from sympy_mcp.state import SymPyState


def _metric(state: "SymPyState", metric_key: str) -> Any:
    if metric_key not in state.metrics:
        raise tc.TensorError(f"Metric key '{metric_key}' not found.")
    return state.metrics[metric_key]


def _operand(state: "SymPyState", tensor_key: str, metric_key: Optional[str]) -> Tuple[Any, str, Any]:
    """(components, config, metric) for a stored metric or tensor."""
    if tensor_key in state.metrics:
        obj = state.metrics[tensor_key]
        parent = obj
    elif tensor_key in state.tensor_objects:
        obj = state.tensor_objects[tensor_key]
        if type(obj).__name__ == "ChristoffelSymbols":
            raise tc.TensorError(
                "Christoffel symbols are not a tensor, so tensor operations don't apply to them."
            )
        if obj.order == 0:
            raise tc.TensorError(f"'{tensor_key}' is a scalar; it has no indices.")
        parent = obj.parent_metric
    else:
        raise tc.TensorError(f"Tensor key '{tensor_key}' not found.")
    metric = _metric(state, metric_key) if metric_key is not None else parent
    if metric is None:
        raise tc.TensorError(f"'{tensor_key}' has no associated metric; pass metric_key.")
    return obj.tensor(), obj.config, metric


def _store_tensor(
    state: "SymPyState", arr: Any, config: str, metric: Any, name: str, simplify: bool
) -> StoredResult:
    if not config:
        return _store_scalar(state, arr, simplify)
    if simplify:
        arr = tc.simplify_array(arr)
    key = f"tensor_{state.expression_counter}"
    state.expression_counter += 1
    state.tensor_objects[key] = BaseRelativityTensor(
        arr, metric.syms, config=config, parent_metric=metric, name=name
    )
    state.expressions[key] = arr
    return state._result(key, config=config)


def _store_scalar(state: "SymPyState", value: Any, simplify: bool) -> StoredResult:
    if isinstance(value, sympy.NDimArray):
        value = value[()]
    if simplify:
        value = sympy.simplify(value)
    return state._result(state._store(value))


@guard("during tensor computation")
def create_tensor(state, metric_key: str, components: Any, config: str):
    metric = _metric(state, metric_key)
    if not config or set(config) - {"u", "l"}:
        raise tc.TensorError("config must be a string of 'u' (upper) and 'l' (lower), one letter per index.")
    n = len(metric.syms)
    coords = {str(s): s for s in metric.syms}

    def parse(item: Any, depth: int) -> Any:
        if depth == len(config):
            if isinstance(item, list):
                raise tc.TensorError(f"Components are nested deeper than the {len(config)} indices in config.")
            return state._parse(str(item), extra=coords)
        if not isinstance(item, list) or len(item) != n:
            raise tc.TensorError(
                f"Each index needs {n} entries (one per coordinate {list(metric.syms)}); "
                f"check the nesting of components against config '{config}'."
            )
        return [parse(sub, depth + 1) for sub in item]

    arr = sympy.Array(parse(components, 0))
    return _store_tensor(state, arr, config, metric, "Tensor", simplify=False)


@guard("during tensor computation")
def covariant_derivative(state, tensor_key: str, metric_key: Optional[str], simplify: bool):
    arr, config, metric = _operand(state, tensor_key, metric_key)
    result, new_config = tc.covariant_derivative(arr, config, metric)
    return _store_tensor(state, result, new_config, metric, f"nabla {tensor_key}", simplify)


@guard("during tensor computation")
def divergence(state, tensor_key: str, index: int, metric_key: Optional[str], simplify: bool):
    arr, config, metric = _operand(state, tensor_key, metric_key)
    if not 0 <= index < len(config):
        raise tc.TensorError(f"Index {index} is out of range for a rank-{len(config)} tensor.")
    result, new_config = tc.divergence(arr, config, index, metric)
    return _store_tensor(state, result, new_config, metric, f"div {tensor_key}", simplify)


@guard("during tensor computation")
def contract(state, tensor_key: str, index_a: int, index_b: int, metric_key: Optional[str], simplify: bool):
    arr, config, metric = _operand(state, tensor_key, metric_key)
    result, new_config = tc.contract(arr, config, index_a, index_b, metric)
    return _store_tensor(state, result, new_config, metric, f"contracted {tensor_key}", simplify)


@guard("during tensor computation")
def change_index(state, tensor_key: str, index: int, to: str, metric_key: Optional[str], simplify: bool):
    arr, config, metric = _operand(state, tensor_key, metric_key)
    result, new_config = tc.change_index(arr, config, index, metric, to)
    return _store_tensor(state, result, new_config, metric, f"{tensor_key} ({new_config})", simplify)


@guard("during tensor computation")
def tensor_component(state, tensor_key: str, indices: List[Any], simplify: bool):
    if tensor_key not in state.expressions:
        raise tc.TensorError(f"Tensor key '{tensor_key}' not found.")
    arr = state.expressions[tensor_key]
    if tensor_key in state.metrics:
        syms = state.metrics[tensor_key].syms
    elif tensor_key in state.tensor_objects:
        syms = state.tensor_objects[tensor_key].syms
    else:
        syms = [str(i) for i in range(arr.shape[0])] if getattr(arr, "shape", None) else []
    if not isinstance(arr, sympy.NDimArray):
        raise tc.TensorError(f"'{tensor_key}' is not a tensor or array.")
    position = tc.component_indices(indices, syms)
    if len(position) != arr.rank():
        raise tc.TensorError(f"'{tensor_key}' has rank {arr.rank()}; got {len(position)} indices.")
    return _store_scalar(state, arr[position], simplify)


@guard("during tensor computation")
def kretschmann_scalar(state, metric_key: str, simplify: bool):
    return _store_scalar(state, tc.kretschmann(_metric(state, metric_key)), simplify)


@guard("during tensor computation")
def killing_equation(state, metric_key: str, vector: List[str], vector_config: str, simplify: bool):
    metric = _metric(state, metric_key)
    if vector_config not in ("u", "l"):
        raise tc.TensorError("vector_config must be 'u' (components xi^a) or 'l' (components xi_a).")
    if len(vector) != len(metric.syms):
        raise tc.TensorError(
            f"The vector needs {len(metric.syms)} components, one per coordinate {list(metric.syms)}."
        )
    coords = {str(s): s for s in metric.syms}
    components = [state._parse(str(c), extra=coords) for c in vector]
    arr = tc.killing_tensor(components, vector_config, metric)
    if simplify:
        arr = tc.simplify_array(arr)
    if all(c == 0 for c in sympy.flatten(arr.tolist())):
        satisfied: Optional[bool] = True
    else:
        # Without simplification a nonzero-looking component may still be zero
        satisfied = False if simplify else None
    result = _store_tensor(state, arr, "ll", metric, "Killing equation", simplify=False)
    result.extras["satisfied"] = satisfied
    return result
