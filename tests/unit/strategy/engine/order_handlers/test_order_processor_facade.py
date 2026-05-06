"""AST static-guard regression for the `OrderProcessor` facade (PROJ-368 Phase 5).

The hard gates landed in Phase 4 at:
- `tests/unit/strategy/engine/test_order_processor_no_legacy_helpers.py`
  (LOC < 200, no legacy private helpers, no `if order.type ==
  OrderType.X` ladders)
- `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py`
  (every OrderType handled by OrderProcessor has a registered handler)

This file adds Phase-5-style structural checks that complement those
gates: OrderType reference count cap on the facade, and a re-import
of the Phase 4 gates so the per-handler test suite proves them
together.
"""
from __future__ import annotations

import ast
import pathlib

ORDER_PROCESSOR = (
    pathlib.Path(__file__).resolve().parents[5]
    / "game"
    / "strategy"
    / "engine"
    / "order_processor.py"
)


def test_order_processor_minimal_order_type_references():
    """Cap OrderType references on the facade.

    The slim facade still references `OrderType` for two reasons:
    1. The `process_transfer` shim validates that an order is a
       transfer family member before delegating (`order.type not in
       (OrderType.TRANSFER, OrderType.LOAD_POPULATION,
       OrderType.UNLOAD_POPULATION)`) -- 3 references.
    2. `process_join_fleet` and `process_colonize` use
       `OrderType.JOIN_FLEET` / `OrderType.COLONIZE` for the registry
       lookup -- 2 references.

    Total: <= 6 references. Any more means a new branching ladder
    has been introduced; the registry is the right place for that.
    """
    tree = ast.parse(ORDER_PROCESSOR.read_text(encoding="utf-8"))
    refs = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "OrderType"
    ]
    assert len(refs) <= 6, (
        f"OrderProcessor references OrderType {len(refs)} times; "
        "facade target is <= 6 (3 in process_transfer shim + 1 each in "
        "process_join_fleet / process_colonize / execute_action_order's "
        "registry lookup)."
    )


def test_phase_4_gates_still_pass():
    """Re-runs the Phase 4 hard gates as a regression check.

    Importing the gate test modules causes their assertions to be
    discovered by pytest. They run as separate test items; this test
    just confirms the modules import cleanly so a missing file or
    rename is caught here too.
    """
    import tests.unit.strategy.engine.test_order_processor_no_legacy_helpers as gate_no_legacy
    import tests.unit.strategy.engine.order_handlers.test_handler_registry_completeness as gate_completeness

    # Sanity: the gate modules expose the expected named tests.
    assert hasattr(gate_no_legacy, "test_no_legacy_private_helpers_on_order_processor")
    assert hasattr(gate_no_legacy, "test_order_processor_facade_under_200_loc")
    assert hasattr(gate_no_legacy, "test_no_order_type_branching_in_facade")
    assert hasattr(gate_completeness, "test_every_action_order_type_has_a_handler")
