"""
Data extraction utilities for TestLabScreen.

This module contains pure data loading operations with no UI dependencies:
- get_test_data_dir(): Locate the combat_lab/data directory
- TestLabDataExtractor: Load ship and component data from test scenarios

Extracted from screen.py to reduce file size and improve testability.
"""
import os

from game.core.json_utils import load_json
from combat_lab.logging_config import get_logger

logger = get_logger(__name__)


def get_test_data_dir():
    """
    Get the path to combat_lab/data directory.

    This function provides a single source of truth for locating test data files,
    avoiding incorrect relative path construction from different modules.

    Returns:
        str: Absolute path to combat_lab/data directory
    """
    # Navigate from game/ui/screens/test_lab/ to project root (4 levels up)
    # Then into combat_lab/data
    current_dir = os.path.dirname(__file__)  # game/ui/screens/test_lab
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))  # project root
    return os.path.join(project_root, 'combat_lab', 'data')


class TestLabDataExtractor:
    """
    Handles data extraction operations for TestLabScreen.

    Loads ship and component data from test scenarios without any UI dependencies.
    """

    def __init__(self, registry):
        """
        Initialize the data extractor.

        Args:
            registry: TestRegistry instance for looking up test scenarios
        """
        self.registry = registry
        self._components_cache = None

    def extract_ships(self, test_id):
        """
        Extract ship information from test scenario metadata.

        Args:
            test_id: Test ID (e.g., "BEAM360-001")

        Returns:
            List[Dict]: [
                {
                    'role': 'Attacker',  # or 'Target', 'Ship', 'Low Mass', etc.
                    'filename': 'Test_Attacker_Beam360_Low.json',
                    'ship_data': {...},  # Full ship JSON
                    'component_ids': ['test_beam_low_acc_1dmg', ...]  # All component IDs
                }
            ]
        """
        scenario_info = self.registry.get_by_id(test_id)

        if not scenario_info:
            return []

        metadata = scenario_info['metadata']
        ships = []

        # Parse conditions for ship filenames
        # Supported formats:
        # - "Attacker: Test_Attacker_Beam360_Low.json"
        # - "Target: Test_Target_Stationary.json (mass=400)"
        # - "Ship: Test_Engine_1x_LowMass.json"
        # - "Test 3 ships: LowMass (40), MedMass (2220), HighMass (10220)"
        for condition in metadata.conditions:
            if '.json' in condition and ':' in condition:
                parts = condition.split(':', 1)
                role = parts[0].strip()
                filename_part = parts[1].strip()

                # Extract only the .json filename (ignore anything after .json like "(mass=400)")
                json_end = filename_part.index('.json') + 5  # +5 for '.json'
                filename = filename_part[:json_end]

                # Load ship JSON file
                ship_path = os.path.join(
                    get_test_data_dir(),
                    'ships',
                    filename
                )

                ship_data = load_json(ship_path)
                if ship_data is None:
                    logger.error(f"Failed to load ship file: {ship_path}")
                    continue

                # Extract component IDs from layers
                component_ids = self._extract_component_ids(ship_data)

                ships.append({
                    'role': role,
                    'filename': filename,
                    'ship_data': ship_data,
                    'component_ids': component_ids
                })

        # Also check for scenario class attributes that specify ship files
        # PropulsionScenario uses 'ship_file' attribute
        scenario_cls = scenario_info.get('class')
        if scenario_cls and not ships:
            # Check for single ship_file attribute
            if hasattr(scenario_cls, 'ship_file') and scenario_cls.ship_file:
                filename = scenario_cls.ship_file
                ship_path = os.path.join(
                    get_test_data_dir(),
                    'ships',
                    filename
                )
                ship_data = load_json(ship_path)
                if ship_data:
                    component_ids = self._extract_component_ids(ship_data)

                    ships.append({
                        'role': 'Ship',
                        'filename': filename,
                        'ship_data': ship_data,
                        'component_ids': component_ids
                    })

        # Handle PROP-002 multi-ship test by checking condition format
        if not ships and 'Test 3 ships' in str(metadata.conditions):
            # PROP-002 uses multiple ships: LowMass, MedMass, HighMass
            multi_ship_files = [
                ('Low Mass', 'Test_Engine_1x_LowMass.json'),
                ('Med Mass', 'Test_Engine_1x_MedMass.json'),
                ('High Mass', 'Test_Engine_1x_HighMass.json'),
            ]
            for role, filename in multi_ship_files:
                ship_path = os.path.join(
                    get_test_data_dir(),
                    'ships',
                    filename
                )
                ship_data = load_json(ship_path)
                if ship_data:
                    component_ids = self._extract_component_ids(ship_data)

                    ships.append({
                        'role': role,
                        'filename': filename,
                        'ship_data': ship_data,
                        'component_ids': component_ids
                    })

        return ships

    def _extract_component_ids(self, ship_data):
        """
        Extract component IDs from ship layer data.

        Args:
            ship_data: Ship JSON data with 'layers' key

        Returns:
            List[str]: List of component IDs found in CORE, ARMOR, HULL layers
        """
        component_ids = []
        for layer_name in ['CORE', 'ARMOR', 'HULL']:
            layer = ship_data.get('layers', {}).get(layer_name, [])
            for component in layer:
                comp_id = component.get('id')
                if comp_id:
                    component_ids.append(comp_id)
        return component_ids

    def load_component(self, component_id):
        """
        Load component JSON from components.json by ID.

        Args:
            component_id: Component ID (e.g., "test_beam_low_acc_1dmg")

        Returns:
            Dict: Component JSON data, or None if not found
        """
        # Load and cache components.json on first call
        if self._components_cache is None:
            components_path = os.path.join(
                get_test_data_dir(),
                'components.json'
            )

            components_data = load_json(components_path, default={})
            # Extract the components list from the wrapper object
            components_list = components_data.get('components', [])
            # Convert list to dict for faster lookup
            self._components_cache = {
                comp['id']: comp
                for comp in components_list
            }

        return self._components_cache.get(component_id)

    def get_components_cache(self):
        """Get the components cache dictionary.

        Ensures the cache is populated before returning. This provides
        public access to the cache without exposing the private attribute.

        Returns:
            Dict[str, Dict]: Mapping of component ID to component data
        """
        if self._components_cache is None:
            # Trigger cache population by loading a dummy component
            self.load_component("__ensure_cache__")
        return self._components_cache or {}
