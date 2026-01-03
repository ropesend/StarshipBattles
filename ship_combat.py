import pygame
import math
import random
from components import LayerType, ComponentStatus  # Phase 7: Removed Bridge, Weapon, etc. (now use abilities)
from logger import log_debug
from game_constants import AttackType

class ShipCombatMixin:
    """
    Mixin class handling ship combat (firing, taking damage).
    Requires the host class to have:
    - layers (dict of components)
    - current_energy, current_ammo, is_alive
    - position, velocity, angle
    - current_target (for aiming)
    """

    def update_combat_cooldowns(self):
        """Update weapon cooldowns and energy regeneration. Assumes 1 tick cycle."""
        if not self.is_alive: return

        # Regenerate Shield (Custom Logic preserved as per Plan)
        # Using Generic Energy Resource
        if self.current_shields < self.max_shields and self.shield_regen_rate > 0:
            regen_amount = self.shield_regen_rate / 100.0
            cost_amount = self.shield_regen_cost / 100.0
            
            # Use Generic Resource
            has_energy = True
            if cost_amount > 0 and hasattr(self, 'resources'):
                energy_res = self.resources.get_resource('energy')
                if energy_res:
                    if energy_res.current_value >= cost_amount:
                        energy_res.consume(cost_amount)
                    else:
                        has_energy = False

            
            if has_energy:
                self.current_shields += regen_amount
                if self.current_shields > self.max_shields:
                    self.current_shields = self.max_shields
        
        # Apply Ship Repair
        if getattr(self, 'repair_rate', 0) > 0:
             self._apply_repair(self.repair_rate / 100.0)

        # Component Cooldowns - Moved to Ship.update()
        pass

    def fire_weapons(self, context=None):
        """
        Attempts to fire all ready weapons.
        Args:
            context (dict): Optional combat context dict containing 'projectiles' list, 'grid', etc.
        Returns a list of Projectile objects or dicts (for beams).
        """
        attacks = []
        if not self.is_alive or getattr(self, 'is_derelict', False): return attacks

        for layer in self.layers.values():
            for comp in layer['components']:
                # Handle Hangar Launch (Phase 4: ability-based check)
                if comp.has_ability('VehicleLaunch') and comp.is_active:
                    vl_ability = comp.get_ability('VehicleLaunch')
                    # Auto-launch if we have a target (or maybe strategy dictates?)
                    # For now, if we have a target, we launch.
                    if self.current_target and vl_ability.try_launch():
                        attacks.append({
                            'type': AttackType.LAUNCH,
                            'source': self,
                            'origin': self.position,
                            'hangar': comp,
                            'fighter_class': vl_ability.fighter_class
                        })
                    continue

                if comp.has_ability('WeaponAbility') and comp.is_active:
                    # Get weapon ability for attribute access
                    weapon_ab = comp.get_ability('WeaponAbility')
                    
                    # Check resources via Component Abilities
                    has_resource = comp.can_afford_activation()
                    
                    if has_resource and weapon_ab.can_fire():
                        # TARGETING logic
                        valid_target = False
                        target = None
                        
                        # Potential targets list: Primary + Secondaries
                        potential_targets = []
                        if self.current_target:
                            potential_targets.append(self.current_target)
                        
                        # Only consider secondary targets if we have the capability
                        # (Although max_targets should handle the list population, safe to check)
                        if getattr(self, 'max_targets', 1) > 1 and hasattr(self, 'secondary_targets'):
                            potential_targets.extend(self.secondary_targets)

                        # PDC Override REMOVED - Rely on AI prioritization in secondary_targets
                        
                        # Iterate through potential targets to find the first one we can hit
                        for candidate in potential_targets:
                            if not candidate: continue
                            
                            # Safety: don't target dead things or friendlies
                            if not getattr(candidate, 'is_alive', True): continue
                            if getattr(candidate, 'team_id', -1) == self.team_id: continue

                            # Specialization check: Non-PDC weapons should NOT fire at missiles
                            # Phase 4: Use ability tags instead of legacy dict
                            is_pdc = comp.has_pdc_ability()
                            t_type = getattr(candidate, 'type', 'ship')
                            if t_type == 'missile' and not is_pdc:
                                continue # Standard guns ignore missiles
                                
                            # Simplified Phase 9 Logic: Delegate to Ability
                            # Note: SeekerWeapons handle their own range/arc logic inside check_firing_solution override if needed,
                            # or we handle special seeker logic here.
                            
                            if comp.has_ability('SeekerWeaponAbility'):
                                # Seeker Weapons have unique rules (infinite arc, range = speed*endurance)
                                seeker_ab = comp.get_ability('SeekerWeaponAbility')
                                # Simple proximity check for Seekers (they chase, so arc is irrelevant for launch usually)
                                dist = self.position.distance_to(candidate.position)
                                max_range = seeker_ab.projectile_speed * seeker_ab.endurance * 2.0
                                if dist <= max_range:
                                    valid_target = True
                                    target = candidate
                                    break
                            else:
                                # Standard Direct-Fire Weapons
                                # 1. Solve Lead
                                aim_pos, aim_vec = self._calculate_firing_solution(comp, candidate)
                                
                                # 2. Check Arc/Range using Intercept Point
                                if weapon_ab.check_firing_solution(self.position, self.angle, aim_pos):
                                    valid_target = True
                                    target = candidate
                                    break

                        if valid_target and target and weapon_ab.fire(target):
                            self.total_shots_fired += 1
                            # Phase 7: Safe attribute access after Weapon alias conversion
                            if not hasattr(comp, 'shots_fired'): comp.shots_fired = 0
                            comp.shots_fired += 1
                            
                            # Deduct Resource generically
                            comp.consume_activation()
                            
                            # Deduct Resource
                            if comp.has_ability('BeamWeaponAbility'):
                                # Phase 7: Safe attribute access
                                if not hasattr(comp, 'shots_hit'): comp.shots_hit = 0
                                comp.shots_hit += 1 # Beams are hitscan and we only fire if valid_target (in arc/range)
                                # Technically valid_target means "can hit", but accuracy fail?
                                # BeamWeapon has accuracy falloff. 
                                # Current 'fire_weapons' logic assumes 100% hit if valid_target?
                                # Lines 120-129 create 'beam' attack dict with 'hit': True.
                                # So yes, increment hits.
                                
                                attacks.append({
                                    'type': AttackType.BEAM,
                                    'source': self,
                                    'target': target,
                                    'damage': weapon_ab.damage,
                                    'range': weapon_ab.range,
                                    'origin': self.position,
                                    'component': comp,
                                    'direction': aim_vec.normalize() if aim_vec.length() > 0 else pygame.math.Vector2(1, 0),
                                    'hit': True
                                })
                            else:
                                from projectiles import Projectile
                                
                                # Seeker Logic
                                
                                # Seeker Logic
                                if comp.has_ability('SeekerWeaponAbility'):
                                    seeker_ab = comp.get_ability('SeekerWeaponAbility')
                                    
                                    # Launch vector
                                    rad = math.radians(comp_facing)
                                    launch_vec = pygame.math.Vector2(math.cos(rad), math.sin(rad))
                                    
                                    # If target in arc, launch at target
                                    if abs(diff) <= (weapon_ab.firing_arc / 2):
                                        launch_vec = aim_vec.normalize() if aim_vec.length() > 0 else launch_vec

                                    speed = seeker_ab.projectile_speed / 100.0  # Pixels/tick
                                    p_vel = launch_vec * speed + self.velocity
                                    
                                    proj = Projectile(
                                        owner=self,
                                        position=pygame.math.Vector2(self.position),
                                        velocity=p_vel,
                                        damage=seeker_ab.damage,
                                        range_val=seeker_ab.projectile_speed * seeker_ab.endurance,
                                        endurance=seeker_ab.endurance,
                                        proj_type=AttackType.MISSILE,
                                        turn_rate=seeker_ab.turn_rate,
                                        max_speed=speed,
                                        target=target,
                                        hp=getattr(seeker_ab, 'missile_hp', 1),  # Use Ability stats
                                        color=(255, 50, 50),
                                        source_weapon=comp
                                    )
                                    attacks.append(proj)
                                    
                                else:
                                    # Standard Projectile
                                    projectile_ab = comp.get_ability('ProjectileWeaponAbility')
                                    speed = projectile_ab.projectile_speed / 100.0
                                    p_vel = aim_vec.normalize() * speed + self.velocity
                                    
                                    proj = Projectile(
                                        owner=self,
                                        position=pygame.math.Vector2(self.position),
                                        velocity=p_vel,
                                        damage=projectile_ab.damage,
                                        range_val=projectile_ab.range,
                                        endurance=None, # Range limited
                                        proj_type=AttackType.PROJECTILE,
                                        color=(255, 200, 50),
                                        source_weapon=comp,
                                        target=target
                                    )

                                    attacks.append(proj)
        return attacks

    def _find_pdc_target(self, comp, context):
        """Find the best target for a Point Defense Cannon."""
        projectiles = context.get('projectiles', [])
        if not projectiles: return None
        
        # Get weapon ability for range check
        weapon_ab = comp.get_ability('WeaponAbility')
        weapon_range = weapon_ab.range if weapon_ab else 0
        
        possible_targets = []
        for p in projectiles:
            if not p.is_alive: continue
            if getattr(p, 'team_id', -1) == self.team_id: continue # Don't shoot friendly missiles
            
            # Check range
            dist = self.position.distance_to(p.position)
            if dist > weapon_range: continue
                
            possible_targets.append((p, dist))
            
        if not possible_targets: return None
        
        # Sort by distance (closest first)
        possible_targets.sort(key=lambda x: x[1])
        return possible_targets[0][0]

    def _calculate_firing_solution(self, comp, target):
        """Helper to solve lead and return aim_pos, aim_vec."""
        aim_pos = target.position 
        
        # Determine target velocity
        t_vel = getattr(target, 'velocity', pygame.math.Vector2(0,0))
        
        if comp.has_ability('ProjectileWeaponAbility') or comp.has_ability('SeekerWeaponAbility'):
            # Get projectile speed from the appropriate ability
            if comp.has_ability('SeekerWeaponAbility'):
                proj_ab = comp.get_ability('SeekerWeaponAbility')
            else:
                proj_ab = comp.get_ability('ProjectileWeaponAbility')
            
            projectile_speed = proj_ab.projectile_speed if proj_ab else 500
            t = self.solve_lead(self.position, self.velocity, target.position, t_vel, projectile_speed / 100.0)
            if t > 0:
                aim_pos = target.position + t_vel * t
                
                # Correct for our own velocity (Relative Intercept)
                intercept_vec = aim_pos - self.position
                aim_vec = intercept_vec - self.velocity * t
            else:
                 # No solution, aim at target
                 aim_pos = target.position
                 aim_vec = aim_pos - self.position
        else:
             # Beam
             aim_pos = target.position
             aim_vec = aim_pos - self.position
             
        return aim_pos, aim_vec

    def solve_lead(self, pos, vel, t_pos, t_vel, p_speed):
        """
        Calculates interception time t for a projectile.
        Returns t > 0 if solution found, else 0.
        Note: p_speed should be per tick if vel is per tick.
        """
        D = t_pos - pos
        V = t_vel - vel
        
        a = V.dot(V) - p_speed**2
        b = 2 * V.dot(D)
        c = D.dot(D)
        
        if a == 0:
            if b == 0: return 0
            t = -c / b
            return t if t > 0 else 0
        
        disc = b*b - 4*a*c
        if disc < 0: return 0
        
        sqrt_disc = math.sqrt(disc)
        t1 = (-b + sqrt_disc) / (2*a)
        t2 = (-b - sqrt_disc) / (2*a)
        
        ts = [x for x in [t1, t2] if x > 0]
        return min(ts) if ts else 0

    def take_damage(self, damage_amount):
        if not self.is_alive: return

        # Apply Emissive Armor Reduction (Flat reduction per hit)
        ea = getattr(self, 'emissive_armor', 0)
        if ea > 0:
            damage_amount = max(0, damage_amount - ea)
            if damage_amount <= 0:
                return

        # Apply Crystalline Armor (Absorb and Recharge Shields)
        ca = getattr(self, 'crystalline_armor', 0)
        if ca > 0 and damage_amount > 0:
            absorption = min(ca, damage_amount)
            
            # Reduce Damage
            damage_amount -= absorption
            
            # Recharge Shields
            # Only recharge if shields are active (max_shields > 0)
            if self.max_shields > 0:
                self.current_shields = min(self.max_shields, self.current_shields + absorption)
                
            if damage_amount <= 0:
                return

        remaining_damage = damage_amount
        
        # Shield Absorption
        if self.current_shields > 0:
            absorbed = min(self.current_shields, remaining_damage)
            self.current_shields -= absorbed
            remaining_damage -= absorbed
            
        # Dynamic Layer Order: Sort by radius_pct descending (Outermost first)
        sorted_layers = sorted(self.layers.items(), key=lambda x: x[1]['radius_pct'], reverse=True)
        
        for ltype, layer_data in sorted_layers:
            if remaining_damage <= 0: break
            remaining_damage = self._damage_layer(ltype, remaining_damage)
            
        if remaining_damage < damage_amount:
            self.recalculate_stats()
            self.update_derelict_status()

    def _damage_layer(self, layer_type, damage):
        layer = self.layers[layer_type]
        
        # Loop until damage is exhausted or no valid targets remain
        while damage > 0:
            # Filter for components with HP > 0 (even if inactive/non-functional)
            targets = [c for c in layer['components'] if c.current_hp > 0]
            
            if not targets:
                break
                
            # Weighted random selection based on current HP
            # Higher HP = higher chance to be hit
            weights = [c.current_hp for c in targets]
            
            # random.choices returns a list, even for k=1
            target = random.choices(targets, weights=weights, k=1)[0]
            
            damage_absorbed = min(target.current_hp, damage)
            target.take_damage(damage_absorbed)
            
            damage -= damage_absorbed
            
            # REMOVED: Hardcoded Bridge death. 
            # if isinstance(target, Bridge) and target.current_hp <= 0:
            #     self.die() 
            #     break 
                
        return damage

    def die(self):
        print(f"{self.name} EXPLODED!")
        self.is_alive = False
        self.velocity = pygame.math.Vector2(0,0)
        # Recalculate to ensure UI shows 0 stats
        self.recalculate_stats()

    def _apply_repair(self, repair_amount):
        """Apply structural repair to damaged components."""
        if repair_amount <= 0: return

        # Identify damaged components (Current HP < Max HP)
        # Filter for live components only (HP > 0) to avoid reviving dead parts (unless desired?)
        # For now, sticking to repairing 'damaged' but not strict 'destroyed' logic,
        # but consistency with `_damage_layer` which stops at 0 suggests 0 is dead.
        damaged_candidates = []
        for layer in self.layers.values():
            for comp in layer['components']:
                if 0 < comp.current_hp < comp.max_hp:
                     damaged_candidates.append(comp)

        if not damaged_candidates:
            return

        # Strategy: Repair the most damaged one (relative) to try and restore functionality
        damaged_candidates.sort(key=lambda c: c.current_hp / c.max_hp)

        target = damaged_candidates[0]
        
        # Apply repair
        missing = target.max_hp - target.current_hp
        amount_to_apply = min(missing, repair_amount)
        
        target.current_hp += amount_to_apply
        
        # Check Status Restoration
        # If component was considered inactive/damaged due to HP <= 50%, restore it
        if not target.is_active:
             if target.current_hp > (target.max_hp * 0.5):
                 target.is_active = True
                 target.status = ComponentStatus.ACTIVE

