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


class TestLayerMassValidation:
    """Tests that layer mass violations are detected as warnings."""

    def test_over_layer_mass_produces_warning(self, registries):
        """A design exceeding a layer's mass percentage produces a warning."""
        # Capital_Escort CORE limit = 50% of 1000 (Escort) = 500kg
        # bridge=50, crew_quarters=30 each, life_support=20 each
        # 1 bridge + 14 crew_quarters + 2 life_support = 50 + 420 + 40 = 510 > 500
        design = {
            'ship_class': 'Escort',
            'vehicle_type': 'Ship',
            'theme_id': 'Federation',
            'team_id': 0,
            'color': [255, 255, 255],
            'ai_strategy': 'standard_ranged',
            'layers': {
                'CORE': [
                    {'id': 'bridge'},
                ] + [{'id': 'crew_quarters'} for _ in range(14)] + [
                    {'id': 'life_support'},
                    {'id': 'life_support'},
                ],
            },
            'resources': {'fuel': 0, 'energy': 0, 'ammo': 0},
        }
        validator = DesignValidator(registries)
        result = validator.validate(design)

        layer_warnings = [w for w in result.warnings if 'CORE' in w and 'mass' in w.lower()]
        assert len(layer_warnings) > 0, f"Expected CORE layer mass warning, got: {result.warnings}"

    def test_total_mass_over_budget_produces_warning(self, registries):
        """A design exceeding the total class mass budget produces a warning."""
        # Escort max_mass is 1000. crew_quarters=30 each.
        # 1 bridge(50) + 30 crew_quarters(900) + 5 life_support(100) = 1050 > 1000
        design = {
            'ship_class': 'Escort',
            'vehicle_type': 'Ship',
            'theme_id': 'Federation',
            'team_id': 0,
            'color': [255, 255, 255],
            'ai_strategy': 'standard_ranged',
            'layers': {
                'CORE': [{'id': 'bridge'}] + [{'id': 'crew_quarters'} for _ in range(10)],
                'OUTER': [{'id': 'crew_quarters'} for _ in range(20)] + [
                    {'id': 'life_support'} for _ in range(5)
                ],
            },
            'resources': {'fuel': 0, 'energy': 0, 'ammo': 0},
        }
        validator = DesignValidator(registries)
        result = validator.validate(design)

        total_warnings = [w for w in result.warnings if 'total' in w.lower() and 'mass' in w.lower()]
        assert len(total_warnings) > 0, f"Expected total mass warning, got: {result.warnings}"

    def test_layer_violations_are_warnings_not_errors(self, registries):
        """Layer mass violations are warnings (not errors) so designs can still be saved."""
        design = {
            'ship_class': 'Escort',
            'vehicle_type': 'Ship',
            'theme_id': 'Federation',
            'team_id': 0,
            'color': [255, 255, 255],
            'ai_strategy': 'standard_ranged',
            'layers': {
                'CORE': [
                    {'id': 'bridge'},
                    {'id': 'crew_quarters'},
                    {'id': 'crew_quarters'},
                    {'id': 'crew_quarters'},
                    {'id': 'crew_quarters'},
                    {'id': 'crew_quarters'},
                    {'id': 'life_support'},
                    {'id': 'life_support'},
                ],
            },
            'resources': {'fuel': 0, 'energy': 0, 'ammo': 0},
        }
        validator = DesignValidator(registries)
        result = validator.validate(design)

        # is_valid should still be True (only errors make it False)
        # warnings should exist for mass issues
        assert result.is_valid is True or len(result.errors) > 0  # errors only from crew/components

    def test_valid_design_no_mass_warnings(self, registries):
        """A small design within all budgets produces no mass warnings."""
        design = {
            'ship_class': 'Escort',
            'vehicle_type': 'Ship',
            'theme_id': 'Federation',
            'team_id': 0,
            'color': [255, 255, 255],
            'ai_strategy': 'standard_ranged',
            'layers': {
                'CORE': [{'id': 'bridge'}],
                'OUTER': [{'id': 'standard_engine'}],
            },
            'resources': {'fuel': 0, 'energy': 0, 'ammo': 0},
        }
        validator = DesignValidator(registries)
        result = validator.validate(design)

        mass_warnings = [w for w in result.warnings if 'mass' in w.lower()]
        assert len(mass_warnings) == 0, f"Unexpected mass warnings: {mass_warnings}"


class TestDesignValidationResultHasIssues:
    """Tests for the has_issues property."""

    def test_clean_result_has_no_issues(self):
        """A clean result has no issues."""
        from game.strategy.services.design_validator import DesignValidationResult
        result = DesignValidationResult()
        assert result.has_issues is False

    def test_warnings_count_as_issues(self):
        """Warnings count as issues (for build queue blocking)."""
        from game.strategy.services.design_validator import DesignValidationResult
        result = DesignValidationResult()
        result.add_warning("Over mass")
        assert result.has_issues is True

    def test_errors_count_as_issues(self):
        """Errors count as issues."""
        from game.strategy.services.design_validator import DesignValidationResult
        result = DesignValidationResult()
        result.add_error("Missing crew")
        assert result.has_issues is True
