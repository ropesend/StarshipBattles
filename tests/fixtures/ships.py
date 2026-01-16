"""
Shared ship fixtures for tests.

This module provides reusable ship fixtures that can be used across all tests,
eliminating boilerplate ship creation code and ensuring consistent test setups.

Usage in tests:
    def test_something(basic_ship):
        # basic_ship is automatically provided by pytest
        assert basic_ship.max_hp > 0

    def test_with_factory():
        # Or use factory directly for custom ships
        from tests.fixtures.ships import create_test_ship
        ship = create_test_ship(name="MyShip", x=100, y=200)

Available fixtures:
    - empty_ship: Ship with only auto-equipped hull
    - basic_ship: Ship with bridge and engine
    - armed_ship: Ship with weapons
    - shielded_ship: Ship with shields
    - fully_equipped_ship: Ship with all common component types
"""
import pytest
from typing import Tuple

from game.simulation.entities.ship import Ship
from game.simulation.components.component import create_component, LayerType


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
) -> Ship:
    """
    Create a test ship with customizable configuration.

    This factory function creates ships for testing purposes. By default,
    it creates a minimal ship with only the hull. Use parameters to add
    additional components.

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

    Returns:
        Configured Ship instance

    Example:
        # Create armed ship
        ship = create_test_ship(
            name="Attacker",
            add_bridge=True,
            add_engine=True,
            add_weapons=2
        )
    """
    ship = Ship(name=name, x=x, y=y, color=color, ship_class=ship_class)
    ship.team_id = team_id

    # Crew support components go in CORE - required for other components to be active
    if add_crew:
        crew_quarters = create_component(CREW_QUARTERS_ID)
        life_support = create_component(LIFE_SUPPORT_ID)
        if crew_quarters:
            ship.add_component(crew_quarters, LayerType.CORE)
        if life_support:
            ship.add_component(life_support, LayerType.CORE)

    # Bridge goes in CORE (Crewsupport classification, not blocked)
    if add_bridge:
        bridge = create_component(BRIDGE_ID)
        if bridge:
            ship.add_component(bridge, LayerType.CORE)

    # Engine goes in OUTER (Engines classification blocked in CORE)
    if add_engine:
        engine = create_component(ENGINE_ID)
        if engine:
            ship.add_component(engine, LayerType.OUTER)

    # Weapons go in OUTER (Weapons classification blocked in CORE and INNER)
    for _ in range(add_weapons):
        weapon = create_component(WEAPON_ID)
        if weapon:
            ship.add_component(weapon, LayerType.OUTER)

    # Shields go in OUTER (safest choice - INNER may not exist for all ship classes)
    for _ in range(add_shields):
        shield = create_component(SHIELD_ID)
        if shield:
            ship.add_component(shield, LayerType.OUTER)

    ship.recalculate_stats()
    return ship


# =============================================================================
# Pytest Fixtures
# =============================================================================

@pytest.fixture
def empty_ship():
    """
    Create a ship with only the auto-equipped hull (no other components).

    This fixture provides the most minimal ship possible - just the hull
    that is automatically equipped when a ship is created.

    Note: This fixture uses production registry data. For tests using
    custom data, use the use_custom_data marker and create ships manually.
    """
    return Ship(name="EmptyShip", x=0, y=0, color=(255, 255, 255), ship_class=DEFAULT_SHIP_CLASS)


@pytest.fixture
def basic_ship():
    """
    Create a ship with bridge and engine in CORE layer.

    This fixture provides a ship with the minimum components needed
    for basic operation - a bridge (for command) and an engine (for movement).
    """
    return create_test_ship(
        name="BasicShip",
        add_bridge=True,
        add_engine=True
    )


@pytest.fixture
def armed_ship():
    """
    Create a ship with weapons, shields, and components across multiple layers.

    This fixture provides a combat-ready ship with:
    - Bridge in CORE
    - Engine, shield, 2 weapons in OUTER
    - Armor in ARMOR layer
    """
    ship = create_test_ship(
        name="ArmedShip",
        add_bridge=True,
        add_engine=True,
        add_weapons=2,
        add_shields=1
    )

    # Add armor to ARMOR layer
    armor = create_component(ARMOR_ID)
    if armor:
        ship.add_component(armor, LayerType.ARMOR)

    ship.recalculate_stats()
    return ship


@pytest.fixture
def shielded_ship():
    """
    Create a ship with shields but no weapons.

    This fixture provides a defensive ship with:
    - Bridge in CORE
    - Engine and shield in OUTER
    """
    return create_test_ship(
        name="ShieldedShip",
        add_bridge=True,
        add_engine=True,
        add_shields=1
    )


@pytest.fixture
def fully_equipped_ship():
    """
    Create a ship with all common component types.

    This fixture provides a fully-equipped ship with:
    - Bridge in CORE
    - Engine, shield, weapons in OUTER
    - Armor in ARMOR layer
    """
    ship = create_test_ship(
        name="FullyEquippedShip",
        add_bridge=True,
        add_engine=True,
        add_weapons=2,
        add_shields=1
    )

    # Add armor to ARMOR layer
    armor = create_component(ARMOR_ID)
    if armor:
        ship.add_component(armor, LayerType.ARMOR)

    ship.recalculate_stats()
    return ship


@pytest.fixture
def two_opposing_ships():
    """
    Create two ships on opposing teams.

    Returns a tuple of (ship1, ship2) where:
    - ship1 is on team 0, positioned at (100, 400)
    - ship2 is on team 1, positioned at (700, 400)

    Both ships are armed with basic weapons.
    """
    ship1 = create_test_ship(
        name="Ship1",
        x=100,
        y=400,
        team_id=0,
        add_bridge=True,
        add_engine=True,
        add_weapons=1
    )

    ship2 = create_test_ship(
        name="Ship2",
        x=700,
        y=400,
        team_id=1,
        add_bridge=True,
        add_engine=True,
        add_weapons=1
    )

    return ship1, ship2
