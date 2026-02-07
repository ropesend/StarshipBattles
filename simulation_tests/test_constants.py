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

# Special durations for specific test types
RESOURCE_TEST_TICKS = 600  # Allow 1+ weapon reloads
RESOURCE_DEPLETION_TICKS = 1000  # ~10 seconds for full depletion


# ============================================================================
# TEST DISTANCES (pixels)
# ============================================================================

# Point-blank range (minimal range penalty)
POINT_BLANK_DISTANCE = 50

# Mid-range distance (moderate range penalty)
MID_RANGE_DISTANCE = 400

# Standard test distance (default for many tests)
STANDARD_DISTANCE = 500

# Maximum effective range for most weapons
MAX_RANGE_DISTANCE = 800

# Long range (beyond most weapon ranges)
LONG_RANGE_DISTANCE = 3000


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
BEAM_MED_RANGE = 1000
BEAM_MED_DAMAGE = 1

# High accuracy beam weapon
BEAM_HIGH_ACCURACY = 5.0
BEAM_HIGH_FALLOFF = 0.0005
BEAM_HIGH_RANGE = 1200
BEAM_HIGH_DAMAGE = 1


# ============================================================================
# PROJECTILE WEAPON CONFIGURATIONS
# ============================================================================

PROJECTILE_DAMAGE = 10
PROJECTILE_RANGE = 800
PROJECTILE_SPEED = 300


# ============================================================================
# SEEKER/MISSILE WEAPON CONFIGURATIONS
# ============================================================================

SEEKER_DAMAGE = 50
SEEKER_RANGE = 2000
SEEKER_SPEED = 200
SEEKER_TURN_RATE = 3.0
SEEKER_RELOAD_TIME = 5.0  # seconds


# ============================================================================
# SHIP CONFIGURATIONS
# ============================================================================

# Standard stationary target
STATIONARY_TARGET_MASS = 400.0
STATIONARY_TARGET_HP = 1000

# Small erratic target (testing defense/evasion)
SMALL_ERRATIC_TARGET_MASS = 50.0
SMALL_ERRATIC_TARGET_HP = 500

# Large target (easier to hit)
LARGE_TARGET_MASS = 8000.0
LARGE_TARGET_HP = 2000

# High-tick test special targets
HIGH_TICK_TARGET_HP = 60000  # Survives 100k ticks for statistical tests


# ============================================================================
# STATISTICAL VALIDATION MARGINS
# ============================================================================

# Standard margin for 500-tick tests (±6% = 99% confidence, ~1% failure rate)
STANDARD_MARGIN = 0.06

# High precision margin for 100k-tick tests (±1% = 99.99% confidence)
HIGH_PRECISION_MARGIN = 0.01

# Medium precision margin
MEDIUM_MARGIN = 0.04

# Relaxed margin for complex scenarios
RELAXED_MARGIN = 0.10


# ============================================================================
# CALCULATED CONSTANTS
# ============================================================================

def calculate_target_radius(mass: float) -> float:
    """
    Calculate target radius from mass.

    Formula: radius = 40 * (mass / 1000)^(1/3)

    Args:
        mass: Ship mass in kg

    Returns:
        Radius in pixels
    """
    return 40 * ((mass / 1000) ** (1/3))


def calculate_surface_distance(center_distance: float, target_mass: float) -> float:
    """
    Calculate surface-to-center distance for range penalty calculations.

    Args:
        center_distance: Distance from attacker center to target center
        target_mass: Target mass (used to calculate radius)

    Returns:
        Distance from attacker to target surface
    """
    target_radius = calculate_target_radius(target_mass)
    return center_distance - target_radius


# Standard radius calculations (for reference in test metadata)
STATIONARY_TARGET_RADIUS = calculate_target_radius(STATIONARY_TARGET_MASS)  # ~29.47 pixels
SMALL_ERRATIC_TARGET_RADIUS = calculate_target_radius(SMALL_ERRATIC_TARGET_MASS)  # ~14.72 pixels
LARGE_TARGET_RADIUS = calculate_target_radius(LARGE_TARGET_MASS)  # ~80 pixels


# ============================================================================
# RESOURCE CONSUMPTION CONSTANTS
# ============================================================================

# Energy consumption per weapon fire
BEAM_ENERGY_COST = 10
PROJECTILE_ENERGY_COST = 5
SEEKER_ENERGY_COST = 50

# Ammo consumption per weapon fire
PROJECTILE_AMMO_COST = 1
SEEKER_AMMO_COST = 1

# Starting resource amounts
STANDARD_ENERGY = 1000
STANDARD_AMMO = 100
LIMITED_AMMO = 10


# ============================================================================
# PROPULSION CONSTANTS
# ============================================================================

# Standard propulsion values
STANDARD_ACCELERATION = 50.0
STANDARD_TURN_SPEED = 2.0
HIGH_ACCELERATION = 100.0
HIGH_TURN_SPEED = 4.0


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

# Defense test ship filenames
SHIELDED_TARGET_SHIP = "Test_Target_Shielded.json"
SHIELD_REGEN_TARGET_SHIP = "Test_Target_Shield_Regen.json"
EMISSIVE_ARMOR_TARGET_SHIP = "Test_Target_EmissiveArmor.json"
ECM_TARGET_SHIP = "Test_Target_ECM.json"
SENSOR_ATTACKER_SHIP = "Test_Attacker_Beam360_WithSensor.json"

# Defense test durations
DEFENSE_TEST_TICKS = 500    # Standard duration for defense tests


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
MOD_BASE_BEAM_FALLOFF = 0.001

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

# Alternative seeds for variation testing
ALT_SEED_1 = 123
ALT_SEED_2 = 456
ALT_SEED_3 = 789
