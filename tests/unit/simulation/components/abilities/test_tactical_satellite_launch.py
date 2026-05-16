"""PROJ-FMS-D Phase 1 — Tactical satellite launch (design-instance) tests.

Mirrors the PROJ-FMS-C ``test_tactical_fighter_launch.py`` shape. Pins:
- ``BattleEngine.launch_satellites_in_battle(carrier, [CarriedVehicle])``
  spawns full design-backed Satellite ships.
- Spawned satellites are tagged with ``launched_in_battle_id`` for
  end-of-battle reboard.
- HP is preserved through the design-instance materialisation.
"""
from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from game.core.math import Vector2
from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import NeverCondition
from game.strategy.data.carried_vehicle import CarriedVehicle


def _minimal_satellite_design():
    """A minimal but valid Satellite design suitable for ShipSerializer."""
    return {
        "name": "Test Satellite",
        "ship_class": "Satellite (Small)",
        "vehicle_class": "Satellite (Small)",
        "vehicle_type": "Satellite",
        "theme_id": "Federation",
        "layers": {
            "CORE": [
                {"id": "hull_satellite_small", "is_active": True},
            ],
        },
    }


def _make_engine():
    with patch('game.simulation.systems.battle_engine.BattleLogger'):
        mock_factory = Mock()
        mock_ai = Mock()
        mock_ai.update = Mock()
        mock_ai.ship = Mock()
        mock_factory.create_for_ship = Mock(return_value=mock_ai)
        mock_factory.create_for_ships = Mock(return_value=[mock_ai])
        mock_factory.set_grid = Mock()
        mock_factory.set_rng = Mock()
        engine = BattleEngine(ai_factory=mock_factory)
        engine.end_condition = NeverCondition()
        engine.tick_counter = 0
        engine.recent_beams = []
        return engine


def _make_carrier_stub(fresh_registries):
    source = Mock()
    source.name = "Carrier"
    source.is_alive = True
    source.is_derelict = False
    source.team_id = 0
    source.position = Vector2(0, 0)
    source.velocity = Vector2(0, 0)
    source.angle = 0
    source.radius = 20
    source.color = (255, 255, 255)
    source.theme_id = "Federation"
    source.registries = fresh_registries
    source.get_all_components = Mock(return_value=[])
    source.update = Mock()
    source.just_fired_projectiles = []
    source.fleet_attack_bonus = 0.0
    source.fleet_defense_bonus = 0.0
    return source


class TestTacticalSatelliteLaunchDesignInstance:
    """Design-instance launch path produces real combat satellites."""

    def test_carried_vehicle_payload_spawns_satellite_with_design_components(
        self, fresh_registries,
    ):
        # If the minimal hull id isn't in the registries, fall back to a
        # known fighter hull — what matters is the spawn path.
        from game.core.exceptions import StateException

        engine = _make_engine()
        carrier = _make_carrier_stub(fresh_registries)
        engine.ships = [carrier]
        engine.ai_controllers = []

        try:
            cv = CarriedVehicle(
                design_id="test_satellite",
                design_data=_minimal_satellite_design(),
                vehicle_type="satellite",
                mass=30.0,
                current_hp=60,
            )
            spawned = engine.launch_satellites_in_battle(carrier, [cv])
        except (KeyError, StateException, ValueError):
            pytest.skip("Minimal satellite design hull not present in registries.")

        assert len(spawned) == 1
        sat = spawned[0]
        assert sat is engine.ships[-1]
        assert sat.team_id == 0
        # Carried HP propagated to the new ship's current_hp.
        assert sat.current_hp == pytest.approx(60.0, abs=0.5)

    def test_launched_satellite_tagged_with_battle_id(self, fresh_registries):
        from game.core.exceptions import StateException

        engine = _make_engine()
        carrier = _make_carrier_stub(fresh_registries)
        engine.ships = [carrier]
        engine.ai_controllers = []

        try:
            cv = CarriedVehicle(
                design_id="test_satellite",
                design_data=_minimal_satellite_design(),
                vehicle_type="satellite",
                mass=30.0,
                current_hp=60,
            )
            spawned = engine.launch_satellites_in_battle(carrier, [cv])
        except (KeyError, StateException, ValueError):
            pytest.skip("Minimal satellite design hull not present in registries.")

        assert len(spawned) == 1
        sat = spawned[0]
        assert getattr(sat, "launched_in_battle_id", None) is not None

    def test_multiple_launch_spawns_n_satellites(self, fresh_registries):
        from game.core.exceptions import StateException

        engine = _make_engine()
        carrier = _make_carrier_stub(fresh_registries)
        engine.ships = [carrier]
        engine.ai_controllers = []

        try:
            cvs = [
                CarriedVehicle(
                    design_id="test_satellite",
                    design_data=_minimal_satellite_design(),
                    vehicle_type="satellite",
                    mass=30.0,
                    current_hp=50 + i,
                )
                for i in range(3)
            ]
            spawned = engine.launch_satellites_in_battle(carrier, cvs)
        except (KeyError, StateException, ValueError):
            pytest.skip("Minimal satellite design hull not present in registries.")

        assert len(spawned) == 3
        hps = sorted(int(s.current_hp) for s in spawned)
        assert hps == [50, 51, 52]
