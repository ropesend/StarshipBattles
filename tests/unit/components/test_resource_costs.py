import pytest
import json
import os
from game.simulation.components.component import Component
from game.strategy.data.planet import PLANET_RESOURCES

# Path to components.json
COMPONENTS_JSON_PATH = os.path.join("data", "components.json")

@pytest.fixture
def component_list():
    """Returns the list of components from components.json."""
    with open(COMPONENTS_JSON_PATH, "r") as f:
        data = json.load(f)
        return data["components"]

class TestComponentResourceCosts:
    """
    TDD Phase 1: Verify all components have valid resource_cost data.
    """

    def test_all_components_have_resource_cost(self, component_list):
        """Phase 1.1: Every component in components.json must have a resource_cost dict."""
        for comp in component_list:
            assert "resource_cost" in comp, f"Component {comp.get('id')} missing 'resource_cost'"
            assert isinstance(comp["resource_cost"], dict), f"resource_cost for {comp.get('id')} must be a dict"

    def test_resource_names_valid(self, component_list):
        """Phase 1.1: All resource keys must be in PLANET_RESOURCES."""
        for comp in component_list:
            costs = comp.get("resource_cost", {})
            for res_name in costs.keys():
                assert res_name in PLANET_RESOURCES, f"Invalid resource '{res_name}' in component {comp.get('id')}"

    def test_resource_values_integer(self, component_list):
        """Phase 1.1: Resource costs should be positive integers."""
        for comp in component_list:
            costs = comp.get("resource_cost", {})
            for res_name, amount in costs.items():
                assert isinstance(amount, int), f"Cost for {res_name} in {comp.get('id')} must be int"
                assert amount >= 0, f"Cost for {res_name} in {comp.get('id')} cannot be negative"

class TestComponentModifierCosts:
    """
    TDD Phase 2: Verify modifiers affect resource costs correctly.
    """

    @pytest.fixture(autouse=True)
    def setup_registry(self):
        """Ensure registries are loaded."""
        from game.simulation.components.component import load_components, load_modifiers
        load_components()
        load_modifiers()

    def test_get_resource_cost_base(self):
        """Verify get_resource_cost returns base costs when no modifiers present."""
        from game.simulation.components.component import create_component
        comp = create_component('bridge')
        
        # Base Metals cost for bridge is 80
        costs = comp.get_resource_cost()
        assert costs['Metals'] == 80
        assert costs['Organics'] == 20

    def test_size_mount_multiplies_cost(self):
        """Verify simple_size_mount scales all costs linearly."""
        from game.simulation.components.component import create_component
        comp = create_component('railgun') # Base Metals: 150
        
        # Add size modifier (2.0x)
        comp.add_modifier('simple_size_mount', 2.0)
        
        costs = comp.get_resource_cost()
        assert costs['Metals'] == 300 # 150 * 2

    def test_range_mount_exponential_cost(self):
        """Verify range_mount scales costs by 3.5^level."""
        from game.simulation.components.component import create_component
        comp = create_component('railgun') # Base Metals: 150
        
        # Add range modifier (Level 1)
        comp.add_modifier('range_mount', 1.0)
        
        costs = comp.get_resource_cost()
        # 150 * 3.5 = 525
        assert costs['Metals'] == 525
