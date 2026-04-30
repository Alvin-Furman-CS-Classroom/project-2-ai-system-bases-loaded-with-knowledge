"""
Generic CSP solver: backtracking with MRV, forward checking, optional LCV,
and branch-and-bound for additive objectives.

Used by ``position_assignment.assign_defensive_positions`` for Module 3.
"""

from __future__ import annotations

import copy
from typing import Callable, Dict, Hashable, List, Mapping, Optional, Sequence, Set, Tuple

Variable = Hashable
Value = Hashable
Assignment = Dict[Variable, Value]
Domains = Dict[Variable, List[Value]]
ContributionFn = Callable[[Variable, Value], float]
PartialConstraintFn = Callable[[Assignment], bool]


def _deepcopy_domains(domains: Mapping[Variable, Sequence[Value]]) -> Domains:
    return {v: list(vals) for v, vals in domains.items()}


def _apply_locked(
    variables: Sequence[Variable],
    domains: Domains,
    locked: Mapping[Variable, Value],
    all_different: bool,
) -> Tuple[Optional[Assignment], Domains]:
    assignment: Assignment = {}
    dom = _deepcopy_domains(domains)

    for var, val in locked.items():
        if var not in dom:
            raise KeyError(f"locked variable {var!r} not in domains")
        if val not in dom[var]:
            return None, dom
        assignment[var] = val
        dom[var] = [val]
        if all_different:
            for other in variables:
                if other == var:
                    continue
                if val in dom[other]:
                    dom[other] = [x for x in dom[other] if x != val]
                if not dom[other]:
                    return None, dom

    return assignment, dom


def _mrv_variable(unassigned: Set[Variable], domains: Domains) -> Variable:
    return min(unassigned, key=lambda v: (len(domains[v]), str(v)))


def _lcv_order_values(
    var: Variable,
    domain: List[Value],
    unassigned: Set[Variable],
    domains: Domains,
    all_different: bool,
) -> List[Value]:
    if len(domain) <= 1:
        return list(domain)

    def flexibility(val: Value) -> Tuple[int, str]:
        total = 0
        for other in unassigned:
            if other == var:
                continue
            d = domains[other]
            if all_different:
                total += len([x for x in d if x != val])
            else:
                total += len(d)
        return (total, str(val))

    return sorted(domain, key=lambda v: (-flexibility(v)[0], flexibility(v)[1]))


def _upper_bound_additive(
    partial_score: float,
    unassigned: Set[Variable],
    domains: Domains,
    contribution: ContributionFn,
) -> float:
    ub = partial_score
    for v in unassigned:
        vals = domains.get(v, [])
        if not vals:
            return float("-inf")
        ub += max(contribution(v, x) for x in vals)
    return ub


def _assign_and_forward_check(
    var: Variable,
    val: Value,
    dom_state: Domains,
    variables: Sequence[Variable],
    all_different: bool,
    unassigned: Set[Variable],
) -> Optional[Domains]:
    """
    Deep-copy domains, set ``var`` to ``val``, remove ``val`` from other variables if
    ``all_different``. Return ``None`` if any still-unassigned variable has an empty domain.
    """
    new_dom = copy.deepcopy(dom_state)
    new_dom[var] = [val]
    if all_different:
        for other in variables:
            if other == var:
                continue
            if val in new_dom[other]:
                new_dom[other] = [x for x in new_dom[other] if x != val]

    new_unassigned = set(unassigned)
    new_unassigned.discard(var)
    if any(len(new_dom[u]) == 0 for u in new_unassigned):
        return None
    return new_dom


class _BestAssignmentTracker:
    """Holds the best complete assignment found so far (maximize score)."""

    __slots__ = ("score", "assignment")

    def __init__(self) -> None:
        self.score: float = float("-inf")
        self.assignment: Optional[Assignment] = None

    def record_if_better(self, partial_score: float, assign: Assignment) -> None:
        if partial_score > self.score:
            self.score = partial_score
            self.assignment = assign.copy()


