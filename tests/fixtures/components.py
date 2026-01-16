"""
Shared component fixtures for tests.

This module provides reusable component fixtures that can be used across all tests,
eliminating boilerplate component creation code and ensuring consistent test setups.

Usage in tests:
    def test_something(weapon_component):
        # weapon_component is automatically provided by pytest
        assert weapon_component.has_ability('WeaponAbility')

    def test_with_factory():
        # Or use factory directly for custom components
        from tests.fixtures.components import create_weapon
        weapon = create_weapon()

Available fixtures:
    - weapon_component: A laser cannon component
    - engine_component: A standard engine component
    - shield_component: A shield generator component
    - armor_component: An armor plate component
    - bridge_component: A bridge component
"""
import pytest

from game.simulation.components.component import create_component, Component, LayerType


# =============================================================================
# Component ID Constants (Production Data)
# =============================================================================

# These are the real component IDs from data/components.json
BRIDGE_ID = "bridge"
ENGINE_ID = "standard_engine"
WEAPON_ID = "laser_cannon"
SHIELD_ID = "shield_generator"
ARMOR_ID = "armor_plate"
CREW_QUARTERS_ID = "crew_quarters"
LIFE_SUPPORT_ID = "life_support"


# =============================================================================
# Factory Functions
# =============================================================================

def create_weapon(component_id: str = WEAPON_ID) -> Component:
    """
    Create a weapon component.

    Args:
        component_id: Component ID to use (default: laser_cannon)

    Returns:
        Component with WeaponAbility
    """
    component = create_component(component_id)
    if component is None:
        raise ValueError(f"Failed to create weapon component with ID: {component_id}")
    return component


def create_engine(component_id: str = ENGINE_ID) -> Component:
    """
    Create an engine component.

    Args:
        component_id: Component ID to use (default: standard_engine)

    Returns:
        Component with CombatPropulsion ability
    """
    component = create_component(component_id)
    if component is None:
        raise ValueError(f"Failed to create engine component with ID: {component_id}")
    return component


def create_shield(component_id: str = SHIELD_ID) -> Component:
    """
    Create a shield component.

    Args:
        component_id: Component ID to use (default: shield_generator)

    Returns:
        Component with ShieldProjection ability
    """
    component = create_component(component_id)
    if component is None:
        raise ValueError(f"Failed to create shield component with ID: {component_id}")
    return component


def create_armor(component_id: str = ARMOR_ID) -> Component:
    """
    Create an armor component.

    Args:
        component_id: Component ID to use (default: armor_plate)

    Returns:
        Component with positive HP for protection
    """
    component = create_component(component_id)
    if component is None:
        raise ValueError(f"Failed to create armor component with ID: {component_id}")
    return component


def create_bridge(component_id: str = BRIDGE_ID) -> Component:
    """
    Create a bridge component.

    Args:
        component_id: Component ID to use (default: bridge)

    Returns:
        Component with CommandAndControl ability
    """
    component = create_component(component_id)
    if component is None:
        raise ValueError(f"Failed to create bridge component with ID: {component_id}")
    return component


def create_crew_quarters(component_id: str = CREW_QUARTERS_ID) -> Component:
    """
    Create a crew quarters component.

    Args:
        component_id: Component ID to use (default: crew_quarters)

    Returns:
        Component that provides crew capacity
    """
    component = create_component(component_id)
    if component is None:
        raise ValueError(f"Failed to create crew quarters component with ID: {component_id}")
    return component


def create_life_support(component_id: str = LIFE_SUPPORT_ID) -> Component:
    """
    Create a life support component.

    Args:
        component_id: Component ID to use (default: life_support)

    Returns:
        Component that provides life support
    """
    component = create_component(component_id)
    if component is None:
        raise ValueError(f"Failed to create life support component with ID: {component_id}")
    return component


# =============================================================================
# Pytest Fixtures
# =============================================================================

@pytest.fixture
def weapon_component():
    """
    Create a weapon component (laser cannon).

    Returns a Component instance with WeaponAbility.
    """
    return create_weapon()


@pytest.fixture
def engine_component():
    """
    Create an engine component (standard engine).

    Returns a Component instance with CombatPropulsion ability.
    """
    return create_engine()


@pytest.fixture
def shield_component():
    """
    Create a shield component (shield generator).

    Returns a Component instance with ShieldProjection ability.
    """
    return create_shield()


@pytest.fixture
def armor_component():
    """
    Create an armor component (armor plate).

    Returns a Component instance with positive HP for protection.
    """
    return create_armor()


@pytest.fixture
def bridge_component():
    """
    Create a bridge component.

    Returns a Component instance with CommandAndControl ability.
    """
    return create_bridge()


@pytest.fixture
def crew_quarters_component():
    """
    Create a crew quarters component.

    Returns a Component instance that provides crew capacity.
    """
    return create_crew_quarters()


@pytest.fixture
def life_support_component():
    """
    Create a life support component.

    Returns a Component instance that provides life support.
    """
    return create_life_support()
