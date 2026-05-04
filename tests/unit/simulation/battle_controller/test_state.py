"""Tests for BattleController state save/load and results."""
import pytest
from unittest.mock import Mock, patch

from game.simulation.battle_controller import (
    BattleController,
    BattleConfig,)


class TestBattleControllerStateSaveLoad:
    """Tests for state save and load."""

    def test_save_state_raises_when_not_started(self, controller, basic_config, mock_service):
        """save_state raises StateException when not started."""
        from game.core.exceptions import StateException
        controller.configure(basic_config)

        with pytest.raises(StateException, match="not started"):
            controller.save_state()

    def test_save_state_captures_state(self, controller, basic_config, mock_service):
        """save_state captures battle state from engine."""
        controller.configure(basic_config)
        controller.start()

        mock_engine = Mock()
        mock_engine.ships = []
        mock_engine.projectiles = []
        mock_engine.tick_counter = 100
        mock_service.get_engine.return_value = mock_engine

        # Patch BattleState in the manager module where it's actually called
        with patch('game.simulation.managers.battle_state_manager.BattleState') as MockState:
            mock_state = Mock()
            MockState.capture_from_engine.return_value = mock_state

            result = controller.save_state()

            MockState.capture_from_engine.assert_called()
            assert result is mock_state

    def test_load_state_restores_battle(self, controller, mock_service):
        """load_state restores battle from BattleState.

        Also pins PROJ-331 OBSERVATION-B: load_state defaults
        `_retreat_manager.boundary` to `UnboundedRegion()` when the
        restored config carries no boundary (battle_controller.py:130-131).
        MAJ-003 fix (review req_20260504_213455_95a42d).
        """
        from game.simulation.combat.boundary import UnboundedRegion

        # Create a mock BattleState
        mock_state = Mock()
        mock_state.seed = 12345
        mock_state.end_condition_data = {"type": "team_eliminated"}
        mock_state.allow_retreat = False
        mock_state.allow_reinforcements = False
        mock_state.ships = {"state-ship-id": Mock(team_id=0)}
        mock_state.tick_count = 500
        mock_state.projectiles = []  # Added for projectile restoration (NEW-SIM-007)
        controller._registries = Mock(name="registries")

        mock_engine = Mock()
        mock_engine.ships = []
        mock_engine.projectiles = []
        mock_service.get_engine.return_value = mock_engine

        restored_ship = Mock()
        restored_ship.id = "runtime-ship-id"
        mock_state_manager = Mock()
        # restore_config_from_state returns a BattleConfig() — its `.boundary`
        # is None by default, which triggers the UnboundedRegion fallback.
        mock_state_manager.restore_config_from_state.return_value = BattleConfig()
        mock_state_manager.extract_ships_from_state.return_value = (
            [restored_ship],
            {restored_ship.id: "state-ship-id"},
        )
        controller._state_manager = mock_state_manager

        result = controller.load_state(mock_state)

        assert result.success is True
        assert controller._is_configured is True
        assert controller._is_started is True
        mock_state_manager.extract_ships_from_state.assert_called_once_with(
            mock_state,
            registries=controller._registries,
        )
        mock_service.add_ship.assert_called_with(restored_ship, 0)
        # MAJ-003 fix: pin OBSERVATION-B boundary default contract.
        assert isinstance(
            controller._retreat_manager.boundary,
            UnboundedRegion,
        ), (
            "PROJ-331 OBSERVATION-B: load_state must default boundary to "
            "UnboundedRegion when the restored config has no boundary set."
        )

    def test_load_state_handles_error(self, controller):
        """load_state handles errors gracefully.

        PROJ-269 Phase 6: BattleMode validation is gone, so this test
        now verifies that a state-manager that raises during restore
        propagates an error result rather than crashing.
        """
        mock_state = Mock()
        controller._state_manager = Mock()
        controller._state_manager.restore_config_from_state.side_effect = ValueError("bad state")

        result = controller.load_state(mock_state)

        assert result.success is False
        assert len(result.errors) > 0


