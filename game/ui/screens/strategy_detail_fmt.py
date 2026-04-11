"""
Detail formatting utilities for strategy screen.

Functions for formatting HTML reports for planets, stars, fleets,
and other objects displayed in the detail panel.

Cross-layer imports (acceptable for UI):
- OrderType: Runtime - formats order type display strings
- Protocols: Runtime - duck typing for object identification
"""
from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from game.core.constants import EARTH_MASS
from game.core.string_utils import display_name
from game.ui.utils.formatters import format_compact_number
from game.strategy.data.order_types import OrderType
from game.core.protocols import (
    is_star_system, is_star, is_planet, is_fleet,
    is_warp_point, is_sector_environment, is_storm
)

if TYPE_CHECKING:
    from game.core.protocols import IPlanet, IFleet, IFacility, IShipInstance


def format_spectrum_html(star) -> str:
    """
    Format star spectrum data as HTML.

    Args:
        star: Star object with spectrum attribute

    Returns:
        HTML string with spectrum intensity values
    """
    s = star.spectrum
    html = "<br><b>Spectrum Intensity (W/m^2 rel):</b><br>"
    html += f" Gamma: {s.gamma_ray:.2e}<br>"
    html += f" X-Ray: {s.xray:.2e}<br>"
    html += f" UV:    {s.ultraviolet:.2e}<br>"
    html += f" Blue:  {s.blue:.2e}<br>"
    html += f" Green: {s.green:.2e}<br>"
    html += f" Red:   {s.red:.2e}<br>"
    html += f" IR:    {s.infrared:.2e}<br>"
    html += f" Micro: {s.microwave:.2e}<br>"
    html += f" Radio: {s.radio:.2e}<br>"
    return html


def format_atmosphere_raw(planet) -> str:
    """
    Format planet atmosphere data as HTML.

    Args:
        planet: Planet object with atmosphere dict

    Returns:
        HTML string with atmosphere composition
    """
    html = f"<b>Atmosphere ({planet.total_pressure_atm:.2f} atm):</b><br>"
    for gas, pa in planet.atmosphere.items():
        html += f" {gas}: {pa:.1f} Pa<br>"
    return html


