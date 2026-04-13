"""PROJ-270 Phase 4: BattleController emits BattleOutcome at battle end.

Verifies that visual-mode battles produce a `BattleOutcome` once
`is_battle_over()` returns True, closing the half of the unified-entry
contract that headless already satisfies.
"""
from unittest.mock import MagicMock

import pytest

from game.simulation.battle_controller import BattleController
from game.simulation.battle_config import BattleConfig


@pytest.fixture
def controller_with_mock_service():
    """BattleController with a mocked service so we can control tick ends."""
    service = MagicMock()
    engine = MagicMock()
    engine.ships = []
    engine.retreated_ships = []
    engine.tick_counter = 42
    service.get_engine.return_value = engine
    service.create_battle.return_value = MagicMock(success=True)
    service.start_battle.return_value = MagicMock(success=True)
    service.update.return_value = MagicMock(success=True)
    return BattleController(service=service), service, engine


class TestBattleControllerGetOutcome:
    """Controller exposes a `BattleOutcome` once the battle ends."""

    def test_get_outcome_returns_none_before_battle_ends(
        self, controller_with_mock_service,
    ):
        controller, service, _engine = controller_with_mock_service
        controller.configure(BattleConfig())
        service.is_battle_over.return_value = False
        controller.start()
        assert controller.get_outcome() is None

    def test_get_outcome_returns_none_without_spec(
        self, controller_with_mock_service,
    ):
        """If caller never set_spec(), controller has no way to build an outcome."""
        controller, service, _engine = controller_with_mock_service
        controller.configure(BattleConfig())
        controller.start()
        # Simulate battle ending
        service.is_battle_over.return_value = True
        controller.update()
        # Still None because no spec is set
        assert controller.get_outcome() is None

    def test_get_outcome_populated_after_battle_ends_with_spec(
        self, controller_with_mock_service, monkeypatch,
    ):
        """After `set_spec` + battle ending, `get_outcome()` returns a real outcome."""
        from game.simulation import battle_runner
        controller, service, engine = controller_with_mock_service

        # Patch extract_outcome so the test doesn't need to mock every
        # outcome-assembly detail; assert just that it's called with our
        # engine + spec.
        mock_outcome = MagicMock(name="BattleOutcome")
        captured = {}

        def _fake_extract(eng, spc):
            captured["engine"] = eng
            captured["spec"] = spc
            return mock_outcome
        monkeypatch.setattr(battle_runner, "extract_outcome", _fake_extract)

        controller.configure(BattleConfig())
        mock_spec = MagicMock(name="BattleSpec")
        controller.set_spec(mock_spec)
        controller.start()

        # Battle ends on the first update
        service.is_battle_over.return_value = True
        controller.update()

        outcome = controller.get_outcome()
        assert outcome is mock_outcome
        assert captured["engine"] is engine
        assert captured["spec"] is mock_spec

    def test_get_outcome_extracted_only_once(
        self, controller_with_mock_service, monkeypatch,
    ):
        """Multiple `update()` calls after battle-end don't re-extract the outcome."""
        from game.simulation import battle_runner
        controller, service, _engine = controller_with_mock_service

        call_count = {"n": 0}

        def _fake_extract(eng, spc):
            call_count["n"] += 1
            return MagicMock()
        monkeypatch.setattr(battle_runner, "extract_outcome", _fake_extract)

        controller.configure(BattleConfig())
        controller.set_spec(MagicMock())
        controller.start()

        service.is_battle_over.return_value = True
        controller.update()
        controller.update()
        controller.update()

        assert call_count["n"] == 1, (
            "extract_outcome was called multiple times; Phase 4 contract "
            "requires it to fire exactly once per battle."
        )


