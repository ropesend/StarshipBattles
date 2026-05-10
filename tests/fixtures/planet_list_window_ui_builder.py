"""Test-only UI builders for ``PlanetListWindow`` (PROJ-329C Phase 3).

These pair with the production ``PlanetListUiBuilder`` at
``game/ui/screens/planet_list_window.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol (``tests/fixtures/ui_builder_protocol.py:UiBuilder``).

* ``NullPlanetListWindowUiBuilder`` is a no-op builder.

* ``MockPlanetListWindowUiBuilder`` populates the widget slots that
  ``refresh_list`` / ``update`` / ``process_event`` reach for: sidebar
  references, ``main_panel``, ``column_manager``, ``data_source``,
  ``selection``, ``virtual_table``, ``btn_navigate``, plus the
  ``ui_filters`` shape so range-text-entry / chip iterations don't
  KeyError.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.planet_list_window import PlanetListWindow


class NullPlanetListWindowUiBuilder:
    """No-op builder. Leaves widget slots in the empty Stage-1 state."""

    def build(self, screen: "PlanetListWindow") -> None:
        return None


class MockPlanetListWindowUiBuilder:
    """Builder that populates the widget slots with MagicMocks.

    The defaults match the production widget surface closely enough for
    ``refresh_list`` to be patched out in tests, and for ``update`` /
    ``process_event`` iterations not to KeyError when iterating the
    ``ui_filters`` shape.
    """

    def build(self, screen: "PlanetListWindow") -> None:
        for required in (
            "columns",
            "all_planets",
            "preset_manager",
            "_filter_mgr",
            "_planet_ranges",
            "_effect_keys",
            "ui_filters",
        ):
            if not hasattr(screen, required):
                raise AssertionError(
                    f"MockPlanetListWindowUiBuilder.build: screen has "
                    f"no `{required}` attribute. Build the screen via "
                    f"bypass_init AFTER Stage-1 cheap-state construction "
                    f"has run."
                )

        # Sidebar widget references
        screen.sidebar_panel = MagicMock(name="sidebar_panel")
        screen.sidebar_scroller = MagicMock(name="sidebar_scroller")
        screen.txt_name_filter = MagicMock(name="txt_name_filter")
        screen.txt_name_filter.get_text.return_value = ""
        screen.btn_all_types = MagicMock(name="btn_all_types")
        screen.btn_none_types = MagicMock(name="btn_none_types")
        screen.btn_all_owners = MagicMock(name="btn_all_owners")
        screen.btn_none_owners = MagicMock(name="btn_none_owners")
        screen.btn_all_effects = MagicMock(name="btn_all_effects")
        screen.btn_none_effects = MagicMock(name="btn_none_effects")
        screen.btn_apply = MagicMock(name="btn_apply")
        screen.btn_save_preset = MagicMock(name="btn_save_preset")
        screen.txt_preset_name = MagicMock(name="txt_preset_name")
        screen.dd_presets = MagicMock(name="dd_presets")
        screen.dd_presets.selected_option = "Default"

        # ui_filters: provide the range subdicts refresh_list() reaches
        # for plus the empty section dicts process_event iterates over.
        for axis in ("gravity", "temp", "mass"):
            min_slider = MagicMock(name=f"slider_{axis}_min")
            min_slider.get_current_value.return_value = 0.0
            max_slider = MagicMock(name=f"slider_{axis}_max")
            max_slider.get_current_value.return_value = 0.0
            screen.ui_filters[axis] = {
                'min': min_slider,
                'max': max_slider,
                'min_txt': MagicMock(name=f"txt_{axis}_min"),
                'max_txt': MagicMock(name=f"txt_{axis}_max"),
                'limits': (0.0, 1.0),
            }
        screen.ui_filters.setdefault('types', {})
        screen.ui_filters.setdefault('owners', {})
        screen.ui_filters.setdefault('effects', {})
        screen.ui_filters.setdefault('columns', {})

        # Main content area
        screen.main_panel = MagicMock(name="main_panel")
        screen.column_manager = MagicMock(name="column_manager")
        screen.column_manager.sort_column_id = 'owner'
        screen.column_manager.sort_descending = False
        screen.data_source = MagicMock(name="data_source")
        screen.selection = MagicMock(name="selection")
        screen.virtual_table = MagicMock(name="virtual_table")
        screen.virtual_table.scroll_bar = MagicMock(name="scroll_bar")
        screen.virtual_table.scroll_bar.check_has_moved_recently.return_value = False
        screen.btn_navigate = MagicMock(name="btn_navigate")


__all__ = [
    "NullPlanetListWindowUiBuilder",
    "MockPlanetListWindowUiBuilder",
]
