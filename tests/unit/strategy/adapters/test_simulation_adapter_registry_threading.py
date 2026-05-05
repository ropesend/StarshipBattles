"""PROJ-361 regression: SimulationBattleResolver must thread an injected
``GameRegistries`` through to ``run_battle.registry_provider`` instead of
silently falling back to ``get_default_registry_provider()``.

Source review finding: Reviews/results/2026-05-05_strategy-layer-tech-debt-review/
report.md (finding #1). Before this regression test, ``simulation_adapter.py``
called ``run_battle(..., registry_provider=get_default_registry_provider())``
unconditionally — dropping any explicitly injected registries during ship
materialization. PROJ-361 closes that gap while preserving the PROJ-306
fallback when the caller passes ``registries=None``.
"""

from unittest.mock import MagicMock, patch


class _MockShipInstance:
    """Minimal ShipInstance-like stand-in matching the existing
    test_simulation_adapter.py shape so the spec compiler is satisfied."""

    def __init__(self, instance_id="i", combat_capable=True):
        self.instance_id = instance_id
        self.design_id = f"design-{instance_id}"
        self.design_data = {"theme_id": "Federation"}
        self.name = f"Ship-{instance_id}"
        self.components = {}
        self._combat_capable = combat_capable

    def is_combat_capable(self):
        return self._combat_capable

    def to_ship(self, pos, team_id=0, registries=None):  # noqa: D401
        ship = MagicMock()
        ship.instance_id = self.instance_id
        return ship


def _make_fleet(fleet_id, ships):
    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.ships = ships
    fleet.task_forces = []
    return fleet


def _make_outcome(winner_team_id=0, duration=100, replay_id=None):
    from game.simulation.battle_outcome import ShipStatus

    outcome = MagicMock()
    outcome.duration_ticks = duration
    outcome.replay_id = replay_id

    team0 = MagicMock()
    team0.team_id = 0
    team1 = MagicMock()
    team1.team_id = 1

    def _team_ships(is_alive):
        ship = MagicMock()
        ship.status = ShipStatus.SURVIVED if is_alive else ShipStatus.DESTROYED
        return [ship]

    team0.ships = _team_ships(winner_team_id == 0)
    team1.ships = _team_ships(winner_team_id == 1)
    outcome.teams = (team0, team1)
    return outcome


class TestRegistryThreadingToRunBattle:
    """PROJ-361: ``registries`` argument must reach ``run_battle.registry_provider``."""

    def test_resolve_battle_threads_injected_registries(self, fresh_registries):
        """When the caller injects registries, those exact registries reach
        ``run_battle.registry_provider`` (identity, not equality)."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        # Marker mutation: change a unique sentinel into the components dict
        # so that any default-provider lookup of this key would miss it. The
        # threading test uses identity (`is`), but the marker also documents
        # *why* the injection matters end-to-end.
        fresh_registries.components["__PROJ361_MARKER__"] = {
            "id": "__PROJ361_MARKER__",
            "name": "PROJ-361 sentinel",
            "category": "special",
        }

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [_MockShipInstance("a")])
        fleet2 = _make_fleet(2, [_MockShipInstance("b")])

        captured = {}

        def _fake_run_battle(spec, *, ai_factory, registry_provider, capture_context):
            captured["registry_provider"] = registry_provider
            return _make_outcome(winner_team_id=0)

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            side_effect=_fake_run_battle,
        ):
            resolver.resolve_battle(
                [fleet1, fleet2], registries=fresh_registries
            )

        assert captured["registry_provider"] is fresh_registries, (
            "Injected GameRegistries was not threaded to run_battle.registry_provider; "
            "the resolver silently fell back to the default provider."
        )

    def test_resolve_battle_falls_back_to_default_when_no_registries(self):
        """PROJ-306 fallback: when ``registries=None``, the resolver still
        calls ``get_default_registry_provider()`` — strategy layer is the
        only place that boundary is permitted."""
        from game.core.registry import get_default_registry_provider
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [_MockShipInstance("a")])
        fleet2 = _make_fleet(2, [_MockShipInstance("b")])

        captured = {}

        def _fake_run_battle(spec, *, ai_factory, registry_provider, capture_context):
            captured["registry_provider"] = registry_provider
            return _make_outcome(winner_team_id=0)

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            side_effect=_fake_run_battle,
        ):
            resolver.resolve_battle([fleet1, fleet2], registries=None)

        assert captured["registry_provider"] is get_default_registry_provider()
