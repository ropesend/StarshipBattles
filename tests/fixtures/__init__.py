"""
Shared test fixtures for Starship Battles.

This package provides reusable fixtures for tests, eliminating
boilerplate and hardcoded values.

Available modules:
    - paths: Path resolution utilities (project_root, data_dir, etc.)
    - ships: Ship creation fixtures (basic_ship, armed_ship, etc.)
    - components: Component creation fixtures
    - battle: Battle engine fixtures
    - test_scenarios: Combat Lab test scenario fixtures
    - ai: AI-related fixtures (strategy_manager_with_test_data)
"""
from tests.fixtures.paths import (
    get_project_root,
    get_data_dir,
    get_assets_dir,
    get_unit_test_data_dir,
)
from tests.fixtures.common import (
    initialized_ship_data,
    initialized_ship_data_with_modifiers,
)
from tests.fixtures.ships import (
    create_test_ship,
)
from tests.fixtures.components import (
    create_weapon,
    create_engine,
    create_shield,
    create_armor,
    create_bridge,
    create_crew_quarters,
    create_life_support,
)
from tests.fixtures.battle import (
    create_battle_engine,
    create_battle_engine_with_ships,
    create_mock_battle_engine,
    create_mock_battle_scene,
)
from tests.fixtures.test_scenarios import (
    create_test_metadata,
    create_mock_test_scenario,
    create_mock_test_registry,
    create_mock_test_runner,
    create_mock_test_history,
    create_scenario_info,
    create_sample_ship_data,
    create_sample_component_data,
)
from tests.fixtures.ai import (
    strategy_manager_with_test_data,
)

__all__ = [
    # Path utilities
    'get_project_root',
    'get_data_dir',
    'get_assets_dir',
    'get_unit_test_data_dir',
    # Ship data initialization
    'initialized_ship_data',
    'initialized_ship_data_with_modifiers',
    # Ship factory
    'create_test_ship',
    # Component factories
    'create_weapon',
    'create_engine',
    'create_shield',
    'create_armor',
    'create_bridge',
    'create_crew_quarters',
    'create_life_support',
    # Battle engine factories
    'create_battle_engine',
    'create_battle_engine_with_ships',
    'create_mock_battle_engine',
    'create_mock_battle_scene',
    # Test scenario factories
    'create_test_metadata',
    'create_mock_test_scenario',
    'create_mock_test_registry',
    'create_mock_test_runner',
    'create_mock_test_history',
    'create_scenario_info',
    'create_sample_ship_data',
    'create_sample_component_data',
    # AI fixtures
    'strategy_manager_with_test_data',
]
