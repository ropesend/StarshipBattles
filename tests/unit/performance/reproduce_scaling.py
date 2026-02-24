import pytest
import pygame

from game.simulation.components.component import load_components, create_component, load_modifiers
from game.core.paths import Paths
from game.core.registry import RegistryManager


@pytest.fixture
def component_environment():
    """Set up pygame and load components/modifiers for testing."""
    pygame.init()

    # Load data using centralized paths
    load_components(Paths.COMPONENTS_FILE)
    load_modifiers(Paths.MODIFIERS_FILE)

    yield

    pygame.quit()


class TestComponentScaling:

    def test_crew_scaling(self, component_environment):
        # Create Crew Quarters
        cq = create_component("crew_quarters", registries=RegistryManager.instance())
        assert cq is not None, "Crew Quarters should exist"

        # New Ability System: Access via get_ability
        initial_capacity = cq.get_ability('CrewCapacity').amount
        print(f"Initial Crew Capacity: {initial_capacity}")

        # Apply simple_size modifier (Scale 2)
        res = cq.add_modifier("simple_size_mount", 2.0)
        assert res, "Should successfully add modifier"

        scaled_capacity = cq.get_ability('CrewCapacity').amount
        print(f"Scaled Crew Capacity (x2): {scaled_capacity}")

        assert scaled_capacity == initial_capacity * 2, "Crew Capacity should scale linearly with size"

    def test_life_support_scaling(self, component_environment):
        # Create Life Support
        ls = create_component("life_support", registries=RegistryManager.instance())
        assert ls is not None, "Life Support should exist"

        initial_capacity = ls.get_ability('LifeSupportCapacity').amount
        print(f"Initial Life Support: {initial_capacity}")

        # Apply simple_size modifier (Scale 2)
        ls.add_modifier("simple_size_mount", 2.0)

        scaled_capacity = ls.get_ability('LifeSupportCapacity').amount
        print(f"Scaled Life Support (x2): {scaled_capacity}")

        assert scaled_capacity == initial_capacity * 2, "Life Support should scale linearly with size"
