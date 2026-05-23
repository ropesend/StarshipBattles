"""Tests for StrategyGameStateManager (PROJ-173 Phase 4).

Tests the extracted turn processing and game state management functionality.
"""

import contextlib

import pytest
from unittest.mock import MagicMock, patch


def _make_game_state_manager():
    """Create a StrategyGameStateManager with mocked screen dependency."""
    from game.ui.screens.strategy_game_state_manager import StrategyGameStateManager

    # Create mock screen
    mock_screen = MagicMock()
    mock_screen.session = MagicMock()
    mock_screen._facade = MagicMock()
    # PROJ-475 Phase 2 Task 2.4: auto-save routes through
    # facade.session_meta.save_current_game() (returns the
    # (success, message, save_path) triple). Concrete triple so the unpack in
    # process_full_turn succeeds.
    mock_screen._facade.session_meta.save_current_game.return_value = (
        True, "Saved", "/tmp/save.json"
    )
    mock_screen.ui = MagicMock()
    mock_screen.ui.manager = MagicMock()
    mock_screen.ui.width = 1920
    mock_screen.ui.height = 1080
    mock_screen.turn_processing = False
    mock_screen.current_player_index = 0
    mock_screen.selected_object = None
    mock_screen.selected_fleet = None
    mock_screen.last_selected_system = None

    # Setup empire mocking
    empire0 = MagicMock()
    empire0.id = 0
    empire0.name = "Empire Zero"
    empire0.colonies = [MagicMock(name="empire0_home")]
    # Issue #25: defeat detection runs at the top of
    # `_apply_turn_start_state`; explicitly stub `is_eliminated` so the
    # existing live-empire tests don't trip the defeat path because of
    # MagicMock's auto-truthy return.
    empire0.is_eliminated = MagicMock(return_value=False)
    empire1 = MagicMock()
    empire1.id = 1
    empire1.name = "Empire One"
    empire1.colonies = [MagicMock(name="empire1_home")]
    empire1.is_eliminated = MagicMock(return_value=False)
    mock_screen.empires = [empire0, empire1]
    mock_screen.session.empires = [empire0, empire1]
    # PROJ-477 Phase 4: the manager iterates next/current empires through
    # scene.world.iter_empires; mirror the same list tests configure.
    mock_screen.world.iter_empires.side_effect = lambda: iter(mock_screen.empires)
    mock_screen.session.human_player_ids = [0, 1]
    mock_screen.human_player_ids = [0, 1]
    # PROJ-475 Phase 3: the manager reads human-player ids through
    # ``screen.facade.session_meta.human_player_ids()`` (the screen
    # pass-through was retired). Many tests reassign ``screen.human_player_ids``
    # after construction, so source the facade surface dynamically from that
    # attribute (a test-helper shorthand) to keep both in lockstep. Both
    # ``mock_screen.facade`` and ``mock_screen._facade`` are wired since they
    # are distinct MagicMock children.
    _hpi = lambda: mock_screen.human_player_ids
    mock_screen._facade.session_meta.human_player_ids.side_effect = _hpi
    mock_screen.facade.session_meta.human_player_ids.side_effect = _hpi
    mock_screen.active_empire = empire0

    # Property mock for current_empire — tracks current_player_index so
    # rollover-branch tests can observe the post-rotation empire.
    def _current_empire(self):
        idx = self.human_player_ids[self.current_player_index]
        return next(e for e in self.empires if e.id == idx)

    type(mock_screen).current_empire = property(_current_empire)

    # Setup draw method for rendering
    mock_screen.draw = MagicMock()
    mock_screen.center_camera_on = MagicMock()
    mock_screen.on_ui_selection = MagicMock()

    manager = StrategyGameStateManager(mock_screen)

    return manager, mock_screen


class TestGameStateManagerInit:
    """Test StrategyGameStateManager initialization."""

    def test_init_stores_screen_reference(self):
        """Manager should store reference to parent screen."""
        manager, screen = _make_game_state_manager()
        assert manager._screen is screen


class TestAdvanceTurn:
    """Test advance_turn() method."""

    def test_increments_player_index(self):
        """advance_turn() should increment current_player_index."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]

        manager.advance_turn()

        assert screen.current_player_index == 1

    def test_wraps_and_processes_when_all_ready(self):
        """advance_turn() should wrap and process turn when all players ready."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0]
        screen._facade.events.turn_events.return_value = []

        with patch('pygame.display.get_surface', return_value=None):
            manager.advance_turn()

        assert screen.current_player_index == 0
        screen._facade.process_turn.assert_called_once()

    def test_updates_player_label(self):
        """advance_turn() should update player label."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]

        manager.advance_turn()

        screen.ui.lbl_current_player.set_text.assert_called()

    def test_centers_camera_on_next_player_home(self):
        """advance_turn() should center camera on next player's home colony."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]

        manager.advance_turn()

        screen.center_camera_on.assert_called_once()


class TestProcessFullTurnLegacy:
    """Test process_full_turn() method (formerly _process_full_turn, FEAT-20 made public)."""

    def test_sets_turn_processing_flag(self):
        """process_full_turn() should set turn_processing during processing."""
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = []

        # Track the flag value during processing
        processing_values = []

        def track_processing(*args, **kwargs):
            processing_values.append(screen.turn_processing)

        screen._facade.process_turn.side_effect = track_processing

        with patch('pygame.display.get_surface', return_value=None):
            manager.process_full_turn()

        # Flag should have been True during process_turn
        assert True in processing_values
        # Flag should be False after completion
        assert screen.turn_processing is False

    def test_calls_facade_process_turn(self):
        """process_full_turn() should call facade.process_turn()."""
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = []

        with patch('pygame.display.get_surface', return_value=None):
            manager.process_full_turn()

        screen._facade.process_turn.assert_called_once()

    def test_returns_active_empire_turn_events(self):
        """process_full_turn() returns the active empire's turn events.

        Issue #9: the per-player turn-start helper is the single source of
        truth for opening the event log; process_full_turn no longer opens
        it directly. The events are still returned so the FEAT-20 dev-loop
        caller (run_n_turns) can aggregate them for a combined end-of-loop
        log.
        """
        manager, screen = _make_game_state_manager()
        mock_events = [MagicMock()]
        screen._facade.events.turn_events.return_value = mock_events

        with patch('pygame.display.get_surface', return_value=None):
            result = manager.process_full_turn()

        screen._facade.events.turn_events.assert_called()
        assert result == mock_events

    def test_does_not_open_event_log_directly(self):
        """process_full_turn() must NOT open the event log itself.

        Issue #9: the per-player turn-start helper called from
        advance_turn is the single source of truth. process_full_turn
        opening it again would double-fire on the rollover branch.
        """
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = [MagicMock()]

        with patch('pygame.display.get_surface', return_value=None):
            manager.process_full_turn()

        screen.ui.open_event_log_with_events.assert_not_called()

    def test_auto_saves_when_save_path_exists(self):
        """process_full_turn() should auto-save when the session has a save_path.

        PROJ-475 Phase 2 Task 2.4: auto-save now routes through
        ``facade.session_meta.save_current_game()`` (the facade owns the
        session) rather than ``SaveGameService.save_game(screen.session)``.
        """
        manager, screen = _make_game_state_manager()
        screen._facade.session_meta.save_path.return_value = "/test/save.json"
        screen._facade.session_meta.save_current_game.return_value = (
            True, "Saved", "/test/save.json"
        )
        screen._facade.events.turn_events.return_value = []

        with patch('pygame.display.get_surface', return_value=None):
            manager.process_full_turn()

        screen._facade.session_meta.save_current_game.assert_called_once_with()

    def test_does_not_refresh_selected_object_directly(self):
        """process_full_turn() must NOT touch ``selected_object`` itself.

        Issue #9: the helper reseats the lower-right panel to the new
        player's home colony via ``on_ui_selection(home_colony)``.
        process_full_turn refreshing the stale selected_object would
        either show last turn's selection (the bug) or double-render
        on top of the home colony reseat.
        """
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = []
        screen.selected_object = MagicMock()

        with patch('pygame.display.get_surface', return_value=None):
            manager.process_full_turn()

        screen.on_ui_selection.assert_not_called()


