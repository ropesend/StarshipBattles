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
from game.simulation.entities.ship import Ship

if TYPE_CHECKING:
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
    """Spawn a launched fighter and add it to the battle."""
    source_ship = attack.get('source')
    fighter_class = attack.get('fighter_class', 'Fighter (Small)')
    origin = attack.get('origin', Vector2(0, 0))

    count = len([ship for ship in engine.ships if ship.team_id == source_ship.team_id])
    new_name = f"{source_ship.name} Wing {count+1}"

    offset = Vector2(engine.rng.uniform(-10, 10), engine.rng.uniform(-10, 10))
    spawn_pos = origin + offset

    new_ship = Ship(
        name=new_name,
        x=spawn_pos.x,
        y=spawn_pos.y,
        color=source_ship.color,
        team_id=source_ship.team_id,
        ship_class=fighter_class,
        theme_id=source_ship.theme_id,
        registries=source_ship.registries,
    )

    new_ship.velocity = Vector2(source_ship.velocity)
    launch_dir = Vector2(1, 0).rotate(source_ship.angle)
    new_ship.velocity += launch_dir * BattleTuning.FIGHTER_LAUNCH_SPEED
    new_ship.angle = source_ship.angle

    engine.add_ship_mid_battle(new_ship, new_ship.team_id)
    engine.logger.log(f"LAUNCH: {new_name} launched from {source_ship.name}")
