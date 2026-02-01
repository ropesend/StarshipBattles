"""
Resource System Test Scenarios (RESOURCE-001 to RESOURCE-008)

These tests validate that resource consumption, depletion, and regeneration
work correctly:
- Fuel consumption by engines (constant drain)
- Fuel starvation stops engine thrust
- Fuel generation sustains engine operation
- Energy consumption by beam weapons (per-shot)
- Energy depletion stops weapon
- Energy regeneration sustains weapon
- Ammo consumption by projectile weapons
- Ammo consumption by seeker weapons

Test Coverage:
- Fuel: 3 tests (consumption, depletion/starvation, regeneration)
- Energy: 3 tests (consumption, depletion, regeneration)
- Ammo Projectile: 2 tests (consumption, depletion)
- Ammo Seeker: 1 test (consumption/launches)

Key Mechanics:
- ResourceConsumption: Constant drain (engines) or activation cost (weapons)
- ResourceStorage: Adds capacity to ship's resource pool
- ResourceGeneration: Regenerates resource per tick

Expected Values Architecture:
- Each test defines EXPECTED values that must match the actual .json data
- Pre-run validation compares expected vs actual BEFORE test execution
- Tests cannot run if data mismatches are detected
- This ensures tests stay in sync with ship/component data files
"""

import pygame
from game.simulation.physics_constants import K_SPEED
from simulation_tests.scenarios import TestScenario, TestMetadata
from simulation_tests.scenarios.validation import DeterministicMatchRule
from simulation_tests.scenarios.prerun_validation import (
    DataExpectation, CalculatedExpectation, SetupCondition, PassCriterion
)


# =============================================================================
# EXPECTED VALUES FOR RESOURCE TESTS
# =============================================================================
# These values MUST match the actual .json ship/component data files.
# If a mismatch is detected, the test will be blocked from running.
#
# Data source: simulation_tests/data/ships/*.json
#              simulation_tests/data/components.json
# =============================================================================

# -----------------------------------------------------------------------------
# RESOURCE-001: Engine Fuel Consumption (Test_Engine_FuelConsumption.json)
# Engine: test_engine_fuel_1 (thrust=500, 1.0 fuel/sec)
# Storage: test_storage_fuel (1000 fuel)
# Hull: hull_test_s (mass=400)
# -----------------------------------------------------------------------------
RES001_SHIP_FILE = "Test_Engine_FuelConsumption.json"
RES001_HULL_MASS = 400
RES001_ENGINE_THRUST = 500
RES001_FUEL_CONSUMPTION_PER_SEC = 1.0
RES001_INITIAL_FUEL = 1000.0
RES001_MAX_TICKS = 500
RES001_DURATION_SEC = RES001_MAX_TICKS / 100.0  # 5.0 seconds
RES001_EXPECTED_FUEL_CONSUMED = RES001_FUEL_CONSUMPTION_PER_SEC * RES001_DURATION_SEC  # 5.0
RES001_EXPECTED_FINAL_FUEL = RES001_INITIAL_FUEL - RES001_EXPECTED_FUEL_CONSUMED  # 995.0
RES001_MAX_SPEED = (RES001_ENGINE_THRUST * K_SPEED) / RES001_HULL_MASS  # 31.25

# -----------------------------------------------------------------------------
# RESOURCE-002: Engine Fuel Depletion (Test_Engine_FuelDepletion.json)
# Engine: test_engine_fuel_1 (1.0 fuel/sec)
# Storage: test_storage_fuel_small (2.5 fuel)
# Expected depletion at tick 250 (2.5 seconds)
# -----------------------------------------------------------------------------
RES002_SHIP_FILE = "Test_Engine_FuelDepletion.json"
RES002_INITIAL_FUEL = 2.5
RES002_FUEL_CONSUMPTION_PER_SEC = 1.0
RES002_MAX_TICKS = 500
RES002_EXPECTED_DEPLETION_TICK = int(RES002_INITIAL_FUEL / RES002_FUEL_CONSUMPTION_PER_SEC * 100)  # 250
RES002_EXPECTED_FINAL_FUEL = 0.0
RES002_EXPECTED_FINAL_VELOCITY = 0.0  # Ship stops when fuel depletes

# -----------------------------------------------------------------------------
# RESOURCE-003: Fuel Generation Sustains Movement (Test_Engine_FuelRegen.json)
# Engine: test_engine_fuel_1 (1.0 fuel/sec consumption)
# Storage: test_storage_fuel_small (2.5 fuel)
# Generator: test_gen_fuel (1.0 fuel/sec generation)
# Net rate: 0 (balanced)
# -----------------------------------------------------------------------------
RES003_SHIP_FILE = "Test_Engine_FuelRegen.json"
RES003_INITIAL_FUEL = 2.5
RES003_FUEL_CONSUMPTION_PER_SEC = 1.0
RES003_FUEL_GENERATION_PER_SEC = 1.0
RES003_MAX_TICKS = 500
RES003_NET_RATE = RES003_FUEL_GENERATION_PER_SEC - RES003_FUEL_CONSUMPTION_PER_SEC  # 0.0

# -----------------------------------------------------------------------------
# RESOURCE-004: Beam Energy Consumption (Test_Attacker_BeamRapid_HighEnergy.json)
# Weapon: test_beam_rapid_1dmg (1 energy/shot, 1 damage, 0 reload)
# Storage: test_storage_energy_100k (100,000 energy)
# Duration: 100 ticks = 100 shots = 100 energy consumed
# -----------------------------------------------------------------------------
RES004_SHIP_FILE = "Test_Attacker_BeamRapid_HighEnergy.json"
RES004_INITIAL_ENERGY = 100000.0
RES004_ENERGY_PER_SHOT = 1
RES004_DAMAGE_PER_HIT = 1
RES004_MAX_TICKS = 100
RES004_EXPECTED_SHOTS = RES004_MAX_TICKS  # 100
RES004_EXPECTED_ENERGY_CONSUMED = RES004_EXPECTED_SHOTS * RES004_ENERGY_PER_SHOT  # 100
RES004_EXPECTED_FINAL_ENERGY = RES004_INITIAL_ENERGY - RES004_EXPECTED_ENERGY_CONSUMED  # 99,900

# -----------------------------------------------------------------------------
# RESOURCE-005: Beam Energy Depletion (Test_Attacker_BeamRapid_LowEnergy.json)
# Weapon: test_beam_rapid_1dmg (1 energy/shot)
# Storage: test_storage_energy_small (25 energy)
# Expected: 25 shots then stops
# -----------------------------------------------------------------------------
RES005_SHIP_FILE = "Test_Attacker_BeamRapid_LowEnergy.json"
RES005_INITIAL_ENERGY = 25.0
RES005_ENERGY_PER_SHOT = 1
RES005_MAX_TICKS = 100
RES005_EXPECTED_SHOTS = int(RES005_INITIAL_ENERGY / RES005_ENERGY_PER_SHOT)  # 25
RES005_EXPECTED_FINAL_ENERGY = 0.0

