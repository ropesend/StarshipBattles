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

from game.simulation.physics_constants import K_SPEED
from combat_lab.scenarios import TestMetadata
from combat_lab.scenarios.templates import ComparisonScenario, ResourceScenario
from combat_lab.scenarios.validation import check_exact, check_approx, check_true


# =============================================================================
# EXPECTED VALUES FOR RESOURCE TESTS
# =============================================================================
# These values MUST match the actual .json ship/component data files.
# If a mismatch is detected, the test will be blocked from running.
#
# Data source: combat_lab/data/ships/*.json
#              combat_lab/data/components.json
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

# -----------------------------------------------------------------------------
# RESOURCE-009: Energy Contention — Beam + Shield Regen Share Pool
# Baseline: Beam (1 energy/shot) + 100k battery → fires all 500 ticks
# Variant: Beam (1 energy/shot) + regen (5 energy/sec) + 250 battery
#   Total consumption: 100/sec (beam) + 5/sec (regen) = 105/sec = 1.05/tick
#   Battery depletes at ~tick 238. Beam stops firing.
# Expected: variant fires fewer shots than baseline
# -----------------------------------------------------------------------------
RES009_BASELINE_SHIP = "Test_Attacker_BeamEnergy_HighBattery.json"
RES009_VARIANT_SHIP = "Test_Attacker_BeamEnergy_Regen_LimitedBattery.json"
RES009_MAX_TICKS = 500
RES009_VARIANT_BATTERY = 250.0
RES009_BEAM_ENERGY_PER_TICK = 1.0     # 1 energy per shot, fires every tick
RES009_REGEN_ENERGY_PER_SEC = 5.0     # constant drain
RES009_TOTAL_ENERGY_PER_SEC = 100.0 + RES009_REGEN_ENERGY_PER_SEC  # 105/sec


# ============================================================================
# FUEL CONSUMPTION TESTS
# ============================================================================

class EngineFuelConsumptionScenario(ResourceScenario):
    """
    RESOURCE-001: Engine Consumes Fuel

    Tests that engine fuel consumption rate is predictable. With 1.0 fuel/sec
    consumption and 1000 fuel capacity, running for 500 ticks (5 seconds)
    should consume exactly 5.0 fuel.
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
        ui_priority=10,
        tags=["resource", "fuel", "consumption", "engine"],
    )

    ship_file = RES001_SHIP_FILE
    resource_type = "fuel"
    thrust_forward = True

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Ship Mass", RES001_HULL_MASS, self.ship.mass))
        checks.append(check_exact("Initial Fuel", RES001_INITIAL_FUEL, self.initial_value))
        checks.append(check_exact("Engine Thrust", RES001_ENGINE_THRUST, self.ship.total_thrust))
        # Precondition
        checks.append(check_true("Ship Moved", self.final_velocity > 0, actual=self.final_velocity))
        # Outcome
        checks.append(check_approx("Final Fuel", RES001_EXPECTED_FINAL_FUEL, self.final_value, tolerance=0.01))
        checks.append(check_approx("Fuel Consumed", RES001_EXPECTED_FUEL_CONSUMED, self.value_consumed, tolerance=0.01))
        return checks


class EngineFuelDepletionScenario(ResourceScenario):
    """
    RESOURCE-002: Engine Starvation Stops Movement

    Tests that engine stops providing thrust when fuel is depleted.
    With 2.5 fuel and 1.0 fuel/sec consumption, engine runs out at tick ~250.
    Ship should decelerate to 0 velocity by end of test.

    NOTE: This test currently FAILS because the engine does not stop when
    fuel is depleted -- this is a real game bug, not a test bug.
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
        ui_priority=10,
        tags=["resource", "fuel", "depletion", "starvation", "engine"],
    )

    ship_file = RES002_SHIP_FILE
    resource_type = "fuel"
    thrust_forward = True

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Ship Mass", RES001_HULL_MASS, self.ship.mass))
        checks.append(check_exact("Initial Fuel", RES002_INITIAL_FUEL, self.initial_value))
        # Precondition
        checks.append(check_true("Ship Moved", self.distance_traveled > 0, actual=self.distance_traveled))
        # Outcome
        checks.append(check_approx("Fuel Depleted", RES002_EXPECTED_FINAL_FUEL, self.final_value, tolerance=0.01, phase="outcome"))
        checks.append(check_true("Ship Stopped", self.final_velocity < 0.01,
                                 actual=self.final_velocity, phase="outcome"))
        return checks


