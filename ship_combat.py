import pygame
import math
import random
from components import LayerType, Weapon, BeamWeapon, ProjectileWeapon, Bridge
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

    def update_combat_cooldowns(self, dt):
        """Update weapon cooldowns and energy regeneration."""
        if not self.is_alive: return

        # Regenerate Energy
        if self.current_energy < self.max_energy:
            # self.energy_gen_rate provided by host
            self.current_energy += self.energy_gen_rate * dt / 60.0
            if self.current_energy > self.max_energy:
                self.current_energy = self.max_energy
        
        # Regenerate Shields (if energy available)
        if self.current_shields < self.max_shields and self.shield_regen_rate > 0:
            regen_amount = self.shield_regen_rate * dt / 60.0
            cost_amount = self.shield_regen_cost * dt / 60.0
            
            if self.current_energy >= cost_amount:
                self.current_energy -= cost_amount
                self.current_shields += regen_amount
                if self.current_shields > self.max_shields:
                    self.current_shields = self.max_shields
        
        # Component Cooldowns
        for layer in self.layers.values():
            for comp in layer['components']:
                if hasattr(comp, 'update') and comp.is_active:
                    comp.update(dt)

    def fire_weapons(self):
        """
        Attempts to fire all ready weapons.
        Returns a list of dicts representing attacks (Projectiles or Beams).
        """
        attacks = []
        if not self.is_alive: return attacks

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
                        
                        # We need 'aim_vec' for the firing check
                        aim_vec = pygame.math.Vector2(1, 0).rotate(self.angle) # Default forward

                        if self.current_target:
                            target = self.current_target
                            dist = self.position.distance_to(target.position)
                            
                            if dist <= comp.range:
                                # Solve Firing Solution
                                aim_pos, aim_vec = self._calculate_firing_solution(comp, target)

                                # ARC CHECK
                                aim_angle = math.degrees(math.atan2(aim_vec.y, aim_vec.x)) % 360
                                ship_angle = self.angle
                                comp_facing = (ship_angle + comp.facing_angle) % 360
                                diff = (aim_angle - comp_facing + 180) % 360 - 180
                                
                                if abs(diff) <= comp.firing_arc:
                                    valid_target = True
                                else:
                                    # ARC FAIL - Debug logging could go here
                                    # log_debug(f"ARC FAIL...")
                                    pass

                        if valid_target and comp.fire():
                            # Deduct Resource
                            if isinstance(comp, BeamWeapon):
                                self.current_energy -= cost
                                attacks.append({
                                    'type': 'beam',
                                    'source': self,
                                    'target': self.current_target,
                                    'damage': comp.damage,
                                    'range': comp.range,
                                    'origin': self.position,
                                    'component': comp,
                                    'direction': aim_vec.normalize() if aim_vec.length() > 0 else pygame.math.Vector2(1, 0),
                                    'hit': True
                                })
                            else:
                                self.current_ammo -= cost
                                # Projectile
                                speed = comp.projectile_speed if isinstance(comp, ProjectileWeapon) else 1000
                                p_vel = aim_vec.normalize() * speed + self.velocity
                                
                                attacks.append({
                                    'type': 'projectile',
                                    'source': self,
                                    'position': pygame.math.Vector2(self.position),
                                    'velocity': p_vel,
                                    'damage': comp.damage,
                                    'range': comp.range,
                                    'color': (255, 200, 50)
                                })
        return attacks

    def _calculate_firing_solution(self, comp, target):
        """Helper to solve lead and return aim_pos, aim_vec."""
        aim_pos = target.position # Default
        
        if isinstance(comp, ProjectileWeapon):
            t = self.solve_lead(self.position, self.velocity, target.position, target.velocity, comp.projectile_speed)
            if t > 0:
                aim_pos = target.position + target.velocity * t
                
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

    def _damage_layer(self, layer_type, damage):
        layer = self.layers[layer_type]
        living_components = [c for c in layer['components'] if c.is_active]
        
        if not living_components:
            return damage 
            
        target = random.choice(living_components)
        damage_absorbed = min(target.current_hp, damage)
        target.take_damage(damage) 
        
        if isinstance(target, Bridge) and not target.is_active:
            self.die()
            
        return damage - damage_absorbed

    def die(self):
        print(f"{self.name} EXPLODED!")
        self.is_alive = False
        self.velocity = pygame.math.Vector2(0,0)
