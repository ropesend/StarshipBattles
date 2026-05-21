"""PROJ-FMS-C Phase 1 — Tactical fighter launch (design-instance) tests.

Covers:
- ``BattleEngine.launch_fighters_in_battle(carrier, [CarriedVehicle])``
  spawns full design-backed combat ships.
- Spawned fighters are tagged with ``launched_in_battle_id`` for
  end-of-battle reboard.
- PROJ-FMS-C audit Fix 1: the legacy ``fighter_class``-string launch
  path has been REMOVED. Payloads without a ``carried_vehicle`` field
  are dropped.
"""
from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from game.core.constants import AttackType
from game.core.math import Vector2
from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import NeverCondition
from game.strategy.data.carried_vehicle import CarriedVehicle


def _minimal_fighter_design():
    """A minimal but valid Fighter design suitable for ShipSerializer."""
    return {
        "name": "Test Fighter",
        "ship_class": "Fighter (Small)",
        "vehicle_class": "Fighter (Small)",
        "vehicle_type": "Fighter",
        "theme_id": "Federation",
        "layers": {
            "CORE": [
                {"id": "hull_fighter_small", "is_active": True},
                {"id": "fighter_cockpit", "is_active": True},
            ],
        },
    }


def _make_engine(fresh_registries):
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


class TestTacticalFighterLaunchDesignInstance:
    """Design-instance launch path replaces the class-string spawn."""

    def test_carried_vehicle_payload_spawns_fighter_with_design_components(
        self, fresh_registries
    ):
        engine = _make_engine(fresh_registries)
        carrier = _make_carrier_stub(fresh_registries)
        engine.ships = [carrier]
        engine.ai_controllers = []

        cv = CarriedVehicle(
            design_id="test_fighter",
            design_data=_minimal_fighter_design(),
            vehicle_type="fighter",
            mass=20.0,
            current_hp=75,
        )

        spawned = engine.launch_fighters_in_battle(carrier, [cv])
        assert len(spawned) == 1
        fighter = spawned[0]
        assert fighter is engine.ships[-1]
        assert fighter.team_id == 0
        # Carried HP propagated to the new ship's current_hp.
        assert fighter.current_hp == pytest.approx(75.0, abs=0.5)

    def test_launched_fighter_tagged_with_battle_id(self, fresh_registries):
        engine = _make_engine(fresh_registries)
        carrier = _make_carrier_stub(fresh_registries)
        engine.ships = [carrier]
        engine.ai_controllers = []

        cv = CarriedVehicle(
            design_id="test_fighter",
            design_data=_minimal_fighter_design(),
            vehicle_type="fighter",
            mass=20.0,
            current_hp=80,
        )

        spawned = engine.launch_fighters_in_battle(carrier, [cv])
        assert len(spawned) == 1
        fighter = spawned[0]
        # Tag is set; non-None.
        assert getattr(fighter, "launched_in_battle_id", None) is not None

    def test_multiple_launch_spawns_n_fighters(self, fresh_registries):
        engine = _make_engine(fresh_registries)
        carrier = _make_carrier_stub(fresh_registries)
        engine.ships = [carrier]
        engine.ai_controllers = []

        cvs = [
            CarriedVehicle(
                design_id="test_fighter",
                design_data=_minimal_fighter_design(),
                vehicle_type="fighter",
                mass=20.0,
                current_hp=70 + i,
            )
            for i in range(3)
        ]

        spawned = engine.launch_fighters_in_battle(carrier, cvs)
        assert len(spawned) == 3
        hps = sorted(int(s.current_hp) for s in spawned)
        assert hps == [70, 71, 72]


class TestLaunchInBattleSharedImplementation:
    """Cluster 8 (PROJ-465): ``launch_fighters_in_battle`` and
    ``launch_satellites_in_battle`` share one implementation.

    Both public methods must remain (AI carrier controller resolves them
    by name via ``getattr``) and must spawn identically for the same
    inputs — they differ only in docstring.
    """

    def test_both_methods_spawn_identically(self, fresh_registries):
        engine = _make_engine(fresh_registries)
        carrier = _make_carrier_stub(fresh_registries)
        engine.ships = [carrier]
        engine.ai_controllers = []

        cv = CarriedVehicle(
            design_id="test_fighter",
            design_data=_minimal_fighter_design(),
            vehicle_type="fighter",
            mass=20.0,
            current_hp=77,
        )

        spawned_f = engine.launch_fighters_in_battle(carrier, [cv])
        spawned_s = engine.launch_satellites_in_battle(carrier, [cv])

        assert len(spawned_f) == 1
        assert len(spawned_s) == 1
        assert spawned_f[0].current_hp == pytest.approx(spawned_s[0].current_hp)

    def test_both_public_names_present(self, fresh_registries):
        engine = _make_engine(fresh_registries)
        assert callable(getattr(engine, "launch_fighters_in_battle"))
        assert callable(getattr(engine, "launch_satellites_in_battle"))


class TestLegacyFighterClassLaunchRemoved:
    """PROJ-FMS-C audit Fix 1: the legacy class-string LAUNCH path is gone.

    Pre-fix the legacy path spawned a generic ship and emitted a
    deprecation warning. Post-fix the payload is rejected outright —
    only the design-instance ``carried_vehicle`` path produces a spawn.
    """

    def test_legacy_fighter_class_payload_is_dropped(
        self, fresh_registries,
    ):
        from game.simulation.systems import attack_processor

        engine = _make_engine(fresh_registries)
        carrier = _make_carrier_stub(fresh_registries)
        engine.ships = [carrier]
        engine.ai_controllers = []

        ships_before = list(engine.ships)
        legacy_attack = {
            'type': AttackType.LAUNCH,
            'source': carrier,
            'hangar': Mock(),
            'fighter_class': 'Fighter (Small)',  # no ``carried_vehicle``
            'origin': Vector2(0, 0),
        }

        attack_processor.process_launch_attack(engine, legacy_attack)

        # No new ship — the legacy class-string spawn path was removed.
        assert engine.ships == ships_before
