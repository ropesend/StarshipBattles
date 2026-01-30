"""Tests for IBattleUI protocol and DTOs.

PROJ-43 Phase 12: Tests for the battle UI interface and data transfer objects.

These tests verify:
1. DTOs can be created and have expected attributes
2. DTOs are immutable (frozen dataclasses)
3. IBattleUI protocol can be implemented
4. Protocol structural typing works correctly
"""
import pytest
from typing import List, Optional, Any
from dataclasses import FrozenInstanceError

from game.ui.interfaces.battle_ui import (
    IBattleUI,
    ShipDTO,
    ComponentDTO,
    ProjectileDTO,
    BeamDTO,
    ResourceDTO,
)
from game.core.math import Vector2


class TestResourceDTO:
    """Tests for ResourceDTO dataclass."""

    def test_create_resource_dto(self):
        """ResourceDTO can be created with required fields."""
        dto = ResourceDTO(
            name="fuel",
            current_value=50.0,
            max_value=100.0
        )
        assert dto.name == "fuel"
        assert dto.current_value == 50.0
        assert dto.max_value == 100.0

    def test_resource_dto_is_frozen(self):
        """ResourceDTO is immutable."""
        dto = ResourceDTO(name="fuel", current_value=50.0, max_value=100.0)
        with pytest.raises(FrozenInstanceError):
            dto.current_value = 75.0


class TestComponentDTO:
    """Tests for ComponentDTO dataclass."""

    def test_create_component_dto(self):
        """ComponentDTO can be created with required fields."""
        dto = ComponentDTO(
            name="Laser Cannon",
            layer="outer",
            current_hp=80.0,
            max_hp=100.0,
            is_active=True,
            status="active",
            has_weapon=True,
            shots_fired=10,
            shots_hit=7
        )
        assert dto.name == "Laser Cannon"
        assert dto.layer == "outer"
        assert dto.current_hp == 80.0
        assert dto.max_hp == 100.0
        assert dto.is_active is True
        assert dto.status == "active"
        assert dto.has_weapon is True
        assert dto.shots_fired == 10
        assert dto.shots_hit == 7

    def test_component_dto_is_frozen(self):
        """ComponentDTO is immutable."""
        dto = ComponentDTO(
            name="Engine",
            layer="inner",
            current_hp=100.0,
            max_hp=100.0,
            is_active=True,
            status="active",
            has_weapon=False,
            shots_fired=0,
            shots_hit=0
        )
        with pytest.raises(FrozenInstanceError):
            dto.current_hp = 50.0


class TestShipDTO:
    """Tests for ShipDTO dataclass."""

    def test_create_ship_dto_minimal(self):
        """ShipDTO can be created with minimal required fields."""
        dto = ShipDTO(
            id="ship_1",
            name="Test Ship",
            team_id=0,
            position=Vector2(100, 200),
            velocity=Vector2(10, 0),
            heading=0.0,
            is_alive=True,
            is_derelict=False,
            hp=100.0,
            max_hp=100.0,
            current_shields=50.0,
            max_shields=100.0,
            current_speed=50.0,
            max_speed=100.0,
            mass=1000.0,
            total_thrust=500.0,
            turn_speed=0.1,
            total_shots_fired=0,
            crew_onboard=10,
            crew_required=10,
            current_target_name=None,
            secondary_target_names=[],
            max_targets=1,
            ai_strategy="default",
            source_file=None,
            resources=[],
            components=[]
        )
        assert dto.id == "ship_1"
        assert dto.name == "Test Ship"
        assert dto.team_id == 0
        assert dto.position.x == 100
        assert dto.is_alive is True

    def test_ship_dto_with_components(self):
        """ShipDTO can contain ComponentDTO objects."""
        comp = ComponentDTO(
            name="Engine",
            layer="inner",
            current_hp=100.0,
            max_hp=100.0,
            is_active=True,
            status="active",
            has_weapon=False,
            shots_fired=0,
            shots_hit=0
        )
        dto = ShipDTO(
            id="ship_1",
            name="Test Ship",
            team_id=0,
            position=Vector2(0, 0),
            velocity=Vector2(0, 0),
            heading=0.0,
            is_alive=True,
            is_derelict=False,
            hp=100.0,
            max_hp=100.0,
            current_shields=0.0,
            max_shields=0.0,
            current_speed=0.0,
            max_speed=100.0,
            mass=1000.0,
            total_thrust=500.0,
            turn_speed=0.1,
            total_shots_fired=0,
            crew_onboard=10,
            crew_required=10,
            current_target_name=None,
            secondary_target_names=[],
            max_targets=1,
            ai_strategy="default",
            source_file=None,
            resources=[],
            components=[comp]
        )
        assert len(dto.components) == 1
        assert dto.components[0].name == "Engine"

    def test_ship_dto_is_frozen(self):
        """ShipDTO is immutable."""
        dto = ShipDTO(
            id="ship_1",
            name="Test Ship",
            team_id=0,
            position=Vector2(0, 0),
            velocity=Vector2(0, 0),
            heading=0.0,
            is_alive=True,
            is_derelict=False,
            hp=100.0,
            max_hp=100.0,
            current_shields=0.0,
            max_shields=0.0,
            current_speed=0.0,
            max_speed=100.0,
            mass=1000.0,
            total_thrust=500.0,
            turn_speed=0.1,
            total_shots_fired=0,
            crew_onboard=10,
            crew_required=10,
            current_target_name=None,
            secondary_target_names=[],
            max_targets=1,
            ai_strategy="default",
            source_file=None,
            resources=[],
            components=[]
        )
        with pytest.raises(FrozenInstanceError):
            dto.hp = 50.0


