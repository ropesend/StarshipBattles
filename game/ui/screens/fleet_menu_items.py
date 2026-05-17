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

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Protocol

from game.core.input_actions import InputAction
from game.strategy.data.deployed_group import FighterWing, SatelliteConstellation


@dataclass(frozen=True)
class FleetMenuItem:
    """One row in the fleet context menu.

    Attributes:
        label: Display label, e.g. ``"Open Warp Point"``.
        action: The ``InputAction`` to dispatch when this row is clicked.
            ``None`` is allowed when ``callback`` is set (QA Observation
            B: FMS rows have no InputAction enum value today).
        shortcut: Display text of the bound key (e.g. ``"Ctrl+W"``);
            ``""`` if the action is unbound.
        callback: Optional zero-arg callable. When set, the menu invokes
            this directly instead of routing ``action`` through the
            fleet command router. Used by the FMS rows.
    """

    label: str
    action: Optional[InputAction]
    shortcut: str
    callback: Optional[Callable[[], None]] = field(default=None)


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


# --- QA Observation B Phase 7: FMS row gates -------------------------------


def _fleet_has_carried_vehicle(fleet: Any, vehicle_type: str) -> bool:
    """True if any ship in ``fleet`` carries a vehicle of ``vehicle_type``.

    PROJ-431 Phase 1e: reads through ``ship.bay_inventory.bay`` — the
    homogeneous typed slot for design-backed carried vehicles. Mirrors
    how ``fms_shared.count_matching_bay`` filters.
    """
    for ship in getattr(fleet, "ships", None) or ():
        inventory = getattr(ship, "bay_inventory", None)
        if inventory is None:
            continue
        for cv in getattr(inventory, "bay", None) or ():
            if getattr(cv, "vehicle_type", None) == vehicle_type:
                return True
    return False


def _matching_deployed_group_at_fleet_hex(
    fleet: Any, galaxy: Any, group_cls: type,
) -> bool:
    """True if a same-empire deployed group of ``group_cls`` sits at hex.

    PROJ-431 Phase 3: dispatch on the concrete
    :class:`DeployedGroup` subclass (FighterWing / SatelliteConstellation),
    not on a string ``group_kind``. Falls back to ``False`` on mocks
    that lack ``empires``.
    """
    if galaxy is None:
        return False
    owner_id = getattr(fleet, "owner_id", None)
    if owner_id is None:
        return False
    target_hex = fleet.location
    empires = getattr(galaxy, "empires", None) or []
    for emp in empires:
        if getattr(emp, "id", None) != owner_id:
            continue
        for other in getattr(emp, "deployed_groups", None) or ():
            if not isinstance(other, group_cls):
                continue
            if other.location == target_hex:
                return True
    return False


def build_menu_items(
    fleet: Any,
    galaxy: Any,
    mapper: _MapperLike,
    callbacks: Optional[dict[str, Callable[[], None]]] = None,
) -> list[FleetMenuItem]:
    """Return the ordered list of menu items the fleet can perform.

    Items the fleet cannot perform are omitted entirely (not greyed —
    per AC: "exactly the orders the fleet can perform").

    ``callbacks`` (QA Observation B Phase 7) supplies the zero-arg
    callables for the five FMS rows (``lay_mines``, ``launch_fighters``,
    ``launch_satellites``, ``recover_fighters``, ``recover_satellites``).
    When omitted (or a key is missing) the corresponding FMS row is not
    emitted — this keeps existing call sites and tests that don't supply
    callbacks unchanged.
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

    # QA Observation B Phase 7: FMS rows (callback-driven, no InputAction).
    if callbacks:
        fms_rows: list[tuple[str, str, bool]] = [
            (
                "Lay Mines",
                "lay_mines",
                _has(fleet, "StrategicMineLayer")
                and _fleet_has_carried_vehicle(fleet, "mine"),
            ),
            (
                "Launch Fighters",
                "launch_fighters",
                _has(fleet, "StrategicFighterLaunch")
                and _fleet_has_carried_vehicle(fleet, "fighter"),
            ),
            (
                "Launch Satellites",
                "launch_satellites",
                _has(fleet, "StrategicSatelliteLaunch")
                and _fleet_has_carried_vehicle(fleet, "satellite"),
            ),
            (
                "Recover Fighters",
                "recover_fighters",
                _has(fleet, "RecoverFighters")
                and _matching_deployed_group_at_fleet_hex(
                    fleet, galaxy, FighterWing,
                ),
            ),
            (
                "Recover Satellites",
                "recover_satellites",
                _has(fleet, "RecoverSatellites")
                and _matching_deployed_group_at_fleet_hex(
                    fleet, galaxy, SatelliteConstellation,
                ),
            ),
        ]
        for label, key, visible in fms_rows:
            if not visible:
                continue
            cb = callbacks.get(key)
            if cb is None:
                continue
            items.append(
                FleetMenuItem(
                    label=label, action=None, shortcut="", callback=cb,
                )
            )

    return items
