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
