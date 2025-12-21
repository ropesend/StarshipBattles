import pygame
import random
import math
import json
import os
from physics import PhysicsBody
from components import Component, LayerType, Bridge, Engine, Thruster, Tank, Armor, Weapon, Generator, BeamWeapon, ProjectileWeapon, CrewQuarters, LifeSupport, Sensor, Electronics
from logger import log_debug


# Load Vehicle Classes from JSON
VEHICLE_CLASSES = {}
SHIP_CLASSES = {}  # Legacy compatibility - maps class name to max_mass

def load_vehicle_classes(filepath="data/vehicleclasses.json"):
    global VEHICLE_CLASSES, SHIP_CLASSES
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            VEHICLE_CLASSES = data.get('classes', {})
            # Build legacy SHIP_CLASSES dict for backward compatibility
            SHIP_CLASSES = {name: cls['max_mass'] for name, cls in VEHICLE_CLASSES.items()}
    except FileNotFoundError:
        print(f"Warning: {filepath} not found, using defaults")
        VEHICLE_CLASSES = {
            "Escort": {"hull_mass": 50, "max_mass": 1000, "requirements": {}},
            "Frigate": {"hull_mass": 100, "max_mass": 2000, "requirements": {}},
            "Destroyer": {"hull_mass": 200, "max_mass": 4000, "requirements": {}},
            "Cruiser": {"hull_mass": 400, "max_mass": 8000, "requirements": {}},
            "Battlecruiser": {"hull_mass": 800, "max_mass": 16000, "requirements": {}},
            "Battleship": {"hull_mass": 1600, "max_mass": 32000, "requirements": {}},
            "Dreadnought": {"hull_mass": 3200, "max_mass": 64000, "requirements": {}}
        }
        SHIP_CLASSES = {name: cls['max_mass'] for name, cls in VEHICLE_CLASSES.items()}

# Load on module import
load_vehicle_classes()