class TestProcessFullTurnErrorBoundary:
    """PROJ-409 MAJ-014: defensive raw ``EnginePhaseError`` catch removed.

    The facade is the only converter from ``EnginePhaseError`` →
    ``TurnFailedError`` (see ``StrategySessionFacade.process_turn`` and
    ``tests/unit/strategy/facade/test_strategy_session_facade.py::
    TestProcessTurnErrorConversion``). Per CLAUDE.md Rule 4 the UI must
    not catch a domain-engine exception type as a fallback for a
    facade-bypass that cannot happen.
    """

    def test_turn_failed_error_opens_dialog_clears_overlay_skips_autosave(self):
        """Canonical path: ``TurnFailedError`` is handled — dialog shown,
        progress overlay cleared, no autosave, no event-log popup."""
        from game.core.exceptions import TurnFailedError

        manager, screen = _make_game_state_manager()
        screen._facade.session_meta.save_path.return_value = "/tmp/save.json"
        screen._facade.events.turn_events.return_value = []
        # Pre-set tick state so we can verify ``finally`` clears it.
        screen.current_tick = 42
        screen.total_ticks = 100

        err = TurnFailedError(
            message="phase boom",
            code="S101",
            context={"phase_name": "test_phase", "tick": 5,
                     "turn_number": 3, "original_type": "RuntimeError"},
        )
        screen._facade.process_turn.side_effect = err

        with patch("pygame.display.get_surface", return_value=None), \
             patch.object(manager, "_show_turn_failed_dialog") as mock_dialog:
            manager.process_full_turn()

        # Dialog opened with the error.
        mock_dialog.assert_called_once_with(err)
        # Progress overlay cleared by the ``finally`` block.
        assert screen.current_tick is None
        assert screen.total_ticks is None
        # turn_processing flag cleared.
        assert screen.turn_processing is False
        # Autosave SKIPPED (rollback already happened in TurnEngine).
        # PROJ-475: autosave routes through facade.session_meta.save_current_game().
        screen._facade.session_meta.save_current_game.assert_not_called()
        # Event-log popup SKIPPED.
        screen.ui.open_event_log_with_events.assert_not_called()

    def test_raw_engine_phase_error_propagates_uncaught(self):
        """Architectural contract: the UI must NOT catch raw
        ``EnginePhaseError``. The facade is the sole converter; if a code
        path bypasses the facade and raises raw ``EnginePhaseError``,
        let it propagate so the bypass is loud, not papered over."""
        from game.core.exceptions import EnginePhaseError

        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = []

        engine_err = EnginePhaseError(
            "raw bypass",
            code="S101",
            context={"phase_name": "bypass", "tick": 1},
        )
        screen._facade.process_turn.side_effect = engine_err

        with patch("pygame.display.get_surface", return_value=None):
            with pytest.raises(EnginePhaseError):
                manager.process_full_turn()


class TestUpdatePlayerLabel:
    """Test _update_player_label() method."""

    def test_updates_label_text(self):
        """Should update player label with correct player number."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 1

        manager._update_player_label()

        screen.ui.lbl_current_player.set_text.assert_called_with("Player 2's Turn")

    def test_uses_1_indexed_player_number(self):
        """Player number should be 1-indexed."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0

        manager._update_player_label()

        screen.ui.lbl_current_player.set_text.assert_called_with("Player 1's Turn")


# ===========================================================================
# Issue #9: per-player turn-start state helper
# ===========================================================================

