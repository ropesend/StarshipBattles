"""Unit tests for game/ui/services/battle_ui_service.py

PROJ-142: TCG-UI2-009 - Tests for BattleUIService DTO conversion.
"""
import pytest
from unittest.mock import Mock, MagicMock


class TestProjectileColors:
    """Tests for PROJECTILE_COLORS mapping."""

    def test_projectile_colors_has_attack_types(self):
        """PROJECTILE_COLORS should have entries for AttackTypes."""
        from game.ui.services.battle_ui_service import PROJECTILE_COLORS
        from game.core.constants import AttackType

        # Check that main attack types are present
        assert AttackType.PROJECTILE in PROJECTILE_COLORS
        assert AttackType.MISSILE in PROJECTILE_COLORS
        assert AttackType.BEAM in PROJECTILE_COLORS

    def test_projectile_colors_are_rgb_tuples(self):
        """All projectile colors should be RGB tuples."""
        from game.ui.services.battle_ui_service import PROJECTILE_COLORS

        for attack_type, color in PROJECTILE_COLORS.items():
            assert isinstance(color, tuple), f"{attack_type} color is not tuple"
            assert len(color) == 3, f"{attack_type} color has {len(color)} components"

    def test_default_projectile_color_is_rgb_tuple(self):
        """DEFAULT_PROJECTILE_COLOR should be RGB tuple."""
        from game.ui.services.battle_ui_service import DEFAULT_PROJECTILE_COLOR

        assert isinstance(DEFAULT_PROJECTILE_COLOR, tuple)
        assert len(DEFAULT_PROJECTILE_COLOR) == 3


class TestBattleUIServiceInitialization:
    """Tests for BattleUIService initialization."""

    def test_initialization_stores_battle_service(self):
        """BattleUIService should store the battle service reference."""
        from game.ui.services.battle_ui_service import BattleUIService

        mock_battle_service = Mock()
        ui_service = BattleUIService(mock_battle_service)

        assert ui_service._battle_service is mock_battle_service


class TestGetEngineOrNone:
    """Tests for _get_engine_or_none helper method."""

    def test_returns_engine_when_available(self):
        """_get_engine_or_none returns engine when battle service has one."""
        from game.ui.services.battle_ui_service import BattleUIService

        mock_engine = Mock()
        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = mock_engine

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service._get_engine_or_none()

        assert result is mock_engine

    def test_returns_none_when_no_engine(self):
        """_get_engine_or_none returns None when no engine."""
        from game.ui.services.battle_ui_service import BattleUIService

        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = None

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service._get_engine_or_none()

        assert result is None


class TestGetShips:
    """Tests for get_ships method."""

    def test_get_ships_returns_empty_when_no_engine(self):
        """get_ships returns empty list when no engine."""
        from game.ui.services.battle_ui_service import BattleUIService

        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = None

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service.get_ships()

        assert result == []

    def test_get_ships_converts_to_dtos(self):
        """get_ships converts Ship objects to ShipDTOs."""
        from game.ui.services.battle_ui_service import BattleUIService
        from game.ui.interfaces.battle_ui import ShipDTO

        # Create mock ship with required attributes
        mock_ship = Mock()
        mock_ship.is_alive = True
        mock_ship.name = "TestShip"
        mock_ship.team_id = 0
        mock_ship.position = Mock(x=100, y=200)
        mock_ship.velocity = Mock(x=0, y=0)
        mock_ship.angle = 45.0
        mock_ship.is_derelict = False
        mock_ship.hp = 100
        mock_ship.max_hp = 100
        mock_ship.current_shields = 50
        mock_ship.max_shields = 50
        mock_ship.current_speed = 10
        mock_ship.max_speed = 20
        mock_ship.mass = 1000
        mock_ship.total_thrust = 500
        mock_ship.turn_speed = 30
        mock_ship.total_shots_fired = 5
        mock_ship.current_target = None
        mock_ship.secondary_targets = []
        mock_ship.max_targets = 1
        mock_ship.ai_strategy = "aggressive"
        mock_ship.source_file = None
        mock_ship.layers = {}

        # Mock resources
        mock_ship.resources = Mock()
        mock_ship.resources.get_all_resources.return_value = []

        mock_engine = Mock()
        mock_engine.ships = [mock_ship]

        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = mock_engine

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service.get_ships()

        assert len(result) == 1
        assert isinstance(result[0], ShipDTO)
        assert result[0].name == "TestShip"


class TestGetProjectiles:
    """Tests for get_projectiles method."""

    def test_get_projectiles_returns_empty_when_no_engine(self):
        """get_projectiles returns empty list when no engine."""
        from game.ui.services.battle_ui_service import BattleUIService

        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = None

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service.get_projectiles()

        assert result == []

    def test_get_projectiles_converts_to_dtos(self):
        """get_projectiles converts projectile objects to ProjectileDTOs."""
        from game.ui.services.battle_ui_service import BattleUIService
        from game.ui.interfaces.battle_ui import ProjectileDTO

        mock_proj = Mock()
        mock_proj.position = Mock(x=100, y=200)
        mock_proj.velocity = Mock(x=10, y=0)
        mock_proj.damage = 25
        mock_proj.type = None  # Will use default color

        mock_engine = Mock()
        mock_engine.projectiles = [mock_proj]

        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = mock_engine

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service.get_projectiles()

        assert len(result) == 1
        assert isinstance(result[0], ProjectileDTO)


