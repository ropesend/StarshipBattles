"""
Tests for GameConfig and PlayerConfig
"""
import pytest
from game.strategy.engine.game_config import PlayerConfig, GameConfig
from game.core.exceptions import ValidationException


class TestPlayerConfig:
    """Tests for PlayerConfig dataclass"""

    def test_player_config_defaults(self):
        """PlayerConfig has sensible defaults"""
        config = PlayerConfig()

        assert config.name == "Empire"
        assert config.theme == "Federation"
        assert config.color == (128, 128, 128)
        assert config.is_human is True

    def test_player_config_with_custom_values(self):
        """PlayerConfig accepts custom name, theme, color, is_human"""
        config = PlayerConfig(
            name="Terran Command",
            theme="Atlantians",
            color=(0, 100, 255),
            is_human=False
        )

        assert config.name == "Terran Command"
        assert config.theme == "Atlantians"
        assert config.color == (0, 100, 255)
        assert config.is_human is False

    def test_player_config_serialization(self):
        """PlayerConfig can round-trip through to_dict/from_dict"""
        original = PlayerConfig(
            name="Test Empire",
            theme="Romulans",
            color=(255, 0, 0),
            is_human=True
        )

        data = original.to_dict()
        restored = PlayerConfig.from_dict(data)

        assert restored.name == original.name
        assert restored.theme == original.theme
        assert restored.color == original.color
        assert restored.is_human == original.is_human

    def test_player_config_serialization_preserves_types(self):
        """Serialization preserves correct types"""
        config = PlayerConfig(color=(100, 200, 50))

        data = config.to_dict()
        assert isinstance(data['color'], list)  # JSON-compatible

        restored = PlayerConfig.from_dict(data)
        assert isinstance(restored.color, tuple)  # Back to tuple


