"""
Tests for NewGameSetupScreen UI state management.

PROJ-266 Phase 2: Coverage for empire visibility, race display updates,
race callbacks, start validation, and cancel behavior. Uses bypass-init
pattern since the real __init__ requires a live pygame_gui display.
"""

from unittest.mock import MagicMock, patch


# =============================================================================
# Helpers
# =============================================================================

def _make_screen():
    """Create a NewGameSetupScreen with bypassed init and mock UI elements."""
    from game.ui.screens.new_game_setup_screen import NewGameSetupScreen

    with patch.object(NewGameSetupScreen, '__init__', lambda self, *a, **kw: None):
        screen = NewGameSetupScreen.__new__(NewGameSetupScreen)

    # Set up the attributes that real __init__ would create
    screen.player_count = 2
    screen.galaxy_type = "spiral"
    screen.system_count = 20
    screen.on_start_callback = MagicMock()
    screen.on_cancel_callback = MagicMock()
    screen.active_race_modal = None
    screen.race_modal_player_index = -1
    screen.error_label = MagicMock()

    # Mock UI element arrays (4 players max)
    screen.empire_name_inputs = [MagicMock() for _ in range(4)]
    screen.theme_labels = [MagicMock() for _ in range(4)]
    screen.num_labels = [MagicMock() for _ in range(4)]
    screen.race_preview_labels = [MagicMock() for _ in range(4)]
    screen.load_race_buttons = [MagicMock() for _ in range(4)]
    screen.setup_race_buttons = [MagicMock() for _ in range(4)]
    screen.player_races = [None, None, None, None]

    # save_name_input for _on_start_clicked
    screen.save_name_input = MagicMock()
    screen.save_name_input.get_text.return_value = "TestSave"

    # kill method (from UIWindow)
    screen.kill = MagicMock()

    return screen


def _make_race_config(name="Test Race", faction_name="Test Faction",
                      government_type="Democracy"):
    rc = MagicMock()
    rc.name = name
    rc.faction_name = faction_name
    rc.government_type = government_type
    rc.society_type = None
    rc.theme_id = "default"
    return rc


# =============================================================================
# Empire Visibility Tests
# =============================================================================


class TestUpdateEmpireVisibility:
    """Tests for _update_empire_visibility()."""

    def test_shows_correct_count_for_2_players(self):
        """With player_count=2, first 2 empire rows visible, last 2 hidden."""
        screen = _make_screen()
        screen.player_count = 2

        screen._update_empire_visibility()

        # Players 0,1 should be shown
        screen.empire_name_inputs[0].show.assert_called()
        screen.empire_name_inputs[1].show.assert_called()
        # Players 2,3 should be hidden
        screen.empire_name_inputs[2].hide.assert_called()
        screen.empire_name_inputs[3].hide.assert_called()

    def test_shows_all_4_for_4_players(self):
        """With player_count=4, all 4 rows visible."""
        screen = _make_screen()
        screen.player_count = 4

        screen._update_empire_visibility()

        for i in range(4):
            screen.empire_name_inputs[i].show.assert_called()

    def test_clears_race_for_hidden_players(self):
        """Hidden players have their race selection cleared."""
        screen = _make_screen()
        screen.player_count = 4
        screen.player_races[2] = _make_race_config()
        screen.player_races[3] = _make_race_config()

        # Reduce to 2 players
        screen.player_count = 2
        screen._update_empire_visibility()

        assert screen.player_races[2] is None
        assert screen.player_races[3] is None

    def test_does_not_clear_visible_player_races(self):
        """Visible players keep their race selection."""
        screen = _make_screen()
        race = _make_race_config()
        screen.player_races[0] = race
        screen.player_count = 2

        screen._update_empire_visibility()

        assert screen.player_races[0] is race


# =============================================================================
# Race Display Tests
# =============================================================================