def format_planet_info(planet: IPlanet) -> str:
    """
    Format comprehensive planet information as HTML.

    Args:
        planet: Planet object (IPlanet protocol)

    Returns:
        HTML string with planet details
    """
    text = f"<b>Planet:</b> {planet.name}<br>"
    text += f"<b>Type:</b> {planet.planet_type.name}<br>"
    text += f"<b>Orbit:</b> Ring {planet.orbit_distance}<br>"

    # Mass formatting
    m_earth = EARTH_MASS
    m_jup = 1.89e27
    if planet.mass >= m_jup:
        m_str = f"{planet.mass/m_jup:.2f} M_Jup"
    elif planet.mass >= m_earth:
        m_str = f"{planet.mass/m_earth:.2f} M_Earth"
    else:
        m_str = f"{planet.mass/m_earth:.4f} M_Earth"

    text += f"<b>Mass:</b> {m_str}<br>"
    text += f"<b>Radius:</b> {planet.radius/1000.0:.0f} km<br>"
    text += f"<b>Gravity:</b> {planet.surface_gravity/9.81:.2f} g<br>"
    text += f"<b>Temp:</b> {int(planet.surface_temperature)} K<br>"
    text += f"<b>Water:</b> {planet.surface_water*100:.0f}%<br>"
    text += f"<b>Pressure:</b> {planet.total_pressure_atm:.2f} atm<br>"

    # Colony status and facilities (BUG-19 fix)
    # IPlanet.owner_id is always present (Optional[int])
    if planet.owner_id is not None:
        text += f"<br><b>Colony Status:</b> Owned<br>"

        # Population section - IPlanet.populations is always present (List)
        populations = planet.populations
        total_pop = sum(p.count for p in populations) if populations else 0
        max_pop = planet.max_population

        if total_pop > 0 or max_pop > 0:
            pop_str = format_compact_number(total_pop)
            max_str = format_compact_number(max_pop)

            text += f"<br><b>Population:</b> {pop_str} / {max_str}<br>"

            # Per-species breakdown
            if len(populations) > 0:
                for pop in populations:
                    # Happiness indicator
                    if pop.happiness >= 0.8:
                        h_icon = "+"
                    elif pop.happiness >= 0.4:
                        h_icon = "~"
                    else:
                        h_icon = "-"

                    cnt_str = format_compact_number(pop.count)

                    text += f" - {pop.race_id}: {cnt_str} [{h_icon}]<br>"

        # Show facilities/complexes list - IPlanet.facilities is always present (List)
        facilities = planet.facilities
        if facilities:
            text += "<br><b>Complexes:</b><br>"
            for facility in facilities:
                f: IFacility = facility
                f_name = f.name if f.name else f.design_id
                f_status = "Active" if f.is_operational else "Offline"
                text += f" - {f_name} ({f_status})<br>"
        else:
            text += "<br><b>Complexes:</b> None<br>"

    # PROJ-237: Energy & Shield display
    energy_cap = getattr(planet, 'energy_capacity', None)
    if isinstance(energy_cap, (int, float)) and energy_cap > 0:
        energy_val = getattr(planet, 'energy', 0.0)
        energy_pct = (energy_val / energy_cap * 100) if energy_cap > 0 else 0
        text += f"<br><b>Energy:</b> {energy_val:.0f} / {energy_cap:.0f} ({energy_pct:.0f}%)"

    # Show all toggleable ability statuses with tick progress
    _ALL_TOGGLEABLE = {
        'PlanetaryShield': 'Planetary Shield',
        **_ACTIVATABLE_DISPLAY_NAMES,
    }
    facilities = getattr(planet, 'facilities', None)
    if isinstance(facilities, list) and facilities:
        for ability_key, display_name in _ALL_TOGGLEABLE.items():
            if _planet_has_ability_facility(planet, ability_key):
                status = _get_ability_status_text(planet, ability_key)
                text += f"<br><b>{display_name}:</b> {status}"

    # Resources are displayed in the dedicated resource grid panel (PROJ-82)
    return text


def _planet_has_shield_facility(planet) -> bool:
    """Check if a planet has any facility with a PlanetaryShield ability.

    Checks both inline abilities in design_data and the component registry.
    """
    from game.core.patterns.layer_iterator import iter_components
    from game.strategy.services.component_inspector import get_component_abilities
    from game.core.registry import get_default_registry_provider

    # Try to get component registry for lookup
    component_registry = None
    try:
        provider = get_default_registry_provider()
        component_registry = provider.get_components()
    except Exception:
        pass

    for facility in planet.facilities:
        design_data = getattr(facility, 'design_data', None)
        if not isinstance(design_data, dict):
            continue
        for comp in iter_components(design_data):
            # Check inline abilities
            if isinstance(comp, dict) and 'PlanetaryShield' in comp.get('abilities', {}):
                return True
            # Check registry
            comp_id = comp.get('id', '') if isinstance(comp, dict) else str(comp)
            if comp_id and component_registry:
                comp_def = component_registry.get(comp_id)
                if comp_def and 'PlanetaryShield' in get_component_abilities(comp_def):
                    return True
    return False


def _get_system_ability_status(system) -> dict:
    """Scan all planets in a system for activatable abilities and their status.

    Returns dict mapping ability_key -> dict with 'status_text' str and 'planet_name' str.
    Only includes abilities that have facilities present. Status text includes
    tick progress for activating/deactivating abilities.
    """
    result = {}
    planets = getattr(system, 'planets', [])
    if not isinstance(planets, list):
        return result
    for planet in planets:
        for ability_key in _ACTIVATABLE_DISPLAY_NAMES:
            if _planet_has_ability_facility(planet, ability_key):
                status_text = _get_ability_status_text(planet, ability_key)
                if ability_key not in result:
                    result[ability_key] = {'status_text': status_text, 'planet_name': planet.name}
                elif 'Active' == status_text:
                    # Prefer showing "Active" over "Inactive" if multiple planets have it
                    result[ability_key] = {'status_text': status_text, 'planet_name': planet.name}
    return result


