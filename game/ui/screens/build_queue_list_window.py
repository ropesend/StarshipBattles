"""Build Queue List Window - Shows all active build queues for an empire (BUG-67)."""
import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UILabel


class BuildQueueListWindow(UIWindow):
    """Window listing all active build queues across planets and fleets."""

    ROW_HEIGHT = 30

    def __init__(self, rect, manager, empire, on_close_callback=None):
        super().__init__(rect, manager, window_display_title="Build Queues", resizable=False)
        self.empire = empire
        self.on_close_callback = on_close_callback
        self.row_labels = []
        self._build_list()

    def _build_list(self):
        """Build the list of all active build queues."""
        container = self.get_container()
        content_width = container.get_size()[0] - 20
        y = 10

        # Clear old labels
        for lbl in self.row_labels:
            lbl.kill()
        self.row_labels = []

        # Header row
        header = UILabel(
            relative_rect=pygame.Rect(10, y, content_width, self.ROW_HEIGHT),
            text="Location                    Item                 Turns Left",
            manager=self.ui_manager,
            container=container
        )
        self.row_labels.append(header)
        y += self.ROW_HEIGHT + 5

        has_items = False

        # Collect from colonies
        for planet in self.empire.colonies:
            for item in planet.construction_queue:
                has_items = True
                design_id = item.get('design_id', '?')
                turns = item.get('turns_remaining', '?')
                item_type = item.get('type', 'ship')
                text = f"{planet.name:<28s} {design_id:<20s} {turns} turns ({item_type})"
                lbl = UILabel(
                    relative_rect=pygame.Rect(10, y, content_width, self.ROW_HEIGHT),
                    text=text,
                    manager=self.ui_manager,
                    container=container
                )
                self.row_labels.append(lbl)
                y += self.ROW_HEIGHT

        # Collect from fleets with shipyards
        for fleet in self.empire.fleets:
            if not fleet.construction_queue:
                continue
            for item in fleet.construction_queue:
                has_items = True
                design_id = item.get('design_id', '?')
                turns = item.get('turns_remaining', '?')
                item_type = item.get('type', 'ship')
                text = f"{fleet.name:<28s} {design_id:<20s} {turns} turns ({item_type})"
                lbl = UILabel(
                    relative_rect=pygame.Rect(10, y, content_width, self.ROW_HEIGHT),
                    text=text,
                    manager=self.ui_manager,
                    container=container
                )
                self.row_labels.append(lbl)
                y += self.ROW_HEIGHT

        if not has_items:
            lbl = UILabel(
                relative_rect=pygame.Rect(10, y, content_width, self.ROW_HEIGHT),
                text="No active build queues.",
                manager=self.ui_manager,
                container=container
            )
            self.row_labels.append(lbl)

    def kill(self):
        for lbl in self.row_labels:
            lbl.kill()
        self.row_labels = []
        if self.on_close_callback:
            self.on_close_callback()
        super().kill()
