"""Controller for CargoQuickDialog (PROJ-329C Phase 2).

Owns the facade-side queries that ``CargoQuickDialog`` previously called
inline during ``_populate_items`` + ``_issue_orders``: resolving colonies
at a hex (with fleet-location fallback), fetching unload/load items via
``CargoTransferService``, and dispatching ``IssueTransferCommand`` for
each non-zero slider on confirm.

The controller does NOT touch ``pygame_gui`` widgets. Widget construction
lives in ``CargoQuickDialogUiBuilder`` (in the screen module). The
controller is constructed in Stage 1 of the screen ``__init__`` (cheap;
no facade I/O), and its query methods are called from the builder during
Stage 3.

Pattern reference: PROJ-328 Phase C ``transfer_controller.py``.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from game.strategy.services.cargo_transfer_service import CargoTransferService

logger = logging.getLogger(__name__)


class CargoQuickDialogController:
    """Facade-coupled queries + command dispatch for CargoQuickDialog.

    The dialog calls ``get_unload_items`` / ``get_load_items`` from the
    builder during Stage 3, then ``issue_orders`` from ``_issue_orders``
    on confirm.
    """

    def __init__(self, fleet, hex_coord, direction: str, facade) -> None:
        self.fleet = fleet
        self.hex_coord = hex_coord
        self.direction = direction
        self.facade = facade

    # ---- Queries ----

    def get_unload_items(self) -> List[Dict[str, Any]]:
        colonies = CargoTransferService.resolve_colonies(
            self.facade, self.hex_coord, self.fleet
        )
        return CargoTransferService.get_unload_items(
            self.facade, self.fleet.id, colonies
        )

    def get_load_items(self) -> List[Dict[str, Any]]:
        colonies = CargoTransferService.resolve_colonies(
            self.facade, self.hex_coord, self.fleet
        )
        return CargoTransferService.get_load_items(self.facade, colonies)

    def get_target_planet_id(self) -> Optional[Any]:
        """Resolve the destination planet for an unload. ``None`` if the
        hex has no colonies."""
        colonies = CargoTransferService.resolve_colonies(
            self.facade, self.hex_coord, self.fleet
        )
        if not colonies:
            return None
        return colonies[0].planet_id

    # ---- Command emission ----

    def issue_orders(self, resolved_items: List[Dict[str, Any]]) -> int:
        """Issue transfer commands for all items with positive ``amount``.

        Returns the count of dispatched orders.

        PROJ-348 T5.1: ``resolved_items`` is the dialog's cargo_items list
        with each entry's ``amount`` field already populated from the
        slider. The controller no longer touches pygame_gui widgets — that
        boundary used to be violated by reading ``item['slider'].get_current_value()``
        here, contradicting the controller's "does NOT touch pygame_gui
        widgets" contract documented in this module's docstring.

        Each ``resolved_items`` entry must include:
            'amount': int (already resolved from slider)
            'type': str (cargo type)
            'max': int
            'species_id': Optional[str]
            'label': str (logging only)
            'planet_id': Optional[int] (load direction)
        """
        target_planet_id = None
        if self.direction == 'unload':
            target_planet_id = self.get_target_planet_id()

        orders_issued = 0
        for item in resolved_items:
            amount = int(item['amount'])
            if amount <= 0:
                continue

            planet_id = (
                item.get('planet_id')
                if self.direction == 'load'
                else target_planet_id
            )
            if not planet_id:
                continue

            cmd = CargoTransferService.build_transfer_command(
                fleet_id=self.fleet.id,
                planet_id=planet_id,
                cargo_type=item['type'],
                direction=self.direction,
                amount=amount,
                max_amount=item['max'],
                species_id=item['species_id'],
            )

            result = self.facade.handle_command(cmd)
            if result.is_valid:
                orders_issued += 1
                logger.info(
                    f"CargoQuickDialog: Order issued for {item['label']}"
                )
            else:
                logger.info(
                    f"CargoQuickDialog: Validation failed: {result.message}"
                )

        return orders_issued


__all__ = ["CargoQuickDialogController"]
