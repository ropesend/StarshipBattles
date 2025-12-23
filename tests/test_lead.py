import math

class MockVector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __sub__(self, other):
        return MockVector(self.x - other.x, self.y - other.y)
    def do(self, other): # Dot product
        return self.x * other.x + self.y * other.y
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    def __repr__(self):
        return f"({self.x}, {self.y})"

def solve_lead(shooter_pos, shooter_vel, target_pos, target_vel, projectile_speed):
    # Quadratic Intercept
    D = target_pos - shooter_pos
    V = target_vel - shooter_vel
    
    a_q = V.dot(V) - projectile_speed**2
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
            
    return t

# Test
p1 = MockVector(0,0)
v1 = MockVector(0,0)
p2 = MockVector(100,0)
v2 = MockVector(0,0)
s = 100
t = solve_lead(p1, v1, p2, v2, s)
print(f"Static Target: {t} (Expected 1.0)")

v2 = MockVector(0, 100)
t = solve_lead(p1, v1, p2, v2, s)
print(f"Moving Target 90deg: {t}")
