import pygame
from game.engine.physics import PhysicsBody
from game.core.logger import log_debug, log_event
from game.core.constants import AttackType

class Projectile(PhysicsBody):
    def __init__(self, owner, position, velocity, damage, range_val, endurance, proj_type, source_weapon=None, **kwargs):
        super().__init__(position.x, position.y)
        self.velocity = velocity
        self.owner = owner
        self.team_id = getattr(owner, 'team_id', -1)
        self.damage = damage
        self.max_range = range_val
        self.endurance = endurance # in seconds
        self.max_endurance = endurance  # Store initial value for UI
        
        # Ensure type is AttackType
        if isinstance(proj_type, str):
            try:
                self.type = AttackType(proj_type)
            except ValueError:
                # Fallback if unknown string, though ideally we strictly define valid types
                # Assuming 'missile' and 'projectile' match AttackType values
                self.type = proj_type 
        else:
            self.type = proj_type
        
        # 'projectile', 'missile', 'beam' (beams usually separate but maybe unified later)
        
        # Optional args
        self.turn_rate = kwargs.get('turn_rate', 0)
        self.max_speed = kwargs.get('max_speed', 0)
        self.target = kwargs.get('target', None)
        self.hp = kwargs.get('hp', 1) # Missiles can be shot down
        self.max_hp = self.hp  # Store initial value for UI
        self.radius = kwargs.get('radius', 3)
        self.color = kwargs.get('color', (255, 255, 0))
        self.source_weapon = source_weapon
        
        # Turn direction commitment for stable guidance (prevents oscillation)
        self.last_turn_direction = 0  # -1 for clockwise, +1 for counter-clockwise
        
        self.distance_traveled = 0
        self.is_alive = True
        
        # Flag for targeting systems
        self.is_derelict = False # Projectiles aren't ships, but this helps unified filtering
        
        # Status for UI tracking
        self.status = 'active' # active, hit, miss, destroyed
        
    def update(self):
        if not self.is_alive: return

        # Fixed tick duration (1 tick = 0.01s)
        dt = 0.01

        # Endurance check
        if self.endurance is not None:
             self.endurance -= dt
             if self.endurance <= 0:
                 self.is_alive = False
                 self.status = 'miss'
                 # Log Expiration (Seeker or Timed Projectile)
                 if self.type == AttackType.MISSILE or self.type == 'missile':
                     log_event("SEEKER_EXPIRE", 
                               seeker_id=str(id(self)), 
                               reason="lifetime",
                               tick=0)
                 return

        # Guidance Logic (if missile)
        if (self.type == AttackType.MISSILE or self.type == 'missile') and self.target and self.target.is_alive:
            self._update_guidance(dt)
            
        # Physics Update (from PhysicsBody)
        self.position += self.velocity
        
        self.distance_traveled += self.velocity.length()
        if self.max_range and self.distance_traveled > self.max_range:
            self.is_alive = False
            self.status = 'miss'
            # Log Range Expiration
            if self.type == AttackType.MISSILE or self.type == 'missile':
                log_event("SEEKER_EXPIRE", 
                          seeker_id=str(id(self)), 
                          reason="max_range",
                          tick=0)

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
                
                # Normalize angle to [-180, 180] to ensure shortest turn path
                # Pygame's angle_to can return values like 225 instead of -135
                if angle_diff > 180:
                    angle_diff -= 360
                elif angle_diff < -180:
                    angle_diff += 360
                    
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
                
                # Commit to turn direction near ±180° to prevent oscillation
                # When target is behind us, angle_to can flip between +179 and -180
                # causing flip-flop turning. Lock to previous direction instead.
                # Commit to turn direction when target is generally behind (>135 degrees offset)
                # This prevents flip-flopping efficiently for rear-aspect launches.
                if abs(abs(angle_diff) - 180) < 45:  # Within 45° of 180 (i.e. > 135°)
                    if self.last_turn_direction != 0:
                        rotation = abs(rotation) * self.last_turn_direction
                
                # Store turn direction for next frame
                if rotation != 0:
                    self.last_turn_direction = 1 if rotation > 0 else -1
                
                new_vel = current_dir.rotate(rotation) * self.max_speed
                self.velocity = new_vel

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.is_alive = False
            self.status = 'destroyed'
            log_debug(f"Projectile {self} destroyed by point defense!")
