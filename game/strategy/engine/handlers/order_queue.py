"""Order-list manipulation command handlers.

Owns: ColonizeMission (queues MOVE+COLONIZE), ClearOrders, SplitFleet,
DeleteOrder, ReorderOrder.

These handlers don't add new movement to a fleet — they manipulate the
order queue or fleet composition itself.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import (
    ClearOrdersCommand,
    DeleteOrderCommand,
    QueueColonizeMissionCommand,
    ReorderOrderCommand,
    SplitFleetCommand,
)
from game.strategy.engine.commands.registry import (
    CommandRegistry,
    CommandSpec,
    command_spec,
)
from game.strategy.engine.handlers.base import (
    BaseCommandHandler,
    add_move_order_if_needed,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


@command_spec(
    command_class=QueueColonizeMissionCommand,
    order_type=None,
    category='action',
    execution_model='mission',
    facade_helper_name='dispatch_queue_colonize_mission',
)
class ColonizeMissionCommandHandler(BaseCommandHandler):
    """Handler for QueueColonizeMissionCommand."""

    def execute(self, session: 'GameSession', cmd: 'QueueColonizeMissionCommand') -> ValidationResult:
        """Handle QueueColonizeMissionCommand - queues MOVE and COLONIZE orders."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Resolve planet (None is valid - means "any planet")
        planet = None
        if cmd.planet_id is not None:
            planet, error = self._resolve_planet(session, cmd.planet_id)
            if error:
                return error

            # Pod availability is validated at execution time, not command time.
            # The player may load a pod onto the ship before the fleet arrives.

        # Loading is handled by explicit TRANSFER orders from the UI dialog.

        # 3. Queue MOVE order if needed (chain-aware path calculation)
        # PROJ-207 Phase 5: Use shared helper with auto chain detection
        move_result = add_move_order_if_needed(session, fleet, cmd.target_hex)
        if not move_result.is_valid:
            return move_result

        # 5. Queue COLONIZE order (target=None means "any available planet")
        colonize_target = self._build_colonize_target(planet, cmd)
        colonize_order = Order(OrderType.COLONIZE, target=colonize_target)
        fleet.add_order(colonize_order)

        planet_name = planet.name if planet else "Any Planet"
        logger.info(f"GameSession: Queued Colonize Mission for Fleet {fleet.id} -> {planet_name}")
        return ValidationResult.success()


@command_spec(
    command_class=ClearOrdersCommand,
    order_type=None,
    category='fleet_management',
    execution_model='instant',
    facade_helper_name='dispatch_clear_orders',
)
class ClearOrdersCommandHandler(BaseCommandHandler):
    """Handler for ClearOrdersCommand."""

    def execute(self, session: 'GameSession', cmd: 'ClearOrdersCommand') -> ValidationResult:
        """Handle ClearOrdersCommand - clears all orders from fleet."""
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Clear orders and path (PROJ-222: use Fleet API for pursuer cleanup)
        fleet.clear_orders()

        logger.info(f"GameSession: Cleared orders for Fleet {fleet.id}")
        return ValidationResult.success()


@command_spec(
    command_class=SplitFleetCommand,
    order_type=None,
    category='fleet_management',
    execution_model='instant',
    facade_helper_name='dispatch_split_fleet',
)
class SplitFleetCommandHandler(BaseCommandHandler):
    """Handler for SplitFleetCommand (PROJ-208 Phase 1)."""

    def execute(self, session: 'GameSession', cmd: 'SplitFleetCommand') -> ValidationResult:
        """Handle SplitFleetCommand - split ships into a new fleet.

        Removes specified ships from source fleet and creates a new fleet
        with those ships at the same location.
        """
        # 1. Resolve source fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate ship_instance_ids
        if not cmd.ship_instance_ids:
            return ValidationResult.error("No ships specified for split.")

        # Find ships to move
        ships_to_move = []
        for instance_id in cmd.ship_instance_ids:
            found = None
            for ship in fleet.ships:
                if ship.instance_id == instance_id:
                    found = ship
                    break
            if found is None:
                return ValidationResult.error(f"Ship {instance_id} not found in fleet.")
            ships_to_move.append(found)

        # 3. Validate at least one ship remains in source fleet
        remaining_count = len(fleet.ships) - len(ships_to_move)
        if remaining_count < 1:
            return ValidationResult.error("At least one ship must remain in the source fleet.")

        # 4. Get owning empire to generate new fleet ID
        if fleet.owner_id < 0 or fleet.owner_id >= len(session.empires):
            return ValidationResult.error("Fleet owner not found.")
        empire = session.empires[fleet.owner_id]

        # 5. Create new fleet at same location (globally unique ID from Galaxy)
        from game.strategy.data.fleet import Fleet
        new_fleet_id = session.galaxy.get_next_fleet_id()
        display_name = f"Fleet {empire.get_next_fleet_display_number()}"
        new_fleet = Fleet(
            fleet_id=new_fleet_id,
            owner_id=fleet.owner_id,
            location=fleet.location,
            component_registry=fleet._component_registry,
            display_name=display_name,
        )

        # 6. Move ships to new fleet
        for ship in ships_to_move:
            fleet.remove_ship(ship)
            new_fleet.add_ship(ship)

        # 7. Register new fleet with empire (auto-registers with galaxy via PROJ-219)
        empire.add_fleet(new_fleet)

        logger.info(f"GameSession: Split fleet {cmd.fleet_id} -> new fleet {new_fleet_id} ({len(ships_to_move)} ships)")
        return ValidationResult.success()


