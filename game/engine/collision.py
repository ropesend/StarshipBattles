"""
Collision System - Hit Detection and Combat Resolution

This module handles collision detection and damage resolution for combat:
- Beam weapon raycasting (sphere-ray intersection)
- Ship-to-ship ramming collisions

Sphere-Ray Intersection (Beam Attacks):
    Uses quadratic formula to find intersection points of a ray with a sphere.

    Given:
        - Ray origin: P
        - Ray direction: D (unit vector)
        - Sphere center: C
        - Sphere radius: r

    Let f = P - C (vector from sphere center to ray origin)

    Solve: |P + t*D - C|² = r²
    Expands to: (D·D)t² + 2(f·D)t + (f·f - r²) = 0

    Coefficients:
        a = D·D (always 1 if D is normalized)
        b = 2(f·D)
        c = f·f - r²

    Discriminant: b² - 4ac
        < 0: No intersection (ray misses sphere)
        = 0: Tangent hit (one intersection point)
        > 0: Two intersection points (entry and exit)

    Solutions: t = (-b ± √discriminant) / 2a
        t₁ is the entry point (closer)
        t₂ is the exit point (farther)

Hit Chance Calculation (Sigmoid):
    Hit probability uses a logistic function for smooth falloff.
    See BeamWeaponAbility.calculate_hit_chance() in abilities/weapons.py

    Formula: P = 1 / (1 + e^(-net_score))

    Where: net_score = (base_accuracy + attack_bonuses) - (range_penalty + defense_penalties)
        - base_accuracy: Weapon's inherent accuracy (0.0-1.0 typically)
        - attack_bonuses: Attacker's sensor score
        - range_penalty: accuracy_falloff * distance
        - defense_penalties: Target's ECM/defense score
"""
import math
import random
from typing import List, Dict, Any, TYPE_CHECKING, cast

from game.core.config import BattleTuning
from game.core.combat_types import DamageContext

if TYPE_CHECKING:
    from game.simulation.combat.attack_contract import BeamResolution
    from game.simulation.components.abilities.weapons import BeamWeaponAbility

# Note: Ship type hint uses Any to avoid tight coupling with simulation entities


