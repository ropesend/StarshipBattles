"""Construction-queue CRUD command handlers.

Owns: AddToConstructionQueue (the largest handler in the original file —
124 LOC including two private helpers), RemoveFromConstructionQueue,
ReorderConstructionQueue.

These handlers operate on the construction queue of either a Planet or
a Fleet via `BaseCommandHandler._resolve_build_entity` / `_resolve_queue`.
Multi-queue support (facility queues) is handled at the base level.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, TYPE_CHECKING

from game.core.validation import ValidationResult
from game.strategy.engine.commands import (
    AddToConstructionQueueCommand,
    RemoveFromConstructionQueueCommand,
    ReorderConstructionQueueCommand,
    SetBuildQueuePausedCommand,
)
from game.strategy.engine.commands.registry import (
    CommandRegistry,
    CommandSpec,
    command_spec,
)
from game.strategy.engine.handlers.base import BaseCommandHandler
from game.strategy.services.design_cost_calculator import DesignCostCalculator
from game.strategy.systems.design_library import DesignLibrary

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.engine.game_session import GameSession


@command_spec(
    command_class=AddToConstructionQueueCommand,
    order_type=None,
    category='construction',
    execution_model='instant',
    facade_helper_name='dispatch_add_to_construction_queue',
)
class AddToConstructionQueueCommandHandler(BaseCommandHandler):
    """Handler for AddToConstructionQueueCommand (PROJ-208 Phase 2)."""

    def execute(self, session: 'GameSession', cmd: 'AddToConstructionQueueCommand') -> ValidationResult:
        """Handle AddToConstructionQueueCommand - add item to construction queue.

        Creates a queue item dict with design_id, type, turns_remaining, and
        cost tracking fields, then inserts or appends to the entity's queue.
        """
        # 1. Resolve entity (planet or fleet)
        entity = self._resolve_build_entity(session, cmd.entity_id, cmd.entity_type)
        if entity is None:
            return ValidationResult.error(f"{cmd.entity_type.capitalize()} not found.")

        # 2. Find the correct queue - may be entity.construction_queue or a facility queue
        queue = self._resolve_queue(entity, cmd.queue_id)
        if queue is None:
            return ValidationResult.error(f"Construction queue not found.")

        # 3. Validate index if specified
        if cmd.index is not None:
            if cmd.index < 0 or cmd.index > len(queue):
                return ValidationResult.error(f"Invalid queue index: {cmd.index}")

        # 4. Check design validity (mass budget)
        design_valid = self._check_design_valid(session, entity, cmd.design_id)
        if not design_valid:
            return ValidationResult.error("Design exceeds mass budget and cannot be built.")

        # 5. Calculate design cost (PROJ-213: fix empty total_cost bug)
        total_cost = self._load_design_cost(session, entity, cmd.design_id)

        # 5. Pre-calculate initial turns estimate (BUG-96)
        from game.strategy.data.build_queue_source import (
            get_production_rate_for_queue, estimate_build_turns,
        )
        production_rate = get_production_rate_for_queue(entity, cmd.queue_id)
        initial_turns = estimate_build_turns(total_cost, production_rate)

        # 6. Create queue item
        queue_item = {
            "design_id": cmd.design_id,
            "type": cmd.category,
            "turns_remaining": initial_turns,
            "total_cost": total_cost,
            "resources_consumed": {res: 0.0 for res in total_cost},
        }

        # 7. Add target_planet_id for complexes if specified
        if cmd.target_planet_id is not None:
            queue_item["target_planet_id"] = cmd.target_planet_id

        # 8. Insert or append
        if cmd.index is not None:
            queue.insert(cmd.index, queue_item)
            logger.info(f"GameSession: Inserted {cmd.design_id} into {cmd.entity_type} {cmd.entity_id} queue at {cmd.index}")
        else:
            queue.append(queue_item)
            logger.info(f"GameSession: Appended {cmd.design_id} to {cmd.entity_type} {cmd.entity_id} queue")

        return ValidationResult.success()

    def _check_design_valid(self, session: 'GameSession', entity, design_id: str) -> bool:
        """Check if a design is valid for construction.

        Uses DesignValidator to check crew, life support, and mass budgets.

        Args:
            session: Game session for save_path.
            entity: Planet or Fleet with owner_id.
            design_id: ID of the design to check.

        Returns:
            True if the design is valid, False if it has errors.
        """
        try:
            empire_id = getattr(entity, 'owner_id', 0)
            library = DesignLibrary(session.save_path, empire_id)
            load_result = library.load_design_data(design_id)
            if not load_result.success:
                return True  # Can't validate, allow by default

            if session.registries:
                from game.strategy.services.design_validator import DesignValidator
                validator = DesignValidator(session.registries)
                result = validator.validate(load_result.data)
                # Block on errors AND warnings (e.g., layer mass over budget)
                if result.has_issues:
                    issues = result.errors + result.warnings
                    logger.warning(
                        f"Design '{design_id}' failed validation: {'; '.join(issues)}"
                    )
                    return False
                return True

            return True
        except (OSError, ValueError, KeyError):
            return True  # Can't validate, allow by default

    def _load_design_cost(self, session: 'GameSession', entity, design_id: str) -> Dict[str, float]:
        """Load design data and calculate total resource cost.

        PROJ-213: Populates queue items with actual build costs so
        ProductionEngine can process tick-based resource consumption.

        Args:
            session: Game session for save_path.
            entity: Planet or Fleet with owner_id.
            design_id: ID of the design to get cost for.

        Returns:
            Dict mapping resource type to cost amount, empty dict on failure.
        """
        try:
            empire_id = getattr(entity, 'owner_id', 0)
            library = DesignLibrary(session.save_path, empire_id)
            load_result = library.load_design_data(design_id)
            if not load_result.success:
                logger.warning(f"Could not load design data for {design_id}: {load_result.error}")
                return {}
            # PROJ-218: Pass registries for Ship-loading cost calculation
            return DesignCostCalculator.calculate_total_cost(load_result.data, session.registries)
        except (OSError, ValueError, KeyError) as e:
            logger.warning(f"Failed to calculate design cost for {design_id}: {e}")
            return {}


@command_spec(
    command_class=RemoveFromConstructionQueueCommand,
    order_type=None,
    category='construction',
    execution_model='instant',
    facade_helper_name='dispatch_remove_from_construction_queue',
)
class RemoveFromConstructionQueueCommandHandler(BaseCommandHandler):
    """Handler for RemoveFromConstructionQueueCommand (PROJ-208 Phase 2).

    BUG-103: Updated to use _resolve_queue() from BaseCommandHandler for
    multi-queue entity support (facility queues).
    """

    def execute(self, session: 'GameSession', cmd: 'RemoveFromConstructionQueueCommand') -> ValidationResult:
        """Handle RemoveFromConstructionQueueCommand - remove item from queue.

        For fleets, if the queue becomes empty, may need BUILD order cleanup
        (handled by separate RemoveBuildOrderCommand if needed).
        """
        # 1. Resolve entity (planet or fleet)
        entity = self._resolve_build_entity(session, cmd.entity_id, cmd.entity_type)
        if entity is None:
            return ValidationResult.error(f"{cmd.entity_type.capitalize()} not found.")

        # 2. Find the correct queue (BUG-103: supports facility queues via queue_id)
        queue = self._resolve_queue(entity, getattr(cmd, 'queue_id', None))
        if queue is None:
            return ValidationResult.error(f"Construction queue not found.")

        # 3. Validate index
        if cmd.item_index < 0 or cmd.item_index >= len(queue):
            return ValidationResult.error(f"Invalid queue index: {cmd.item_index}")

        # 4. Remove item
        removed_item = queue.pop(cmd.item_index)
        logger.info(f"GameSession: Removed item {cmd.item_index} from {cmd.entity_type} {cmd.entity_id} queue")

        return ValidationResult.success()


@command_spec(
    command_class=ReorderConstructionQueueCommand,
    order_type=None,
    category='construction',
    execution_model='instant',
    facade_helper_name='dispatch_reorder_construction_queue',
)
class ReorderConstructionQueueCommandHandler(BaseCommandHandler):
    """Handler for ReorderConstructionQueueCommand (PROJ-208 Phase 2).

    BUG-103: Updated to use _resolve_queue() from BaseCommandHandler for
    multi-queue entity support (facility queues).
    """

    def execute(self, session: 'GameSession', cmd: 'ReorderConstructionQueueCommand') -> ValidationResult:
        """Handle ReorderConstructionQueueCommand - move item to new position.

        Performs atomic pop + insert to move item from from_index to to_index.
        """
        # 1. Resolve entity (planet or fleet)
        entity = self._resolve_build_entity(session, cmd.entity_id, cmd.entity_type)
        if entity is None:
            return ValidationResult.error(f"{cmd.entity_type.capitalize()} not found.")

        # 2. Find the correct queue (BUG-103: supports facility queues via queue_id)
        queue = self._resolve_queue(entity, getattr(cmd, 'queue_id', None))
        if queue is None:
            return ValidationResult.error(f"Construction queue not found.")

        # 3. Validate indices
        if cmd.from_index < 0 or cmd.from_index >= len(queue):
            return ValidationResult.error(f"Invalid from_index: {cmd.from_index}")
        if cmd.to_index < 0 or cmd.to_index >= len(queue):
            return ValidationResult.error(f"Invalid to_index: {cmd.to_index}")

        # 4. Perform atomic reorder (pop + insert)
        item = queue.pop(cmd.from_index)
        queue.insert(cmd.to_index, item)

        logger.info(f"GameSession: Reordered {cmd.entity_type} {cmd.entity_id} queue {cmd.from_index} -> {cmd.to_index}")
        return ValidationResult.success()


@command_spec(
    command_class=SetBuildQueuePausedCommand,
    order_type=None,
    category='construction',
    execution_model='instant',
    # No facade helper today (FEAT-17 wires through other paths).
    facade_helper_name=None,
)
class SetBuildQueuePausedCommandHandler(BaseCommandHandler):
    """Handler for SetBuildQueuePausedCommand (FEAT-17).

    Toggles `construction_queue_paused` on the queue's owner entity. Three
    targets:
      - planet base queue → owner is the Planet itself
      - planet shipyard facility queue → owner is the PlanetaryFacility
      - fleet space-yard queue → owner is the Fleet itself

    Resolution mirrors the queue-list resolution used by
    AddToConstructionQueueCommandHandler etc., via
    `BaseCommandHandler._resolve_queue_owner`.
    """

    def execute(self, session: 'GameSession', cmd: 'SetBuildQueuePausedCommand') -> ValidationResult:
        # 1. Resolve entity (planet or fleet)
        entity = self._resolve_build_entity(session, cmd.entity_id, cmd.entity_type)
        if entity is None:
            return ValidationResult.error(f"{cmd.entity_type.capitalize()} not found.")

        # 2. Resolve the queue *owner* (entity itself, or a facility)
        owner = self._resolve_queue_owner(entity, getattr(cmd, 'queue_id', None))
        if owner is None:
            return ValidationResult.error(
                f"Build queue '{getattr(cmd, 'queue_id', None)}' not found."
            )

        # 3. Set the flag
        owner.construction_queue_paused = bool(cmd.paused)

        action = "Paused" if cmd.paused else "Resumed"
        logger.info(
            f"GameSession: {action} build queue on {cmd.entity_type} "
            f"{cmd.entity_id} (queue_id={getattr(cmd, 'queue_id', None)})"
        )
        return ValidationResult.success()

def register(registry: CommandRegistry) -> None:
    """PROJ-371: register this module's handlers into ``registry``."""
    for handler_cls in (
        AddToConstructionQueueCommandHandler,
        RemoveFromConstructionQueueCommandHandler,
        ReorderConstructionQueueCommandHandler,
        SetBuildQueuePausedCommandHandler,
    ):
        registry.register(CommandSpec(
            handler_class=handler_cls,
            **handler_cls.__command_spec_kwargs__,
        ))
