import pygame
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIImage

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

        # Store tooltip data for custom rendering (not using pygame_gui's built-in)
        self.tooltip_text = self._generate_tooltip(component)
        
        # Button for interaction (covers the whole item) - NO tool_tip_text
        self.button = UIButton(
            relative_rect=pygame.Rect(0, 0, width, self.height),
            text="",
            manager=manager,
            container=self.panel,
            # tool_tip_text removed to allow custom tooltip handling
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
        # Use component type if no pretty name
        display_name = component.name
        UILabel(
            relative_rect=pygame.Rect(45, 0, width-50, self.height),
            text=f"{display_name} ({component.mass}t)",
            manager=manager,
            container=self.panel,
            anchors={'left': 'left', 'right': 'right', 'centerY': 'center'}
        )

    def _generate_tooltip(self, c):
        lines = []
        # Header: Name + Classification
        classification = c.data.get('major_classification', 'Unknown')
        lines.append(f"<b>{c.name}</b>")
        lines.append(f"<i>{classification}</i>")
        lines.append("----------------")
        lines.append(f"Type: {c.type_str}")
        lines.append(f"Mass: {c.mass}t  HP: {c.max_hp}")
        
        # Specific stats from data to be safe, or attributes if reliable
        if 'damage' in c.data: lines.append(f"Damage: {c.data['damage']}")
        if 'range' in c.data: lines.append(f"Range: {c.data['range']}")
        if 'energy_generation' in c.data: lines.append(f"Gen: {c.data['energy_generation']}/s")
        if 'capacity' in c.data: lines.append(f"Cap: {c.data['capacity']} {c.data.get('resource_type','')}")
        if 'thrust_force' in c.data: lines.append(f"Thrust: {c.data['thrust_force']}")
        if 'abilities' in c.data:
            for k, v in c.data['abilities'].items():
                if v is True: lines.append(f"Ab: {k}")
                elif isinstance(v, (int, float)): lines.append(f"{k}: {v}")
                
        return "<br>".join(lines)

    def set_selected(self, selected):
        if selected:
            self.button.select()
        else:
            self.button.unselect()
            
    def kill(self):
        self.panel.kill()
