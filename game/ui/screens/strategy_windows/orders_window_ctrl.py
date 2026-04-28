"""Fleet/Planet Orders Window registrar (PROJ-238).

The largest registrar — its ``open`` method branches on ``entity_type`` and
constructs three command-dispatch closures (clear / delete / reorder) per
branch plus an ``edit_order_callback`` closure.

Closure-capture contract:

* ``clear_orders_callback`` and friends MUST dispatch through
  ``composer.scene.facade.handle_command``. The closures bind the local
  ``facade`` and ``owner_id`` names so the captured values are stable even
  if the scene's facade attribute is later rebound.
* ``edit_order_callback`` MUST forward ``(entity, order_index, order)`` to
  ``scene.on_edit_order``.

PROJ-309 sub-phase 3.10: extracted from ``strategy_window_manager.py``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class OrdersRegistrar:
    """Lifecycle for the Fleet/Planet Orders Window slot (PROJ-238)."""

    def __init__(self, composer: "StrategyWindowManager") -> None:
        self._composer = composer

    def open(self, entity, entity_type: str = "fleet") -> None:
        """Open the Orders Window for a fleet or planet.

        Args:
            entity: The fleet or planet to show orders for.
            entity_type: "fleet" or "planet".
        """
        c = self._composer
        if c.fleet_orders_window:
            c.fleet_orders_window.kill()

        w, h = 480, 500
        rect = pygame.Rect((c.width - w) / 2, (c.height - h) / 2, w, h)

        # Bind locals so the closures capture stable references rather than
        # walking back through ``self._composer.scene.facade`` on each call.
        scene = c.scene
        facade = scene.facade

        if entity_type == "planet":
            def clear_orders_callback(entity_id: int) -> None:
                from game.strategy.engine.commands import ClearPlanetOrdersCommand
                cmd = ClearPlanetOrdersCommand(planet_id=entity_id)
                facade.handle_command(cmd)

            def delete_order_callback(entity_id: int, order_index: int) -> None:
                from game.strategy.engine.commands import DeletePlanetOrderCommand
                cmd = DeletePlanetOrderCommand(
                    planet_id=entity_id, order_index=order_index
                )
                facade.handle_command(cmd)

            def reorder_order_callback(
                entity_id: int, order_index: int, direction: int
            ) -> None:
                pass  # Planet order reordering not yet implemented
        else:
            owner_id = entity.owner_id

            def clear_orders_callback(entity_id: int) -> None:
                from game.strategy.engine.commands import ClearOrdersCommand
                cmd = ClearOrdersCommand(fleet_id=entity_id, empire_id=owner_id)
                facade.handle_command(cmd)

            def delete_order_callback(entity_id: int, order_index: int) -> None:
                from game.strategy.engine.commands import DeleteOrderCommand
                cmd = DeleteOrderCommand(
                    fleet_id=entity_id, order_index=order_index, empire_id=owner_id
                )
                facade.handle_command(cmd)

            def reorder_order_callback(
                entity_id: int, order_index: int, direction: int
            ) -> None:
                from game.strategy.engine.commands import ReorderOrderCommand
                cmd = ReorderOrderCommand(
                    fleet_id=entity_id,
                    order_index=order_index,
                    direction=direction,
                    empire_id=owner_id,
                )
                facade.handle_command(cmd)

        def edit_order_callback(entity_id: int, order_index: int, order) -> None:
            scene.on_edit_order(entity, order_index, order)

        # Local import preserved from source — OrdersWindow has historically
        # been imported at method scope to avoid an import cycle. Keep it
        # deferred here until the cycle is independently verified absent.
        from game.ui.screens.orders_window import OrdersWindow

        c.fleet_orders_window = OrdersWindow(
            rect, c.manager, entity,
            window_manager=c,
            entity_type=entity_type,
            input_mapper=c._mapper,
            clear_orders_callback=clear_orders_callback,
            delete_order_callback=delete_order_callback,
            reorder_order_callback=reorder_order_callback,
            edit_order_callback=edit_order_callback,
        )
