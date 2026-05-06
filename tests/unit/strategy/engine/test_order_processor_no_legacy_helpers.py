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
    """The facade target is <= 200 LOC."""
    loc = len(ORDER_PROCESSOR.read_text(encoding="utf-8").splitlines())
    assert loc <= 200, (
        f"order_processor.py is {loc} LOC; PROJ-368 facade target is <= 200"
    )


def test_no_order_type_branching_in_facade():
    """Facade should reference OrderType only for registry lookups, never to branch.

    PROJ-368 invariant: zero comparison-based branching on ``OrderType``
    members in the facade. Dispatch belongs in the handler layer; the
    facade only owns argument shape-changes around ``registry.get(order_type)``.

    PROJ-368 review MAJ-002: the original guard only matched ``ast.Eq`` and
    silently allowed ``order_type not in (OrderType.X, ...)`` ladders. The
    revised guard drops the operator-type filter entirely and rejects ANY
    ``ast.Compare`` whose operands include an ``OrderType.<member>``
    attribute reference -- covers ``==``, ``!=``, ``is``, ``is not``,
    ``in``, ``not in``, and any future operator. The `OrderType` LHS/RHS
    can appear on either side of the comparison.
    """
    def _references_order_type(node: ast.AST) -> bool:
        """True if the AST subtree has an `OrderType.<member>` attribute access."""
        for child in ast.walk(node):
            if (
                isinstance(child, ast.Attribute)
                and isinstance(child.value, ast.Name)
                and child.value.id == "OrderType"
            ):
                return True
        return False

    tree = ast.parse(ORDER_PROCESSOR.read_text(encoding="utf-8"))
    bad_compares = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        operands = [node.left, *node.comparators]
        if any(_references_order_type(op) for op in operands):
            bad_compares.append(ast.unparse(node))
    assert not bad_compares, (
        f"Facade must not branch by comparing OrderType: {bad_compares}"
    )
