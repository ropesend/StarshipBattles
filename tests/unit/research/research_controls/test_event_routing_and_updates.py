"""
Event-routing + state-update characterization tests for ResearchControlPanel.

PROJ-337 gap-fill: pins observed behavior for ~25 behaviors not covered by
test_reset_state.py. Reuses the existing `mock_pygame_gui` autouse fixture
that swaps `sys.modules['pygame_gui']` and reloads the module, plus the
`MagicMock(spec=ResearchControlPanel) + lambda` binding pattern to invoke
real methods on a mock instance without running `_create_ui`.

D-007 (decisions.md): pin observed behavior including any apparently-buggy
paths (e.g. `update_turn_log` truncation). File separate tickets for any
behavior that appears wrong.
"""
import pytest
from unittest.mock import MagicMock


# ---------- helpers ----------------------------------------------------------

def _make_panel(rc, mock_tracker, mock_tech_tree=None, *,
                bind_methods=None):
    """Build a MagicMock(spec=ResearchControlPanel) with bound real methods.

    `bind_methods` is a list of method names to bind to the real method via
    a lambda closure (so the real method runs on the mock instance).
    """
    panel = MagicMock(spec=rc.ResearchControlPanel)
    panel.tracker = mock_tracker
    panel.tech_tree = mock_tech_tree or MagicMock()
    panel._selected_node = None

    # Callbacks
    panel.on_next_turn = MagicMock()
    panel.on_close = MagicMock()
    panel.on_reset = MagicMock()
    panel.on_auto_spread_changed = MagicMock()

    # UI element mocks
    panel.btn_next_turn = MagicMock()
    panel.btn_close = MagicMock()
    panel.btn_reset = MagicMock()
    panel.btn_auto_spread = MagicMock()
    panel.slider_budget = MagicMock()
    panel.slider_allocation = MagicMock()
    panel.lbl_turn = MagicMock()
    panel.lbl_node_name = MagicMock()
    panel.lbl_node_level = MagicMock()
    panel.lbl_node_chance = MagicMock()
    panel.lbl_node_decay = MagicMock()
    panel.lbl_node_volatility = MagicMock()
    panel.lbl_node_price = MagicMock()
    panel.lbl_node_status = MagicMock()
    panel.lbl_allocated = MagicMock()
    panel.lbl_budget_value = MagicMock()
    panel.lbl_allocation_value = MagicMock()
    panel.log_box = MagicMock()
    panel.log_box.html_text = "<i>No events yet. Click 'Next Turn' to simulate.</i>"

    # Bind requested real methods so we can call them on the mock
    cls = rc.ResearchControlPanel
    bind_methods = bind_methods or []
    for name in bind_methods:
        method = getattr(cls, name)
        # Bind with closure capturing both method and panel
        panel.__dict__[name] = (
            lambda _m=method, _p=panel: lambda *a, **kw: _m(_p, *a, **kw)
        )()

    return panel


# ---------- Section A: handle_event button routing --------------------------

class TestHandleEventButtons:

    def test_btn_next_turn_invokes_callback_returns_true(
            self, mock_pygame_gui, mock_tracker, mock_tech_tree):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker, mock_tech_tree)

        event = MagicMock()
        event.type = rc.pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = panel.btn_next_turn

        result = rc.ResearchControlPanel.handle_event(
            panel, event, None, mock_tech_tree
        )

        assert result is True
        panel.on_next_turn.assert_called_once()

    def test_btn_close_invokes_callback_returns_true(
            self, mock_pygame_gui, mock_tracker, mock_tech_tree):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker, mock_tech_tree)

        event = MagicMock()
        event.type = rc.pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = panel.btn_close

        result = rc.ResearchControlPanel.handle_event(
            panel, event, None, mock_tech_tree
        )

        assert result is True
        panel.on_close.assert_called_once()

    def test_btn_reset_invokes_callback_returns_true(
            self, mock_pygame_gui, mock_tracker, mock_tech_tree):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker, mock_tech_tree)

        event = MagicMock()
        event.type = rc.pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = panel.btn_reset

        result = rc.ResearchControlPanel.handle_event(
            panel, event, None, mock_tech_tree
        )

        assert result is True
        panel.on_reset.assert_called_once()

    def test_btn_auto_spread_toggles_and_invokes_callback(
            self, mock_pygame_gui, mock_tracker, mock_tech_tree):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker, mock_tech_tree)

        event = MagicMock()
        event.type = rc.pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = panel.btn_auto_spread

        result = rc.ResearchControlPanel.handle_event(
            panel, event, None, mock_tech_tree
        )

        assert result is True
        panel._toggle_auto_spread.assert_called_once()

    def test_unhandled_event_returns_false(
            self, mock_pygame_gui, mock_tracker, mock_tech_tree):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker, mock_tech_tree)

        event = MagicMock()
        event.type = rc.pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = MagicMock()  # Unknown ui_element

        result = rc.ResearchControlPanel.handle_event(
            panel, event, None, mock_tech_tree
        )

        assert result is False