@command_spec(
    command_class=DeleteOrderCommand,
    order_type=None,
    category='fleet_management',
    execution_model='instant',
    facade_helper_name='dispatch_delete_order',
)
class DeleteOrderCommandHandler(BaseCommandHandler):
    """Handler for DeleteOrderCommand (PROJ-208 Phase 1)."""

    def execute(self, session: 'GameSession', cmd: 'DeleteOrderCommand') -> ValidationResult:
        """Handle DeleteOrderCommand - remove an order from the queue.

        If the active order (index 0) is deleted, the fleet's path is invalidated.
        """
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate order_index
        if cmd.order_index < 0 or cmd.order_index >= len(fleet.orders):
            return ValidationResult.error(f"Invalid order index: {cmd.order_index}")

        # 3. Remove the order (PROJ-222: use Fleet API for pursuer cleanup)
        fleet.remove_order_at(cmd.order_index)

        logger.info(f"GameSession: Deleted order {cmd.order_index} from fleet {cmd.fleet_id}")
        return ValidationResult.success()


@command_spec(
    command_class=ReorderOrderCommand,
    order_type=None,
    category='fleet_management',
    execution_model='instant',
    facade_helper_name='dispatch_reorder_order',
)
class ReorderOrderCommandHandler(BaseCommandHandler):
    """Handler for ReorderOrderCommand (PROJ-208 Phase 1)."""

    def execute(self, session: 'GameSession', cmd: 'ReorderOrderCommand') -> ValidationResult:
        """Handle ReorderOrderCommand - swap order positions.

        If the active order (index 0) is affected, the fleet's path is invalidated.
        """
        # 1. Resolve fleet
        fleet, error = self._resolve_player_fleet(session, cmd.fleet_id)
        if error:
            return error

        # 2. Validate order_index
        if cmd.order_index < 0 or cmd.order_index >= len(fleet.orders):
            return ValidationResult.error(f"Invalid order index: {cmd.order_index}")

        # 3. Validate direction
        if cmd.direction not in (-1, 1):
            return ValidationResult.error(f"Invalid direction: {cmd.direction} (must be -1 or 1)")

        # 4. Validate target index
        target_index = cmd.order_index + cmd.direction
        if target_index < 0 or target_index >= len(fleet.orders):
            return ValidationResult.error(f"Cannot move order {cmd.order_index} in direction {cmd.direction}")

        # 5. Swap orders.
        # PROJ-370 Phase 2: route through IFleetMutator.
        session.fleet_mutator.swap_orders(fleet, cmd.order_index, target_index)

        # 6. If active order (index 0) was affected, invalidate path
        if cmd.order_index == 0 or target_index == 0:
            # PROJ-370 Phase 2: route through IFleetMutator.
            session.fleet_mutator.set_path(fleet, [])

        logger.info(f"GameSession: Reordered fleet {cmd.fleet_id} order {cmd.order_index} -> {target_index}")
        return ValidationResult.success()

def register(registry: CommandRegistry) -> None:
    """PROJ-371: register this module's handlers into ``registry``."""
    for handler_cls in (
        ColonizeMissionCommandHandler,
        ClearOrdersCommandHandler,
        SplitFleetCommandHandler,
        DeleteOrderCommandHandler,
        ReorderOrderCommandHandler,
    ):
        registry.register(CommandSpec(
            handler_class=handler_cls,
            **handler_cls.__command_spec_kwargs__,
        ))