class TestApplyTurnStartState:
    """Issue #9: ``_apply_turn_start_state`` is the single source of truth
    for per-player turn-start UI state — clears stale selection, centres
    camera, populates the lower-right detail panel via the manual-click
    code path, and opens the per-player event log (BUG-123 scoping,
    FEAT-20 suppression honoured).
    """

    def test_clears_stale_selection_state(self):
        """Helper clears ``selected_fleet`` / ``selected_object`` /
        ``last_selected_system`` so the next player never inherits the
        previous player's pick."""
        manager, screen = _make_game_state_manager()
        screen.selected_fleet = MagicMock()
        screen.selected_object = MagicMock()
        screen.last_selected_system = MagicMock()
        screen._facade.events.turn_events.return_value = []
        empire = screen.empires[1]

        manager._apply_turn_start_state(empire)

        assert screen.selected_fleet is None
        assert screen.selected_object is None
        assert screen.last_selected_system is None

    def test_centres_camera_on_home_colony(self):
        """Helper centres the camera on ``empire.colonies[0]``."""
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = []
        empire = screen.empires[1]

        manager._apply_turn_start_state(empire)

        screen.center_camera_on.assert_called_once_with(empire.colonies[0])

    def test_auto_selects_home_colony_via_manual_click_path(self):
        """Helper calls ``on_ui_selection(home_colony)`` — the same path a
        manual planet click takes — so ``PlanetReportPanel`` is populated
        via ``show_detailed_report`` and selection-side concerns (e.g.
        ``transfer_dialog.handle_external_selection``,
        ``last_selected_system`` derivation) stay consistent with manual
        clicks."""
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = []
        empire = screen.empires[1]

        manager._apply_turn_start_state(empire)

        screen.on_ui_selection.assert_called_once_with(empire.colonies[0])

    def test_opens_event_log_scoped_to_previous_turn_and_new_empire(self):
        """Helper opens the event log for the new empire's events from the
        just-completed turn (``session.turn_number - 1``).

        ``GameSession.process_turn`` post-increments ``session.turn_number``,
        so by the time the helper runs after ``process_full_turn`` the
        facade's ``get_turn_number()`` returns ``N+1`` while the events the
        player needs to see were filed with ``turn=N``. The helper must
        subtract one to find them. Mock values are deliberately asymmetric
        (8 -> 7) so the test cannot tautologise: it verifies the helper
        queries the *previous* turn, not whatever ``get_turn_number``
        returns. BUG-123 scoping: ``empire_id=empire.id`` + ``empire_name``.
        """
        manager, screen = _make_game_state_manager()
        mock_events = [MagicMock()]
        screen._facade.events.turn_events.return_value = mock_events
        screen._facade.session_meta.turn_number.return_value = 8
        empire = screen.empires[1]

        manager._apply_turn_start_state(empire)

        screen._facade.events.turn_events.assert_called_once_with(
            turn=7, empire_id=empire.id
        )
        screen.ui.open_event_log_with_events.assert_called_once_with(
            mock_events, empire_name=empire.name
        )

    def test_no_event_log_when_no_events(self):
        """Empty turn_events suppresses the popup."""
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = []
        empire = screen.empires[1]

        manager._apply_turn_start_state(empire)

        screen.ui.open_event_log_with_events.assert_not_called()

    def test_obs3_syncs_event_log_unconditionally_on_player_swap(self):
        """QA Obs 3 (2026-05-16): the data-source rebind must fire EVERY
        player swap, regardless of whether the incoming player has events.
        Without this, a cached EventLogWindow alive from the previous
        player's turn keeps showing that player's rows when the new player
        has nothing to display.

        ``sync_event_log_for_empire(events, empire_name)`` is the
        unconditional rebind hook; ``open_event_log_with_events(...)``
        remains conditional on a non-empty events list (the auto-popup
        gate)."""
        # Case A: incoming player has events.
        manager, screen = _make_game_state_manager()
        events = [MagicMock()]
        screen._facade.events.turn_events.return_value = events
        empire = screen.empires[1]

        manager._apply_turn_start_state(empire)

        screen.ui.sync_event_log_for_empire.assert_called_once_with(
            events, empire_name=empire.name,
        )
        screen.ui.open_event_log_with_events.assert_called_once_with(
            events, empire_name=empire.name,
        )

        # Case B: incoming player has NO events. sync still fires (so a
        # cached visible window from the previous player is refreshed to
        # empty + hidden); auto-open does not.
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = []
        empire = screen.empires[1]

        manager._apply_turn_start_state(empire)

        screen.ui.sync_event_log_for_empire.assert_called_once_with(
            [], empire_name=empire.name,
        )
        screen.ui.open_event_log_with_events.assert_not_called()

    def test_respects_suppress_event_log_flag(self):
        """``_suppress_event_log`` (FEAT-20) gates the popup so dev-loop
        ``run_n_turns`` can surface a single combined log at the end
        instead of one modal per turn."""
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = [MagicMock()]
        manager._suppress_event_log = True
        empire = screen.empires[1]

        manager._apply_turn_start_state(empire)

        screen.ui.open_event_log_with_events.assert_not_called()

    def test_short_circuits_when_empire_has_no_colonies(self):
        """Pathological edge case: empire has lost all colonies — leave
        state untouched rather than crash. Camera/selection are not
        touched; event-log popup also short-circuits (no home to
        anchor)."""
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = [MagicMock()]
        empire = screen.empires[1]
        empire.colonies = []

        manager._apply_turn_start_state(empire)

        screen.center_camera_on.assert_not_called()
        screen.on_ui_selection.assert_not_called()
        screen.ui.open_event_log_with_events.assert_not_called()

    def test_finds_events_after_process_turn_increment(self):
        """Issue #9 regression: end-to-end simulation of the rejected-fix
        scenario.

        ``GameSession.process_turn`` increments ``turn_number`` after
        running, so events filed at turn N live in the log while
        ``facade.session_meta.turn_number()`` returns N+1. A live facade-shaped
        fake that maps ``get_turn_events(turn, ...)`` -> only events
        with matching turn proves the helper looks up the *just-completed*
        turn (N), not the upcoming turn (N+1).
        """
        manager, screen = _make_game_state_manager()
        empire = screen.empires[1]

        # Events filed under turn N=3 (turn engine wrote them before the
        # session.turn_number += 1 in GameSession.process_turn).
        turn_n_events = [MagicMock(name="evt_turn_3")]
        events_by_turn = {3: turn_n_events}

        # Post-process: session.turn_number is now N+1 = 4.
        screen._facade.session_meta.turn_number.return_value = 4
        screen._facade.events.turn_events.side_effect = (
            lambda turn, *, empire_id: list(events_by_turn.get(turn, []))
        )

        manager._apply_turn_start_state(empire)

        # The helper must find the turn-3 events even though the live
        # session is now on turn 4.
        screen.ui.open_event_log_with_events.assert_called_once_with(
            turn_n_events, empire_name=empire.name
        )


@pytest.mark.parametrize(
    "human_player_ids,expected_next_id,need_display_patch",
    [
        ([0, 1], 1, False),  # per-player switch (else branch)
        ([0], 0, True),       # full-turn rollover branch
    ],
    ids=["per_player_switch", "rollover_branch"],
)
def test_advance_turn_helper_invocation(
    human_player_ids, expected_next_id, need_display_patch
):
    """Parametrized (PROJ-479 Task 1.10): the turn-start helper is
    invoked with the correct next empire on BOTH the per-player-switch
    (else) branch and the full-turn-rollover branch."""
    manager, screen = _make_game_state_manager()
    screen.current_player_index = 0
    screen.human_player_ids = human_player_ids
    screen._facade.events.turn_events.return_value = []

    contexts = [patch.object(manager, "_apply_turn_start_state")]
    if need_display_patch:
        contexts.append(patch("pygame.display.get_surface", return_value=None))
    with contextlib.ExitStack() as stack:
        mock_helper = stack.enter_context(contexts[0])
        for ctx in contexts[1:]:
            stack.enter_context(ctx)
        manager.advance_turn()

    mock_helper.assert_called_once()
    called_empire = mock_helper.call_args[0][0]
    assert called_empire.id == expected_next_id