class TestBattleControllerGetResults:
    """Tests for get_results()."""

    def test_get_results_returns_battle_results(self, controller, basic_config, mock_service):
        """get_results returns BattleResults object."""
        controller.configure(basic_config)
        controller.start()

        mock_engine = Mock()
        mock_engine.ships = []
        mock_engine.projectiles = []
        mock_engine.tick_counter = 100
        mock_service.get_engine.return_value = mock_engine
        mock_service.get_winner.return_value = 0

        with patch('game.simulation.battle_controller.BattleState') as MockState:
            mock_state = Mock()
            mock_state.ships = {}
            MockState.capture_from_engine.return_value = mock_state

            results = controller.get_results()

            assert results.winner == 0
            assert results.tick_count == 100

    def test_get_results_categorizes_escaped_ships(self, controller, basic_config, mock_service):
        """get_results correctly categorizes escaped ships."""
        controller.configure(basic_config)
        controller.start()

        mock_engine = Mock()
        mock_engine.ships = []
        mock_engine.projectiles = []
        mock_engine.tick_counter = 100
        mock_service.get_engine.return_value = mock_engine
        mock_service.get_winner.return_value = 0

        # Add escaped ship
        controller._retreat_manager.escaped_ships = ['escaped-ship-id']

        # Patch BattleState in the manager module where it's actually called
        with patch('game.simulation.managers.battle_state_manager.BattleState') as MockState:
            mock_escaped_state = Mock()
            mock_escaped_state.is_alive = True  # Escaped ships can be "alive" but out of battle

            mock_state = Mock()
            mock_state.ships = {'escaped-ship-id': mock_escaped_state}
            MockState.capture_from_engine.return_value = mock_state

            results = controller.get_results()

            assert mock_escaped_state in results.escaped_ships


class TestBattleControllerLoadStateProjectiles:
    """PROJ-331 Phase 2a: pin load_state projectile-restore path.

    Characterization tests — they describe what current production does
    when restoring projectiles via `BattleState.projectiles` -> engine.
    """

    def _build_load_state_setup(self, controller, mock_service, *,
                                 projectiles, ship_id="runtime-ship",
                                 save_id="state-ship-id"):
        """Wire a controller for load_state with `projectiles` attached."""
        mock_state = Mock()
        mock_state.seed = 12345
        mock_state.end_condition_data = {"type": "team_eliminated"}
        mock_state.allow_retreat = False
        mock_state.allow_reinforcements = False
        mock_state.ships = {save_id: Mock(team_id=0)}
        mock_state.tick_count = 0
        mock_state.projectiles = projectiles
        controller._registries = Mock(name="registries")

        engine_ship = Mock()
        engine_ship.id = ship_id

        mock_engine = Mock()
        mock_engine.ships = [engine_ship]
        mock_engine.projectiles = []
        mock_service.get_engine.return_value = mock_engine

        restored_ship = Mock()
        restored_ship.id = ship_id
        mock_state_manager = Mock()
        mock_state_manager.restore_config_from_state.return_value = BattleConfig()
        mock_state_manager.extract_ships_from_state.return_value = (
            [restored_ship],
            {restored_ship.id: save_id},
        )
        controller._state_manager = mock_state_manager
        return mock_state, mock_engine, engine_ship

    def test_load_state_restores_alive_projectiles_only(self, controller, mock_service):
        """Only `proj_state.is_alive == True` entries get restored."""
        alive_a = Mock()
        alive_a.is_alive = True
        alive_a.to_projectile = Mock(return_value=Mock(name="proj_a"))
        alive_b = Mock()
        alive_b.is_alive = True
        alive_b.to_projectile = Mock(return_value=Mock(name="proj_b"))
        dead = Mock()
        dead.is_alive = False
        dead.to_projectile = Mock(return_value=Mock(name="proj_dead"))

        mock_state, mock_engine, _ = self._build_load_state_setup(
            controller, mock_service,
            projectiles=[alive_a, alive_b, dead],
        )

        result = controller.load_state(mock_state)

        assert result.success is True
        assert len(mock_engine.projectiles) == 2
        # Dead projectile's to_projectile is never invoked.
        dead.to_projectile.assert_not_called()
        alive_a.to_projectile.assert_called_once()
        alive_b.to_projectile.assert_called_once()

    def test_load_state_resolves_projectile_owner_via_ship_id_map(
        self, controller, mock_service,
    ):
        """`to_projectile` receives `ship_lookup={save_id: engine_ship}`."""
        alive = Mock()
        alive.is_alive = True
        alive.to_projectile = Mock(return_value=Mock())

        mock_state, _, engine_ship = self._build_load_state_setup(
            controller, mock_service,
            projectiles=[alive], ship_id="runtime-ship",
            save_id="save_id_1",
        )

        result = controller.load_state(mock_state)

        assert result.success is True
        # to_projectile called with a single dict arg containing
        # save_id -> engine_ship.
        call_args = alive.to_projectile.call_args
        ship_lookup = call_args.args[0]
        assert ship_lookup == {"save_id_1": engine_ship}


