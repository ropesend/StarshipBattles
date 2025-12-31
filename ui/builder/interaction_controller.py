import pygame
from profiling import profile_action

class InteractionController:
    def __init__(self, builder, view):
        self.builder = builder
        self.view = view
        self.dragged_item = None
        self.selected_component = None
        self.hovered_component = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Left Click
                # Ignore clicks if over detail panel (which sits inside/over the view)
                if self.builder.detail_panel.rect.collidepoint(event.pos):
                    return

                if self.view.rect.collidepoint(event.pos) and not self.dragged_item:
                    found = self.view.get_component_at(event.pos, self.builder.ship)
                    if found:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LALT] or keys[pygame.K_RALT]:
                            # Clone
                            original = found[2]
                            self.dragged_item = original.clone()
                            for m in original.modifiers:
                                new_m = m.definition.create_modifier(m.value)
                                self.dragged_item.modifiers.append(new_m)
                            self.dragged_item.recalculate_stats()
                        elif self.selected_component == found:
                            # Pick up
                            layer, index, comp = found
                            self.builder.ship.remove_component(layer, index)
                            self.dragged_item = comp
                            self.selected_component = None
                            self.builder.on_selection_changed(None)
                            self.builder.update_stats()
                        else:
                            # Select
                            self.selected_component = found
                            self.builder.on_selection_changed(found)
                    else:
                        # Deselect
                        self.selected_component = None
                        self.builder.on_selection_changed(None)
                        
        elif event.type == pygame.MOUSEBUTTONUP:
             if event.button == 1 and self.dragged_item:
                 keys = pygame.key.get_pressed()
                 shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                 
                 item_to_clone = self.dragged_item
                 self._handle_drop(event.pos)
                 
                 if shift_held:
                     self.dragged_item = item_to_clone.clone()
                     for m in item_to_clone.modifiers:
                        self.dragged_item.add_modifier(m.definition.id)
                        new_m = self.dragged_item.get_modifier(m.definition.id)
                        if new_m: new_m.value = m.value
                     self.dragged_item.recalculate_stats()
                 else:
                      self.dragged_item = None
                      self.builder.left_panel.deselect_all()  # Clear selection when no longer carrying

    def update(self):
        mx, my = pygame.mouse.get_pos()
        self.hovered_component = None
        if self.view.rect.collidepoint(mx, my):
             found = self.view.get_component_at((mx, my), self.builder.ship)
             if found:
                 self.hovered_component = found[2]

    @profile_action("Builder: Drop Component")
    def _handle_drop(self, pos):
        # Check if dropped on LayerPanel
        closest_layer = self.builder.layer_panel.get_target_layer_at(pos)
        
        if not closest_layer:
            # Fallback (optional?) or just ignore
            # User request: "Instead of Adding them to the circles... drop them onto this new list"
            # So we strictly enforce list dropping for component addition?
            # Or should we keep the old logic as backup? 
            # "Instead of" implies replacement.
            return
        
        if closest_layer:
            # Suppress header toggle (fix for drop causing toggle)
            if hasattr(self.builder.layer_panel, 'suppress_toggle'):
                self.builder.layer_panel.suppress_toggle()
            
            comp = self.dragged_item
            # Check restrictions using the centralized validator (allowed_layers removed from components)
            from ship import VALIDATOR
            validation = VALIDATOR.validate_addition(self.builder.ship, comp, closest_layer)
            
            if not validation.is_valid:
                 reason = ", ".join(validation.errors)
                 self.builder.show_error(f"Cannot place: {reason}")
                 return

            # Add component (re-validates internally, but that's fine)
            # Check bulk add count
            count = 1
            if hasattr(self.builder.left_panel, 'get_add_count'):
                count = self.builder.left_panel.get_add_count()
                
            if count > 1:
                added = self.builder.ship.add_components_bulk(comp, closest_layer, count)
                if added > 0:
                    self.builder.update_stats()
                    if added < count:
                        self.builder.show_error(f"Added only {added}/{count} (Check limits)")
                else:
                   self.builder.show_error("Could not add components")
            else:
                if self.builder.ship.add_component(comp, closest_layer):
                   self.builder.update_stats()
                else:
                   self.builder.show_error("Could not add component")
