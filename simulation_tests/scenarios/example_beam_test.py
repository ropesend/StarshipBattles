"""
Example Beam Test Scenario

This is a simple example demonstrating the TestScenario pattern.
This scenario validates that a beam weapon can hit a stationary target at close range.

This file serves as:
1. A working example of the TestScenario pattern
2. Verification that the infrastructure works
3. A template for creating new test scenarios
"""

import pygame
from simulation_tests.scenarios import TestScenario, TestMetadata


class ExampleBeamPointBlankTest(TestScenario):
    """
    Example test: Beam weapon at point-blank range.

    This test validates the most basic beam weapon behavior - hitting a
    stationary target at very close range.
    """

    metadata = TestMetadata(
        test_id="EXAMPLE-001",
        category="Examples",
        subcategory="Beam Weapons",
        name="Example beam point-blank test",
        summary="Demonstrates TestScenario pattern with a simple beam weapon test",
        conditions=[
            "Distance: 50px (point-blank)",
            "Stationary target",
            "Low accuracy beam (base_accuracy: 0.5)"
        ],
        edge_cases=["Minimum engagement range"],
        expected_outcome="Beam should hit and deal damage at close range",
        pass_criteria="Damage dealt > 0",
        max_ticks=500,
        seed=42,
        ui_priority=1,
        tags=["example", "beam", "point_blank"]
    )

    def setup(self, battle_engine):
        """
        Configure the test scenario.

        Loads two ships (attacker with beam, stationary target) and positions
        them 50 pixels apart.
        """
        # Load test ships using helper method
        attacker = self._load_ship('Test_Attacker_Beam360_Low.json')
        target = self._load_ship('Test_Target_Stationary.json')

        # Position ships at point-blank range
        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0  # Facing right (+x direction)

        target.position = pygame.math.Vector2(50, 0)  # 50px to the right
        target.angle = 0

        # Store initial HP for damage calculation
        self.initial_target_hp = target.hp

        # Start battle with fixed seed for reproducibility
        battle_engine.start([attacker], [target], seed=self.metadata.seed)

        # Set attacker's target
        attacker.current_target = target

        # Store references for use in update() and verify()
        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """
        Called every tick during simulation.

        Forces the attacker to fire weapons every tick. This is needed because
        test ships may not have AI controllers.
        """
        # Force weapon firing
        self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine):
        """
        Check if the test passed.

        Returns True if the beam weapon dealt any damage to the target.
        """
        # Calculate damage dealt
        damage_dealt = self.initial_target_hp - self.target.hp

        # Store detailed results for reporting
        self.results['damage_dealt'] = damage_dealt
        self.results['initial_hp'] = self.initial_target_hp
        self.results['final_hp'] = self.target.hp
        self.results['target_alive'] = self.target.is_alive
        self.results['ticks_run'] = battle_engine.tick_counter

        # Test passes if any damage was dealt
        passed = damage_dealt > 0

        return passed
