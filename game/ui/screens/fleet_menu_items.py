"""Pure capability-driven builder for the fleet right-click context menu.

Issue #20. This module deliberately has no pygame dependency: every
visibility decision lives here so it can be unit-tested in isolation.
The UI wrapper in ``strategy_fleet_context_menu.py`` consumes the list
returned here.

The builder takes the fleet, the galaxy (for "at a colonisable planet
hex" check), and an ``InputMapper``-like object whose
``get_display_text(action)`` returns the human-readable keyboard
shortcut.

Capability gates mirror the gates already enforced by
``FleetCommandRouter.handle_fleet_action`` and
``FleetCommandRouter.handle_superweapon_action`` so the menu shows
exactly the orders the hotkeys would let the fleet perform — no
duplicated logic, no divergent rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from game.core.input_actions import InputAction


@dataclass(frozen=True)
class FleetMenuItem:
    """One row in the fleet context menu.

    Attributes:
        label: Display label, e.g. ``"Open Warp Point"``.
        action: The ``InputAction`` to dispatch when this row is clicked.
        shortcut: Display text of the bound key (e.g. ``"Ctrl+W"``);
            ``""`` if the action is unbound.
    """

    label: str
    action: InputAction
    shortcut: str


class _MapperLike(Protocol):
    def get_display_text(self, action: InputAction) -> str: ...


def _has(fleet: Any, ability: str) -> bool:
    caps = getattr(fleet, "capabilities", None)
    if caps is None:
        return False
    return bool(caps.has_ability(ability))


def _can_warp(fleet: Any) -> bool:
    caps = getattr(fleet, "capabilities", None)
    if caps is None:
        return False
    return bool(caps.can_use_warp())


def _can_strategic_move(fleet: Any) -> bool:
    """PROJ-FMS-A: non-``fleet`` group_kinds cannot move on the strategy map.

    Resilient to mock fleets that lack the property entirely (defaults
    to True so existing tests don't break).
    """
    val = getattr(fleet, "can_strategic_move", True)
    return bool(val)


def _has_self_destruct_ships(fleet: Any) -> bool:
    caps = getattr(fleet, "capabilities", None)
    if caps is None:
        return False
    return bool(caps.ships_with_ability("SelfDestruct"))


def _at_colonisable_hex(fleet: Any, galaxy: Any) -> bool:
    if galaxy is None:
        return False
    planets = galaxy.get_planets_at_global_hex(fleet.location) or []
    for p in planets:
        if getattr(p, "owner_id", None) is None:
            return True
    return False


def build_menu_items(
    fleet: Any,
    galaxy: Any,
    mapper: _MapperLike,
) -> list[FleetMenuItem]:
    """Return the ordered list of menu items the fleet can perform.

    Items the fleet cannot perform are omitted entirely (not greyed —
    per AC: "exactly the orders the fleet can perform").
    """
    # PROJ-FMS-A: non-fleet group_kinds (fighter_group / satellite_group /
    # mine_group) cannot perform strategic moves or merge with other fleets.
    can_move = _can_strategic_move(fleet)
    rows: list[tuple[str, InputAction, bool]] = [
        ("Move", InputAction.FLEET_MOVE, can_move),
        ("Join Fleet", InputAction.FLEET_JOIN, can_move),
        (
            "Colonize",
            InputAction.FLEET_COLONIZE,
            _has(fleet, "ColonizePlanet") and _at_colonisable_hex(fleet, galaxy),
        ),
        ("Transfer Cargo", InputAction.FLEET_TRANSFER, _has(fleet, "CargoStorage")),
        ("Drop Cargo", InputAction.FLEET_DROP_CARGO, _has(fleet, "CargoStorage")),
        ("Load Cargo", InputAction.FLEET_LOAD_CARGO, _has(fleet, "CargoStorage")),
        ("Warp Jump", InputAction.FLEET_WARP, _can_warp(fleet)),
        (
            "Open Warp Point",
            InputAction.FLEET_OPEN_WARP_POINT,
            _has(fleet, "OpenWarpPoint"),
        ),
        (
            "Close Warp Point",
            InputAction.FLEET_CLOSE_WARP_POINT,
            _has(fleet, "CloseWarpPoint"),
        ),
        (
            "Implode Planet",
            InputAction.FLEET_IMPLODE_PLANET,
            _has(fleet, "DestroyPlanet"),
        ),
        (
            "Stellerate Star",
            InputAction.FLEET_STELLERATE_STAR,
            _has(fleet, "DestroyStar"),
        ),
        (
            "Create Dyson Sphere",
            InputAction.FLEET_CREATE_DYSON_SPHERE,
            _has(fleet, "CreateDysonSphere"),
        ),
        (
            "Self-Destruct",
            InputAction.FLEET_SELF_DESTRUCT,
            _has_self_destruct_ships(fleet),
        ),
    ]

    items: list[FleetMenuItem] = []
    for label, action, visible in rows:
        if not visible:
            continue
        items.append(
            FleetMenuItem(
                label=label,
                action=action,
                shortcut=mapper.get_display_text(action),
            )
        )
    return items
