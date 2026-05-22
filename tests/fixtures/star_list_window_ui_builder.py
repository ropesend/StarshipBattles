"""Test-only UI builders for ``StarListWindow`` (PROJ-329B Phase 1).

These pair with the production ``StarListWindowUiBuilder`` at
``game/ui/screens/star_list_window.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol (``tests/fixtures/ui_builder_protocol.py:UiBuilder``).

* ``NullStarListWindowUiBuilder`` is a no-op builder.

* ``MockStarListWindowUiBuilder`` populates the widget slots
  (``sidebar_panel``, ``sidebar_scroller``, ``txt_name_filter``,
  ``btn_all_types``, ``btn_none_types``, ``btn_apply``,
  ``btn_save_preset``, ``txt_preset_name``, ``dd_presets``,
  ``ui_filters``, ``main_panel``, ``column_manager``, ``data_source``,
  ``selection``, ``virtual_table``, ``btn_navigate``) with MagicMocks.
  Does NOT call ``refresh_list`` (production builder triggers it as the
  final step).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.star_list_window import StarListWindow


class NullStarListWindowUiBuilder:
    """No-op builder. Leaves widget slots unset (other than the
    ``btn_navigate`` and ``ui_filters`` defaults set in Stage 1)."""

    def build(self, screen: "StarListWindow") -> None:
        return None


class MockStarListWindowUiBuilder:
    """Populates widget slots with MagicMocks for tests that exercise
    event handlers + filter delegation but do not need real pygame_gui
    widgets.
    """

    def build(self, screen: "StarListWindow") -> None:
        for required in ("world", "all_stars", "columns", "preset_manager"):
            if not hasattr(screen, required):
                raise AssertionError(
                    f"MockStarListWindowUiBuilder.build: screen has "
                    f"no `{required}` attribute. Build the screen via "
                    f"bypass_init AFTER Stage-1 cheap-state construction "
                    f"has run."
                )

        screen.sidebar_panel = MagicMock(name="sidebar_panel")
        screen.sidebar_scroller = MagicMock(name="sidebar_scroller")

        screen.txt_name_filter = MagicMock(name="txt_name_filter")
        screen.txt_name_filter.get_text.return_value = ""

        screen.btn_all_types = MagicMock(name="btn_all_types")
        screen.btn_none_types = MagicMock(name="btn_none_types")
        screen.btn_apply = MagicMock(name="btn_apply")
        screen.btn_save_preset = MagicMock(name="btn_save_preset")
        screen.txt_preset_name = MagicMock(name="txt_preset_name")
        screen.dd_presets = MagicMock(name="dd_presets")
        screen.dd_presets.selected_option = None

        # ui_filters is a nested dict in production; provide a minimal
        # slider mock for each numeric range key so refresh_list can
        # call get_current_value without crashing if a test triggers it.
        def _slider_pair() -> dict:
            min_s = MagicMock(name="min_slider")
            min_s.get_current_value.return_value = 0.0
            max_s = MagicMock(name="max_slider")
            max_s.get_current_value.return_value = 1.0
            return {
                'min': min_s,
                'max': max_s,
                'min_txt': MagicMock(name="min_txt"),
                'max_txt': MagicMock(name="max_txt"),
                'limits': (0.0, 1.0),
            }

        screen.ui_filters = {
            'mass': _slider_pair(),
            'temperature': _slider_pair(),
            'luminosity': _slider_pair(),
            'age': _slider_pair(),
            'radius_hexes': _slider_pair(),
            'types': {},
            'columns': {},
        }

        screen.main_panel = MagicMock(name="main_panel")
        screen.column_manager = MagicMock(name="column_manager")
        screen.column_manager.sort_column_id = 'name'
        screen.column_manager.sort_descending = False
        screen.data_source = MagicMock(name="data_source")
        screen.selection = MagicMock(name="selection")
        screen.virtual_table = MagicMock(name="virtual_table")
        screen.btn_navigate = MagicMock(name="btn_navigate")


__all__ = [
    "NullStarListWindowUiBuilder",
    "MockStarListWindowUiBuilder",
]
