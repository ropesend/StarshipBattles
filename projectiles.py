import pygame
from physics import PhysicsBody
from logger import log_debug

class Projectile(PhysicsBody):
    def __init__(self, owner, position, velocity, damage, range_val, endurance, proj_type, source_weapon=None, **kwargs):
        super().__init__(position.x, position.y)
        self.velocity = velocity
        self.owner = owner
        self.team_id = getattr(owner, 'team_id', -1)
        self.damage = damage
        self.max_range = range_val
        self.endurance = endurance # in seconds
        self.type = proj_type # 'projectile', 'missile', 'beam' (beams usually separate but maybe unified later)
        
        # Optional args
        self.turn_rate = kwargs.get('turn_rate', 0)
        self.max_speed = kwargs.get('max_speed', 0)
        self.target = kwargs.get('target', None)
        self.hp = kwargs.get('hp', 1) # Missiles can be shot down
        self.radius = kwargs.get('radius', 3)
        self.radius = kwargs.get('radius', 3)
        self.color = kwargs.get('color', (255, 255, 0))
        self.source_weapon = source_weapon
        
        self.distance_traveled = 0
        self.is_alive = True
        
        # Flag for targeting systems
        self.is_derelict = False # Projectiles aren't ships, but this helps unified filtering
        
        # Status for UI tracking
        self.status = 'active' # active, hit, miss, destroyed
        
    def update(self, dt=0.01):
        if not self.is_alive: return

        # Endurance check
        if self.endurance is not None:
             self.endurance -= dt
             if self.endurance <= 0:
                 self.is_alive = False
                 self.status = 'miss'
                 return

        # Guidance Logic (if missile)
        if self.type == 'missile' and self.target and self.target.is_alive:
            self._update_guidance(dt)
            
        # Physics Update (from PhysicsBody)
        # PhysicsBody.update adds accel, drag, and moves position.
        # But Projectile logic in BattleScene was:
        # pos += vel
        # distance += vel.length
        # We want to use PhysicsBody but we need to track distance for range limit.
        
        # Override standard update slightly or hook into it
        # PhysicsBody.update defaults to dt=1.0 logic (1 tick). 
        # But we passed 0.01. Let's rely on velocity.
        
        # For simple projectiles, no drag usually?
        # self.drag = 0 
        
        self.position += self.velocity
        
        self.distance_traveled += self.velocity.length()
        if self.max_range and self.distance_traveled > self.max_range:
            self.is_alive = False
            self.status = 'miss'

    def _update_guidance(self, dt):
        target = self.target
        p_pos = self.position
        p_vel = self.velocity
        
        # Calculate lead
        # Assume owner has solve_lead or we implement a static one?
        # Owner might be dead, so careful.
        # We can implement a simplified intercept here.
        
        # Simple intercept logic:
        # We want to hit target.
        rel_pos = target.position - p_pos
        dist = rel_pos.length()
        
        if dist > 0:
            # Desired velocity vector
            # Predict target position?
            # t = dist / self.max_speed
            # predicted_pos = target.position + target.velocity * t
            
            # Use strict pursuit for now or a simple lead if possible
            # Replicating existing logic from battle.py:
            # t = owner.solve_lead(...)
            
            # Let's try to use the owner's solver if available, else direct
            t = 0
            if hasattr(self.owner, 'solve_lead'):
                 t = self.owner.solve_lead(p_pos, pygame.math.Vector2(0,0), target.position, target.velocity, self.max_speed)
            
            aim_pos = target.position
            if t > 0:
                aim_pos = target.position + target.velocity * t
                
            desired_vec = aim_pos - p_pos
            if desired_vec.length_squared() > 0:
                desired_dir = desired_vec.normalize()
                current_dir = p_vel.normalize() if p_vel.length() > 0 else pygame.math.Vector2(1, 0)
                
                angle_diff = current_dir.angle_to(desired_dir)
                max_turn = self.turn_rate * dt * 100 # turn_rate is deg/sec? wait. 
                # In components.json: "turn_rate": 90 (deg/sec assumed?)
                # In battle.py: max_turn = p['turn_rate'] / 100.0 (Degrees per tick)
                # If dt=0.01 (1 tick), then max_turn should be turn_rate * dt
                # Yes.
                
                max_turn_step = self.turn_rate * 0.01 # Fixed 1 tick
                
                if abs(angle_diff) > max_turn_step:
                    rotation = max_turn_step if angle_diff > 0 else -max_turn_step
                else:
                    rotation = angle_diff
                
                new_vel = current_dir.rotate(rotation) * self.max_speed
                self.velocity = new_vel

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.is_alive = False
            self.status = 'destroyed'
            log_debug(f"Projectile {self} destroyed by point defense!")
