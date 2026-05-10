"""Characterization tests for BattleUIService (PROJ-340).

Pins observed conversion behavior of the simulation -> UI DTO seam at
``game/ui/services/battle_ui_service.py``. This module mocks the
``BattleService`` directly; sibling tests under ``battle_ui_service/``
already cover broader integration behavior, so the behaviors here are
intentionally narrowed to the seam-specific contracts called out in the
PROJ-340 phase-1 checklist.
"""
from __future__ import annotations

from unittest.mock import Mock

import pytest

from game.core.constants import AttackType
from game.core.math import Vector2
from game.ui.colors import WHITE
from game.ui.interfaces.battle_ui import ShipDTO
from game.ui.services.battle_ui_service import (
    BattleUIService,
    DEFAULT_PROJECTILE_COLOR,
    PROJECTILE_COLORS,
)


def _make_resource_holder(resources):
    """Build a Mock matching the ``ship.resources`` API used during conversion."""
    holder = Mock()
    holder.get_all_resources.return_value = resources
    return holder


def _make_minimal_ship(**overrides):
    """Build a Mock ship with the attribute surface ``_convert_ship`` reads.

    Defaults are tuned so a single ship round-trips to a valid ShipDTO without
    further setup. Tests can override individual fields via ``**overrides``.
    """
    ship = Mock()
    ship.id = "ship-1"
    ship.name = "Falcon"
    ship.team_id = 0
    ship.position = Vector2(10.0, 20.0)
    ship.velocity = Vector2(0.0, 0.0)
    ship.angle = 0.42
    ship.is_alive = True
    ship.is_derelict = False
    ship.hp = 50.0
    ship.max_hp = 100.0
    ship.current_shields = 25.0
    ship.max_shields = 50.0
    ship.current_speed = 5.0
    ship.max_speed = 10.0
    ship.mass = 100.0
    ship.total_thrust = 200.0
    ship.turn_speed = 0.5
    ship.total_shots_fired = 0
    ship.crew_onboard = 5
    ship.crew_required = 5
    ship.current_target = None
    ship.secondary_targets = []
    ship.max_targets = 1
    ship.movement_policy = "brawl"
    ship.source_file = "ships/falcon.json"
    ship.layers = {}
    ship.resources = _make_resource_holder([])
    for k, v in overrides.items():
        setattr(ship, k, v)
    return ship


def _service_with_engine(engine):
    """Wrap a Mock engine in a BattleUIService for testing."""
    battle_service = Mock()
    battle_service.get_engine.return_value = engine
    return BattleUIService(battle_service)


class TestEngineNoneFallback:
    def test_get_ships_returns_empty_list_when_engine_is_none(self):
        service = _service_with_engine(None)
        assert service.get_ships() == []


class TestShipConversion:
    def test_get_ships_converts_each_engine_ship_to_shipdto(self):
        engine = Mock()
        engine.ships = [_make_minimal_ship(id="a"), _make_minimal_ship(id="b")]
        service = _service_with_engine(engine)

        dtos = service.get_ships()

        assert len(dtos) == 2
        assert all(isinstance(dto, ShipDTO) for dto in dtos)
        assert [dto.id for dto in dtos] == ["a", "b"]

    def test_convert_ship_uses_ship_angle_as_dto_heading(self):
        ship = _make_minimal_ship(angle=1.234)
        engine = Mock()
        engine.ships = [ship]
        service = _service_with_engine(engine)

        dto = service.get_ships()[0]

        # Production maps ship.angle -> dto.heading verbatim.
        assert dto.heading == pytest.approx(1.234)

    def test_convert_ship_resolves_current_target_name_to_string(self):
        target = Mock()
        target.name = "Phantom"
        ship = _make_minimal_ship(current_target=target)
        engine = Mock()
        engine.ships = [ship]
        service = _service_with_engine(engine)

        dto = service.get_ships()[0]

        assert dto.current_target_name == "Phantom"

    def test_convert_ship_lists_secondary_target_names_in_order(self):
        sec1, sec2, sec3 = Mock(), Mock(), Mock()
        sec1.name = "Alpha"
        sec2.name = "Beta"
        sec3.name = "Gamma"
        ship = _make_minimal_ship(secondary_targets=[sec1, sec2, sec3])
        engine = Mock()
        engine.ships = [ship]
        service = _service_with_engine(engine)

        dto = service.get_ships()[0]

        assert dto.secondary_target_names == ["Alpha", "Beta", "Gamma"]


def _make_projectile(proj_type=AttackType.PROJECTILE):
    """Build a Mock projectile with the attribute surface _convert_projectile reads."""
    proj = Mock()
    proj.id = "p-1"
    proj.position = Vector2(0.0, 0.0)
    proj.velocity = Vector2(1.0, 0.0)
    proj.radius = 1.0
    proj.damage = 5.0
    proj.hp = 1.0
    proj.max_hp = 1.0
    proj.status = "active"
    proj.endurance = 10.0
    proj.max_endurance = 10.0
    proj.target = None
    proj.max_speed = 50.0
    proj.type = proj_type
    return proj


class TestProjectileConversion:
    def test_convert_projectile_uses_projectile_colors_mapping_for_type(self):
        proj = _make_projectile(proj_type=AttackType.MISSILE)
        engine = Mock()
        engine.ships = []
        engine.projectiles = [proj]
        service = _service_with_engine(engine)

        dto = service.get_projectiles()[0]

        assert dto.color == PROJECTILE_COLORS[AttackType.MISSILE]

    def test_convert_projectile_falls_back_to_default_color_for_unknown_type(self):
        proj = _make_projectile(proj_type=AttackType.LAUNCH)  # not in PROJECTILE_COLORS
        engine = Mock()
        engine.ships = []
        engine.projectiles = [proj]
        service = _service_with_engine(engine)

        dto = service.get_projectiles()[0]

        assert dto.color == DEFAULT_PROJECTILE_COLOR


class TestBeamConversion:
    def test_convert_beam_defaults_missing_color_to_white(self):
        engine = Mock()
        engine.ships = []
        engine.projectiles = []
        engine.recent_beams = [
            {"start": Vector2(1.0, 2.0), "end": Vector2(3.0, 4.0)}
        ]
        service = _service_with_engine(engine)

        dto = service.get_recent_beams()[0]

        assert dto.color == WHITE