# -----------------------------------------------------------------------------
# RESOURCE-005a: Energy Regeneration Sustains Weapon (Test_Attacker_BeamRapid_WithGen.json)
# Weapon: test_beam_rapid_1dmg (1 energy/shot, fires every tick)
# Storage: test_storage_energy_small (25 energy)
# Generator: test_gen_fusion (100 energy/sec = 1/tick)
# Net rate: 0 (balanced)
# -----------------------------------------------------------------------------
RES005A_SHIP_FILE = "Test_Attacker_BeamRapid_WithGen.json"
RES005A_INITIAL_ENERGY = 25.0
RES005A_ENERGY_PER_SHOT = 1
RES005A_ENERGY_GENERATION_PER_SEC = 100.0  # = 1/tick
RES005A_MAX_TICKS = 100
RES005A_EXPECTED_SHOTS = RES005A_MAX_TICKS  # 100 (generator keeps up)

# -----------------------------------------------------------------------------
# RESOURCE-006: Projectile Ammo Consumption (Test_Attacker_ProjRapid_HighAmmo.json)
# Weapon: test_proj_rapid (1 ammo/shot, 0 reload)
# Storage: test_storage_ammo_100k (100,000 ammo)
# Duration: 100 ticks = 100 shots
# -----------------------------------------------------------------------------
RES006_SHIP_FILE = "Test_Attacker_ProjRapid_HighAmmo.json"
RES006_INITIAL_AMMO = 100000.0
RES006_AMMO_PER_SHOT = 1
RES006_MAX_TICKS = 100
RES006_EXPECTED_SHOTS = RES006_MAX_TICKS  # 100
RES006_EXPECTED_AMMO_CONSUMED = RES006_EXPECTED_SHOTS * RES006_AMMO_PER_SHOT  # 100
RES006_EXPECTED_FINAL_AMMO = RES006_INITIAL_AMMO - RES006_EXPECTED_AMMO_CONSUMED  # 99,900

# -----------------------------------------------------------------------------
# RESOURCE-007: Projectile Ammo Depletion (Test_Attacker_ProjRapid_LowAmmo.json)
# Weapon: test_proj_rapid (1 ammo/shot)
# Storage: test_storage_ammo_small (10 ammo)
# Expected: 10 shots then stops
# -----------------------------------------------------------------------------
RES007_SHIP_FILE = "Test_Attacker_ProjRapid_LowAmmo.json"
RES007_INITIAL_AMMO = 10.0
RES007_AMMO_PER_SHOT = 1
RES007_MAX_TICKS = 100
RES007_EXPECTED_SHOTS = int(RES007_INITIAL_AMMO / RES007_AMMO_PER_SHOT)  # 10
RES007_EXPECTED_FINAL_AMMO = 0.0

# -----------------------------------------------------------------------------
# RESOURCE-008: Seeker Ammo Consumption (Test_Attacker_SeekerRapid_HighAmmo.json)
# Weapon: test_seeker_rapid (1 ammo/launch, 0 reload)
# Storage: test_storage_ammo_100k (100,000 ammo)
# Duration: 100 ticks = 100 launches
# Note: Verifies launches/ammo only, NOT hits (seekers take time to reach target)
# -----------------------------------------------------------------------------
RES008_SHIP_FILE = "Test_Attacker_SeekerRapid_HighAmmo.json"
RES008_INITIAL_AMMO = 100000.0
RES008_AMMO_PER_LAUNCH = 1
RES008_MAX_TICKS = 100
RES008_EXPECTED_LAUNCHES = RES008_MAX_TICKS  # 100
RES008_EXPECTED_AMMO_CONSUMED = RES008_EXPECTED_LAUNCHES * RES008_AMMO_PER_LAUNCH  # 100
RES008_EXPECTED_FINAL_AMMO = RES008_INITIAL_AMMO - RES008_EXPECTED_AMMO_CONSUMED  # 99,900


# ============================================================================
# FUEL CONSUMPTION TESTS
# ============================================================================

