"""
Shared ship fixtures for tests.

This module provides reusable ship fixtures that can be used across all tests,
eliminating boilerplate ship creation code and ensuring consistent test setups.

Usage in tests:
    def test_something(basic_ship):
        # basic_ship is automatically provided by pytest
        assert basic_ship.max_hp > 0

    def test_with_factory(fresh_registries):
        # Or use factory directly for custom ships
        from tests.fixtures.ships import create_test_ship
        ship = create_test_ship(name="MyShip", x=100, y=200, registries=fresh_registries)

Available fixtures:
    - empty_ship: Ship with only auto-equipped hull
    - basic_ship: Ship with bridge and engine
    - armed_ship: Ship with weapons
    - shielded_ship: Ship with shields
    - fully_equipped_ship: Ship with all common component types

PROJ-50: All fixtures require fresh_registries for strict DI compliance.
"""
import pytest
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from game.core.registry import GameRegistries

from game.simulation.entities.ship import Ship
from game.simulation.components.component import create_component
from game.simulation.components.component_constants import LayerType


# =============================================================================
# Component ID Constants (Production Data)
# =============================================================================

# These are the real component IDs from data/components.json
# Using production IDs ensures fixtures work with the standard registry hydration
BRIDGE_ID = "bridge"
ENGINE_ID = "standard_engine"
WEAPON_ID = "laser_cannon"
SHIELD_ID = "shield_generator"
ARMOR_ID = "armor_plate"
CREW_QUARTERS_ID = "crew_quarters"
LIFE_SUPPORT_ID = "life_support"

# Default ship class that exists in production data
DEFAULT_SHIP_CLASS = "Escort"


# =============================================================================
# Factory Function
# =============================================================================

def create_test_ship(
    name: str = "TestShip",
    x: float = 0,
    y: float = 0,
    color: Tuple[int, int, int] = (255, 255, 255),
    ship_class: str = DEFAULT_SHIP_CLASS,
    team_id: int = 0,
    add_bridge: bool = False,
    add_engine: bool = False,
    add_weapons: int = 0,
    add_shields: int = 0,
    add_crew: bool = True,
    *,
    registries: 'GameRegistries',
) -> Ship:
    """
    Create a test ship with customizable configuration.

    This factory function creates ships for testing purposes. By default,
    it creates a minimal ship with only the hull. Use parameters to add
    additional components.

    PROJ-50: Strict DI - registries is required. Pass fresh_registries fixture.

    Components are placed in appropriate layers based on game rules:
    - Crew (quarters + life support) → CORE (required for other components to be active)
    - Bridge → CORE (allowed, Crewsupport classification)
    - Engine → OUTER (Engines blocked in CORE)
    - Weapons → OUTER (Weapons blocked in CORE and INNER)
    - Shields → OUTER (allowed in all non-restricted layers)

    Args:
        name: Ship name
        x: X position
        y: Y position
        color: Ship color tuple (R, G, B)
        ship_class: Vehicle class name (must exist in registry)
        team_id: Team ID for the ship
        add_bridge: If True, add a bridge component
        add_engine: If True, add an engine component
        add_weapons: Number of weapon components to add
        add_shields: Number of shield components to add
        add_crew: If True (default), add crew_quarters and life_support
                  (required for components to be active)
        registries: GameRegistries for DI (required keyword-only).

    Returns:
        Configured Ship instance

    Raises:
        TypeError: If registries is None

    Example:
        # Create armed ship with DI
        ship = create_test_ship(
            name="Attacker",
            add_bridge=True,
            add_engine=True,
            add_weapons=2,
            registries=fresh_registries
        )
    """
    if registries is None:
        raise TypeError("registries is required for create_test_ship")
    ship = Ship(name=name, x=x, y=y, color=color, ship_class=ship_class, registries=registries)
    ship.team_id = team_id

    # Crew support components go in CORE - required for other components to be active
    if add_crew:
        crew_quarters = create_component(CREW_QUARTERS_ID, registries=registries)
        life_support = create_component(LIFE_SUPPORT_ID, registries=registries)
        if crew_quarters:
            ship.add_component(crew_quarters, LayerType.CORE)
        if life_support:
            ship.add_component(life_support, LayerType.CORE)

    # Bridge goes in CORE (Crewsupport classification, not blocked)
    if add_bridge:
        bridge = create_component(BRIDGE_ID, registries=registries)
        if bridge:
            ship.add_component(bridge, LayerType.CORE)

    # Engine goes in OUTER (Engines classification blocked in CORE)
    if add_engine:
        engine = create_component(ENGINE_ID, registries=registries)
        if engine:
            ship.add_component(engine, LayerType.OUTER)

    # Weapons go in OUTER (Weapons classification blocked in CORE and INNER)
    for _ in range(add_weapons):
        weapon = create_component(WEAPON_ID, registries=registries)
        if weapon:
            ship.add_component(weapon, LayerType.OUTER)

    # Shields go in OUTER (safest choice - INNER may not exist for all ship classes)
    for _ in range(add_shields):
        shield = create_component(SHIELD_ID, registries=registries)
        if shield:
            ship.add_component(shield, LayerType.OUTER)

    ship.recalculate_stats()
    return ship


