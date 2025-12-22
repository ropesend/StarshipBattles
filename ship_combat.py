import pygame
import math
import random
from components import LayerType, Weapon, BeamWeapon, ProjectileWeapon, Bridge, SeekerWeapon
from logger import log_debug

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

        # Regenerate Energy
        if self.current_energy < self.max_energy:
            self.current_energy += self.energy_gen_rate / 100.0
            if self.current_energy > self.max_energy:
                self.current_energy = self.max_energy
        
        # Regenerate Shields (if energy available)
        if self.current_shields < self.max_shields and self.shield_regen_rate > 0:
            regen_amount = self.shield_regen_rate / 100.0
            cost_amount = self.shield_regen_cost / 100.0
            
            if self.current_energy >= cost_amount:
                self.current_energy -= cost_amount
                self.current_shields += regen_amount
                if self.current_shields > self.max_shields:
                    self.current_shields = self.max_shields
        
        # Component Cooldowns
        for layer in self.layers.values():
            for comp in layer['components']:
                if hasattr(comp, 'update') and comp.is_active:
                    # Pass 1 tick (0.01 seconds) to update
                    comp.update()

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
                if isinstance(comp, Weapon) and comp.is_active:
                    # Determine cost and resource type
                    cost = 0
                    has_resource = False
                    
                    if isinstance(comp, BeamWeapon):
                        cost = comp.energy_cost
                        has_resource = (self.current_energy >= cost)
                    else:
                        cost = comp.ammo_cost
                        has_resource = (self.current_ammo >= cost)
                    
                    if has_resource and comp.can_fire():
                        # TARGETING logic
                        valid_target = False
                        target = self.current_target
                        
                        # PDC Override: look for missiles if context provided
                        is_pdc = comp.abilities.get('PointDefense', False)
                        if is_pdc and context:
                            pdc_target = self._find_pdc_target(comp, context)
                            if pdc_target:
                                target = pdc_target
                        
                        # If no target found for PDC, it can still fire at main target if valid?
                        # Usually PDCs only fire at missiles/fighters. 
                        # Let's say if it found a missile target, use it. 
                        # Else if it's dual purpose, use main target?
                        # For now, strict PDC behavior: ONLY targets missiles if found, else if main target is close enough?
                        # Ignoring main target for PDC unless it matches criteria?
                        # Let's assume PDCs can shoot ships if no missiles.
                        
                        if not target: continue
                        
                        # Distance Check
                        dist = self.position.distance_to(target.position)
                        max_range = comp.range
                        if isinstance(comp, SeekerWeapon):
                            # Approximate max range for initial check
                            max_range = comp.projectile_speed * comp.endurance * 2.0 

                        if dist <= max_range:
                            # Solve Firing Solution
                            aim_pos, aim_vec = self._calculate_firing_solution(comp, target)
                            
                            # ARC CHECK
                            aim_angle = math.degrees(math.atan2(aim_vec.y, aim_vec.x)) % 360
                            ship_angle = self.angle
                            comp_facing = (ship_angle + comp.facing_angle) % 360
                            diff = (aim_angle - comp_facing + 180) % 360 - 180
                            
                            if abs(diff) <= comp.firing_arc:
                                valid_target = True
                            elif isinstance(comp, SeekerWeapon):
                                # Seeker weapons can launch if target is out of arc
                                valid_target = True
                        
                        if valid_target and comp.fire():
                            self.total_shots_fired += 1
                            comp.shots_fired += 1
                            
                            # Deduct Resource
                            if isinstance(comp, BeamWeapon):
                                self.current_energy -= cost
                                comp.shots_hit += 1 # Beams are hitscan and we only fire if valid_target (in arc/range)
                                # Technically valid_target means "can hit", but accuracy fail?
                                # BeamWeapon has accuracy falloff. 
                                # Current 'fire_weapons' logic assumes 100% hit if valid_target?
                                # Lines 120-129 create 'beam' attack dict with 'hit': True.
                                # So yes, increment hits.
                                
                                attacks.append({
                                    'type': 'beam',
                                    'source': self,
                                    'target': target,
                                    'damage': comp.damage,
                                    'range': comp.range,
                                    'origin': self.position,
                                    'component': comp,
                                    'direction': aim_vec.normalize() if aim_vec.length() > 0 else pygame.math.Vector2(1, 0),
                                    'hit': True
                                })
                            else:
                                from projectiles import Projectile
                                self.current_ammo -= cost
                                
                                # Seeker Logic
                                if isinstance(comp, SeekerWeapon):
                                    # Launch vector
                                    rad = math.radians(comp_facing)
                                    launch_vec = pygame.math.Vector2(math.cos(rad), math.sin(rad))
                                    
                                    # If target in arc, launch at target
                                    if abs(diff) <= comp.firing_arc:
                                        launch_vec = aim_vec.normalize() if aim_vec.length() > 0 else launch_vec

                                    speed = comp.projectile_speed / 100.0  # Pixels/tick
                                    p_vel = launch_vec * speed + self.velocity
                                    
                                    proj = Projectile(
                                        owner=self,
                                        position=pygame.math.Vector2(self.position),
                                        velocity=p_vel,
                                        damage=comp.damage,
                                        range_val=comp.projectile_speed * comp.endurance,
                                        endurance=comp.endurance,
                                        proj_type='missile',
                                        turn_rate=comp.turn_rate,
                                        max_speed=speed,
                                        target=target,
                                        hp=comp.hp,
                                        color=(255, 50, 50),
                                        source_weapon=comp
                                    )
                                    attacks.append(proj)
                                    
                                else:
                                    # Standard Projectile
                                    speed = comp.projectile_speed / 100.0
                                    p_vel = aim_vec.normalize() * speed + self.velocity
                                    
                                    proj = Projectile(
                                        owner=self,
                                        position=pygame.math.Vector2(self.position),
                                        velocity=p_vel,
                                        damage=comp.damage,
                                        range_val=comp.range,
                                        endurance=None, # Range limited
                                        proj_type='projectile',
                                        color=(255, 200, 50),
                                        source_weapon=comp
                                    )
                                    attacks.append(proj)
        return attacks

    def _find_pdc_target(self, comp, context):
        """Find the best target for a Point Defense Cannon."""
        projectiles = context.get('projectiles', [])
        if not projectiles: return None
        
        possible_targets = []
        for p in projectiles:
            if not p.is_alive: continue
            if getattr(p, 'team_id', -1) == self.team_id: continue # Don't shoot friendly missiles
            
            # Check range
            dist = self.position.distance_to(p.position)
            if dist > comp.range: continue
                
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
        
        if isinstance(comp, ProjectileWeapon):
            t = self.solve_lead(self.position, self.velocity, target.position, t_vel, comp.projectile_speed / 100.0)
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

        remaining_damage = damage_amount
        
        # Shield Absorption
        if self.current_shields > 0:
            absorbed = min(self.current_shields, remaining_damage)
            self.current_shields -= absorbed
            remaining_damage -= absorbed
            
        layer_order = [LayerType.ARMOR, LayerType.OUTER, LayerType.INNER, LayerType.CORE]
        
        for ltype in layer_order:
            if remaining_damage <= 0: break
            remaining_damage = self._damage_layer(ltype, remaining_damage)
            
        if remaining_damage < damage_amount:
            self.recalculate_stats()

    def _damage_layer(self, layer_type, damage):
        layer = self.layers[layer_type]
        living_components = [c for c in layer['components'] if c.is_active]
        
        if not living_components:
            return damage 
            
        target = random.choice(living_components)
        damage_absorbed = min(target.current_hp, damage)
        target.take_damage(damage_absorbed)  # FIX: Only deal absorbed amount, not full damage
        
        if isinstance(target, Bridge) and not target.is_active:
            self.die()
            
        return damage - damage_absorbed

    def die(self):
        print(f"{self.name} EXPLODED!")
        self.is_alive = False
        self.velocity = pygame.math.Vector2(0,0)
        # Recalculate to ensure UI shows 0 stats
        self.recalculate_stats()