@pytest.mark.parametrize(
    "human_player_ids,need_display_patch",
    [
        ([0, 1], False),
        ([0], True),
    ],
    ids=["per_player_switch", "rollover_branch"],
)
def test_advance_turn_runs_helper_after_sync_active_empire(
    human_player_ids, need_display_patch
):
    """Parametrized (PROJ-479 Task 1.10): on BOTH branches,
    ``_sync_active_empire`` must run BEFORE ``_apply_turn_start_state``
    so event-log scoping reads the just-rotated empire (BUG-125)."""
    manager, screen = _make_game_state_manager()
    screen.current_player_index = 0
    screen.human_player_ids = human_player_ids
    screen._facade.events.turn_events.return_value = []
    call_order = []

    def record_sync():
        call_order.append("sync")

    def record_helper(empire):
        call_order.append("helper")

    contexts = [
        patch.object(manager, "_sync_active_empire", side_effect=record_sync),
        patch.object(manager, "_apply_turn_start_state",
                     side_effect=record_helper),
    ]
    if need_display_patch:
        contexts.append(patch("pygame.display.get_surface", return_value=None))
    with contextlib.ExitStack() as stack:
        for ctx in contexts:
            stack.enter_context(ctx)
        manager.advance_turn()

    assert call_order == ["sync", "helper"]


class TestAdvanceTurnPerPlayerSwitch:
    """Issue #9: per-player switch (else branch of ``advance_turn``)
    invokes the turn-start helper for the next empire.

    Note: the 2 structurally identical tests
    (`applies_turn_start_state`, `runs_helper_after_sync_active_empire`)
    were parametrized at module scope above per PROJ-479 Task 1.10. The
    branch-specific behavior tests remain here."""

    def test_else_branch_clears_selection_end_to_end(self):
        """Acceptance criterion: ``selected_fleet`` / ``selected_object`` /
        ``last_selected_system`` cleared at the per-player switch."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]
        screen.selected_fleet = MagicMock()
        screen.selected_object = MagicMock()
        screen.last_selected_system = MagicMock()
        screen._facade.events.turn_events.return_value = []

        manager.advance_turn()

        assert screen.selected_fleet is None
        assert screen.selected_object is None
        assert screen.last_selected_system is None

    def test_else_branch_auto_selects_next_player_home(self):
        """Acceptance criterion: lower-right detail panel populated via
        ``on_ui_selection(home_colony)``."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]
        screen._facade.events.turn_events.return_value = []

        manager.advance_turn()

        next_empire = screen.empires[1]
        screen.on_ui_selection.assert_called_once_with(next_empire.colonies[0])

    def test_else_branch_opens_event_log_for_next_empire(self):
        """Acceptance criterion: event log auto-opens on each per-player
        turn-start (not only after a full turn). The lookup uses the
        previous turn (``session.turn_number - 1``) because the helper
        runs after ``process_turn`` has incremented; asymmetric mock
        (5 -> 4) prevents tautology."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]
        mock_events = [MagicMock()]
        screen._facade.events.turn_events.return_value = mock_events
        screen._facade.session_meta.turn_number.return_value = 5

        manager.advance_turn()

        next_empire = screen.empires[1]
        screen._facade.events.turn_events.assert_called_once_with(
            turn=4, empire_id=next_empire.id
        )
        screen.ui.open_event_log_with_events.assert_called_once_with(
            mock_events, empire_name=next_empire.name
        )


class TestAdvanceTurnRolloverBranch:
    """Issue #9: full-turn rollover branch (after ``process_full_turn``)
    also invokes the turn-start helper for player 1.

    Note: the 2 structurally identical tests
    (`applies_helper_for_player_1`, `runs_helper_after_sync_active_empire`)
    were parametrized at module scope above per PROJ-479 Task 1.10."""

    def test_rollover_no_double_fire_of_event_log(self):
        """``process_full_turn`` no longer opens the log directly; the
        helper is the single opener. Rollover must therefore see exactly
        one ``open_event_log_with_events`` call, not two."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0]
        mock_events = [MagicMock()]
        screen._facade.events.turn_events.return_value = mock_events

        with patch("pygame.display.get_surface", return_value=None):
            manager.advance_turn()

        assert screen.ui.open_event_log_with_events.call_count == 1

    def test_rollover_does_not_call_helper_when_turn_failed(self):
        """On a ``TurnFailedError``, ``process_full_turn`` returns early
        with rollback. The rollover helper should still be invoked so
        the player sees a clean state, but with no events (the facade
        will still answer ``get_turn_events`` — returning whatever it
        considers valid after the rollback). The acceptance test here
        is narrower: a TurnFailed must NOT raise out of advance_turn.
        """
        from game.core.exceptions import TurnFailedError

        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0]
        screen._facade.events.turn_events.return_value = []
        screen._facade.process_turn.side_effect = TurnFailedError(
            message="phase boom",
            code="S101",
            context={"phase_name": "p", "tick": 1, "turn_number": 1,
                     "original_type": "RuntimeError"},
        )

        with patch("pygame.display.get_surface", return_value=None), \
             patch.object(manager, "_show_turn_failed_dialog"):
            # Must not raise.
            manager.advance_turn()


# ===========================================================================
# FEAT-20: process_full_turn (renamed public) + run_n_turns
# ===========================================================================

class TestProcessFullTurnPublic:
    """`_process_full_turn` is renamed to public `process_full_turn` (FEAT-20)."""

    def test_public_alias_exists(self):
        """A public `process_full_turn` method must exist."""
        manager, _screen = _make_game_state_manager()
        assert callable(getattr(manager, "process_full_turn", None))


