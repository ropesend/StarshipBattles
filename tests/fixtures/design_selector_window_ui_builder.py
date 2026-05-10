"""Test-only UI builders for ``DesignSelectorWindow`` (PROJ-329B Phase 4).

Production builder lives at
``game.ui.screens.design_selector_window:DesignSelectorUiBuilder``.

* ``NullDesignSelectorWindowUiBuilder`` — no-op.

* ``MockDesignSelectorWindowUiBuilder`` — populates the sidebar widgets,
  list container, bottom buttons with MagicMocks. Does NOT call
  ``_refresh_designs`` (production builder triggers it as final step).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.design_selector_window import DesignSelectorWindow


class NullDesignSelectorWindowUiBuilder:
    """No-op builder."""

    def build(self, screen: "DesignSelectorWindow") -> None:
        return None


class MockDesignSelectorWindowUiBuilder:
    """Populate sidebar + list + button mocks."""

    def build(self, screen: "DesignSelectorWindow") -> None:
        if not hasattr(screen, "design_library"):
            raise AssertionError(
                "MockDesignSelectorWindowUiBuilder.build: screen has no "
                "`design_library` attribute. Build the screen via "
                "bypass_init AFTER Stage-1 cheap-state construction."
            )

        screen.sidebar_panel = MagicMock(name="sidebar_panel")

        screen.name_search_entry = MagicMock(name="name_search_entry")
        screen.name_search_entry.get_text.return_value = ""

        screen.class_dropdown = MagicMock(name="class_dropdown")
        screen.class_dropdown.selected_option = "All Classes"

        screen.type_dropdown = MagicMock(name="type_dropdown")
        screen.type_dropdown.selected_option = "All Types"

        # Mode-dependent widgets the production code creates: leave as
        # MagicMocks so handler tests don't crash.
        screen.role_dropdown = MagicMock(name="role_dropdown")
        screen.role_dropdown.selected_option = "All Roles"

        screen.obsolete_button = MagicMock(name="obsolete_button")
        screen.apply_filters_button = MagicMock(name="apply_filters_button")
        screen.select_button = MagicMock(name="select_button")
        screen.cancel_button = MagicMock(name="cancel_button")

        screen.list_container = MagicMock(name="list_container")
        screen.list_container.get_container.return_value = MagicMock(
            name="list_container_inner"
        )


__all__ = [
    "NullDesignSelectorWindowUiBuilder",
    "MockDesignSelectorWindowUiBuilder",
]