class EngineFuelRegenerationScenario(ResourceScenario):
    """
    RESOURCE-003: Fuel Generation Sustains Movement

    Tests that fuel generator keeps engine running. With 1.0 fuel/sec consumption
    and 1.0 fuel/sec generation, fuel should stay stable and ship keeps moving.

    NOTE: This test currently FAILS because the generator is not working.
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
        ui_priority=10,
        tags=["resource", "fuel", "regeneration", "engine"],
    )

    ship_file = RES003_SHIP_FILE
    resource_type = "fuel"
    thrust_forward = True

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        fuel_change = self.final_value - self.initial_value
        # Data
        checks.append(check_exact("Ship Mass", RES001_HULL_MASS, self.ship.mass))
        checks.append(check_exact("Initial Fuel", RES003_INITIAL_FUEL, self.initial_value))
        checks.append(check_exact("Engine Thrust", RES001_ENGINE_THRUST, self.ship.total_thrust))
        # Outcome
        checks.append(check_true("Fuel Stable", abs(fuel_change) < 0.5,
                                 actual=fuel_change, phase="outcome",
                                 detail=f"fuel_change={fuel_change:.4f}, threshold=0.5"))
        checks.append(check_true("Ship Moving", self.final_velocity > 0,
                                 actual=self.final_velocity, phase="outcome"))
        return checks


# ============================================================================
# ENERGY CONSUMPTION TESTS (BEAM WEAPONS)
# ============================================================================

class BeamEnergyConsumptionScenario(ResourceScenario):
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
        ui_priority=9,
        tags=["resource", "energy", "consumption", "beam-weapons"],
    )

    ship_file = RES004_SHIP_FILE
    resource_type = "energy"
    force_fire = True
    target_ship_file = "Test_Target_Stationary.json"
    target_distance = 10

    def _collect_extra_results(self, outcome, telemetry=None):
        """Store shots_fired derived from energy consumed."""
        self.shots_fired = int(self.value_consumed)  # 1 energy per shot
        self.results['shots_fired'] = self.shots_fired

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Initial Energy", RES004_INITIAL_ENERGY, self.initial_value))
        # Outcome
        checks.append(check_approx("Energy Consumed", RES004_EXPECTED_ENERGY_CONSUMED, self.value_consumed, tolerance=0.01))
        checks.append(check_exact("Shots Fired", RES004_EXPECTED_SHOTS, self.shots_fired, phase="outcome"))
        return checks


class BeamEnergyDepletionScenario(ResourceScenario):
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
        ui_priority=9,
        tags=["resource", "energy", "depletion", "beam-weapons"],
    )

    ship_file = RES005_SHIP_FILE
    resource_type = "energy"
    force_fire = True
    target_ship_file = "Test_Target_Stationary.json"
    target_distance = 10

    def _collect_extra_results(self, outcome, telemetry=None):
        """Store shots_fired derived from energy consumed."""
        self.shots_fired = int(self.value_consumed)
        self.results['shots_fired'] = self.shots_fired

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Initial Energy", RES005_INITIAL_ENERGY, self.initial_value))
        # Outcome
        checks.append(check_exact("Energy Depleted", RES005_EXPECTED_FINAL_ENERGY, self.final_value, phase="outcome"))
        checks.append(check_exact("Shots Fired", RES005_EXPECTED_SHOTS, self.shots_fired, phase="outcome"))
        return checks


class BeamEnergyRegenerationScenario(ResourceScenario):
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
        ui_priority=9,
        tags=["resource", "energy", "regeneration", "beam-weapons"],
    )

    ship_file = RES005A_SHIP_FILE
    resource_type = "energy"
    force_fire = True
    target_ship_file = "Test_Target_Stationary.json"
    target_distance = 10

    def _collect_extra_results(self, outcome, telemetry=None):
        """Estimate shots by damage (1 damage per hit at point-blank)."""
        self.shots_fired = self.damage_dealt
        self.results['shots_fired'] = self.shots_fired
        self.results['energy_change'] = self.final_value - self.initial_value

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Initial Energy", RES005A_INITIAL_ENERGY, self.initial_value))
        # Outcome
        checks.append(check_true("Shots Fired Near Expected",
                                 abs(self.shots_fired - RES005A_EXPECTED_SHOTS) < 5,
                                 actual=self.shots_fired, phase="outcome",
                                 detail=f"expected~{RES005A_EXPECTED_SHOTS}, tolerance=5"))
        checks.append(check_true("Energy Not Depleted", self.final_value >= 0,
                                 actual=self.final_value, phase="outcome"))
        return checks


# ============================================================================
# AMMO CONSUMPTION TESTS (PROJECTILE & SEEKER)
# ============================================================================

class ProjectileAmmoConsumptionScenario(ResourceScenario):
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
        ui_priority=8,
        tags=["resource", "ammo", "consumption", "projectile-weapons"],
    )

    ship_file = RES006_SHIP_FILE
    resource_type = "ammo"
    force_fire = True
    target_ship_file = "Test_Target_Stationary.json"
    target_distance = 50

    def _collect_extra_results(self, outcome, telemetry=None):
        """Store shots_fired derived from ammo consumed."""
        self.shots_fired = int(self.value_consumed)
        self.results['shots_fired'] = self.shots_fired

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Initial Ammo", RES006_INITIAL_AMMO, self.initial_value))
        # Outcome
        checks.append(check_approx("Ammo Consumed", RES006_EXPECTED_AMMO_CONSUMED, self.value_consumed, tolerance=0.01))
        checks.append(check_exact("Shots Fired", RES006_EXPECTED_SHOTS, self.shots_fired, phase="outcome"))
        return checks


class ProjectileAmmoDepletionScenario(ResourceScenario):
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
        ui_priority=8,
        tags=["resource", "ammo", "depletion", "projectile-weapons"],
    )

    ship_file = RES007_SHIP_FILE
    resource_type = "ammo"
    force_fire = True
    target_ship_file = "Test_Target_Stationary.json"
    target_distance = 50

    def _collect_extra_results(self, outcome, telemetry=None):
        """Store shots_fired derived from ammo consumed."""
        self.shots_fired = int(self.value_consumed)
        self.results['shots_fired'] = self.shots_fired

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Initial Ammo", RES007_INITIAL_AMMO, self.initial_value))
        # Outcome
        checks.append(check_exact("Ammo Depleted", RES007_EXPECTED_FINAL_AMMO, self.final_value, phase="outcome"))
        checks.append(check_exact("Shots Fired", RES007_EXPECTED_SHOTS, self.shots_fired, phase="outcome"))
        return checks


class SeekerAmmoConsumptionScenario(ResourceScenario):
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
        ui_priority=7,
        tags=["resource", "ammo", "consumption", "seeker-weapons", "missiles"],
    )

    ship_file = RES008_SHIP_FILE
    resource_type = "ammo"
    force_fire = True
    target_ship_file = "Test_Target_Stationary.json"
    target_distance = 500

    def _collect_extra_results(self, outcome, telemetry=None):
        """Store launches derived from ammo consumed."""
        self.launches = int(self.value_consumed)  # 1 ammo per launch
        self.results['launches'] = self.launches

    def validate(self, outcome, telemetry=None) -> list:
        checks = self._template_preconditions()
        # Data
        checks.append(check_exact("Initial Ammo", RES008_INITIAL_AMMO, self.initial_value))
        # Outcome
        checks.append(check_approx("Ammo Consumed", RES008_EXPECTED_AMMO_CONSUMED, self.value_consumed, tolerance=0.01))
        checks.append(check_exact("Launches", RES008_EXPECTED_LAUNCHES, self.launches, phase="outcome"))
        return checks


# ============================================================================
# RESOURCE CONTENTION TESTS
# ============================================================================

class EnergyContentionBeamRegenScenario(ComparisonScenario):
    """
    RESOURCE-009: Shield Regen + Beam Both Consume Energy From Same Pool

    Battle A: Beam (1 energy/shot, fires every tick) + 100k battery → fires all 500 ticks
    Battle B: Beam (1 energy/shot) + shield regen (5 energy/sec) + 250 battery
              Total: 105 energy/sec. Battery depletes at ~tick 238. Beam stops.

    When energy runs out, BOTH systems stop. The variant fires fewer shots because
    the shield regen competes for the same energy pool, depleting it faster.
    """

    metadata = TestMetadata(
        test_id="RESOURCE-009",
        category="Resource System",
        subcategory="Contention",
        name="Energy Contention — Beam + Shield Regen Share Pool",
        summary="Beam and shield regen competing for limited energy causes earlier weapon shutdown",
        conditions=[
            f"Baseline: {RES009_BASELINE_SHIP} (beam + 100k battery, fires all {RES009_MAX_TICKS} ticks)",
            f"Variant: {RES009_VARIANT_SHIP} (beam + regen + {RES009_VARIANT_BATTERY} battery)",
            f"Beam: 1 energy/shot (activation trigger), fires every tick = 100 energy/sec",
            f"Regen: {RES009_REGEN_ENERGY_PER_SEC} energy/sec (constant drain)",
            f"Total variant drain: {RES009_TOTAL_ENERGY_PER_SEC} energy/sec",
            "Target: Test_Target_Stationary.json (stationary, extreme HP)",
            f"Distance: 100 pixels (point blank)",
            f"Test Duration: {RES009_MAX_TICKS} ticks",
        ],
        edge_cases=[
            "Two systems (beam + regen) share the same energy pool",
            "Constant drain (regen) + activation drain (beam) deplete pool faster",
            "After energy depletes, beam cannot fire (activation cost check fails)",
        ],
        expected_outcome="Variant fires fewer shots than baseline because energy is shared "
                         "with shield regen and depletes early.",
        pass_criteria="variant_damage_dealt < baseline_damage_dealt, both > 0",
        max_ticks=RES009_MAX_TICKS,
        seed=42,
        tags=["resource", "energy", "contention", "beam", "shield-regen", "comparison"],
    )

    baseline_attacker_ship = RES009_BASELINE_SHIP
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = RES009_VARIANT_SHIP
    variant_target_ship = "Test_Target_Stationary.json"
    distance = 100

    def validate(self, ab) -> list:
        checks = self._template_preconditions()

        # Precondition: baseline fired all ticks (plenty of energy)
        baseline_shots = self.results.get('baseline_attacker_total_shots_fired', 0)
        checks.append(check_true(
            "Baseline Fired Extensively",
            baseline_shots >= RES009_MAX_TICKS * 0.9,
            detail=f"baseline_shots={baseline_shots}, expected~={RES009_MAX_TICKS}",
        ))

        # Precondition: variant also fired (had some energy)
        variant_shots = self.results.get('variant_attacker_total_shots_fired', 0)
        checks.append(check_true(
            "Variant Fired Some Shots",
            variant_shots > 0,
            detail=f"variant_shots={variant_shots}",
        ))

        # Precondition: variant energy depleted
        variant_energy = self.attacker.resources.get_resource("energy")
        checks.append(check_true(
            "Variant Energy Depleted",
            variant_energy is not None and variant_energy.current_value < 1.0,
            detail=f"energy={variant_energy.current_value if variant_energy else 'N/A'}",
        ))

        # Outcome: variant fired fewer shots (energy contention)
        checks.append(check_true(
            "Contention Reduced Shots Fired",
            variant_shots < baseline_shots,
            detail=f"variant={variant_shots}, baseline={baseline_shots}, "
                   f"reduction={baseline_shots - variant_shots}",
            phase="outcome",
        ))

        # Outcome: variant dealt less damage
        checks.append(check_true(
            "Contention Reduced Damage",
            self.variant_damage_dealt < self.baseline_damage_dealt,
            detail=f"variant_dmg={self.variant_damage_dealt}, baseline_dmg={self.baseline_damage_dealt}",
            phase="outcome",
        ))

        return checks


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
    'SeekerAmmoConsumptionScenario',
    # Contention tests
    'EnergyContentionBeamRegenScenario',
]