class CollisionSystem:
    """
    System for handling collisions and raycasting.

    Accepts an optional RNG instance for deterministic hit rolls (PROJ-252).
    """

    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng: random.Random = rng if rng is not None else random.Random()

    def process_beam_attack(self, attack: 'BeamResolution', recent_beams: List[Dict[str, Any]]) -> None:
        """
        Process a beam weapon attack using raycasting.

        PROJ-359 Phase 4: consumes the typed `BeamResolution` produced by the
        Beam / PDC family handlers. The legacy dict-shaped carrier was deleted
        in this phase; simulation-layer semantics no longer leak into the
        engine layer via dict keys.

        Args:
            attack: BeamResolution from a registered Beam/PDC family handler
            recent_beams: List to append beam visualization data to
        """
        start_pos = attack.origin
        direction = attack.direction
        max_range = attack.range
        target = attack.target

        end_pos = start_pos + direction * max_range

        if target and target.is_alive:
            f = start_pos - target.position
            a = direction.dot(direction)
            b = 2 * f.dot(direction)
            c = f.dot(f) - target.radius**2

            discriminant = b*b - 4*a*c

            if discriminant >= 0:
                # Avoid division by zero if direction length is 0 (shouldn't happen with valid direction)
                if a == 0:
                     t1 = t2 = 0
                else:
                    t1 = (-b - math.sqrt(discriminant)) / (2*a)
                    t2 = (-b + math.sqrt(discriminant)) / (2*a)

                valid_t = []
                if 0 <= t1 <= max_range: valid_t.append(t1)
                if 0 <= t2 <= max_range: valid_t.append(t2)

                if valid_t:
                    hit_dist = min(valid_t)
                    beam_comp = attack.component

                    # Get ability for hit chance and damage calculations.
                    # BeamResolution invariant: AttackRequest carries a live
                    # weapon_ability for the dispatched beam component
                    # (see game/simulation/combat/families/_beam_common.py and
                    # game/simulation/combat/attack_contract.py). A missing
                    # BeamWeaponAbility here is a programming error, not a
                    # runtime condition to silently absorb.
                    beam_ab_raw = beam_comp.get_ability('BeamWeaponAbility')
                    assert beam_ab_raw is not None, (
                        f"BeamResolution invariant: component {beam_comp.name!r} "
                        f"dispatched as beam but has no BeamWeaponAbility"
                    )
                    beam_ab = cast("BeamWeaponAbility", beam_ab_raw)

                    # Get Scores (includes fleet aura bonuses)
                    source_ship = attack.source
                    attack_score = 0.0
                    if source_ship and hasattr(source_ship, 'get_total_sensor_score'):
                        attack_score = source_ship.get_total_sensor_score()
                        fleet_atk = getattr(source_ship, 'fleet_attack_bonus', None)
                        if isinstance(fleet_atk, (int, float)):
                            attack_score += fleet_atk

                    defense_score = target.total_defense_score
                    fleet_def = getattr(target, 'fleet_defense_bonus', None)
                    if isinstance(fleet_def, (int, float)):
                        defense_score += fleet_def

                    # Calculate Chance with Sigmoid Logic using ability
                    chance = beam_ab.calculate_hit_chance(hit_dist, attack_score, defense_score)

                    if self.rng.random() < chance:
                        # Record confirmed hit on the firing component
                        beam_comp.shots_hit += 1

                        # Evaluate damage at hit distance using ability
                        damage = beam_ab.get_damage(hit_dist)
                        # Handle both Ship targets (have combat_engine) and
                        # Projectile targets (PDC shooting at missiles)
                        if hasattr(target, 'combat_engine'):
                            ctx = DamageContext(
                                attacker=source_ship,
                                source_weapon=beam_comp,
                                damage_type="beam",
                            )
                            target.combat_engine.take_damage(damage, context=ctx)
                        elif hasattr(target, 'take_damage'):
                            target.take_damage(damage)
                        end_pos = start_pos + direction * hit_dist
        
        # Store for visualization
        recent_beams.append({
            'start': start_pos,
            'end': end_pos,
            'color': (100, 255, 255) # Could be derived from weapon type
        })

    def process_ramming(self, ships: List[Any], logger: Any = None) -> None:
        """
        Process ship-to-ship ramming collisions.
        
        Args:
            ships: List of Ship objects to check
            logger: Optional logger for events
        """
        for s in ships:
            if not s.is_alive: continue
            if getattr(s, 'movement_policy', '') != 'ramming_speed': continue
            
            target = s.current_target
            if not target or not target.is_alive: continue
            
            collision_radius = s.radius + target.radius
            
            if s.position.distance_to(target.position) < collision_radius:
                # PROJ-40/NEW-AI-004: Use getattr with default for safe HP access
                hp_rammer = getattr(s, 'hp', 100)
                hp_target = getattr(target, 'hp', 100)

                rammer_ctx = DamageContext(attacker=target, damage_type="ramming")
                target_ctx = DamageContext(attacker=s, damage_type="ramming")

                msg = ""
                if hp_rammer < hp_target:
                    s.combat_engine.take_damage(hp_rammer + BattleTuning.GUARANTEED_KILL_DAMAGE, context=rammer_ctx)
                    target.combat_engine.take_damage(hp_rammer * BattleTuning.RAMMING_DAMAGE_FACTOR, context=target_ctx)
                    msg = f"Ramming: {s.name} destroyed by {target.name}!"
                elif hp_target < hp_rammer:
                    target.combat_engine.take_damage(hp_target + BattleTuning.GUARANTEED_KILL_DAMAGE, context=target_ctx)
                    s.combat_engine.take_damage(hp_target * BattleTuning.RAMMING_DAMAGE_FACTOR, context=rammer_ctx)
                    msg = f"Ramming: {target.name} destroyed by {s.name}!"
                else:
                    s.combat_engine.take_damage(hp_rammer + BattleTuning.GUARANTEED_KILL_DAMAGE, context=rammer_ctx)
                    target.combat_engine.take_damage(hp_target + BattleTuning.GUARANTEED_KILL_DAMAGE, context=target_ctx)
                    msg = f"Ramming: Mutual destruction!"
                
                if logger:
                    logger.log(msg)
