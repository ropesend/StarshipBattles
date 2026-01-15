"""
Scenario Data Service

Handles loading and parsing ship and component data from JSON files for test scenarios.
Provides centralized access to test data files without tight coupling to UI.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from simulation_tests.logging_config import get_logger

logger = get_logger(__name__)


class ScenarioDataService:
    """Service for loading and managing test scenario data."""

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize scenario data service.

        Args:
            data_dir: Root data directory (defaults to simulation_tests/data)
        """
        if data_dir is None:
            # Default to simulation_tests/data
            self.data_dir = Path(__file__).parent.parent.parent / 'simulation_tests' / 'data'
        else:
            self.data_dir = Path(data_dir)

        self.ships_dir = self.data_dir / 'ships'
        self.components_file = self.data_dir / 'components.json'

        # Cache for components.json (loaded once on first access)
        self._components_cache: Optional[Dict[str, Dict[str, Any]]] = None

    def extract_ships_from_scenario(
        self,
        scenario_metadata,
        registry=None
    ) -> List[Dict[str, Any]]:
        """
        Extract ship information from test scenario metadata.

        Args:
            scenario_metadata: TestMetadata object containing conditions
            registry: Optional TestRegistry to get scenario info

        Returns:
            List[Dict]: [
                {
                    'role': 'Attacker',  # or 'Target', 'Ship1', etc.
                    'filename': 'Test_Attacker_Beam360_Low.json',
                    'ship_data': {...},  # Full ship JSON
                    'component_ids': ['test_beam_low_acc_1dmg', ...]  # All component IDs
                }
            ]
        """
        ships = []

        # Parse conditions for ship filenames
        # Format: "Attacker: Test_Attacker_Beam360_Low.json" or "Target: Test_Target_Stationary.json (mass=400)"
        for condition in scenario_metadata.conditions:
            if '.json' in condition and ':' in condition:
                parts = condition.split(':', 1)
                role = parts[0].strip()
                filename_part = parts[1].strip()

                # Extract only the .json filename (ignore anything after .json like "(mass=400)")
                json_end = filename_part.index('.json') + 5  # +5 for '.json'
                filename = filename_part[:json_end]

                # Load ship JSON file
                ship_path = self.ships_dir / filename

                try:
                    with open(ship_path, 'r') as f:
                        ship_data = json.load(f)

                    # Extract component IDs from layers
                    component_ids = []
                    for layer_name in ['CORE', 'ARMOR', 'HULL', 'WEAPONS', 'EXTERNAL', 'SURFACE', 'INNER', 'OUTER']:
                        layer = ship_data.get('layers', {}).get(layer_name, [])
                        for component in layer:
                            comp_id = component.get('id')
                            if comp_id:
                                component_ids.append(comp_id)

                    ships.append({
                        'role': role,
                        'filename': filename,
                        'ship_data': ship_data,
                        'component_ids': component_ids
                    })

                except FileNotFoundError:
                    logger.error(f"Ship file not found: {ship_path}")
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in ship file {filename}: {e}")
                except Exception as e:
                    logger.error(f"Error loading ship {filename}: {e}")

        return ships

    def load_component_data(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Load component JSON from components.json by ID.

        Args:
            component_id: Component ID (e.g., "test_beam_low_acc_1dmg")

        Returns:
            Dict: Component JSON data, or None if not found
        """
        # Load and cache components.json on first call
        if self._components_cache is None:
            try:
                with open(self.components_file, 'r') as f:
                    components_data = json.load(f)
                    # Extract the components list from the wrapper object
                    components_list = components_data.get('components', [])
                    # Convert list to dict for faster lookup
                    self._components_cache = {
                        comp['id']: comp
                        for comp in components_list
                    }
            except FileNotFoundError:
                logger.error(f"Components file not found: {self.components_file}")
                self._components_cache = {}
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in components file: {e}")
                self._components_cache = {}
            except Exception as e:
                logger.error(f"Error loading components.json: {e}")
                self._components_cache = {}

        return self._components_cache.get(component_id)

    def get_components_cache(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the full components cache.

        Returns:
            Dict mapping component IDs to component data
        """
        # Ensure cache is loaded
        if self._components_cache is None:
            self.load_component_data("dummy")  # Trigger cache load
        return self._components_cache or {}

    def build_validation_context(
        self,
        scenario_metadata
    ) -> Dict[str, Any]:
        """
        Build validation context from ship and component JSON files.

        This context is used by validation rules to check expected values
        against actual component data.

        Args:
            scenario_metadata: TestMetadata object

        Returns:
            Dict with 'attacker', 'target', etc. containing component data
        """
        context = {}

        # Extract ships from scenario
        ships = self.extract_ships_from_scenario(scenario_metadata)

        # Ensure components are loaded
        if self._components_cache is None:
            self.load_component_data("dummy")

        for ship_info in ships:
            role = ship_info['role'].lower()  # 'Attacker' -> 'attacker'
            ship_data = ship_info['ship_data']
            component_ids = ship_info['component_ids']

            # Build ship validation data structure
            ship_validation_data = {
                'mass': ship_data.get('expected_stats', {}).get('mass', 0)
            }

            # Extract weapon data from first component with weapon ability
            for comp_id in component_ids:
                comp_data = self._components_cache.get(comp_id)
                if comp_data and 'abilities' in comp_data:
                    abilities = comp_data['abilities']

                    # Check for BeamWeaponAbility
                    if 'BeamWeaponAbility' in abilities:
                        weapon_ability = abilities['BeamWeaponAbility']
                        ship_validation_data['weapon'] = {
                            'damage': weapon_ability.get('damage'),
                            'range': weapon_ability.get('range'),
                            'base_accuracy': weapon_ability.get('base_accuracy'),
                            'accuracy_falloff': weapon_ability.get('accuracy_falloff'),
                            'reload': weapon_ability.get('reload'),
                            'firing_arc': weapon_ability.get('firing_arc')
                        }
                        break  # Found weapon, use first one

                    # Check for ProjectileWeaponAbility
                    if 'ProjectileWeaponAbility' in abilities:
                        weapon_ability = abilities['ProjectileWeaponAbility']
                        ship_validation_data['weapon'] = {
                            'damage': weapon_ability.get('damage'),
                            'range': weapon_ability.get('range'),
                            'projectile_speed': weapon_ability.get('projectile_speed'),
                            'reload': weapon_ability.get('reload')
                        }
                        break

                    # Check for SeekerWeaponAbility
                    if 'SeekerWeaponAbility' in abilities:
                        weapon_ability = abilities['SeekerWeaponAbility']
                        ship_validation_data['weapon'] = {
                            'damage': weapon_ability.get('damage'),
                            'range': weapon_ability.get('range'),
                            'projectile_speed': weapon_ability.get('projectile_speed'),
                            'turning_rate': weapon_ability.get('turning_rate'),
                            'reload': weapon_ability.get('reload')
                        }
                        break

            context[role] = ship_validation_data

        return context

    def clear_cache(self):
        """Clear the components cache to force reload on next access."""
        self._components_cache = None
