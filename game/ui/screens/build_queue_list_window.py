"""Build Queue List Window - Shows all active build queues for an empire (BUG-67).

PROJ-313: Migrated to ``StrategyModalWindow`` base class.
PROJ-328 Phase A Task A.2: Two-stage construction pattern. Row collection
is pure-Python (``BuildQueueRowCollector``); widget construction lives
behind ``BuildQueueListUiBuilder`` so tests can swap in
``Null{...}UiBuilder`` / ``Mock{...}UiBuilder`` from
``tests/fixtures/build_queue_list_ui_builder.py``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, TYPE_CHECKING

import pygame
import pygame_gui
from pygame_gui.elements import UILabel

from game.core.input_actions import InputAction
from game.core.profiling import profile_action
from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.ui.services.input_mapper import InputMapper
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


@dataclass(frozen=True)
class BuildQueueRow:
    """Pure-data description of one row in the build-queue list.

    The ``text`` field is the pre-formatted display string. ``location``
    and ``design_id`` are kept for tests/debug; the renderer only uses
    ``text``.
    """

    location: str
    design_id: str
    turns_remaining: Any
    item_type: str
    text: str


class BuildQueueRowCollector:
    """Walks an empire's colonies + fleets and produces ``BuildQueueRow``
    instances for every active construction-queue item.

    Pure: no pygame_gui widgets, no display. Safe to construct + call in
    tests without ``bypass_init``.
    """

    @profile_action("Panel: BuildQueue.collect_rows")
    def collect(self, empire) -> List[BuildQueueRow]:
        rows: List[BuildQueueRow] = []
        for planet in empire.colonies:
            rows.extend(self._rows_from_owner(planet, planet.construction_queue))
        for fleet in empire.fleets:
            queue = getattr(fleet, "construction_queue", None)
            if not queue:
                continue
            rows.extend(self._rows_from_owner(fleet, queue))
        return rows

    def _rows_from_owner(self, owner, queue: Iterable[dict]) -> List[BuildQueueRow]:
        out: List[BuildQueueRow] = []
        for item in queue:
            design_id = item.get('design_id', '?')
            turns = item.get('turns_remaining', '?')
            item_type = item.get('type', 'ship')
            text = f"{owner.name:<28s} {design_id:<20s} {turns} turns ({item_type})"
            out.append(BuildQueueRow(
                location=owner.name,
                design_id=design_id,
                turns_remaining=turns,
                item_type=item_type,
                text=text,
            ))
        return out


class BuildQueueListUiBuilder:
    """Production widget builder. Reads the screen's collected rows and
    creates one ``UILabel`` per row (plus a header / empty-state label).

    The builder is invoked from ``BuildQueueListWindow.__init__`` after
    the shell is constructed, and from ``rebuild_list()`` when the
    queue contents change.
    """

    HEADER_TEXT = "Location                    Item                 Turns Left"
    EMPTY_TEXT = "No active build queues."

    @profile_action("Panel: BuildQueue.rebuild_ui_labels")
    def build(self, screen: "BuildQueueListWindow") -> None:
        container = screen.get_container()
        content_width = container.get_size()[0] - 20
        y = 10

        # Clear any previous labels.
        for lbl in screen.row_labels:
            lbl.kill()
        screen.row_labels = []

        # Header row.
        header = UILabel(
            relative_rect=pygame.Rect(10, y, content_width, screen.ROW_HEIGHT),
            text=self.HEADER_TEXT,
            manager=screen.ui_manager,
            container=container,
        )
        screen.row_labels.append(header)
        y += screen.ROW_HEIGHT + 5

        rows = screen._row_collector.collect(screen.empire)
        for row in rows:
            lbl = UILabel(
                relative_rect=pygame.Rect(10, y, content_width, screen.ROW_HEIGHT),
                text=row.text,
                manager=screen.ui_manager,
                container=container,
            )
            screen.row_labels.append(lbl)
            y += screen.ROW_HEIGHT

        if not rows:
            lbl = UILabel(
                relative_rect=pygame.Rect(10, y, content_width, screen.ROW_HEIGHT),
                text=self.EMPTY_TEXT,
                manager=screen.ui_manager,
                container=container,
            )
            screen.row_labels.append(lbl)


class BuildQueueListWindow(StrategyModalWindow):
    """Window listing all active build queues across planets and fleets.

    PROJ-313: Migrated to ``StrategyModalWindow`` base class.
    PROJ-328 Phase A Task A.2: Two-stage construction. ``__init__``
    runs cheap state + the row collector before the bypass point, then
    ``super().__init__`` opens the shell, then ``BuildQueueListUiBuilder``
    builds the labels. Tests pass a ``MockBuildQueueListUiBuilder`` so
    the bypass branch still populates ``row_labels`` etc.
    """

    ROW_HEIGHT = 30

    def __init__(
        self,
        rect,
        manager,
        empire,
        *,
        window_manager: "StrategyWindowManager | None",
        on_close_callback=None,
        input_mapper: Optional['InputMapper'] = None,
        ui_builder: Optional[BuildQueueListUiBuilder] = None,
        row_collector: Optional[BuildQueueRowCollector] = None,
    ):
        # ---- Stage 1: cheap state ----
        self.empire = empire
        self.on_close_callback = on_close_callback
        self._mapper = input_mapper
        self.row_labels: List = []
        self._row_collector = row_collector or BuildQueueRowCollector()

        # ---- Stage 2: shell ----
        super().__init__(
            rect, manager,
            window_display_title="Build Yards",
            resizable=False,
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        # Bypass branch (test): only invoke an *explicitly supplied*
        # ui_builder so MockBuildQueueListUiBuilder can populate widget
        # slots; production tests that don't supply one leave row_labels
        # at the placeholder. (PROJ-325 PoC finding 2.)
        if getattr(self, '_window_init_bypassed', False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or BuildQueueListUiBuilder()).build(self)

    def rebuild_list(self, ui_builder: Optional[BuildQueueListUiBuilder] = None) -> None:
        """Re-collect rows + rebuild labels. Used by callers that want to
        refresh the list after the empire's construction queues change.
        """
        (ui_builder or BuildQueueListUiBuilder()).build(self)

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """Dispatch keyboard events via InputMapper.

        Args:
            event: A pygame KEYDOWN event.

        Returns:
            True if the event was handled.
        """
        if not self._mapper:
            return False
        action = self._mapper.resolve(event, contexts=["build_queue"])
        if action == InputAction.BUILD_QUEUE_CLOSE:
            self.kill()
            return True
        return False

    def process_event(self, event) -> bool:
        """Handle pygame events, including hotkeys."""
        handled = super().process_event(event)
        if event.type == pygame.KEYDOWN:
            if self._handle_keydown(event):
                return True
        return handled

    def kill(self) -> None:
        for lbl in self.row_labels:
            lbl.kill()
        self.row_labels = []
        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
