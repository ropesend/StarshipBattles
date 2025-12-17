import math
import pygame
from components import LayerType

class AIController:
    def __init__(self, ship, enemy_ship):
        self.ship = ship
        self.enemy = enemy_ship

    def update(self, dt):
        if not self.ship.is_alive or not self.enemy.is_alive:
            # Just drift if fight over
            return

        if self.ship.current_fuel <= 0:
            # Drift behavior (do nothing, physics continues)
            return

        distance = self.ship.position.distance_to(self.enemy.position)
        
        # 1. Navigation
        # Calculate angle to enemy
        dx = self.enemy.position.x - self.ship.position.x
        dy = self.enemy.position.y - self.ship.position.y
        
        target_angle = math.degrees(math.atan2(dy, dx)) % 360
        current_angle = self.ship.angle % 360
        
        # Calculate difference (-180 to 180)
        angle_diff = (target_angle - current_angle + 180) % 360 - 180
        
        # Rotate
        if abs(angle_diff) > 5:
            # Determine direction
            direction = 1 if angle_diff > 0 else -1
            self.ship.rotate(dt, direction)
        
        # Thrust
        # If angle < 5 degrees and distance > 300px, fire Engines.
        if abs(angle_diff) < 20 and distance > 300: # 20 degree cone for thrusting feels better, but prompt said 5?
            # Prompt: "If angle < 5 degrees and distance > 300px, fire Engines."
            # Sticking to prompt strictly for logic.
            if abs(angle_diff) < 5:
                self.ship.thrust_forward(dt)

        # 2. Combat
        # "If distance < Railgun Range and generic "in sights", fire Railguns."
        # Generic in sights can be angle < 10 degrees?
        in_sights = abs(angle_diff) < 10
        
        if in_sights:
            self.ship.comp_trigger_pulled = True
        else:
            self.ship.comp_trigger_pulled = False

    # attempt_fire removed, logic moved to Ship update via trigger

