import pygame
import random
import math
from physics import PhysicsBody
from components import Component, LayerType, Bridge, Engine, Thruster, Tank, Armor, Weapon, Generator, BeamWeapon

class Ship(PhysicsBody):
    def __init__(self, name, x, y, color, team_id=0):
        super().__init__(x, y)
        self.name = name
        self.color = color
        self.team_id = team_id
        self.current_target = None
        
        # Layers
        self.layers = {
            LayerType.CORE:  {'components': [], 'radius_pct': 0.2, 'hp_pool': 0, 'max_hp_pool': 0},
            LayerType.INNER: {'components': [], 'radius_pct': 0.5, 'hp_pool': 0, 'max_hp_pool': 0},
            LayerType.OUTER: {'components': [], 'radius_pct': 0.8, 'hp_pool': 0, 'max_hp_pool': 0},
            LayerType.ARMOR: {'components': [], 'radius_pct': 1.0, 'hp_pool': 0, 'max_hp_pool': 0}
        }
        
        self.max_mass_budget = 1000
        self.current_mass = 0
        
        # Resources
        self.max_fuel = 0
        self.current_fuel = 0
        self.max_ammo = 0
        self.current_ammo = 0
        self.max_energy = 0
        self.current_energy = 0
        self.energy_gen_rate = 0
        
        # Stats
        self.total_thrust = 0
        self.turn_speed = 0
        self.is_alive = True
        self.bridge_destroyed = False
        
        # Arcade Physics
        self.current_speed = 0
        self.acceleration_rate = 0
        self.max_speed = 0
        
        # Collision
        self.radius = 40

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
        self.mass = self.current_mass if self.current_mass > 0 else 1 # Avoid div by 0
        self.total_thrust = 0
        self.turn_speed = 0
        self.max_fuel = 0
        self.max_ammo = 0
        self.max_energy = 0
        self.energy_gen_rate = 0
        
        self.drag = 0.5 # Default drag/friction
        self.layers[LayerType.ARMOR]['max_hp_pool'] = 0
        
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
            
        # Arcade Physics Calculations
        # a = F/m
        self.acceleration_rate = self.total_thrust / self.mass
        # Max speed calculation:
        # In Newtonian with Drag: v_term = a / drag. 
        # We'll use this as our "Max Speed" cap for arcade feel.
        # If drag is 0, we cap at something reasonable or 1000.
        if self.drag > 0:
            self.max_speed = self.acceleration_rate / self.drag
        else:
            self.max_speed = 1000

        if self.drag > 0:
            self.max_speed = self.acceleration_rate / self.drag
        else:
            self.max_speed = 1000

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
                        if comp.fire():
                            # Deduct Resource
                            if isinstance(comp, BeamWeapon):
                                self.current_energy -= cost
                                # Beam Event
                                attacks.append({
                                    'type': 'beam',
                                    'owner': self,
                                    'target': self.current_target,
                                    'damage': comp.damage,
                                    'range': comp.range,
                                    'origin': pygame.math.Vector2(self.position),
                                    'direction': self.forward_vector(),
                                    'component': comp
                                })
                            else:
                                self.current_ammo -= cost
                                # Projectile Event
                                muzzle_speed = 500
                                forward = self.forward_vector()
                                vel = self.velocity + forward * muzzle_speed
                                attacks.append({
                                    'type': 'projectile',
                                    'pos': pygame.math.Vector2(self.position),
                                    'vel': vel,
                                    'damage': comp.damage,
                                    'range': comp.range,
                                    'distance_traveled': 0,
                                    'owner': self,
                                    'target': self.current_target
                                })
        return attacks

    def to_dict(self):
        """Serialize ship to dictionary."""
        data = {
            "name": self.name,
            "color": self.color,
            "team_id": self.team_id,
            "layers": {}
        }
        
        for ltype, layer_data in self.layers.items():
            comp_ids = [c.id for c in layer_data['components']]
            data["layers"][ltype.name] = comp_ids
            
        return data

    @staticmethod
    def from_dict(data):
        """Create new Ship instance from dictionary."""
        # Using a dummy position, caller should update it
        ship = Ship(data["name"], 0, 0, tuple(data["color"]), data.get("team_id", 0))
        
        from components import create_component, LayerType
        
        # We need to import LayerType here or ensure it's available. It is imported at top.
        
        for layer_name, comp_ids in data["layers"].items():
            ltype = LayerType[layer_name]
            for cid in comp_ids:
                comp = create_component(cid)
                if comp:
                    ship.add_component(comp, ltype)
                    
        return ship

