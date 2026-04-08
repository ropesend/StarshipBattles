"""
Test Movement Controllers for Combat Lab Scenarios.

These controllers issue thrust_forward() and rotate() commands directly,
bypassing the AI controller but using the real physics engine. All movement
obeys the ship's physical properties (thrust, mass, turn speed).

The combat engine uses arcade physics: velocity immediately follows heading
on turns with no speed loss. This means constant thrust + constant rotation
produces a circular path.

Usage in scenarios:
    from combat_lab.scenarios.movement import StraightLineController

    class MyScenario(StaticTargetScenario):
        target_movement = StraightLineController()
"""

import math
import random


class StraightLineController:
    """
    Thrust every tick, no rotation.

    Ship accelerates from rest to max_speed along its initial heading
    and holds that speed. The direction of travel is determined by the
    ship's angle at the start of the simulation.
    """

    def update(self, ship):
        ship.thrust_forward()


class CircularOrbitController:
    """
    Thrust + constant rotation every tick.

    With arcade physics (velocity follows heading), this produces a
    circular path once the ship reaches max_speed. The orbit radius
    depends on the ship's speed and turn rate.

    Args:
        direction: 1 for clockwise, -1 for counter-clockwise.
    """

    def __init__(self, direction=1):
        self.direction = direction

    def update(self, ship):
        ship.thrust_forward()
        ship.rotate(self.direction)


class ErraticController:
    """
    Thrust + random rotation changes at intervals, with a leash.

    The ship thrusts every tick and changes rotation direction at random
    intervals. If the ship drifts beyond max_radius from center, it
    steers back toward center instead of following the random pattern.

    Uses a seeded RNG for deterministic, reproducible movement.

    Args:
        center: Center point to orbit around (pygame.math.Vector2).
        max_radius: Maximum distance from center before leash activates.
        min_interval: Minimum ticks between direction changes.
        max_interval: Maximum ticks between direction changes.
        seed: Random seed for reproducibility.
    """

    def __init__(self, center, max_radius=500, min_interval=50, max_interval=200, seed=42):
        self.center = center
        self.max_radius = max_radius
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.rng = random.Random(seed)
        self.current_direction = 0  # -1, 0, or 1
        self.next_change_tick = 0
        self.tick = 0

    def update(self, ship):
        ship.thrust_forward()
        self.tick += 1

        # Leash: if too far from center, steer back
        offset = ship.position - self.center
        dist = offset.length()

        if dist > self.max_radius:
            # Calculate angle from ship heading to center
            to_center = self.center - ship.position
            target_angle = math.degrees(math.atan2(to_center.y, to_center.x)) % 360
            ship_angle = ship.angle % 360
            diff = (target_angle - ship_angle + 180) % 360 - 180

            if abs(diff) > 2.0:  # Dead band to prevent jitter
                ship.rotate(1 if diff > 0 else -1)
            return

        # Random direction changes at intervals
        if self.tick >= self.next_change_tick:
            self.current_direction = self.rng.choice([-1, 0, 1])
            interval = self.rng.randint(self.min_interval, self.max_interval)
            self.next_change_tick = self.tick + interval

        if self.current_direction != 0:
            ship.rotate(self.current_direction)