class TestGetRecentBeams:
    """Tests for get_recent_beams method."""

    def test_get_recent_beams_returns_empty_when_no_engine(self):
        """get_recent_beams returns empty list when no engine."""
        from game.ui.services.battle_ui_service import BattleUIService

        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = None

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service.get_recent_beams()

        assert result == []

    def test_get_recent_beams_converts_to_dtos(self):
        """get_recent_beams converts beam dicts to BeamDTOs."""
        from game.ui.services.battle_ui_service import BattleUIService
        from game.ui.interfaces.battle_ui import BeamDTO

        mock_beam = {
            'start': Mock(x=0, y=0),
            'end': Mock(x=100, y=100),
            'color': (255, 255, 255)
        }

        mock_engine = Mock()
        mock_engine.recent_beams = [mock_beam]

        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = mock_engine

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service.get_recent_beams()

        assert len(result) == 1
        assert isinstance(result[0], BeamDTO)


class TestBattleStateQueries:
    """Tests for battle state query methods."""

    def test_is_battle_over_returns_true_when_no_engine(self):
        """is_battle_over returns True when no engine."""
        from game.ui.services.battle_ui_service import BattleUIService

        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = None

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service.is_battle_over()

        assert result is True

    def test_is_battle_over_delegates_to_engine(self):
        """is_battle_over delegates to engine.is_battle_over()."""
        from game.ui.services.battle_ui_service import BattleUIService

        mock_engine = Mock()
        mock_engine.is_battle_over.return_value = False

        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = mock_engine

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service.is_battle_over()

        assert result is False
        mock_engine.is_battle_over.assert_called_once()

    def test_get_winner_returns_none_when_no_engine(self):
        """get_winner returns None when no engine."""
        from game.ui.services.battle_ui_service import BattleUIService

        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = None

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service.get_winner()

        assert result is None

    def test_get_winner_delegates_to_engine(self):
        """get_winner delegates to engine.get_winner()."""
        from game.ui.services.battle_ui_service import BattleUIService

        mock_engine = Mock()
        mock_engine.get_winner.return_value = 0

        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = mock_engine

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service.get_winner()

        assert result == 0

    def test_get_tick_count_returns_zero_when_no_engine(self):
        """get_tick_count returns 0 when no engine."""
        from game.ui.services.battle_ui_service import BattleUIService

        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = None

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service.get_tick_count()

        assert result == 0

    def test_get_tick_count_returns_engine_counter(self):
        """get_tick_count returns engine.tick_counter."""
        from game.ui.services.battle_ui_service import BattleUIService

        mock_engine = Mock()
        mock_engine.tick_counter = 1000

        mock_battle_service = Mock()
        mock_battle_service.get_engine.return_value = mock_engine

        ui_service = BattleUIService(mock_battle_service)
        result = ui_service.get_tick_count()

        assert result == 1000


class TestConvertComponent:
    """Tests for _convert_component method."""

    def test_convert_component_creates_dto(self):
        """_convert_component creates ComponentDTO with correct data."""
        from game.ui.services.battle_ui_service import BattleUIService
        from game.ui.interfaces.battle_ui import ComponentDTO

        mock_comp = Mock()
        mock_comp.name = "Laser Gun"
        mock_comp.current_hp = 80
        mock_comp.max_hp = 100
        mock_comp.is_active = True
        mock_comp.status = Mock(name="ACTIVE")
        mock_comp.has_ability = Mock(return_value=True)
        mock_comp.shots_fired = 10
        mock_comp.shots_hit = 7

        mock_battle_service = Mock()
        ui_service = BattleUIService(mock_battle_service)

        result = ui_service._convert_component(mock_comp, "core")

        assert isinstance(result, ComponentDTO)
        assert result.name == "Laser Gun"
        assert result.layer == "core"
        assert result.current_hp == 80
        assert result.max_hp == 100
        assert result.is_active is True
        assert result.has_weapon is True


class TestConvertBeam:
    """Tests for _convert_beam method."""

    def test_convert_beam_with_missing_keys(self):
        """_convert_beam handles missing keys with defaults."""
        from game.ui.services.battle_ui_service import BattleUIService
        from game.ui.interfaces.battle_ui import BeamDTO
        from game.core.math import Vector2

        mock_battle_service = Mock()
        ui_service = BattleUIService(mock_battle_service)

        # Empty dict - should use defaults
        result = ui_service._convert_beam({})

        assert isinstance(result, BeamDTO)
        assert result.color == (255, 255, 255)  # Default color