_ACTIVATABLE_DISPLAY_NAMES = {
    'GeologicStabilizer': 'Geologic Stabilizer',
    'StellarStabilizer': 'Stellar Stabilizer',
    'WarpFieldStabilizer': 'Warp Field Stabilizer',
    'GravityModifier': 'Gravity Modifier',
    'RadiationShield': 'Radiation Shield',
}


def _get_ability_status_text(planet, ability_name: str) -> str:
    """Get display status for a toggleable ability including tick progress.

    Reads from ComponentActivationState on facilities to show:
    - "Activating (100/250 ticks)" during activation
    - "Active" when fully active
    - "Deactivating (50/150 ticks)" during deactivation
    - "Inactive" when inactive
    """
    from game.strategy.data.component_activation_state import (
        ActivationPhase,
        ComponentActivationState,
    )

    # Scan facility component_states for this ability
    for facility in getattr(planet, 'facilities', []):
        for key, state_data in getattr(facility, 'component_states', {}).items():
            if not isinstance(state_data, dict):
                continue
            if state_data.get('ability_name') != ability_name:
                continue
            state = ComponentActivationState.from_dict(state_data)
            if state.phase == ActivationPhase.ACTIVATING:
                return f"Activating ({state.progress_ticks}/{state.required_ticks} ticks)"
            elif state.phase == ActivationPhase.ACTIVE:
                return "Active"
            elif state.phase == ActivationPhase.DEACTIVATING:
                return f"Deactivating ({state.progress_ticks}/{state.required_ticks} ticks)"

    # Fallback to planet-level active_abilities
    active_abilities = getattr(planet, 'active_abilities', {})
    return "Active" if active_abilities.get(ability_name, False) else "Inactive"


def _planet_has_ability_facility(planet, ability_key: str) -> bool:
    """Check if a planet has any facility with a specific ability."""
    from game.core.patterns.layer_iterator import iter_components
    from game.strategy.services.component_inspector import extract_abilities_from_component

    registries = None
    try:
        from game.core.registry import get_default_registry_manager
        registries = get_default_registry_manager()
    except Exception:
        pass

    for facility in getattr(planet, 'facilities', []):
        design_data = getattr(facility, 'design_data', None)
        if not isinstance(design_data, dict):
            continue
        for comp in iter_components(design_data):
            abilities = extract_abilities_from_component(comp, registries)
            if ability_key in abilities:
                return True
    return False


def format_star_system_info(system) -> str:
    """
    Format star system information as HTML.

    Args:
        system: StarSystem object

    Returns:
        HTML string with system details
    """
    primary = system.primary_star
    if primary:
        text = f"<b>System:</b> {system.name}<br>"
        text += f"<b>Primary:</b> {primary.name}<br>"
        text += f"<b>Type:</b> {primary.star_type.name}<br>"
        text += f"<b>Mass:</b> {primary.mass:.2f} Sol<br>"
        text += f"<b>Temp:</b> {int(primary.temperature)} K<br>"
        text += f"<b>Stars:</b> {len(system.stars)}<br>"
    else:
        text = f"<b>System:</b> {system.name}<br>(Empty System)"

    # Show system-wide stabilizer status
    _system_abilities = _get_system_ability_status(system)
    for ability_key, display_name in _ACTIVATABLE_DISPLAY_NAMES.items():
        if ability_key in _system_abilities:
            info = _system_abilities[ability_key]
            status = info.get('status_text', 'Inactive')
            planet_name = info.get('planet_name', '')
            text += f"<br><b>{display_name}:</b> {status} ({planet_name})"

    return text


def format_star_info(star) -> str:
    """
    Format individual star information as HTML.

    Args:
        star: Star object

    Returns:
        HTML string with star details
    """
    text = f"<b>Star:</b> {star.name}<br>"
    text += f"<b>Type:</b> {star.star_type.name}<br>"
    text += f"<b>Mass:</b> {star.mass:.2f} Sol<br>"
    text += f"<b>Temp:</b> {int(star.temperature)} K<br>"
    text += f"<b>Radius:</b> {star.radius_hexes} Hex<br>"
    return text


