"""
Combat Lab Test Constants

Centralized constants used across test scenarios to eliminate magic numbers
and improve maintainability. Update these values in one place to affect all tests.
"""

# ============================================================================
# TEST DURATIONS
# ============================================================================

# Standard test duration for most scenarios
STANDARD_TEST_TICKS = 500

# High-precision test duration for statistical validation
HIGH_TICK_TEST_TICKS = 100000


# ============================================================================
# TEST DISTANCES (pixels)
# ============================================================================

# Point-blank range (minimal range penalty, must exceed ship radii to avoid overlap)
POINT_BLANK_DISTANCE = 100

# Mid-range distance (moderate range penalty)
MID_RANGE_DISTANCE = 400

# Standard test distance (default for many tests)
STANDARD_DISTANCE = 500

# Maximum effective range for most weapons
MAX_RANGE_DISTANCE = 800

# Near max-range distance for beam accuracy tests (within 800px weapon range)
NEAR_MAX_RANGE_DISTANCE = 750

# Seeker tracking test distance
SEEKER_TRACKING_DISTANCE = 1000

# Beyond-weapon-range distances for out-of-range tests
BEAM_OUT_OF_RANGE_DISTANCE = 900
PROJECTILE_OUT_OF_RANGE_DISTANCE = 1200


# ============================================================================
# BEAM WEAPON CONFIGURATIONS
# ============================================================================

# Low accuracy beam weapon
BEAM_LOW_ACCURACY = 0.5
BEAM_LOW_FALLOFF = 0.002
BEAM_LOW_RANGE = 800
BEAM_LOW_DAMAGE = 1

# Medium accuracy beam weapon
BEAM_MED_ACCURACY = 2.0
BEAM_MED_FALLOFF = 0.001
BEAM_MED_RANGE = 800
BEAM_MED_DAMAGE = 1

# High accuracy beam weapon
BEAM_HIGH_ACCURACY = 5.0
BEAM_HIGH_FALLOFF = 0.0005
BEAM_HIGH_RANGE = 800
BEAM_HIGH_DAMAGE = 1


# ============================================================================
# SHIP CONFIGURATIONS
# ============================================================================

# Standard stationary target
STATIONARY_TARGET_MASS = 400.0


# ============================================================================
# STATISTICAL VALIDATION MARGINS
# ============================================================================

# Standard margin for 500-tick tests (±10% = ~2.7x SE for p≈0.5, ~95%+ pass rate)
# The 6% margin was unreliable (~45% failure rate) for low-accuracy tests near 50% hit rate.
# High-tick tests (100k ticks, ±1%) provide precise validation.
STANDARD_MARGIN = 0.10

# High precision margin for 100k-tick tests (±1% = 99.99% confidence)
HIGH_PRECISION_MARGIN = 0.01


# ============================================================================
# DEFENSE ABILITY CONSTANTS
# ============================================================================

# Shield configuration
SHIELD_CAPACITY = 200       # HP from test_shield_200 component
SHIELD_REGEN_RATE = 10      # HP/sec from test_shield_regen_10 component

# Emissive armor
EMISSIVE_ARMOR_REDUCTION = 5  # Flat damage reduction per hit

# To-hit modifiers
ECM_DEFENSE_VALUE = 1.0     # Defense score bonus from test_ecm_1
SENSOR_ATTACK_VALUE = 1.0   # Attack score bonus from test_sensor_1
TOHIT_PENALTY_VALUE = -0.5  # Negative attack modifier from test_tohit_penalty
ECM_PENALTY_VALUE = -0.5    # Negative defense modifier from test_ecm_penalty

# Defense test ship filenames
SHIELDED_TARGET_SHIP = "Test_Target_Shielded.json"
SHIELD_REGEN_TARGET_SHIP = "Test_Target_Shield_Regen.json"
EMISSIVE_ARMOR_TARGET_SHIP = "Test_Target_EmissiveArmor.json"
ECM_TARGET_SHIP = "Test_Target_ECM.json"
SENSOR_ATTACKER_SHIP = "Test_Attacker_Beam360_WithSensor.json"

# Defense test durations
DEFENSE_TEST_TICKS = 500    # Standard duration for defense tests

# ShieldProjection test category
SHIELD_PROJ_1B_CAPACITY = 1_000_000_000
SHIELD_PROJ_100_CAPACITY = 100
SHIELD_PROJ_SINGLE_SHOT_DAMAGE = 150
SHIELD_PROJ_TEST_TICKS = 1000        # Tests 001-003 (guaranteed-hit beam, 1 dmg/tick)
SHIELD_PROJ_SINGLE_SHOT_TICKS = 100  # Test 004 (single 150-dmg shot)
SHIELD_PROJ_ENERGY_RATE = 1.0        # Energy consumption per second for energy shield
SHIELD_PROJ_LARGE_BATTERY = 15       # Energy: lasts 1500 ticks (> test duration)
SHIELD_PROJ_SMALL_BATTERY = 5        # Energy: lasts 500 ticks (depletes mid-test)


# ============================================================================
# MODIFIER TEST CONSTANTS
# ============================================================================

# Modifier test ship filenames
DAMAGE_BOOST_ATTACKER_SHIP = "Test_Attacker_Beam_DamageBoost.json"
RANGE_BOOST_ATTACKER_SHIP = "Test_Attacker_Beam_RangeBoost.json"
TURRET180_ATTACKER_SHIP = "Test_Attacker_Beam_Turret180.json"
THRUST_BOOST_ENGINE_SHIP = "Test_Engine_ThrustBoost.json"

# Modifier parameter values (as applied in ship JSONs)
DAMAGE_BOOST_PARAM = 1.5       # test_damage_boost value
RANGE_BOOST_PARAM = 1          # test_range_boost value (2^1 = 2x range)
TURRET_ARC_PARAM = 180         # test_turret value (180 degree arc)
THRUST_BOOST_PARAM = 2         # test_thrust_boost value (2x thrust)

# Base weapon stats (from test_beam_med_acc_1dmg)
MOD_BASE_BEAM_DAMAGE = 1
MOD_BASE_BEAM_RANGE = 800
MOD_BASE_BEAM_ARC = 360
MOD_BASE_BEAM_ACCURACY = 2.0

# Base engine stats (from test_engine_no_fuel)
MOD_BASE_ENGINE_THRUST = 500

# Expected post-modifier values
MOD_EXPECTED_DAMAGE = MOD_BASE_BEAM_DAMAGE * DAMAGE_BOOST_PARAM          # 1.5
MOD_EXPECTED_RANGE = MOD_BASE_BEAM_RANGE * (2 ** RANGE_BOOST_PARAM)      # 1600
MOD_EXPECTED_ARC = TURRET_ARC_PARAM                                       # 180
MOD_EXPECTED_THRUST = MOD_BASE_ENGINE_THRUST * THRUST_BOOST_PARAM         # 1000

# Modifier test durations
MODIFIER_TEST_TICKS = 500


# ============================================================================
# SEED VALUES
# ============================================================================

# Standard seed for reproducible tests
STANDARD_SEED = 42