# =============================================================================
# Pytest Fixtures (PROJ-50: All require fresh_registries)
# =============================================================================

@pytest.fixture
def empty_ship(fresh_registries):
    """
    Create a ship with only the auto-equipped hull (no other components).

    This fixture provides the most minimal ship possible - just the hull
    that is automatically equipped when a ship is created.

    PROJ-50: Uses fresh_registries for strict DI compliance.
    """
    return Ship(name="EmptyShip", x=0, y=0, color=(255, 255, 255),
                ship_class=DEFAULT_SHIP_CLASS, registries=fresh_registries)


@pytest.fixture
def basic_ship(fresh_registries):
    """
    Create a ship with bridge and engine in CORE layer.

    This fixture provides a ship with the minimum components needed
    for basic operation - a bridge (for command) and an engine (for movement).

    PROJ-50: Uses fresh_registries for strict DI compliance.
    """
    return create_test_ship(
        name="BasicShip",
        add_bridge=True,
        add_engine=True,
        registries=fresh_registries
    )


@pytest.fixture
def armed_ship(fresh_registries):
    """
    Create a ship with weapons, shields, and components across multiple layers.

    This fixture provides a combat-ready ship with:
    - Bridge in CORE
    - Engine, shield, 2 weapons in OUTER
    - Armor in ARMOR layer

    PROJ-50: Uses fresh_registries for strict DI compliance.
    """
    ship = create_test_ship(
        name="ArmedShip",
        add_bridge=True,
        add_engine=True,
        add_weapons=2,
        add_shields=1,
        registries=fresh_registries
    )

    # Add armor to ARMOR layer
    armor = create_component(ARMOR_ID, registries=fresh_registries)
    if armor:
        ship.add_component(armor, LayerType.ARMOR)

    ship.recalculate_stats()
    return ship


@pytest.fixture
def shielded_ship(fresh_registries):
    """
    Create a ship with shields but no weapons.

    This fixture provides a defensive ship with:
    - Bridge in CORE
    - Engine and shield in OUTER

    PROJ-50: Uses fresh_registries for strict DI compliance.
    """
    return create_test_ship(
        name="ShieldedShip",
        add_bridge=True,
        add_engine=True,
        add_shields=1,
        registries=fresh_registries
    )


@pytest.fixture
def fully_equipped_ship(fresh_registries):
    """
    Create a ship with all common component types.

    This fixture provides a fully-equipped ship with:
    - Bridge in CORE
    - Engine, shield, weapons in OUTER
    - Armor in ARMOR layer

    PROJ-50: Uses fresh_registries for strict DI compliance.
    """
    ship = create_test_ship(
        name="FullyEquippedShip",
        add_bridge=True,
        add_engine=True,
        add_weapons=2,
        add_shields=1,
        registries=fresh_registries
    )

    # Add armor to ARMOR layer
    armor = create_component(ARMOR_ID, registries=fresh_registries)
    if armor:
        ship.add_component(armor, LayerType.ARMOR)

    ship.recalculate_stats()
    return ship


@pytest.fixture
def two_opposing_ships(fresh_registries):
    """
    Create two ships on opposing teams.

    Returns a tuple of (ship1, ship2) where:
    - ship1 is on team 0, positioned at (100, 400)
    - ship2 is on team 1, positioned at (700, 400)

    Both ships are armed with basic weapons.

    PROJ-50: Uses fresh_registries for strict DI compliance.
    """
    ship1 = create_test_ship(
        name="Ship1",
        x=100,
        y=400,
        team_id=0,
        add_bridge=True,
        add_engine=True,
        add_weapons=1,
        registries=fresh_registries
    )

    ship2 = create_test_ship(
        name="Ship2",
        x=700,
        y=400,
        team_id=1,
        add_bridge=True,
        add_engine=True,
        add_weapons=1,
        registries=fresh_registries
    )

    return ship1, ship2


# =============================================================================
# Class-Specific Ship Fixtures
# =============================================================================

@pytest.fixture
def basic_cruiser_ship(fresh_registries):
    """
    Create a basic Cruiser ship for testing.

    The Cruiser class has 4 layers (CORE, INNER, OUTER, ARMOR) which makes
    it suitable for testing features that require the INNER layer.

    PROJ-50: Uses fresh_registries for strict DI compliance.
    """
    ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Cruiser",
                registries=fresh_registries)
    ship.recalculate_stats()
    return ship


@pytest.fixture
def basic_escort_ship(fresh_registries):
    """
    Create a basic Escort ship for testing.

    The Escort class has 3 layers (CORE, OUTER, ARMOR) and is a smaller
    ship class suitable for basic testing.

    PROJ-50: Uses fresh_registries for strict DI compliance.
    """
    ship = Ship("TestShip", 0, 0, (255, 255, 255), ship_class="Escort",
                registries=fresh_registries)
    ship.recalculate_stats()
    return ship
