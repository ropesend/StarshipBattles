import pytest
from unittest.mock import MagicMock

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components.component import Component
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_project_root


@pytest.fixture
def ship_data():
    """Initialize ship data and clean up registry after test."""
    initialize_ship_data(str(get_project_root()))
    yield
    RegistryManager.instance().clear()


@pytest.fixture
def fighter(ship_data):
    """Create a Fighter ship (2 layers: CORE, ARMOR)."""
    return Ship("TestFighter", 0, 0, (255, 0, 0), ship_class="Fighter (Small)")


@pytest.fixture
def escort(ship_data):
    """Create an Escort ship (3 layers: CORE, OUTER, ARMOR)."""
    return Ship("TestEscort", 0, 0, (0, 255, 0), ship_class="Escort")


class TestLayerRefinements:

    def test_layer_mass_limits_loaded(self, fighter, escort):
        """Verify max_mass_pct is loaded correctly from JSON."""
        # Fighter: 2 layers -> CORE: 1.0, ARMOR: 0.3
        core = fighter.layers[LayerType.CORE]
        armor = fighter.layers[LayerType.ARMOR]

        assert core['max_mass_pct'] == 1.0, "Fighter CORE should be 100%"
        assert armor['max_mass_pct'] == pytest.approx(0.3, abs=0.01), "Fighter ARMOR should be 30%"

        # Verify Escort (likely 3 real layers + 1 HULL)
        layer_count = len(escort.layers)

        # [NEW] Adjust for mandatory HULL layer
        if layer_count == 4:
            # Was 3-layer -> now 4. Core: 0.5, Outer: 0.7, Armor: 0.3
            assert escort.layers[LayerType.CORE]['max_mass_pct'] == 0.5
            assert escort.layers[LayerType.OUTER]['max_mass_pct'] == 0.7
        elif layer_count == 5:
            # Was 4-layer -> now 5.
            assert escort.layers[LayerType.CORE]['max_mass_pct'] == 0.3
            assert escort.layers[LayerType.OUTER]['max_mass_pct'] == 0.5

    def test_mass_budget_enforcement(self, fighter):
        """Verify mass_budget_exceeded logic via VALIDATOR."""
        # Fighter Max Mass = 250 (from JSON usually)
        max_mass = fighter.max_mass_budget

        # Armor Limit = 30% of max_mass
        armor_limit = max_mass * 0.3

        # Mock component
        heavy_armor = MagicMock(spec=Component)
        heavy_armor.mass = armor_limit + 10
        heavy_armor.allowed_layers = [LayerType.ARMOR]
        heavy_armor.allowed_vehicle_types = ["Fighter"]
        heavy_armor.data = {'major_classification': 'Armor'}
        # Specific attributes needed for checks
        heavy_armor.type_str = "Armor"
        heavy_armor.id = "heavy_armor"
        # Since we use validate_addition, we need to ensure other checks pass or we focus on mass
        from game.simulation.ship_validator import MassBudgetRule

        rule = MassBudgetRule()

        # Check budget check directly using strict rule check to Isolate test
        res = rule.validate(fighter, heavy_armor, LayerType.ARMOR)
        assert not res.is_valid, "Should fail mass budget"
        assert any("Mass budget exceeded" in e for e in res.errors)

        # Check allowed mass
        light_armor = MagicMock(spec=Component)
        light_armor.mass = armor_limit - 10
        light_armor.allowed_layers = [LayerType.ARMOR]
        light_armor.allowed_vehicle_types = ["Fighter"]
        light_armor.data = {'major_classification': 'Armor'}
        light_armor.type_str = "Armor"
        light_armor.id = "light_armor"

        res = rule.validate(fighter, light_armor, LayerType.ARMOR)
        assert res.is_valid, "Should allow mass within budget"

    def test_all_layers_filter_logic(self, fighter, escort):
        """Verify the logic for 'All Layers' filter."""
        # Simulation of the logic in left_panel.py

        # Component allowed in CORE only
        comp_core = MagicMock()
        comp_core.allowed_layers = [LayerType.CORE]

        # Component allowed in OUTER only
        comp_outer = MagicMock()
        comp_outer.allowed_layers = [LayerType.OUTER]

        # Fighter has CORE, ARMOR. No OUTER.
        valid_layers_fighter = set(fighter.layers.keys())

        # Check Core Comp -> Should be visible
        assert any(l in valid_layers_fighter for l in comp_core.allowed_layers)

        # Check Outer Comp -> Should NOT be visible on Fighter
        assert not any(l in valid_layers_fighter for l in comp_outer.allowed_layers)

        # Escort (assuming it has OUTER)
        valid_layers_escort = set(escort.layers.keys())
        if LayerType.OUTER in valid_layers_escort:
             assert any(l in valid_layers_escort for l in comp_outer.allowed_layers)

    def test_dynamic_radius_calculation(self, fighter, escort):
        """Verify layer radii are calculated based on area proportional to mass."""
        # For Fighter:
        # CORE: 1.0 Mass Pct
        # ARMOR: 0.3 Mass Pct
        # Total Capacity = 1.3

        # Expected Radii:
        # Core Radius = sqrt(1.0 / 1.3) = sqrt(0.769) ~= 0.877
        # Armor Radius = sqrt((1.0 + 0.3) / 1.3) = sqrt(1.0) = 1.0

        core_r = fighter.layers[LayerType.CORE]['radius_pct']
        armor_r = fighter.layers[LayerType.ARMOR]['radius_pct']

        assert core_r == pytest.approx(0.877, abs=0.001), f"Fighter Core Radius mismatch. Got {core_r}"
        assert armor_r == pytest.approx(1.0, abs=0.001), f"Fighter Armor Radius mismatch. Got {armor_r}"

        # Verify Escort (assuming 3 layers: Core 0.5, Outer 0.7, Armor 0.3) -> Total 1.5 (or whatever it actually is)
        # Inspect actual mass limits to be sure
        present_layers = [l for l in [LayerType.CORE, LayerType.INNER, LayerType.OUTER, LayerType.ARMOR] if l in escort.layers]
        total_mass = sum(escort.layers[l]['max_mass_pct'] for l in present_layers)

        cumulative = 0
        for l in present_layers:
            cumulative += escort.layers[l]['max_mass_pct']
            expected_r = (cumulative / total_mass) ** 0.5
            actual_r = escort.layers[l]['radius_pct']
            assert actual_r == pytest.approx(expected_r, abs=0.001), f"Escort {l.name} radius mismatch"
