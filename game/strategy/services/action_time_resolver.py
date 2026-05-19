"""
ActionTimeResolver - Resolves action_time for tick-based order execution.

PROJ-187: Strategy Orders Tick-Based Action System
PROJ-238: Unified to handle both fleet and planet orders.
PROJ-424 Phase 3: ``ORDER_TO_ABILITY_MAP`` and ``_build_order_to_ability_map``
removed. The resolver now reads ``order_metadata.order_to_ability_map`` at
CALL time, so ``command_registry.register(..., replace=True)`` mod overlays
are visible immediately. The previous import-time snapshot was the single
most dangerous stale-snapshot in the codebase (TD-03).
PROJ-429 / TD-07 Phase 4: ``ORDER_TO_TIME_FIELD`` removed entirely.
The per-ability action-time field name comes from
``ability_metadata.ability_action_time_field(name)``; for
ACTIVATE_ABILITY / DEACTIVATE_ABILITY the per-ability ``EnergyFacet``
declares ``activation_time_field`` and ``deactivation_time_field``.

This service looks up the action_time for a given order by finding the
relevant ability on the entity's components. Each strategic action has an
action_time that determines how many ticks it takes to complete.

Action times are defined on component abilities in components.json:
- ColonizePlanet: {"planet_type": "CONTINENTAL", "action_time": 2}
- DestroyPlanet: {"action_time": 3}
- PlanetaryShield: {"activation_time": 50, "deactivation_time": 10}
etc.
"""
from typing import TYPE_CHECKING, Any, Dict, Optional

from game.core.patterns.layer_iterator import iter_components
from game.strategy.services.ability_metadata import (
    ability_action_time_field,
    get_ability_metadata,
)
from game.strategy.services.component_abilities import (
    iterate_design_components,
)
from game.strategy.data.order_types import OrderType
from game.strategy.engine.commands.order_metadata_view import order_metadata

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.planet import Planet
    from game.strategy.data.order_types import Order


def _activate_time_field(ability_name: str, *, activating: bool) -> str:
    """Return the ``ability_data`` field name to read for an
    ACTIVATE_ABILITY / DEACTIVATE_ABILITY order.

    Sources the field name from the per-ability ``EnergyFacet`` in the
    unified ``AbilityMetadataRegistry``.

    PROJ-429 Phase 8 (Codex follow-up): if ``ability_name`` is not
    registered, OR is registered without an ``EnergyFacet``, raise
    ``ValueError``. The previous literal fallback
    (``'activation_time'``/``'deactivation_time'``) silently papered
    over caller/registry drift — an unregistered energy ability
    happened to work today because the facet defaults match the
    literals, but the moment a new energy ability declares a
    non-default field name a stale caller would read the wrong field
    with no error. Fail fast instead.
    """
    meta = get_ability_metadata(ability_name)
    if meta is None:
        raise ValueError(
            f"ActionTimeResolver: ACTIVATE_ABILITY/DEACTIVATE_ABILITY order "
            f"targets ability {ability_name!r}, which is NOT registered in "
            f"AbilityMetadataRegistry. Add an entry with an EnergyFacet to "
            f"game/strategy/services/ability_metadata.py."
        )
    if meta.energy is None:
        raise ValueError(
            f"ActionTimeResolver: ACTIVATE_ABILITY/DEACTIVATE_ABILITY order "
            f"targets ability {ability_name!r}, which IS registered in "
            f"AbilityMetadataRegistry but carries no EnergyFacet. Only "
            f"energy-cycling abilities (those declaring activation/"
            f"deactivation timings) can be (de)activated."
        )
    return (
        meta.energy.activation_time_field
        if activating
        else meta.energy.deactivation_time_field
    )


