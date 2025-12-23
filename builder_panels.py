import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UISelectionList, UIButton, UITextEntryLine, UIDropDownMenu, UITextBox, UIScrollingContainer, UIImage
from builder_components import ModifierEditorPanel
from ship import SHIP_CLASSES, VEHICLE_CLASSES
from ai import COMBAT_STRATEGIES
import logging

class ComponentListItem:
    def __init__(self, component, manager, container, y_pos, width, sprite_mgr):
        self.component = component
        self.height = 40
        self.rect = pygame.Rect(0, y_pos, width, self.height)
        
        # Container panel for the item
        self.panel = UIPanel(
            relative_rect=self.rect,
            manager=manager,
            container=container,
            object_id='#component_item_panel',
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        
        # Button for interaction (covers the whole item)
        self.button = UIButton(
            relative_rect=pygame.Rect(0, 0, width, self.height),
            text="",
            manager=manager,
            container=self.panel,
            # object_id='#component_item_bg', # Optional: custom theming
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )
        
        # Icon
        icon_size = 32
        sprite = sprite_mgr.get_sprite(component.sprite_index)
        if sprite:
            scaled = pygame.transform.scale(sprite, (icon_size, icon_size))
            UIImage(
                relative_rect=pygame.Rect(5, (self.height - icon_size)//2, icon_size, icon_size),
                image_surface=scaled,
                manager=manager,
                container=self.panel
            )

        # Label
        UILabel(
            relative_rect=pygame.Rect(45, 0, width-50, self.height),
            text=f"{component.name} ({component.mass}t)",
            manager=manager,
            container=self.panel,
            anchors={'left': 'left', 'right': 'right', 'centerY': 'center'}
        )

    def set_selected(self, selected):
        if selected:
            self.button.select()
        else:
            self.button.unselect()
            
    def kill(self):
        self.panel.kill()

class BuilderLeftPanel:
    def __init__(self, builder, manager, rect):
        self.builder = builder
        self.manager = manager
        self.rect = rect
        self.items = []
        self.selected_item = None
        
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#left_panel'
        )
        
        # Title
        UILabel(
            relative_rect=pygame.Rect(10, 5, 100, 30),
            text="Components",
            manager=manager,
            container=self.panel
        )
        
        # Sort Dropdown
        self.sort_options = ["Mass (Low-High)", "Mass (High-Low)", "Name (A-Z)", "Type"]
        self.current_sort = "Mass (Low-High)"
        self.sort_dropdown = UIDropDownMenu(
            options_list=self.sort_options,
            starting_option=self.current_sort,
            relative_rect=pygame.Rect(rect.width - 160, 5, 150, 30),
            manager=manager,
            container=self.panel
        )
        
        # Scroll Container
        self.list_y = 40
        container_height = (rect.height // 2) - 45
        self.scroll_container = UIScrollingContainer(
            relative_rect=pygame.Rect(5, self.list_y, rect.width - 10, container_height),
            manager=manager,
            container=self.panel,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        )
        
        # Modifier Panel
        self.modifier_panel = ModifierEditorPanel(
            manager=manager,
            container=self.panel,
            width=rect.width,
            preset_manager=builder.preset_manager,
            on_change_callback=self._on_modifier_change
        )
        
    def update_component_list(self):
        """Filter, sort, and populate the component list."""
        # Clear existing
        for item in self.items:
            item.kill()
        self.items = []
        
        # Filter
        v_type = getattr(self.builder.ship, 'vehicle_type', "Ship")
        filtered = [c for c in self.builder.available_components if v_type in c.allowed_vehicle_types]
        
        # Sort
        if self.current_sort == "Mass (Low-High)":
            filtered.sort(key=lambda c: c.mass)
        elif self.current_sort == "Mass (High-Low)":
            filtered.sort(key=lambda c: c.mass, reverse=True)
        elif self.current_sort == "Name (A-Z)":
            filtered.sort(key=lambda c: c.name)
        elif self.current_sort == "Type":
            filtered.sort(key=lambda c: (c.type_str, c.name))
            
        # Create Items
        item_width = self.scroll_container.get_container().get_rect().width
        y = 0
        for comp in filtered:
            item = ComponentListItem(
                component=comp,
                manager=self.manager,
                container=self.scroll_container,
                y_pos=y,
                width=item_width,
                sprite_mgr=self.builder.sprite_mgr
            )
            self.items.append(item)
            y += item.height
            
        # Update Scroll Area
        self.scroll_container.set_scrollable_area_dimensions((item_width, y))
        
    def draw(self, screen):
        # Icons are now drawn by UIImage widgets inside slots
        pass

    def _on_modifier_change(self):
        if self.builder.selected_component:
            self.builder.selected_component[2].recalculate_stats()
        self.builder.ship.recalculate_stats()
        self.builder.right_panel.update_stats_display(self.builder.ship)

    def rebuild_modifier_ui(self):
        editing_component = self.builder.selected_component[2] if self.builder.selected_component else None
        half_page_y = self.rect.height // 2
        self.modifier_panel.rebuild(editing_component, self.builder.template_modifiers)
        self.modifier_panel.layout(half_page_y)

    def handle_event(self, event):
        # Handle Sort Dropdown
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == self.sort_dropdown:
            self.current_sort = event.text
            self.update_component_list()
            return None
            
        # Handle Item Clicks
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for item in self.items:
                if event.ui_element == item.button:
                    # Deselect others
                    for i in self.items: i.set_selected(False)
                    item.set_selected(True)
                    self.selected_item = item
                    return ('select_component_type', item.component)

        # Modifier Panel
        action = self.modifier_panel.handle_event(event)
        return action
        
    def get_hovered_component(self, mx, my):
        # Check if mouse is over any item button
        # Using pygame_gui check_hover logic might be tricky since button is internal
        # But we can check if button.rect contains mouse
        
        # Simple check: iterate visible items?
        # ComponentListItem is wrapper, self.button is the UI element
        for item in self.items:
            # We must use the absolute rect of the button
            # But button.rect is relative to container? No, pygame_gui element.rect is usually absolute screen rect 
            # OR relative depends on container. 
            # In pygame_gui 0.6.x, .rect is usually absolute screen position for interaction.
            # Let's trust button.rect.collidepoint
            if item.button.rect.collidepoint(mx, my):
                return item.component
        return None

class BuilderRightPanel:
    def __init__(self, builder, manager, rect):
        self.builder = builder
        self.manager = manager
        self.rect = rect
        
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#right_panel'
        )
        
        self.setup_controls()
        self.setup_stats()
        
    def setup_controls(self):
        y = 10
        width = self.rect.width
        col_w = width - 20
        
        # Name
        UILabel(pygame.Rect(10, y, 60, 25), "Name:", manager=self.manager, container=self.panel)
        self.name_entry = UITextEntryLine(pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        self.name_entry.set_text(self.builder.ship.name)
        y += 40
        
        # Theme
        UILabel(pygame.Rect(10, y, 60, 25), "Theme:", manager=self.manager, container=self.panel)
        theme_options = self.builder.theme_manager.get_available_themes()
        curr_theme = getattr(self.builder.ship, 'theme_id', 'Federation')
        if theme_options and curr_theme not in theme_options: curr_theme = theme_options[0]
        
        self.theme_dropdown = UIDropDownMenu(theme_options, curr_theme, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        y += 40
        
        # Vehicle Type
        UILabel(pygame.Rect(10, y, 60, 25), "Type:", manager=self.manager, container=self.panel)
        # Get unique types
        types = sorted(list(set(c.get('type', 'Ship') for c in VEHICLE_CLASSES.values())))
        if not types: types = ["Ship"]
        
        curr_type = getattr(self.builder.ship, 'vehicle_type', "Ship")
        if curr_type not in types: curr_type = types[0]
        
        self.vehicle_type_dropdown = UIDropDownMenu(types, curr_type, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        y += 40

        # Class
        UILabel(pygame.Rect(10, y, 60, 25), "Class:", manager=self.manager, container=self.panel)
        # Filter classes by current type
        class_options = [name for name, cls in VEHICLE_CLASSES.items() if cls.get('type', 'Ship') == curr_type]
        class_options.sort()
        if not class_options: class_options = ["Escort"]

        curr_class = self.builder.ship.ship_class
        if curr_class not in class_options: curr_class = class_options[0]
        
        self.class_dropdown = UIDropDownMenu(class_options, curr_class, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        y += 40
        
        # AI
        UILabel(pygame.Rect(10, y, 60, 25), "AI:", manager=self.manager, container=self.panel)
        ai_options = [strat.get('name', sid.replace('_', ' ').title()) for sid, strat in COMBAT_STRATEGIES.items()]
        
        ai_display = self.builder.ship.ai_strategy.replace('_', ' ').title()
        for sid, strat in COMBAT_STRATEGIES.items():
            if sid == self.builder.ship.ai_strategy:
                ai_display = strat.get('name', ai_display)
                break
                
        self.ai_dropdown = UIDropDownMenu(ai_options, ai_display, pygame.Rect(70, y, 195, 30), manager=self.manager, container=self.panel)
        
        self.last_y = y + 50

    def setup_stats(self):
        y = self.last_y
        
        # Stats Header
        UILabel(pygame.Rect(10, y, 150, 25), "── Ship Stats ──", manager=self.manager, container=self.panel)
        y += 30
        
        self.stat_labels = {}
        stat_names = ['mass', 'max_hp', 'max_shields', 'shield_regen', 'shield_cost', 'max_speed', 
                      'turn_rate', 'acceleration', 'thrust', 'energy_gen', 'max_fuel', 'max_ammo', 'max_energy', 'targeting']

        
        for stat in stat_names:
            self.stat_labels[stat] = UILabel(pygame.Rect(10, y, 350, 20), f"{stat}: --", manager=self.manager, container=self.panel)
            y += 20
        y += 5
        
        # Layer Usage
        UILabel(pygame.Rect(10, y, 150, 20), "── Layer Usage ──", manager=self.manager, container=self.panel)
        y += 22
        self.layer_labels = {}
        for l in ['CORE', 'INNER', 'OUTER', 'ARMOR']:
            self.layer_labels[l] = UILabel(pygame.Rect(10, y, 350, 22), f"{l}: --%", manager=self.manager, container=self.panel)
            y += 22
        y += 10
        
         # Crew
        UILabel(pygame.Rect(10, y, 150, 20), "── Crew ──", manager=self.manager, container=self.panel)
        y += 22
        self.crew_labels = {}
        for c in ['crew_required', 'crew_housed', 'life_support']:
            self.crew_labels[c] = UILabel(pygame.Rect(10, y, 350, 22), f"{c}: --", manager=self.manager, container=self.panel)
            y += 22
        y += 10

        # Requirements
        UILabel(pygame.Rect(10, y, 150, 20), "── Requirements ──", manager=self.manager, container=self.panel)
        y += 22
        
        rem_h = self.rect.height - y - 10
        self.requirements_text_box = UITextBox("✓ All requirements met", pygame.Rect(10, y, self.rect.width - 25, rem_h), manager=self.manager, container=self.panel)

    def update_stats_display(self, s):
        """Update ship stats labels."""
        # Mass with color indicator
        mass_status = "✓" if s.mass_limits_ok else "✗"
        self.stat_labels['mass'].set_text(f"Mass: {s.mass:.0f} / {s.max_mass_budget} {mass_status}")
        
        self.stat_labels['max_hp'].set_text(f"Max HP: {s.max_hp:.0f}")
        self.stat_labels['max_shields'].set_text(f"Shields: {s.max_shields:.0f}")
        self.stat_labels['shield_regen'].set_text(f"Shield Regen: {s.shield_regen_rate:.1f}/s")
        self.stat_labels['shield_cost'].set_text(f"Regen Cost: {s.shield_regen_cost:.1f} E/t")
        
        self.stat_labels['max_speed'].set_text(f"Max Speed: {s.max_speed:.0f}")
        self.stat_labels['turn_rate'].set_text(f"Turn Rate: {s.turn_speed:.0f} deg/s")
        self.stat_labels['acceleration'].set_text(f"Acceleration: {s.acceleration_rate:.2f}")
        self.stat_labels['thrust'].set_text(f"Total Thrust: {s.total_thrust:.0f}")
        self.stat_labels['energy_gen'].set_text(f"Energy Gen: {s.energy_gen_rate:.1f}/s")
        self.stat_labels['max_fuel'].set_text(f"Max Fuel: {s.max_fuel:.0f}")
        self.stat_labels['max_ammo'].set_text(f"Max Ammo: {s.max_ammo:.0f}")
        self.stat_labels['max_energy'].set_text(f"Max Energy: {s.max_energy:.0f}")
        
        # Targeting
        t_count = getattr(s, 'max_targets', 1)
        t_text = "Single" if t_count == 1 else f"Multi ({t_count})"
        self.stat_labels['targeting'].set_text(f"Targeting: {t_text}")
        

        
        # Update layer stats
        from ship import LayerType
        layer_name_map = {
            LayerType.CORE: 'CORE',
            LayerType.INNER: 'INNER', 
            LayerType.OUTER: 'OUTER',
            LayerType.ARMOR: 'ARMOR'
        }
        
        for layer_type, layer_name in layer_name_map.items():
            status = s.layer_status.get(layer_type, {})
            ratio = status.get('ratio', 0) * 100
            limit = status.get('limit', 1.0) * 100
            is_ok = status.get('ok', True)
            mass = status.get('mass', 0)
            
            status_icon = "✓" if is_ok else "✗ OVER"
            self.layer_labels[layer_name].set_text(
                f"{layer_name}: {ratio:.0f}% / {limit:.0f}% ({mass:.0f}t) {status_icon}"
            )
        
        # Update crew stats
        crew_capacity = max(0, s.get_ability_total('CrewCapacity'))
        crew_required = s.get_ability_total('CrewRequired')
        
        # Legacy fallback
        legacy_req = abs(min(0, s.get_ability_total('CrewCapacity')))
        crew_required += legacy_req
        
        crew_housed = crew_capacity
        
        crew_ok = crew_capacity >= crew_required
        crew_status = "✓" if crew_ok else f"✗ Missing {crew_required - crew_capacity}"
        self.crew_labels['crew_required'].set_text(f"Crew Required: {crew_required}")
        self.crew_labels['crew_housed'].set_text(f"Crew On Board: {crew_housed} {crew_status}")
        
        life_support = s.get_ability_total('LifeSupportCapacity')
        ls_ok = life_support >= crew_required
        ls_status = "✓" if ls_ok else f"✗ -{crew_required - life_support}"
        self.crew_labels['life_support'].set_text(f"Life Support: {life_support} {ls_status}")
        
        # Update requirements
        missing_reqs = s.get_missing_requirements()
        if not s.mass_limits_ok:
            missing_reqs.append("⚠ Over mass limit")
        
        if not missing_reqs:
            html = "<font color='#88ff88'>✓ All requirements met</font>"
        else:
            html = "<br>".join([f"<font color='#ffaa55'>{req}</font>" for req in missing_reqs])
        
        self.requirements_text_box.html_text = html
        self.requirements_text_box.rebuild()