# ---------- Section B: handle_event slider routing --------------------------

class TestHandleEventSliders:

    def test_slider_budget_updates_tracker_label_and_allocation_range(
            self, mock_pygame_gui, mock_tracker, mock_tech_tree):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker, mock_tech_tree)
        panel.slider_budget.get_current_value.return_value = 250

        event = MagicMock()
        event.type = rc.pygame_gui.UI_HORIZONTAL_SLIDER_MOVED
        event.ui_element = panel.slider_budget

        result = rc.ResearchControlPanel.handle_event(
            panel, event, None, mock_tech_tree
        )

        assert result is True
        mock_tracker.set_rp_budget.assert_called_once_with(250)
        panel.update_budget_display.assert_called_once()
        panel._update_allocation_slider_range.assert_called_once()

    def test_slider_allocation_uses_actual_clamped_value_in_label(
            self, mock_pygame_gui, mock_tracker, mock_tech_tree):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker, mock_tech_tree)

        node = MagicMock()
        node.id = 'sel'
        panel._selected_node = node

        # Slider position 100 but tracker clamps to 75
        panel.slider_allocation.get_current_value.return_value = 100
        clamped_state = MagicMock(rp_allocation=75)
        mock_tracker.get_state.return_value = clamped_state

        event = MagicMock()
        event.type = rc.pygame_gui.UI_HORIZONTAL_SLIDER_MOVED
        event.ui_element = panel.slider_allocation

        result = rc.ResearchControlPanel.handle_event(
            panel, event, None, mock_tech_tree
        )

        assert result is True
        # Label should show actual clamped value (75), not slider value (100)
        panel.lbl_allocation_value.set_text.assert_called_once_with('75')


# ---------- Section C: update_selected_node ---------------------------------

class TestUpdateSelectedNode:

    def test_update_selected_node_populates_all_seven_labels(
            self, mock_pygame_gui, mock_tracker, mock_node):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        rc.ResearchControlPanel.update_selected_node(panel, mock_node, mock_tracker)

        panel.lbl_node_name.set_text.assert_called()
        panel.lbl_node_level.set_text.assert_called()
        panel.lbl_node_chance.set_text.assert_called()
        panel.lbl_node_decay.set_text.assert_called()
        panel.lbl_node_volatility.set_text.assert_called()
        panel.lbl_node_price.set_text.assert_called()
        panel.lbl_node_status.set_text.assert_called()

    def test_update_selected_node_price_label_shows_maxed_when_at_cap(
            self, mock_pygame_gui, mock_tracker, mock_node):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        # current_level == max_levels -> "maxed"
        mock_node.max_levels = 3
        state = MagicMock(current_level=3, current_chance=0.5, rp_allocation=0)
        mock_tracker.get_state.return_value = state

        rc.ResearchControlPanel.update_selected_node(panel, mock_node, mock_tracker)

        last_call = panel.lbl_node_price.set_text.call_args
        assert '(maxed)' in last_call[0][0]

    def test_update_selected_node_enables_allocation_slider_only_when_available(
            self, mock_pygame_gui, mock_tracker, mock_node):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        mock_node.get_status.return_value = 'completed'
        rc.ResearchControlPanel.update_selected_node(panel, mock_node, mock_tracker)
        panel.slider_allocation.disable.assert_called()
        panel.slider_allocation.enable.assert_not_called()

    def test_update_selected_node_sets_allocation_to_state_rp_allocation(
            self, mock_pygame_gui, mock_tracker, mock_node):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        mock_node.get_status.return_value = 'available'
        state = MagicMock(current_level=0, current_chance=0.5, rp_allocation=42)
        mock_tracker.get_state.return_value = state

        rc.ResearchControlPanel.update_selected_node(panel, mock_node, mock_tracker)

        panel.slider_allocation.set_current_value.assert_called_with(42)


