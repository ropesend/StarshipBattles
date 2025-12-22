
import pygame
import unittest
from projectiles import Projectile
from ship import Ship

class MockOwner:
    def __init__(self):
        self.team_id = 0
    def solve_lead(self, p1, v1, p2, v2, s):
        return 0 # Direct pursuit for simplicity

class MockTarget:
    def __init__(self, pos):
        self.position = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(0, 0)
        self.is_alive = True

def test_rear_aspect():
    pygame.init()
    owner = MockOwner()
    # Missile pointing UP (0, -1)
    # Target is DOWN (0, 100) -> 180 degrees behind
    # Missile slightly off-axis (150 degrees from Target)
    # Target (0, 1) [Down]
    # Velocity (100, -200) [Up-Right] approx 150 deg?
    # Let's be precise.
    # Target is DOWN (0, 1). 
    # Velocity UP is (0, -1). 180 deg.
    # We want 170 deg. Rotate UP by 10 deg.
    # Up turned 10 deg right = (sin(10), -cos(10))
    # sin(10) ~= 0.17.
    vel = pygame.math.Vector2(0, -100).rotate(10)
    p_pos = pygame.math.Vector2(0, 0)
    p_vel = vel # (17, -98)
    target = MockTarget((0, 200)) # Target is DOWN
    
    # High turn rate to exacerbate overshoots
    proj = Projectile(owner, p_pos, p_vel, 10, 1000, 10, 'missile', 
                      turn_rate=180, max_speed=100, target=target)
    
    print("Step | AngleToTarget | Rotation | LastDir | Velocity")
    for i in range(100):
        # Calculate angle manually to log
        rel = target.position - proj.position
        vel_angle = proj.velocity.angle_to(pygame.math.Vector2(1, 0)) # Ref
        # That's simpler:
        
        # We want internal state.
        # But we can't inspect internal vars easily without modifying Projectile or using debugger.
        # We will iterate and print public state.
        
        old_vel = proj.velocity
        proj.update() # dt=0.01 implicit
        
        # Calculate resulting angle change
        angle_change = old_vel.angle_to(proj.velocity)
        
        # Angle to target
        to_target = target.position - proj.position
        angle_to_target = proj.velocity.angle_to(to_target)
        
        print(f"{i:3d} | {angle_to_target:6.2f} | {angle_change:6.2f} | {proj.last_turn_direction:2d} | {proj.velocity}")
        
        if proj.distance_traveled > 500: break

test_rear_aspect()
