"""Tests for BattleUIService entity conversion.

Tests for converting simulation objects to DTOs:
- Ships to ShipDTO
- Projectiles to ProjectileDTO
- Beams to BeamDTO

PROJ-157: Added TestProjectileColors from flat test file.
"""
import pytest
from unittest.mock import Mock

from game.ui.services.battle_ui_service import (
    BattleUIService,
    PROJECTILE_COLORS,
    DEFAULT_PROJECTILE_COLOR,
)
from game.core.constants import AttackType
from game.ui.interfaces.battle_ui import (
    IBattleUI,
    ShipDTO,
    ProjectileDTO,
    BeamDTO,
    ComponentDTO,
)
from game.core.math import Vector2
from game.simulation.entities.layer_data import LayerData


class TestProjectileColors:
    """Tests for PROJECTILE_COLORS mapping (migrated from flat file)."""

    def test_projectile_colors_has_attack_types(self):
        """PROJECTILE_COLORS should have entries for AttackTypes."""
        assert AttackType.PROJECTILE in PROJECTILE_COLORS
        assert AttackType.MISSILE in PROJECTILE_COLORS
        assert AttackType.BEAM in PROJECTILE_COLORS

    def test_projectile_colors_are_rgb_tuples(self):
        """All projectile colors should be RGB tuples."""
        for attack_type, color in PROJECTILE_COLORS.items():
            assert isinstance(color, tuple), f"{attack_type} color is not tuple"
            assert len(color) == 3, f"{attack_type} color has {len(color)} components"

    def test_default_projectile_color_is_rgb_tuple(self):
        """DEFAULT_PROJECTILE_COLOR should be RGB tuple."""
        assert isinstance(DEFAULT_PROJECTILE_COLOR, tuple)
        assert len(DEFAULT_PROJECTILE_COLOR) == 3


class TestBattleUIServiceCreation:
    """Tests for BattleUIService creation and setup."""

    def test_create_service_with_battle_service(self):
        """BattleUIService can be created with a BattleService."""
        mock_service = Mock()
        mock_service.get_engine.return_value = None

        service = BattleUIService(mock_service)
        assert service is not None

    def test_service_satisfies_protocol(self):
        """BattleUIService satisfies IBattleUI protocol."""
        mock_service = Mock()
        mock_service.get_engine.return_value = None

        service = BattleUIService(mock_service)
        assert isinstance(service, IBattleUI)


class TestBattleUIServiceShipConversion:
    """Tests for ship to ShipDTO conversion."""

    def test_get_ships_returns_list_of_dtos(self, mock_battle_service, mock_ship):
        """get_ships() returns a list of ShipDTO objects."""
        service = BattleUIService(mock_battle_service)
        ships = service.get_ships()

        assert len(ships) == 1
        assert isinstance(ships[0], ShipDTO)

    def test_ship_dto_has_correct_basic_properties(self, mock_battle_service, mock_ship):
        """ShipDTO has correct values from the ship object."""
        service = BattleUIService(mock_battle_service)
        dto = service.get_ships()[0]

        assert dto.name == "Test Ship"
        assert dto.team_id == 0
        assert dto.position.x == 100
        assert dto.position.y == 200
        assert dto.is_alive is True
        assert dto.hp == 80.0
        assert dto.max_hp == 100.0

    def test_ship_dto_converts_resources(self, mock_battle_service, mock_ship):
        """ShipDTO includes resource DTOs."""
        service = BattleUIService(mock_battle_service)
        dto = service.get_ships()[0]

        assert len(dto.resources) == 1
        assert dto.resources[0].name == "fuel"
        assert dto.resources[0].current_value == 50.0

    def test_ship_with_target_includes_target_name(self, mock_battle_service, mock_ship):
        """Ship with a target has target name in DTO."""
        target = Mock()
        target.name = "Enemy Ship"
        mock_ship.current_target = target

        service = BattleUIService(mock_battle_service)
        dto = service.get_ships()[0]

        assert dto.current_target_name == "Enemy Ship"

    def test_ship_with_components_converts_to_dto(self, mock_battle_service, mock_ship):
        """Ship components are converted to ComponentDTO."""
        # Add mock component
        comp = Mock()
        comp.name = "Laser"
        comp.current_hp = 50.0
        comp.max_hp = 100.0
        comp.is_active = True
        comp.status = Mock()
        comp.status.name = "ACTIVE"
        comp.has_ability = Mock(return_value=True)
        comp.shots_fired = 10
        comp.shots_hit = 7

        mock_ship.layers = {
            Mock(value="outer"): LayerData(components=[comp])
        }

        service = BattleUIService(mock_battle_service)
        dto = service.get_ships()[0]

        assert len(dto.components) == 1
        assert dto.components[0].name == "Laser"
        assert dto.components[0].has_weapon is True


class TestBattleUIServiceProjectileConversion:
    """Tests for projectile to ProjectileDTO conversion."""

    def test_get_projectiles_returns_list_of_dtos(self, mock_battle_service_with_projectile):
        """get_projectiles() returns a list of ProjectileDTO objects."""
        service = BattleUIService(mock_battle_service_with_projectile)
        projectiles = service.get_projectiles()

        assert len(projectiles) == 1
        assert isinstance(projectiles[0], ProjectileDTO)

    def test_projectile_dto_has_correct_properties(self, mock_battle_service_with_projectile):
        """ProjectileDTO has correct values from the projectile object."""
        service = BattleUIService(mock_battle_service_with_projectile)
        dto = service.get_projectiles()[0]

        assert dto.position.x == 50
        assert dto.damage == 25.0
        assert dto.status == "active"

    def test_projectile_with_target_includes_name(self, mock_battle_service_with_projectile, mock_projectile):
        """Projectile with target has target name in DTO."""
        target = Mock()
        target.name = "Target Ship"
        mock_projectile.target = target

        service = BattleUIService(mock_battle_service_with_projectile)
        dto = service.get_projectiles()[0]

        assert dto.target_name == "Target Ship"


class TestBattleUIServiceBeamConversion:
    """Tests for beam to BeamDTO conversion."""

    def test_get_recent_beams_returns_list_of_dtos(self, mock_battle_service_with_beams):
        """get_recent_beams() returns a list of BeamDTO objects."""
        service = BattleUIService(mock_battle_service_with_beams)
        beams = service.get_recent_beams()

        assert len(beams) == 1
        assert isinstance(beams[0], BeamDTO)

    def test_beam_dto_has_correct_properties(self, mock_battle_service_with_beams):
        """BeamDTO has correct values from the beam dict."""
        service = BattleUIService(mock_battle_service_with_beams)
        dto = service.get_recent_beams()[0]

        assert dto.start.x == 0
        assert dto.end.x == 100
        assert dto.color == (255, 0, 0)
