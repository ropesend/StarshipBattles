import pygame
import random
import math
import json
from physics import PhysicsBody
from components import Component, LayerType, Bridge, Engine, Thruster, Tank, Armor, Weapon, Generator, BeamWeapon, ProjectileWeapon
from logger import log_debug


# Ship Classes and their Mass Limits
SHIP_CLASSES = {
    "Escort": 1000,
    "Frigate": 2000,
    "Destroyer": 4000,
    "Cruiser": 8000,
    "Battlecruiser": 16000,
    "Battleship": 32000,
    "Dreadnought": 64000
}

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
        self.base_mass = 50 # Cockpit/Structure
        self.total_thrust = 0
        self.max_speed = 0
        self.turn_speed = 0
        self.drag = 0.5 # New Arcade Drag
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
        
        # Radius Scaling
        base_radius = 40
        ref_mass = 1000
        budget = max(self.max_mass_budget, 1000)
        ratio = budget / ref_mass
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
        # Turn proportional to 1/Mass^2
        
        # Tuning Constants to make it feel right
        K_THRUST = 50000 
        K_TURN = 500000 
        
        if self.mass > 0:
            self.acceleration_rate = (self.total_thrust * K_THRUST) / (self.mass * self.mass)
            self.turn_speed = (self.turn_speed * K_TURN) / (self.mass * self.mass)
            
            # Max Speed = Thrust / Mass logic (Linear)
            # Or maintain drag model?
            # User said "top speed proportional to 1/ mass".
            # With Accel ~ 1/m^2 and Drag constant, Max Speed would be 1/m^2. 
            # So we must adjust Drag or Max Speed calculation explicitly.
            
            # Let's enforce Max Speed explicitly
            K_SPEED = 200000
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
            
        # Ensure minimums
        if self.max_speed < 10: self.max_speed = 10
            
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

    def check_validity(self):
        self.recalculate_stats()
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

        # Regenerate Energy
        if self.current_energy < self.max_energy:
            self.current_energy += self.energy_gen_rate * dt
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
        # Simple damping:
        self.current_speed *= (1 - self.drag * dt)
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
                        fuel_cost += comp.fuel_cost_per_sec * dt
            
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
                                    D = target.position - self.position
                                    V = target.velocity - self.velocity
                                    
                                    a_q = V.dot(V) - s_proj**2
                                    b_q = 2 * V.dot(D)
                                    c_q = D.dot(D)
                                    
                                    t = 0
                                    if a_q == 0:
                                        if b_q != 0: t = -c_q/b_q
                                    else:
                                        disc = b_q*b_q - 4*a_q*c_q
                                        if disc >= 0:
                                            t1 = (-b_q + math.sqrt(disc)) / (2*a_q)
                                            t2 = (-b_q - math.sqrt(disc)) / (2*a_q)
                                            ts = [x for x in [t1, t2] if x > 0]
                                            if ts: t = min(ts)
                                    
                                    if t > 0:
                                        aim_pos = target.position + target.velocity * t
                                        self.aim_point = aim_pos
                                else:
                                     # Beam
                                     self.aim_point = target.position

                                # ARC CHECK
                                aim_vec = aim_pos - self.position
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
                                    pass
                                    # log_debug(f"{self.name} weapon {comp.name} out of arc: {diff:.1f} vs {comp.firing_arc}")

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
                                    'direction': aim_vec.normalize() if aim_vec.length() > 0 else pygame.math.Vector2(1, 0),
                                    'hit': True # Revisit hit chance?
                                })
                            else:
                                self.current_ammo -= cost
                                # Projectile
                                speed = comp.projectile_speed if isinstance(comp, ProjectileWeapon) else 1000
                                aim_vec = aim_pos - self.position
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
        data = {
            "name": self.name,
            "color": self.color,
            "team_id": self.team_id,
            "ship_class": self.ship_class,
            "layers": {}
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
                            
                    s.add_component(new_comp, layer_type)
        
        s.recalculate_stats()
        return s