class EngineFuelConsumptionScenario(TestScenario):
    """
    RESOURCE-001: Engine Consumes Fuel

    Tests that engine fuel consumption rate is predictable. With 1.0 fuel/sec
    consumption and 1000 fuel capacity, running for 500 ticks (5 seconds)
    should consume exactly 5.0 fuel.

    Pre-Run Validation:
    - Data values from .json files are validated against expected values
    - Calculated physics values are validated against formulas
    - Test will not run if any validation fails
    """

    metadata = TestMetadata(
        test_id="RESOURCE-001",
        category="Resource System",
        subcategory="Fuel",
        name="Engine Fuel Consumption",
        summary="Validates engine consumes fuel at predictable rate during operation",
        conditions=[
            f"Ship: {RES001_SHIP_FILE}",
            f"Engine thrust: {RES001_ENGINE_THRUST}",
            f"Fuel consumption: {RES001_FUEL_CONSUMPTION_PER_SEC}/sec",
            f"Initial Fuel: {RES001_INITIAL_FUEL} units",
            f"Test Duration: {RES001_MAX_TICKS} ticks ({RES001_DURATION_SEC} seconds)",
            "Throttle: 100% (thrust_forward each tick)"
        ],
        edge_cases=[
            "Engine runs continuously at full throttle",
            "Large fuel tank - won't deplete during test",
            "Ship should reach max speed and keep moving"
        ],
        expected_outcome=f"Fuel decreases from {RES001_INITIAL_FUEL} to {RES001_EXPECTED_FINAL_FUEL} ({RES001_EXPECTED_FUEL_CONSUMED} consumed)",
        pass_criteria=f"final_fuel = {RES001_EXPECTED_FINAL_FUEL}, final_velocity > 0",
        max_ticks=RES001_MAX_TICKS,
        seed=42,
        battle_end_mode="time_based",
        ui_priority=10,
        tags=["resource", "fuel", "consumption", "engine"],
        validation_rules=[
            # Data verification
            DeterministicMatchRule(
                name='Initial Fuel',
                path='results.initial_fuel',
                expected=RES001_INITIAL_FUEL,
                description=f'Ship starts with {RES001_INITIAL_FUEL} fuel'
            ),
            DeterministicMatchRule(
                name='Final Fuel',
                path='results.final_fuel',
                expected=RES001_EXPECTED_FINAL_FUEL,
                tolerance=0.01,
                description=f'{RES001_INITIAL_FUEL} - {RES001_EXPECTED_FUEL_CONSUMED} = {RES001_EXPECTED_FINAL_FUEL}'
            ),
            DeterministicMatchRule(
                name='Fuel Consumed',
                path='results.fuel_consumed',
                expected=RES001_EXPECTED_FUEL_CONSUMED,
                tolerance=0.01,
                description=f'{RES001_FUEL_CONSUMPTION_PER_SEC}/sec × {RES001_DURATION_SEC}s = {RES001_EXPECTED_FUEL_CONSUMED}'
            ),
        ]
    )

    # =========================================================================
    # PRE-RUN VALIDATION: Data Expectations
    # =========================================================================
    data_expectations = [
        DataExpectation(
            name='Initial Fuel Capacity',
            source='initial_fuel',
            expected=RES001_INITIAL_FUEL,
            json_file=RES001_SHIP_FILE
        ),
        DataExpectation(
            name='Engine Thrust',
            source='total_thrust',
            expected=RES001_ENGINE_THRUST,
            json_file=RES001_SHIP_FILE
        ),
    ]

    # =========================================================================
    # PRE-RUN VALIDATION: Calculated Expectations
    # =========================================================================
    calculated_expectations = [
        CalculatedExpectation(
            name='Expected Fuel Consumed',
            formula='consumption_rate × duration_seconds',
            formula_expr=lambda rate, duration: rate * duration,
            expected=RES001_EXPECTED_FUEL_CONSUMED,
            variables={
                'rate': RES001_FUEL_CONSUMPTION_PER_SEC,
                'duration': RES001_DURATION_SEC
            }
        ),
        CalculatedExpectation(
            name='Expected Final Fuel',
            formula='initial_fuel - fuel_consumed',
            formula_expr=lambda initial, consumed: initial - consumed,
            expected=RES001_EXPECTED_FINAL_FUEL,
            variables={
                'initial': RES001_INITIAL_FUEL,
                'consumed': RES001_EXPECTED_FUEL_CONSUMED
            }
        ),
    ]

    # =========================================================================
    # SETUP CONDITIONS
    # =========================================================================
    setup_conditions = [
        SetupCondition(name='Initial Position', value='(0, 0)', description='Ship starts at origin'),
        SetupCondition(name='Initial Angle', value='0°', description='Ship faces right (+X)'),
        SetupCondition(name='Test Duration', value=f'{RES001_MAX_TICKS} ticks', description=f'{RES001_DURATION_SEC} seconds'),
        SetupCondition(name='Thrust Command', value='Forward (each tick)', description='thrust_forward() called every tick'),
    ]

    # =========================================================================
    # PASS CRITERIA
    # =========================================================================
    pass_criteria = [
        PassCriterion(
            description=f'Final Fuel = {RES001_EXPECTED_FINAL_FUEL}',
            expression=lambda r: abs(r.get('final_fuel', 0) - RES001_EXPECTED_FINAL_FUEL) < 0.01,
            numeric_threshold=RES001_EXPECTED_FINAL_FUEL
        ),
        PassCriterion(
            description=f'Fuel Consumed = {RES001_EXPECTED_FUEL_CONSUMED}',
            expression=lambda r: abs(r.get('fuel_consumed', 0) - RES001_EXPECTED_FUEL_CONSUMED) < 0.01,
            numeric_threshold=RES001_EXPECTED_FUEL_CONSUMED
        ),
        PassCriterion(
            description='Ship is moving (velocity > 0)',
            expression=lambda r: r.get('final_velocity', 0) > 0,
            numeric_threshold=0.0
        ),
    ]

    def setup(self, battle_engine):
        """Setup test scenario."""
        ship = self._load_ship(RES001_SHIP_FILE)

        ship.position = pygame.math.Vector2(0, 0)
        ship.angle = 0

        self.initial_fuel = ship.resources.get_value('fuel')
        self.initial_velocity = ship.current_speed
        self.start_position = pygame.math.Vector2(ship.position)

        end_condition = self._create_end_condition()

        battle_engine.start([ship], [],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        self.ship = ship
        self._run_prerun_validation()

    def _run_prerun_validation(self):
        """Run pre-run validation and store results."""
        from simulation_tests.scenarios.prerun_validation import PreRunValidator

        context = {
            'ship': self.ship,
            'initial_fuel': self.ship.resources.get_value('fuel'),
            'total_thrust': self.ship.total_thrust,
        }

        validator = PreRunValidator()
        self.prerun_validation = validator.validate_scenario(self, context)
        self.results['prerun_validation'] = self.prerun_validation.to_dict()

        if not self.prerun_validation.can_run:
            error_msg = "Pre-run validation failed:\n" + "\n".join(self.prerun_validation.blocking_errors)
            raise ValueError(error_msg)

    def update(self, battle_engine):
        """Apply thrust each tick to make ship move and consume fuel."""
        if self.ship and self.ship.is_alive:
            self.ship.thrust_forward()

    def verify(self, battle_engine) -> bool:
        """Check fuel consumption matches expected."""
        final_fuel = self.ship.resources.get_value('fuel')
        fuel_consumed = self.initial_fuel - final_fuel
        final_velocity = self.ship.current_speed
        final_position = pygame.math.Vector2(self.ship.position)
        distance_traveled = final_position.distance_to(self.start_position)
        ticks_run = battle_engine.tick_counter

        # Store results
        self.results['test_id'] = self.metadata.test_id
        self.results['initial_fuel'] = self.initial_fuel
        self.results['final_fuel'] = final_fuel
        self.results['fuel_consumed'] = fuel_consumed
        self.results['expected_consumed'] = RES001_EXPECTED_FUEL_CONSUMED
        self.results['expected_final_fuel'] = RES001_EXPECTED_FINAL_FUEL
        self.results['final_velocity'] = final_velocity
        self.results['distance_traveled'] = distance_traveled
        self.results['ticks_run'] = ticks_run

        # Run validation rules
        if hasattr(self.metadata, 'validation_rules') and self.metadata.validation_rules:
            self.run_validation(battle_engine)

        # Evaluate pass criteria
        all_criteria_passed = all(
            criterion.evaluate(self.results)
            for criterion in self.pass_criteria
        )
        self.results['all_criteria_passed'] = all_criteria_passed

        return all_criteria_passed


class EngineFuelDepletionScenario(TestScenario):
    """
    RESOURCE-002: Engine Starvation Stops Movement

    Tests that engine stops providing thrust when fuel is depleted.
    With 2.5 fuel and 1.0 fuel/sec consumption, engine runs out at tick ~250.
    Ship should decelerate to 0 velocity by end of test.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-002",
        category="Resource System",
        subcategory="Fuel",
        name="Engine Fuel Depletion (Starvation)",
        summary="Validates engine stops providing thrust when fuel depletes",
        conditions=[
            f"Ship: {RES002_SHIP_FILE}",
            f"Fuel consumption: {RES002_FUEL_CONSUMPTION_PER_SEC}/sec",
            f"Initial Fuel: {RES002_INITIAL_FUEL} units",
            f"Expected Depletion: tick ~{RES002_EXPECTED_DEPLETION_TICK} ({RES002_INITIAL_FUEL} seconds)",
            f"Test Duration: {RES002_MAX_TICKS} ticks",
            "Throttle: 100%"
        ],
        edge_cases=[
            "Engine starves when fuel reaches 0",
            "Ship decelerates after starvation (no thrust)",
            "Final velocity should be 0"
        ],
        expected_outcome=f"Fuel depletes at tick ~{RES002_EXPECTED_DEPLETION_TICK}, ship decelerates to velocity=0",
        pass_criteria=f"final_fuel = 0, final_velocity = 0, distance_traveled > 0",
        max_ticks=RES002_MAX_TICKS,
        seed=42,
        battle_end_mode="time_based",
        ui_priority=10,
        tags=["resource", "fuel", "depletion", "starvation", "engine"],
        validation_rules=[
            DeterministicMatchRule(
                name='Final Fuel',
                path='results.final_fuel',
                expected=RES002_EXPECTED_FINAL_FUEL,
                description='Fuel fully depleted'
            ),
            DeterministicMatchRule(
                name='Final Velocity',
                path='results.final_velocity',
                expected=RES002_EXPECTED_FINAL_VELOCITY,
                tolerance=0.01,
                description='Ship stopped after fuel starvation'
            ),
        ]
    )

    data_expectations = [
        DataExpectation(
            name='Initial Fuel',
            source='initial_fuel',
            expected=RES002_INITIAL_FUEL,
            json_file=RES002_SHIP_FILE
        ),
    ]

    calculated_expectations = [
        CalculatedExpectation(
            name='Depletion Tick',
            formula='initial_fuel / consumption_rate × 100',
            formula_expr=lambda fuel, rate: int(fuel / rate * 100),
            expected=RES002_EXPECTED_DEPLETION_TICK,
            variables={
                'fuel': RES002_INITIAL_FUEL,
                'rate': RES002_FUEL_CONSUMPTION_PER_SEC
            }
        ),
    ]

    pass_criteria = [
        PassCriterion(
            description='Fuel Depleted (final_fuel = 0)',
            expression=lambda r: r.get('final_fuel', 1) == 0,
            numeric_threshold=0.0
        ),
        PassCriterion(
            description='Ship Stopped (velocity < 0.01)',
            expression=lambda r: r.get('final_velocity', 1) < 0.01,
            numeric_threshold=0.0
        ),
        PassCriterion(
            description='Ship Moved Before Starvation',
            expression=lambda r: r.get('distance_traveled', 0) > 0,
            numeric_threshold=0.0
        ),
    ]

    def setup(self, battle_engine):
        """Setup test scenario."""
        ship = self._load_ship(RES002_SHIP_FILE)

        ship.position = pygame.math.Vector2(0, 0)
        ship.angle = 0

        self.initial_fuel = ship.resources.get_value('fuel')
        self.initial_position = pygame.math.Vector2(ship.position)

        end_condition = self._create_end_condition()

        battle_engine.start([ship], [],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        self.ship = ship

    def update(self, battle_engine):
        """Apply thrust each tick."""
        if self.ship and self.ship.is_alive:
            self.ship.thrust_forward()

    def verify(self, battle_engine) -> bool:
        """Check fuel depleted and ship stopped."""
        final_fuel = self.ship.resources.get_value('fuel')
        final_velocity = self.ship.current_speed
        final_position = pygame.math.Vector2(self.ship.position)
        distance_traveled = final_position.distance_to(self.initial_position)
        ticks_run = battle_engine.tick_counter

        self.results['test_id'] = self.metadata.test_id
        self.results['initial_fuel'] = self.initial_fuel
        self.results['final_fuel'] = final_fuel
        self.results['fuel_consumed'] = self.initial_fuel - final_fuel
        self.results['final_velocity'] = final_velocity
        self.results['distance_traveled'] = distance_traveled
        self.results['ticks_run'] = ticks_run

        # Run validation rules
        if hasattr(self.metadata, 'validation_rules') and self.metadata.validation_rules:
            self.run_validation(battle_engine)

        # Evaluate pass criteria
        all_criteria_passed = all(
            criterion.evaluate(self.results)
            for criterion in self.pass_criteria
        )
        self.results['all_criteria_passed'] = all_criteria_passed

        return all_criteria_passed


class EngineFuelRegenerationScenario(TestScenario):
    """
    RESOURCE-003: Fuel Generation Sustains Movement

    Tests that fuel generator keeps engine running. With 1.0 fuel/sec consumption
    and 1.0 fuel/sec generation, fuel should stay stable and ship keeps moving.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-003",
        category="Resource System",
        subcategory="Fuel",
        name="Fuel Generation Sustains Movement",
        summary="Validates fuel generator keeps engine running by matching consumption",
        conditions=[
            f"Ship: {RES003_SHIP_FILE}",
            f"Fuel Consumption: {RES003_FUEL_CONSUMPTION_PER_SEC}/sec",
            f"Fuel Generation: {RES003_FUEL_GENERATION_PER_SEC}/sec",
            f"Net Rate: {RES003_NET_RATE} (balanced)",
            f"Initial Fuel: {RES003_INITIAL_FUEL} units",
            f"Test Duration: {RES003_MAX_TICKS} ticks"
        ],
        edge_cases=[
            "Generator exactly matches consumption",
            "Fuel should stay approximately stable",
            "Ship should keep moving throughout"
        ],
        expected_outcome=f"Fuel stays stable (~{RES003_INITIAL_FUEL}), ship maintains velocity > 0",
        pass_criteria=f"final_fuel ≈ initial_fuel, final_velocity > 0",
        max_ticks=RES003_MAX_TICKS,
        seed=42,
        battle_end_mode="time_based",
        ui_priority=10,
        tags=["resource", "fuel", "regeneration", "engine"],
        validation_rules=[
            DeterministicMatchRule(
                name='Fuel Stable',
                path='results.fuel_change',
                expected=0.0,
                tolerance=0.5,
                description='Generator matches consumption (net rate = 0)'
            ),
        ]
    )

    data_expectations = [
        DataExpectation(
            name='Initial Fuel',
            source='initial_fuel',
            expected=RES003_INITIAL_FUEL,
            json_file=RES003_SHIP_FILE
        ),
    ]

    pass_criteria = [
        PassCriterion(
            description='Fuel Stable (change < 0.5)',
            expression=lambda r: abs(r.get('fuel_change', 10)) < 0.5,
            numeric_threshold=0.0
        ),
        PassCriterion(
            description='Ship Moving (velocity > 0)',
            expression=lambda r: r.get('final_velocity', 0) > 0,
            numeric_threshold=0.0
        ),
    ]

    def setup(self, battle_engine):
        """Setup test scenario."""
        ship = self._load_ship(RES003_SHIP_FILE)

        ship.position = pygame.math.Vector2(0, 0)
        ship.angle = 0

        self.initial_fuel = ship.resources.get_value('fuel')

        end_condition = self._create_end_condition()

        battle_engine.start([ship], [],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        self.ship = ship

    def update(self, battle_engine):
        """Apply thrust each tick."""
        if self.ship and self.ship.is_alive:
            self.ship.thrust_forward()

    def verify(self, battle_engine) -> bool:
        """Check fuel stable and ship moving."""
        final_fuel = self.ship.resources.get_value('fuel')
        final_velocity = self.ship.current_speed
        ticks_run = battle_engine.tick_counter

        self.results['test_id'] = self.metadata.test_id
        self.results['initial_fuel'] = self.initial_fuel
        self.results['final_fuel'] = final_fuel
        self.results['fuel_change'] = final_fuel - self.initial_fuel
        self.results['final_velocity'] = final_velocity
        self.results['ticks_run'] = ticks_run

        # Run validation rules
        if hasattr(self.metadata, 'validation_rules') and self.metadata.validation_rules:
            self.run_validation(battle_engine)

        # Evaluate pass criteria
        all_criteria_passed = all(
            criterion.evaluate(self.results)
            for criterion in self.pass_criteria
        )
        self.results['all_criteria_passed'] = all_criteria_passed

        return all_criteria_passed


# ============================================================================
# ENERGY CONSUMPTION TESTS (BEAM WEAPONS)
# ============================================================================

class BeamEnergyConsumptionScenario(TestScenario):
    """
    RESOURCE-004: Beam Weapon Consumes Energy

    Tests that beam weapon consumes energy per shot. With 1 energy per shot,
    0 reload, and 100,000 energy, weapon fires 100 times consuming 100 energy.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-004",
        category="Resource System",
        subcategory="Energy",
        name="Beam Weapon Energy Consumption",
        summary="Validates beam weapon consumes energy per shot at predictable rate",
        conditions=[
            f"Attacker: {RES004_SHIP_FILE}",
            "Target: Test_Target_Stationary.json",
            f"Energy Cost: {RES004_ENERGY_PER_SHOT} per shot",
            f"Initial Energy: {RES004_INITIAL_ENERGY} units",
            "Weapon Reload: 0.0 (fires every tick)",
            "Distance: 10 pixels (point-blank)",
            f"Test Duration: {RES004_MAX_TICKS} ticks"
        ],
        edge_cases=[
            "Weapon fires every tick (0 reload)",
            f"1 damage per hit for easy counting",
            "High capacity storage - won't deplete"
        ],
        expected_outcome=f"{RES004_EXPECTED_SHOTS} shots fired, {RES004_EXPECTED_ENERGY_CONSUMED} energy consumed, final = {RES004_EXPECTED_FINAL_ENERGY}",
        pass_criteria=f"energy_consumed = {RES004_EXPECTED_ENERGY_CONSUMED}, shots_fired = {RES004_EXPECTED_SHOTS}",
        max_ticks=RES004_MAX_TICKS,
        seed=42,
        battle_end_mode="time_based",
        ui_priority=9,
        tags=["resource", "energy", "consumption", "beam-weapons"],
        validation_rules=[
            DeterministicMatchRule(
                name='Energy Consumed',
                path='results.energy_consumed',
                expected=RES004_EXPECTED_ENERGY_CONSUMED,
                tolerance=0.01,
                description=f'{RES004_EXPECTED_SHOTS} shots × {RES004_ENERGY_PER_SHOT} energy/shot'
            ),
            DeterministicMatchRule(
                name='Final Energy',
                path='results.final_energy',
                expected=RES004_EXPECTED_FINAL_ENERGY,
                tolerance=0.01,
                description=f'{RES004_INITIAL_ENERGY} - {RES004_EXPECTED_ENERGY_CONSUMED} = {RES004_EXPECTED_FINAL_ENERGY}'
            ),
        ]
    )

    data_expectations = [
        DataExpectation(
            name='Initial Energy',
            source='initial_energy',
            expected=RES004_INITIAL_ENERGY,
            json_file=RES004_SHIP_FILE
        ),
    ]

    calculated_expectations = [
        CalculatedExpectation(
            name='Expected Energy Consumed',
            formula='shots × energy_per_shot',
            formula_expr=lambda shots, cost: shots * cost,
            expected=RES004_EXPECTED_ENERGY_CONSUMED,
            variables={
                'shots': RES004_EXPECTED_SHOTS,
                'cost': RES004_ENERGY_PER_SHOT
            }
        ),
    ]

    pass_criteria = [
        PassCriterion(
            description=f'Energy Consumed = {RES004_EXPECTED_ENERGY_CONSUMED}',
            expression=lambda r: abs(r.get('energy_consumed', 0) - RES004_EXPECTED_ENERGY_CONSUMED) < 0.01,
            numeric_threshold=RES004_EXPECTED_ENERGY_CONSUMED
        ),
        PassCriterion(
            description=f'Shots Fired = {RES004_EXPECTED_SHOTS}',
            expression=lambda r: r.get('shots_fired', 0) == RES004_EXPECTED_SHOTS,
            numeric_threshold=RES004_EXPECTED_SHOTS
        ),
    ]

    def setup(self, battle_engine):
        """Setup test scenario."""
        attacker = self._load_ship(RES004_SHIP_FILE)
        target = self._load_ship("Test_Target_Stationary.json")

        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0
        target.position = pygame.math.Vector2(10, 0)
        target.angle = 0

        self.initial_energy = attacker.resources.get_value('energy')
        self.initial_hp = target.hp

        end_condition = self._create_end_condition()

        battle_engine.start([attacker], [target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        attacker.current_target = target

        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check energy consumed and damage dealt."""
        final_energy = self.attacker.resources.get_value('energy')
        energy_consumed = self.initial_energy - final_energy
        damage_dealt = self.initial_hp - self.target.hp
        ticks_run = battle_engine.tick_counter

        self.results['test_id'] = self.metadata.test_id
        self.results['initial_energy'] = self.initial_energy
        self.results['final_energy'] = final_energy
        self.results['energy_consumed'] = energy_consumed
        self.results['shots_fired'] = int(energy_consumed)  # 1 energy per shot
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = ticks_run

        # Run validation rules
        if hasattr(self.metadata, 'validation_rules') and self.metadata.validation_rules:
            self.run_validation(battle_engine)

        # Evaluate pass criteria
        all_criteria_passed = all(
            criterion.evaluate(self.results)
            for criterion in self.pass_criteria
        )
        self.results['all_criteria_passed'] = all_criteria_passed

        return all_criteria_passed


class BeamEnergyDepletionScenario(TestScenario):
    """
    RESOURCE-005: Energy Depletion Stops Weapon

    Tests that beam weapon stops firing when energy is depleted.
    With 25 energy and 1 per shot, weapon fires 25 times then stops.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-005",
        category="Resource System",
        subcategory="Energy",
        name="Beam Energy Depletion",
        summary="Validates beam weapon stops firing when energy depletes",
        conditions=[
            f"Attacker: {RES005_SHIP_FILE}",
            "Target: Test_Target_Stationary.json",
            f"Energy Cost: {RES005_ENERGY_PER_SHOT} per shot",
            f"Initial Energy: {RES005_INITIAL_ENERGY} units",
            f"Maximum Shots: {RES005_EXPECTED_SHOTS}",
            "Distance: 10 pixels (point-blank)",
            f"Test Duration: {RES005_MAX_TICKS} ticks"
        ],
        edge_cases=[
            f"Weapon fires until energy < cost ({RES005_ENERGY_PER_SHOT})",
            f"Should fire exactly {RES005_EXPECTED_SHOTS} times",
            "No energy regeneration"
        ],
        expected_outcome=f"{RES005_EXPECTED_SHOTS} shots fired, energy = 0, weapon stops",
        pass_criteria=f"final_energy = 0, shots_fired = {RES005_EXPECTED_SHOTS}",
        max_ticks=RES005_MAX_TICKS,
        seed=42,
        battle_end_mode="time_based",
        ui_priority=9,
        tags=["resource", "energy", "depletion", "beam-weapons"],
        validation_rules=[
            DeterministicMatchRule(
                name='Final Energy',
                path='results.final_energy',
                expected=RES005_EXPECTED_FINAL_ENERGY,
                description='Energy fully depleted'
            ),
            DeterministicMatchRule(
                name='Shots Fired',
                path='results.shots_fired',
                expected=RES005_EXPECTED_SHOTS,
                description=f'{RES005_INITIAL_ENERGY} / {RES005_ENERGY_PER_SHOT} = {RES005_EXPECTED_SHOTS} shots'
            ),
        ]
    )

    data_expectations = [
        DataExpectation(
            name='Initial Energy',
            source='initial_energy',
            expected=RES005_INITIAL_ENERGY,
            json_file=RES005_SHIP_FILE
        ),
    ]

    pass_criteria = [
        PassCriterion(
            description='Energy Depleted (final_energy = 0)',
            expression=lambda r: r.get('final_energy', 1) == 0,
            numeric_threshold=0.0
        ),
        PassCriterion(
            description=f'Shots Fired = {RES005_EXPECTED_SHOTS}',
            expression=lambda r: r.get('shots_fired', 0) == RES005_EXPECTED_SHOTS,
            numeric_threshold=RES005_EXPECTED_SHOTS
        ),
    ]

    def setup(self, battle_engine):
        """Setup test scenario."""
        attacker = self._load_ship(RES005_SHIP_FILE)
        target = self._load_ship("Test_Target_Stationary.json")

        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0
        target.position = pygame.math.Vector2(10, 0)
        target.angle = 0

        self.initial_energy = attacker.resources.get_value('energy')
        self.initial_hp = target.hp

        end_condition = self._create_end_condition()

        battle_engine.start([attacker], [target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        attacker.current_target = target

        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check energy depleted and weapon stopped."""
        final_energy = self.attacker.resources.get_value('energy')
        energy_consumed = self.initial_energy - final_energy
        damage_dealt = self.initial_hp - self.target.hp
        ticks_run = battle_engine.tick_counter

        self.results['test_id'] = self.metadata.test_id
        self.results['initial_energy'] = self.initial_energy
        self.results['final_energy'] = final_energy
        self.results['energy_consumed'] = energy_consumed
        self.results['shots_fired'] = int(energy_consumed)
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = ticks_run

        # Run validation rules
        if hasattr(self.metadata, 'validation_rules') and self.metadata.validation_rules:
            self.run_validation(battle_engine)

        # Evaluate pass criteria
        all_criteria_passed = all(
            criterion.evaluate(self.results)
            for criterion in self.pass_criteria
        )
        self.results['all_criteria_passed'] = all_criteria_passed

        return all_criteria_passed


class BeamEnergyRegenerationScenario(TestScenario):
    """
    RESOURCE-005a: Energy Regeneration Sustains Weapon

    Tests that energy generator allows continuous firing. With 100/sec generation
    (1/tick) and 1 energy per shot, weapon fires continuously.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-005a",
        category="Resource System",
        subcategory="Energy",
        name="Energy Regeneration Sustains Weapon",
        summary="Validates energy generator allows continuous beam firing",
        conditions=[
            f"Attacker: {RES005A_SHIP_FILE}",
            "Target: Test_Target_Stationary.json",
            f"Energy Cost: {RES005A_ENERGY_PER_SHOT} per shot",
            f"Energy Generation: {RES005A_ENERGY_GENERATION_PER_SEC}/sec (1/tick)",
            "Net Rate: 0 (balanced)",
            f"Initial Energy: {RES005A_INITIAL_ENERGY} units",
            "Distance: 10 pixels (point-blank)",
            f"Test Duration: {RES005A_MAX_TICKS} ticks"
        ],
        edge_cases=[
            "Generator matches weapon consumption",
            f"Weapon should fire every tick ({RES005A_EXPECTED_SHOTS} shots)",
            "Energy should stay approximately stable"
        ],
        expected_outcome=f"{RES005A_EXPECTED_SHOTS} shots fired, energy stable, ~100 damage dealt",
        pass_criteria=f"shots_fired ≈ {RES005A_EXPECTED_SHOTS}, final_energy >= 0",
        max_ticks=RES005A_MAX_TICKS,
        seed=42,
        battle_end_mode="time_based",
        ui_priority=9,
        tags=["resource", "energy", "regeneration", "beam-weapons"],
        validation_rules=[
            DeterministicMatchRule(
                name='Shots Fired',
                path='results.shots_fired',
                expected=RES005A_EXPECTED_SHOTS,
                tolerance=5,  # Allow small variance
                description='Generator sustains continuous firing'
            ),
        ]
    )

    pass_criteria = [
        PassCriterion(
            description=f'Shots Fired ≈ {RES005A_EXPECTED_SHOTS}',
            expression=lambda r: abs(r.get('shots_fired', 0) - RES005A_EXPECTED_SHOTS) < 5,
            numeric_threshold=RES005A_EXPECTED_SHOTS
        ),
        PassCriterion(
            description='Energy Not Depleted',
            expression=lambda r: r.get('final_energy', -1) >= 0,
            numeric_threshold=0.0
        ),
    ]

    def setup(self, battle_engine):
        """Setup test scenario."""
        attacker = self._load_ship(RES005A_SHIP_FILE)
        target = self._load_ship("Test_Target_Stationary.json")

        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0
        target.position = pygame.math.Vector2(10, 0)
        target.angle = 0

        self.initial_energy = attacker.resources.get_value('energy')
        self.initial_hp = target.hp

        end_condition = self._create_end_condition()

        battle_engine.start([attacker], [target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        attacker.current_target = target

        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check weapon fires continuously with generator."""
        final_energy = self.attacker.resources.get_value('energy')
        damage_dealt = self.initial_hp - self.target.hp
        ticks_run = battle_engine.tick_counter

        # Estimate shots by damage (1 damage per hit at point-blank)
        estimated_shots = damage_dealt

        self.results['test_id'] = self.metadata.test_id
        self.results['initial_energy'] = self.initial_energy
        self.results['final_energy'] = final_energy
        self.results['energy_change'] = final_energy - self.initial_energy
        self.results['damage_dealt'] = damage_dealt
        self.results['shots_fired'] = estimated_shots
        self.results['ticks_run'] = ticks_run

        # Run validation rules
        if hasattr(self.metadata, 'validation_rules') and self.metadata.validation_rules:
            self.run_validation(battle_engine)

        # Evaluate pass criteria
        all_criteria_passed = all(
            criterion.evaluate(self.results)
            for criterion in self.pass_criteria
        )
        self.results['all_criteria_passed'] = all_criteria_passed

        return all_criteria_passed


# ============================================================================
# AMMO CONSUMPTION TESTS (PROJECTILE & SEEKER)
# ============================================================================

class ProjectileAmmoConsumptionScenario(TestScenario):
    """
    RESOURCE-006: Projectile Weapon Consumes Ammo

    Tests that projectile weapon consumes ammo per shot.
    With 1 ammo per shot, 0 reload, and 100,000 ammo, fires 100 times.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-006",
        category="Resource System",
        subcategory="Ammo",
        name="Projectile Ammo Consumption",
        summary="Validates projectile weapon consumes ammo per shot",
        conditions=[
            f"Attacker: {RES006_SHIP_FILE}",
            "Target: Test_Target_Stationary.json",
            f"Ammo Cost: {RES006_AMMO_PER_SHOT} per shot",
            f"Initial Ammo: {RES006_INITIAL_AMMO} units",
            "Weapon Reload: 0.0 (fires every tick)",
            "Distance: 50 pixels",
            f"Test Duration: {RES006_MAX_TICKS} ticks"
        ],
        edge_cases=[
            "Weapon fires every tick",
            "Fast projectile speed for near-instant hit",
            "High capacity storage - won't deplete"
        ],
        expected_outcome=f"{RES006_EXPECTED_SHOTS} shots fired, {RES006_EXPECTED_AMMO_CONSUMED} ammo consumed, final = {RES006_EXPECTED_FINAL_AMMO}",
        pass_criteria=f"ammo_consumed = {RES006_EXPECTED_AMMO_CONSUMED}, shots_fired = {RES006_EXPECTED_SHOTS}",
        max_ticks=RES006_MAX_TICKS,
        seed=42,
        battle_end_mode="time_based",
        ui_priority=8,
        tags=["resource", "ammo", "consumption", "projectile-weapons"],
        validation_rules=[
            DeterministicMatchRule(
                name='Ammo Consumed',
                path='results.ammo_consumed',
                expected=RES006_EXPECTED_AMMO_CONSUMED,
                tolerance=0.01,
                description=f'{RES006_EXPECTED_SHOTS} shots × {RES006_AMMO_PER_SHOT} ammo/shot'
            ),
            DeterministicMatchRule(
                name='Final Ammo',
                path='results.final_ammo',
                expected=RES006_EXPECTED_FINAL_AMMO,
                tolerance=0.01,
                description=f'{RES006_INITIAL_AMMO} - {RES006_EXPECTED_AMMO_CONSUMED} = {RES006_EXPECTED_FINAL_AMMO}'
            ),
        ]
    )

    data_expectations = [
        DataExpectation(
            name='Initial Ammo',
            source='initial_ammo',
            expected=RES006_INITIAL_AMMO,
            json_file=RES006_SHIP_FILE
        ),
    ]

    pass_criteria = [
        PassCriterion(
            description=f'Ammo Consumed = {RES006_EXPECTED_AMMO_CONSUMED}',
            expression=lambda r: abs(r.get('ammo_consumed', 0) - RES006_EXPECTED_AMMO_CONSUMED) < 0.01,
            numeric_threshold=RES006_EXPECTED_AMMO_CONSUMED
        ),
        PassCriterion(
            description=f'Shots Fired = {RES006_EXPECTED_SHOTS}',
            expression=lambda r: r.get('shots_fired', 0) == RES006_EXPECTED_SHOTS,
            numeric_threshold=RES006_EXPECTED_SHOTS
        ),
    ]

    def setup(self, battle_engine):
        """Setup test scenario."""
        attacker = self._load_ship(RES006_SHIP_FILE)
        target = self._load_ship("Test_Target_Stationary.json")

        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0
        target.position = pygame.math.Vector2(50, 0)
        target.angle = 0

        self.initial_ammo = attacker.resources.get_value('ammo')
        self.initial_hp = target.hp

        end_condition = self._create_end_condition()

        battle_engine.start([attacker], [target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        attacker.current_target = target

        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check ammo consumed."""
        final_ammo = self.attacker.resources.get_value('ammo')
        ammo_consumed = self.initial_ammo - final_ammo
        damage_dealt = self.initial_hp - self.target.hp
        ticks_run = battle_engine.tick_counter

        self.results['test_id'] = self.metadata.test_id
        self.results['initial_ammo'] = self.initial_ammo
        self.results['final_ammo'] = final_ammo
        self.results['ammo_consumed'] = ammo_consumed
        self.results['shots_fired'] = int(ammo_consumed)
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = ticks_run

        # Run validation rules
        if hasattr(self.metadata, 'validation_rules') and self.metadata.validation_rules:
            self.run_validation(battle_engine)

        # Evaluate pass criteria
        all_criteria_passed = all(
            criterion.evaluate(self.results)
            for criterion in self.pass_criteria
        )
        self.results['all_criteria_passed'] = all_criteria_passed

        return all_criteria_passed


class ProjectileAmmoDepletionScenario(TestScenario):
    """
    RESOURCE-007: Ammo Depletion Stops Projectile Weapon

    Tests that projectile weapon stops firing when ammo is depleted.
    With 10 ammo, fires 10 times then stops.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-007",
        category="Resource System",
        subcategory="Ammo",
        name="Projectile Ammo Depletion",
        summary="Validates projectile weapon stops when ammo depletes",
        conditions=[
            f"Attacker: {RES007_SHIP_FILE}",
            "Target: Test_Target_Stationary.json",
            f"Ammo Cost: {RES007_AMMO_PER_SHOT} per shot",
            f"Initial Ammo: {RES007_INITIAL_AMMO} units",
            f"Maximum Shots: {RES007_EXPECTED_SHOTS}",
            "Distance: 50 pixels",
            f"Test Duration: {RES007_MAX_TICKS} ticks"
        ],
        edge_cases=[
            "Weapon fires until ammo == 0",
            f"Should fire exactly {RES007_EXPECTED_SHOTS} times",
            "No ammo regeneration"
        ],
        expected_outcome=f"{RES007_EXPECTED_SHOTS} shots fired, ammo = 0, weapon stops",
        pass_criteria=f"final_ammo = 0, shots_fired = {RES007_EXPECTED_SHOTS}",
        max_ticks=RES007_MAX_TICKS,
        seed=42,
        battle_end_mode="time_based",
        ui_priority=8,
        tags=["resource", "ammo", "depletion", "projectile-weapons"],
        validation_rules=[
            DeterministicMatchRule(
                name='Final Ammo',
                path='results.final_ammo',
                expected=RES007_EXPECTED_FINAL_AMMO,
                description='Ammo fully depleted'
            ),
            DeterministicMatchRule(
                name='Shots Fired',
                path='results.shots_fired',
                expected=RES007_EXPECTED_SHOTS,
                description=f'{RES007_INITIAL_AMMO} / {RES007_AMMO_PER_SHOT} = {RES007_EXPECTED_SHOTS} shots'
            ),
        ]
    )

    data_expectations = [
        DataExpectation(
            name='Initial Ammo',
            source='initial_ammo',
            expected=RES007_INITIAL_AMMO,
            json_file=RES007_SHIP_FILE
        ),
    ]

    pass_criteria = [
        PassCriterion(
            description='Ammo Depleted (final_ammo = 0)',
            expression=lambda r: r.get('final_ammo', 1) == 0,
            numeric_threshold=0.0
        ),
        PassCriterion(
            description=f'Shots Fired = {RES007_EXPECTED_SHOTS}',
            expression=lambda r: r.get('shots_fired', 0) == RES007_EXPECTED_SHOTS,
            numeric_threshold=RES007_EXPECTED_SHOTS
        ),
    ]

    def setup(self, battle_engine):
        """Setup test scenario."""
        attacker = self._load_ship(RES007_SHIP_FILE)
        target = self._load_ship("Test_Target_Stationary.json")

        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0
        target.position = pygame.math.Vector2(50, 0)
        target.angle = 0

        self.initial_ammo = attacker.resources.get_value('ammo')
        self.initial_hp = target.hp

        end_condition = self._create_end_condition()

        battle_engine.start([attacker], [target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        attacker.current_target = target

        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check ammo depleted and weapon stopped."""
        final_ammo = self.attacker.resources.get_value('ammo')
        ammo_consumed = self.initial_ammo - final_ammo
        damage_dealt = self.initial_hp - self.target.hp
        ticks_run = battle_engine.tick_counter

        self.results['test_id'] = self.metadata.test_id
        self.results['initial_ammo'] = self.initial_ammo
        self.results['final_ammo'] = final_ammo
        self.results['ammo_consumed'] = ammo_consumed
        self.results['shots_fired'] = int(ammo_consumed)
        self.results['damage_dealt'] = damage_dealt
        self.results['ticks_run'] = ticks_run

        # Run validation rules
        if hasattr(self.metadata, 'validation_rules') and self.metadata.validation_rules:
            self.run_validation(battle_engine)

        # Evaluate pass criteria
        all_criteria_passed = all(
            criterion.evaluate(self.results)
            for criterion in self.pass_criteria
        )
        self.results['all_criteria_passed'] = all_criteria_passed

        return all_criteria_passed


class SeekerAmmoConsumptionScenario(TestScenario):
    """
    RESOURCE-008: Seeker Weapon Consumes Ammo

    Tests that seeker weapon consumes ammo per launch.
    With 1 ammo per launch, 0 reload, and 100,000 ammo, launches 100 seekers.
    Note: Verifies launches and ammo only, NOT hits (seekers take time to reach target).
    """

    metadata = TestMetadata(
        test_id="RESOURCE-008",
        category="Resource System",
        subcategory="Ammo",
        name="Seeker Ammo Consumption",
        summary="Validates seeker weapon consumes ammo per launch",
        conditions=[
            f"Attacker: {RES008_SHIP_FILE}",
            "Target: Test_Target_Stationary.json",
            f"Ammo Cost: {RES008_AMMO_PER_LAUNCH} per launch",
            f"Initial Ammo: {RES008_INITIAL_AMMO} units",
            "Weapon Reload: 0.0 (launches every tick)",
            "Distance: 500 pixels (seekers in flight)",
            f"Test Duration: {RES008_MAX_TICKS} ticks"
        ],
        edge_cases=[
            "Launches every tick",
            "Seekers take time to reach target",
            "Verify launches/ammo, NOT hits"
        ],
        expected_outcome=f"{RES008_EXPECTED_LAUNCHES} launches, {RES008_EXPECTED_AMMO_CONSUMED} ammo consumed (hits not verified)",
        pass_criteria=f"ammo_consumed = {RES008_EXPECTED_AMMO_CONSUMED}, launches = {RES008_EXPECTED_LAUNCHES}",
        max_ticks=RES008_MAX_TICKS,
        seed=42,
        battle_end_mode="time_based",
        ui_priority=7,
        tags=["resource", "ammo", "consumption", "seeker-weapons", "missiles"],
        validation_rules=[
            DeterministicMatchRule(
                name='Ammo Consumed',
                path='results.ammo_consumed',
                expected=RES008_EXPECTED_AMMO_CONSUMED,
                tolerance=0.01,
                description=f'{RES008_EXPECTED_LAUNCHES} launches × {RES008_AMMO_PER_LAUNCH} ammo/launch'
            ),
            DeterministicMatchRule(
                name='Final Ammo',
                path='results.final_ammo',
                expected=RES008_EXPECTED_FINAL_AMMO,
                tolerance=0.01,
                description=f'{RES008_INITIAL_AMMO} - {RES008_EXPECTED_AMMO_CONSUMED} = {RES008_EXPECTED_FINAL_AMMO}'
            ),
        ]
    )

    data_expectations = [
        DataExpectation(
            name='Initial Ammo',
            source='initial_ammo',
            expected=RES008_INITIAL_AMMO,
            json_file=RES008_SHIP_FILE
        ),
    ]

    pass_criteria = [
        PassCriterion(
            description=f'Ammo Consumed = {RES008_EXPECTED_AMMO_CONSUMED}',
            expression=lambda r: abs(r.get('ammo_consumed', 0) - RES008_EXPECTED_AMMO_CONSUMED) < 0.01,
            numeric_threshold=RES008_EXPECTED_AMMO_CONSUMED
        ),
        PassCriterion(
            description=f'Launches = {RES008_EXPECTED_LAUNCHES}',
            expression=lambda r: r.get('launches', 0) == RES008_EXPECTED_LAUNCHES,
            numeric_threshold=RES008_EXPECTED_LAUNCHES
        ),
    ]

    def setup(self, battle_engine):
        """Setup test scenario."""
        attacker = self._load_ship(RES008_SHIP_FILE)
        target = self._load_ship("Test_Target_Stationary.json")

        attacker.position = pygame.math.Vector2(0, 0)
        attacker.angle = 0
        target.position = pygame.math.Vector2(500, 0)  # Far enough for seekers in flight
        target.angle = 0

        self.initial_ammo = attacker.resources.get_value('ammo')

        end_condition = self._create_end_condition()

        battle_engine.start([attacker], [target],
                          seed=self.metadata.seed,
                          end_condition=end_condition)

        attacker.current_target = target

        self.attacker = attacker
        self.target = target

    def update(self, battle_engine):
        """Force attacker to fire each tick."""
        if self.attacker and self.attacker.is_alive:
            self.attacker.comp_trigger_pulled = True

    def verify(self, battle_engine) -> bool:
        """Check ammo consumed (launches, not hits)."""
        final_ammo = self.attacker.resources.get_value('ammo')
        ammo_consumed = self.initial_ammo - final_ammo
        ticks_run = battle_engine.tick_counter

        self.results['test_id'] = self.metadata.test_id
        self.results['initial_ammo'] = self.initial_ammo
        self.results['final_ammo'] = final_ammo
        self.results['ammo_consumed'] = ammo_consumed
        self.results['launches'] = int(ammo_consumed)  # 1 ammo per launch
        self.results['ticks_run'] = ticks_run
        # Note: damage_dealt not verified for seekers (still in flight)

        # Run validation rules
        if hasattr(self.metadata, 'validation_rules') and self.metadata.validation_rules:
            self.run_validation(battle_engine)

        # Evaluate pass criteria
        all_criteria_passed = all(
            criterion.evaluate(self.results)
            for criterion in self.pass_criteria
        )
        self.results['all_criteria_passed'] = all_criteria_passed

        return all_criteria_passed


# ============================================================================
# EXPORT ALL SCENARIOS
# ============================================================================

__all__ = [
    # Fuel tests
    'EngineFuelConsumptionScenario',
    'EngineFuelDepletionScenario',
    'EngineFuelRegenerationScenario',
    # Energy tests
    'BeamEnergyConsumptionScenario',
    'BeamEnergyDepletionScenario',
    'BeamEnergyRegenerationScenario',
    # Ammo tests
    'ProjectileAmmoConsumptionScenario',
    'ProjectileAmmoDepletionScenario',
    'SeekerAmmoConsumptionScenario'
]
