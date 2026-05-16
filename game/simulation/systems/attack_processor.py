"""Attack processing helpers for the battle engine.

PROJ-382 Phase 5: extracted from ``battle_engine.py`` to bring the parent
module under the 500 LOC ceiling.  Four free functions take an explicit
``engine`` reference and dispatch projectile / beam / launch attacks
through the engine's collaborators (logger, projectile manager,
collision system).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from game.core.constants import AttackType
from game.core.config import BattleTuning
from game.core.math import Vector2

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.systems.battle_engine import BattleEngine


def collect_new_attacks(engine: "BattleEngine", alive_ships: List["Ship"]) -> List[Any]:
    """Collect and clear attacks emitted by ships this tick."""
    new_attacks: List[Any] = []
    for ship in alive_ships:
        if ship.just_fired_projectiles:
            new_attacks.extend(ship.just_fired_projectiles)
            ship.just_fired_projectiles = []
    return new_attacks


def process_attacks(engine: "BattleEngine", attacks: List[Any]) -> None:
    """Process projectile, beam, and launch attacks.

    PROJ-359 Phase 4: discriminator unified on ``.type``. Beam attacks are
    ``BeamResolution`` dataclasses (not dicts); only the LAUNCH path remains
    a dict (out-of-scope for PROJ-359 — that's a hangar path, not a
    weapon family).
    """
    for attack in attacks:
        # LAUNCH is the only remaining dict-shaped attack carrier.
        is_dict = isinstance(attack, dict)
        attack_type = attack.get('type') if is_dict else attack.type

        if attack_type in (AttackType.PROJECTILE, AttackType.MISSILE):
            process_projectile_attack(engine, attack, attack_type, is_dict)
        elif attack_type == AttackType.BEAM:
            engine.collision_system.process_beam_attack(attack, engine.recent_beams)
        elif attack_type == AttackType.LAUNCH:
            process_launch_attack(engine, attack)


def process_projectile_attack(
    engine: "BattleEngine", attack: Any, attack_type: AttackType, is_dict: bool,
) -> None:
    """Register a projectile or missile attack with logging."""
    if is_dict:
        return

    engine.projectile_manager.add_projectile(attack)
    if attack_type == AttackType.PROJECTILE:
        engine.logger.log(f"Projectile fired at {attack.position}")
    else:
        target_name = attack.target.name if attack.target else 'unknown'
        engine.logger.log(f"Missile fired at {target_name}")


def process_launch_attack(engine: "BattleEngine", attack: Dict[str, Any]) -> None:
    """Spawn a launched fighter from a CarriedVehicle payload.

    PROJ-FMS-C Phase 1 (post audit-fix): the attack payload must carry a
    ``carried_vehicle`` field — a serialized :class:`CarriedVehicle` dict
    (or the dataclass instance). Spawns a full design-backed fighter
    with the vehicle's components, weapons, and HP. The spawned ship is
    tagged with ``launched_in_battle_id = engine._battle_id`` so the
    end-of-battle reboard hook (Phase 3) can identify it.

    The pre-PROJ-FMS-C class-string ``fighter_class`` path (the legacy
    ``VehicleLaunchAbility`` auto-launch shape) was removed in the audit
    fix pass; payloads without ``carried_vehicle`` are skipped.
    """
    source_ship = attack.get('source')
    origin = attack.get('origin', Vector2(0, 0))
    carried_payload = attack.get('carried_vehicle')

    if carried_payload is None:
        engine.logger.log(
            f"LAUNCH: attack from {getattr(source_ship, 'name', '?')} "
            f"missing carried_vehicle payload; skipping (legacy fighter_class "
            f"path was removed in PROJ-FMS-C audit Fix 1)."
        )
        return

    offset = Vector2(engine.rng.uniform(-10, 10), engine.rng.uniform(-10, 10))
    spawn_pos = origin + offset
    count = len([ship for ship in engine.ships if ship.team_id == source_ship.team_id])
    new_name = f"{source_ship.name} Wing {count+1}"

    new_ship = _spawn_from_carried_vehicle(
        engine,
        source_ship=source_ship,
        carried_payload=carried_payload,
        new_name=new_name,
        spawn_pos=spawn_pos,
    )
    if new_ship is None:
        engine.logger.log(
            f"LAUNCH: failed to spawn fighter from carried_vehicle "
            f"(source={getattr(source_ship, 'name', '?')})"
        )
        return

    new_ship.velocity = Vector2(source_ship.velocity)
    launch_dir = Vector2(1, 0).rotate(source_ship.angle)
    new_ship.velocity += launch_dir * BattleTuning.FIGHTER_LAUNCH_SPEED
    new_ship.angle = source_ship.angle

    # PROJ-FMS-C Phase 1: tag mid-battle-launched fighters so the
    # end-of-battle reboard hook (Phase 3) can distinguish launched-this-
    # battle from pre-existing fighter_group fighters.
    battle_id = getattr(engine, "_battle_id", None) or id(engine)
    try:
        new_ship.launched_in_battle_id = battle_id  # type: ignore[attr-defined]
    except Exception:  # Intentional broad catch: tagging is best-effort metadata; failure must not break the launch.
        pass

    engine.add_ship_mid_battle(new_ship, new_ship.team_id)
    # PROJ-FMS-C Phase 3: register this in-battle-launched fighter on
    # the engine's reboard tracker (when installed). The tracker is
    # populated at battle setup by the spec-compiler's
    # ``pre_tick_loop_callback``; tests that bypass that wiring (no
    # tracker present) silently skip — reboard is opt-in per battle.
    tracker = getattr(engine, "reboard_tracker", None)
    if tracker is not None:
        try:
            tracker.track(new_ship)
        except Exception:  # Intentional broad catch: tracker is best-effort metadata; failure must not break the launch.
            pass
    engine.logger.log(f"LAUNCH: {new_name} launched from {source_ship.name}")


def _spawn_from_carried_vehicle(
    engine: "BattleEngine",
    *,
    source_ship: "Ship",
    carried_payload: Any,
    new_name: str,
    spawn_pos: Vector2,
) -> Any:
    """Spawn a full design-backed fighter from a CarriedVehicle payload.

    Uses :meth:`ShipSerializer.from_dict` against the carried vehicle's
    ``design_data`` so the spawned ship has full components, weapons,
    abilities, and HP. ``current_hp`` from the CarriedVehicle is
    preserved; per-component damage state (when present) is applied
    after deserialisation.

    Returns ``None`` on irrecoverable failure (logged + skip).
    """
    # Late imports keep the simulation/strategy boundary clean.
    from game.simulation.entities.ship_serialization import ShipSerializer
    from game.strategy.data.carried_vehicle import CarriedVehicle

    cv = CarriedVehicle.from_any(carried_payload) if not isinstance(
        carried_payload, CarriedVehicle
    ) else carried_payload
    if cv is None:
        return None
    if not cv.design_data:
        return None

    try:
        new_ship = ShipSerializer.from_dict(
            cv.design_data, registries=source_ship.registries,
        )
    except Exception:  # Intentional broad catch: ShipSerializer.from_dict raises across many design-data corruption modes; treat as launch failure rather than crash the battle.
        return None

    # Position / identity / team.
    new_ship.name = new_name
    new_ship.team_id = source_ship.team_id
    new_ship.theme_id = getattr(source_ship, "theme_id", new_ship.theme_id)
    new_ship.color = source_ship.color
    new_ship.position = spawn_pos
    new_ship.x = spawn_pos.x
    new_ship.y = spawn_pos.y
    new_ship.angle = source_ship.angle

    # Preserve HP from the CarriedVehicle.
    try:
        if cv.current_hp and cv.current_hp > 0:
            new_ship.current_hp = float(cv.current_hp)
    except Exception:  # Intentional broad catch: setting current_hp on minimal stubs may raise; the new ship's design max_hp is the safe default.
        pass

    # PROJ-FMS-C audit Fix 2: restore per-component damage state. The
    # CarriedVehicle's ``component_states`` map (``{key: ComponentState}``)
    # mirrors the strategic-layer ``LaunchFightersOrderHandler`` behaviour:
    # the launched fighter starts with the same per-component HP it had
    # when it was loaded into the bay. Without this, a fighter that was
    # damaged in a previous battle would be silently fully-repaired by
    # the bay round-trip.
    if cv.component_states:
        try:
            new_ship.components = dict(cv.component_states)
        except Exception:  # Intentional broad catch: minimal stub ships may treat ``components`` as a property; ignore and fall back to the default initial state.
            pass

    return new_ship
