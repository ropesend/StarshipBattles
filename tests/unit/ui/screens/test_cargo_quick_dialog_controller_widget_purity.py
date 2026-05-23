"""
PROJ-348 T5.1 — Characterization test: CargoQuickDialogController must
NOT touch pygame_gui widgets.

The controller's docstring (cargo_quick_dialog_controller.py:9-13) says
"The controller does NOT touch pygame_gui widgets." Pre-fix it violated
that contract by reading `item['slider'].get_current_value()` directly in
`issue_orders`.

This test asserts the contract by passing `resolved_items` entries that
have NO `'slider'` key — if `issue_orders` tries to dereference one it
would KeyError. Pre-fix this test FAILS; post-fix it PASSES.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from game.ui.screens.cargo_quick_dialog_controller import (
    CargoQuickDialogController,
)


def test_issue_orders_consumes_resolved_amount_field_not_slider_widget():
    """`issue_orders` must read `item['amount']` (resolved by the dialog)
    and never `item['slider']`. Passing items WITHOUT a slider key proves
    the controller is widget-pure."""
    fleet = MagicMock()
    fleet.id = 99
    facade = MagicMock()
    facade.handle_command.return_value = MagicMock(is_valid=True)

    controller = CargoQuickDialogController(
        fleet=fleet,
        hex_coord=(0, 0),
        direction='load',
        facade=facade,
    )

    resolved_items = [
        {
            'amount': 5,
            'type': 'metals',
            'max': 100,
            'species_id': None,
            'label': 'Metals',
            'planet_id': 7,
            # Note: NO 'slider' key. If the controller tries to read it,
            # this test KeyErrors and fails.
        },
    ]

    orders_issued = controller.issue_orders(resolved_items)

    assert orders_issued == 1
    facade.handle_command.assert_called_once()
    # PROJ-479 Task 3.28: explicit named extraction instead of call_args[0][0]
    cmd = facade.handle_command.call_args.args[0]
    assert cmd.amount == 5
    assert cmd.cargo_type == 'metals'


def test_issue_orders_skips_zero_amount_entries():
    """Zero amounts are skipped — no command emitted for them."""
    fleet = MagicMock()
    fleet.id = 99
    facade = MagicMock()
    facade.handle_command.return_value = MagicMock(is_valid=True)

    controller = CargoQuickDialogController(
        fleet=fleet,
        hex_coord=(0, 0),
        direction='load',
        facade=facade,
    )

    resolved_items = [
        {'amount': 0, 'type': 'metals', 'max': 100, 'species_id': None,
         'label': 'Metals', 'planet_id': 7},
        {'amount': 3, 'type': 'fuel', 'max': 50, 'species_id': None,
         'label': 'Fuel', 'planet_id': 7},
    ]

    orders_issued = controller.issue_orders(resolved_items)

    assert orders_issued == 1
    assert facade.handle_command.call_count == 1
