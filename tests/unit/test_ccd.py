import math

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    def length_sq(self):
        return self.x**2 + self.y**2
    def length(self):
        return math.sqrt(self.length_sq())
    def __repr__(self):
        return f"({self.x:.1f}, {self.y:.1f})"

def check_collision(p_pos, p_vel, s_pos, s_vel, radius, dt):
    # Relative Motion
    D = p_pos - s_pos
    V = p_vel - s_vel
    
    # t_cpa = -(D . V) / (V . V)
    v_sq = V.length_sq()
    if v_sq == 0:
        # Parallel/Static relative motion
        dist = D.length()
        return dist <= radius, 0
        
    t = -(D.dot(V)) / v_sq
    
    # Clamp t to segment [0, dt]
    t_clamped = max(0, min(t, dt))
    
    # Position at t
    p_at_t = p_pos + p_vel * t_clamped
    s_at_t = s_pos + s_vel * t_clamped
    
    dist_sq = (p_at_t - s_at_t).length_sq()
    
    hit = dist_sq <= (radius**2)
    return hit, t_clamped

# Test Case: Tunneling
# Ship at (100, 0), Radius 40.
# Projectile starts at (0, 0), moving (20000, 0).
# dt = 0.016 (60 FPS) -> moves 320 units per frame.
# Should pass through ship in one frame.

s_pos = Vector(100, 0)
s_vel = Vector(0, 0)
s_rad = 40

p_pos = Vector(0, 0)
p_vel = Vector(20000, 0)
dt = 0.016

hit, t = check_collision(p_pos, p_vel, s_pos, s_vel, s_rad, dt)
print(f"Tunneling Test: Hit={hit}, Time={t:.5f}")

# Test Case: Miss (High speed but off target)
p_pos_miss = Vector(0, 100) # y=100 is > radius 40
hit_miss, t_miss = check_collision(p_pos_miss, p_vel, s_pos, s_vel, s_rad, dt)
print(f"Miss Test: Hit={hit_miss}, Time={t_miss:.5f}")
