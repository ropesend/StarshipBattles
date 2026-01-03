import pygame
import pygame_gui
import os
from pygame_gui.elements import UIPanel, UILabel, UIImage, UIButton, UIWindow, UITextBox
from components import LayerType  # Phase 7: Removed unused legacy class imports
import json
from ui.builder.modifier_logic import ModifierLogic

class ComponentDetailPanel:
    def __init__(self, manager, rect, image_base_path, event_bus=None):
        self.manager = manager
        self.rect = rect
        self.image_base_path = image_base_path
        
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#detail_panel'
        )
        
        if event_bus:
            event_bus.subscribe("SELECTION_CHANGED", self.on_selection_changed)
        
        self.current_component = None
        self.last_html = ""
        self.last_img_comp = None
        self.portrait_cache = {}
        
        # Image Element
        # Width is rect.width - 20 padding
        # Aspect ratio 1:1 for portrait
        img_size = rect.width - 20
        self.image_rect = pygame.Rect(10, 10, img_size, img_size)
        self.image_element = None
        
        # Button Area
        button_height = 40
        button_y = rect.height - button_height - 10
        self.details_btn = UIButton(
            relative_rect=pygame.Rect(10, button_y, rect.width - 20, button_height),
            text='Component Details',
            manager=manager,
            container=self.panel
        )
        self.details_btn.hide()

        # Stats Text Box
        self.start_y = self.image_rect.bottom + 10
        stats_height = button_y - self.start_y - 10
        
        from pygame_gui.elements import UITextBox
        self.stats_text_box = UITextBox(
            html_text="",
            relative_rect=pygame.Rect(10, self.start_y, rect.width - 20, stats_height),
            manager=manager,
            container=self.panel
        )
        
        # Placeholder text when nothing is selected
        self.placeholder_label = UILabel(
            pygame.Rect(10, rect.height // 2 - 10, rect.width - 20, 20),
            "Hover or Select Component",
            manager=manager,
            container=self.panel
        )

    def on_selection_changed(self, selection_data):
         # selection_data matches what BuilderSceneGUI emits: self.selected_component
         # which is a tuple (layer, idx, comp) or None using the new system
         
         if selection_data and isinstance(selection_data, tuple):
             self.show_component(selection_data[2])
         elif hasattr(selection_data, 'id'): # Direct component
             self.show_component(selection_data)
         else:
             self.show_component(None)
        
        
    def show_component(self, comp):
        if not comp:
            self.current_component = None
            self.last_img_comp = None
            self.last_html = ""
            self._clear_display()
            self.placeholder_label.show()
            self.stats_text_box.hide()
            self.details_btn.hide()
            return
            
        self.placeholder_label.hide()
        self.stats_text_box.show()
        self.details_btn.show()
        
        # 1. Update Image (only if changed)
        if comp != self.last_img_comp:
            self._update_image(comp)
            self.last_img_comp = comp
            
        self.current_component = comp
        
        # 2. Update Stats
        lines = []
        
        def add_line(text, color='#FFFFFF'):
            # Proper HTML formatting
            if color != '#FFFFFF':
                lines.append(f"<font color='{color}'>{text}</font>")
            else:
                lines.append(text)
            
        # Header
        add_line(f"<b>{comp.name}</b>", '#FFFF64')
        add_line(f"{comp.type_str}", '#C8C8C8')
        add_line(f"Mass: {comp.mass:.1f}t", '#C8C8C8')
        add_line(f"HP: {comp.max_hp:.0f}", '#C8C8C8')
        lines.append("<br>") # Spacer
        
        # --- Dynamic Ability Stats (The Refactor) ---
        # Instead of manually checking attributes, we ask the component.
        # This covers: Weapons, Engines, Shields, Resources, Hangars
        
        if hasattr(comp, 'get_ui_rows'):
            for row in comp.get_ui_rows():
                label = row.get('label', 'Unknown')
                val = row.get('value', '')
                color = row.get('color_hint', '#C8C8C8')
                add_line(f"{label}: {val}", color)

        # Abilities (Unregistered / Custom Data / Fallback)
        if comp.abilities:
            from abilities import ABILITY_REGISTRY
            
            shown_header = False
            
            for k, v in comp.abilities.items():
                # Skip fully registered Ability Classes (handled by get_ui_rows)
                if k in ABILITY_REGISTRY:
                    continue
                # Skip legacy shims (if they still exist in data)
                if k in ["ProjectileWeapon", "BeamWeapon", "Armor"]:
                    continue
                    
                if not shown_header:
                    lines.append("<br>Abilities:")
                    shown_header = True

                add_line(f"• {k}: {v}", '#C8C8C8')
                    
        # Modifiers
        if comp.modifiers:
            lines.append("<br>Modifiers:")
            for m in comp.modifiers:
                is_mandatory = ModifierLogic.is_modifier_mandatory(m.definition.id, comp)
                
                name_str = m.definition.name
                color = '#96FF96' # Green for optional
                
                if is_mandatory:
                    name_str = f"{name_str} [A]" # Auto
                    color = '#FFD700' # Gold
                    
                add_line(f"• {name_str}: {m.value:.2f}", color)
        
        full_html = "<br>".join(lines)
        if full_html != self.last_html:
            self.stats_text_box.html_text = full_html
            self.stats_text_box.rebuild()
            self.last_html = full_html

    def show_details_popup(self):
        if not self.current_component:
            return

        json_str = json.dumps(self.current_component.data, indent=4)
        # Simple HTML formatting for text box
        html_str = json_str.replace("\n", "<br>").replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
        
        win_size = (500, 600)
        start_pos = (
            (self.rect.width - win_size[0]) // 2 + self.rect.x,
            (self.rect.height - win_size[1]) // 2 + self.rect.y
        )
        # Center on screen or panel? Let's center on screen if possible, but we only have Manager.
        # Use simple centering logic or fixed pos.
        
        window = UIWindow(
            rect=pygame.Rect((100, 100), win_size),
            manager=self.manager,
            window_display_title=f"Details: {self.current_component.name}",
            resizable=True
        )
        
        text_box = UITextBox(
            html_text=f"<font face='consolas, monospace' size=4 color='#E0E0E0'>{html_str}</font>",
            relative_rect=pygame.Rect(10, 10, win_size[0]-20, win_size[1]-50),
            manager=self.manager,
            container=window,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

    def _clear_display(self):
        self.stats_text_box.html_text = ""
        self.stats_text_box.rebuild()
        if self.image_element:
            self.image_element.kill()
            self.image_element = None
            
    def _update_image(self, comp):
        # Only reload if changed
        if self.image_element:
            self.image_element.kill()
            self.image_element = None
            
        index = comp.sprite_index
        file_index = index + 1
        filename = f"2048Portrait_Comp_{file_index:03d}.jpg"
        
        full_path = os.path.join(self.image_base_path, "Components 2048", filename)
        
        surf = None
        if os.path.exists(full_path):
             if full_path in self.portrait_cache:
                 surf = self.portrait_cache[full_path]
             else:
                 try:
                    loaded = pygame.image.load(full_path).convert()
                    surf = pygame.transform.scale(loaded, (self.image_rect.width, self.image_rect.height))
                    self.portrait_cache[full_path] = surf
                 except Exception as e:
                     print(f"Failed to load portrait {full_path}: {e}")
        
        if surf:
            self.image_element = UIImage(
                relative_rect=self.image_rect,
                image_surface=surf,
                manager=self.manager,
                container=self.panel
            )
        else:
            # Placeholder
            empty = pygame.Surface((self.image_rect.width, self.image_rect.height))
            empty.fill((50, 50, 60))
            font = pygame.font.SysFont("Arial", 14)
            text = font.render(f"No Image\n{filename}", True, (200, 200, 200))
            empty.blit(text, (10, 10))
            
            self.image_element = UIImage(
                relative_rect=self.image_rect,
                image_surface=empty,
                manager=self.manager,
                container=self.panel
            )

    def set_position(self, pos):
        self.panel.set_position(pos)
        self.rect.topleft = pos

