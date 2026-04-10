"""
Tests for SpiralArmPrimitive density field.
"""

import pytest
import math
from game.strategy.generation.density.primitives.spiral_arm import SpiralArmPrimitive


class TestSpiralArmPrimitive:
    """Tests for SpiralArmPrimitive."""

    def test_center_has_high_density(self, spiral_arm_primitive):
        """Center should have high density (all arms converge)."""
        center = spiral_arm_primitive.evaluate(0, 0)
        assert center > 0.5

    def test_arms_have_higher_density_than_gaps(self, spiral_arm_primitive):
        """Points on arms should have higher density than gaps."""
        # This is tricky to test precisely, but we can sample and check variance
        densities = []
        for r in [100, 200, 300]:
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                q = int(r * math.cos(rad))
                r_coord = int(r * math.sin(rad))
                densities.append(spiral_arm_primitive.evaluate(q, r_coord))

        # With arms, we should see significant variance
        min_d = min(densities)
        max_d = max(densities)
        assert max_d - min_d > 0.3, "Should have contrast between arms and gaps"

    def test_output_always_in_valid_range(self, spiral_arm_primitive):
        """Output should always be in [0, 1]."""
        test_coords = [
            (0, 0), (100, 0), (-100, 0), (0, 100), (0, -100),
            (300, 200), (-300, -200), (500, 500)
        ]
        for q, r in test_coords:
            density = spiral_arm_primitive.evaluate(q, r)
            assert 0.0 <= density <= 1.0, f"Invalid density {density} at ({q}, {r})"

    def test_arm_count_affects_pattern(self):
        """Different arm counts should produce different patterns."""
        prim2 = SpiralArmPrimitive(arm_count=2, pitch_angle=20, arm_width=50, peak_density=1.0)
        prim4 = SpiralArmPrimitive(arm_count=4, pitch_angle=20, arm_width=50, peak_density=1.0)

        # Sample at various angles at fixed radius
        samples_2 = []
        samples_4 = []
        for angle in range(0, 360, 15):
            rad = math.radians(angle)
            q = int(200 * math.cos(rad))
            r = int(200 * math.sin(rad))
            samples_2.append(prim2.evaluate(q, r))
            samples_4.append(prim4.evaluate(q, r))

        # Count peaks (high density regions)
        threshold = 0.5
        peaks_2 = sum(1 for d in samples_2 if d > threshold)
        peaks_4 = sum(1 for d in samples_4 if d > threshold)

        # 4-arm should have more peaks than 2-arm
        assert peaks_4 > peaks_2

    def test_rotation_shifts_pattern(self):
        """Rotation parameter should shift the spiral pattern."""
        prim1 = SpiralArmPrimitive(rotation=0, arm_count=2, pitch_angle=20, arm_width=50)
        prim2 = SpiralArmPrimitive(rotation=math.pi/2, arm_count=2, pitch_angle=20, arm_width=50)

        # Sample at a fixed point - should differ due to rotation
        d1 = prim1.evaluate(200, 0)
        d2 = prim2.evaluate(200, 0)

        # The patterns should be different
        # (exact difference depends on spiral math)
        assert d1 != d2