class TestGameConfig:
    """Tests for GameConfig dataclass"""

    def test_game_config_with_players_list(self):
        """GameConfig accepts list of PlayerConfig"""
        players = [
            PlayerConfig(name="Empire 1", theme="Federation", color=(0, 0, 255)),
            PlayerConfig(name="Empire 2", theme="Atlantians", color=(0, 200, 150)),
            PlayerConfig(name="Empire 3", theme="Romulans", color=(0, 180, 0)),
        ]

        config = GameConfig(players=players)

        assert len(config.players) == 3
        assert config.players[0].name == "Empire 1"
        assert config.players[1].theme == "Atlantians"
        assert config.players[2].color == (0, 180, 0)

    def test_game_config_save_name(self):
        """GameConfig stores user-provided save name"""
        config = GameConfig(save_name="MyFirstGame")

        assert config.save_name == "MyFirstGame"

    def test_game_config_default_players(self):
        """GameConfig has default 2-player setup"""
        config = GameConfig()

        assert len(config.players) == 2
        # First player
        assert config.players[0].name == "Terran Command"
        assert config.players[0].theme == "Federation"
        # Second player
        assert config.players[1].name == "Xeno Hive"
        assert config.players[1].theme == "Atlantians"

    def test_game_config_players_serialization(self):
        """GameConfig players list round-trips through serialization"""
        original = GameConfig(
            save_name="TestGame",
            players=[
                PlayerConfig(name="Alpha", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Beta", theme="Klingons", color=(0, 255, 0)),
            ],
            galaxy_radius=5000,
            system_count=30
        )

        data = original.to_dict()
        restored = GameConfig.from_dict(data)

        assert restored.save_name == original.save_name
        assert len(restored.players) == 2
        assert restored.players[0].name == "Alpha"
        assert restored.players[1].theme == "Klingons"
        assert restored.galaxy_radius == 5000
        assert restored.system_count == 30

    def test_game_config_rejects_more_than_4_players(self):
        """GameConfig validates max 4 players"""
        players = [
            PlayerConfig(name=f"Empire {i}", theme="Federation")
            for i in range(5)
        ]

        with pytest.raises(ValidationException) as exc_info:
            GameConfig(players=players)

        assert "maximum" in str(exc_info.value).lower()

    def test_game_config_rejects_empty_players(self):
        """GameConfig requires at least 1 player"""
        with pytest.raises(ValidationException) as exc_info:
            GameConfig(players=[])

        assert "minimum" in str(exc_info.value).lower()

    def test_game_config_galaxy_settings(self):
        """GameConfig preserves galaxy generation settings"""
        config = GameConfig(galaxy_radius=6000, system_count=40)

        assert config.galaxy_radius == 6000
        assert config.system_count == 40

    def test_game_config_theme_path_property(self):
        """GameConfig provides theme path for each player"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Test", theme="Romulans", color=(255, 0, 0))
            ]
        )

        theme_path = config.get_player_theme_path(0)

        assert "Romulans" in theme_path
        assert "ShipThemes" in theme_path

    def test_game_config_theme_path_invalid_index(self):
        """get_player_theme_path returns None for invalid index"""
        config = GameConfig()  # 2 players

        assert config.get_player_theme_path(5) is None
        assert config.get_player_theme_path(-1) is None


class TestGameConfigThemeDefaults:
    """Tests for theme auto-assignment constants"""

    def test_theme_defaults_constant_exists(self):
        """THEME_DEFAULTS constant is defined"""
        from game.strategy.engine.game_config import THEME_DEFAULTS

        assert len(THEME_DEFAULTS) == 4

    def test_theme_defaults_has_four_themes(self):
        """THEME_DEFAULTS has entries for all 4 player slots"""
        from game.strategy.engine.game_config import THEME_DEFAULTS

        themes = [t[0] for t in THEME_DEFAULTS]
        assert "Federation" in themes
        assert "Atlantians" in themes
        assert "Romulans" in themes
        assert "Klingons" in themes

    def test_theme_defaults_has_colors(self):
        """THEME_DEFAULTS includes color tuples"""
        from game.strategy.engine.game_config import THEME_DEFAULTS

        for theme, color in THEME_DEFAULTS:
            assert isinstance(color, tuple)
            assert len(color) == 3


class TestGameConfigGalaxyGeneration:
    """Tests for galaxy generation settings in GameConfig"""

    def test_default_galaxy_type_is_random(self):
        """Default galaxy_type should be 'random'"""
        config = GameConfig()
        assert config.galaxy_type == "random"

    def test_default_galaxy_seed_is_none(self):
        """Default galaxy_seed should be None"""
        config = GameConfig()
        assert config.galaxy_seed is None

    def test_galaxy_type_accepts_valid_types(self):
        """galaxy_type should accept all valid layout types"""
        valid_types = ["random", "cluster", "spiral", "barred_spiral",
                       "ring", "irregular", "diamond", "uniform"]

        for gtype in valid_types:
            config = GameConfig(galaxy_type=gtype)
            assert config.galaxy_type == gtype

    def test_galaxy_type_rejects_invalid_type(self):
        """galaxy_type should reject invalid types"""
        with pytest.raises(ValidationException) as exc_info:
            GameConfig(galaxy_type="invalid_galaxy")

        assert "galaxy" in str(exc_info.value).lower()

    def test_galaxy_seed_accepts_integer(self):
        """galaxy_seed should accept integer values"""
        config = GameConfig(galaxy_seed=12345)
        assert config.galaxy_seed == 12345

    def test_galaxy_seed_accepts_zero(self):
        """galaxy_seed should accept zero"""
        config = GameConfig(galaxy_seed=0)
        assert config.galaxy_seed == 0

    def test_galaxy_seed_accepts_large_values(self):
        """galaxy_seed should accept large integer values"""
        config = GameConfig(galaxy_seed=2**31 - 1)
        assert config.galaxy_seed == 2**31 - 1

    def test_galaxy_type_serialization(self):
        """galaxy_type should round-trip through serialization"""
        original = GameConfig(galaxy_type="spiral", galaxy_seed=42)

        data = original.to_dict()
        assert data['galaxy_type'] == "spiral"
        assert data['galaxy_seed'] == 42

        restored = GameConfig.from_dict(data)
        assert restored.galaxy_type == "spiral"
        assert restored.galaxy_seed == 42

    def test_galaxy_settings_default_on_missing_keys(self):
        """from_dict should use defaults for missing galaxy_type/seed"""
        data = {
            'galaxy_radius': 4000,
            'system_count': 25,
            'players': []
        }

        # Should not raise - uses defaults
        config = GameConfig.from_dict(data)
        assert config.galaxy_type == "random"
        assert config.galaxy_seed is None

    def test_galaxy_type_combined_with_other_settings(self):
        """galaxy_type works with other config settings"""
        config = GameConfig(
            galaxy_type="ring",
            galaxy_seed=999,
            galaxy_radius=8000,
            system_count=100,
            save_name="TestGalaxy"
        )

        assert config.galaxy_type == "ring"
        assert config.galaxy_seed == 999
        assert config.galaxy_radius == 8000
        assert config.system_count == 100
        assert config.save_name == "TestGalaxy"
