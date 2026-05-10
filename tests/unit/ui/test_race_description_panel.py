"""
Unit tests for RaceDescriptionPanel.

PROJ-12 Phase 4: TDD tests written before extraction.
Tests the race description panel functionality.

PROJ-322 Task 5.2 (APC-001-F02): the legacy `RaceDescriptionPanel.__new__` +
`patch.object(__init__, ...)` blocks have been replaced with the shared
`make_ui_widget` factory routed through a module-scope `_bypass_init_panel`
helper.
"""

import pytest
from unittest.mock import MagicMock, patch

from tests.fixtures.ui_widget_factory import make_ui_widget


def _bypass_init_panel(race_config=None):
    """Build a `RaceDescriptionPanel` via the shared `make_ui_widget` factory.

    Replaces the inline `__new__` + `patch.object(__init__, ...)` blocks
    that wired ~10 attrs per test. The factory mocks every
    `pygame_gui.elements.UI*` class for the duration of `__init__`, so
    `_create_content` runs but is bounded; the production attribute
    initialization (`self.race_config = race_config`,
    `self.bio_text_box = pygame_gui...UITextEntryBox(...)`, etc.) all runs
    normally with mocked elements.

    Tests typically then overwrite `panel.bio_text_box` /
    `panel.socio_text_box` with controlled `MagicMock` instances before
    exercising the method under test.

    PROJ-322 Task 5.2 / APC-001-F02.
    """
    if race_config is None:
        race_config = MagicMock()
        race_config.bio_description = ""
        race_config.socio_description = ""
    from game.ui.panels.race_description_panel import RaceDescriptionPanel

    return make_ui_widget(RaceDescriptionPanel, race_config=race_config)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_race_config():
    """Create a mock RaceConfig with description properties."""
    config = MagicMock()
    config.bio_description = "Test biological description"
    config.socio_description = "Test sociological description"
    return config


@pytest.fixture
def mock_ui_manager():
    """Create a mock pygame_gui UIManager."""
    manager = MagicMock()
    return manager


# =============================================================================
# Test: RaceDescriptionPanel Import and Creation
# =============================================================================