class TestBattleControllerConfigureAcceptsSpec:
    """PROJ-270 Task 4.2/4.3: `configure(config, spec=...)` is the unified path.

    Prior to the tighten, callers had to do `configure(config)` *then*
    `set_spec(spec)` in two steps. The tightened API accepts `spec` as
    an optional keyword to `configure()` so production call sites
    (app.py, test_lab/screen.py, test_execution_service.py) can pass
    both in a single call.

    `spec=None` must still be permitted — the legacy `BattleScreen.start(
    team0, team1)` bypass and ~60 existing unit tests call `configure(
    basic_config)` with no spec.
    """

    def test_configure_accepts_spec_kwarg(self, controller_with_mock_service):
        """`configure(config, spec=spec)` stores spec for later outcome extraction."""
        controller, _service, _engine = controller_with_mock_service
        mock_spec = MagicMock(name="BattleSpec")

        result = controller.configure(BattleConfig(), spec=mock_spec)

        assert result.success, "configure should still succeed with spec"
        # Spec must be stored so get_outcome() can use it at battle end.
        assert controller._spec is mock_spec, (
            "configure(config, spec=...) must internally store the spec "
            "on the controller (same invariant as set_spec)."
        )

    def test_configure_without_spec_still_works(self, controller_with_mock_service):
        """`configure(config)` with no spec keeps working — legacy test path."""
        controller, _service, _engine = controller_with_mock_service

        result = controller.configure(BattleConfig())

        assert result.success
        assert controller._spec is None, (
            "spec=None is the no-spec fallback; controller must not "
            "accidentally synthesize one."
        )

    def test_configure_with_spec_enables_outcome_extraction(
        self, controller_with_mock_service, monkeypatch,
    ):
        """End-to-end: configure(config, spec) + battle end → outcome emitted."""
        from game.simulation import battle_runner
        controller, service, engine = controller_with_mock_service
        mock_outcome = MagicMock(name="BattleOutcome")
        mock_spec = MagicMock(name="BattleSpec")

        monkeypatch.setattr(
            battle_runner, "extract_outcome",
            lambda eng, spc: mock_outcome,
        )

        controller.configure(BattleConfig(), spec=mock_spec)
        controller.start()
        service.is_battle_over.return_value = True
        controller.update()

        assert controller.get_outcome() is mock_outcome


class TestBattleControllerStartFromSpec:
    """PROJ-270 Phase 10: `BattleController.start_from_spec` is the single
    spec-in visual-mode entry. Routes through `start_engine_from_spec` —
    the same code path `run_battle` uses — to eliminate the 3 duplicated
    engine-plumbing blocks in production call sites.
    """

    def test_start_from_spec_exists(self):
        """Method presence guard — required for the unified visual-mode path."""
        from game.simulation.battle_controller import BattleController
        assert callable(getattr(BattleController, "start_from_spec", None)), (
            "BattleController.start_from_spec is required — visual-mode "
            "callers route through it instead of hand-rolling spec→engine plumbing."
        )

    def test_start_from_spec_stores_spec_for_outcome_extraction(
        self, monkeypatch,
    ):
        """After start_from_spec, controller.get_outcome() returns the
        real outcome at battle end (spec is wired for extract_outcome)."""
        from unittest.mock import MagicMock
        from game.simulation import battle_runner
        from game.simulation.battle_controller import BattleController
        from game.simulation.battle_config import BattleConfig

        fake_engine = MagicMock()
        fake_engine.ships = []
        fake_engine.retreated_ships = []
        fake_engine.tick_counter = 0
        fake_engine.is_battle_over.return_value = False

        def _fake_start(spec, *, ai_factory, ship_builder):
            return fake_engine, {}

        monkeypatch.setattr(
            battle_runner, "start_engine_from_spec", _fake_start,
        )

        mock_spec = MagicMock(name="BattleSpec")
        mock_spec.boundary = None
        mock_spec.seed = 42
        mock_spec.end_condition = MagicMock()
        mock_spec.absolute_max_ticks = 100

        controller = BattleController(service=MagicMock())
        controller._service.adopt_started_engine = MagicMock(
            return_value=MagicMock(success=True)
        )
        controller._state_manager = MagicMock()
        controller._state_manager.capture_state = MagicMock(return_value=None)

        result, ships_by_role = controller.start_from_spec(
            mock_spec, ai_factory=MagicMock(), ship_builder=lambda s: MagicMock(),
        )

        assert result.success
        assert controller._spec is mock_spec, (
            "start_from_spec must set_spec so get_outcome() works at battle end"
        )
        assert controller._is_started is True


