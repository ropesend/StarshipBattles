"""End-of-battle reboard for in-battle-launched fighters and satellites.

PROJ-FMS-C Phase 3 introduced this for fighters. PROJ-FMS-D Phase 2
generalised it to also reboard satellites — the same
``launched_in_battle_id`` tag, the same per-CarriedVehicle round-trip,
just dispatched per ``vehicle_type`` so each kind lands in its own
overflow group (``fighter_group`` vs ``satellite_group``) and only
counts as fighter / satellite cargo for the bay-type filter.

Surviving in-battle-launched vehicles auto-reboard onto any friendly
ship with bay space. Overflow spills into a new ``{vehicle_type}_group``
Fleet in the sector (or merges into a pre-existing same-empire group of
the same kind at the same hex). Pre-existing fighter_group /
satellite_group entries that participated stay in their original group
unless explicitly recovered via the strategic
:class:`RecoverFightersOrderHandler` / :class:`RecoverSatellitesOrderHandler`
actions.

The reboard pipeline is hooked into :func:`run_battle` via the
spec-compiler's ``pre_tick_loop_callback`` (the same wiring pattern that
PROJ-FMS-B used for tactical mine resolvers): the callback installs a
``ReboardTracker`` on the engine, attack_processor appends each
launched fighter / satellite to it, and the strategy post-battle hook
calls :func:`apply_reboard` once the outcome is known.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.systems.battle_engine import BattleEngine
    from game.strategy.data.fleet import Fleet


logger = logging.getLogger(__name__)


class ReboardTracker:
    """Per-battle tracker for fighters launched during the battle.

    Installed on :class:`BattleEngine` as ``engine.reboard_tracker`` by
    the spec compiler's ``pre_tick_loop_callback`` (PROJ-FMS-C Phase 3).
    :func:`attack_processor.process_launch_attack` appends each spawned
    fighter to ``launched_ships``.

    The tracker also captures the battle id so the post-battle hook can
    confirm a ship's ``launched_in_battle_id`` tag really matches this
    battle (defensive — fighters reused across battles must not be
    silently reboarded by the wrong cycle).
    """

    def __init__(self, *, battle_id: Optional[Any] = None) -> None:
        self.battle_id: Optional[Any] = battle_id
        self.launched_ships: List["Ship"] = []

    def track(self, ship: "Ship") -> None:
        self.launched_ships.append(ship)


def apply_reboard(
    *,
    engine: "BattleEngine",
    participating_fleets_by_owner: Dict[Any, List["Fleet"]],
    empires_by_owner: Dict[Any, Any],
) -> Dict[str, int]:
    """Reboard surviving in-battle-launched fighters and spill overflow.

    Args:
        engine: The :class:`BattleEngine` after :meth:`shutdown`. Reads
            ``engine.reboard_tracker.launched_ships`` and inspects each
            ship's ``is_alive`` / ``current_hp`` / ``team_id`` to decide
            recovery.
        participating_fleets_by_owner: ``{owner_id: [Fleet, ...]}`` for
            empires that fielded fleets in the battle. The carrier
            search walks every ship of each fleet looking for available
            bay space.
        empires_by_owner: ``{owner_id: Empire}``. Used for overflow:
            when no friendly carrier has bay space, a new ``fighter_group``
            Fleet is created at the participating fleet's hex and added
            to the empire's ``fleets`` list.

    Returns:
        A summary dict ``{"reboarded": int, "overflowed": int,
        "discarded": int}`` describing what happened. Discarded
        counts fighters that died mid-battle (not recovered).
    """
    summary = {"reboarded": 0, "overflowed": 0, "discarded": 0}

    tracker: Optional[ReboardTracker] = getattr(engine, "reboard_tracker", None)
    if tracker is None or not tracker.launched_ships:
        return summary

    # Build a per-owner bay-availability scan once.
    for ship in tracker.launched_ships:
        if not _ship_is_alive(ship):
            summary["discarded"] += 1
            continue
        team_id = getattr(ship, "team_id", None)
        if team_id is None:
            summary["discarded"] += 1
            continue
        owner_id = _resolve_owner_for_team(
            team_id, participating_fleets_by_owner,
        )
        if owner_id is None:
            summary["discarded"] += 1
            continue

        cv = _ship_to_carried_vehicle(ship)
        if cv is None:
            summary["discarded"] += 1
            continue

        # Try to reboard onto any friendly ship with bay space.
        friendly_fleets = participating_fleets_by_owner.get(owner_id, [])
        loaded = False
        for fleet in friendly_fleets:
            for candidate in fleet.ships:
                if not _candidate_alive(candidate):
                    continue
                cargo_mgr = getattr(candidate, "_cargo_mgr", None)
                if cargo_mgr is None:
                    continue
                try:
                    if cargo_mgr.load_vehicle(cv):
                        loaded = True
                        summary["reboarded"] += 1
                        break
                except Exception:  # Intentional broad catch: load_vehicle may raise across many failure modes (registries missing, stub fleets); treat as "couldn't reboard" rather than crash the hook.
                    continue
            if loaded:
                break

        if loaded:
            continue

        # Overflow: spill into a new group Fleet in the sector. The
        # group_kind matches the CarriedVehicle.vehicle_type so a
        # satellite-overflow lands in a satellite_group (not a
        # fighter_group). Closes the loop with the strategic
        # RecoverSatellitesOrderHandler.
        empire = empires_by_owner.get(owner_id)
        if empire is None:
            summary["discarded"] += 1
            continue
        sector_hex = _resolve_sector_hex(friendly_fleets)
        if sector_hex is None:
            summary["discarded"] += 1
            continue
        overflow_group = _ensure_overflow_group(
            empire=empire,
            sector_hex=sector_hex,
            vehicle_type=getattr(cv, "vehicle_type", "fighter"),
        )
        overflow_instance = _build_overflow_ship_instance(
            cv, owner_id=owner_id,
        )
        if overflow_instance is None:
            summary["discarded"] += 1
            continue
        overflow_group.ships.append(overflow_instance)
        summary["overflowed"] += 1

    return summary


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ship_is_alive(ship: Any) -> bool:
    if not getattr(ship, "is_alive", True):
        return False
    hp = getattr(ship, "current_hp", None)
    if hp is not None and hp <= 0:
        return False
    return True


def _candidate_alive(candidate: Any) -> bool:
    if not getattr(candidate, "is_alive", True):
        return False
    if getattr(candidate, "is_derelict", False):
        return False
    return True


def _resolve_owner_for_team(
    team_id: int,
    participating_fleets_by_owner: Dict[Any, List["Fleet"]],
) -> Optional[Any]:
    """Reverse-lookup the owner_id for a team_id.

    The spec compiler assigns team_ids in insertion order of
    ``fleets_by_owner``. Iterating the same dict here gives the same
    ordering for matching.
    """
    for idx, owner_id in enumerate(participating_fleets_by_owner.keys()):
        if idx == team_id:
            return owner_id
    return None


def _ship_to_carried_vehicle(ship: Any) -> Optional[Any]:
    """Materialise a CarriedVehicle dict-payload from a sim ``Ship``.

    Walks the design data + current HP + per-component damage state.
    Designed to be robust against test-stub ships (Mocks, partial
    fixtures); returns ``None`` when the ship can't be converted cleanly.

    PROJ-FMS-C audit Fix 2: now captures ``ship.components`` (the
    per-component :class:`ComponentState` map) into
    :attr:`CarriedVehicle.component_states`. This mirrors how
    :class:`RecoverFightersOrderHandler` preserves damage state for
    strategic-layer recoveries, closing the end-to-end loop the docs
    describe.

    PROJ-FMS-D Phase 2: ``vehicle_type`` is inferred from the sim
    ship's ``vehicle_type`` attribute (the same field
    :class:`AIControllerFactory` uses to dispatch). A ship whose
    vehicle_type isn't ``Fighter`` or ``Satellite`` is treated as a
    fighter for backwards-compat with pre-FMS-D test fixtures that
    relied on the hard-coded fighter path.
    """
    from game.simulation.entities.ship_serialization import ShipSerializer
    from game.strategy.data.carried_vehicle import CarriedVehicle

    try:
        design_data = ShipSerializer.to_dict(ship)
    except Exception:  # Intentional broad catch: ShipSerializer.to_dict may raise on minimal test ships; reboard is best-effort.
        return None

    design_id = (
        getattr(ship, "design_id", None)
        or design_data.get("design_id")
        or design_data.get("name", "fighter")
    )
    try:
        current_hp = float(getattr(ship, "current_hp", 0) or 0)
    except (TypeError, ValueError):
        current_hp = 0.0
    if current_hp <= 0:
        return None
    mass = float(design_data.get("expected_stats", {}).get("mass", 0.0) or 0.0)
    if mass <= 0:
        try:
            mass = float(getattr(ship, "mass", 0.0) or 0.0)
        except (TypeError, ValueError):
            mass = 0.0

    # PROJ-FMS-C audit Fix 2: capture per-component damage state. Sim ships
    # store this on ``ship.components`` as ``{key: ComponentState}``;
    # CarriedVehicle.component_states uses the same shape so the bay-side
    # restore in :func:`_spawn_from_carried_vehicle` can re-apply it
    # symmetrically.
    components = getattr(ship, "components", None)
    component_states = dict(components) if components else None

    # PROJ-FMS-D Phase 2: vehicle_type-aware. Sim Ship.vehicle_type uses
    # the canonical capitalisation ("Fighter" / "Satellite"); the
    # CarriedVehicle field is lowercase. Default = "fighter" so legacy
    # callers that pre-date PROJ-FMS-D still round-trip cleanly.
    sim_vt = (getattr(ship, "vehicle_type", "Fighter") or "Fighter").lower()
    if sim_vt in ("satellite",):
        cv_type = "satellite"
    else:
        cv_type = "fighter"

    try:
        return CarriedVehicle(
            design_id=str(design_id),
            design_data=design_data,
            vehicle_type=cv_type,
            mass=mass,
            current_hp=int(current_hp),
            component_states=component_states,
        )
    except ValueError:
        return None


def _resolve_sector_hex(fleets: List["Fleet"]) -> Optional[Any]:
    for fleet in fleets:
        loc = getattr(fleet, "location", None)
        if loc is not None:
            return loc
    return None


def _ensure_overflow_fighter_group(*, empire: Any, sector_hex: Any) -> Any:
    """Backwards-compat alias of :func:`_ensure_overflow_group` for fighters."""
    return _ensure_overflow_group(
        empire=empire, sector_hex=sector_hex, vehicle_type="fighter",
    )


def _ensure_overflow_group(
    *, empire: Any, sector_hex: Any, vehicle_type: str,
) -> Any:
    """Look up or mint an overflow deployed-group at ``sector_hex``.

    PROJ-431 Phase 3: returns a :class:`FighterWing` /
    :class:`SatelliteConstellation` on ``empire.deployed_groups``,
    not a synthetic ``Fleet(group_kind=...)``.

    Reboard policy (PROJ-FMS-C decisions.md, carried forward): if a
    pre-existing group of the same type at the sector already belongs
    to this empire, MERGE overflow into it. Otherwise mint a fresh group.
    """
    from game.strategy.data.deployed_group import (
        FighterWing,
        SatelliteConstellation,
    )

    vt = vehicle_type.lower()
    if vt == "satellite":
        target_cls: type = SatelliteConstellation
        display_name_template = "Satellite Group"
        base_id = 300000
    else:
        # Default = fighter for backwards-compat with PROJ-FMS-C tests
        # that don't set a vehicle_type on the CarriedVehicle.
        target_cls = FighterWing
        display_name_template = "Fighter Wing"
        base_id = 200000

    deployed = getattr(empire, "deployed_groups", None)
    if deployed is None:
        deployed = []
        empire.deployed_groups = deployed
    for g in deployed:
        if not isinstance(g, target_cls):
            continue
        if getattr(g, "location", None) == sector_hex:
            return g

    new_id = _mint_overflow_id(empire, base_id=base_id)
    group = target_cls(
        group_id=new_id,
        owner_id=getattr(empire, "id", 0),
        location=sector_hex,
        display_name=f"{display_name_template} {new_id}",
    )
    deployed.append(group)
    return group


def _mint_overflow_id(empire: Any, *, base_id: int = 200000) -> int:
    deployed = getattr(empire, "deployed_groups", None) or ()
    existing = {g.id for g in deployed if isinstance(g.id, int)}
    candidate = base_id
    while candidate in existing:
        candidate += 1
    return candidate


def _build_overflow_ship_instance(cv: Any, *, owner_id: int) -> Optional[Any]:
    """Build a ShipInstance for the overflow group from a CarriedVehicle.

    PROJ-FMS-D audit Fix 1: routes through the shared
    :func:`game.strategy.data.carried_vehicle_deploy.carried_vehicle_to_ship_instance_safe`
    helper so the overflow path preserves the same fields as the
    strategic-launch path (HP + component_states + alive flags +
    vehicle-type-aware instance prefix). Before the fix, the overflow
    path skipped the ``cv.component_states`` restore and silently dropped
    per-component damage state for any in-battle-launched fighter or
    satellite that overflowed at battle end.
    """
    from game.strategy.data.carried_vehicle_deploy import (
        carried_vehicle_to_ship_instance_safe,
    )

    return carried_vehicle_to_ship_instance_safe(cv, owner_id=owner_id)


__all__ = ["ReboardTracker", "apply_reboard"]
