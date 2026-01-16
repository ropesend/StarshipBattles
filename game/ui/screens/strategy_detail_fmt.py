"""
Detail formatting utilities for strategy screen.

Functions for formatting HTML reports for planets, stars, fleets,
and other objects displayed in the detail panel.
"""
from game.strategy.data.fleet import OrderType


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


def format_planet_info(planet) -> str:
    """
    Format comprehensive planet information as HTML.

    Args:
        planet: Planet object

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

    if hasattr(planet, 'resources') and planet.resources:
        text += "<br><b>Resources:</b><br>"
        for r_name, r_data in planet.resources.items():
            qty = r_data['quantity']
            if qty >= 1000000:
                q_str = f"{qty/1000000:.1f}M"
            elif qty >= 1000:
                q_str = f"{qty/1000:.0f}k"
            else:
                q_str = str(qty)

            qual = r_data['quality']
            text += f" {r_name}: {q_str} (Q:{qual:.0f})<br>"

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


def format_fleet_info(fleet) -> str:
    """
    Format fleet information as HTML.

    Args:
        fleet: Fleet object

    Returns:
        HTML string with fleet details
    """
    text = f"<b>Fleet:</b> {fleet.id}<br>"
    text += f"<b>Owner:</b> {fleet.owner_id}<br>"
    text += f"<b>Ships:</b> {len(fleet.ships)}<br>"
    text += f"<b>Location:</b> {fleet.location}<br>"

    text += "<b>Orders:</b><br>"
    if fleet.orders:
        for i, order in enumerate(fleet.orders):
            if order.type == OrderType.MOVE:
                text += f" {i+1}. MOVE {order.target}<br>"
            elif order.type == OrderType.COLONIZE:
                p_name = order.target.name if hasattr(order.target, 'name') else "Unknown"
                text += f" {i+1}. COLONIZE {p_name}<br>"
            else:
                text += f" {i+1}. {order.type.name}<br>"
    else:
        text += " (No Orders)<br>"

    return text


def format_sector_environment_info(env) -> str:
    """
    Format sector environment information as HTML.

    Args:
        env: SectorEnvironment object with calculate_radiation method

    Returns:
        HTML string with environment details
    """
    spec = env.calculate_radiation()

    text = f"<b>Local Environment</b><br>"
    text += f"<b>System:</b> {env.system.name}<br>"
    text += f"<b>Local:</b> {env.local_hex}<br>"
    text += f"<br><b>Total Incident Radiation:</b><br>"
    text += f"{spec.get_total_output():.2e} W/m^2 (relative)<br>"

    return text


def format_warp_point_info(warp_point) -> str:
    """
    Format warp point information as HTML.

    Args:
        warp_point: WarpPoint object

    Returns:
        HTML string with warp point details
    """
    text = f"<b>Warp Point</b><br>"
    text += f"<b>To:</b> {warp_point.destination_id}<br>"
    text += f"<b>Local Loc:</b> {warp_point.location}<br>"
    return text


def get_label_for_object(obj) -> str:
    """
    Get a display label for any game object.

    Args:
        obj: Any game object (system, star, planet, fleet, etc.)

    Returns:
        Human-readable label string
    """
    if hasattr(obj, 'stars'):
        return f"System: {obj.name}"
    elif hasattr(obj, 'color') and hasattr(obj, 'mass'):
        return f"Star: {obj.name}"
    elif hasattr(obj, 'planet_type'):
        return f"Planet: {obj.name}"
    elif hasattr(obj, 'destination_id'):
        return f"Warp Point -> {obj.destination_id}"
    elif hasattr(obj, 'ships'):
        return f"Fleet {obj.id} ({len(obj.ships)})"
    elif hasattr(obj, 'calculate_radiation'):
        return "Local Radiation Analysis"
    return "Unknown Object"