class TestUpdateRaceDisplay:
    """Tests for _update_race_display()."""

    def test_with_race_shows_faction_name(self):
        """With a race selected, preview shows faction name."""
        screen = _make_screen()
        race = _make_race_config(faction_name="United Federation")
        screen.player_races[0] = race

        screen._update_race_display(0)

        screen.race_preview_labels[0].set_text.assert_called()
        call_text = screen.race_preview_labels[0].set_text.call_args[0][0]
        assert "United Federation" in call_text

    def test_without_race_shows_not_selected(self):
        """Without a race, preview shows 'not selected' message."""
        screen = _make_screen()
        screen.player_races[0] = None

        screen._update_race_display(0)

        call_text = screen.race_preview_labels[0].set_text.call_args[0][0]
        assert "not selected" in call_text.lower() or "no race" in call_text.lower() or "species" in call_text.lower()


# =============================================================================
# Race Callback Tests
# =============================================================================


class TestRaceCallbacks:
    """Tests for _on_race_selected, _on_race_created, _on_race_dialog_cancelled."""

    def test_on_race_selected_sets_player_race(self):
        """_on_race_selected sets the race for the correct player."""
        screen = _make_screen()
        race = _make_race_config()

        screen._on_race_selected(1, race)

        assert screen.player_races[1] is race
        assert screen.active_race_modal is None
        assert screen.race_modal_player_index == -1

    def test_on_race_created_sets_player_race(self):
        """_on_race_created sets the race for the correct player."""
        screen = _make_screen()
        race = _make_race_config(name="New Race")

        screen._on_race_created(0, race)

        assert screen.player_races[0] is race
        assert screen.active_race_modal is None

    def test_on_race_dialog_cancelled_clears_modal(self):
        """_on_race_dialog_cancelled clears modal state without changing race."""
        screen = _make_screen()
        screen.active_race_modal = MagicMock()
        screen.race_modal_player_index = 2
        original_race = screen.player_races[2]

        screen._on_race_dialog_cancelled()

        assert screen.active_race_modal is None
        assert screen.race_modal_player_index == -1
        assert screen.player_races[2] is original_race  # Unchanged


# =============================================================================
# Start Game Tests
# =============================================================================


class TestOnStartClicked:
    """Tests for _on_start_clicked validation and config building."""

    def test_invalid_save_name_shows_error(self):
        """Invalid save name sets error label text."""
        screen = _make_screen()
        screen.save_name_input.get_text.return_value = ""  # Empty name

        screen._on_start_clicked()

        screen.error_label.set_text.assert_called()
        screen.on_start_callback.assert_not_called()

    def test_valid_config_calls_callback(self):
        """Valid configuration calls on_start_callback with GameConfig."""
        screen = _make_screen()
        screen.save_name_input.get_text.return_value = "ValidSave"
        screen.player_count = 1
        screen.empire_name_inputs[0].get_text.return_value = "Empire One"

        with patch.object(type(screen), 'validate_save_name', return_value=(True, "")):
            screen._on_start_clicked()

        screen.on_start_callback.assert_called_once()

    def test_uses_race_name_as_empire_name(self):
        """When race is selected, uses race name as empire name."""
        screen = _make_screen()
        screen.save_name_input.get_text.return_value = "TestGame"
        screen.player_count = 1
        race = _make_race_config(name="Klingon Empire")
        screen.player_races[0] = race

        with patch.object(type(screen), 'validate_save_name', return_value=(True, "")):
            screen._on_start_clicked()

        # The config passed to callback should use the race name
        config = screen.on_start_callback.call_args[0][0]
        assert config.players[0].name == "Klingon Empire"


# =============================================================================
# Cancel Tests
# =============================================================================


class TestOnCancelClicked:
    """Tests for _on_cancel_clicked."""

    def test_cancel_calls_callback_and_kills(self):
        """Cancel invokes callback and kills window."""
        screen = _make_screen()

        screen._on_cancel_clicked()

        screen.on_cancel_callback.assert_called_once()
        screen.kill.assert_called_once()
