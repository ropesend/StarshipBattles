"""
Conftest for fixture tests.

Imports fixtures so they're available to fixture tests.
"""
from tests.fixtures.paths import project_root, data_dir, assets_dir, test_data_dir
from tests.fixtures.ships import (
    empty_ship,
    basic_ship,
    armed_ship,
    shielded_ship,
    fully_equipped_ship,
    two_opposing_ships,
)
from tests.fixtures.components import (
    weapon_component,
    engine_component,
    shield_component,
    armor_component,
    bridge_component,
    crew_quarters_component,
    life_support_component,
)
from tests.fixtures.battle import (
    battle_engine,
    battle_engine_with_ships,
    mock_battle_engine,
    mock_battle_scene,
)
