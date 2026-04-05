"""
Thrust Multiplier Modifier Test Scenarios (MOD-THRUST-001 through MOD-THRUST-005)

Dedicated test scenarios for the thrust_mult modifier applied via test_thrust_boost.
These validate that the modifier correctly scales engine thrust and that all derived
physics stats (max_speed, acceleration_rate) respond correctly.

Ship Files:
- Test_Engine_ThrustBoost.json — hull_test_s(mass=400) + test_engine_no_fuel(thrust=500)
  + test_thrust_boost(param=2), thrust 500->1000
- Test_Engine_1x_MedMass.json — hull_test_m(mass=1000) + 2x mass_sim_1k(mass=1000 each)
  + test_engine_no_fuel(thrust=500), no modifier (baseline), total mass=3000
- Test_Engine_ThrustPenalty.json — hull_test_s(mass=400) + test_engine_no_fuel(thrust=500)
  + test_thrust_penalty(param=0.5), thrust 500->250

Test Coverage:
- MOD-THRUST-001: Static thrust and max_speed after 2x modifier
- MOD-THRUST-002: Baseline unmodified engine (identity check)
- MOD-THRUST-003: Dynamic velocity reaches expected speed within 500 ticks
- MOD-THRUST-004: Derived acceleration_rate is correct with modified thrust
- MOD-THRUST-005: Penalty halves thrust (0.5x modifier)
"""

from game.simulation.physics_constants import K_SPEED, K_THRUST
from simulation_tests.scenarios.base import TestMetadata
from simulation_tests.scenarios.templates import PropulsionScenario
from simulation_tests.scenarios.validation import check_exact, check_approx, check_true
from simulation_tests.test_constants import (
    STANDARD_SEED,
    THRUST_BOOST_ENGINE_SHIP,
    MOD_BASE_ENGINE_THRUST,
    MOD_EXPECTED_THRUST,
    THRUST_BOOST_PARAM,
)

# =============================================================================
# EXPECTED VALUES FOR THRUST MODIFIER TESTS
# =============================================================================

# Ship: Test_Engine_ThrustBoost.json
#   hull_test_s(mass=400) + test_engine_no_fuel(thrust=500) + test_thrust_boost(param=2)
#   thrust 500 * 2 = 1000, mass=400
THRUST_BOOST_MASS = 400
THRUST_BOOST_BASE_THRUST = MOD_BASE_ENGINE_THRUST           # 500
THRUST_BOOST_MODIFIED_THRUST = MOD_EXPECTED_THRUST           # 1000
THRUST_BOOST_MAX_SPEED = (THRUST_BOOST_MODIFIED_THRUST * K_SPEED) / THRUST_BOOST_MASS  # 62.5
THRUST_BOOST_ACCEL = (THRUST_BOOST_MODIFIED_THRUST * K_THRUST) / (THRUST_BOOST_MASS ** 2)  # 0.15625

# Ship: Test_Engine_1x_MedMass.json
#   hull_test_m(mass=1000) + 2x mass_sim_1k(mass=1000 each) + test_engine_no_fuel(thrust=500)
#   no modifier, total mass=3000, thrust=500
BASELINE_SHIP_FILE = "Test_Engine_1x_MedMass.json"
BASELINE_MASS = 3000  # hull_test_m(1000) + 2x mass_sim_1k(1000 each)
BASELINE_THRUST = 500
BASELINE_MAX_SPEED = (BASELINE_THRUST * K_SPEED) / BASELINE_MASS  # ~4.1667

# Common test config
MOD_THRUST_TEST_TICKS = 500


# ============================================================================
# MOD-THRUST-001: Static thrust and max_speed verification
# ============================================================================