class ActionTimeResolver:
    """Resolves action_time for tick-based order execution.

    PROJ-238: Unified resolver for both fleet and planet orders.
    Looks up the action_time from the relevant ability on either
    fleet ships or planet facilities, depending on entity type.
    """

    @staticmethod
    def resolve_action_time(
        entity,
        order: 'Order',
        component_registry: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Resolve the action_time for a given order.

        PROJ-238: Accepts either Fleet or Planet as entity.

        Args:
            entity: The Fleet or Planet executing the order.
            order: The Order being executed.
            component_registry: Optional component registry for ability lookup.

        Returns:
            Integer action_time (ticks required to complete the action).
        """
        # Movement orders are handled by movement engine, not action engine
        if order.type in order_metadata.movement_order_types:
            return 0

        # Generic ability toggle: read ability name from order target.
        # PROJ-429 / TD-07 Phase 4: the time-field name is read from the
        # per-ability ``EnergyFacet`` in the unified registry, not a
        # hardcoded literal.
        if order.type in (OrderType.ACTIVATE_ABILITY, OrderType.DEACTIVATE_ABILITY):
            target = order.target if isinstance(order.target, dict) else {}
            ability_name = target.get('ability_name', '')
            if not ability_name:
                return 1
            time_field = _activate_time_field(
                ability_name,
                activating=(order.type == OrderType.ACTIVATE_ABILITY),
            )
            return ActionTimeResolver._find_planet_ability_time(
                entity, order, ability_name, time_field, component_registry
            )

        # Get the ability name for this order type. Read the map at call
        # time — PROJ-424 Phase 3 deletes the import-time snapshot, so a
        # ``command_registry.register(..., replace=True)`` overlay is
        # visible here immediately.
        ability_name = order_metadata.order_to_ability_map.get(order.type)
        if ability_name is None:
            return 1

        # Determine the time field to extract. PROJ-429 / TD-07 Phase 4
        # deletes the empty ``ORDER_TO_TIME_FIELD`` extension point. The
        # per-ability field is read from the unified registry.
        time_field = ability_action_time_field(ability_name)

        # Search entity's components (ships for fleets, facilities for planets)
        # PROJ-238: Use order type to determine search path (avoids MagicMock hasattr issues).
        # QA Observation B: FMS orders (LAY_MINES, LAUNCH_*, RECOVER_*) can
        # be issued from either a fleet or a planet — detect from the
        # entity itself rather than the order type. ``Planet`` has
        # ``facilities`` (a list); ``Fleet`` has ``ships``.
        if order.type in order_metadata.planet_action_order_types:
            return ActionTimeResolver._find_planet_ability_time(
                entity, order, ability_name, time_field, component_registry
            )
        if hasattr(entity, "facilities") and not hasattr(entity, "ships"):
            return ActionTimeResolver._find_planet_ability_time(
                entity, order, ability_name, time_field, component_registry
            )
        return ActionTimeResolver._find_fleet_ability_time(
            entity, ability_name, time_field, component_registry or {}
        )

    @staticmethod
    def _find_fleet_ability_time(
        fleet: 'Fleet',
        ability_name: str,
        time_field: str,
        component_registry: Dict[str, Any]
    ) -> int:
        """Find action_time from the first ship with the specified ability."""
        for ship in fleet.ships:
            for _comp_entry, _comp_def, abilities in iterate_design_components(
                ship.design_data, component_registry
            ):
                if ability_name in abilities:
                    ability_data = abilities[ability_name]
                    return ActionTimeResolver._extract_time(ability_data, time_field)
        return 1

    @staticmethod
    def _find_planet_ability_time(
        planet: 'Planet',
        order: 'Order',
        ability_name: str,
        time_field: str,
        component_registry: Optional[Dict[str, Any]] = None
    ) -> int:
        """Find action_time from the target facility's components.

        PROJ-238: Searches facilities for the ability, optionally filtering
        by the target facility specified in order.target.
        """
        # Find target facility if specified
        target = order.target
        facility_id = None
        if isinstance(target, dict):
            facility_id = target.get('facility_instance_id')

        facilities_to_search = planet.facilities
        if facility_id:
            facilities_to_search = [
                f for f in planet.facilities
                if f.instance_id == facility_id
            ]

        for facility in facilities_to_search:
            if not facility.is_operational:
                continue
            for comp in iter_components(facility.design_data):
                abilities = _get_abilities(comp, component_registry)
                ability_data = abilities.get(ability_name)
                if isinstance(ability_data, dict):
                    time_value = ability_data.get(time_field)
                    if isinstance(time_value, (int, float)) and time_value > 0:
                        return int(time_value)

        return 1

    @staticmethod
    def _extract_time(ability_data: Any, time_field: str = 'action_time') -> int:
        """Extract time value from ability data.

        Args:
            ability_data: The ability data (dict, bool, or string).
            time_field: The field name to extract (default 'action_time').

        Returns:
            Time value, defaults to 1.
        """
        if isinstance(ability_data, dict):
            return ability_data.get(time_field, 1)
        return 1


def _get_abilities(comp, component_registry: Optional[Dict[str, Any]] = None) -> dict:
    """Extract abilities from a component entry.

    Delegates to centralized extract_abilities_from_component().
    """
    from game.strategy.services.component_abilities import extract_abilities_from_component
    return extract_abilities_from_component(comp, component_registry)