class TestRunNTurns:
    """FEAT-20: dev-mode `run_n_turns(n)` runs the full turn n times with cancel support."""

    def test_calls_process_full_turn_n_times(self):
        """Calling run_n_turns(5) invokes process_full_turn 5 times."""
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = []
        screen.dev_run_cancel_requested = False

        with patch.object(manager, "process_full_turn") as mock_pft, \
             patch.object(manager, "_pump_cancel_events"), \
             patch("pygame.display.get_surface", return_value=None):
            completed = manager.run_n_turns(5)

        assert mock_pft.call_count == 5
        assert completed == 5

    def test_stops_on_cancel_after_current_turn(self):
        """If cancel is requested between iterations, the loop stops cleanly.

        PROJ-323 Task 5.1: use itertools.count Counter for tick-tracking
        side_effect, assert on outcome (completed) rather than internal
        mock call counts.
        """
        from itertools import count
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = []
        screen.dev_run_cancel_requested = False

        # Set the cancel flag after the second process_full_turn call so the
        # loop should stop before iteration 3.
        counter = count(1)

        def trip_cancel_after_two(*args, **kwargs):
            if next(counter) == 2:
                screen.dev_run_cancel_requested = True

        with patch.object(manager, "process_full_turn", side_effect=trip_cancel_after_two), \
             patch.object(manager, "_pump_cancel_events"), \
             patch("pygame.display.get_surface", return_value=None):
            completed = manager.run_n_turns(10)

        # Outcome assertion: 2 turns completed before cancel halted the loop.
        assert completed == 2

    def test_returns_completed_count(self):
        """run_n_turns returns the number of turns actually completed."""
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = []
        screen.dev_run_cancel_requested = False

        with patch.object(manager, "process_full_turn"), \
             patch.object(manager, "_pump_cancel_events"), \
             patch("pygame.display.get_surface", return_value=None):
            completed = manager.run_n_turns(3)

        assert completed == 3

    def test_resets_cancel_flag_at_start(self):
        """A stale `dev_run_cancel_requested` flag should be cleared on entry."""
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = []
        # Pre-set: simulate a leftover flag from a prior aborted run.
        screen.dev_run_cancel_requested = True

        with patch.object(manager, "process_full_turn") as mock_pft, \
             patch.object(manager, "_pump_cancel_events"), \
             patch("pygame.display.get_surface", return_value=None):
            completed = manager.run_n_turns(2)

        assert mock_pft.call_count == 2
        assert completed == 2

    def test_suppresses_event_log_during_loop_and_surfaces_combined_at_end(self):
        """Per-turn event log auto-open is suppressed during the loop;
        a combined log opens once at the end with all events."""
        manager, screen = _make_game_state_manager()
        # Each call returns a different list of events.
        e1 = [MagicMock(name="evt1")]
        e2 = [MagicMock(name="evt2"), MagicMock(name="evt3")]
        e3 = []
        screen._facade.events.turn_events.side_effect = [e1, e2, e3]
        screen.dev_run_cancel_requested = False
        # Reset the open-event-log mock since process_full_turn will be REAL here.
        screen.ui.open_event_log_with_events.reset_mock()

        with patch.object(manager, "_pump_cancel_events"), \
             patch("pygame.display.get_surface", return_value=None):
            manager.run_n_turns(3)

        # During the loop, open_event_log_with_events must NOT be called per-turn —
        # only once at the end with the combined event list (e1 + e2).
        # (Empty per-turn lists contribute nothing.)
        assert screen.ui.open_event_log_with_events.call_count == 1
        combined_events = screen.ui.open_event_log_with_events.call_args[0][0]
        assert len(combined_events) == 3  # 1 + 2 + 0
        assert combined_events[0] is e1[0]
        assert combined_events[1] is e2[0]
        assert combined_events[2] is e2[1]

    def test_no_combined_log_when_no_events(self):
        """If no turn produced events, no event log opens at the end."""
        manager, screen = _make_game_state_manager()
        screen._facade.events.turn_events.return_value = []
        screen.dev_run_cancel_requested = False
        screen.ui.open_event_log_with_events.reset_mock()

        with patch.object(manager, "_pump_cancel_events"), \
             patch("pygame.display.get_surface", return_value=None):
            manager.run_n_turns(2)

        screen.ui.open_event_log_with_events.assert_not_called()


# ===========================================================================
# Issue #25: defeated player elimination from turn rotation
# ===========================================================================

def _make_n_player_state_manager(n_players: int):
    """Build a game state manager wired with ``n_players`` human empires.

    Each empire has one fleet and one colony so ``is_eliminated()`` is
    False by default. Tests then strip assets to flip a specific empire.
    """
    from game.ui.screens.strategy_game_state_manager import StrategyGameStateManager

    mock_screen = MagicMock()
    mock_screen.session = MagicMock()
    mock_screen._facade = MagicMock()
    # PROJ-475 Phase 2 Task 2.4: auto-save routes through
    # facade.session_meta.save_current_game(); concrete triple for the unpack.
    mock_screen._facade.session_meta.save_current_game.return_value = (
        True, "Saved", "/tmp/save.json"
    )
    mock_screen.ui = MagicMock()
    mock_screen.ui.manager = MagicMock()
    mock_screen.ui.width = 1920
    mock_screen.ui.height = 1080
    mock_screen.turn_processing = False
    mock_screen.current_player_index = 0
    mock_screen.selected_object = None
    mock_screen.selected_fleet = None
    mock_screen.last_selected_system = None

    empires = []
    for i in range(n_players):
        emp = MagicMock()
        emp.id = i
        emp.name = f"Empire {i}"
        emp.colonies = [MagicMock(name=f"empire{i}_home")]
        emp.fleets = [MagicMock(name=f"empire{i}_fleet")]
        emp.is_eliminated = MagicMock(return_value=False)
        empires.append(emp)

    mock_screen.empires = empires
    mock_screen.session.empires = empires
    # PROJ-477 Phase 4: manager iterates empires via scene.world.iter_empires.
    mock_screen.world.iter_empires.side_effect = lambda: iter(mock_screen.empires)
    ids = list(range(n_players))
    mock_screen.session.human_player_ids = ids
    mock_screen.human_player_ids = ids
    # PROJ-475 Phase 3: facade-sourced human-player ids (see _make_game_state_manager).
    _hpi = lambda: mock_screen.human_player_ids
    mock_screen._facade.session_meta.human_player_ids.side_effect = _hpi
    mock_screen.facade.session_meta.human_player_ids.side_effect = _hpi
    mock_screen.active_empire = empires[0]

    def _current_empire(self):
        idx = self.human_player_ids[self.current_player_index]
        return next(e for e in self.empires if e.id == idx)

    type(mock_screen).current_empire = property(_current_empire)

    mock_screen.draw = MagicMock()
    mock_screen.center_camera_on = MagicMock()
    mock_screen.on_ui_selection = MagicMock()

    manager = StrategyGameStateManager(mock_screen)
    return manager, mock_screen, empires


def _eliminate(empire) -> None:
    """Flip an empire's assets so ``is_eliminated()`` returns True."""
    empire.colonies = []
    empire.fleets = []
    empire.is_eliminated = MagicMock(return_value=True)


class TestEmpireIsEliminatedIntegration:
    """Issue #25: ``_defeated_player_ids`` tracker initialises empty for
    a fresh session and detection runs through the turn-start hook."""

    def test_defeated_player_ids_starts_empty(self):
        """Fresh manager has no entries — first turn-start of an already
        defeated empire will populate it."""
        manager, _, _ = _make_n_player_state_manager(2)

        assert manager._defeated_player_ids == set()