def _recursive_search_maximize(
    variables: Sequence[Variable],
    contribution: ContributionFn,
    all_different: bool,
    use_lcv: bool,
    use_branch_bound: bool,
    partial_ok: Callable[[Assignment], bool],
    assign: Assignment,
    dom_state: Domains,
    unassigned: Set[Variable],
    partial_score: float,
    best: _BestAssignmentTracker,
) -> None:
    """
    Depth-first search with MRV variable order, optional LCV value order,
    forward checking, and branch-and-bound pruning.
    """
    if use_branch_bound:
        ub = _upper_bound_additive(partial_score, unassigned, dom_state, contribution)
        if ub < best.score:
            return

    if not unassigned:
        best.record_if_better(partial_score, assign)
        return

    var = _mrv_variable(unassigned, dom_state)
    vals = list(dom_state[var])
    if not vals:
        return

    ordered_vals = (
        _lcv_order_values(var, vals, unassigned, dom_state, all_different)
        if use_lcv
        else sorted(vals, key=str)
    )

    for val in ordered_vals:
        if val not in dom_state[var]:
            continue

        new_assign = dict(assign)
        new_assign[var] = val
        if not partial_ok(new_assign):
            continue

        new_score = partial_score + contribution(var, val)
        new_dom = _assign_and_forward_check(
            var, val, dom_state, variables, all_different, unassigned
        )
        if new_dom is None:
            continue

        new_unassigned = set(unassigned)
        new_unassigned.remove(var)

        _recursive_search_maximize(
            variables,
            contribution,
            all_different,
            use_lcv,
            use_branch_bound,
            partial_ok,
            new_assign,
            new_dom,
            new_unassigned,
            new_score,
            best,
        )


def solve_max_csp(
    variables: Sequence[Variable],
    domains: Mapping[Variable, Sequence[Value]],
    contribution: ContributionFn,
    *,
    all_different: bool = True,
    locked: Optional[Mapping[Variable, Value]] = None,
    partial_constraint: Optional[PartialConstraintFn] = None,
    use_lcv: bool = True,
    use_branch_bound: bool = True,
) -> Optional[Assignment]:
    """
    Find a complete assignment maximizing sum(contribution(var, assignment[var])).

    Args:
        variables: CSP variables (e.g. positions), in stable iteration order.
        domains: Allowed values per variable (e.g. eligible players).
        contribution: Additive score for assigning ``value`` to ``variable``.
        all_different: If True, each value used at most once.
        locked: Pre-fixed assignments before search.
        partial_constraint: Optional predicate on partial assignment dict.
        use_lcv: Order values with least-constraining-value heuristic.
        use_branch_bound: Prune when optimistic upper bound cannot beat best score.

    Returns:
        Best assignment dict, or None if unsatisfiable / inconsistent locks.
    """
    var_set = set(variables)
    if len(var_set) != len(variables):
        raise ValueError("variables must be unique")

    for v in variables:
        if v not in domains:
            raise KeyError(f"variable {v!r} missing from domains")

    locked = locked or {}
    initial_partial, dom = _apply_locked(list(variables), _deepcopy_domains(domains), locked, all_different)
    if initial_partial is None:
        return None

    assignment: Assignment = dict(initial_partial)

    def partial_ok(assign: Assignment) -> bool:
        if partial_constraint is not None and not partial_constraint(assign):
            return False
        return True

    if not partial_ok(assignment):
        return None

    unassigned_start = set(variables) - set(assignment.keys())
    initial_score = sum(contribution(v, assignment[v]) for v in assignment)

    best = _BestAssignmentTracker()
    _recursive_search_maximize(
        variables,
        contribution,
        all_different,
        use_lcv,
        use_branch_bound,
        partial_ok,
        assignment,
        dom,
        unassigned_start,
        initial_score,
        best,
    )

    return best.assignment


__all__ = ["solve_max_csp"]
