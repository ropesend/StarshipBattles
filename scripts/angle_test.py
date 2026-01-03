
import pygame
import math

v_up = pygame.math.Vector2(0, -1)
v_down = pygame.math.Vector2(0, 1)
v_right = pygame.math.Vector2(1, 0)
v_left = pygame.math.Vector2(-1, 0)

print(f"Up to Right: {v_up.angle_to(v_right)}") # Expected +90 or -90
print(f"Right to Down: {v_right.angle_to(v_down)}")
print(f"Right to Up: {v_right.angle_to(v_up)}") # Expected -90 or 270
print(f"Up to Down: {v_up.angle_to(v_down)}")

# Up-Right
v_ur = pygame.math.Vector2(1, -1).normalize()
print(f"Up-Right to Down: {v_ur.angle_to(v_down)}")

# Up-Left
v_ul = pygame.math.Vector2(-1, -1).normalize()
print(f"Up-Left to Down: {v_ul.angle_to(v_down)}")
