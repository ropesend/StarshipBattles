"""Tests for SimulationBattleResolver adapter.

PROJ-269 Phase 6 Task 6.5/6.11: the adapter was rewritten to use
`build_strategy_battle_spec` + `run_battle`. The tests here mock that
surface instead of the legacy `BattleController`/`BattleConfig`/`BattleMode`.
"""
from unittest.mock import MagicMock, patch


class _MockShipInstance:
    """Minimal ShipInstance-like stand-in that satisfies both the
    adapter's call shape (is_combat_capable / to_ship / instance_id) and
    the strategy compiler's attribute reads (design_id / design_data /
    name / components)."""

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
    """Build a fleet stand-in that satisfies the compiler's reads."""
    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.ships = ships
    fleet.task_forces = []
    return fleet


def _make_outcome(winner_team_id, duration=100):
    """Build a minimal BattleOutcome stand-in for _determine_winner."""
    from game.simulation.battle_outcome import ShipStatus

    outcome = MagicMock()
    outcome.duration_ticks = duration

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


class TestSimulationBattleResolverBehavior:
    """Test SimulationBattleResolver behavior against the run_battle surface."""

    def test_resolve_battle_returns_battle_result(self):
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from game.strategy.interfaces.battle_resolver import BattleResult

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [_MockShipInstance("a")])
        fleet2 = _make_fleet(2, [_MockShipInstance("b")])

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            return_value=_make_outcome(winner_team_id=0),
        ):
            result = resolver.resolve_battle([fleet1, fleet2])

        assert isinstance(result, BattleResult)
        assert result.winner == 0
        assert result.tick_count == 100

    def test_resolve_battle_passes_seed_to_compiler(self):
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [_MockShipInstance("a")])
        fleet2 = _make_fleet(2, [_MockShipInstance("b")])

        seen_spec = {}

        def _fake_run_battle(spec, **_):
            seen_spec["seed"] = spec.seed
            return _make_outcome(winner_team_id=0)

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            side_effect=_fake_run_battle,
        ):
            resolver.resolve_battle([fleet1, fleet2], seed=42)

        assert seen_spec["seed"] == 42

    def test_resolve_battle_constructs_two_teams(self):
        """Fleet1 → team 0, Fleet2 → team 1."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [_MockShipInstance("a1")])
        fleet2 = _make_fleet(2, [_MockShipInstance("b1")])

        seen_spec = {}

        def _fake_run_battle(spec, **_):
            seen_spec["teams"] = spec.teams
            return _make_outcome(winner_team_id=0)

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            side_effect=_fake_run_battle,
        ):
            resolver.resolve_battle([fleet1, fleet2])

        teams = seen_spec["teams"]
        assert len(teams) == 2
        assert teams[0].team_id == 0
        assert teams[1].team_id == 1

    def test_resolve_battle_handles_one_empty_fleet(self):
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from game.strategy.interfaces.battle_resolver import BattleResult

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [_MockShipInstance("a")])
        fleet2 = _make_fleet(2, [])

        result = resolver.resolve_battle([fleet1, fleet2])

        assert isinstance(result, BattleResult)
        assert result.winner == 0  # Fleet 1 wins because Fleet 2 is empty
        assert result.tick_count == 0

    def test_resolve_battle_handles_both_empty_fleets(self):
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
        from game.strategy.interfaces.battle_resolver import BattleResult

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [])
        fleet2 = _make_fleet(2, [])

        result = resolver.resolve_battle([fleet1, fleet2])

        assert isinstance(result, BattleResult)
        assert result.winner is None
        assert result.tick_count == 0

    def test_resolve_battle_short_circuits_when_no_run_battle_needed(self):
        """Empty fleet edge-case should NOT invoke run_battle."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [])
        fleet2 = _make_fleet(2, [_MockShipInstance("b")])

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
        ) as mock_run_battle:
            result = resolver.resolve_battle([fleet1, fleet2])

        mock_run_battle.assert_not_called()
        assert result.winner == 1

    def test_resolve_battle_determines_winner_from_outcome(self):
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [_MockShipInstance("a")])
        fleet2 = _make_fleet(2, [_MockShipInstance("b")])

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            return_value=_make_outcome(winner_team_id=1, duration=250),
        ):
            result = resolver.resolve_battle([fleet1, fleet2])

        assert result.winner == 1
        assert result.tick_count == 250


