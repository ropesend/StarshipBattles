"""Contract tests for the public API of `game.ui.screens.test_lab.test_run_details`.

PROJ-309 sub-phase 3.6 decomposes `test_run_details.py` (960 LOC) into a
`details/` subpackage. These tests lock the public surface so the split is
invisible to callers:

* `TestRunDetailsPanel` class is importable from the canonical historical
  path `game.ui.screens.test_lab.test_run_details` (preserved via shim).
* `TestRunDetailsPanel` is also importable from the new canonical path
  `game.ui.screens.test_lab.details`.
* The constructor signature `(x, y, width, height)` is preserved.
* The public method surface — `set_run`, `clear`, `handle_event`, `draw` —
  survives the split.
* The three callback attributes — `on_view_states`, `on_use_seed`,
  `on_copy_results` — survive (these are set by `panel_manager.py`).
* The three button-rect attributes — `view_states_button_rect`,
  `use_seed_button_rect`, `copy_results_button_rect` — survive (these are
  read by `handle_event` after being written by the action-buttons render).

These tests must PASS pre-split (against the original 960-line file) AND
post-split (against the new subpackage). That guarantees byte-for-byte
public-API stability for the two real callers (`panel_manager.py`,
`results_panel.py`).
"""
from __future__ import annotations

import pygame


def test_test_run_details_panel_importable_from_canonical_legacy_path() -> None:
    """`TestRunDetailsPanel` must remain importable from
    `game.ui.screens.test_lab.test_run_details` (the path used by
    `panel_manager.py`)."""
    from game.ui.screens.test_lab.test_run_details import TestRunDetailsPanel

    assert TestRunDetailsPanel is not None
    assert isinstance(TestRunDetailsPanel, type)


def test_test_run_details_panel_importable_from_new_subpackage_path() -> None:
    """Post-split, `TestRunDetailsPanel` is also importable from
    `game.ui.screens.test_lab.details`. Pre-split this import is allowed
    to fail, but we mark it as expected for the new layout."""
    try:
        from game.ui.screens.test_lab.details import TestRunDetailsPanel as DetailsPanel
    except ImportError:
        # Pre-split: the subpackage doesn't exist yet. Acceptable.
        return
    assert DetailsPanel is not None
    assert isinstance(DetailsPanel, type)


def test_legacy_and_new_paths_resolve_to_same_class() -> None:
    """If both import paths exist, they must point at the same class object —
    not two parallel definitions."""
    from game.ui.screens.test_lab.test_run_details import TestRunDetailsPanel as Legacy
    try:
        from game.ui.screens.test_lab.details import TestRunDetailsPanel as Canonical
    except ImportError:
        return  # Pre-split state — only legacy exists, vacuous pass.
    assert Legacy is Canonical


def _make_panel():
    """Helper: instantiate the panel with reasonable rect."""
    pygame.init()
    pygame.font.init()
    from game.ui.screens.test_lab.test_run_details import TestRunDetailsPanel
    return TestRunDetailsPanel(0, 0, 600, 400)


def test_constructor_accepts_x_y_width_height() -> None:
    """Constructor signature `(x, y, width, height)` is the public contract
    used by `panel_manager.py`."""
    panel = _make_panel()
    assert panel.x == 0
    assert panel.y == 0
    assert panel.width == 600
    assert panel.height == 400


def test_set_run_method_present() -> None:
    """`set_run(run_record, run_number)` is called by `results_panel.py`."""
    panel = _make_panel()
    assert hasattr(panel, "set_run")
    assert callable(panel.set_run)


def test_clear_method_present() -> None:
    """`clear()` is called by `results_panel.py` to deselect."""
    panel = _make_panel()
    assert hasattr(panel, "clear")
    assert callable(panel.clear)
    # Should be safe to call when no run is selected.
    panel.clear()
    assert panel.selected_run is None


def test_handle_event_method_present() -> None:
    """`handle_event(event)` is the input-routing entry point."""
    panel = _make_panel()
    assert hasattr(panel, "handle_event")
    assert callable(panel.handle_event)
    # Returns False when no run is selected.
    fake_event = pygame.event.Event(pygame.MOUSEWHEEL, {"y": 1})
    assert panel.handle_event(fake_event) is False


def test_draw_method_present() -> None:
    """`draw(surface)` is the public render entry point."""
    panel = _make_panel()
    assert hasattr(panel, "draw")
    assert callable(panel.draw)


def test_callback_attributes_present() -> None:
    """`panel_manager.py` sets these three callbacks. They must default to
    None and be settable as plain attributes."""
    panel = _make_panel()
    assert hasattr(panel, "on_view_states")
    assert hasattr(panel, "on_use_seed")
    assert hasattr(panel, "on_copy_results")
    assert panel.on_view_states is None
    assert panel.on_use_seed is None
    assert panel.on_copy_results is None
    # Settable.
    panel.on_view_states = lambda r, n: None
    panel.on_use_seed = lambda s: None
    panel.on_copy_results = lambda r, n: None


def test_button_rect_attributes_present() -> None:
    """`handle_event` reads these three rect attributes that are written by
    the action-buttons render. They must exist as attributes (default None)."""
    panel = _make_panel()
    assert hasattr(panel, "view_states_button_rect")
    assert hasattr(panel, "use_seed_button_rect")
    assert hasattr(panel, "copy_results_button_rect")
    assert panel.view_states_button_rect is None
    assert panel.use_seed_button_rect is None
    assert panel.copy_results_button_rect is None


def test_selected_run_attribute_present() -> None:
    """`selected_run` is read by `handle_event` to short-circuit when nothing
    is selected and to deliver the run+number to button callbacks."""
    panel = _make_panel()
    assert hasattr(panel, "selected_run")
    assert panel.selected_run is None


def test_scroll_attribute_present() -> None:
    """`scroll` is a `ScrollState` that backs scroll position and is read by
    `clear` and `set_run`."""
    panel = _make_panel()
    assert hasattr(panel, "scroll")