class TestAdvanceTurnRotationSkip:
    """Issue #25: ``advance_turn`` must skip empires whose IDs are in
    ``_defeated_player_ids`` when picking the next rotation slot.
    """

    def test_3p_skips_defeated_middle_player(self):
        """3 players, P1 defeated mid-game: P0 → (skip P1) → P2 → rollover."""
        manager, screen, empires = _make_n_player_state_manager(3)
        screen._facade.events.turn_events.return_value = []
        manager._defeated_player_ids = {1}

        # Currently at P0 (index 0). Advance — should land on P2 (index 2),
        # NOT P1 (index 1).
        screen.current_player_index = 0
        manager.advance_turn()

        assert screen.current_player_index == 2

    def test_3p_rollover_skips_defeated(self):
        """3 players, P1 defeated, currently at P2 (last live): advance
        rolls over to P0 and processes the full turn."""
        manager, screen, empires = _make_n_player_state_manager(3)
        screen._facade.events.turn_events.return_value = []
        manager._defeated_player_ids = {1}
        screen.current_player_index = 2

        with patch("pygame.display.get_surface", return_value=None):
            manager.advance_turn()

        # Rollover landed on P0 and called process_turn.
        assert screen.current_player_index == 0
        screen._facade.process_turn.assert_called_once()

    def test_2p_single_survivor_repeated_end_turn_advances_survivor(self):
        """2 players, P0 defeated. Repeated End Turn keeps advancing P1's
        turn without prompting P0 and without crashing."""
        manager, screen, empires = _make_n_player_state_manager(2)
        screen._facade.events.turn_events.return_value = []
        manager._defeated_player_ids = {0}
        screen.current_player_index = 1

        with patch("pygame.display.get_surface", return_value=None):
            for _ in range(5):
                manager.advance_turn()

        # P1 stays the active player; full-turn rollover fires every click.
        assert screen.current_player_index == 1
        assert screen._facade.process_turn.call_count == 5

    def test_2p_p2_defeated_advance_lands_back_on_p1(self):
        """2P, P1 (index 1) defeated. From P0, End Turn rolls over to P0
        with a full-turn processed."""
        manager, screen, empires = _make_n_player_state_manager(2)
        screen._facade.events.turn_events.return_value = []
        manager._defeated_player_ids = {1}
        screen.current_player_index = 0

        with patch("pygame.display.get_surface", return_value=None):
            manager.advance_turn()

        assert screen.current_player_index == 0
        screen._facade.process_turn.assert_called_once()


class TestApplyTurnStartStateDefeatDetection:
    """Issue #25: turn-start hook detects new defeats, fires modal once,
    AND still surfaces the just-completed turn's event log so the player
    sees what led to their defeat (per user direction).
    """

    def test_newly_eliminated_empire_fires_defeat_modal(self):
        """First turn-start after an empire is eliminated: ``_show_defeat_dialog``
        is called and the empire id is added to ``_defeated_player_ids``."""
        manager, screen, empires = _make_n_player_state_manager(2)
        screen._facade.events.turn_events.return_value = []
        defeated = empires[1]
        _eliminate(defeated)

        with patch.object(manager, "_show_defeat_dialog") as mock_modal:
            manager._apply_turn_start_state(defeated)

        mock_modal.assert_called_once_with(defeated)
        assert 1 in manager._defeated_player_ids

    def test_defeat_modal_fires_once(self):
        """Subsequent turn-start calls for the same empire do NOT re-fire
        the modal — ``_defeated_player_ids`` membership gates it."""
        manager, screen, empires = _make_n_player_state_manager(2)
        screen._facade.events.turn_events.return_value = []
        defeated = empires[1]
        _eliminate(defeated)

        with patch.object(manager, "_show_defeat_dialog") as mock_modal:
            manager._apply_turn_start_state(defeated)
            manager._apply_turn_start_state(defeated)

        assert mock_modal.call_count == 1

    def test_defeated_empire_still_sees_event_log(self):
        """Per user direction (Q3): a newly defeated empire sees both the
        last-turn event log AND the defeat modal. The event-log lookup
        must still happen for the just-completed turn."""
        manager, screen, empires = _make_n_player_state_manager(2)
        mock_events = [MagicMock(name="last_turn_event")]
        screen._facade.events.turn_events.return_value = mock_events
        screen._facade.session_meta.turn_number.return_value = 7
        defeated = empires[1]
        _eliminate(defeated)

        with patch.object(manager, "_show_defeat_dialog"):
            manager._apply_turn_start_state(defeated)

        # Event log opened scoped to the defeated empire. (Matches the
        # current helper's ``get_turn_number()`` call — the `-1` queried
        # by the issue #9 fix lives on the fix/issue-9 branch and is not
        # yet merged into main, so the helper uses the bare turn number
        # here.)
        screen._facade.events.turn_events.assert_called_once_with(
            turn=7, empire_id=defeated.id
        )
        screen.ui.open_event_log_with_events.assert_called_once_with(
            mock_events, empire_name=defeated.name
        )

    def test_defeated_empire_skips_camera_focus(self):
        """A defeated empire has no colonies — ``center_camera_on`` and
        ``on_ui_selection`` must not be called."""
        manager, screen, empires = _make_n_player_state_manager(2)
        screen._facade.events.turn_events.return_value = []
        defeated = empires[1]
        _eliminate(defeated)

        with patch.object(manager, "_show_defeat_dialog"):
            manager._apply_turn_start_state(defeated)

        screen.center_camera_on.assert_not_called()
        screen.on_ui_selection.assert_not_called()

    def test_live_empire_does_not_fire_defeat_modal(self):
        """Regression guard: live empires must NOT trigger the modal or
        the defeated-set bookkeeping."""
        manager, screen, empires = _make_n_player_state_manager(2)
        screen._facade.events.turn_events.return_value = []
        live = empires[1]

        with patch.object(manager, "_show_defeat_dialog") as mock_modal:
            manager._apply_turn_start_state(live)

        mock_modal.assert_not_called()
        assert manager._defeated_player_ids == set()

    def test_live_empire_path_unchanged(self):
        """Issue #9 composition: a live empire still gets the four
        original actions — clear selection, camera focus, on_ui_selection,
        event log."""
        manager, screen, empires = _make_n_player_state_manager(2)
        mock_events = [MagicMock(name="evt")]
        screen._facade.events.turn_events.return_value = mock_events
        screen._facade.session_meta.turn_number.return_value = 3
        screen.selected_fleet = MagicMock()
        screen.selected_object = MagicMock()
        screen.last_selected_system = MagicMock()
        live = empires[1]

        manager._apply_turn_start_state(live)

        assert screen.selected_fleet is None
        assert screen.selected_object is None
        assert screen.last_selected_system is None
        screen.center_camera_on.assert_called_once_with(live.colonies[0])
        screen.on_ui_selection.assert_called_once_with(live.colonies[0])
        screen.ui.open_event_log_with_events.assert_called_once_with(
            mock_events, empire_name=live.name
        )

    def test_event_log_fires_before_defeat_modal(self):
        """UX ordering: the event log opens first (so the player sees
        what happened), then the defeat modal pops. Both must be
        invoked, in that order, by a single ``_apply_turn_start_state``
        call on a newly defeated empire."""
        manager, screen, empires = _make_n_player_state_manager(2)
        screen._facade.events.turn_events.return_value = [MagicMock()]
        defeated = empires[1]
        _eliminate(defeated)

        call_order = []
        screen.ui.open_event_log_with_events.side_effect = (
            lambda *a, **k: call_order.append("event_log")
        )

        with patch.object(
            manager, "_show_defeat_dialog",
            side_effect=lambda *_: call_order.append("defeat_modal"),
        ):
            manager._apply_turn_start_state(defeated)

        assert call_order == ["event_log", "defeat_modal"]


