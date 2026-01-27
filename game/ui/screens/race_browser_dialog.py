"""
Race Browser Dialog - In-game dialog for browsing and selecting saved races.

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.

Shows a scrollable list of races with small previews:
- Portrait (60px)
- Flag (60px, all 3 shapes)
- Ship (60px, top-down view)
- Race name
"""
import pygame
import pygame_gui
from typing import Callable, Optional, TYPE_CHECKING

from game.core.logger import log_debug
from game.ui.assets import ShipThemeManager
from game.ui.screens.race_asset_loader import RaceAssetLoader

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig
    from game.strategy.systems.race_library import RaceLibrary


class RaceBrowserDialog(pygame_gui.elements.UIWindow):
    """
    In-game dialog for browsing and selecting saved races.

    Shows a scrollable list of races with small previews:
    - Portrait (60px)
    - Flag (60px, all 3 shapes)
    - Ship (60px, top-down view)
    - Race name
    """

    # Preview sizes
    PREVIEW_SIZE = 60
    ROW_HEIGHT = 80

    def __init__(self, rect: pygame.Rect, manager: pygame_gui.UIManager,
                 race_library: 'RaceLibrary',
                 on_select_callback: Callable[['RaceConfig'], None],
                 on_cancel_callback: Callable[[], None]):
        """
        Create race browser dialog.

        Args:
            rect: Window rectangle
            manager: pygame_gui UIManager
            race_library: RaceLibrary instance for loading races
            on_select_callback: Callback(RaceConfig) when user selects a race
            on_cancel_callback: Callback() when user cancels
        """
        super().__init__(
            rect,
            manager,
            window_display_title="Load Race",
            object_id="#race_browser_dialog",
            resizable=False
        )

        self.race_library = race_library
        self.on_select_callback = on_select_callback
        self.on_cancel_callback = on_cancel_callback

        # PROJ-12 Phase 4: Use shared asset loader
        self._asset_loader = RaceAssetLoader()

        # Track UI elements for cleanup
        self.race_rows = []  # List of dicts with row UI elements
        self.selected_race = None
        self.selected_row_index = -1

        self._create_ui()
        self._load_races()

    def _create_ui(self):
        """Create the dialog UI elements."""
        container = self.get_container()
        content_width = container.get_size()[0] - 20
        content_height = container.get_size()[1]

        # Scrolling container for race list
        scroll_height = content_height - 80  # Leave room for buttons
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(10, 10, content_width, scroll_height),
            manager=self.ui_manager,
            container=container
        )

        # Bottom buttons
        btn_width = 120
        btn_height = 40
        btn_y = content_height - 55

        self.btn_cancel = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, btn_y, btn_width, btn_height),
            text="Cancel",
            manager=self.ui_manager,
            container=container
        )

        self.btn_load = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(content_width - btn_width, btn_y, btn_width, btn_height),
            text="Load",
            manager=self.ui_manager,
            container=container
        )
        self.btn_load.disable()  # Disabled until a race is selected

        # "No races" label (hidden by default)
        self.no_races_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, scroll_height // 2, content_width, 30),
            text="No saved races found. Create one first!",
            manager=self.ui_manager,
            container=container
        )
        self.no_races_label.hide()

    def _load_races(self):
        """Load all races and populate the list."""
        races = self.race_library.get_all_races()

        if not races:
            self.no_races_label.show()
            return

        # Initialize ShipThemeManager for ship previews
        theme_manager = ShipThemeManager.instance()
        theme_manager.initialize()

        # Set scrollable area size
        scroll_rect = self.scroll_container.get_relative_rect()
        total_height = len(races) * self.ROW_HEIGHT + 10
        self.scroll_container.set_scrollable_area_dimensions(
            (scroll_rect.width - 20, max(total_height, scroll_rect.height))
        )

        y = 5
        for i, race in enumerate(races):
            row = self._create_race_row(race, y, i, theme_manager)
            self.race_rows.append(row)
            y += self.ROW_HEIGHT

    def _create_race_row(self, race: 'RaceConfig', y: int, index: int,
                         theme_manager: ShipThemeManager) -> dict:
        """Create a single race row with previews."""
        scroll_rect = self.scroll_container.get_relative_rect()
        row_width = scroll_rect.width - 40

        row = {
            'race': race,
            'index': index,
            'elements': []
        }

        x = 5

        # Row button (clickable background)
        row_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(x, y, row_width, self.ROW_HEIGHT - 5),
            text="",
            manager=self.ui_manager,
            container=self.scroll_container,
            object_id=f"#race_row_{index}"
        )
        row['button'] = row_btn
        row['elements'].append(row_btn)

        # Portrait preview
        x += 10
        portrait_surf = self._load_portrait_preview(race.portrait_id)
        if portrait_surf:
            portrait_img = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(x, y + 10, self.PREVIEW_SIZE, self.PREVIEW_SIZE),
                image_surface=portrait_surf,
                manager=self.ui_manager,
                container=self.scroll_container
            )
            row['elements'].append(portrait_img)
        x += self.PREVIEW_SIZE + 10

        # Flag preview (single shape, not all 3)
        flag_surf = self._load_flag_preview(race.flag_id)
        if flag_surf:
            flag_img = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(x, y + 10, self.PREVIEW_SIZE, self.PREVIEW_SIZE),
                image_surface=flag_surf,
                manager=self.ui_manager,
                container=self.scroll_container
            )
            row['elements'].append(flag_img)
        x += self.PREVIEW_SIZE + 10

        # Ship preview (top-down view)
        if race.theme_id:
            ship_surf = theme_manager.get_image(race.theme_id, "Cruiser")
            if ship_surf:
                # Scale to preview size
                w, h = ship_surf.get_size()
                scale = min(self.PREVIEW_SIZE / w, self.PREVIEW_SIZE / h)
                new_size = (int(w * scale), int(h * scale))
                scaled_ship = pygame.transform.smoothscale(ship_surf, new_size)

                ship_img = pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect(x, y + 10, self.PREVIEW_SIZE, self.PREVIEW_SIZE),
                    image_surface=scaled_ship,
                    manager=self.ui_manager,
                    container=self.scroll_container
                )
                row['elements'].append(ship_img)
        x += self.PREVIEW_SIZE + 15

        # Race name label
        name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(x, y + 25, row_width - x - 10, 30),
            text=race.name or "[Unnamed Race]",
            manager=self.ui_manager,
            container=self.scroll_container
        )
        row['elements'].append(name_label)
        row['name_label'] = name_label

        return row

    def _load_portrait_preview(self, portrait_id: Optional[str]) -> Optional[pygame.Surface]:
        """Load and scale a portrait for preview.

        PROJ-12 Phase 4: Delegates to RaceAssetLoader.
        """
        return self._asset_loader.load_portrait_preview(portrait_id, self.PREVIEW_SIZE)

    def _load_flag_preview(self, flag_id: Optional[str]) -> Optional[pygame.Surface]:
        """Load and scale a flag for preview (rectangle shape only).

        PROJ-12 Phase 4: Delegates to RaceAssetLoader.
        """
        return self._asset_loader.load_flag_preview(flag_id, self.PREVIEW_SIZE)

    def _select_row(self, index: int):
        """Select a race row."""
        # Deselect previous
        if self.selected_row_index >= 0 and self.selected_row_index < len(self.race_rows):
            old_row = self.race_rows[self.selected_row_index]
            old_row['button'].unselect()

        # Select new
        self.selected_row_index = index
        if index >= 0 and index < len(self.race_rows):
            row = self.race_rows[index]
            row['button'].select()
            self.selected_race = row['race']
            self.btn_load.enable()
        else:
            self.selected_race = None
            self.btn_load.disable()

    def process_event(self, event: pygame.event.Event) -> bool:
        """Handle UI events."""
        consumed = super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_cancel:
                self.on_cancel_callback()
                self.kill()
                return True

            elif event.ui_element == self.btn_load:
                if self.selected_race:
                    self.on_select_callback(self.selected_race)
                    self.kill()
                return True

            # Check if a race row was clicked
            for i, row in enumerate(self.race_rows):
                if event.ui_element == row['button']:
                    self._select_row(i)
                    return True

        # Double-click to load
        if event.type == pygame_gui.UI_BUTTON_DOUBLE_CLICKED:
            for i, row in enumerate(self.race_rows):
                if event.ui_element == row['button']:
                    self._select_row(i)
                    if self.selected_race:
                        self.on_select_callback(self.selected_race)
                        self.kill()
                    return True

        return consumed
