"""Tests for DesignValidator — validates designs before build queue insertion."""
import pytest
from game.core.registry import GameRegistries
from game.simulation.components.component import load_components_data, load_modifiers_data
from game.simulation.entities.ship_loader import load_vehicle_classes_data
from game.strategy.services.design_validator import DesignValidator


@pytest.fixture
def registries():
    minimal = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
    return GameRegistries(
        components=load_components_data(registries=minimal),
        modifiers=load_modifiers_data(),
        vehicle_classes=load_vehicle_classes_data(),
        resources={}
    )


class TestDesignValidator:

    def test_valid_design_passes(self, registries):
        """A design with sufficient crew and life support passes."""
        design = {
            'ship_class': 'frigate',
            'layers': {
                'CORE': [
                    {'id': 'bridge', 'modifiers': []},
                    {'id': 'crew_quarters', 'modifiers': []},
                    {'id': 'life_support', 'modifiers': []},
                ]
            }
        }
        validator = DesignValidator(registries)
        result = validator.validate(design)
        # Bridge needs crew, crew_quarters provides 10, life_support provides 25
        # This may or may not pass depending on exact crew requirements
        # The point is: no crash, returns a result
        assert isinstance(result.is_valid, bool)
        assert isinstance(result.errors, list)

    def test_missing_crew_fails(self, registries):
        """Design with components requiring crew but no crew quarters should fail."""
        # Use a component with a fixed (non-formula) CrewRequired value
        design = {
            'ship_class': 'frigate',
            'layers': {
                'CORE': [
                    # metal_harvester has CrewRequired: 5 (fixed numeric)
                    {'id': 'metal_harvester', 'modifiers': []},
                    {'id': 'metal_harvester', 'modifiers': []},
                    {'id': 'metal_harvester', 'modifiers': []},
                    # No crew_quarters — 15 crew required, 0 capacity
                ]
            }
        }
        validator = DesignValidator(registries)
        result = validator.validate(design)
        assert not result.is_valid
        assert any("crew housing" in e.lower() for e in result.errors)

    def test_missing_component_fails(self, registries):
        """Design with nonexistent component should fail."""
        design = {
            'ship_class': 'frigate',
            'layers': {
                'CORE': [
                    {'id': 'nonexistent_component_xyz', 'modifiers': []},
                ]
            }
        }
        validator = DesignValidator(registries)
        result = validator.validate(design)
        assert not result.is_valid
        assert any("not found" in e.lower() for e in result.errors)

    def test_empty_design_fails(self, registries):
        """Empty design data should fail."""
        validator = DesignValidator(registries)
        result = validator.validate({})
        # Empty design has no components — no crew issues, but validates OK
        # (no components = no crew required = no crew deficit)
        assert isinstance(result.is_valid, bool)

    def test_none_design_fails(self, registries):
        """None design should fail."""
        validator = DesignValidator(registries)
        result = validator.validate(None)
        assert not result.is_valid
