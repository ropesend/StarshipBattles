"""FMS context-menu callback builders (QA Observation B Phases 6-7).

Both the fleet right-click menu and the planet right-click menu need
zero-arg callables that dispatch the five FMS Issue*Commands through the
strategy facade. Centralising those builders here keeps
:mod:`strategy_ui` thin and makes the dispatch surface trivially
unit-testable in isolation.

Each builder returns a ``{action_name: Callable[[], None]}`` dict whose
keys match the ones consumed by
:func:`fleet_menu_items.build_menu_items` and
:func:`planet_menu_items.build_menu_items`.
"""
from __future__ import annotations

from typing import Any, Callable, Optional

from game.strategy.engine.commands import (
    IssueLaunchFightersCommand,
    IssueLaunchSatellitesCommand,
    IssueLayMinesCommand,
    IssueRecoverFightersCommand,
    IssueRecoverSatellitesCommand,
)


def build_planet_fms_callbacks(
    planet: Any,
    facade: Any,
    close_menu: Callable[[], None],
) -> dict[str, Callable[[], None]]:
    """Return the FMS callback dict for a planet right-click menu.

    Each callback closes the menu, builds the matching ``Issue*Command``
    with ``planet_id=planet.id``, and dispatches it through ``facade``.
    """
    def _dispatch(cmd: Any) -> None:
        close_menu()
        if facade is None:
            return
        facade.handle_command(cmd)

    return {
        "lay_mines": lambda: _dispatch(
            IssueLayMinesCommand(planet_id=planet.id, mine_design_id="auto"),
        ),
        "launch_fighters": lambda: _dispatch(
            IssueLaunchFightersCommand(planet_id=planet.id),
        ),
        "launch_satellites": lambda: _dispatch(
            IssueLaunchSatellitesCommand(planet_id=planet.id),
        ),
        "recover_fighters": lambda: _dispatch(
            IssueRecoverFightersCommand(planet_id=planet.id),
        ),
        "recover_satellites": lambda: _dispatch(
            IssueRecoverSatellitesCommand(planet_id=planet.id),
        ),
    }


def _first_ship_id_with(fleet: Any, ability: str) -> Optional[str]:
    """Return the ``instance_id`` of the first fleet ship with ``ability``.

    Returns ``None`` when the fleet has no capabilities object or no
    ship owns the ability. The callers wire each ability to a single
    FMS command; if multiple ships have the same ability the first one
    is chosen deterministically (capability calculator preserves fleet
    order).
    """
    caps = getattr(fleet, "capabilities", None)
    if caps is None:
        return None
    ships = caps.ships_with_ability(ability) or []
    if not ships:
        return None
    sid = getattr(ships[0], "instance_id", None)
    return str(sid) if sid is not None else None


def build_fleet_fms_callbacks(
    fleet: Any,
    facade: Any,
    close_menu: Callable[[], None],
) -> dict[str, Callable[[], None]]:
    """Return the FMS callback dict for a fleet right-click menu.

    Mirrors :func:`build_planet_fms_callbacks` but resolves
    ``ship_instance_id`` from the first ship that owns the relevant
    ability (the menu row's capability gate guarantees one exists).
    """
    def _dispatch(cmd: Any) -> None:
        close_menu()
        if facade is None:
            return
        facade.handle_command(cmd)

    return {
        "lay_mines": lambda: _dispatch(
            IssueLayMinesCommand(
                fleet_id=fleet.id,
                ship_instance_id=_first_ship_id_with(fleet, "StrategicMineLayer"),
                mine_design_id="auto",
            ),
        ),
        "launch_fighters": lambda: _dispatch(
            IssueLaunchFightersCommand(
                fleet_id=fleet.id,
                ship_instance_id=_first_ship_id_with(fleet, "StrategicFighterLaunch"),
            ),
        ),
        "launch_satellites": lambda: _dispatch(
            IssueLaunchSatellitesCommand(
                fleet_id=fleet.id,
                ship_instance_id=_first_ship_id_with(fleet, "StrategicSatelliteLaunch"),
            ),
        ),
        "recover_fighters": lambda: _dispatch(
            IssueRecoverFightersCommand(
                fleet_id=fleet.id,
                ship_instance_id=_first_ship_id_with(fleet, "RecoverFighters"),
            ),
        ),
        "recover_satellites": lambda: _dispatch(
            IssueRecoverSatellitesCommand(
                fleet_id=fleet.id,
                ship_instance_id=_first_ship_id_with(fleet, "RecoverSatellites"),
            ),
        ),
    }


__all__ = [
    "build_fleet_fms_callbacks",
    "build_planet_fms_callbacks",
]