class ModThrustStaticScenario(PropulsionScenario):
    """
    MOD-THRUST-001: Verify thrust modifier doubles total_thrust and max_speed.

    Setup: Engine with thrust_mult=2 (param=2). Base thrust=500, mass=400.
    Checks ship.total_thrust == 1000, ship.max_speed == 62.5, final speed matches.
    """
    metadata = TestMetadata(
        test_id="MOD-THRUST-001",
        category="ThrustMultiplier",
        subcategory="ThrustMultiplier",
        name="Thrust modifier doubles thrust and max_speed",
        summary="Verify test_thrust_boost(param=2) doubles engine thrust from 500 to 1000 and max_speed to 62.5",
        conditions=[
            f"Ship: {THRUST_BOOST_ENGINE_SHIP} (hull_test_s + test_engine_no_fuel + test_thrust_boost(param={THRUST_BOOST_PARAM}), mass={THRUST_BOOST_MASS})",
            f"Base engine thrust: {THRUST_BOOST_BASE_THRUST}, modified: {THRUST_BOOST_MODIFIED_THRUST} (x{THRUST_BOOST_PARAM})",
            f"Expected max_speed: {THRUST_BOOST_MAX_SPEED}",
        ],
        edge_cases=[],
        expected_outcome=f"ship.total_thrust = {THRUST_BOOST_MODIFIED_THRUST}, ship.max_speed = {THRUST_BOOST_MAX_SPEED}",
        pass_criteria=f"total_thrust == {THRUST_BOOST_MODIFIED_THRUST} AND max_speed == {THRUST_BOOST_MAX_SPEED} AND reaches that speed",
        max_ticks=MOD_THRUST_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=30,
        tags=["modifier", "thrust_mult"],
    )

    ship_file = THRUST_BOOST_ENGINE_SHIP
    thrust_forward = True

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify modifier applied to thrust
        checks.append(check_exact(
            "Ship Mass", THRUST_BOOST_MASS,
            self.ship.mass, phase="data",
        ))
        checks.append(check_exact(
            "Modified Total Thrust", THRUST_BOOST_MODIFIED_THRUST,
            self.ship.total_thrust, phase="data",
        ))
        checks.append(check_approx(
            "Modified Max Speed", THRUST_BOOST_MAX_SPEED,
            self.ship.max_speed, tolerance=0.001,
            phase="data",
        ))

        # Outcome: ship reaches expected max speed
        final_speed = self.final_velocity.length()
        checks.append(check_approx(
            "Final Speed Matches Max Speed", THRUST_BOOST_MAX_SPEED,
            final_speed, tolerance=0.05,
            phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-THRUST-002: Baseline unmodified engine (identity check)
# ============================================================================

class ModThrustBaselineScenario(PropulsionScenario):
    """
    MOD-THRUST-002: Verify unmodified engine has expected base thrust.

    Setup: Standard engine (no modifier) with mass=3000, thrust=500.
    Confirms the baseline works correctly so modifier tests are meaningful.
    """
    metadata = TestMetadata(
        test_id="MOD-THRUST-002",
        category="ThrustMultiplier",
        subcategory="ThrustMultiplier",
        name="Baseline engine without thrust modifier",
        summary="Verify unmodified engine produces expected thrust (identity baseline for modifier comparison)",
        conditions=[
            f"Ship: {BASELINE_SHIP_FILE} (hull_test_m + 2x mass_sim_1k + test_engine_no_fuel, no modifier)",
            f"Engine thrust: {BASELINE_THRUST} (unmodified), mass: {BASELINE_MASS}",
            f"Expected max_speed: {BASELINE_MAX_SPEED:.4f}",
        ],
        edge_cases=["No modifier applied - identity check"],
        expected_outcome=f"ship.total_thrust = {BASELINE_THRUST} (unmodified)",
        pass_criteria=f"total_thrust == {BASELINE_THRUST}",
        max_ticks=MOD_THRUST_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=31,
        tags=["modifier", "thrust_mult"],
    )

    ship_file = BASELINE_SHIP_FILE
    thrust_forward = True

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify no modifier effect
        checks.append(check_exact(
            "Ship Mass", BASELINE_MASS,
            self.ship.mass, phase="data",
        ))
        checks.append(check_exact(
            "Unmodified Total Thrust", BASELINE_THRUST,
            self.ship.total_thrust, phase="data",
        ))
        checks.append(check_approx(
            "Unmodified Max Speed", BASELINE_MAX_SPEED,
            self.ship.max_speed, tolerance=0.001,
            phase="data",
        ))

        # Outcome: ship moves (basic sanity)
        checks.append(check_true(
            "Ship Reached Positive Speed",
            self.final_velocity.length() > 0,
            actual=self.final_velocity.length(),
            phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-THRUST-003: Dynamic velocity verification
# ============================================================================

class ModThrustDynamicVelocityScenario(PropulsionScenario):
    """
    MOD-THRUST-003: Verify modified ship actually reaches boosted speed.

    Setup: Same thrust-boosted ship, verify velocity.length() >= 60.0 within 500 ticks.
    This tests that the modifier's effect on thrust propagates through to actual movement,
    not just the static attributes.
    """
    metadata = TestMetadata(
        test_id="MOD-THRUST-003",
        category="ThrustMultiplier",
        subcategory="ThrustMultiplier",
        name="Thrust modifier produces faster movement",
        summary="Verify ship with 2x thrust modifier reaches velocity >= 60.0 within 500 ticks",
        conditions=[
            f"Ship: {THRUST_BOOST_ENGINE_SHIP} (hull_test_s + test_engine_no_fuel + test_thrust_boost(param={THRUST_BOOST_PARAM}), mass={THRUST_BOOST_MASS})",
            f"Modified thrust: {THRUST_BOOST_MODIFIED_THRUST}, expected max_speed: {THRUST_BOOST_MAX_SPEED}",
            f"Thrust forward for {MOD_THRUST_TEST_TICKS} ticks",
        ],
        edge_cases=["Dynamic verification - not just attribute check"],
        expected_outcome="Ship velocity.length() >= 60.0 (close to max_speed 62.5)",
        pass_criteria="velocity.length() >= 60.0 within 500 ticks",
        max_ticks=MOD_THRUST_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=32,
        tags=["modifier", "thrust_mult"],
    )

    ship_file = THRUST_BOOST_ENGINE_SHIP
    thrust_forward = True

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Precondition: modifier is applied
        checks.append(check_exact(
            "Modified Total Thrust", THRUST_BOOST_MODIFIED_THRUST,
            self.ship.total_thrust, phase="precondition",
        ))

        # Outcome: velocity actually reached boosted speed
        final_speed = self.final_velocity.length()
        checks.append(check_true(
            "Velocity >= 60.0 px/tick",
            final_speed >= 60.0,
            actual=final_speed,
            phase="outcome",
        ))
        checks.append(check_true(
            "Velocity <= Max Speed (not exceeding cap)",
            final_speed <= THRUST_BOOST_MAX_SPEED + 0.01,
            actual=final_speed,
            phase="outcome",
        ))
        return checks


# ============================================================================
# MOD-THRUST-004: Derived acceleration_rate verification
# ============================================================================

class ModThrustAccelerationScenario(PropulsionScenario):
    """
    MOD-THRUST-004: Verify derived acceleration_rate is correct with modified thrust.

    Setup: Engine with thrust_mult=2. Base thrust=500, modified=1000, mass=400.
    acceleration_rate = (total_thrust * K_THRUST) / mass^2
                     = (1000 * 2500) / 160000
                     = 0.15625

    This confirms the modifier effect cascades through all derived physics stats.
    """
    metadata = TestMetadata(
        test_id="MOD-THRUST-004",
        category="ThrustMultiplier",
        subcategory="ThrustMultiplier",
        name="Thrust modifier produces correct acceleration_rate",
        summary=(
            f"Verify acceleration_rate = (total_thrust * K_THRUST) / mass^2 "
            f"= ({THRUST_BOOST_MODIFIED_THRUST} * {K_THRUST}) / {THRUST_BOOST_MASS}^2 "
            f"= {THRUST_BOOST_ACCEL}"
        ),
        conditions=[
            f"Ship: {THRUST_BOOST_ENGINE_SHIP} (hull_test_s + test_engine_no_fuel + test_thrust_boost(param={THRUST_BOOST_PARAM}), mass={THRUST_BOOST_MASS})",
            f"Modified thrust: {THRUST_BOOST_MODIFIED_THRUST}, K_THRUST: {K_THRUST}",
            f"Expected acceleration_rate: ({THRUST_BOOST_MODIFIED_THRUST} * {K_THRUST}) / {THRUST_BOOST_MASS}^2 = {THRUST_BOOST_ACCEL}",
        ],
        edge_cases=["Derived stat depends on modified thrust, not base thrust"],
        expected_outcome=f"ship.acceleration_rate == {THRUST_BOOST_ACCEL}",
        pass_criteria=f"acceleration_rate == {THRUST_BOOST_ACCEL}",
        max_ticks=MOD_THRUST_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=33,
        tags=["modifier", "thrust_mult"],
    )

    ship_file = THRUST_BOOST_ENGINE_SHIP
    thrust_forward = True

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify modifier applied to thrust
        checks.append(check_exact(
            "Modified Total Thrust", THRUST_BOOST_MODIFIED_THRUST,
            self.ship.total_thrust, phase="data",
        ))
        checks.append(check_exact(
            "Ship Mass", THRUST_BOOST_MASS,
            self.ship.mass, phase="data",
        ))

        # Outcome: acceleration_rate matches formula
        checks.append(check_approx(
            "Acceleration Rate", THRUST_BOOST_ACCEL,
            self.ship.acceleration_rate, tolerance=0.0001,
            phase="outcome",
        ))

        # Cross-check: the template also calculates expected_acceleration_rate
        checks.append(check_approx(
            "Template Expected Acceleration Matches",
            THRUST_BOOST_ACCEL,
            self.expected_acceleration_rate, tolerance=0.0001,
            phase="outcome",
        ))
        return checks


# =============================================================================
# EXPECTED VALUES FOR THRUST PENALTY TESTS
# =============================================================================

# Ship: Test_Engine_ThrustPenalty.json
#   hull_test_s(mass=400) + test_engine_no_fuel(thrust=500) + test_thrust_penalty(param=0.5)
#   thrust 500 * 0.5 = 250, mass=400
THRUST_PENALTY_SHIP_FILE = "Test_Engine_ThrustPenalty.json"
THRUST_PENALTY_MASS = 400
THRUST_PENALTY_PARAM = 0.5
THRUST_PENALTY_MODIFIED_THRUST = MOD_BASE_ENGINE_THRUST * THRUST_PENALTY_PARAM  # 250
THRUST_PENALTY_MAX_SPEED = (THRUST_PENALTY_MODIFIED_THRUST * K_SPEED) / THRUST_PENALTY_MASS  # 15.625


# ============================================================================
# MOD-THRUST-005: Penalty halves thrust
# ============================================================================

class ModThrustPenaltyScenario(PropulsionScenario):
    """
    MOD-THRUST-005: Verify thrust penalty modifier halves total_thrust and max_speed.

    Setup: Engine with thrust_mult=0.5 (param=0.5). Base thrust=500, mass=400.
    Checks ship.total_thrust == 250, ship.max_speed ~= 15.625, ship reaches that speed.
    """
    metadata = TestMetadata(
        test_id="MOD-THRUST-005",
        category="ThrustMultiplier",
        subcategory="ThrustMultiplier",
        name="Penalty halves thrust",
        summary="Verify test_thrust_penalty(param=0.5) halves engine thrust from 500 to 250 and max_speed to 15.625",
        conditions=[
            f"Ship: {THRUST_PENALTY_SHIP_FILE} (hull_test_s + test_engine_no_fuel + test_thrust_penalty(param={THRUST_PENALTY_PARAM}), mass={THRUST_PENALTY_MASS})",
            f"Base engine thrust: {MOD_BASE_ENGINE_THRUST}, modified: {THRUST_PENALTY_MODIFIED_THRUST} (x{THRUST_PENALTY_PARAM})",
            f"Expected max_speed: {THRUST_PENALTY_MAX_SPEED}",
        ],
        edge_cases=["Penalty modifier reduces thrust below base value"],
        expected_outcome=f"ship.total_thrust = {THRUST_PENALTY_MODIFIED_THRUST}, ship.max_speed = {THRUST_PENALTY_MAX_SPEED}",
        pass_criteria=f"total_thrust == {THRUST_PENALTY_MODIFIED_THRUST} AND max_speed ~= {THRUST_PENALTY_MAX_SPEED} AND reaches near that speed",
        max_ticks=MOD_THRUST_TEST_TICKS,
        seed=STANDARD_SEED,
        battle_end_mode="time_based",
        ui_priority=34,
        tags=["modifier", "thrust_mult", "penalty"],
    )

    ship_file = THRUST_PENALTY_SHIP_FILE
    thrust_forward = True

    def validate(self, engine) -> list:
        checks = self._template_preconditions()

        # Data: verify penalty modifier applied to thrust
        checks.append(check_exact(
            "Modified Total Thrust", THRUST_PENALTY_MODIFIED_THRUST,
            self.ship.total_thrust, phase="data",
        ))
        checks.append(check_approx(
            "Modified Max Speed", THRUST_PENALTY_MAX_SPEED,
            self.ship.max_speed, tolerance=0.001,
            phase="data",
        ))

        # Outcome: ship reaches near expected max speed
        final_speed = self.final_velocity.length()
        checks.append(check_true(
            "Final Speed > 14 (reaches near max speed)",
            final_speed > 14,
            actual=final_speed,
            phase="outcome",
        ))
        checks.append(check_true(
            "Final Speed < 16 (doesn't exceed max)",
            final_speed < 16,
            actual=final_speed,
            phase="outcome",
        ))
        return checks
