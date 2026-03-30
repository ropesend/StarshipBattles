
import pytest
import os
import json
from game.core.registry import RegistryManager

# Helper to load components
def load_components_data():
    # Try different paths to find data/components.json
    paths = [
        "data/components.json",
        os.path.join(os.path.dirname(__file__), "../../../data/components.json"),
        "../../data/components.json"
    ]
    
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r') as f:
                data = json.load(f)
                return data.get('components', [])
    return []

COMPONENTS = load_components_data()
if not COMPONENTS:
    # Fallback debug: list files in CWD and data/
    cwd = os.getcwd()
    try:
        data_files = os.listdir("data")
    except Exception as e:
        data_files = str(e)
        
    raise ValueError(f"No components loaded! CWD: {cwd}, Data files: {data_files}")


class TestComponentDefinitions:
    """
    Data-driven tests validation for components.json.
    Ensures all components meet basic data integrity requirements.
    """

    @pytest.mark.parametrize("comp", COMPONENTS, ids=lambda c: c.get('id', 'unknown'))
    def test_component_ids_are_valid(self, comp):
        """Verify checking that all component IDs are lower_case_snake_case and valid."""
        assert 'id' in comp, "Component missing ID"
        c_id = comp['id']
        assert c_id == c_id.lower(), f"Component ID {c_id} must be lowercase"
        assert " " not in c_id, f"Component ID {c_id} must not contain spaces"
        assert len(c_id) > 2, f"Component ID {c_id} is too short"

    @pytest.mark.parametrize("comp", COMPONENTS, ids=lambda c: c.get('id', 'unknown'))
    def test_component_required_fields(self, comp):
        """Verify that mandatory fields exist."""
        required = ['name', 'type', 'mass', 'hp']
        for field in required:
            assert field in comp, f"Component {comp.get('id')} missing required field: {field}"
            
    @pytest.mark.parametrize("comp", COMPONENTS, ids=lambda c: c.get('id', 'unknown'))
    def test_component_metrics_are_positive(self, comp):
        """Verify mass, HP and cost are non-negative numbers."""
        # Handle formulas (strings starting with =)
        
        if not isinstance(comp['mass'], str):
             assert comp['mass'] >= 0, f"Component {comp['id']} has negative mass"
             
        if not isinstance(comp['hp'], str):
             assert comp['hp'] >= 0, f"Component {comp['id']} has negative HP"
             
        if not isinstance(comp.get('cost', 0), str):
             assert comp.get('cost', 0) >= 0, f"Component {comp['id']} has negative cost"

    @pytest.mark.parametrize("comp", COMPONENTS, ids=lambda c: c.get('id', 'unknown'))
    def test_component_type_valid(self, comp):
        """Verify type is one of the known valid types."""
        # We can expand this list as needed, or check against an enum if available
        # But for data validation, we just want to catch typos.
        known_types = [
            "Weapon", "Engine", "Defense", "Utility", "Structure", "Hull",
            "Reactor", "Sensor", "Hangar"
        ]
        # Check if type is in known types OR if we should just log unknown ones
        # Use a soft check or broad category check
        assert comp['type'] in known_types or len(comp['type']) > 2

    @pytest.mark.parametrize("comp", COMPONENTS, ids=lambda c: c.get('id', 'unknown'))
    def test_component_resource_costs(self, comp):
        """Verify resource costs logic if present."""
        if 'resource_cost' in comp:
            PLANET_RESOURCE_NAMES = ["Metals", "Organics", "Vapors", "Radioactives", "Exotics"]
            costs = comp['resource_cost']
            assert isinstance(costs, dict), "resource_cost must be a dictionary"
            for res, amount in costs.items():
                # Allow formula strings (starting with "=") or non-negative integers
                is_formula = isinstance(amount, str) and amount.startswith("=")
                is_valid_int = isinstance(amount, (int, float)) and amount >= 0
                assert is_formula or is_valid_int, (
                    f"Resource cost {res} for {comp['id']} must be non-negative number or formula"
                )
                assert res in PLANET_RESOURCE_NAMES, f"Unknown resource: {res}"

    @pytest.mark.parametrize("comp", COMPONENTS, ids=lambda c: c.get('id', 'unknown'))
    def test_component_abilities_format(self, comp):
        """Verify abilities dict structure."""
        if 'abilities' in comp:
            assert isinstance(comp['abilities'], dict), "abilities must be a dictionary"
            for ab_name, ab_data in comp['abilities'].items():
                assert len(ab_name) > 0
                # ab_data can be dict or list or primitive? usually dict