class TestRequireRegistriesForStateRestore:
    """PROJ-331 Phase 2a: pin `_require_registries_for_state_restore` gate."""

    def test_require_registries_returns_none_for_empty_state_when_registries_unset(
        self, controller,
    ):
        """state_count=0 + registries=None: returns None, no raise."""
        controller._registries = None
        result = controller._require_registries_for_state_restore(state_count=0)
        assert result is None

    def test_require_registries_raises_validation_exception_for_nonempty_state_when_registries_unset(
        self, controller,
    ):
        """state_count>0 + registries=None: raises ValidationException(MISSING_DEPENDENCY)."""
        from game.core.exceptions import ValidationException
        controller._registries = None
        with pytest.raises(ValidationException) as exc_info:
            controller._require_registries_for_state_restore(state_count=3)
        # MISSING_DEPENDENCY = "C003"
        assert exc_info.value.code == "C003"


class TestExtractOutcomeOnBattleEndSwallowsCaptureExceptions:
    """PROJ-331 OBSERVATION-C (MAJ-002 fix from review req_20260504_213455_95a42d).

    Pins the broad-except at battle_controller.py:445 — when
    `get_default_capture_sink().on_battle_ended` raises, _extract_outcome_on_battle_end
    must still set self._outcome and complete normally. A refactor that
    removes the catch (or changes its scope) should fail this test.
    """

    def test_outcome_is_set_when_capture_sink_raises(self, controller, mock_service):
        """Capture-sink exception MUST NOT prevent _outcome from being set."""
        # _spec only needs to be non-None for the early-return guard at
        # battle_controller.py:432 to fall through. Mock is sufficient —
        # production reads engine.replay_id, not spec fields, on this path.
        controller._spec = Mock(name="battle_spec")

        mock_engine = Mock()
        mock_engine.replay_id = "test-replay-id"
        mock_service.get_engine.return_value = mock_engine

        sentinel_outcome = Mock(name="extracted_outcome")
        with patch(
            "game.simulation.battle_runner.extract_outcome",
            return_value=sentinel_outcome,
        ), patch(
            "game.simulation.replay.get_default_capture_sink",
        ) as mock_sink_factory:
            mock_sink = Mock()
            mock_sink.on_battle_ended.side_effect = RuntimeError("sink broke")
            mock_sink_factory.return_value = mock_sink

            # Must not raise.
            controller._extract_outcome_on_battle_end()

        assert controller._outcome is sentinel_outcome, (
            "PROJ-331 OBSERVATION-C: _extract_outcome_on_battle_end must "
            "still set self._outcome even when on_battle_ended raises."
        )
