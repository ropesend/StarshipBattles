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

from game.core.hex_math import HexCoord, hex_distance
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType

logger = logging.getLogger(__name__)
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.galaxy import Galaxy, WarpPoint
from game.strategy.events.event_types import EventType, EventCategory
from game.strategy.services.superweapon_registry import (
    SuperweaponSpec,
    find_superweapon_spec,
)
from game.strategy.validation.superweapon_validator import SuperweaponValidator
from game.strategy.data.pathfinding import get_system_at_hex

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire


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

    def __init__(self, event_bus=None):
        """Initialize the superweapon order processor.

        Args:
            event_bus: Optional EventBus for structured event logging.
        """
        self._event_bus = event_bus

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
               'planet' → must not be None; 'dict' → must be dict (with
               legacy plain-string passthrough for CLOSE_WARP_POINT);
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
                # CLOSE_WARP_POINT preserves a legacy plain-string back-compat
                # path; the precheck closure validates whether the raw value
                # has a usable destination_id. OPEN_WARP_POINT rejects
                # non-dict outright.
                if spec.order_type == OrderType.CLOSE_WARP_POINT:
                    pass
                else:
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
        system = get_system_at_hex(galaxy, fleet.location)
        if system is not None:
            return f"System {system.name}"
        return "System"

    def process_implode_planet(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'],
        component_registry: Optional[Dict[str, Any]] = None
    ) -> SuperweaponResult:
        """Process an IMPLODE_PLANET order via spec-driven dispatch.

        Destroys the target planet; ship preserved for reuse.
        """
        spec = find_superweapon_spec(OrderType.IMPLODE_PLANET)

        def _effect(*, fleet, empire, galaxy, empires, order, ship, component_registry):
            target_planet = order.target
            # Remove planet from colony list if owned (iterate all empires
            # to catch enemy planets).
            if target_planet.owner_id is not None:
                for emp in empires:
                    if target_planet in emp.colonies:
                        emp.colonies.remove(target_planet)
            galaxy.unregister_planet(target_planet)
            return {
                "event_message": f"Planet {target_planet.name} destroyed",
                "log_message": f"Planet {target_planet.name} destroyed by fleet {fleet.id}",
                "planet_id": target_planet.id,
                "planet_name": target_planet.name,
            }

        return self.execute_superweapon(
            fleet, empire, galaxy, empires, spec, _effect, component_registry
        )

    def process_stellerate_star(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'],
        component_registry: Optional[Dict[str, Any]] = None
    ) -> SuperweaponResult:
        """Process a STELLERATE_STAR order via spec-driven dispatch.

        Suicide weapon: destroys all stars and planets in the system and
        destroys ALL fleets within the 50-hex system radius (including the
        acting fleet) via SystemDestroyer. Warp points preserved.

        Spec ``ability_name=None``; the ability-ship lookup is skipped.
        Spec ``consume_ship=True``; the dispatcher emits the STAR_DESTROYED
        event ad-hoc and skips ``_finalize_superweapon`` (the fleet is
        already gone, and the order MUST stay un-popped to match the
        pre-refactor semantics pinned by Phase 1 characterization tests).
        """
        spec = find_superweapon_spec(OrderType.STELLERATE_STAR)

        def _precheck(*, fleet, empire, galaxy, empires, order, component_registry):
            if get_system_at_hex(galaxy, fleet.location) is None:
                return SuperweaponResult(success=False, message="Fleet not at a star system")
            return None

        def _effect(*, fleet, empire, galaxy, empires, order, ship, component_registry):
            system = get_system_at_hex(galaxy, fleet.location)
            system_name = system.name

            # PROJ-277: SystemDestroyer collects-then-mutates so every fleet
            # within the 50-hex radius is destroyed.
            from game.strategy.services.system_destroyer import (
                collect_system_contents,
                destroy_system,
            )
            plan = collect_system_contents(system, galaxy, empires)
            destroy_system(plan, galaxy, empires, event_bus=self._event_bus)

            return {
                "event_message": f"Star system {system_name} destroyed",
                "log_message": f"Star system {system_name} stellerated by fleet {fleet.id}",
                "system_name": system_name,
                "location_name": system_name,
            }

        return self.execute_superweapon(
            fleet, empire, galaxy, empires, spec, _effect, component_registry,
            precheck_fn=_precheck,
        )

    def process_open_warp_point(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'] = None,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> SuperweaponResult:
        """Process an OPEN_WARP_POINT order via spec-driven dispatch.

        Creates bidirectional warp points between current system and target
        system. Ship preserved for reuse.
        """
        spec = find_superweapon_spec(OrderType.OPEN_WARP_POINT)

        def _precheck(*, fleet, empire, galaxy, empires, order, component_registry):
            if get_system_at_hex(galaxy, fleet.location) is None:
                return SuperweaponResult(success=False, message="Fleet not at a star system")
            # Pre-refactor parity: target-system existence is validated
            # BEFORE ability-ship lookup, so "Target system not found" beats
            # "No ship with OpenWarpPoint ability" when both would fail.
            target_system_name = order.target.get('target_system_name', '')
            if galaxy.name_map.get(target_system_name) is None:
                return SuperweaponResult(
                    success=False,
                    message=f"Target system '{target_system_name}' not found",
                )
            return None

        def _effect(*, fleet, empire, galaxy, empires, order, ship, component_registry):
            params = order.target  # dispatcher already validated isinstance(dict)
            target_system_name = params.get('target_system_name', '')

            current_system = get_system_at_hex(galaxy, fleet.location)
            target_system = galaxy.name_map[target_system_name]

            # Calculate warp point locations.
            # Near-end: at fleet's local position within current system.
            fleet_local = fleet.location - current_system.global_location
            near_wp = WarpPoint(target_system.name, fleet_local)

            # Far-end: direction from target back toward current, scaled to
            # typical orbit distance (6 hexes).
            direction_q = current_system.global_location.q - target_system.global_location.q
            direction_r = current_system.global_location.r - target_system.global_location.r
            dist = max(abs(direction_q), abs(direction_r), 1)
            orbit_distance = 6
            far_q = round(direction_q / dist * orbit_distance)
            far_r = round(direction_r / dist * orbit_distance)
            far_wp = WarpPoint(current_system.name, HexCoord(far_q, far_r))

            current_system.warp_points.append(near_wp)
            target_system.warp_points.append(far_wp)

            return {
                "event_message": f"Warp point opened to {target_system.name}",
                "log_message": (
                    f"Warp point opened between {current_system.name} "
                    f"and {target_system.name}"
                ),
                "source_system": current_system.name,
                "target_system": target_system.name,
            }

        return self.execute_superweapon(
            fleet, empire, galaxy, empires or [], spec, _effect, component_registry,
            precheck_fn=_precheck,
        )

    def process_close_warp_point(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'] = None,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> SuperweaponResult:
        """Process a CLOSE_WARP_POINT order via spec-driven dispatch.

        Removes both ends of the warp link; ship preserved for reuse.
        Strictly validates the fleet is at the exact warp-point sector
        (hex) — not just the right system — to defend against reordered
        moves that would close the wrong warp point.
        """
        spec = find_superweapon_spec(OrderType.CLOSE_WARP_POINT)

        def _parse_close_target(target):
            """Parse target into (destination_id, expected_hex). Legacy
            back-compat: a plain string target was the pre-PROJ-228 form.
            """
            if isinstance(target, dict):
                destination_id = target.get('destination_id', '')
                hex_data = target.get('target_hex')
                expected_hex = HexCoord(hex_data['q'], hex_data['r']) if hex_data else None
            else:
                destination_id = target
                expected_hex = None
            return destination_id, expected_hex

        def _precheck(*, fleet, empire, galaxy, empires, order, component_registry):
            destination_id, _expected_hex = _parse_close_target(order.target)
            if not destination_id:
                return SuperweaponResult(success=False, message="No destination specified")
            if get_system_at_hex(galaxy, fleet.location) is None:
                return SuperweaponResult(success=False, message="Fleet not at a star system")
            return None

        def _effect(*, fleet, empire, galaxy, empires, order, ship, component_registry):
            destination_id, expected_hex = _parse_close_target(order.target)
            current_system = get_system_at_hex(galaxy, fleet.location)

            # Strict sector-level validation: fleet must be AT the warp
            # point hex, not just somewhere in the system.
            if expected_hex and fleet.location != expected_hex:
                logger.warning(
                    f"Fleet {fleet.id}: Expected to be at sector {expected_hex} but is at "
                    f"sector {fleet.location}, canceling CLOSE_WARP_POINT order"
                )
                return SuperweaponResult(
                    success=False,
                    message=(
                        f"Fleet is at sector {fleet.location} but order targets "
                        f"warp point at sector {expected_hex}"
                    ),
                )

            galaxy.remove_warp_link(current_system.name, destination_id)

            return {
                "event_message": f"Warp point to {destination_id} closed",
                "log_message": (
                    f"Warp point closed between {current_system.name} "
                    f"and {destination_id}"
                ),
                "source_system": current_system.name,
                "target_system": destination_id,
            }

        return self.execute_superweapon(
            fleet, empire, galaxy, empires or [], spec, _effect, component_registry,
            precheck_fn=_precheck,
        )

    def process_create_dyson_sphere(
        self,
        fleet: Fleet,
        empire: 'Empire',
        galaxy: Galaxy,
        empires: List['Empire'],
        component_registry: Optional[Dict[str, Any]] = None
    ) -> SuperweaponResult:
        """Process a CREATE_DYSON_SPHERE order via spec-driven dispatch.

        Removes star and nearby planets (within zone radius), creates a
        Dyson Sphere planet at system center using the race's ideal
        environmental conditions (or sensible defaults). Ship preserved.
        """
        spec = find_superweapon_spec(OrderType.CREATE_DYSON_SPHERE)

        def _precheck(*, fleet, empire, galaxy, empires, order, component_registry):
            system = get_system_at_hex(galaxy, fleet.location)
            if system is None:
                return SuperweaponResult(success=False, message="Fleet not at a star system")
            if not system.stars:
                return SuperweaponResult(success=False, message="System has no stars")
            return None

        def _effect(*, fleet, empire, galaxy, empires, order, ship, component_registry):
            system = get_system_at_hex(galaxy, fleet.location)
            primary_star = system.stars[0]
            star_loc = primary_star.location

            # Remove planets within zone radius (radius_hexes=6 -> 91 hexes,
            # center + 5 rings).
            dyson_radius = 5
            planets_to_remove = [
                planet for planet in system.planets
                if hex_distance(planet.location, star_loc) <= dyson_radius
            ]
            for planet in planets_to_remove:
                if planet.owner_id is not None:
                    for emp in empires:
                        if planet in emp.colonies:
                            emp.colonies.remove(planet)
                galaxy.unregister_planet(planet)

            system.stars = []

            # PROJ-283 Phase 4: registry-driven preferences.
            race = empire.race_config if empire else None
            if race:
                prefs = race.preferences
                gravity = prefs["gravity"].setpoint
                temperature = prefs["temperature"].setpoint
                water = prefs["water"].setpoint
                atmosphere = {
                    factor_id.split(".", 1)[1]: pref.setpoint
                    for factor_id, pref in prefs.items()
                    if factor_id.startswith("gas.") and pref.setpoint > 0
                }
            else:
                gravity = 9.81  # 1g
                temperature = 288.0  # ~15°C
                water = 0.3
                atmosphere = {"O2": 21000.0, "N2": 79000.0}  # Earth-like (Pa)

            dyson = Planet(
                name=f"Dyson Sphere ({system.name})",
                location=HexCoord(0, 0),
                orbit_distance=0,
                mass=2e30,
                radius=1.5e11,
                surface_area=1e18,
                density=1.0,
                surface_gravity=gravity,
                surface_pressure=101325.0,
                surface_temperature=temperature,
                surface_water=water,
                atmosphere=atmosphere,
                tectonic_activity=0.0,
                magnetic_field=1.0,
                planet_type=PlanetType.DYSON_SPHERE,
                image_id="Sphereworld_Portrait.png",
                radius_hexes=6,
            )
            system.planets.append(dyson)
            galaxy.register_planet(system, dyson)

            return {
                "event_message": f"Dyson Sphere created in {system.name}",
                "log_message": f"Dyson Sphere created in {system.name}",
                "system_name": system.name,
                "planet_id": dyson.id,
                "planet_name": dyson.name,
            }

        return self.execute_superweapon(
            fleet, empire, galaxy, empires, spec, _effect, component_registry,
            precheck_fn=_precheck,
        )

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
        system = get_system_at_hex(galaxy, fleet_location) if galaxy else None
        if system is None:
            return None
        planets = getattr(system, 'planets', [])
        if not isinstance(planets, list):
            return None
        for planet in planets:
            return planet
        return None
