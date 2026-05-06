"""No-legacy-helper AST guard (PROJ-368 Phase 4 Task 4.11).

After Phase 4, every legacy private helper that lived on `OrderProcessor`
must be deleted -- their copies live on the per-OrderType handlers in
`game/strategy/engine/order_handlers/`. Failing this test BLOCKS
Phase 4 sign-off.
"""
from __future__ import annotations

import ast
import pathlib

ORDER_PROCESSOR = (
    pathlib.Path(__file__).resolve().parents[4]
    / "game"
    / "strategy"
    / "engine"
    / "order_processor.py"
)


def test_no_legacy_private_helpers_on_order_processor():
    tree = ast.parse(ORDER_PROCESSOR.read_text(encoding="utf-8"))
    forbidden = {
        "_execute_fleet_merge",
        "_execute_fleet_transfer",
        "_execute_load",
        "_execute_unload",
        "_load_pod_from_staging_yard",
        "_unload_pod_to_staging_yard",
        "_deploy_drop_pod",
        "_validate_tick_inputs",
        "_elect_canonical_merges",
        "_emit_join_cancelled",
    }
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in forbidden:
            offenders.append(node.name)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("_process_"):
            offenders.append(node.name)
    assert not offenders, (
        f"Legacy private helpers must be deleted from OrderProcessor: {offenders}"
    )


def test_order_processor_facade_under_200_loc():
    """The facade target is < 200 LOC."""
    loc = len(ORDER_PROCESSOR.read_text(encoding="utf-8").splitlines())
    assert loc < 200, (
        f"order_processor.py is {loc} LOC; PROJ-368 facade target is < 200"
    )


def test_no_order_type_branching_in_facade():
    """Facade should reference OrderType only for the registry lookup.

    PROJ-368 invariant: no `if order.type == OrderType.X` ladders or
    `order.type in (OrderType.X, ...)` conditionals in the facade. The
    only allowed OrderType references are the handful of explicit
    member accesses (e.g. `OrderType.JOIN_FLEET` in delegating method
    bodies) and the `in (...)` validation in `process_transfer`.

    The looser constraint here counts `Compare` AST nodes -- the facade
    must contain ZERO `if order.type == OrderType.<name>` comparisons.
    """
    tree = ast.parse(ORDER_PROCESSOR.read_text(encoding="utf-8"))
    bad_compares = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        # Look for `order.type == OrderType.<member>` patterns.
        for cmp_op, cmp in zip(node.ops, node.comparators):
            if not isinstance(cmp_op, ast.Eq):
                continue
            if (
                isinstance(cmp, ast.Attribute)
                and isinstance(cmp.value, ast.Name)
                and cmp.value.id == "OrderType"
            ):
                bad_compares.append(ast.unparse(node))
    assert not bad_compares, (
        f"Facade must not branch on OrderType equality: {bad_compares}"
    )
