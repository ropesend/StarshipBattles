"""Test-only UI builders for ``PlanetAbilitiesWindow`` (PROJ-329C Phase 1).

These pair with the production ``PlanetAbilitiesUiBuilder`` at
``game/ui/screens/planet_abilities_window.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol (``tests/fixtures/ui_builder_protocol.py:UiBuilder``).

* ``NullPlanetAbilitiesWindowUiBuilder`` is a no-op builder.

* ``MockPlanetAbilitiesWindowUiBuilder`` populates ``screen._widgets``
  / ``screen._editor_buttons`` / ``screen._toggle_buttons`` /
  ``screen._status_labels`` shape-compatibly so existing tests that
  reach the slot dicts continue to pass. By default the dicts are left
  empty (no ability rows); pass ``mock_rows=...`` to seed entries.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.planet_abilities_window import PlanetAbilitiesWindow


class NullPlanetAbilitiesWindowUiBuilder:
    """No-op builder. Leaves widget slots in the empty Stage-1 state."""

    def build(self, screen: "PlanetAbilitiesWindow") -> None:
        return None


class MockPlanetAbilitiesWindowUiBuilder:
    """Builder that populates the widget slot dicts with MagicMocks.

    By default produces no ability rows / no editor buttons (matches the
    "no abilities" production branch). Tests can subclass or pass
    ``mock_rows`` (a list of ``(facility_id, component_key, ability_name)``
    tuples) to seed the dicts.
    """

    def __init__(
        self,
        mock_rows: Optional[List[tuple]] = None,
        mock_editor_buttons: Optional[List[str]] = None,
    ) -> None:
        self.mock_rows = mock_rows or []
        self.mock_editor_buttons = mock_editor_buttons or []

    def build(self, screen: "PlanetAbilitiesWindow") -> None:
        for required in (
            "_toggle_buttons",
            "_editor_buttons",
            "_status_labels",
            "_widgets",
        ):
            if not hasattr(screen, required):
                raise AssertionError(
                    f"MockPlanetAbilitiesWindowUiBuilder.build: screen has "
                    f"no `{required}` attribute. Build the screen via "
                    f"bypass_init AFTER Stage-1 cheap-state construction "
                    f"has run."
                )

        for label in self.mock_editor_buttons:
            btn = MagicMock(name=f"editor_button[{label}]")
            btn._editor_type = label.lower()
            screen._editor_buttons.append(btn)
            screen._widgets.append(btn)

        for facility_id, component_key, ability_name in self.mock_rows:
            row_key = f"{facility_id}:{component_key}"

            name_lbl = MagicMock(name=f"name_lbl[{row_key}]")
            screen._widgets.append(name_lbl)

            status_lbl = MagicMock(name=f"status_lbl[{row_key}]")
            screen._widgets.append(status_lbl)
            screen._status_labels[row_key] = status_lbl

            btn = MagicMock(name=f"toggle_btn[{row_key}]")
            btn._ability_name = ability_name
            btn._facility_id = facility_id
            btn._component_key = component_key
            btn._is_active = False
            screen._widgets.append(btn)
            screen._toggle_buttons[row_key] = btn


__all__ = [
    "NullPlanetAbilitiesWindowUiBuilder",
    "MockPlanetAbilitiesWindowUiBuilder",
]