# ---------- Section D: clear_selection --------------------------------------

class TestClearSelection:

    def test_clear_selection_resets_all_seven_labels_to_placeholder(
            self, mock_pygame_gui, mock_tracker):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        rc.ResearchControlPanel.clear_selection(panel)

        panel.lbl_node_name.set_text.assert_called_with("(None)")
        panel.lbl_node_level.set_text.assert_called_with("Level: -")
        panel.lbl_node_chance.set_text.assert_called_with("Chance: -")
        panel.lbl_node_decay.set_text.assert_called_with("Decay: -")
        panel.lbl_node_volatility.set_text.assert_called_with("Volatility: -")
        panel.lbl_node_price.set_text.assert_called_with("Price: -")
        panel.lbl_node_status.set_text.assert_called_with("Status: -")

    def test_clear_selection_disables_allocation_slider_resets_to_zero(
            self, mock_pygame_gui, mock_tracker):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        rc.ResearchControlPanel.clear_selection(panel)

        panel.slider_allocation.disable.assert_called_once()
        panel.slider_allocation.set_current_value.assert_called_once_with(0)
        panel.lbl_allocation_value.set_text.assert_called_with('-')


# ---------- Section E: budget + auto-spread ---------------------------------

class TestBudgetAndAutoSpread:

    def test_update_budget_display_writes_allocated_over_budget(
            self, mock_pygame_gui, mock_tracker):
        rc = mock_pygame_gui
        mock_tracker.get_total_allocated.return_value = 75
        mock_tracker.rp_budget = 200
        panel = _make_panel(rc, mock_tracker)

        rc.ResearchControlPanel.update_budget_display(panel)

        panel.lbl_allocated.set_text.assert_called_with("Allocated: 75 / 200")

    def test_toggle_auto_spread_on_calls_spread_rp_evenly(
            self, mock_pygame_gui, mock_tracker, mock_tech_tree):
        rc = mock_pygame_gui
        mock_tracker.auto_spread_enabled = False
        panel = _make_panel(rc, mock_tracker, mock_tech_tree)

        rc.ResearchControlPanel._toggle_auto_spread(panel)

        # auto_spread_enabled flipped to True
        assert mock_tracker.auto_spread_enabled is True
        mock_tracker.spread_rp_evenly.assert_called_once_with(mock_tech_tree)

    def test_toggle_auto_spread_off_does_not_call_spread_rp_evenly(
            self, mock_pygame_gui, mock_tracker, mock_tech_tree):
        rc = mock_pygame_gui
        mock_tracker.auto_spread_enabled = True
        panel = _make_panel(rc, mock_tracker, mock_tech_tree)

        rc.ResearchControlPanel._toggle_auto_spread(panel)

        assert mock_tracker.auto_spread_enabled is False
        mock_tracker.spread_rp_evenly.assert_not_called()

    def test_update_auto_spread_button_text_matches_state(
            self, mock_pygame_gui, mock_tracker):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        # ON case
        mock_tracker.auto_spread_enabled = True
        rc.ResearchControlPanel._update_auto_spread_button(panel)
        panel.btn_auto_spread.set_text.assert_called_with("Auto-Spread: ON")

        # OFF case
        mock_tracker.auto_spread_enabled = False
        rc.ResearchControlPanel._update_auto_spread_button(panel)
        panel.btn_auto_spread.set_text.assert_called_with("Auto-Spread: OFF")

    def test_update_allocation_slider_range_uses_max_one_floor(
            self, mock_pygame_gui, mock_tracker):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        node = MagicMock()
        node.id = 'sel'
        panel._selected_node = node

        # current_allocation + remaining == 0 -> floor to 1
        mock_tracker.get_state.return_value = MagicMock(rp_allocation=0)
        mock_tracker.get_remaining_rp.return_value = 0

        rc.ResearchControlPanel._update_allocation_slider_range(panel)

        # value_range upper bound is 1 (floor), not 0
        assert panel.slider_allocation.value_range == (0, 1)


# ---------- Section F: update_turn_log --------------------------------------

