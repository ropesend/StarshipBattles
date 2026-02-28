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
    m_earth = 5.97e24
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
            # Format population with K/M suffixes
            if total_pop >= 1_000_000:
                pop_str = f"{total_pop / 1_000_000:.1f}M"
            elif total_pop >= 1_000:
                pop_str = f"{total_pop / 1_000:.0f}K"
            else:
                pop_str = str(total_pop)

            if max_pop >= 1_000_000:
                max_str = f"{max_pop / 1_000_000:.1f}M"
            elif max_pop >= 1_000:
                max_str = f"{max_pop / 1_000:.0f}K"
            else:
                max_str = str(max_pop)

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

                    if pop.count >= 1_000:
                        cnt_str = f"{pop.count / 1_000:.0f}K"
                    else:
                        cnt_str = str(pop.count)

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

    # Resources are displayed in the dedicated resource grid panel (PROJ-82)
    return text


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
    text += f"<b>Diam:</b> {star.diameter_hexes:.1f} Hex<br>"
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

    Args:
        fleet: Fleet object (IFleet protocol)

    Returns:
        HTML string with cargo summary, or empty string if no cargo
    """
    totals: dict[str, int] = {}
    for ship in fleet.ships:
        s: IShipInstance = ship
        # IShipInstance.cargo_contents is always present (Dict)
        for cargo_type, amount in s.cargo_contents.items():
            if amount > 0:
                totals[cargo_type] = totals.get(cargo_type, 0) + amount

    if not totals:
        return ""

    text = "<b>Cargo:</b><br>"
    for cargo_type, amount in totals.items():
        display_name = cargo_type.replace('_', ' ').title()
        text += f" {display_name}: {amount}<br>"

    return text


def _format_orders(fleet: IFleet) -> str:
    """
    Format fleet orders as numbered HTML list.

    Handles MOVE, COLONIZE, BUILD, TRANSFER, and generic order types.

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
            # PROJ-187: Display WARP order with target warp point hex
            text += f" {i+1}. WARP through {order.target}<br>"
        elif order.type == OrderType.COLONIZE:
            p_name = order.target.name if order.target else 'Unknown'
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
        elif order.type == OrderType.OPEN_WARP_POINT:
            if isinstance(order.target, dict):
                target_name = order.target.get('target_system_name', 'Unknown')
                text += f" {i+1}. OPEN WARP POINT -> {target_name}<br>"
            else:
                text += f" {i+1}. OPEN WARP POINT<br>"
        elif order.type == OrderType.CLOSE_WARP_POINT:
            dest = order.target if isinstance(order.target, str) else "Unknown"
            text += f" {i+1}. CLOSE WARP POINT -> {dest}<br>"
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

    # Travel range
    speed = int(fleet.speed)
    fuel = fleet.fuel_endurance()
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