class TestRaceDescriptionPanelCreation:
    """Tests for RaceDescriptionPanel initialization."""

    def test_race_description_panel_has_text_box_references(self):
        """RaceDescriptionPanel has expected text box reference attributes."""
        panel = _bypass_init_panel()

        assert hasattr(panel, 'bio_text_box')
        assert hasattr(panel, 'bio_char_label')
        assert hasattr(panel, 'socio_text_box')
        assert hasattr(panel, 'socio_char_label')

    def test_race_description_panel_has_max_length_constant(self):
        """RaceDescriptionPanel has MAX_LENGTH constant."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        assert hasattr(RaceDescriptionPanel, 'MAX_LENGTH')
        # PROJ-299: bumped 500 → 5000 to accommodate LLM-generated text.
        assert RaceDescriptionPanel.MAX_LENGTH == 5000


# =============================================================================
# Test: Character Count Updates
# =============================================================================

class TestCharacterCountUpdates:
    """Tests for character count label updates."""

    def test_update_char_counts_updates_bio_label(self):
        """update_char_counts updates biological description character count."""
        panel = _bypass_init_panel()

        panel.bio_text_box = MagicMock()
        panel.bio_text_box.get_text.return_value = "Test text"  # 9 chars
        panel.bio_char_label = MagicMock()
        panel.socio_text_box = None
        panel.socio_char_label = None

        panel.update_char_counts()

        panel.bio_char_label.set_text.assert_called_with("9/5000")

    def test_update_char_counts_updates_socio_label(self):
        """update_char_counts updates sociological description character count."""
        panel = _bypass_init_panel()

        panel.bio_text_box = None
        panel.bio_char_label = None
        panel.socio_text_box = MagicMock()
        panel.socio_text_box.get_text.return_value = "A longer test text"  # 18 chars
        panel.socio_char_label = MagicMock()

        panel.update_char_counts()

        panel.socio_char_label.set_text.assert_called_with("18/5000")

    def test_update_char_counts_handles_empty_text(self):
        """update_char_counts handles empty text correctly."""
        panel = _bypass_init_panel()

        panel.bio_text_box = MagicMock()
        panel.bio_text_box.get_text.return_value = ""
        panel.bio_char_label = MagicMock()
        panel.socio_text_box = MagicMock()
        panel.socio_text_box.get_text.return_value = ""
        panel.socio_char_label = MagicMock()

        panel.update_char_counts()

        panel.bio_char_label.set_text.assert_called_with("0/5000")
        panel.socio_char_label.set_text.assert_called_with("0/5000")


# =============================================================================
# Test: Configuration Updates
# =============================================================================

class TestConfigurationUpdates:
    """Tests for updating RaceConfig from panel values."""

    def test_update_config_reads_bio_text_box(self, mock_race_config):
        """update_config reads biological description from text box."""
        panel = _bypass_init_panel(race_config=mock_race_config)

        panel.bio_text_box = MagicMock()
        panel.bio_text_box.get_text.return_value = "New bio description"
        panel.socio_text_box = None

        panel.update_config()

        assert mock_race_config.bio_description == "New bio description"

    def test_update_config_reads_socio_text_box(self, mock_race_config):
        """update_config reads sociological description from text box."""
        panel = _bypass_init_panel(race_config=mock_race_config)

        panel.bio_text_box = None
        panel.socio_text_box = MagicMock()
        panel.socio_text_box.get_text.return_value = "New socio description"

        panel.update_config()

        assert mock_race_config.socio_description == "New socio description"

    def test_update_config_enforces_max_length(self, mock_race_config):
        """update_config enforces the MAX_LENGTH char limit (5000 post-PROJ-299)."""
        panel = _bypass_init_panel(race_config=mock_race_config)

        # Create text longer than MAX_LENGTH=5000 chars
        long_text = "A" * 6000

        panel.bio_text_box = MagicMock()
        panel.bio_text_box.get_text.return_value = long_text
        panel.socio_text_box = MagicMock()
        panel.socio_text_box.get_text.return_value = long_text

        panel.update_config()

        assert len(mock_race_config.bio_description) == 5000
        assert len(mock_race_config.socio_description) == 5000


# =============================================================================
# Test: Loading from Config
# =============================================================================

class TestLoadingFromConfig:
    """Tests for setting panel values from RaceConfig."""

    def test_set_from_config_updates_bio_text_box(self, mock_race_config):
        """set_from_config updates biological text box from config."""
        mock_race_config.bio_description = "Loaded bio text"
        panel = _bypass_init_panel(race_config=mock_race_config)

        panel.bio_text_box = MagicMock()
        panel.bio_char_label = MagicMock()
        panel.socio_text_box = None
        panel.socio_char_label = None

        panel.set_from_config()

        panel.bio_text_box.set_text.assert_called_with("Loaded bio text")

    def test_set_from_config_updates_socio_text_box(self, mock_race_config):
        """set_from_config updates sociological text box from config."""
        mock_race_config.socio_description = "Loaded socio text"
        panel = _bypass_init_panel(race_config=mock_race_config)

        panel.bio_text_box = None
        panel.bio_char_label = None
        panel.socio_text_box = MagicMock()
        panel.socio_char_label = MagicMock()

        panel.set_from_config()

        panel.socio_text_box.set_text.assert_called_with("Loaded socio text")

    def test_set_from_config_handles_empty_descriptions(self, mock_race_config):
        """set_from_config handles empty/None descriptions."""
        # Construct with valid empty strings so _create_content's
        # len(race_config.bio_description) doesn't choke; override to the
        # test's intended values (one None) AFTER construction.
        mock_race_config.bio_description = ""
        mock_race_config.socio_description = ""
        panel = _bypass_init_panel(race_config=mock_race_config)
        mock_race_config.bio_description = ""
        mock_race_config.socio_description = None

        panel.bio_text_box = MagicMock()
        panel.bio_char_label = MagicMock()
        panel.socio_text_box = MagicMock()
        panel.socio_char_label = MagicMock()

        panel.set_from_config()

        panel.bio_text_box.set_text.assert_called_with("")
        panel.socio_text_box.set_text.assert_called_with("")

    def test_set_from_config_updates_char_counts(self, mock_race_config):
        """set_from_config calls update_char_counts after setting text."""
        panel = _bypass_init_panel(race_config=mock_race_config)

        panel.bio_text_box = MagicMock()
        panel.bio_text_box.get_text.return_value = "test"
        panel.bio_char_label = MagicMock()
        panel.socio_text_box = MagicMock()
        panel.socio_text_box.get_text.return_value = "test"
        panel.socio_char_label = MagicMock()

        panel.set_from_config()

        # Should update char counts after setting text
        panel.bio_char_label.set_text.assert_called()
        panel.socio_char_label.set_text.assert_called()


# =============================================================================
# Test: PROJ-299 LLM controller integration
# =============================================================================


class TestProj299ControllerIntegration:
    """Tests for PROJ-299 controller-driven LLM generation widgets."""

    def test_attach_controller_creates_button_attributes(self):
        """attach_controller() creates btn_generate_bio/socio, btn_cancel_bio/socio,
        btn_re_roll_bio/socio, lbl_bio_status, lbl_socio_status attributes."""
        panel = _bypass_init_panel()
        # Override the text boxes / char labels with plain MagicMocks so
        # attach_controller's internal access patterns are deterministic.
        panel.bio_text_box = MagicMock()
        panel.socio_text_box = MagicMock()
        panel.bio_char_label = MagicMock()
        panel.socio_char_label = MagicMock()
        panel._controller = None

        controller = MagicMock()
        with patch('pygame_gui.elements.UIButton', MagicMock()), \
             patch('pygame_gui.elements.UILabel', MagicMock()):
            panel.attach_controller(controller)

        assert panel._controller is controller
        assert hasattr(panel, 'btn_generate_bio')
        assert hasattr(panel, 'btn_cancel_bio')
        assert hasattr(panel, 'btn_re_roll_bio')
        assert hasattr(panel, 'btn_generate_socio')
        assert hasattr(panel, 'btn_cancel_socio')
        assert hasattr(panel, 'btn_re_roll_socio')
        assert hasattr(panel, 'lbl_bio_status')
        assert hasattr(panel, 'lbl_socio_status')

    def _make_panel_with_widgets(self):
        """Helper: factory-built panel + all controller-side widget mocks
        wired in. The factory's `_create_content` populated the text boxes /
        char labels as Mocks but the test wants its own controlled MagicMocks
        to assert `assert_called` against."""
        panel = _bypass_init_panel()
        panel.bio_text_box = MagicMock()
        panel.socio_text_box = MagicMock()
        panel.bio_char_label = MagicMock()
        panel.socio_char_label = MagicMock()
        panel.btn_generate_bio = MagicMock()
        panel.btn_cancel_bio = MagicMock()
        panel.btn_re_roll_bio = MagicMock()
        panel.btn_generate_socio = MagicMock()
        panel.btn_cancel_socio = MagicMock()
        panel.btn_re_roll_socio = MagicMock()
        panel.lbl_bio_status = MagicMock()
        panel.lbl_socio_status = MagicMock()
        panel._controller = None
        # Race config — set_state DONE branch reads bio/socio_description
        # to push generated text into the text boxes.
        panel.race_config = MagicMock()
        panel.race_config.bio_description = "Generated bio text"
        panel.race_config.socio_description = "Generated socio text"
        return panel

    def test_set_state_idle_shows_only_generate_bio(self):
        """Initial state: Generate enabled+visible, Cancel/Re-roll hidden."""
        from game.strategy.services.race_description_llm_controller import FieldStatus

        panel = self._make_panel_with_widgets()
        ctrl = MagicMock()
        ctrl.bio_status = FieldStatus.IDLE
        ctrl.socio_status = FieldStatus.IDLE
        ctrl.bio_elapsed_seconds = 0.0
        ctrl.socio_elapsed_seconds = 0.0
        panel._controller = ctrl

        panel.set_state(ctrl)

        panel.btn_generate_bio.show.assert_called()
        panel.btn_generate_bio.enable.assert_called()
        panel.btn_cancel_bio.hide.assert_called()
        panel.btn_re_roll_bio.hide.assert_called()

    def test_set_state_running_disables_generate_shows_cancel_locks_text_box(self):
        from game.strategy.services.race_description_llm_controller import FieldStatus

        panel = self._make_panel_with_widgets()
        ctrl = MagicMock()
        ctrl.bio_status = FieldStatus.RUNNING
        ctrl.socio_status = FieldStatus.IDLE
        ctrl.bio_elapsed_seconds = 12.0
        ctrl.socio_elapsed_seconds = 0.0
        panel._controller = ctrl

        panel.set_state(ctrl)

        panel.btn_generate_bio.disable.assert_called()
        panel.btn_cancel_bio.show.assert_called()
        panel.btn_re_roll_bio.hide.assert_called()
        # Status label shows "Generating Bio… 12s"
        call_args = panel.lbl_bio_status.set_text.call_args
        assert call_args is not None
        text = call_args[0][0]
        assert "12" in text
        assert "Generat" in text  # "Generating"
        # Text box disabled while RUNNING
        panel.bio_text_box.disable.assert_called()

    def test_set_state_done_shows_re_roll(self):
        from game.strategy.services.race_description_llm_controller import FieldStatus

        panel = self._make_panel_with_widgets()
        ctrl = MagicMock()
        ctrl.bio_status = FieldStatus.DONE
        ctrl.socio_status = FieldStatus.IDLE
        ctrl.bio_elapsed_seconds = 0.0
        ctrl.socio_elapsed_seconds = 0.0
        panel._controller = ctrl

        panel.set_state(ctrl)

        panel.btn_generate_bio.show.assert_called()
        panel.btn_generate_bio.enable.assert_called()
        panel.btn_re_roll_bio.show.assert_called()
        panel.btn_cancel_bio.hide.assert_called()
        panel.bio_text_box.enable.assert_called()

    def test_set_state_error_shows_status_label_with_error(self):
        from game.strategy.services.race_description_llm_controller import FieldStatus

        panel = self._make_panel_with_widgets()
        ctrl = MagicMock()
        ctrl.bio_status = FieldStatus.ERROR
        ctrl.socio_status = FieldStatus.IDLE
        ctrl.bio_elapsed_seconds = 0.0
        ctrl.socio_elapsed_seconds = 0.0
        ctrl.bio_error = MagicMock()
        panel._controller = ctrl

        panel.set_state(ctrl)

        # Bio error → status label visible with error message
        panel.lbl_bio_status.set_text.assert_called()
        text = panel.lbl_bio_status.set_text.call_args[0][0]
        assert "fail" in text.lower() or "error" in text.lower()

    def test_set_state_done_pushes_generated_text_into_text_box(self):
        """Regression: PROJ-299 v1 had a bug where set_state() updated
        button visibility but NEVER pushed race_config.bio_description /
        socio_description into the UI text box. The user clicked Generate,
        the LLM completed, the data model had the text — but the box stayed
        empty. Verify both fields push their text on the DONE transition."""
        from game.strategy.services.race_description_llm_controller import FieldStatus

        panel = self._make_panel_with_widgets()
        panel.race_config.bio_description = "BIO_OUTPUT"
        panel.race_config.socio_description = "SOCIO_OUTPUT"
        # Text boxes currently report a different value (so the equality
        # guard doesn't short-circuit the set_text call).
        panel.bio_text_box.get_text.return_value = ""
        panel.socio_text_box.get_text.return_value = ""

        ctrl = MagicMock()
        ctrl.bio_status = FieldStatus.DONE
        ctrl.socio_status = FieldStatus.DONE
        ctrl.bio_elapsed_seconds = 0.0
        ctrl.socio_elapsed_seconds = 0.0
        panel._controller = ctrl

        panel.set_state(ctrl)

        panel.bio_text_box.set_text.assert_called_with("BIO_OUTPUT")
        panel.socio_text_box.set_text.assert_called_with("SOCIO_OUTPUT")

    def test_set_state_done_skips_set_text_when_unchanged(self):
        """Equality guard: don't repaint the text box every frame when
        nothing changed — set_state() is called from on_change, which
        fires often."""
        from game.strategy.services.race_description_llm_controller import FieldStatus

        panel = self._make_panel_with_widgets()
        panel.race_config.bio_description = "SAME"
        panel.bio_text_box.get_text.return_value = "SAME"

        ctrl = MagicMock()
        ctrl.bio_status = FieldStatus.DONE
        ctrl.socio_status = FieldStatus.IDLE
        ctrl.bio_elapsed_seconds = 0.0
        ctrl.socio_elapsed_seconds = 0.0
        panel._controller = ctrl

        panel.set_state(ctrl)

        panel.bio_text_box.set_text.assert_not_called()


# =============================================================================
# Issue #6: per-frame elapsed-timer tick + textbox-sizing constant
# =============================================================================


class TestUpdateTicksElapsedTimer:
    """Issue #6: panel.update(time_delta) re-renders the elapsed-seconds
    label while a field is RUNNING. PROJ-299 wired set_state() only as the
    controller's on_change callback, which fires on state transitions; the
    label was never repainted while RUNNING. update() is the per-frame pump."""

    def _make_panel_with_widgets(self, lbl_initial_text: str = ""):
        """Helper: factory-built panel + a UILabel-like status mock whose
        `text` attribute mirrors what `set_text(...)` was last called with.
        Required so the idempotence guard can compare correctly."""
        panel = _bypass_init_panel()

        def _make_label(initial: str):
            lbl = MagicMock()
            lbl.text = initial

            def _set_text(new):
                lbl.text = new
            lbl.set_text.side_effect = _set_text
            return lbl

        panel.lbl_bio_status = _make_label(lbl_initial_text)
        panel.lbl_socio_status = _make_label(lbl_initial_text)
        panel.bio_text_box = MagicMock()
        panel.socio_text_box = MagicMock()
        panel._controller = None
        return panel

    def test_update_ticks_status_label_while_running(self):
        """Calling panel.update(dt) while bio is RUNNING re-renders
        lbl_bio_status with the current int(elapsed) seconds."""
        from game.strategy.services.race_description_llm_controller import FieldStatus

        panel = self._make_panel_with_widgets(lbl_initial_text="Generating Bio… 0s")
        ctrl = MagicMock()
        ctrl.bio_status = FieldStatus.RUNNING
        ctrl.socio_status = FieldStatus.IDLE
        ctrl.bio_elapsed_seconds = 5.0
        ctrl.socio_elapsed_seconds = 0.0
        panel._controller = ctrl

        panel.update(1 / 60)

        panel.lbl_bio_status.set_text.assert_called()
        text = panel.lbl_bio_status.set_text.call_args[0][0]
        assert "5s" in text
        assert "Generat" in text

    def test_update_does_not_overwrite_label_when_not_running(self):
        """When status is IDLE / DONE / ERROR / CANCELLED, update()
        must NOT touch lbl_*_status — that would stomp the label that
        _apply_field_state set on the last transition (e.g., the error
        message or the empty-on-DONE label)."""
        from game.strategy.services.race_description_llm_controller import FieldStatus

        for status in (
            FieldStatus.IDLE,
            FieldStatus.DONE,
            FieldStatus.ERROR,
            FieldStatus.CANCELLED,
        ):
            panel = self._make_panel_with_widgets(
                lbl_initial_text="<previously-set label>"
            )
            ctrl = MagicMock()
            ctrl.bio_status = status
            ctrl.socio_status = status
            ctrl.bio_elapsed_seconds = 7.0
            ctrl.socio_elapsed_seconds = 7.0
            panel._controller = ctrl

            panel.update(1 / 60)

            panel.lbl_bio_status.set_text.assert_not_called(), (
                f"set_text was called for non-RUNNING status {status}"
            )
            panel.lbl_socio_status.set_text.assert_not_called(), (
                f"set_text was called for non-RUNNING status {status}"
            )

    def test_update_skips_set_text_when_string_unchanged(self):
        """Idempotence guard: same int second across many frames must
        not generate a set_text storm. Mirrors the text_box guard in
        _apply_field_state."""
        from game.strategy.services.race_description_llm_controller import FieldStatus

        panel = self._make_panel_with_widgets()
        ctrl = MagicMock()
        ctrl.bio_status = FieldStatus.RUNNING
        ctrl.socio_status = FieldStatus.IDLE
        ctrl.bio_elapsed_seconds = 4.2
        ctrl.socio_elapsed_seconds = 0.0
        panel._controller = ctrl

        panel.update(1 / 60)
        first_call_count = panel.lbl_bio_status.set_text.call_count
        # Five more frames within the same int-second.
        for _ in range(5):
            panel.update(1 / 60)

        assert panel.lbl_bio_status.set_text.call_count == first_call_count

    def test_update_handles_controller_None(self):
        """No-LLM-provider path: attach_controller() never ran, so
        self._controller is None. update() must short-circuit, not raise."""
        panel = self._make_panel_with_widgets()
        panel._controller = None

        panel.update(1 / 60)  # MUST NOT raise


class TestHeaderOverheadConstantSizing:
    """Issue #6: HEADER_OVERHEAD class constant replaces magic 100 in
    text_area_height = (panel_height - HEADER_OVERHEAD) // 2. Ensures
    the new value gives at least as much vertical room as the old one."""

    def test_header_overhead_constant_exists_and_is_no_more_than_old_value(self):
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        assert hasattr(RaceDescriptionPanel, "HEADER_OVERHEAD"), (
            "HEADER_OVERHEAD must be exposed as a class constant so "
            "_create_content and attach_controller stay in sync."
        )
        # The original magic constant was 100. The fix loosens it so the
        # textboxes get more vertical space. Loosening means HEADER_OVERHEAD
        # <= 100 → text_area_height >= old value.
        assert RaceDescriptionPanel.HEADER_OVERHEAD <= 100

    def test_text_area_height_grew_relative_to_old_formula(self):
        """At the production panel size (~1020 px), the new formula must
        yield text_area_height STRICTLY greater than the old (panel_height
        - 100) // 2 — otherwise the cramped-textbox bug isn't fixed."""
        from game.ui.panels.race_description_panel import RaceDescriptionPanel

        panel_height = 1020  # production interior height
        old_formula = (panel_height - 100) // 2
        new_formula = (panel_height - RaceDescriptionPanel.HEADER_OVERHEAD) // 2
        assert new_formula > old_formula, (
            f"new {new_formula} must be > old {old_formula} for the fix to help"
        )
