"""Test-only UI builders for ``FoodAllocationEditor`` (PROJ-329A Phase 2
Task 2.1).

These pair with the production ``FoodAllocationEditorUiBuilder`` at
``game/ui/screens/food_allocation_editor.py``. Both provide a
``build(screen) -> None`` method matching the production builder
protocol (``tests/fixtures/ui_builder_protocol.py:UiBuilder``).

* ``NullFoodAllocationEditorUiBuilder`` is a no-op builder. Use it when
  a test only exercises Stage-1 cheap state (gathered rows, planet,
  callbacks) and does not touch widget refs.

* ``MockFoodAllocationEditorUiBuilder`` populates ``screen._row_widgets``
  with one ``(slider, entry, preview)`` MagicMock triple per gathered
  row, plus ``screen.btn_apply`` / ``screen.btn_cancel`` MagicMocks.
  Use it for tests that exercise ``collect_allocations``,
  ``_on_apply``, or button-press handling without a live pygame
  display.

Per the consensus refactor plan and PROJ-325 PoC finding 2, the bypass
branch invokes an explicitly supplied ``ui_builder`` so these mocks are
useful without per-call wiring.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from game.ui.screens.food_allocation_editor import FoodAllocationEditor


class NullFoodAllocationEditorUiBuilder:
    """No-op builder. Leaves ``screen._row_widgets`` empty and does not
    populate ``btn_apply`` / ``btn_cancel``."""

    def build(self, screen: "FoodAllocationEditor") -> None:
        return None


class MockFoodAllocationEditorUiBuilder:
    """Builder that populates ``screen._row_widgets`` with MagicMock
    triples — one per row in ``screen._rows`` — plus ``btn_apply`` /
    ``btn_cancel`` MagicMocks.

    The mock slider's ``get_current_value`` returns the row's
    ``current_allocation`` so ``collect_allocations`` returns sensible
    values out of the box. Tests that need different values can
    overwrite the row widget entries directly.
    """

    def build(self, screen: "FoodAllocationEditor") -> None:
        # Defensive: fail loud if Stage-1 wiring didn't run.
        for required in ("_rows", "_row_widgets"):
            if not hasattr(screen, required):
                raise AssertionError(
                    f"MockFoodAllocationEditorUiBuilder.build: screen has "
                    f"no `{required}` attribute. Build the screen via "
                    f"bypass_init AFTER Stage-1 cheap-state construction "
                    f"has run."
                )

        for row in screen._rows:
            slider = MagicMock(name=f"slider_{row.race_id}")
            slider.get_current_value.return_value = row.current_allocation
            slider.has_moved_recently = False
            entry = MagicMock(name=f"entry_{row.race_id}")
            entry.get_text.return_value = f"{row.current_allocation:.2f}"
            preview = MagicMock(name=f"preview_{row.race_id}")
            screen._row_widgets[row.race_id] = (slider, entry, preview)

        screen.btn_apply = MagicMock(name="btn_apply")
        screen.btn_cancel = MagicMock(name="btn_cancel")


__all__ = [
    "NullFoodAllocationEditorUiBuilder",
    "MockFoodAllocationEditorUiBuilder",
]