def _format_ship_groups(fleet: IFleet) -> str:
    """
    Format ship list grouped by design, sorted by mass descending.

    Args:
        fleet: Fleet object (IFleet protocol)

    Returns:
        HTML string with grouped ship list
    """
    if not fleet.ships:
        return "<b>Ships: None</b><br>"

    # Count ships per design_id
    design_counts = Counter(ship.design_id for ship in fleet.ships)

    # Collect display info per unique design (name + mass from first ship)
    design_info: dict[str, tuple[str, float]] = {}
    for ship in fleet.ships:
        s: IShipInstance = ship
        did = s.design_id
        if did not in design_info:
            # IShipInstance.design_data is always present (Dict)
            data = s.design_data or {}
            name = data.get('name', str(did)) if isinstance(data, dict) else str(did)
            stats = s.get_calculated_stats()
            raw_mass = stats.get('mass', 0) if isinstance(stats, dict) else 0
            mass = float(raw_mass) if isinstance(raw_mass, (int, float)) else 0.0
            design_info[did] = (name, mass)

    # Sort by mass descending, then name for stability
    sorted_designs = sorted(
        design_counts.keys(),
        key=lambda d: (-design_info[d][1], design_info[d][0]),
    )

    total = sum(design_counts.values())
    text = f"<b>Ships ({total}):</b><br>"
    for design_id in sorted_designs:
        name, _mass = design_info[design_id]
        count = design_counts[design_id]
        if count > 1:
            text += f" {name} x {count}<br>"
        else:
            text += f" {name}<br>"

    return text


def _format_cargo_summary(fleet: IFleet) -> str:
    """
    Format aggregated cargo summary across all ships in the fleet.

    Shows resource cargo, passengers, and carried items (drop pods).
    """
    totals: dict[str, int] = {}
    carried_items: dict[str, int] = {}  # name -> count

    for ship in fleet.ships:
        s: IShipInstance = ship
        for cargo_type, amount in s.cargo_contents.items():
            if amount > 0:
                totals[cargo_type] = totals.get(cargo_type, 0) + amount
        items = getattr(s, 'carried_items', None)
        if isinstance(items, list):
            for item in items:
                name = item.get('name', 'Unknown')
                carried_items[name] = carried_items.get(name, 0) + 1

    if not totals and not carried_items:
        return ""

    text = "<b>Cargo:</b><br>"
    for cargo_type, amount in totals.items():
        cargo_label = display_name(cargo_type)
        text += f" {cargo_label}: {amount}<br>"
    for name, count in carried_items.items():
        label = f"{name} x{count}" if count > 1 else name
        text += f" {label}<br>"

    return text


