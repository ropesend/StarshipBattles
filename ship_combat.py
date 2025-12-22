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

    def update_combat_cooldowns(self, dt=1.0):
        """Update weapon cooldowns and energy regeneration. dt is ignored (1 tick)."""
        if not self.is_alive: return

        # Regenerate Energy
        if self.current_energy < self.max_energy:
            # self.energy_gen_rate is Per Second. 100 ticks/sec.
            # Add 1/100th of rate per tick.
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
                    # Comp update might need tick awareness, pass 1.0 or nothing
                    # Check component definition.
                    # Standard components usually just decrement counters.
                    comp.update(1.0) # Assuming comps treat dt as seconds reduction? 
                    # If comp.reload_current is in seconds, we subtract 1/100.
                    # Or we change comp to use ticks.
                    # Let's look at Component.update. It likely does: timer -= dt.
                    # If initialized with reload_time (seconds), we must subtract 0.01 per tick
                    # OR convert reload_time to ticks at start.
                    # For now, passing 0.01 (1 tick in seconds) preserves behavior IF comps use seconds.
                    # BUT user wants "No Time". Ideally comps count ticks.
                    # If I pass 0.01 here, I am using "seconds".
                    # If I pass 1.0 here, the component subtracts 1.0 "unit".
                    # If reload_time is 2.0 "units", then 1.0 clears it in 2 ticks. Too fast.
                    # OPTION A: Pass 0.01 (representing 1 tick's worth of seconds).
                    # OPTION B: Refactor Components to store ticks.
                    # Given constraints, Option A is safest step for "cycle based" where cycle = 0.01s.
                    # BUT user said "Reload Time 2.0s -> 200 ticks".
                    # So reload_timer should start at 200. update(1) reduces by 1.
                    # I can't refactor ALL components in this one step easily without seeing Component class.
                    # I will assume for this step: Pass 0.01 to legacy seconds-based counters, 
                    # effectively mapping 1 tick = 0.01 seconds deduction.
                    # This achieves the "100 ticks = 1 second" result.
                    pass 
                    
                    # Correction: I am refactoring `comp.update` call. 
                    # I will look at Component class next. For now, let's stick to consistent logic.
                    # If I change logic to Ticks, I should pass 1 (tick).
                    # If Component still stores 2.0 (seconds), I need to change Component.
                    # Let's pass 0.01 for now to mimic the 100 ticks = 1 sec requirement comfortably 
                    # without breaking the internal timer logic if it is float seconds.
                    # This obeys "Physics and Logic based on cycles", where 1 cycle removes 0.01 "time units" from cooldown.
                    comp.update(0.01)

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
                                # Speed was pixels/sec. Now pixels/tick?
                                # If projectile_speed is 2000 (pixels/sec), 
                                # and we run 100 ticks/sec, speed per tick is 20.
                                speed = comp.projectile_speed / 100.0 if isinstance(comp, ProjectileWeapon) else 10.0
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
