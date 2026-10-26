"""
Tensor calculus on component arrays for the relativity tools.

A tensor is a SymPy Array plus an index configuration string such as "ulll"
('u' = contravariant, 'l' = covariant), in the coordinate order of its
metric. Covariant derivatives append the derivative index last:
(nabla T)[..., c] = nabla_c T[...].
"""

import itertools
from typing import Any, List, Sequence, Tuple

import sympy
from einsteinpy.symbolic import ChristoffelSymbols, RiemannCurvatureTensor


class TensorError(ValueError):
    pass


def _get(arr: Any, idx: Tuple[int, ...]) -> Any:
    return arr[idx] if idx else arr[()]


def _array(values: dict, shape: Tuple[int, ...]) -> sympy.Array:
    if not shape:
        return sympy.Array(values[()])
    flat = [values[idx] for idx in itertools.product(*(range(n) for n in shape))]
    return sympy.Array(flat, shape)


def simplify_array(arr: sympy.Array) -> sympy.Array:
    return arr.applyfunc(sympy.simplify)


def metric_arrays(metric: Any) -> Tuple[sympy.Array, sympy.Array]:
    """(g_ab, g^ab) of an einsteinpy MetricTensor, whatever its own config."""
    if metric.config == "ll":
        return metric.tensor(), metric.inv().tensor()
    return metric.inv().tensor(), metric.tensor()


def christoffel(metric: Any) -> sympy.Array:
    """Gamma^a_bc (config 'ull')."""
    return ChristoffelSymbols.from_metric(metric).tensor()


def covariant_derivative(arr: Any, config: str, metric: Any) -> Tuple[sympy.Array, str]:
    """nabla_c T, with c appended as the last (covariant) index."""
    syms = metric.syms
    n = len(syms)
    gamma = christoffel(metric)
    rank = len(config)
    values = {}
    for idx in itertools.product(range(n), repeat=rank):
        for c in range(n):
            term = sympy.diff(_get(arr, idx), syms[c])
            for pos, kind in enumerate(config):
                for d in range(n):
                    swapped = idx[:pos] + (d,) + idx[pos + 1:]
                    if kind == "u":
                        term += gamma[idx[pos], c, d] * _get(arr, swapped)
                    else:
                        term -= gamma[d, c, idx[pos]] * _get(arr, swapped)
            values[idx + (c,)] = term
    return _array(values, (n,) * (rank + 1)), config + "l"


def change_index(arr: Any, config: str, index: int, metric: Any, to: str) -> Tuple[sympy.Array, str]:
    """Raise (to='u') or lower (to='l') one index with the metric."""
    if not 0 <= index < len(config):
        raise TensorError(f"Index {index} is out of range for a rank-{len(config)} tensor.")
    if config[index] == to:
        raise TensorError(f"Index {index} is already {'upper' if to == 'u' else 'lower'}.")
    g_ll, g_uu = metric_arrays(metric)
    g = g_uu if to == "u" else g_ll
    n = len(metric.syms)
    rank = len(config)
    values = {}
    for idx in itertools.product(range(n), repeat=rank):
        values[idx] = sum(
            g[idx[index], d] * _get(arr, idx[:index] + (d,) + idx[index + 1:]) for d in range(n)
        )
    return _array(values, (n,) * rank), config[:index] + to + config[index + 1:]


def contract(arr: Any, config: str, i: int, j: int, metric: Any) -> Tuple[Any, str]:
    """Contract index i with index j, raising one of them first if both have the same position."""
    rank = len(config)
    if i == j or not (0 <= i < rank and 0 <= j < rank):
        raise TensorError(f"Cannot contract indices {i} and {j} of a rank-{rank} tensor.")
    if config[i] == config[j]:
        arr, config = change_index(arr, config, i, metric, "l" if config[i] == "u" else "u")
    n = len(metric.syms)
    keep = [p for p in range(rank) if p not in (i, j)]
    values = {}
    for free in itertools.product(range(n), repeat=len(keep)):
        total = 0
        for d in range(n):
            idx = [0] * rank
            for p, v in zip(keep, free):
                idx[p] = v
            idx[i] = idx[j] = d
            total += _get(arr, tuple(idx))
        values[free] = total
    new_config = "".join(config[p] for p in keep)
    if not keep:
        return values[()], ""
    return _array(values, (n,) * len(keep)), new_config


def divergence(arr: Any, config: str, index: int, metric: Any) -> Tuple[Any, str]:
    """nabla_a T^{..a..}: contract `index` with the derivative index."""
    derivative, d_config = covariant_derivative(arr, config, metric)
    return contract(derivative, d_config, index, len(config), metric)


def kretschmann(metric: Any) -> Any:
    """R_abcd R^abcd."""
    riemann = RiemannCurvatureTensor.from_metric(metric)
    arr, config = riemann.tensor(), riemann.config  # 'ulll'
    lower, _ = change_index(arr, config, 0, metric, "l")
    upper = lower
    up_config = "llll"
    for index in range(4):
        upper, up_config = change_index(upper, up_config, index, metric, "u")
    n = len(metric.syms)
    return sum(
        lower[idx] * upper[idx] for idx in itertools.product(range(n), repeat=4)
    )


def killing_tensor(vector: Sequence[Any], config: str, metric: Any) -> sympy.Array:
    """nabla_(a xi_b) = (nabla_a xi_b + nabla_b xi_a) / 2, config 'll'."""
    arr = sympy.Array(list(vector))
    if config == "u":
        arr, config = change_index(arr, "u", 0, metric, "l")
    derivative, _ = covariant_derivative(arr, "l", metric)  # [b, a] = nabla_a xi_b
    n = len(metric.syms)
    values = {
        (a, b): (derivative[b, a] + derivative[a, b]) / 2
        for a, b in itertools.product(range(n), repeat=2)
    }
    return _array(values, (n, n))


def component_indices(indices: Sequence[Any], syms: Sequence[Any]) -> Tuple[int, ...]:
    """Map a mix of integer positions and coordinate names to integer positions."""
    names: List[str] = [str(s) for s in syms]
    result = []
    for item in indices:
        if isinstance(item, int) or (isinstance(item, str) and item.lstrip("-").isdigit()):
            position = int(item)
        elif item in names:
            position = names.index(item)
        else:
            raise TensorError(f"'{item}' is not an index position or one of the coordinates {names}.")
        if not 0 <= position < len(names):
            raise TensorError(f"Index {position} is out of range for {len(names)} coordinates.")
        result.append(position)
    return tuple(result)