def _format_orders(fleet: IFleet) -> str:
    """
    Format fleet orders as numbered HTML list.

    Args:
        fleet: Fleet object (IFleet protocol)

    Returns:
        HTML string with formatted orders
    """
    text = "<b>Orders:</b><br>"
    if not fleet.orders:
        text += " (No Orders)<br>"
        return text

    for i, order in enumerate(fleet.orders):
        if order.type == OrderType.MOVE:
            text += f" {i+1}. MOVE {order.target}<br>"
        elif order.type == OrderType.WARP:
            text += f" {i+1}. WARP through {order.target}<br>"
        elif order.type == OrderType.MOVE_TO_FLEET:
            f_id = order.target.id if is_fleet(order.target) else "?"
            text += f" {i+1}. Intercept Fleet {f_id}<br>"
        elif order.type == OrderType.JOIN_FLEET:
            f_id = order.target.id if is_fleet(order.target) else "?"
            text += f" {i+1}. Join Fleet {f_id}<br>"
        elif order.type == OrderType.COLONIZE:
            target = order.target
            if isinstance(target, dict):
                planet_obj = target.get('planet')
                p_name = planet_obj.name if planet_obj else 'Any Planet'
            elif target and hasattr(target, 'name'):
                p_name = target.name
            else:
                p_name = 'Unknown'
            text += f" {i+1}. COLONIZE {p_name}<br>"
        elif order.type == OrderType.BUILD:
            queue = fleet.construction_queue
            text += f" {i+1}. BUILDING ({len(queue)} items)<br>"
        elif order.type == OrderType.TRANSFER:
            if isinstance(order.target, dict):
                direction = order.target.get('direction', '?')
                cargo_type = order.target.get('cargo_type', '?')
                amount = order.target.get('amount', 0)
                amt_str = str(amount) if amount > 0 else "All"
                text += f" {i+1}. {direction.upper()} {amt_str} {cargo_type}<br>"
            else:
                text += f" {i+1}. TRANSFER {order.target}<br>"
        elif order.type == OrderType.LOAD_POPULATION:
            text += f" {i+1}. Load Cargo<br>"
        elif order.type == OrderType.UNLOAD_POPULATION:
            text += f" {i+1}. Drop Cargo<br>"
        elif order.type == OrderType.OPEN_WARP_POINT:
            if isinstance(order.target, dict):
                target_name = order.target.get('target_system_name', 'Unknown')
                text += f" {i+1}. OPEN WARP POINT -> {target_name}<br>"
            else:
                text += f" {i+1}. OPEN WARP POINT<br>"
        elif order.type == OrderType.CLOSE_WARP_POINT:
            dest = order.target if isinstance(order.target, str) else "Unknown"
            text += f" {i+1}. CLOSE WARP POINT -> {dest}<br>"
        elif order.type == OrderType.IMPLODE_PLANET:
            p_name = order.target.name if is_planet(order.target) else 'Unknown'
            text += f" {i+1}. Implode {p_name}<br>"
        elif order.type == OrderType.STELLERATE_STAR:
            text += f" {i+1}. Stellerate Star<br>"
        elif order.type == OrderType.CREATE_DYSON_SPHERE:
            text += f" {i+1}. Create Dyson Sphere<br>"
        else:
            text += f" {i+1}. {order.type.name}<br>"

    return text


def format_fleet_info(fleet: IFleet) -> str:
    """
    Format comprehensive fleet information as HTML.

    Includes header, travel range, ship groups, cargo summary, and orders.

    Args:
        fleet: Fleet object (IFleet protocol)

    Returns:
        HTML string with fleet details
    """
    # Header
    text = f"<b>Fleet:</b> {fleet.id}<br>"
    text += f"<b>Owner:</b> {fleet.owner_id}<br>"
    text += f"<b>Location:</b> {fleet.location}<br>"

    # Travel range (PROJ-210: use fleet.resources delegate)
    speed = int(fleet.speed)
    fuel = fleet.resources.fuel_endurance()
    if fuel == -1:
        fuel_str = "unlimited fuel"
    else:
        fuel_str = f"{fuel} hex fuel"
    text += f"<b>Range:</b> {speed} hex/turn, {fuel_str}<br>"

    # Ship groups
    text += _format_ship_groups(fleet)

    # Cargo summary (omitted if empty)
    text += _format_cargo_summary(fleet)

    # Orders
    text += _format_orders(fleet)

    return text


def get_label_for_object(obj) -> str:
    """
    Get a display label for any game object.

    Args:
        obj: Any game object (system, star, planet, fleet, etc.)

    Returns:
        Human-readable label string
    """
    if is_star_system(obj):
        return f"System: {obj.name}"
    elif is_star(obj):
        return f"Star: {obj.name}"
    elif is_planet(obj):
        return f"Planet: {obj.name}"
    elif is_warp_point(obj):
        return f"Warp Point -> {obj.destination_id}"
    elif is_fleet(obj):
        return f"Fleet {obj.id} ({len(obj.ships)})"
    elif is_sector_environment(obj):
        return "Local Radiation Analysis"
    elif is_storm(obj):
        return f"Storm: {obj.name}"
    return "Unknown Object"
