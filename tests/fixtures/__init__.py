"""
Shared test fixtures for Starship Battles.

This package provides reusable fixtures for tests, eliminating
boilerplate and hardcoded values.

Available modules:
    - paths: Path resolution utilities (project_root, data_dir, etc.)
    - ships: Ship creation fixtures (basic_ship, armed_ship, etc.)
    - components: Component creation fixtures
    - battle: Battle engine fixtures
"""
from tests.fixtures.paths import (
    get_project_root,
    get_data_dir,
    get_assets_dir,
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

__all__ = [
    # Path utilities
    'get_project_root',
    'get_data_dir',
    'get_assets_dir',
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
]
