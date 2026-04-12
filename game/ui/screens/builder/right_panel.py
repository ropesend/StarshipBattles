"""Right panel for the ship builder.

Displays ship statistics and configuration options.

PROJ-43: Now uses VehicleClassService instead of direct VEHICLE_CLASSES import.
PROJ-80: Stats display delegated to shared DesignStatsPanel.
"""
import logging
import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UITextEntryLine, UIDropDownMenu, UITextBox, UIImage
from pygame_gui.core import UIElement

from game.core.paths import Paths
from game.ui.panels.design_stats_panel import DesignStatsPanel
from game.ui.widgets.dropdown_helper import recreate_dropdown

logger = logging.getLogger(__name__)

_MOVEMENT_OPTIONS = [
    ("kite_max", "Hold Range"),
    ("kite_optimal", "Optimal Range"),
    ("brawl_close", "Advance"),
    ("kite_medium", "Pursue"),
    ("strafe_run", "Hit & Run"),
    ("hold_position", "Hold Position"),
    ("ramming_speed", "Ram"),
    ("flee_panic", "Evasive"),
]

_TARGETING_OPTIONS = [
    ("standard", "Standard"),
    ("sniper", "Sniper"),
    ("brawler", "Brawler"),
    ("anti_fighter", "Anti-Fighter"),
    ("self_defense", "Self Defense"),
]