class TestShowDefeatDialog:
    """Issue #25: ``_show_defeat_dialog`` mirrors ``_show_turn_failed_dialog``
    plumbing — Pattern #31 modal tracking, headless fallback.
    """

    def test_logs_when_no_ui_manager(self, caplog):
        """Headless / mocked environment: no UIManager → logger.error
        and no crash."""
        import logging
        manager, screen, empires = _make_n_player_state_manager(2)
        screen.ui.manager = None
        defeated = empires[1]
        _eliminate(defeated)

        with caplog.at_level(logging.ERROR,
                             logger="game.ui.screens.strategy_game_state_manager"):
            manager._show_defeat_dialog(defeated)

        # No exception means the headless fallback fired.
        assert any("defeat" in rec.message.lower() for rec in caplog.records)

    def test_constructs_dialog_with_empire_name_and_window_manager(self):
        """When a real ui.manager is present, the dialog is constructed
        with the empire name and the strategy window manager threaded
        through for Pattern #31 modal tracking."""
        manager, screen, empires = _make_n_player_state_manager(2)
        defeated = empires[1]
        _eliminate(defeated)
        fake_wm = MagicMock(name="window_manager")
        screen.ui.window_manager = fake_wm

        with patch(
            "game.ui.screens.strategy_game_state_manager.DefeatDialog"
        ) as MockDialog:
            manager._show_defeat_dialog(defeated)

        MockDialog.assert_called_once()
        kwargs = MockDialog.call_args.kwargs
        assert kwargs["manager"] is screen.ui.manager
        assert kwargs["empire_name"] == defeated.name
        assert kwargs["window_manager"] is fake_wm


class TestAdvanceTurnDefeatedSkipEndToEnd:
    """Issue #25: end-to-end advance_turn with a defeated empire already
    in the set — the helper must NOT be called for them."""

    def test_advance_skips_helper_for_defeated_empire(self):
        """3P, P1 in defeated set. From P0, advance lands on P2 and the
        helper is invoked for P2, not P1."""
        manager, screen, empires = _make_n_player_state_manager(3)
        screen._facade.events.turn_events.return_value = []
        manager._defeated_player_ids = {1}
        screen.current_player_index = 0

        with patch.object(manager, "_apply_turn_start_state") as mock_helper:
            manager.advance_turn()

        mock_helper.assert_called_once()
        called_empire = mock_helper.call_args[0][0]
        assert called_empire.id == 2


class TestPerPlayerUiStateContainer:
    """Issue #28: ``StrategyGameStateManager`` owns a session-scoped
    ``PerPlayerUiState`` container so per-window view-state (column
    visibility, sort, tab indices, scroll positions) survives hot-seat
    rotation."""

    def test_container_initialised(self):
        from game.ui.screens.per_player_ui_state import PerPlayerUiState
        manager, _ = _make_game_state_manager()
        assert isinstance(manager._per_player_ui_state, PerPlayerUiState)


