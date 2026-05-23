"""
SuperweaponOrderProcessor - Processes superweapon orders during turn execution.

PROJ-102 Phase 6: Turn execution logic for strategic superweapon orders.

Each superweapon order executes a galaxy-altering effect (destroy planet,
destroy star, open/close warp points, or create Dyson Sphere).
Only stellerate_star consumes the ship; other superweapons preserve the
ship for reuse. (Self-destruct was lifted to `order_handlers/self_destruct.py`
in PROJ-368 Phase 2.)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING
import logging

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType

logger = logging.getLogger(__name__)
from game.strategy.data.planet import Planet
from game.strategy.data.galaxy import Galaxy
from game.strategy.events.event_types import EventCategory
from game.strategy.services.superweapon_registry import SuperweaponSpec
from game.strategy.validation.superweapon_validator import SuperweaponValidator
from game.strategy.services.galaxy_pathfinding_service import GalaxyPathfindingService

if TYPE_CHECKING:
    from game.core.protocols.strategy_mutators import IEmpireMutator
    from game.strategy.data.empire import Empire
    from game.strategy.data.star_system import StarSystem
    from game.strategy.services.fleet_navigation_service import (
        FleetNavigationService,
    )


@dataclass
class SuperweaponResult:
    """Result of a superweapon order execution."""
    success: bool
    fleet_consumed: bool = False
    message: str = ""


class SuperweaponOrderProcessor:
    """
    Processor for superweapon order execution during turn processing.

    Each method handles a specific superweapon type:
    - process_implode_planet() - Destroy a target planet
    - process_stellerate_star() - Destroy star and everything in system (suicide)
    - process_open_warp_point() - Create warp link between two systems
    - process_close_warp_point() - Remove warp link between two systems
    - process_create_dyson_sphere() - Encase star in Dyson Sphere

    Self-destruct was lifted to `order_handlers/self_destruct.py` in
    PROJ-368 Phase 2; it is no longer routed through this processor.
    """

    def __init__(
        self,
        event_bus: Optional[Any] = None,
        empire_mutator: Optional[Any] = None,
        nav_service: Optional[Any] = None,
    ) -> None:
        """Initialize the superweapon order processor.

        Args:
            event_bus: Optional EventBus for structured event logging.
            empire_mutator: PROJ-370 IEmpireMutator. Lazy-defaulted.
            nav_service: ``FleetNavigationService`` used by warp-graph
                mutation handlers (#31) to broadcast path invalidation.
                Lazy-defaulted.
        """
        self._event_bus = event_bus
        self._empire_mutator = empire_mutator
        self._nav_service = nav_service

    def _get_empire_mutator(self) -> "IEmpireMutator":
        if self._empire_mutator is None:
            from game.strategy.services.empire_write_service import (
                EmpireWriteService,
            )
            self._empire_mutator = EmpireWriteService()
        return self._empire_mutator

    def _get_nav_service(self) -> "FleetNavigationService":
        if self._nav_service is None:
            from game.strategy.services.fleet_navigation_service import (
                FleetNavigationService,
            )
            self._nav_service = FleetNavigationService()
        return self._nav_service

    def _finalize_superweapon(
        self,
        fleet: Fleet,
        empire: 'Empire',
        ship,
        event_type,
        event_message: str,
        log_message: str,
        consume_ship: bool = True,
        **event_kwargs
    ) -> SuperweaponResult:
        """
        Finalize superweapon execution after effect is applied.

        Common end-pattern for superweapon methods:
        1. Optionally remove ship from fleet (if consume_ship=True)
        2. Pop order
        3. Check if fleet is empty
        4. Remove empty fleet from empire (SG-003 fix)
        5. Log event
        6. Return result

        Args:
            fleet: Fleet with superweapon order
            empire: Empire that owns the fleet
            ship: Ship to remove (the one carrying the superweapon)
            event_type: EventType for logging
            event_message: Message for log_event and result
            log_message: Message for logger.info
            consume_ship: If True, remove the ship from the fleet (default).
                Only stellerate_star (suicide weapon) should consume.
            **event_kwargs: Additional kwargs for log_event

        Returns:
            SuperweaponResult with success=True and fleet_consumed flag.
        """
        # FEAT-04: Capture location before fleet may be consumed
        fleet_loc = fleet.location

        # Remove ship only if this superweapon consumes it
        if consume_ship and ship:
            fleet.remove_ship(ship)

        # Pop order
        fleet.pop_order()

        # Check if fleet is now empty
        fleet_consumed = len(fleet.ships) == 0

        # Clean up empty fleet (SG-003 fix)
        if fleet_consumed:
            empire.remove_fleet(fleet, event_bus=self._event_bus)

        # Log
        logger.info(log_message)
        if self._event_bus:
            self._event_bus.log_event(
                event_type,
                category=EventCategory.SUPERWEAPONS,
                empire_id=empire.id,
                message=event_message,
                fleet_id=fleet.id,
                location_hex=[fleet_loc.q, fleet_loc.r],
                **event_kwargs
            )

        return SuperweaponResult(
            success=True,
            fleet_consumed=fleet_consumed,
            message=event_message
        )

    def execute_superweapon(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'],
        spec: SuperweaponSpec,
        effect_fn: Callable[..., Any],
        component_registry: Optional[Dict[str, Any]] = None,
        precheck_fn: Optional[Callable[..., Optional[SuperweaponResult]]] = None,
    ) -> SuperweaponResult:
        """Shared dispatcher for spec-driven superweapons (PROJ-364).

        Runs the common prologue in the order pinned by Phase 1
        characterization tests + the failure-message tests in
        ``test_superweapon_edge_cases.py``:

            1. Order present + matches ``spec.order_type``.
            2. Target shape resolution per ``spec.target_type``:
               'planet' → must not be None; 'dict' → must be dict;
               'none' → no check.
            3. Per-weapon precheck (``precheck_fn`` — may return
               ``SuperweaponResult(success=False, ...)`` to short-circuit).
               This is where weapon-specific early failures live, e.g.
               "Fleet not at a star system", "System has no stars",
               "No destination specified" — preserving the pre-refactor
               failure ordering and message text.
            4. Stabilizer block (via ``stabilizer_registry``).
            5. Ability-ship lookup (skipped if ``spec.ability_name is None``).
            6. Effect (``effect_fn``) — may return a failure result OR a
               dict of event kwargs.
            7. Finalize (``_finalize_superweapon``) for non-suicide weapons,
               OR ad-hoc event emit + ``fleet_consumed=True`` for suicide
               weapons (``spec.consume_ship=True``). Suicide weapons skip
               ``_finalize_superweapon`` because the effect closure has
               already destroyed the fleet, and the order MUST stay
               un-popped to match the pre-refactor STELLERATE_STAR
               behavior pinned by Phase 1's
               ``test_success_consumes_fleet_without_pop_order``.

        Both ``precheck_fn`` and ``effect_fn`` may return
        ``SuperweaponResult(success=False, ...)`` to short-circuit; on a
        precheck failure the order is popped and the result returned
        unchanged (mirrors the pre-refactor early-return pattern).
        """
        order = fleet.get_current_order()
        if order is None or order.type != spec.order_type:
            return SuperweaponResult(
                success=False,
                message=f"No {spec.order_type.name} order",
            )

        # Step 2: target shape resolution.
        if spec.target_type == "planet":
            if order.target is None:
                fleet.pop_order()
                return SuperweaponResult(success=False, message="No target planet")
        elif spec.target_type == "dict":
            if not isinstance(order.target, dict):
                # PROJ-445 Phase 2 (F-B-014): both OPEN_WARP_POINT and
                # CLOSE_WARP_POINT now require a dict target. The
                # CLOSE_WARP_POINT plain-string back-compat path was
                # retired — the only emitter has been the dict-shaped
                # IssueCloseWarpPointCommandHandler since PROJ-228.
                fleet.pop_order()
                return SuperweaponResult(
                    success=False,
                    message="Invalid warp point params",
                )

        # Step 3: per-weapon precheck (early failures, e.g. system missing).
        if precheck_fn is not None:
            precheck_result = precheck_fn(
                fleet=fleet,
                empire=empire,
                galaxy=galaxy,
                empires=empires,
                order=order,
                component_registry=component_registry,
            )
            if isinstance(precheck_result, SuperweaponResult) and not precheck_result.success:
                fleet.pop_order()
                return precheck_result

        # Step 4: stabilizer block. Reference planet is the order target for
        # IMPLODE_PLANET; otherwise the first planet in the system at the
        # fleet's location.
        if spec.order_type == OrderType.IMPLODE_PLANET:
            reference_planet = order.target
        else:
            reference_planet = self._get_reference_planet(fleet.location, galaxy)
        blocker = self._check_blocking_stabilizer(
            spec.order_type, reference_planet, galaxy, empires, component_registry
        )
        if blocker is not None:
            target_label = self._stabilizer_target_label(spec, order, fleet, galaxy)
            logger.info(
                f"{target_label} protected by {blocker.ability_name}, "
                f"canceling {spec.order_type.name}"
            )
            fleet.pop_order()
            return SuperweaponResult(
                success=False,
                message=f"{target_label} is protected by a {blocker.ability_name}",
            )

        # Step 5: ability-ship lookup (skipped for STELLERATE_STAR, which
        # has ability_name=None and dispatches via system_destroyer).
        ship = None
        if spec.ability_name is not None:
            if component_registry:
                ship = SuperweaponValidator.find_ship_with_ability(
                    fleet, spec.ability_name, component_registry
                )
            if ship is None:
                logger.warning(
                    f"Fleet {fleet.id}: No ship with {spec.ability_name} ability found, "
                    f"canceling order"
                )
                fleet.pop_order()
                return SuperweaponResult(
                    success=False,
                    message=f"No ship with {spec.ability_name} ability",
                )

        # Step 6: execute weapon-specific effect.
        effect_result = effect_fn(
            fleet=fleet,
            empire=empire,
            galaxy=galaxy,
            empires=empires,
            order=order,
            ship=ship,
            component_registry=component_registry,
        )

        # Effect short-circuited (e.g. target system not found, wrong sector).
        if isinstance(effect_result, SuperweaponResult):
            if not effect_result.success:
                fleet.pop_order()
            return effect_result

        # Otherwise effect_result is a dict of event kwargs.
        event_kwargs: Dict[str, Any] = effect_result

        # Suicide weapons: fleet has already been destroyed by the effect
        # closure (via system_destroyer). Do NOT route through
        # _finalize_superweapon — that would call fleet.pop_order() and
        # empire.remove_fleet() against an already-removed fleet, and the
        # order MUST stay un-popped to match pre-refactor STELLERATE_STAR
        # semantics (see Phase 1 characterization test).
        if spec.consume_ship:
            event_message = event_kwargs.pop("event_message", "")
            log_message = event_kwargs.pop("log_message", event_message)
            logger.info(log_message)
            if self._event_bus:
                self._event_bus.log_event(
                    spec.event_type,
                    category=EventCategory.SUPERWEAPONS,
                    empire_id=empire.id,
                    message=event_message,
                    fleet_id=fleet.id,
                    location_hex=[fleet.location.q, fleet.location.r],
                    **event_kwargs,
                )
            return SuperweaponResult(
                success=True,
                fleet_consumed=True,
                message=event_message,
            )

        # Non-suicide weapons: route through the shared finalize tail.
        return self._finalize_superweapon(
            fleet=fleet,
            empire=empire,
            ship=ship,
            event_type=spec.event_type,
            consume_ship=False,
            **event_kwargs,
        )

    @staticmethod
    def _get_system_at_hex(galaxy: Any, location: HexCoord) -> Optional["StarSystem"]:
        """Resolve the star system at ``location`` (or None).

        Thin pass-through to ``GalaxyPathfindingService.get_system_at_hex``
        kept on the processor as a single internal call site for handlers
        (PROJ-414: the deleted shim previously provided a module-level
        ``get_system_at_hex`` symbol; tests now patch
        ``GalaxyPathfindingService.get_system_at_hex`` directly).
        """
        return GalaxyPathfindingService(galaxy).get_system_at_hex(location)

    def _stabilizer_target_label(
        self, spec: SuperweaponSpec, order, fleet, galaxy
    ) -> str:
        """Build the human-readable target label used in the stabilizer
        block log line + result message. Mirrors the per-weapon strings
        that the pre-refactor code used so log/event payloads stay stable.
        """
        if spec.order_type == OrderType.IMPLODE_PLANET:
            target_planet = order.target
            return f"Planet {target_planet.name}" if target_planet else "Planet"
        # System-scope weapons: name of the system at fleet location.
        system = GalaxyPathfindingService(galaxy).get_system_at_hex(fleet.location)
        if system is not None:
            return f"System {system.name}"
        return "System"

    # ------------------------------------------------------------------
    # Per-superweapon dispatch wrappers.
    #
    # PROJ-396 Phase 3 (ex Task 5.4): the 5 ``process_*`` bodies live in
    # ``game.strategy.engine.superweapon_handlers`` as free functions
    # taking ``processor`` (this instance) as an explicit first parameter
    # — the closures previously closed over ``self`` for
    # ``self._event_bus`` / ``self._get_empire_mutator()`` /
    # ``self.execute_superweapon(...)`` etc. The wrappers below preserve
    # the public method shape that ``order_processor`` calls.
    # ------------------------------------------------------------------

    def process_implode_planet(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'],
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> SuperweaponResult:
        """Destroys the target planet; ship preserved for reuse."""
        from game.strategy.engine.superweapon_handlers import (
            process_implode_planet as _impl,
        )
        return _impl(self, fleet, empire, galaxy, empires, component_registry)

    def process_stellerate_star(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'],
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> SuperweaponResult:
        """Suicide weapon: destroys all stars/planets in the system and
        every fleet within the 50-hex system radius."""
        from game.strategy.engine.superweapon_handlers import (
            process_stellerate_star as _impl,
        )
        return _impl(self, fleet, empire, galaxy, empires, component_registry)

    def process_open_warp_point(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'] = None,
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> SuperweaponResult:
        """Creates bidirectional warp points between current and target
        system. Ship preserved for reuse."""
        from game.strategy.engine.superweapon_handlers import (
            process_open_warp_point as _impl,
        )
        return _impl(self, fleet, empire, galaxy, empires, component_registry)

    def process_close_warp_point(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'] = None,
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> SuperweaponResult:
        """Removes both ends of a warp link; ship preserved for reuse."""
        from game.strategy.engine.superweapon_handlers import (
            process_close_warp_point as _impl,
        )
        return _impl(self, fleet, empire, galaxy, empires, component_registry)

    def process_create_dyson_sphere(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'],
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> SuperweaponResult:
        """Removes star and nearby planets, creates a Dyson Sphere planet
        at system center. Ship preserved for reuse."""
        from game.strategy.engine.superweapon_handlers import (
            process_create_dyson_sphere as _impl,
        )
        return _impl(self, fleet, empire, galaxy, empires, component_registry)

    # PROJ-368 Phase 4: process_self_destruct DELETED. SELF_DESTRUCT now
    # routes through SelfDestructHandler at game.strategy.engine.
    # order_handlers.self_destruct.

    def _check_blocking_stabilizer(
        self,
        order_type: OrderType,
        reference_planet,
        galaxy,
        empires: List['Empire'],
        component_registry,
    ) -> Optional[Any]:
        """Delegate to StabilizerRegistry for order-blocking lookup.

        Centralizes the "what blocks what" mapping in
        `game/strategy/services/stabilizer_registry.py`. Handlers just pass
        their order type + a reference planet (for spatial scope resolution)
        and receive the blocking StabilizerSpec or None.

        `component_registry` MUST be threaded through — facility design_data
        typically stores bare component ids, so ability data is looked up
        via the registry. Omitting it silently hides every stabilizer
        (PROJ-277).
        """
        from game.strategy.services.stabilizer_registry import find_blocking_stabilizer
        return find_blocking_stabilizer(
            order_type, reference_planet, galaxy, empires, component_registry
        )

    def _get_reference_planet(self, fleet_location, galaxy) -> Optional[Planet]:
        """Find any planet in the system at fleet_location — needed so the
        strategic ability scanner can resolve system/sector scope from a
        concrete planet reference.

        Returns the first planet in the system, or None if there are none.
        """
        system = (
            GalaxyPathfindingService(galaxy).get_system_at_hex(fleet_location)
            if galaxy else None
        )
        if system is None:
            return None
        planets = getattr(system, 'planets', [])
        if not isinstance(planets, list):
            return None
        for planet in planets:
            return planet
        return None