class TestUpdateTurnLog:

    def test_update_turn_log_no_events_writes_no_events_text(
            self, mock_pygame_gui, mock_tracker):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        rc.ResearchControlPanel.update_turn_log(panel, [], 3)

        # html_text was assigned
        assert 'No events.' in panel.log_box.html_text
        assert 'Turn 3' in panel.log_box.html_text

    def test_update_turn_log_breakthrough_renders_breakthrough_text(
            self, mock_pygame_gui, mock_tracker):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        events = [{
            'event': 'breakthrough',
            'node_id': 'n1',
            'details': {
                'name': 'Plasma',
                'new_level': 2,
                'max_level': 5,
                'chance': 0.4,
                'roll': 0.2,
            },
        }]

        rc.ResearchControlPanel.update_turn_log(panel, events, 1)

        assert 'BREAKTHROUGH' in panel.log_box.html_text
        # new_level appears
        assert 'Lv 2/5' in panel.log_box.html_text

    def test_update_turn_log_progress_renders_chance_roll_rp(
            self, mock_pygame_gui, mock_tracker):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        events = [{
            'event': 'progress',
            'node_id': 'n1',
            'details': {
                'name': 'Plasma',
                'chance': 0.35,
                'roll': 0.7,
                'rp_invested': 50,
            },
        }]

        rc.ResearchControlPanel.update_turn_log(panel, events, 1)

        html = panel.log_box.html_text
        assert '35.0%' in html or '35%' in html
        assert '70%' in html
        assert '50 RP' in html

    def test_update_turn_log_decay_renders_old_arrow_new_chance(
            self, mock_pygame_gui, mock_tracker):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        events = [{
            'event': 'decay',
            'node_id': 'n1',
            'details': {
                'name': 'Plasma',
                'old_chance': 0.30,
                'new_chance': 0.25,
            },
        }]

        rc.ResearchControlPanel.update_turn_log(panel, events, 1)

        html = panel.log_box.html_text
        assert '->' in html
        assert '30.0%' in html
        assert '25.0%' in html

    def test_update_turn_log_prepends_new_turn_to_existing_log(
            self, mock_pygame_gui, mock_tracker):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        # Pre-populate existing log entry (NOT placeholder)
        panel.log_box.html_text = "<b>Turn 1:</b> existing"

        rc.ResearchControlPanel.update_turn_log(panel, [], 2)

        html = panel.log_box.html_text
        # Turn 2 (new) should appear before Turn 1 (existing)
        assert html.index('Turn 2') < html.index('Turn 1')

    def test_update_turn_log_truncates_after_five_turns(
            self, mock_pygame_gui, mock_tracker):
        # CHARACTERIZE D-007: pin observed split-then-keep-first-5 behavior
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        # Pre-populate with 5 prior turns concatenated by "<br><br>"
        prior = "<br><br>".join(f"<b>Turn {i}:</b> ev" for i in range(5, 0, -1))
        panel.log_box.html_text = prior

        rc.ResearchControlPanel.update_turn_log(panel, [], 6)

        html = panel.log_box.html_text
        # The implementation does parts[:5] which keeps the first 5 splits.
        # New turn is prepended, so we should still see Turn 6 plus 4 prior.
        assert html.count('<b>Turn') == 5
        assert 'Turn 6' in html

    def test_update_turn_log_replaces_no_events_placeholder(
            self, mock_pygame_gui, mock_tracker):
        rc = mock_pygame_gui
        panel = _make_panel(rc, mock_tracker)

        # html_text default already has "No events yet" placeholder
        assert 'No events yet' in panel.log_box.html_text

        rc.ResearchControlPanel.update_turn_log(panel, [], 1)

        html = panel.log_box.html_text
        # Placeholder gone; only turn 1 line
        assert 'No events yet' not in html
        assert 'Turn 1' in html


# ---------- Section G: clear_log --------------------------------------------

class TestClearLog:

    def test_clear_log_resets_log_to_placeholder_text(
            self, mock_pygame_gui, mock_tracker):
        rc = mock_pygame_gui
        mock_tracker.turn_number = 5
        panel = _make_panel(rc, mock_tracker)
        panel.log_box.html_text = '<b>Turn 5:</b> some events'

        rc.ResearchControlPanel.clear_log(panel)

        assert "No events yet" in panel.log_box.html_text
        panel.log_box.rebuild.assert_called_once()