class TestAdvanceTurnCapturesOutgoingState:
    """Issue #28: ``advance_turn`` captures the outgoing player's per-window
    view-state snapshots BEFORE ``_next_live_player_index`` mutates
    ``current_player_index``. Otherwise the capture identity would be
    the incoming player, not the outgoing one."""

    def test_capture_hook_invoked_before_index_advance(self):
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]

        captured_index_at_call = []
        original = manager._capture_outgoing_player_state

        def spy() -> None:
            captured_index_at_call.append(screen.current_player_index)
            original()

        with patch.object(manager, "_capture_outgoing_player_state", side_effect=spy):
            manager.advance_turn()

        assert captured_index_at_call == [0]

    def test_capture_writes_each_live_windows_snapshot_to_outgoing_slot(self):
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]

        # Two opt-in windows: each exposes SNAPSHOT_SLOT, capture_view_state.
        window_a = MagicMock()
        window_a.SNAPSHOT_SLOT = "planet_list"
        window_a.alive = MagicMock(return_value=True)
        window_a.capture_view_state = MagicMock(return_value={"a": 1})
        window_b = MagicMock()
        window_b.SNAPSHOT_SLOT = "empire_panel"
        window_b.alive = MagicMock(return_value=True)
        window_b.capture_view_state = MagicMock(return_value={"b": 2})

        screen.ui.window_manager.iter_snapshot_windows = MagicMock(
            return_value=[window_a, window_b]
        )

        manager.advance_turn()

        assert manager._per_player_ui_state.load(0, "planet_list") == {"a": 1}
        assert manager._per_player_ui_state.load(0, "empire_panel") == {"b": 2}

    def test_capture_skips_dead_windows(self):
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]

        dead = MagicMock()
        dead.SNAPSHOT_SLOT = "planet_list"
        dead.alive = MagicMock(return_value=False)
        dead.capture_view_state = MagicMock()

        screen.ui.window_manager.iter_snapshot_windows = MagicMock(
            return_value=[dead]
        )

        manager.advance_turn()

        dead.capture_view_state.assert_not_called()
        assert manager._per_player_ui_state.load(0, "planet_list") is None

    def test_capture_handles_missing_window_manager_protocol(self):
        """Headless tests / mocks without ``iter_snapshot_windows`` must not crash."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]

        # Strip the optional registry hook only; rest of screen.ui is intact.
        screen.ui.window_manager = None

        # Must not raise.
        manager.advance_turn()

    def test_capture_handles_window_manager_without_iter(self):
        """Window manager without ``iter_snapshot_windows`` attr — no-op."""
        manager, screen = _make_game_state_manager()
        screen.current_player_index = 0
        screen.human_player_ids = [0, 1]

        # Real-shaped window manager but missing the optional hook.
        screen.ui.window_manager = MagicMock(spec=["register_modal"])

        manager.advance_turn()  # no raise


class TestApplyTurnStartStateRestoresIncomingState:
    """Issue #28: at the TOP of ``_apply_turn_start_state``, BEFORE
    issue #25's defeat short-circuit and BEFORE selection-clear, the
    incoming player's snapshots are pushed back onto each opt-in
    window via ``apply_view_state``."""

    def test_restore_called_before_defeat_short_circuit(self):
        """Even a defeated empire's incoming state is restored — so the
        defeat-modal-adjacent windows present in their saved view."""
        manager, screen = _make_game_state_manager()
        empire = screen.empires[0]
        _eliminate(empire)

        # Pre-seed a saved snapshot for the eliminated empire.
        manager._per_player_ui_state.save(empire.id, "planet_list", {"v": 1})

        window = MagicMock()
        window.SNAPSHOT_SLOT = "planet_list"
        window.alive = MagicMock(return_value=True)
        screen.ui.window_manager.iter_snapshot_windows = MagicMock(
            return_value=[window]
        )
        screen._facade.events.turn_events.return_value = []
        screen._facade.session_meta.turn_number.return_value = 5

        with patch.object(manager, "_show_defeat_dialog"):
            manager._apply_turn_start_state(empire)

        window.apply_view_state.assert_called_once_with({"v": 1})

    def test_restore_uses_load_so_first_turn_passes_none(self):
        """An empire with no saved snapshot still has apply called, with
        ``None`` — windows decide whether to no-op or reset to defaults."""
        manager, screen = _make_game_state_manager()
        empire = screen.empires[0]

        window = MagicMock()
        window.SNAPSHOT_SLOT = "planet_list"
        window.alive = MagicMock(return_value=True)
        screen.ui.window_manager.iter_snapshot_windows = MagicMock(
            return_value=[window]
        )
        screen._facade.events.turn_events.return_value = []
        screen._facade.session_meta.turn_number.return_value = 5

        manager._apply_turn_start_state(empire)

        window.apply_view_state.assert_called_once_with(None)

    def test_restore_skips_dead_windows(self):
        manager, screen = _make_game_state_manager()
        empire = screen.empires[0]

        dead = MagicMock()
        dead.SNAPSHOT_SLOT = "planet_list"
        dead.alive = MagicMock(return_value=False)
        screen.ui.window_manager.iter_snapshot_windows = MagicMock(
            return_value=[dead]
        )
        screen._facade.events.turn_events.return_value = []
        screen._facade.session_meta.turn_number.return_value = 5

        manager._apply_turn_start_state(empire)

        dead.apply_view_state.assert_not_called()

    def test_restore_handles_missing_window_manager_protocol(self):
        manager, screen = _make_game_state_manager()
        empire = screen.empires[0]

        # Strip the registry hook.
        screen.ui = MagicMock(spec=["lbl_current_player", "manager", "width", "height", "show_detailed_report", "open_event_log_with_events", "sync_event_log_for_empire"])
        screen.ui.lbl_current_player = MagicMock()
        screen.ui.manager = MagicMock()
        screen.ui.width = 1920
        screen.ui.height = 1080
        screen._facade.events.turn_events.return_value = []
        screen._facade.session_meta.turn_number.return_value = 5

        # Must not raise.
        manager._apply_turn_start_state(empire)


class TestPerPlayerStateHotSeatRoundTrip:
    """Issue #28: end-to-end — Player 0 saves a snapshot at turn-end,
    Player 1 takes the turn (gets None), then rotation returns to
    Player 0 who sees their saved state restored."""

    def test_hot_seat_two_player_round_trip(self):
        manager, screen, empires = _make_n_player_state_manager(2)
        screen._facade.events.turn_events.return_value = []
        screen._facade.session_meta.turn_number.return_value = 5

        # Each empire's window starts with empire-specific state.
        captures = {0: {"view": "p0_view"}, 1: {"view": "p1_view"}}
        applies: list[tuple[int, dict | None]] = []

        window = MagicMock()
        window.SNAPSHOT_SLOT = "planet_list"
        window.alive = MagicMock(return_value=True)

        def _capture():
            return captures[screen.current_player_index]

        def _apply(state):
            applies.append((screen.current_player_index, state))

        window.capture_view_state.side_effect = _capture
        window.apply_view_state.side_effect = _apply
        screen.ui.window_manager.iter_snapshot_windows = MagicMock(
            return_value=[window]
        )

        # P0 → P1 (else branch)
        screen.current_player_index = 0
        manager.advance_turn()
        assert screen.current_player_index == 1
        # P1 → P0 (rollover; processes full turn). Test the index-2 capture/restore.
        manager.advance_turn()
        # Back to P0
        assert screen.current_player_index == 0

        # Snapshots saved per empire
        assert manager._per_player_ui_state.load(0, "planet_list") == {"view": "p0_view"}
        assert manager._per_player_ui_state.load(1, "planet_list") == {"view": "p1_view"}

        # P1 saw None on their first apply; P0 (returning) sees their saved snapshot.
        first_apply_for_p1 = next((s for idx, s in applies if idx == 1), "missing")
        last_apply_for_p0 = [s for idx, s in applies if idx == 0][-1]
        assert first_apply_for_p1 is None
        assert last_apply_for_p0 == {"view": "p0_view"}


class TestDefeatedPlayerSnapshotPreserved:
    """Issue #28: defeated empires' snapshots remain in the container
    (option a — keep indefinitely). They are never re-applied because
    ``_apply_turn_start_state`` is never invoked for them again
    (rotation skips). The container's contents do not block memory
    reclamation in any meaningful way and survive in case of session
    state restoration."""

    def test_defeated_empires_snapshot_is_not_cleared(self):
        manager, screen, empires = _make_n_player_state_manager(3)
        screen._facade.events.turn_events.return_value = []
        screen._facade.session_meta.turn_number.return_value = 5

        # Pre-seed P1's snapshot, then eliminate them.
        manager._per_player_ui_state.save(1, "planet_list", {"v": "p1"})
        _eliminate(empires[1])

        # Drive the defeat detection through the helper directly.
        with patch.object(manager, "_show_defeat_dialog"):
            manager._apply_turn_start_state(empires[1])

        # Snapshot remains (option a).
        assert manager._per_player_ui_state.load(1, "planet_list") == {"v": "p1"}