class Ship(PhysicsBody):
    def __init__(self, name, x, y, color, team_id=0, ship_class="Escort"):
        super().__init__(x, y)
        self.name = name
        self.color = color
        self.team_id = team_id
        self.current_target = None
        self.ship_class = ship_class
        
        # Layers
        self.layers = {
            LayerType.CORE:  {'components': [], 'radius_pct': 0.2, 'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0},
            LayerType.INNER: {'components': [], 'radius_pct': 0.5, 'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0},
            LayerType.OUTER: {'components': [], 'radius_pct': 0.8, 'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0},
            LayerType.ARMOR: {'components': [], 'radius_pct': 1.0, 'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0}
        }
        
        # Stats
        self.mass = 0
        # Get hull mass from vehicle class definition
        class_def = VEHICLE_CLASSES.get(self.ship_class, {"hull_mass": 50, "max_mass": 1000})
        self.base_mass = class_def.get('hull_mass', 50)  # Hull/Structure mass from class
        self.total_thrust = 0
        self.max_speed = 0
        self.turn_speed = 0
        self.drag = 0.5 # New Arcade Drag
        
        # Budget
        self.max_mass_budget = SHIP_CLASSES.get(self.ship_class, 1000)
        
        self.radius = 40 # Will be recalculated
        
        # Resources (Capacities and Current)
        self.max_energy = 100
        self.current_energy = 100
        self.max_fuel = 1000
        self.current_fuel = 1000
        self.max_ammo = 100
        self.current_ammo = 100
        self.energy_gen_rate = 5.0
        
        # New Stats (from old init, but now calculated or managed differently)
        self.mass_limits_ok = True
        self.layer_status = {}
        
        # Old init values, now calculated or managed differently
        self.current_mass = 0 # Replaced by self.mass and self.base_mass
        # self.max_fuel = 0 # Now initialized to 1000
        # self.current_fuel = 0 # Now initialized to 1000
        # self.max_ammo = 0 # Now initialized to 100
        # self.current_ammo = 0 # Now initialized to 100
        # self.max_energy = 0 # Now initialized to 100
        # self.current_energy = 0 # Now initialized to 100
        # self.energy_gen_rate = 0 # Now initialized to 5.0
        
        # Stats
        # self.total_thrust = 0 # Now initialized to 0
        # self.turn_speed = 0 # Now initialized to 0
        self.is_alive = True
        self.bridge_destroyed = False
        
        # AI Strategy
        self.ai_strategy = "optimal_firing_range"  # See combatstrategies.json for options
        
        # Arcade Physics
        self.current_speed = 0
        self.acceleration_rate = 0
        # self.max_speed = 0 # Now initialized to 0
        
        # Collision
        # self.radius = 40 # Now initialized to 40, but will be recalculated

    def add_component(self, component: Component, layer_type: LayerType):
        if layer_type not in component.allowed_layers:
            print(f"Error: {component.name} not allowed in {layer_type}")
            return False

        if self.current_mass + component.mass > self.max_mass_budget:
            print(f"Error: Mass budget exceeded for {self.name}")
            return False
            
        self.layers[layer_type]['components'].append(component)
        component.layer_assigned = layer_type
        self.current_mass += component.mass
        
        # Update Stats
        self.recalculate_stats()
        return True
        
    def remove_component(self, layer_type: LayerType, index: int):
        if 0 <= index < len(self.layers[layer_type]['components']):
            comp = self.layers[layer_type]['components'].pop(index)
            self.current_mass -= comp.mass
            self.recalculate_stats()
            return comp
        return None

    def recalculate_stats(self):
        # 1. Recalculate Total Mass from scratch first
        self.current_mass = 0
        self.layer_status = {}
        self.mass_limits_ok = True
        self.drag = 0.5 
        
        # Initial pass for mass to ensure self.mass is correct for physics calc later
        for layer_type, layer_data in self.layers.items():
            l_mass = sum(c.mass for c in layer_data['components'])
            layer_data['mass'] = l_mass
            self.current_mass += l_mass
            
        self.mass = self.current_mass + self.base_mass

        # Base Stats Reset
        self.total_thrust = 0
        self.turn_speed = 0
        self.max_fuel = 0
        self.max_ammo = 0
        self.max_energy = 0
        self.energy_gen_rate = 0
        
        # Budget & Scaling
        self.max_mass_budget = SHIP_CLASSES.get(self.ship_class, 1000)
        
        # Radius Scaling - based on actual mass (cube root scaling)
        base_radius = 40
        ref_mass = 1000
        actual_mass = max(self.mass, 100)  # Use actual mass, minimum 100 to avoid tiny radius
        ratio = actual_mass / ref_mass
        self.radius = base_radius * (ratio ** (1/3.0))

        self.layers[LayerType.ARMOR]['max_hp_pool'] = 0
        
        # Component Stats Aggregation
        for layer_type, layer_data in self.layers.items():
            for comp in layer_data['components']:
                if isinstance(comp, Engine):
                    self.total_thrust += comp.thrust_force
                elif isinstance(comp, Thruster):
                    self.turn_speed += comp.turn_speed
                elif isinstance(comp, Generator):
                    self.energy_gen_rate += comp.energy_generation_rate
                elif isinstance(comp, Tank):
                    if comp.resource_type == 'fuel':
                        self.max_fuel += comp.capacity
                    elif comp.resource_type == 'ammo':
                        self.max_ammo += comp.capacity
                    elif comp.resource_type == 'energy':
                        self.max_energy += comp.capacity
                elif isinstance(comp, Armor) and layer_type == LayerType.ARMOR:
                    self.layers[LayerType.ARMOR]['max_hp_pool'] += comp.max_hp
                    
        # Reset current resources if initializing (simplified)
        if self.current_fuel == 0: self.current_fuel = self.max_fuel
        if self.current_ammo == 0: self.current_ammo = self.max_ammo
        if self.current_energy == 0: self.current_energy = self.max_energy
        
        # Armor HP initialization
        if self.layers[LayerType.ARMOR]['hp_pool'] == 0:
            self.layers[LayerType.ARMOR]['hp_pool'] = self.layers[LayerType.ARMOR]['max_hp_pool']
            
        # Physics Stats - INVERSE MASS SCALING
        # Max Speed proportional to 1/Mass
        # Accel proportional to 1/Mass^2
        # Turn proportional to 1/Mass^1.5 (changed from mass^2 for less sluggish heavy ships)
        
        # Tuning Constants - scaled for tick-based physics (dt=1.0 per tick)
        # Previously tuned for dt=1/60, now divided by 60
        K_THRUST = 2500  # Was 150000, now 150000/60
        K_TURN = 2500    # Was 150000, now 150000/60
        
        if self.mass > 0:
            self.acceleration_rate = (self.total_thrust * K_THRUST) / (self.mass * self.mass)
            # turn_speed was already accumulated from thrusters above, now apply mass scaling
            raw_turn_speed = self.turn_speed  # This is the sum from all thrusters
            self.turn_speed = (raw_turn_speed * K_TURN) / (self.mass ** 1.5)  # Changed to 1.5 exponent
            
            # Max Speed = Thrust / Mass logic (Linear)
            # Or maintain drag model?
            # User said "top speed proportional to 1/ mass".
            # With Accel ~ 1/m^2 and Drag constant, Max Speed would be 1/m^2. 
            # So we must adjust Drag or Max Speed calculation explicitly.
            
            # Let's enforce Max Speed explicitly
            K_SPEED = 25  # Was 1500, now 1500/60
            self.max_speed = (self.total_thrust * K_SPEED) / self.mass if self.total_thrust > 0 else 0
            
            # Adjust Drag so that Accel / Drag ~= Max Speed?
            # Accel = T*K_T/m^2.  MaxSpeed = T*K_S/m.
            # Drag = Accel / MaxSpeed = (T*K_T/m^2) / (T*K_S/m) = (K_T/K_S) * (1/m)
            # So Drag must be proportional to 1/m.
            
            if self.max_speed > 0:
                self.drag = self.acceleration_rate / self.max_speed
            else:
                self.drag = 0.5
        else:
            self.acceleration_rate = 0
            self.max_speed = 0
            
        # Ensure minimums only if we have engines
        if self.total_thrust > 0 and self.max_speed < 10: self.max_speed = 10
            
        # Validate Limits
        self.mass_limits_ok = True
        self.layer_limits = {
            LayerType.ARMOR: 0.30,
            LayerType.CORE: 0.30,
            LayerType.OUTER: 0.50,
            LayerType.INNER: 0.50
        }
        self.layer_status = {}
        

        for layer_type, layer_data in self.layers.items():
            # Ratio is now based on MAX BUDGET, not current mass
            limit_ratio = self.layer_limits.get(layer_type, 1.0)
            ratio = layer_data['mass'] / self.max_mass_budget
            
            is_ok = ratio <= limit_ratio
            self.layer_status[layer_type] = {
                'mass': layer_data['mass'],
                'ratio': ratio,
                'limit': limit_ratio,
                'ok': is_ok
            }
            if not is_ok: self.mass_limits_ok = False
        
        if self.current_mass > self.max_mass_budget:
            self.mass_limits_ok = False
        
        if self.mass > self.max_mass_budget:
            self.mass_limits_ok = False

    def get_missing_requirements(self):
        """Check class requirements and return list of missing items based on abilities."""
        missing = []
        class_def = VEHICLE_CLASSES.get(self.ship_class, {})
        requirements = class_def.get('requirements', {})
        
        # Gather all components
        all_components = [c for layer in self.layers.values() for c in layer['components']]
        
        # Calculate ability totals from all components
        ability_totals = self._calculate_ability_totals(all_components)
        
        # Check each requirement
        for req_name, req_def in requirements.items():
            ability_name = req_def.get('ability', '')
            min_value = req_def.get('min_value', 0)
            
            if not ability_name:
                continue
            
            current_value = ability_totals.get(ability_name, 0)
            
            # Handle boolean abilities
            if isinstance(min_value, bool):
                if min_value and not current_value:
                    nice_name = self._format_ability_name(ability_name)
                    missing.append(f"⚠ Needs {nice_name}")
            # Handle numeric abilities
            elif isinstance(min_value, (int, float)):
                if current_value < min_value:
                    nice_name = self._format_ability_name(ability_name)
                    if ability_name == 'CrewCapacity':
                        # Special handling for crew - show deficit
                        deficit = min_value - current_value
                        missing.append(f"⚠ Need {abs(current_value)} more crew housing")
                    else:
                        missing.append(f"⚠ Needs {nice_name}")
        
        # Additional crew/life support validation
        crew_capacity = ability_totals.get('CrewCapacity', 0)
        life_support = ability_totals.get('LifeSupportCapacity', 0)
        
        # Crew required is the absolute value of negative crew capacity
        crew_required = abs(min(0, crew_capacity))
        crew_housed = max(0, crew_capacity)
        
        # If we have crew requiring components but not enough life support
        if crew_required > 0 and life_support < crew_required:
            missing.append(f"⚠ Need {crew_required - life_support} more life support")
        
        return missing
    
    def _calculate_ability_totals(self, components):
        """Calculate total values for all abilities from components."""
        totals = {}
        
        # Abilities that should multiply instead of sum
        MULTIPLICATIVE_ABILITIES = {'ToHitAttackModifier', 'ToHitDefenseModifier'}
        
        for comp in components:
            abilities = getattr(comp, 'abilities', {})
            for ability_name, value in abilities.items():
                if isinstance(value, bool):
                    # Boolean abilities: any True makes total True
                    if value:
                        totals[ability_name] = True
                elif isinstance(value, (int, float)):
                    if ability_name in MULTIPLICATIVE_ABILITIES:
                        # Multiplicative abilities: multiply values together
                        totals[ability_name] = totals.get(ability_name, 1.0) * value
                    else:
                        # Additive abilities: sum values
                        totals[ability_name] = totals.get(ability_name, 0) + value
                # Object abilities (like VehicleLaunch) could be handled separately
        
        return totals
    
    def _format_ability_name(self, ability_name):
        """Convert ability ID to readable name."""
        # Insert spaces before capitals and title case
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', ability_name)
    
    def get_ability_total(self, ability_name):
        """Get total value of a specific ability across all components."""
        all_components = [c for layer in self.layers.values() for c in layer['components']]
        totals = self._calculate_ability_totals(all_components)
        return totals.get(ability_name, 0)

    def check_validity(self):
        self.recalculate_stats()
        # Check requirements too
        if self.get_missing_requirements():
            return False
        return self.mass_limits_ok

    @property
    def hp(self):
        return sum(c.current_hp for layer in self.layers.values() for c in layer['components'])

    @property
    def max_hp(self):
        return sum(c.max_hp for layer in self.layers.values() for c in layer['components'])

    @property
    def max_weapon_range(self):
        max_rng = 0
        for layer in self.layers.values():
            for comp in layer['components']:
                if isinstance(comp, Weapon) and comp.is_active:
                    if comp.range > max_rng:
                        max_rng = comp.range
        return max_rng

    def update(self, dt):
        if not self.is_alive: return

        # Regenerate Energy (scaled for tick-based physics)
        if self.current_energy < self.max_energy:
            self.current_energy += self.energy_gen_rate * dt / 60.0
            if self.current_energy > self.max_energy:
                self.current_energy = self.max_energy
        
        # Arcade Movement Logic
        # 1. Rotation and cooldowns are handled
        pass # Rotation is done in rotate() or super().update? Wait, PhysicsBody handles rotation integration.
        # PhysicsBody.update processes: angular_velocity.
        # But we want direct control over rotation? "turning rate".
        # PhysicsBody uses angular_velocity. We can keep that.
        
        # 2. Movement
        # Explicitly set velocity based on direction and speed
        forward = self.forward_vector()
        self.velocity = forward * self.current_speed
        self.position += self.velocity * dt
        
        # Apply Drag/Friction to Speed if NOT thrusting? -> Logic moved to thrust_forward/update
        # If we are NOT thrusting, should we slow down?
        # "Fuel should simply be consumed constantly by the engines"
        # Let's handle friction here if no thrust input (assumed by lack of speed increase).
        # Actually, we don't know "input" state here easily unless we track "is_thrusting".
        # Let's assume standard drag applies to current_speed every frame, and thrust counteracts it.
        # Simple damping (scaled for tick-based physics)
        self.current_speed *= (1 - self.drag * dt / 60.0)
        if self.current_speed < 0.1: self.current_speed = 0
        
        # Sync with PhysicsBody (just position mostly)
        # We are overriding PhysicsBody.update behavior which did accel/velocity integration.
        
        self.angle += self.angular_velocity * dt
        self.angle %= 360
        self.angular_velocity = 0 # Reset each frame for direct control style? 
        # If "turn_speed" is degrees/sec, we likely set angular_velocity in rotate().
        
        # Cooldowns
        for layer in self.layers.values():
            for comp in layer['components']:
                if hasattr(comp, 'update') and comp.is_active:
                    comp.update(dt)
        
        # Handle Firing
        self.just_fired_projectiles = []
        if getattr(self, 'comp_trigger_pulled', False):
             self.just_fired_projectiles = self.fire_weapons()

    def thrust_forward(self, dt):
        if self.current_fuel > 0:
            # Consume Fuel
            fuel_cost = 0
            # Speed increase
            thrust_added = 0
            
            for layer in self.layers.values():
                for comp in layer['components']:
                    if isinstance(comp, Engine) and comp.is_active:
                        # Scale for tick-based physics: fuel_cost_per_sec was tuned for 60 fps
                        fuel_cost += comp.fuel_cost_per_sec * dt / 60.0
            
            if self.current_fuel >= fuel_cost:
                self.current_fuel -= fuel_cost
                
                # Apply Acceleration
                # We add acceleration to speed, capped at max_speed
                # Note: Drag is applied in update(), so we need to add enough to overcome it to reach max.
                # If max_speed = accel / drag, then:
                # speed += accel * dt
                # speed *= (1 - drag * dt)
                # Equilibrium: speed = speed * (1-drag*dt) + accel*dt -> speed*drag*dt = accel*dt -> speed = accel/drag. Checks out.
                
                self.current_speed += self.acceleration_rate * dt
                # Hard cap just in case
                if self.current_speed > self.max_speed:
                    self.current_speed = self.max_speed
            else:
                self.current_fuel = 0

    def rotate(self, dt, direction):
        """Direction: -1 left, 1 right"""
        self.angle += direction * self.turn_speed * dt

    def take_damage(self, damage_amount):
        if not self.is_alive: return

        remaining_damage = damage_amount
        
        # Damage travels through layers
        layer_order = [LayerType.ARMOR, LayerType.OUTER, LayerType.INNER, LayerType.CORE]
        
        for ltype in layer_order:
            if remaining_damage <= 0: break
            remaining_damage = self._damage_layer(ltype, remaining_damage)

    def _damage_layer(self, layer_type, damage):
        """
        Applies damage to a random living component in the layer.
        Returns the remaining damage (0 if fully absorbed, >0 if overflow/pass-through).
        """
        layer = self.layers[layer_type]
        living_components = [c for c in layer['components'] if c.is_active]
        
        if not living_components:
            return damage # Pass through entire damage
            
        target = random.choice(living_components)
        
        # Apply damage
        # Damage absorbed is min(hp, damage)
        damage_absorbed = min(target.current_hp, damage)
        target.take_damage(damage) 
        
        if isinstance(target, Bridge) and not target.is_active:
            self.die()
            
        return damage - damage_absorbed

    def die(self):
        print(f"{self.name} EXPLODED!")
        self.is_alive = False
        self.velocity = pygame.math.Vector2(0,0)

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

    def fire_weapons(self):
        """
        Attempts to fire all ready weapons.
        Returns a list of dicts representing attacks (Projectiles or Beams).
        """
        attacks = []

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
                        # TARGETING
                        valid_target = False
                        aim_pos = None

                        if self.current_target:
                            target = self.current_target
                            dist = self.position.distance_to(target.position)
                            
                            if dist <= comp.range:
                                # Projectile Leading Logic
                                aim_pos = target.position # Default
                                
                                if isinstance(comp, ProjectileWeapon):
                                    # Quadratic Intercept
                                    s_proj = comp.projectile_speed
                                    # D = target.position - self.position # Original line, now target is self.current_target
                                    # V = target.velocity - self.velocity # Original line
                                    
                                    # a_q = V.dot(V) - s_proj**2 # Original line
                                    # b_q = 2 * V.dot(D) # Original line
                                    t = self.solve_lead(self.position, self.velocity, self.current_target.position, self.current_target.velocity, comp.projectile_speed)
                                    if t > 0:
                                        aim_pos = self.current_target.position + self.current_target.velocity * t
                                        self.aim_point = aim_pos
                                        
                                        # Correct for our own velocity (Relative Intecept)
                                        # aim_vec should be the direction we point the muzzle.
                                        # Since P_vel = Muzzle_Dir * Speed + Ship_Vel
                                        # We need to aim at (Intercept - Ship_Motion)
                                        intercept_vec = aim_pos - self.position
                                        aim_vec = intercept_vec - self.velocity * t
                                    else:
                                         # No solution, aim at target
                                         aim_pos = self.current_target.position
                                         aim_vec = aim_pos - self.position
                                else:
                                     # Beam
                                     self.aim_point = self.current_target.position
                                     aim_vec = self.aim_point - self.position

                                # ARC CHECK
                                # aim_vec is now the Muzzle Direction
                                aim_angle = math.degrees(math.atan2(aim_vec.y, aim_vec.x)) % 360
                                ship_angle = self.angle
                                comp_facing = (ship_angle + comp.facing_angle) % 360
                                diff = (aim_angle - comp_facing + 180) % 360 - 180
                                
                                if abs(diff) <= comp.firing_arc:
                                    valid_target = True
                                else:
                                    # ARC FAIL
                                    # Only log occasionally or if specific flag? 
                                    # For now, let's log.
                                    log_debug(f"ARC FAIL: {self.name} weapon {comp.name} | ShipAng: {ship_angle:.1f} | FacMod: {comp.facing_angle} | GlbFac: {comp_facing:.1f} | Aim: {aim_angle:.1f} | Diff: {diff:.1f} | Arc: {comp.firing_arc}")

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
                                    'hit': True # Revisit hit chance?
                                })
                            else:
                                self.current_ammo -= cost
                                # Projectile
                                speed = comp.projectile_speed if isinstance(comp, ProjectileWeapon) else 1000
                                # aim_vec is already calculated correctly above (compensated for ShipVel)
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
                                # LOG SHOT
                                aim_dir_str = f"({aim_vec.x:.1f}, {aim_vec.y:.1f})"
                                log_debug(f"SHOT: {self.name} fired {comp.name}. ShipAngle: {self.angle:.1f}, AimAngle: {aim_angle:.1f}, Diff: {diff:.1f}, Arc: {comp.firing_arc}")
        return attacks

    def to_dict(self):
        """Serialize ship to dictionary."""
        # Recalculate stats to ensure they're current
        self.recalculate_stats()
        
        data = {
            "name": self.name,
            "color": self.color,
            "team_id": self.team_id,
            "ship_class": self.ship_class,
            "ai_strategy": self.ai_strategy,
            "layers": {},
            # Save expected stats for verification when loading
            "expected_stats": {
                "max_hp": self.max_hp,
                "max_fuel": self.max_fuel,
                "max_ammo": self.max_ammo,
                "max_energy": self.max_energy,
                "max_speed": self.max_speed,
                "turn_speed": self.turn_speed,
                "total_thrust": self.total_thrust,
                "mass": self.mass,
                "armor_hp_pool": self.layers[LayerType.ARMOR]['max_hp_pool']
            }
        }
        
        for ltype, layer_data in self.layers.items():
            filter_comps = []
            for c in layer_data['components']:
                # Save component ID and Modifiers
                c_data = {
                    "id": c.id,
                    "modifiers": []
                }
                for m in c.modifiers:
                    c_data['modifiers'].append({
                        "id": m.definition.id,
                        "value": m.value
                    })
                filter_comps.append(c_data)
                
            data["layers"][ltype.name] = filter_comps
        return data

    @staticmethod
    def from_dict(data):
        """Create ship from dictionary."""
        name = data.get("name", "Unnamed")
        color = data.get("color", (200, 200, 200))
        # Ensure color is tuple
        if isinstance(color, list): color = tuple(color)
        
        s = Ship(name, 0, 0, color, data.get("team_id", 0), ship_class=data.get("ship_class", "Escort"))
        s.ai_strategy = data.get("ai_strategy", "optimal_firing_range")
        
        # Load Layers
        # We need access to COMPONENT_REGISTRY and MODIFIER_REGISTRY
        # They are in components.py. Cyclic import?
        # Ship imports components.py, so we can use components.COMPONENT_REGISTRY if exposed?
        # components.py doesn't show COMPONENT_REGISTRY in imports in ship.py
        # We need to import inside function to avoid circular dep if needed?
        
        from components import COMPONENT_REGISTRY, MODIFIER_REGISTRY, ApplicationModifier
        
        for l_name, comps_list in data.get("layers", {}).items():
            layer_type = None
            for l in LayerType:
                if l.name == l_name:
                    layer_type = l
                    break
            
            if not layer_type: continue
            
            for c_entry in comps_list:
                comp_id = ""
                modifiers_data = []
                
                if isinstance(c_entry, str):
                    comp_id = c_entry
                elif isinstance(c_entry, dict):
                    comp_id = c_entry.get("id")
                    modifiers_data = c_entry.get("modifiers", [])
                
                if comp_id in COMPONENT_REGISTRY:
                    new_comp = COMPONENT_REGISTRY[comp_id].clone()
                    
                    # Apply Modifiers
                    for m_dat in modifiers_data:
                        mid = m_dat['id']
                        mval = m_dat['value']
                        if mid in MODIFIER_REGISTRY:
                            # FIX: Pass ID and Value, not the object. add_modifier handles creation.
                            new_comp.add_modifier(mid, mval)
                            
                    if isinstance(new_comp, Weapon):
                        log_debug(f"LOADED Weapon {new_comp.name} on {name}: Facing={new_comp.facing_angle}, Arc={new_comp.firing_arc}")
                            
                    s.add_component(new_comp, layer_type)
        
        s.recalculate_stats()
        
        # Verify loaded stats match expected stats (if saved)
        expected = data.get('expected_stats', {})
        if expected:
            mismatches = []
            if expected.get('max_hp') and abs(s.max_hp - expected['max_hp']) > 1:
                mismatches.append(f"max_hp: got {s.max_hp}, expected {expected['max_hp']}")
            if expected.get('max_fuel') and abs(s.max_fuel - expected['max_fuel']) > 1:
                mismatches.append(f"max_fuel: got {s.max_fuel}, expected {expected['max_fuel']}")
            if expected.get('max_energy') and abs(s.max_energy - expected['max_energy']) > 1:
                mismatches.append(f"max_energy: got {s.max_energy}, expected {expected['max_energy']}")
            if expected.get('max_ammo') and abs(s.max_ammo - expected['max_ammo']) > 1:
                mismatches.append(f"max_ammo: got {s.max_ammo}, expected {expected['max_ammo']}")
            if expected.get('max_speed') and abs(s.max_speed - expected['max_speed']) > 0.1:
                mismatches.append(f"max_speed: got {s.max_speed:.1f}, expected {expected['max_speed']:.1f}")
            if expected.get('turn_speed') and abs(s.turn_speed - expected['turn_speed']) > 0.1:
                mismatches.append(f"turn_speed: got {s.turn_speed:.1f}, expected {expected['turn_speed']:.1f}")
            if expected.get('total_thrust') and abs(s.total_thrust - expected['total_thrust']) > 1:
                mismatches.append(f"total_thrust: got {s.total_thrust}, expected {expected['total_thrust']}")
            if expected.get('mass') and abs(s.mass - expected['mass']) > 1:
                mismatches.append(f"mass: got {s.mass}, expected {expected['mass']}")
            armor_hp = s.layers[LayerType.ARMOR]['max_hp_pool']  
            if expected.get('armor_hp_pool') and abs(armor_hp - expected['armor_hp_pool']) > 1:
                mismatches.append(f"armor_hp_pool: got {armor_hp}, expected {expected['armor_hp_pool']}")
            
            if mismatches:
                print(f"WARNING: Ship '{s.name}' stats mismatch after loading!")
                for m in mismatches:
                    print(f"  - {m}")
        
        return s