class TestOutcomeContentAssertions:
    """PROJ-270 Phase 11.1: strengthen outcome assertions beyond plumbing.

    Skeptic finding: prior tests used `MagicMock(name="BattleOutcome")` —
    a regression returning `BattleOutcome(teams=(), duration_ticks=0)`
    would pass every test. Real-content assertions ensure the outcome
    carries meaningful team + status + duration data.
    """

    def test_outcome_has_populated_teams_after_real_run(self, fresh_registries):
        """Real `run_battle` call with minimal spec — outcome.teams is non-empty."""
        from game.ai.ai_factory import AIControllerFactory
        from game.core.math import Vector2
        from game.simulation.battle_runner import run_battle
        from game.simulation.battle_spec import (
            AIPolicy, BattleSpec, CombatPolicies, EntryVector,
            ShipSpec, SquadronSpec, TaskForceSpec, TeamSpec,
        )
        from game.simulation.combat.boundary import UnboundedRegion, ExitPolicy
        from game.simulation.combat.modifier_stack import ModifierStack
        from game.simulation.combat.telemetry import TelemetryLevel
        from game.simulation.entities.ship_serialization import ShipSerializer
        from game.simulation.systems.battle_end_conditions import TickLimitCondition

        design = {
            "name": "Cruiser", "ship_class": "Escort",
            "vehicle_type": "Ship", "design_role": "fleet_escort",
            "theme_id": "Federation",
            "layers": {
                "CORE": [{"id": "bridge"}],
                "OUTER": [{"id": "laser_cannon"}],
                "ARMOR": [],
            },
            "_metadata": {},
        }

        def _build(ship_spec):
            ship = ShipSerializer.from_dict(design, registries=fresh_registries)
            ship.instance_id = ship_spec.instance_id
            return ship

        def _team(tid, iid):
            ss = ShipSpec(
                instance_id=iid, design_id="Cruiser", theme_id="Federation",
                name=iid, position=Vector2(0, 0), angle=0.0,
                velocity=Vector2(0, 0), components=(),
            )
            return TeamSpec(
                team_id=tid, name=f"T{tid}",
                entry_vector=EntryVector(origin=Vector2(0, 0), facing=0.0),
                fleet_hierarchy=(TaskForceSpec(
                    task_force_id=f"tf-{tid}", formation=None,
                    policies=CombatPolicies(),
                    squadrons=(SquadronSpec(
                        squadron_id=f"sq-{tid}", policies=CombatPolicies(),
                        ships=(ss,),
                    ),),
                ),),
                ai_policy=AIPolicy(),
            )

        spec = BattleSpec(
            seed=1,
            telemetry_level=TelemetryLevel.NORMAL,
            boundary=UnboundedRegion(exit_policy=ExitPolicy.NONE),
            end_condition=TickLimitCondition(max_ticks=2),
            absolute_max_ticks=10,
            teams=(_team(0, "s0"), _team(1, "s1")),
            modifier_stack=ModifierStack.empty(),
            post_battle_hook=None,
        )
        outcome = run_battle(spec, ai_factory=AIControllerFactory(), ship_builder=_build)

        # Real-content assertions — catches `BattleOutcome(teams=())` regressions.
        assert len(outcome.teams) == 2, f"expected 2 teams, got {len(outcome.teams)}"
        assert outcome.duration_ticks > 0, (
            f"duration_ticks should advance past 0, got {outcome.duration_ticks}"
        )
        assert outcome.end_reason is not None
        assert outcome.seed == 1, "seed echoed from spec"
        # Each team has real ship data.
        for team in outcome.teams:
            assert len(team.ships) == 1
            for ship_outcome in team.ships:
                assert ship_outcome.instance_id in ("s0", "s1")
                assert ship_outcome.status is not None
