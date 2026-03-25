"""Round-trip tests for GameConfig and PlayerConfig serialization (PROJ-223 Phase 2)."""

import pytest

from game.strategy.engine.game_config import GameConfig, PlayerConfig
from tests.fixtures.strategy_entities import (
    create_test_game_config,
    create_test_player_config,
    create_test_race_config,
)
from tests.integration.save_load.conftest import assert_round_trip_fidelity, assert_field_preserved


class TestPlayerConfigRoundTrip:
    """PlayerConfig round-trip serialization tests."""

    def test_to_dict_includes_all_fields(self):
        pc = create_test_player_config()
        d = pc.to_dict()
        assert 'name' in d
        assert 'theme' in d
        assert 'color' in d
        assert 'is_human' in d

    def test_from_dict_restores_all_fields(self):
        original = create_test_player_config()
        d = original.to_dict()
        restored = PlayerConfig.from_dict(d)
        assert restored.name == original.name
        assert restored.theme == original.theme
        assert restored.is_human == original.is_human

    def test_optional_race_fields_preserved(self):
        pc = create_test_player_config(race_id="aliens", flag_id="flag_x", portrait_id="port_y")
        d = pc.to_dict()
        restored = PlayerConfig.from_dict(d)
        assert restored.race_id == "aliens"
        assert restored.flag_id == "flag_x"
        assert restored.portrait_id == "port_y"

    def test_color_tuple_list_conversion(self):
        pc = create_test_player_config(color=(0, 100, 255))
        d = pc.to_dict()
        assert isinstance(d['color'], list)
        restored = PlayerConfig.from_dict(d)
        assert restored.color == (0, 100, 255)

    def test_with_race_config(self):
        rc = create_test_race_config()
        pc = create_test_player_config(race_config=rc)
        d = pc.to_dict()
        assert 'race_config' in d
        restored = PlayerConfig.from_dict(d)
        assert restored.race_config is not None
        assert restored.race_config.race_id == rc.race_id

    def test_round_trip_field_level(self):
        assert_round_trip_fidelity(create_test_player_config(), PlayerConfig)


class TestGameConfigRoundTrip:
    """GameConfig round-trip serialization tests."""

    def test_to_dict_includes_all_fields(self):
        gc = create_test_game_config()
        d = gc.to_dict()
        expected = ['galaxy_radius', 'system_count', 'galaxy_type',
                    'galaxy_seed', 'save_name', 'players']
        for key in expected:
            assert key in d, f"Missing key: {key}"

    def test_from_dict_restores_all_fields(self):
        original = create_test_game_config()
        d = original.to_dict()
        restored = GameConfig.from_dict(d)
        assert restored.galaxy_radius == original.galaxy_radius
        assert restored.system_count == original.system_count
        assert restored.galaxy_type == original.galaxy_type
        assert restored.galaxy_seed == original.galaxy_seed
        assert restored.save_name == original.save_name

    def test_nested_player_configs_round_trip(self):
        gc = create_test_game_config(num_players=3)
        d = gc.to_dict()
        restored = GameConfig.from_dict(d)
        assert len(restored.players) == 3
        for orig, rest in zip(gc.players, restored.players):
            assert rest.name == orig.name
            assert rest.theme == orig.theme

    def test_round_trip_field_level(self):
        assert_round_trip_fidelity(create_test_game_config(), GameConfig)