class BuilderRightPanel:
    def __init__(self, builder, manager, rect, event_bus=None, viewmodel=None, vehicle_class_service=None, hide_theme_selector=False):
        self.builder = builder
        self.viewmodel = viewmodel or builder.viewmodel
        self.manager = manager
        self.hide_theme_selector = hide_theme_selector
        self.rect = rect
        self.event_bus = event_bus

        # PROJ-43/PROJ-50/PROJ-211: Inject vehicle class service (strict DI)
        # Vehicle class service is now required - no fallback
        self._vehicle_class_service = vehicle_class_service

        if event_bus:
            from game.ui.screens.builder_utils import BuilderEvents
            event_bus.subscribe(BuilderEvents.SHIP_UPDATED, self.on_ship_updated)
            event_bus.subscribe(BuilderEvents.REGISTRY_RELOADED, self.on_registry_reloaded)

        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#right_panel'
        )

        self.setup_controls()
        self.setup_stats()

    def on_registry_reloaded(self, data):
        """Handle registry reload event - refresh all controls with new data."""
        self.refresh_controls()

    def on_ship_updated(self, ship):
        """Handle ship update event - rebuild if needed, then update stats."""
        if self.stats_panel.needs_rebuild(ship):
            self.stats_panel.rebuild(ship)
            self._sync_from_stats_panel()
        # BUG-04 Fix: Always call update_stats_display to populate values
        # even after rebuild (which only creates empty rows with "--" placeholders)
        self.update_stats_display(ship)

    def setup_controls(self):
        y = 10
        width = self.rect.width
        col_w = width - 20
        
        # Name
        UILabel(pygame.Rect(10, y, 60, 25), "Name:", manager=self.manager, container=self.panel)
        self.name_entry = UITextEntryLine(pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        self.name_entry.set_text(self.builder.ship.name)
        y += 40
        
        # Theme (hidden in integrated/strategy mode where theme is locked to empire)
        self.theme_dropdown = None
        if not self.hide_theme_selector:
            UILabel(pygame.Rect(10, y, 60, 25), "Theme:", manager=self.manager, container=self.panel)
            theme_options = self.builder.theme_manager.get_available_themes()
            curr_theme = self.builder.ship.theme_id
            if theme_options and curr_theme not in theme_options: curr_theme = theme_options[0]

            self.theme_dropdown = UIDropDownMenu(theme_options, curr_theme, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
            y += 40
        
        # Vehicle Type (PROJ-43: via VehicleClassService)
        UILabel(pygame.Rect(10, y, 60, 25), "Type:", manager=self.manager, container=self.panel)
        types = self._vehicle_class_service.get_vehicle_types()
        if not types:
            types = ["Ship"]

        curr_type = self.builder.ship.vehicle_type
        if curr_type not in types:
            curr_type = types[0]

        self.vehicle_type_dropdown = UIDropDownMenu(types, curr_type, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        y += 40

        # Class (PROJ-43: via VehicleClassService)
        UILabel(pygame.Rect(10, y, 60, 25), "Class:", manager=self.manager, container=self.panel)
        class_options = self._vehicle_class_service.get_classes_for_type(curr_type)
        class_options.sort(key=lambda x: x[1])  # Sort by max_mass
        class_options = [name for name, _ in class_options]  # Extract just names
        if not class_options:
            class_options = ["Escort"]

        curr_class = self.builder.ship.ship_class
        if curr_class not in class_options:
            curr_class = class_options[0]

        self.class_dropdown = UIDropDownMenu(class_options, curr_class, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        y += 40
        
        # Movement Policy
        UILabel(pygame.Rect(10, y, 60, 25), "Move:", manager=self.manager, container=self.panel)
        move_options = [name for _, name in _MOVEMENT_OPTIONS]
        curr_move = self.builder.ship.movement_policy
        curr_move_display = next(
            (name for mid, name in _MOVEMENT_OPTIONS if mid == curr_move),
            move_options[0]
        )
        self.movement_dropdown = UIDropDownMenu(move_options, curr_move_display, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        y += 40

        # Targeting Policy
        UILabel(pygame.Rect(10, y, 60, 25), "Target:", manager=self.manager, container=self.panel)
        tgt_options = [name for _, name in _TARGETING_OPTIONS]
        curr_tgt = self.builder.ship.targeting_policy
        curr_tgt_display = next(
            (name for tid, name in _TARGETING_OPTIONS if tid == curr_tgt),
            tgt_options[0]
        )
        self.targeting_dropdown = UIDropDownMenu(tgt_options, curr_tgt_display, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        y += 40

        # Role
        UILabel(pygame.Rect(10, y, 60, 25), "Role:", manager=self.manager, container=self.panel)
        role_options, curr_role_display = self._get_role_dropdown_data(curr_type)
        self.role_dropdown = UIDropDownMenu(role_options, curr_role_display, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)

        # Portrait Image (Side by Side)
        self.portrait_image = None
        img_x = 280
        img_size = 200 # Approx match height of 5 rows (200px)
        self.portrait_rect = pygame.Rect(img_x, 10, img_size, img_size) # Fixed slot

        self.update_portrait_image()

        y += 40
        self.last_y = max(y, 10 + img_size) + 10

    def refresh_controls(self):
        """Update all UI controls to match the current ship state."""
        import pygame
        from pygame_gui.elements import UIDropDownMenu
        
        s = self.builder.ship
        
        # 1. Name
        self.name_entry.set_text(s.name)
        
        # Preservation of Rects
        # Dropdowns are killed and recreated below via recreate_dropdown

        # 2. Recreate Theme (if visible)
        if self.theme_dropdown:
            theme_options = self.builder.theme_manager.get_available_themes()
            curr_theme = s.theme_id
            self.theme_dropdown = recreate_dropdown(
                self.theme_dropdown, theme_options, curr_theme, self.manager, container=self.panel
            )
        
        # 3. Recreate Type (PROJ-43: via VehicleClassService)
        types = self._vehicle_class_service.get_vehicle_types()
        if not types:
            types = ["Ship"]

        curr_type = s.vehicle_type
        # Ensure consistency from class if vehicle_type not set or mismatched
        class_def = self._vehicle_class_service.get_class_definition(s.ship_class)
        if class_def:
            curr_type = class_def.get('type', curr_type)

        if curr_type not in types:
            curr_type = types[0]

        self.vehicle_type_dropdown = recreate_dropdown(
            self.vehicle_type_dropdown, types, curr_type, self.manager, container=self.panel
        )

        # 4. Recreate Class (PROJ-43: via VehicleClassService)
        class_options = self._vehicle_class_service.get_classes_for_type(curr_type)
        class_options.sort(key=lambda x: x[1])  # Sort by max_mass
        class_options = [name for name, _ in class_options]  # Extract just names
        if not class_options:
            class_options = ["Escort"]

        curr_class = s.ship_class
        all_classes = self._vehicle_class_service.get_all_classes()
        if curr_class not in class_options:
            if curr_class in all_classes:
                curr_class = class_options[0]

        self.class_dropdown = recreate_dropdown(
            self.class_dropdown, class_options, curr_class, self.manager, container=self.panel
        )
        
        # 5. Recreate Movement Policy
        move_options = [name for _, name in _MOVEMENT_OPTIONS]
        curr_move = s.movement_policy
        curr_move_display = next(
            (name for mid, name in _MOVEMENT_OPTIONS if mid == curr_move),
            move_options[0]
        )
        self.movement_dropdown = recreate_dropdown(
            self.movement_dropdown, move_options, curr_move_display, self.manager, container=self.panel
        )

        # 5b. Recreate Targeting Policy
        tgt_options = [name for _, name in _TARGETING_OPTIONS]
        curr_tgt = s.targeting_policy
        curr_tgt_display = next(
            (name for tid, name in _TARGETING_OPTIONS if tid == curr_tgt),
            tgt_options[0]
        )
        self.targeting_dropdown = recreate_dropdown(
            self.targeting_dropdown, tgt_options, curr_tgt_display, self.manager, container=self.panel
        )

        # 6. Recreate Role
        role_options, curr_role_display = self._get_role_dropdown_data(curr_type)
        self.role_dropdown = recreate_dropdown(
            self.role_dropdown, role_options, curr_role_display, self.manager, container=self.panel
        )

        # 7. Update Portrait
        self.update_portrait_image()

        # 8. Rebuild Stats
        self.rebuild_stats()


    def update_portrait_image(self):
        """Update the ship portrait based on current theme and class."""
        import os
        import re
        
        # Determine paths
        theme = self.builder.ship.theme_id
        ship_class = self.builder.ship.ship_class
        
        match = re.match(r"(.*)\s+\((.*)\)", ship_class)
        if match:
             base = match.group(1).strip().replace(" ", "")
             sub = match.group(2).strip().replace(" ", "")
             class_clean = f"{sub}{base}"
        else:
             class_clean = ship_class.replace(" ", "")

        filename = f"{class_clean}_Portrait.jpg"
        
        # Load from assets/ShipThemes/{theme}/Portraits/
        full_path = os.path.join(Paths.SHIP_THEMES_DIR, theme, "Portraits", filename)

        if not os.path.exists(full_path):
            # Try with spaces in ship class name
            full_path_space = os.path.join(Paths.SHIP_THEMES_DIR, theme, "Portraits", f"{ship_class}_Portrait.jpg")
            if os.path.exists(full_path_space):
                full_path = full_path_space
            else:
                 # Fallback to Default Portrait
                 default_path = Paths.DEFAULT_SHIP_PORTRAIT
                 if os.path.exists(default_path):
                     full_path = default_path
                 else:
                     if self.portrait_image:
                         self.portrait_image.kill()
                         self.portrait_image = None
                     return

        try:
            image_surf = pygame.image.load(full_path).convert_alpha()
            
            # Scale to fit width, maintaining aspect
            max_w = self.portrait_rect.width
            max_h = self.portrait_rect.height
            
            img_w, img_h = image_surf.get_size()
            scale = min(max_w / img_w, max_h / img_h)
            
            if scale < 1.0:
                new_w = int(img_w * scale)
                new_h = int(img_h * scale)
                image_surf = pygame.transform.smoothscale(image_surf, (new_w, new_h))
            
            # Center it
            final_w, final_h = image_surf.get_size()
            center_x = self.portrait_rect.x + (max_w - final_w) // 2
            center_y = self.portrait_rect.y + (max_h - final_h) // 2
            
            # Update rect to centered position
            display_rect = pygame.Rect(center_x, center_y, final_w, final_h)
            
            if self.portrait_image:
                self.portrait_image.kill()
                
            self.portrait_image = UIImage(
                relative_rect=display_rect,
                image_surface=image_surf,
                manager=self.manager,
                container=self.panel
            )
            
        except (FileNotFoundError, OSError, pygame.error) as e:
            logger.warning(f"Failed to load portrait {full_path}: {e}")

    def setup_stats(self):
        """Set up the stats panel using shared DesignStatsPanel."""
        y = self.last_y
        total_h = self.rect.height - y - 10
        if total_h < 100:
            total_h = 100

        self.stats_panel = DesignStatsPanel(
            manager=self.manager,
            rect=pygame.Rect(0, y, self.rect.width, total_h),
            container=self.panel,
            ship=self.builder.ship,
            show_requirements=True
        )
        # Expose rows_map for tests and update methods
        self._sync_from_stats_panel()

    def _sync_from_stats_panel(self):
        """Sync rows_map from DesignStatsPanel for convenient access by tests."""
        self.rows_map = self.stats_panel.rows_map

    def rebuild_stats(self):
        """Completely rebuild the stats scroll container (e.g. after ship load)."""
        self.stats_panel.rebuild(self.builder.ship)
        self._sync_from_stats_panel()

    def update_class_dropdown(self, new_class: str, valid_classes: list):
        """Kill existing class dropdown and recreate with new options.

        Args:
            new_class: The class to set as selected
            valid_classes: List of valid class names for the dropdown
        """
        self.class_dropdown = recreate_dropdown(
            self.class_dropdown, valid_classes, new_class, self.manager, container=self.panel
        )

    def update_vehicle_type_dropdown(self, new_type: str, valid_types: list):
        """Kill existing vehicle type dropdown and recreate with new options.

        Args:
            new_type: The vehicle type to set as selected
            valid_types: List of valid vehicle types for the dropdown
        """
        self.vehicle_type_dropdown = recreate_dropdown(
            self.vehicle_type_dropdown, valid_types, new_type, self.manager, container=self.panel
        )

    def update_role_dropdown(self, vehicle_type: str):
        """Recreate role dropdown filtered for a new vehicle type.

        Args:
            vehicle_type: Current vehicle type to filter roles for.
        """
        role_options, curr_role_display = self._get_role_dropdown_data(vehicle_type)
        self.role_dropdown = recreate_dropdown(
            self.role_dropdown, role_options, curr_role_display, self.manager, container=self.panel
        )

    def _get_role_dropdown_data(self, vehicle_type: str):
        """Get role dropdown options and current selection for a vehicle type.

        Returns:
            Tuple of (options_list, current_display_name).
        """
        from game.strategy.data.design_role import get_default_design_role_registry

        registry = get_default_design_role_registry()
        roles = registry.get_roles_for_vehicle_type(vehicle_type)

        if not roles:
            return ["General Purpose"], "General Purpose"

        role_options = [r["name"] for r in roles]

        # Find display name for ship's current role
        curr_role_id = self.builder.ship.design_role
        curr_display = registry.get_role_name(curr_role_id)

        if curr_display not in role_options:
            curr_display = role_options[0]

        return role_options, curr_display

    def update_dropdowns_for_data_reload(self, default_class: str, vehicle_classes: dict):
        """Update dropdowns after a data reload with new vehicle class data.

        Args:
            default_class: The default ship class to select
            vehicle_classes: Dict of vehicle class definitions {name: {type, max_mass, ...}}
        """
        # Compute valid classes sorted by max_mass
        valid_classes = [(n, vehicle_classes[n].get('max_mass', 0)) for n in vehicle_classes]
        valid_classes.sort(key=lambda x: x[1])
        valid_class_names = [n for n, _ in valid_classes]
        if not valid_class_names:
            valid_class_names = ["Escort"]

        # Update class dropdown
        self.update_class_dropdown(default_class, valid_class_names)

        # Compute valid types
        types = sorted(set(c.get('type', 'Ship') for c in vehicle_classes.values()))
        if not types:
            types = ["Ship"]
        default_type = vehicle_classes.get(default_class, {}).get('type', 'Ship')

        # Update type dropdown
        self.update_vehicle_type_dropdown(default_type, types)

    def update_stats_display(self, s):
        """Update ship stats labels using shared DesignStatsPanel."""
        self.stats_panel.update_stats(s)