class TestProjectileDTO:
    """Tests for ProjectileDTO dataclass."""

    def test_create_projectile_dto(self):
        """ProjectileDTO can be created with required fields."""
        dto = ProjectileDTO(
            id="proj_1",
            position=Vector2(100, 200),
            velocity=Vector2(50, 0),
            color=(255, 200, 50),
            radius=4.0,
            damage=25.0,
            hp=10.0,
            max_hp=10.0,
            status="active",
            endurance=5.0,
            max_endurance=10.0,
            target_name=None,
            max_speed=100.0
        )
        assert dto.id == "proj_1"
        assert dto.position.x == 100
        assert dto.damage == 25.0
        assert dto.status == "active"

    def test_projectile_dto_is_frozen(self):
        """ProjectileDTO is immutable."""
        dto = ProjectileDTO(
            id="proj_1",
            position=Vector2(0, 0),
            velocity=Vector2(0, 0),
            color=(255, 255, 255),
            radius=4.0,
            damage=25.0,
            hp=10.0,
            max_hp=10.0,
            status="active",
            endurance=5.0,
            max_endurance=10.0,
            target_name=None,
            max_speed=100.0
        )
        with pytest.raises(FrozenInstanceError):
            dto.status = "hit"


class TestBeamDTO:
    """Tests for BeamDTO dataclass."""

    def test_create_beam_dto(self):
        """BeamDTO can be created with required fields."""
        dto = BeamDTO(
            start=Vector2(0, 0),
            end=Vector2(100, 100),
            color=(255, 0, 0)
        )
        assert dto.start.x == 0
        assert dto.end.x == 100
        assert dto.color == (255, 0, 0)

    def test_beam_dto_is_frozen(self):
        """BeamDTO is immutable."""
        dto = BeamDTO(
            start=Vector2(0, 0),
            end=Vector2(100, 100),
            color=(255, 0, 0)
        )
        with pytest.raises(FrozenInstanceError):
            dto.color = (0, 255, 0)


class TestIBattleUIProtocol:
    """Tests for IBattleUI protocol."""

    def test_protocol_is_importable(self):
        """IBattleUI can be imported."""
        from game.ui.interfaces.battle_ui import IBattleUI
        assert IBattleUI is not None

    def test_conforming_class_satisfies_protocol(self):
        """A class with correct methods satisfies the protocol."""
        class MockBattleUI:
            """A mock implementation of IBattleUI."""
            def get_ships(self) -> List[ShipDTO]:
                return []

            def get_projectiles(self) -> List[ProjectileDTO]:
                return []

            def get_recent_beams(self) -> List[BeamDTO]:
                return []

            def is_battle_over(self) -> bool:
                return False

            def get_winner(self) -> Optional[int]:
                return None

            def get_tick_count(self) -> int:
                return 0

        # Verify the mock can be used
        mock = MockBattleUI()
        assert mock.get_ships() == []
        assert mock.is_battle_over() is False
        assert mock.get_tick_count() == 0

    def test_protocol_runtime_checkable(self):
        """IBattleUI is runtime_checkable for isinstance checks."""
        class ValidImplementation:
            def get_ships(self) -> List[ShipDTO]:
                return []

            def get_projectiles(self) -> List[ProjectileDTO]:
                return []

            def get_recent_beams(self) -> List[BeamDTO]:
                return []

            def is_battle_over(self) -> bool:
                return False

            def get_winner(self) -> Optional[int]:
                return None

            def get_tick_count(self) -> int:
                return 0

        impl = ValidImplementation()
        # isinstance check should work with runtime_checkable
        assert isinstance(impl, IBattleUI)

    def test_invalid_implementation_fails_check(self):
        """A class missing methods doesn't satisfy the protocol."""
        class InvalidImplementation:
            """Missing required methods."""
            def get_ships(self) -> List[ShipDTO]:
                return []
            # Missing other required methods

        impl = InvalidImplementation()
        # isinstance check should fail
        assert not isinstance(impl, IBattleUI)
