"""
ShipCombatEngine - Extracted combat logic from Ship class.

This class handles all combat-related operations for a ship:
- Firing weapons (projectile, beam, missile)
- Target selection and validation
- Lead/intercept calculation
- Damage application

Part of PROJ-12 God Class Decomposition.
"""
import math
import random
from typing import TYPE_CHECKING, List, Optional, Tuple, Any, Dict

from game.core.math import Vector2
from game.core.constants import AttackType
from game.core.logger import log_debug, log_info
from game.simulation.components.component import LayerType, ComponentStatus

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.components.component import Component


class ShipCombatEngine:
    """
    Handles all combat-related logic for a ship.

    Extracted from ShipCombatMixin to reduce Ship class complexity
    and improve testability.
    """

    def __init__(self, ship: 'Ship'):
        """
        Initialize combat engine for a ship.

        Args:
            ship: The ship this engine controls combat for
        """
        self._ship = ship

    # =========================================================================
    # Lead Calculation
    # =========================================================================

    def solve_lead(
        self,
        pos: Vector2,
        vel: Vector2,
        t_pos: Vector2,
        t_vel: Vector2,
        p_speed: float
    ) -> float:
        """
        Calculate interception time for a projectile.

        Uses quadratic formula to find the time at which a projectile
        fired from pos at speed p_speed will intercept a target at
        t_pos moving with velocity t_vel.

        Args:
            pos: Shooter position
            vel: Shooter velocity
            t_pos: Target position
            t_vel: Target velocity
            p_speed: Projectile speed (per tick if vel is per tick)

        Returns:
            Interception time t > 0 if solution exists, else 0
        """
        D = t_pos - pos
        V = t_vel - vel

        a = V.dot(V) - p_speed**2
        b = 2 * V.dot(D)
        c = D.dot(D)

        if a == 0:
            if b == 0:
                return 0
            t = -c / b
            return t if t > 0 else 0

        disc = b * b - 4 * a * c
        if disc < 0:
            return 0

        sqrt_disc = math.sqrt(disc)
        t1 = (-b + sqrt_disc) / (2 * a)
        t2 = (-b - sqrt_disc) / (2 * a)

        ts = [x for x in [t1, t2] if x > 0]
        return min(ts) if ts else 0

    # =========================================================================
    # Target Selection
    # =========================================================================

    def select_target(self, candidates: List[Any]) -> Optional[Any]:
        """
        Select the best target from a list of candidates.

        Filters out friendlies and dead ships, returns closest valid enemy.

        Args:
            candidates: List of potential targets

        Returns:
            Best target or None if no valid targets
        """
        ship = self._ship
        valid_targets = []

        for candidate in candidates:
            # Skip dead ships
            if not getattr(candidate, 'is_alive', True):
                continue
            # Skip friendlies
            if getattr(candidate, 'team_id', -1) == ship.team_id:
                continue
            valid_targets.append(candidate)

        if not valid_targets:
            return None

        # Sort by distance, return closest
        valid_targets.sort(
            key=lambda t: ship.position.distance_to(t.position)
        )
        return valid_targets[0]

    # =========================================================================
    # Firing Solution Calculation
    # =========================================================================

    def calculate_firing_solution(
        self,
        comp: 'Component',
        target: Any
    ) -> Tuple[Vector2, Vector2]:
        """
        Calculate aim position and vector for firing at a target.

        For beam weapons: aims directly at target
        For projectile weapons: leads the target based on projectile speed

        Args:
            comp: The weapon component
            target: The target to fire at

        Returns:
            Tuple of (aim_position, aim_vector)
        """
        ship = self._ship
        aim_pos = target.position

        # Determine target velocity
        t_vel = getattr(target, 'velocity', Vector2(0, 0))

        if comp.has_ability('ProjectileWeaponAbility') or comp.has_ability('SeekerWeaponAbility'):
            # Get projectile speed from the appropriate ability
            if comp.has_ability('SeekerWeaponAbility'):
                proj_ab = comp.get_ability('SeekerWeaponAbility')
            else:
                proj_ab = comp.get_ability('ProjectileWeaponAbility')

            projectile_speed = proj_ab.projectile_speed if proj_ab else 500
            t = self.solve_lead(
                ship.position, ship.velocity,
                target.position, t_vel,
                projectile_speed / 100.0
            )

            if t > 0:
                aim_pos = target.position + t_vel * t
                # Correct for our own velocity (Relative Intercept)
                intercept_vec = aim_pos - ship.position
                aim_vec = intercept_vec - ship.velocity * t
            else:
                # No solution, aim at target
                aim_pos = target.position
                aim_vec = aim_pos - ship.position
        else:
            # Beam weapon - aim directly
            aim_pos = target.position
            aim_vec = aim_pos - ship.position

        return aim_pos, aim_vec

    # =========================================================================
    # Fire Weapons
    # =========================================================================

    def fire_weapons(self, context: Optional[dict] = None) -> List[Any]:
        """
        Fire all ready weapons at available targets.

        Iterates through all weapon components, checks firing conditions,
        and creates projectiles or beam attacks as appropriate.

        Args:
            context: Optional context dict with projectiles list for PDC targeting

        Returns:
            List of attack objects (Projectiles or beam attack dicts)
        """
        ship = self._ship
        attacks = []

        if not ship.is_alive or getattr(ship, 'is_derelict', False):
            return attacks

        for layer_type, comp in ship.iter_components():
            # Handle Hangar Launch
            if comp.has_ability('VehicleLaunch') and comp.is_active:
                attack = self._process_hangar_launch(comp)
                if attack:
                    attacks.append(attack)
                continue

            # Handle Weapons
            if comp.has_ability('WeaponAbility') and comp.is_active:
                attack_result = self._process_weapon_fire(comp, context)
                if attack_result:
                    attacks.extend(attack_result) if isinstance(attack_result, list) else attacks.append(attack_result)

        return attacks

    def _process_hangar_launch(self, comp: 'Component') -> Optional[Dict]:
        """
        Process vehicle launch from hangar component.

        Args:
            comp: Hangar component with VehicleLaunch ability

        Returns:
            Launch attack dict or None
        """
        ship = self._ship
        vl_ability = comp.get_ability('VehicleLaunch')

        # Auto-launch if we have a target
        if ship.current_target and vl_ability.try_launch():
            return {
                'type': AttackType.LAUNCH,
                'source': ship,
                'origin': ship.position,
                'hangar': comp,
                'fighter_class': vl_ability.fighter_class
            }
        return None

    def _process_weapon_fire(
        self,
        comp: 'Component',
        context: Optional[dict] = None
    ) -> Optional[List[Any]]:
        """
        Process firing for a weapon component.

        Validates target, checks firing conditions, and creates attack.

        Args:
            comp: Weapon component
            context: Optional context dict

        Returns:
            List of attacks or None
        """
        ship = self._ship
        weapon_ab = comp.get_ability('WeaponAbility')

        if not comp.can_afford_activation():
            return None

        if not weapon_ab.can_fire():
            return None

        # Find valid target
        target = self._find_valid_target(comp, weapon_ab)
        if not target:
            return None

        # Fire the weapon
        if not weapon_ab.fire(target):
            return None

        # Update stats
        ship.total_shots_fired += 1
        if not hasattr(comp, 'shots_fired'):
            comp.shots_fired = 0
        comp.shots_fired += 1

        # Create attack based on weapon type
        return self._create_attack(comp, weapon_ab, target)

    def _find_valid_target(
        self,
        comp: 'Component',
        weapon_ab: Any
    ) -> Optional[Any]:
        """
        Find a valid target for the weapon.

        Checks primary target and secondary targets, validates each
        against weapon constraints (range, arc, type restrictions).

        Args:
            comp: Weapon component
            weapon_ab: Weapon ability instance

        Returns:
            Valid target or None
        """
        ship = self._ship

        # Build candidate list
        potential_targets = []
        if ship.current_target:
            potential_targets.append(ship.current_target)

        if getattr(ship, 'max_targets', 1) > 1 and hasattr(ship, 'secondary_targets'):
            potential_targets.extend(ship.secondary_targets)

        for candidate in potential_targets:
            if not candidate:
                continue

            # Skip dead or friendly
            if not getattr(candidate, 'is_alive', True):
                continue
            if getattr(candidate, 'team_id', -1) == ship.team_id:
                continue

            # PDC check - non-PDC weapons should not fire at missiles
            is_pdc = comp.has_pdc_ability()
            t_type = getattr(candidate, 'type', 'ship')
            if t_type == 'missile' and not is_pdc:
                continue

            # Validate firing solution
            if comp.has_ability('SeekerWeaponAbility'):
                seeker_ab = comp.get_ability('SeekerWeaponAbility')
                dist = ship.position.distance_to(candidate.position)
                max_range = seeker_ab.projectile_speed * seeker_ab.endurance * 2.0
                if dist <= max_range:
                    return candidate
            else:
                aim_pos, aim_vec = self.calculate_firing_solution(comp, candidate)
                if weapon_ab.check_firing_solution(ship.position, ship.angle, aim_pos):
                    return candidate

        return None

    def _create_attack(
        self,
        comp: 'Component',
        weapon_ab: Any,
        target: Any
    ) -> List[Any]:
        """
        Create attack object(s) for a successful weapon fire.

        Args:
            comp: Weapon component
            weapon_ab: Weapon ability
            target: Target being fired at

        Returns:
            List containing attack object(s)
        """
        ship = self._ship
        attacks = []

        aim_pos, aim_vec = self.calculate_firing_solution(comp, target)

        if comp.has_ability('BeamWeaponAbility'):
            # Beam attack - instant hit
            if not hasattr(comp, 'shots_hit'):
                comp.shots_hit = 0
            comp.shots_hit += 1

            attacks.append({
                'type': AttackType.BEAM,
                'source': ship,
                'target': target,
                'damage': weapon_ab.damage,
                'range': weapon_ab.range,
                'origin': ship.position,
                'component': comp,
                'direction': aim_vec.normalize() if aim_vec.length() > 0 else Vector2(1, 0),
                'hit': True
            })
        else:
            # Projectile attack
            from game.simulation.entities.projectile import Projectile

            if comp.has_ability('SeekerWeaponAbility'):
                projectile = self._create_seeker_projectile(comp, target, aim_vec)
            else:
                projectile = self._create_standard_projectile(comp, target, aim_vec)

            attacks.append(projectile)

        return attacks

    def _create_seeker_projectile(
        self,
        comp: 'Component',
        target: Any,
        aim_vec: Vector2
    ) -> Any:
        """Create a seeker/missile projectile."""
        from game.simulation.entities.projectile import Projectile

        ship = self._ship
        seeker_ab = comp.get_ability('SeekerWeaponAbility')
        weapon_ab = comp.get_ability('WeaponAbility')

        # Calculate launch direction
        comp_facing = ship.angle + getattr(comp, 'facing_angle', 0)
        rad = math.radians(comp_facing)
        launch_vec = Vector2(math.cos(rad), math.sin(rad))

        # Check if target is in arc
        if target:
            rel_pos = target.position - ship.position
            target_angle = math.degrees(math.atan2(rel_pos.y, rel_pos.x))
            diff = (target_angle - comp_facing + 180) % 360 - 180
            if abs(diff) <= (weapon_ab.firing_arc / 2):
                launch_vec = aim_vec.normalize() if aim_vec.length() > 0 else launch_vec

        speed = seeker_ab.projectile_speed / 100.0
        p_vel = launch_vec * speed + ship.velocity

        return Projectile(
            owner=ship,
            position=Vector2(ship.position),
            velocity=p_vel,
            damage=seeker_ab.damage,
            range_val=seeker_ab.projectile_speed * seeker_ab.endurance,
            endurance=seeker_ab.endurance,
            proj_type=AttackType.MISSILE,
            turn_rate=seeker_ab.turn_rate,
            max_speed=speed,
            target=target,
            hp=getattr(seeker_ab, 'missile_hp', 1),
            color=(255, 50, 50),
            source_weapon=comp
        )

    def _create_standard_projectile(
        self,
        comp: 'Component',
        target: Any,
        aim_vec: Vector2
    ) -> Any:
        """Create a standard (non-seeking) projectile."""
        from game.simulation.entities.projectile import Projectile

        ship = self._ship
        projectile_ab = comp.get_ability('ProjectileWeaponAbility')

        speed = projectile_ab.projectile_speed / 100.0
        p_vel = aim_vec.normalize() * speed + ship.velocity

        return Projectile(
            owner=ship,
            position=Vector2(ship.position),
            velocity=p_vel,
            damage=projectile_ab.damage,
            range_val=projectile_ab.range,
            endurance=None,
            proj_type=AttackType.PROJECTILE,
            color=(255, 200, 50),
            source_weapon=comp,
            target=target
        )

    # =========================================================================
    # Damage Application
    # =========================================================================

    def take_damage(self, damage_amount: float) -> None:
        """
        Apply damage to the ship.

        Processes damage through:
        1. Emissive armor (flat reduction)
        2. Crystalline armor (absorption + shield recharge)
        3. Shields
        4. Hull layers (outer to inner)

        Args:
            damage_amount: Amount of damage to apply
        """
        ship = self._ship

        if not ship.is_alive:
            return

        # Apply Emissive Armor Reduction (Flat reduction per hit)
        ea = getattr(ship, 'emissive_armor', 0)
        if ea > 0:
            damage_amount = max(0, damage_amount - ea)
            if damage_amount <= 0:
                return

        # Apply Crystalline Armor (Absorb and Recharge Shields)
        ca = getattr(ship, 'crystalline_armor', 0)
        if ca > 0 and damage_amount > 0:
            absorption = min(ca, damage_amount)
            damage_amount -= absorption

            # Recharge shields
            if ship.max_shields > 0:
                ship.current_shields = min(
                    ship.max_shields,
                    ship.current_shields + absorption
                )

            if damage_amount <= 0:
                return

        remaining_damage = damage_amount

        # Shield Absorption
        if ship.current_shields > 0:
            absorbed = min(ship.current_shields, remaining_damage)
            ship.current_shields -= absorbed
            remaining_damage -= absorbed

        # Dynamic Layer Order: Sort by radius_pct descending (Outermost first)
        sorted_layers = sorted(
            ship.layers.items(),
            key=lambda x: x[1]['radius_pct'],
            reverse=True
        )

        for ltype, layer_data in sorted_layers:
            if remaining_damage <= 0:
                break
            remaining_damage = self._damage_layer(ltype, remaining_damage)

        if remaining_damage < damage_amount:
            ship.recalculate_stats()
            ship.update_derelict_status()

    def _damage_layer(self, layer_type: LayerType, damage: float) -> float:
        """
        Apply damage to a specific layer.

        Uses weighted random selection based on component HP.

        Args:
            layer_type: The layer to damage
            damage: Amount of damage to apply

        Returns:
            Remaining damage after layer absorption
        """
        ship = self._ship
        layer = ship.layers[layer_type]

        while damage > 0:
            # Filter for components with HP > 0
            targets = [c for c in layer['components'] if c.current_hp > 0]

            if not targets:
                break

            # Weighted random selection based on current HP
            weights = [c.current_hp for c in targets]
            target = random.choices(targets, weights=weights, k=1)[0]

            damage_absorbed = min(target.current_hp, damage)
            target.take_damage(damage_absorbed)
            damage -= damage_absorbed

        return damage

    # =========================================================================
    # Combat Cooldowns
    # =========================================================================

    def update_combat_cooldowns(self) -> None:
        """
        Update weapon cooldowns and shield/energy regeneration.

        Called each tick to handle:
        - Shield regeneration
        - Repair application
        """
        ship = self._ship

        if not ship.is_alive:
            return

        # Regenerate Shield
        if ship.current_shields < ship.max_shields and ship.shield_regen_rate > 0:
            regen_amount = ship.shield_regen_rate / 100.0
            cost_amount = ship.shield_regen_cost / 100.0

            has_energy = True
            if cost_amount > 0 and hasattr(ship, 'resources'):
                energy_res = ship.resources.get_resource('energy')
                if energy_res:
                    if energy_res.current_value >= cost_amount:
                        energy_res.consume(cost_amount)
                    else:
                        has_energy = False

            if has_energy:
                ship.current_shields += regen_amount
                if ship.current_shields > ship.max_shields:
                    ship.current_shields = ship.max_shields

        # Apply Ship Repair
        if getattr(ship, 'repair_rate', 0) > 0:
            self._apply_repair(ship.repair_rate / 100.0)

    def _apply_repair(self, repair_amount: float) -> None:
        """
        Apply structural repair to damaged components.

        Args:
            repair_amount: Amount of HP to repair per tick
        """
        ship = self._ship

        if repair_amount <= 0:
            return

        damaged_candidates = [
            c for c in ship.get_all_components()
            if 0 < c.current_hp < c.max_hp
        ]

        if not damaged_candidates:
            return

        # Repair the most damaged (relative) component
        damaged_candidates.sort(key=lambda c: c.current_hp / c.max_hp)
        target = damaged_candidates[0]

        missing = target.max_hp - target.current_hp
        amount_to_apply = min(missing, repair_amount)
        target.current_hp += amount_to_apply

        # Restore status if HP above threshold
        if not target.is_active:
            if target.current_hp > (target.max_hp * 0.5):
                target.is_active = True
                target.status = ComponentStatus.ACTIVE
