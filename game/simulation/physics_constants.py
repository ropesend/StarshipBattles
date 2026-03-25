"""
Physics Constants - Single Source of Truth

These constants define the core physics parameters used throughout the game engine
and Combat Lab test framework. They determine how ship stats (thrust, mass, turn rate)
convert to gameplay behavior (speed, acceleration, turn speed).

DO NOT DUPLICATE THESE CONSTANTS. Import from this module instead.

Usage:
    from game.simulation.physics_constants import K_SPEED, K_THRUST, K_TURN
"""

# Speed Calculation
# Formula: max_speed = (total_thrust * K_SPEED) / mass
K_SPEED = 25

# Acceleration Calculation
# Formula: acceleration = (total_thrust * K_THRUST) / (mass ** 2)
K_THRUST = 2500

# Turn Speed Calculation
# Formula: turn_speed = (raw_turn_speed * K_TURN) / (mass ** 1.5)
K_TURN = 25000

# Default maximum mass budget for unknown vehicle classes
DEFAULT_MAX_MASS = 1000

# Documentation of formulas for reference
FORMULA_MAX_SPEED = "max_speed = (total_thrust * K_SPEED) / mass"
FORMULA_ACCELERATION = "acceleration = (total_thrust * K_THRUST) / (mass ** 2)"
FORMULA_TURN_SPEED = "turn_speed = (raw_turn_speed * K_TURN) / (mass ** 1.5)"


def compute_acceleration(thrust: float, mass: float) -> float:
    """Compute acceleration from thrust and mass.

    Formula: acceleration = (thrust * K_THRUST) / mass^2

    PROJ-225: Single source of truth for acceleration formula,
    used by both ShipStatsCalculator (design-time) and ShipPhysicsMixin (runtime).

    Args:
        thrust: Total thrust force
        mass: Ship mass (must be > 0 for non-zero result)

    Returns:
        Acceleration rate, or 0.0 if mass <= 0
    """
    if mass <= 0:
        return 0.0
    return (thrust * K_THRUST) / (mass * mass)


def compute_max_speed(thrust: float, mass: float) -> float:
    """Compute maximum speed from thrust and mass.

    Formula: max_speed = (thrust * K_SPEED) / mass

    PROJ-225: Single source of truth for max speed formula,
    used by both ShipStatsCalculator (design-time) and ShipPhysicsMixin (runtime).

    Args:
        thrust: Total thrust force
        mass: Ship mass (must be > 0 for non-zero result)

    Returns:
        Maximum speed, or 0.0 if mass <= 0
    """
    if mass <= 0:
        return 0.0
    return (thrust * K_SPEED) / mass
