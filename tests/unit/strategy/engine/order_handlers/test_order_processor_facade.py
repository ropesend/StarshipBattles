"""AST static-guard regression for the `OrderProcessor` facade.

PROJ-368 Phase 5 established this file as a structural complement to the
Phase-4 hard gates. PROJ-454 Phase 3 deleted the three legacy facade
methods (`process_join_fleet` / `process_colonize` / `process_transfer`)
and their typed result dataclasses; the remaining facade surface is the
handler-registry construction (`__init__`), the public
``get_handler(order_type)`` accessor, ``process_instant_orders``, and
``execute_action_order``. The cap below reflects that slimmer surface.

Companion hard gates (still active):
- `tests/unit/strategy/engine/test_order_processor_no_legacy_helpers.py`
  (LOC < 200, no legacy private helpers, no `if order.type ==
  OrderType.X` ladders)
- `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py`
  (every OrderType handled by OrderProcessor has a registered handler)
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
    """Cap OrderType references on the facade post-PROJ-454 Phase 3.

    After Phase 3 deleted the three legacy facade shims, the only
    remaining ``OrderType.X`` literal in ``order_processor.py`` is the
    ``process_instant_orders`` registry lookup, which fetches the
    JOIN_FLEET handler unconditionally to drive the BUG-122 three-phase
    pipeline. ``execute_action_order`` uses ``order.type`` (an instance
    attribute access on a runtime Order, NOT an ``OrderType.X`` literal)
    so it does NOT count toward this cap.

    Total: <= 2 references. Any more means a new branching ladder has
    been introduced; the registry is the right place for that.
    """
    tree = ast.parse(ORDER_PROCESSOR.read_text(encoding="utf-8"))
    refs = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "OrderType"
    ]
    assert len(refs) <= 2, (
        f"OrderProcessor references OrderType {len(refs)} times; "
        "post-PROJ-454 cap is <= 2 (only process_instant_orders' "
        "registry lookup for JOIN_FLEET is permitted)."
    )


# PROJ-495 T4.4: deleted ``test_phase_4_gates_still_pass``. Importing the gate
# test modules and asserting ``hasattr`` on their named tests added nothing —
# pytest discovery already fails naturally if those tests are renamed or
# removed, and the hasattr assertions duplicated that failure with no extra
# diagnostic value. The Phase 4 gate test names are listed for traceability:
# - tests/unit/strategy/engine/test_order_processor_no_legacy_helpers.py::
#     test_no_legacy_private_helpers_on_order_processor
#     test_order_processor_facade_under_200_loc
#     test_no_order_type_branching_in_facade
# - tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py::
#     test_every_action_order_type_has_a_handler
