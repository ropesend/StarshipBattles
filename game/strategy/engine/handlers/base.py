"""Infrastructure for the command-handler dispatch system.

Owns:
    - `ICommandHandler` Protocol (typing seam for handlers)
    - `BaseCommandHandler` mixin (resolution helpers used by every handler)
    - `CommandHandlerRegistry` (dispatch table)
    - `add_move_order_if_needed` (chain-aware MOVE auto-queue helper)

Extracted from the monolithic `command_handlers.py` in PROJ-309 sub-phase 3.5
(2026-04-27). PROJ-383 (2026-05-08) deleted the transitional
`command_handlers.py` re-export shim; all callers now import directly from
`game.strategy.engine.handlers/*`.
"""
from __future__ import annotations

from typing import Protocol, Dict, Any, TYPE_CHECKING, runtime_checkable, Optional
import logging

from game.core.error_codes import ErrorCode
from game.core.exceptions import ValidationException
from game.core.validation import ValidationResult
from game.strategy.services.galaxy_pathfinding_service import GalaxyPathfindingService
from game.strategy.data.order_types import Order, OrderType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.planet import Planet
    from game.strategy.engine.game_session import GameSession
    from game.strategy.engine.commands import Command


def add_move_order_if_needed(
    session: 'GameSession',
    fleet,
    target_hex,
    start_hex=None
) -> ValidationResult:
    """Add a MOVE order to fleet if not already at target hex.

    PROJ-204 Phase 3: Extracted from duplicate patterns in command handlers.
    PROJ-207 Phase 5: Added start_hex for chain-aware path calculation.

    Use this when a command needs to auto-queue movement before an action.

    Args:
        session: GameSession for path calculation.
        fleet: Fleet to potentially move.
        target_hex: Destination hex coordinate.
        start_hex: Optional starting hex for path calculation. If None,
                   calculates chain-aware start (last MOVE target or fleet.location).

    Returns:
        ValidationResult - invalid if no path found, valid otherwise.
    """
    # Determine start hex (chain-aware)
    # BUG-70: Find the last MOVE order (skip non-MOVE orders like LOAD_POPULATION)
    if start_hex is None:
        start_hex = fleet.location
        for order in reversed(fleet.orders):
            if order.type == OrderType.MOVE:
                start_hex = order.target
                break

    # Already at target - no move needed
    if start_hex == target_hex:
        return ValidationResult.success()

    # Calculate path from chain-aware start
    path = GalaxyPathfindingService(session.galaxy).find_hybrid_path(
        start_hex, target_hex,
    )
    if not path:
        return ValidationResult.error("No path found to target.")

    # Queue MOVE order
    move_order = Order(OrderType.MOVE, target=target_hex)
    fleet.add_order(move_order)

    # Set path immediately if it's the first order and fleet is at start
    if len(fleet.orders) == 1 and fleet.location == start_hex:
        # PROJ-370 Phase 2: route Fleet.path write through IFleetMutator.
        session.fleet_mutator.set_path(
            fleet, GalaxyPathfindingService.strip_start_hex(fleet.location, path),
        )

    return ValidationResult.success()


@runtime_checkable
class ICommandHandler(Protocol):
    """Protocol for command handlers."""

    def execute(self, session: 'GameSession', command: 'Command') -> ValidationResult:
        """Execute the command using the session context.

        Args:
            session: The game session providing empires, galaxy, etc.
            command: The command object with command-specific data.

        Returns:
            ValidationResult indicating success or failure.
        """
        ...