class TestSimulationBattleResolverDependencyInjection:
    """AI factory must be injectable; no direct AI-layer import at module level."""

    def test_accepts_ai_factory_parameter(self):
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        mock_factory = MagicMock()
        resolver = SimulationBattleResolver(ai_factory=mock_factory)
        assert resolver._ai_factory is mock_factory

    def test_uses_injected_ai_factory(self):
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        mock_factory = MagicMock()
        resolver = SimulationBattleResolver(ai_factory=mock_factory)
        fleet1 = _make_fleet(1, [_MockShipInstance("a")])
        fleet2 = _make_fleet(2, [_MockShipInstance("b")])

        seen = {}

        def _fake_run_battle(spec, *, ai_factory, **_):
            seen["ai_factory"] = ai_factory
            return _make_outcome(winner_team_id=0)

        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            side_effect=_fake_run_battle,
        ):
            resolver.resolve_battle([fleet1, fleet2])

        assert seen["ai_factory"] is mock_factory

    def test_no_direct_ai_layer_import_at_module_level(self):
        import game.strategy.adapters.simulation_adapter as module
        import inspect

        source = inspect.getsource(module)
        module_imports_section = source.split("class SimulationBattleResolver")[0]
        assert "from game.ai.ai_factory import AIControllerFactory" not in module_imports_section


# ---------------------------------------------------------------------------
# FEAT-26 — replay_id plumbing
# ---------------------------------------------------------------------------


def _make_outcome_with_replay_id(replay_id, winner_team_id=0, duration=100):
    """Like _make_outcome, but also surface a replay_id field on the
    BattleOutcome stand-in (FEAT-26)."""
    outcome = _make_outcome(winner_team_id=winner_team_id, duration=duration)
    outcome.replay_id = replay_id
    return outcome


class TestSimulationAdapterReplayId:
    """FEAT-26: BattleResult.replay_id is populated from BattleOutcome.replay_id."""

    def test_simulator_branch_threads_replay_id_from_outcome(self):
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [_MockShipInstance("a")])
        fleet2 = _make_fleet(2, [_MockShipInstance("b")])

        outcome = _make_outcome_with_replay_id(
            replay_id="captured-uuid-string", winner_team_id=0
        )
        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            return_value=outcome,
        ):
            result = resolver.resolve_battle([fleet1, fleet2])

        assert result.replay_id == "captured-uuid-string"

    def test_simulator_branch_replay_id_is_none_when_outcome_has_none(self):
        """A simulator-run battle with no captured replay still threads
        ``None`` through (e.g. when no capture sink is registered)."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [_MockShipInstance("a")])
        fleet2 = _make_fleet(2, [_MockShipInstance("b")])

        outcome = _make_outcome_with_replay_id(replay_id=None, winner_team_id=0)
        with patch(
            "game.strategy.adapters.simulation_adapter.run_battle",
            return_value=outcome,
        ):
            result = resolver.resolve_battle([fleet1, fleet2])

        assert result.replay_id is None

    def test_no_capable_shortcut_branch_replay_id_is_none(self):
        """The 'no team can fight' shortcut never runs the simulator,
        so there is no replay_id."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [])
        fleet2 = _make_fleet(2, [])

        result = resolver.resolve_battle([fleet1, fleet2])

        assert result.replay_id is None

    def test_sole_survivor_shortcut_branch_replay_id_is_none(self):
        """The 'one team has all combat-capable ships' shortcut never
        runs the simulator, so there is no replay_id."""
        from game.strategy.adapters.simulation_adapter import SimulationBattleResolver

        resolver = SimulationBattleResolver(ai_factory=MagicMock())
        fleet1 = _make_fleet(1, [_MockShipInstance("a")])
        fleet2 = _make_fleet(2, [])

        result = resolver.resolve_battle([fleet1, fleet2])

        assert result.replay_id is None
