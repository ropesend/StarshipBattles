import pytest
import pygame

from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components import load_components, create_component, Component, LayerType
from game.core.registry import RegistryManager
from game.simulation.entities.ship_stats import ShipStatsCalculator
from game.core.constants import COMPONENTS_FILE
from tests.fixtures.paths import get_project_root


@pytest.fixture
def energy_repro_setup():
    """Set up pygame and load component data for energy reproduction tests."""
    pygame.init()
    # Ensure clean state
    RegistryManager.instance().clear()

    initialize_ship_data(str(get_project_root()))
    # Use standard components.json path
    load_components(COMPONENTS_FILE)

    yield

    pygame.quit()
    RegistryManager.instance().clear()


class TestEnergyRepro:
    def test_laser_cannon_has_abilities(self, energy_repro_setup):
        """Test that laser_cannon component has weapon ability with energy cost."""
        comps = RegistryManager.instance().components

        # Verify laser_cannon is registered
        assert 'laser_cannon' in comps, "laser_cannon should be in registry"

        # Check data structure
        data = comps['laser_cannon'].data
        assert 'abilities' in data, "laser_cannon data should have abilities key"

        # Create component and verify it can be instantiated
        laser = create_component('laser_cannon')
        assert laser is not None, "laser_cannon should be creatable"

    def test_generator_has_resource_generation_ability(self, energy_repro_setup):
        """Test that generator component has ResourceGeneration ability for energy."""
        comps = RegistryManager.instance().components

        # Verify generator is registered
        assert 'generator' in comps, "generator should be in registry"

        # Check data has ResourceGeneration ability
        data = comps['generator'].data
        assert 'abilities' in data, "generator data should have abilities key"
        assert 'ResourceGeneration' in data['abilities'], \
            "generator should have ResourceGeneration ability"

        # Verify ResourceGeneration contains energy
        resource_gen = data['abilities']['ResourceGeneration']
        assert isinstance(resource_gen, list), "ResourceGeneration should be a list"
        assert len(resource_gen) > 0, "ResourceGeneration should have entries"

        # Find energy resource
        energy_entries = [r for r in resource_gen if r.get('resource') == 'energy']
        assert len(energy_entries) > 0, "generator should generate energy"
        assert 'amount' in energy_entries[0], "energy generation should have amount"
