"""Pure capability-driven builder for the planet right-click context menu.

QA Observation B. Mirrors :mod:`fleet_menu_items` but for planet-level
FMS actions exposed by planetary-complex facility components:

- Lay Mines        (StrategicMineLayer on a facility)
- Launch Fighters  (StrategicFighterLaunch on a facility)
- Launch Satellites (StrategicSatelliteLaunch on a facility)
- Recover Fighters (RecoverFighters on a facility AND a fighter_group
                    at the planet's global hex)
- Recover Satellites (RecoverSatellites on a facility AND a
                    satellite_group at the planet's global hex)

Planet rows carry a zero-arg callback rather than an :class:`InputAction`
since the FMS planet flows have no corresponding ``InputAction`` enum
value today (and the right-click menu is the only planet-side UI
surface for them).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from game.strategy.services.ability_sources.facility import FacilityAbilitySource


@dataclass(frozen=True)
class PlanetMenuItem:
    """One row in the planet context menu.

    Attributes:
        label: Display label, e.g. ``"Lay Mines"``.
        callback: Zero-arg callable invoked when the row is clicked.
    """

    label: str
    callback: Callable[[], None]


def _facility_has_ability(planet: Any, ability_name: str) -> bool:
    """Return True if any operational facility on ``planet`` exposes
    ``ability_name`` through its components.
    """
    facilities = getattr(planet, "facilities", None) or []
    for facility in facilities:
        if not getattr(facility, "is_operational", True):
            continue
        try:
            source = FacilityAbilitySource(facility=facility, planet=planet)
            abilities = source.get_abilities()
        except Exception:  # Intentional broad catch: missing registries / partial mocks in tests must not break menu construction.
            continue
        if ability_name in abilities:
            return True
    return False


def _global_hex(planet: Any, galaxy: Any) -> Any:
    """Best-effort resolve the planet's global hex.

    Uses ``planet.global_hex`` when present (tests set this directly);
    otherwise reconstructs via galaxy lookup; otherwise falls back to
    ``planet.location``.
    """
    gh = getattr(planet, "global_hex", None)
    if gh is not None:
        return gh
    # Reconstruct from system the planet belongs to.
    if galaxy is not None:
        for system in getattr(galaxy, "systems", None) or []:
            if planet in getattr(system, "planets", []):
                return system.global_location + planet.location
    return planet.location


def _matching_group_at_hex(
    planet: Any, galaxy: Any, group_kind: str,
) -> bool:
    """True if any owner-owned ``group_kind`` Fleet sits at the planet's hex."""
    if galaxy is None:
        return False
    target_hex = _global_hex(planet, galaxy)
    empires = getattr(galaxy, "empires", None) or []
    for emp in empires:
        if emp.id != planet.owner_id:
            continue
        for f in getattr(emp, "fleets", []):
            if getattr(f, "group_kind", "fleet") != group_kind:
                continue
            if f.location == target_hex:
                return True
    return False


def build_menu_items(
    planet: Any,
    galaxy: Any,
    callbacks: dict[str, Callable[[], None]],
) -> list[PlanetMenuItem]:
    """Return the ordered list of planet-menu rows.

    ``callbacks`` maps logical action names ("lay_mines",
    "launch_fighters", "launch_satellites", "recover_fighters",
    "recover_satellites") to a zero-arg callable. The UI layer supplies
    these callbacks (typically functions that open a quantity prompt
    dialog and dispatch the appropriate :class:`Issue*Command`).
    """
    rows: list[tuple[str, str, bool]] = [
        (
            "Lay Mines",
            "lay_mines",
            _facility_has_ability(planet, "StrategicMineLayer"),
        ),
        (
            "Launch Fighters",
            "launch_fighters",
            _facility_has_ability(planet, "StrategicFighterLaunch"),
        ),
        (
            "Launch Satellites",
            "launch_satellites",
            _facility_has_ability(planet, "StrategicSatelliteLaunch"),
        ),
        (
            "Recover Fighters",
            "recover_fighters",
            _facility_has_ability(planet, "RecoverFighters")
            and _matching_group_at_hex(planet, galaxy, "fighter_group"),
        ),
        (
            "Recover Satellites",
            "recover_satellites",
            _facility_has_ability(planet, "RecoverSatellites")
            and _matching_group_at_hex(planet, galaxy, "satellite_group"),
        ),
    ]
    items: list[PlanetMenuItem] = []
    for label, key, visible in rows:
        if not visible:
            continue
        cb = callbacks.get(key)
        if cb is None:
            continue
        items.append(PlanetMenuItem(label=label, callback=cb))
    return items


__all__ = ["PlanetMenuItem", "build_menu_items"]