class BaseCommandHandler:
    """Mixin providing common resolution helpers for command handlers.

    Provides static methods for resolving fleets and planets with consistent
    error handling. Returns tuples of (object, error) where exactly one is set.

    PROJ-176 Phase 2: Extracted from duplicate resolution code in 19 handlers.
    PROJ-204 Phase 3: Added _resolve_fleet_required and _resolve_planet_optional.
    """

    @staticmethod
    def _resolve_fleet(session: 'GameSession', fleet_id: int, empire_id: int = None) -> tuple:
        """Resolve a fleet by ID with optional ownership validation.

        Args:
            session: The game session with empires and galaxy.
            fleet_id: The fleet ID to resolve.
            empire_id: Optional empire ID to validate ownership.
                None skips validation (used by intercept-target lookup, where
                cross-empire targets are legitimate).

        Returns:
            tuple[Fleet, None] on success, tuple[None, ValidationResult] on failure.
        """
        fleet = session._get_fleet_by_id(fleet_id)
        if fleet is None:
            return (None, ValidationResult.error("Fleet not found."))

        if empire_id is not None and fleet.owner_id != empire_id:
            return (None, ValidationResult.error("Fleet does not belong to this empire."))

        return (fleet, None)

    @staticmethod
    def _resolve_player_fleet(session: 'GameSession', fleet_id: int) -> tuple:
        """Resolve a fleet and authorize against the active empire.

        BUG-125: this is the standard authorization path for fleet command
        handlers. Identity is session context (`session.active_empire.id`)
        — handlers must NEVER trust an empire identifier supplied through
        the request body. Use `_resolve_fleet(empire_id=None)` for the
        rare cases where cross-empire fleet lookup is legitimate (e.g.
        intercept TARGET; the source-fleet command authorization always
        flows through this helper).

        Args:
            session: The game session with empires and galaxy.
            fleet_id: The fleet ID to resolve.

        Returns:
            tuple[Fleet, None] on success, tuple[None, ValidationResult] on failure.
        """
        active = session.active_empire
        if active is None:
            return (None, ValidationResult.error("No active empire."))
        return BaseCommandHandler._resolve_fleet(session, fleet_id, empire_id=active.id)

    @staticmethod
    def _resolve_fleet_required(session: 'GameSession', fleet_id: int, empire_id: int = None) -> 'Fleet':
        """Resolve a fleet by ID, raising ValidationException if not found.

        Use this when fleet must exist - avoids tuple unpacking boilerplate.

        PROJ-381 Phase 3 (ERR-01-003) replaced the previous bare
        ``ValueError`` with a structured ``ValidationException`` (codes
        ``MISSING_ENTITY`` / ``OWNERSHIP_MISMATCH``). PROJ-395 MAJ-012
        corrects this docstring (which still referenced ``ValueError``).

        Args:
            session: The game session with empires and galaxy.
            fleet_id: The fleet ID to resolve.
            empire_id: Optional empire ID to validate ownership.
                None skips validation.

        Returns:
            Fleet object if found.

        Raises:
            ValidationException: If fleet not found (MISSING_ENTITY) or
                ownership validation fails (OWNERSHIP_MISMATCH). PROJ-381
                Phase 3 (ERR-01-003) replaced the previous bare
                ValueError so handlers can branch on `code`.
        """
        fleet = session._get_fleet_by_id(fleet_id)
        if fleet is None:
            raise ValidationException(
                message="Fleet not found.",
                code=ErrorCode.MISSING_ENTITY.value,
                context={"fleet_id": fleet_id},
            )

        if empire_id is not None and fleet.owner_id != empire_id:
            raise ValidationException(
                message="Fleet does not belong to this empire.",
                code=ErrorCode.OWNERSHIP_MISMATCH.value,
                context={"fleet_id": fleet_id, "empire_id": empire_id},
            )

        return fleet

    # PROJ-431 Phase 3 (2026-05-17): `_reject_if_non_fleet_group` deleted.
    # Deployed fighters/satellites/mines are typed siblings of Fleet
    # (:class:`FighterWing`, :class:`SatelliteConstellation`,
    # :class:`MineGroup`) on ``empire.deployed_groups``. They never
    # reach a fleet-typed handler parameter via the action surface, so
    # the runtime guard is structurally redundant.

    @staticmethod
    def _resolve_player_planet(session: 'GameSession', planet_id: int) -> tuple:
        """Resolve a planet and authorize against the active empire.

        PROJ-375 (DUP-X-01): the standard authorization path for planet
        command handlers. Mirrors `_resolve_player_fleet`. Identity is
        session context (`session.active_empire.id`); handlers must NEVER
        trust an empire identifier supplied through the request body.

        Args:
            session: The game session with empires and galaxy.
            planet_id: The planet ID to resolve.

        Returns:
            tuple[Planet, None] on success, tuple[None, ValidationResult] on failure.
        """
        active = session.active_empire
        if active is None:
            return (None, ValidationResult.error("No active empire."))
        planet = session._get_planet_by_id(planet_id)
        if planet is None:
            return (None, ValidationResult.error("Planet not found."))
        if planet.owner_id != active.id:
            return (None, ValidationResult.error("Planet does not belong to this empire."))
        return (planet, None)

    @staticmethod
    def _resolve_planet(session: 'GameSession', planet_id: int) -> tuple:
        """Resolve a planet by ID.

        Args:
            session: The game session with galaxy.
            planet_id: The planet ID to resolve.

        Returns:
            tuple[Planet, None] on success, tuple[None, ValidationResult] on failure.
        """
        planet = session._get_planet_by_id(planet_id)
        if planet is None:
            return (None, ValidationResult.error("Planet not found."))

        return (planet, None)

    @staticmethod
    def _resolve_planet_optional(session: 'GameSession', planet_id: int, required: bool = True) -> Optional['Planet']:
        """Resolve a planet by ID with configurable error handling.

        Use this when planet may or may not be required.

        Args:
            session: The game session with galaxy.
            planet_id: The planet ID to resolve.
            required: If True, raise ValidationException(MISSING_ENTITY)
                when not found. If False, return None. PROJ-381 Phase 3
                replaced the previous bare ``ValueError`` with a
                structured ``ValidationException``; PROJ-395 MAJ-012
                corrects this docstring.

        Returns:
            Planet object if found, None if not found and required=False.

        Raises:
            ValidationException: If planet not found and required=True
                (MISSING_ENTITY). PROJ-381 Phase 3 (ERR-01-003).
        """
        planet = session._get_planet_by_id(planet_id)
        if planet is None:
            if required:
                raise ValidationException(
                    message="Planet not found.",
                    code=ErrorCode.MISSING_ENTITY.value,
                    context={"planet_id": planet_id},
                )
            return None

        return planet

    @staticmethod
    def _emit_validated_order(
        fleet,
        order_type,
        target,
        result: ValidationResult,
        log_label: str,
    ) -> ValidationResult:
        """Add an Order to fleet if validation passed; log either way.

        PROJ-319 (DUP-X-02): consolidated tail of every superweapon command
        handler. Handlers do their own resolve + validate, then call this to
        finish the "create-and-log if valid" pattern.

        Returns the same ``result`` argument unchanged so callers can write
        ``return self._emit_validated_order(...)``. **The result is propagated
        as-is — including any warnings the validator attached** — rather than
        being flattened to ``ValidationResult.success()``. Today validators
        return only clean-success or hard-error, so this contract is
        observationally identical; if a future validator emits valid-with-warnings
        results, callers will receive those warnings instead of a bare success.
        Do not change this contract without updating every direct + mission
        handler that currently relies on it (PROJ-375 review MAJ-001).
        """
        if result.is_valid:
            order = Order(order_type, target=target)
            fleet.add_order(order)
            logger.info("GameSession: Issued %s order for Fleet %s", log_label, fleet.id)
        return result

    @staticmethod
    def _resolve_build_entity(session: 'GameSession', entity_id: int, entity_type: str) -> Any:
        """Resolve a planet or fleet by ID and type.

        BUG-103: Extracted to BaseCommandHandler for shared use by all
        construction queue handlers.

        Args:
            session: Game session for lookups.
            entity_id: ID of the entity.
            entity_type: "planet" or "fleet".

        Returns:
            Planet or Fleet object, or None if not found.
        """
        if entity_type == "planet":
            return session._get_planet_by_id(entity_id)
        elif entity_type == "fleet":
            return session._get_fleet_by_id(entity_id)
        return None

    @staticmethod
    def _resolve_queue(entity, queue_id: Optional[str]) -> Optional[list]:
        """Find the correct construction queue for the entity.

        BUG-103: Extracted to BaseCommandHandler for shared use by all
        construction queue handlers. Supports multi-queue entities
        (e.g., planets with shipyard facilities).

        Args:
            entity: Planet or Fleet entity.
            queue_id: Optional queue identifier. If None, uses entity.construction_queue.

        Returns:
            The construction queue list, or None if not found.
        """
        # If no queue_id specified, use entity's main queue
        if queue_id is None:
            return getattr(entity, 'construction_queue', None)

        # For planets, check if queue_id matches a facility's instance_id
        if hasattr(entity, 'facilities'):
            for facility in entity.facilities:
                if getattr(facility, 'instance_id', None) == queue_id:
                    return getattr(facility, 'construction_queue', None)

        # Check if queue_id matches base queue pattern (e.g., "planet_100_base")
        base_queue_pattern = f"planet_{getattr(entity, 'id', '')}_base"
        if queue_id == base_queue_pattern:
            return getattr(entity, 'construction_queue', None)

        # Fallback to entity's main queue
        return getattr(entity, 'construction_queue', None)

    @staticmethod
    def _resolve_queue_owner(entity, queue_id: Optional[str]) -> Any:
        """Find the entity that *owns* a queue (i.e., where the per-queue
        flags like FEAT-17's `construction_queue_paused` live).

        Mirrors `_resolve_queue` but returns the owner object, not the
        list. For planet base / fleet queues that's the entity itself; for
        a facility queue that's the matching `PlanetaryFacility`.

        Args:
            entity: Planet or Fleet entity.
            queue_id: Optional queue identifier. None / planet base pattern
                / fleet yard ids → the entity itself; a facility
                instance_id → that facility.

        Returns:
            The Planet, Fleet, or PlanetaryFacility that owns the queue,
            or None if `queue_id` references a facility that doesn't exist.
        """
        if queue_id is None:
            return entity

        # Facility queue: queue_id matches a facility instance_id
        if hasattr(entity, 'facilities'):
            for facility in entity.facilities:
                if getattr(facility, 'instance_id', None) == queue_id:
                    return facility

        # Planet base queue id pattern → planet itself
        base_queue_pattern = f"planet_{getattr(entity, 'id', '')}_base"
        if queue_id == base_queue_pattern:
            return entity

        # Fleet yard ids ("fleet_<id>_yard_<n>") → the fleet itself.
        # Fleet yards share one queue, so any fleet-yard queue_id resolves
        # to the same Fleet. Catch this with a generic prefix check rather
        # than reconstructing the exact id.
        if isinstance(queue_id, str) and queue_id.startswith(f"fleet_{getattr(entity, 'id', '')}_yard_"):
            return entity

        return None

    @staticmethod
    def _build_colonize_target(planet, cmd) -> Any:
        """Build COLONIZE order target — Planet or dict with amounts.

        If population_amount or cargo_amounts are specified on the command,
        wraps the planet in a dict so the colonize handler can extract the
        amounts. Otherwise returns the Planet directly for backward
        compatibility.
        """
        if cmd.population_amount is not None or cmd.cargo_amounts is not None:
            return {
                'planet': planet,
                'population': cmd.population_amount,
                'cargo': cmd.cargo_amounts,
            }
        return planet


class CommandHandlerRegistry:
    """Registry for command handlers with dispatch capability."""

    def __init__(self):
        self._handlers: Dict[str, ICommandHandler] = {}

    def register(self, command_name: str, handler: ICommandHandler) -> None:
        """Register a handler for a command type.

        Args:
            command_name: The command class name (e.g., 'IssueColonizeCommand').
            handler: Handler instance implementing ICommandHandler.
        """
        self._handlers[command_name] = handler

    def dispatch(self, command_name: str, session: 'GameSession', command: 'Command') -> ValidationResult:
        """Dispatch a command to its registered handler.

        Args:
            command_name: The command class name.
            session: The game session context.
            command: The command object.

        Returns:
            ValidationResult from the handler, or failure if no handler found.
        """
        handler = self._handlers.get(command_name)
        if handler is None:
            return ValidationResult.error(f"Unknown command type: {command_name}")
        return handler.execute(session, command)
