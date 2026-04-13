"""Tests for SimulationBattleResolver environmental effects (PROJ-189 + PROJ-269).

PROJ-269 Phase 6 Task 6.5/6.11: the adapter no longer mutates ship
shields pre-battle. Environmental effects flow through the
`ModifierStack` on the compiled `BattleSpec` as global entries with
placeholder effects (Phase 5.5 semantics — real effect evaluation is
post-PROJ-269 content work).
"""

from unittest.mock import MagicMock, patch

import pytest


class _MockShipInstance:
    def __init__(self, instance_id="i"):
        self.instance_id = instance_id
        self.design_id = f"design-{instance_id}"
        self.design_data = {"theme_id": "Federation"}
        self.name = f"Ship-{instance_id}"
        self.components = {}

    def is_combat_capable(self):
        return True

    def to_ship(self, pos, team_id=0, registries=None):
        ship = MagicMock()
        ship.instance_id = self.instance_id
        return ship


def _make_fleet(fleet_id, ships):
    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.ships = ships
    fleet.task_forces = []
    return fleet


def _make_outcome():
    from game.simulation.battle_outcome import ShipStatus

    outcome = MagicMock()
    outcome.duration_ticks = 100
    team0 = MagicMock()
    team0.team_id = 0
    team0.ships = []
    team1 = MagicMock()
    team1.team_id = 1
    team1.ships = [MagicMock(status=ShipStatus.SURVIVED)]
    outcome.teams = (team0, team1)
    return outcome


class TestSimulationBattleResolverEnvironmentalEffects:
    """Environmental effects flow through the ModifierStack on the spec."""

    def test_resolve_battle_accepts_environmental_effects(self):
        """resolve_battle accepts optional environmental_effects parameter."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from game.strategy.services.area_effect_manager import EnvironmentalEffects

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [])
        fleet2 = _make_fleet(2, [])

        effects = EnvironmentalEffects(shield_capacity_mult=0.5, in_storm=True)

        # Both fleets empty → short-circuit; effects ignored but no crash.
        result = resolver.resolve_battle(fleet1, fleet2, environmental_effects=effects)
        assert result is not None

    def test_resolve_battle_emits_storm_modifier_on_spec(self):
        """shield_capacity_mult < 1.0 → a placeholder ModifierEntry with
        source='environment:storm_shield_interference' on the compiled spec."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from game.strategy.services.area_effect_manager import EnvironmentalEffects

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [_MockShipInstance("a")])
        fleet2 = _make_fleet(2, [_MockShipInstance("b")])

        effects = EnvironmentalEffects(shield_capacity_mult=0.5, in_storm=True)

        seen = {}

        def _fake_run_battle(spec, **_):
            seen["stack"] = spec.modifier_stack
            return _make_outcome()

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            side_effect=_fake_run_battle,
        ):
            resolver.resolve_battle(fleet1, fleet2, environmental_effects=effects)

        storm_entries = [
            e for e in seen["stack"].global_
            if e.source == "environment:storm_shield_interference"
        ]
        assert len(storm_entries) == 1
        # PROJ-270 Phase 6.1: storm effects now emit the real
        # `shield_capacity_mult` stat_key so `FleetAuraManager` applies
        # the effect to ship shield capacity during battle.
        assert storm_entries[0].effect.stat_key == "shield_capacity_mult"
        # Value should match the storm's shield_capacity_mult (0.5 in this fixture).
        assert storm_entries[0].effect.value == 0.5

    def test_resolve_battle_no_storm_modifier_when_neutral(self):
        """shield_capacity_mult == 1.0 → no storm ModifierEntry emitted."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from game.strategy.services.area_effect_manager import EnvironmentalEffects

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [_MockShipInstance("a")])
        fleet2 = _make_fleet(2, [_MockShipInstance("b")])

        effects = EnvironmentalEffects()

        seen = {}

        def _fake_run_battle(spec, **_):
            seen["stack"] = spec.modifier_stack
            return _make_outcome()

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            side_effect=_fake_run_battle,
        ):
            resolver.resolve_battle(fleet1, fleet2, environmental_effects=effects)

        assert not any(
            e.source == "environment:storm_shield_interference"
            for e in seen["stack"].global_
        )

    def test_resolve_battle_none_effects_emits_no_storm_modifier(self):
        """None effects → no storm ModifierEntry emitted."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [_MockShipInstance("a")])
        fleet2 = _make_fleet(2, [_MockShipInstance("b")])

        seen = {}

        def _fake_run_battle(spec, **_):
            seen["stack"] = spec.modifier_stack
            return _make_outcome()

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            side_effect=_fake_run_battle,
        ):
            resolver.resolve_battle(fleet1, fleet2, environmental_effects=None)

        assert not any(
            e.source.startswith("environment:") for e in seen["stack"].global_
        )


class TestBattleResolverInterfaceUpdate:
    """Tests that IBattleResolver interface supports environmental_effects."""

    def test_ibattle_resolver_accepts_environmental_effects(self):
        from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult
        from game.strategy.services.area_effect_manager import EnvironmentalEffects

        class TestResolver(IBattleResolver):
            def resolve_battle(self, fleet1, fleet2, seed=None, registries=None, environmental_effects=None):
                return BattleResult(winner=0, tick_count=0, team0_survivors=[], team1_survivors=[])

        resolver = TestResolver()
        effects = EnvironmentalEffects(shield_capacity_mult=0.5)
        result = resolver.resolve_battle(MagicMock(), MagicMock(), environmental_effects=effects)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
