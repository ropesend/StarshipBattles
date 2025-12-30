import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIVerticalScrollBar
from components import Weapon, BeamWeapon, SeekerWeapon, ProjectileWeapon

class WeaponsReportPanel:
    """Panel displaying weapon range and hit probability visualization."""
    
    # === Layout Constants ===
    THRESHOLDS = [0.99, 0.90, 0.80, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10, 0.01]
    WEAPON_ROW_HEIGHT = 45
    WEAPON_NAME_WIDTH = 250
    RANGE_BAR_LEFT_MARGIN = 15
    WEAPON_ICON_SIZE = 32
    WEAPON_ICON_X_OFFSET = 5
    WEAPON_ICON_Y_OFFSET = 6
    WEAPON_NAME_X_OFFSET = 45
    WEAPON_NAME_Y_OFFSET = 12
    WEAPON_NAME_MAX_LEN = 28
    WEAPON_NAME_TRUNCATE_LEN = 25
    
    # === Bar Drawing Constants ===
    BAR_HEIGHT = 10
    BAR_Y_OFFSET = 22  # Offset from row top to bar center
    MARKER_RADIUS = 5
    
    # === Label Positioning ===
    LABEL_ABOVE_OFFSET = 16  # Pixels above bar for labels
    LABEL_BELOW_OFFSET = 8   # Pixels below bar for labels
    LABEL_BELOW_RANGE_OFFSET = 20  # Beam range labels below bar
    SCALE_LABEL_OFFSET = 16  # Scale markers above content
    
    # === Breakpoints ===
    BREAKPOINTS_FULL = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]  # For projectile/seeker
    BREAKPOINTS_MID = [0.2, 0.4, 0.6, 0.8]  # For beam intermediate
    SCALE_MARKERS = [0.25, 0.5, 0.75]  # Background scale lines
    
    # === Color Gradients ===
    # Accuracy threshold colors (green to red for 99% down to 1%)
    THRESHOLD_COLORS = [
        (0, 255, 0),    # 99%
        (50, 230, 0),   # 90%
        (100, 200, 0),  # 80%
        (150, 180, 0),  # 70%
        (180, 150, 0),  # 60%
        (200, 120, 0),  # 50%
        (220, 90, 0),   # 40%
        (240, 60, 0),   # 30%
        (255, 30, 0),   # 20%
        (255, 0, 0),    # 10%
        (150, 0, 0),    # 1%
    ]
    
    # Damage breakpoint colors (green to red for 0% to 100% of range)
    DAMAGE_GRADIENT_COLORS = [
        (50, 255, 50),   # 0% (max damage - bright green)
        (100, 220, 50),  # 20%
        (150, 180, 50),  # 40%
        (200, 140, 50),  # 60%
        (230, 100, 50),  # 80%
        (255, 60, 50),   # 100% (min damage - red)
    ]
    
    # Beam intermediate breakpoint colors (subset of damage gradient)
    BEAM_MID_COLORS = [
        (100, 220, 50),  # 20%
        (150, 180, 50),  # 40%
        (200, 140, 50),  # 60%
        (230, 100, 50),  # 80%
    ]
    
    # === Bar Base Colors ===
    BEAM_BAR_COLOR = (40, 80, 40)
    PROJECTILE_BAR_COLOR = (80, 60, 40)
    SEEKER_BAR_COLOR = (80, 40, 80)
    
    # === Text Colors ===
    COLOR_WEAPON_NAME = (200, 200, 200)
    COLOR_DAMAGE_LABEL = (200, 200, 100)
    COLOR_RANGE_LABEL = (180, 180, 180)
    COLOR_RANGE_SCALE = (120, 120, 140)
    COLOR_SCALE_LINE = (50, 50, 70)
    COLOR_SCALE_LABEL = (80, 80, 100)
    COLOR_NO_WEAPONS = (100, 100, 100)
    COLOR_TARGET_INFO = (200, 220, 100)
    
    # === Tooltip Constants ===
    TOOLTIP_PADDING = 10
    TOOLTIP_LINE_HEIGHT = 20
    TOOLTIP_BG_COLOR = (30, 30, 40)
    TOOLTIP_BORDER_COLOR = (100, 100, 120)
    
    def __init__(self, builder, manager, rect, sprite_mgr):
        self.builder = builder
        self.manager = manager
        self.rect = rect
        self.sprite_mgr = sprite_mgr
        
        # Cached fonts (avoid recreating every frame)
        self.font = pygame.font.SysFont("Arial", 16)
        self.small_font = pygame.font.SysFont("Arial", 14)
        self.target_font = pygame.font.SysFont("Arial", 16)
        
        # Target ship for calculations
        self.target_ship = None
        self.target_defense_mod = 1.0
        self.target_name = None
        
        # Background panel
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#weapons_report_panel'
        )
        
        # Title label
        UILabel(
            relative_rect=pygame.Rect(10, 5, 200, 20),
            text="── Weapons Report ──",
            manager=manager,
            container=self.panel
        )
        
        # Filter Buttons
        btn_y = 2
        btn_h = 24
        start_x = 220
        spacing = 5
        
        self.filter_states = {
            'projectile': True, 
            'beam': True, 
            'seeker': True
        }
        
        self.btn_proj = UIButton(pygame.Rect(start_x, btn_y, 80, btn_h), "Projectiles", manager=manager, container=self.panel)
        self.btn_beam = UIButton(pygame.Rect(start_x + 80 + spacing, btn_y, 60, btn_h), "Beams", manager=manager, container=self.panel)
        self.btn_seek = UIButton(pygame.Rect(start_x + 140 + spacing * 2, btn_y, 70, btn_h), "Seekers", manager=manager, container=self.panel)
        self.btn_all = UIButton(pygame.Rect(start_x + 210 + spacing * 3, btn_y, 50, btn_h), "All", manager=manager, container=self.panel)
        
        self._update_button_colors()
        
        # Scrollbar
        self.scroll_bar_width = 18
        self.scroll_bar = UIVerticalScrollBar(
            relative_rect=pygame.Rect(rect.width - self.scroll_bar_width - 2, 35, self.scroll_bar_width, rect.height - 40),
            visible_percentage=1.0,
            manager=manager,
            container=self.panel
        )
        self.scroll_offset = 0
        
        # Cache for drawn content
        self._weapons_cache = []
        self._max_range = 0
        self._tooltip_data = None  # Store tooltip data for rendering on top
        self.verbose_tooltip = False  # Toggle for detailed stats
        self.hovered_weapon = None  # Track weapon being hovered for firing arc display
    def _update_button_colors(self):
        # Update button text/colours to reflect state
        # Note: PygameGUI doesn't make changing specific button colors easy without State, 
        # but we can toggle text or select state if supported. 
        # For now, let's just use text indicators or rely on the UI theme highlighting selected.
        
        # Simpler approach: Prepend/Append based on state
        def set_text(btn, text, state):
            prefix = "[x] " if state else "[ ] "
            btn.set_text(prefix + text)
            
        set_text(self.btn_proj, "Projs", self.filter_states['projectile'])
        set_text(self.btn_beam, "Beams", self.filter_states['beam'])
        set_text(self.btn_seek, "Seekers", self.filter_states['seeker'])
        
    def set_target(self, ship):
        """Set a specific target ship for calculations."""
        self.target_ship = ship
        self.target_name = ship.name
        # Use target's defensive modifier if available
        self.target_defense_mod = getattr(ship, 'to_hit_profile', 1.0)
        
    def clear_target(self):
        """Reset to default target parameters."""
        self.target_ship = None
        self.target_name = None
        self.target_defense_mod = 1.0
        
    def _get_all_weapons(self, ship):
        """Get list of all weapon components from ship, filtered."""
        weapons = []
        for layer_data in ship.layers.values():
            for comp in layer_data['components']:
                if isinstance(comp, Weapon):
                    # Filter
                    if isinstance(comp, ProjectileWeapon) and not self.filter_states['projectile']: continue
                    if isinstance(comp, BeamWeapon) and not self.filter_states['beam']: continue
                    if isinstance(comp, SeekerWeapon) and not self.filter_states['seeker']: continue
                    
                    weapons.append(comp)
        return weapons
    
    def _calculate_threshold_ranges(self, weapon, ship):
        """
        Calculate the range at which each hit probability threshold is reached.
        
        Returns list of tuples: (threshold, range_value, damage)
        Range is None if threshold is unreachable within weapon range.
        """
        results = []
        target_defense = self.target_defense_mod
        
        
        base_acc = getattr(weapon, 'base_accuracy', 1.0)
        falloff = getattr(weapon, 'accuracy_falloff', 0.0)
        max_range = getattr(weapon, 'range', 0)
        ship_offense = getattr(ship, 'baseline_to_hit_offense', 1.0)
        damage = getattr(weapon, 'damage', 0)
        
        for threshold in self.THRESHOLDS:
            # Calculate range needed for this hit chance
            if falloff > 0:
                # New Formula: Hit = Base * (1 - Range*Falloff) * ShipMod * TargetMod
                # Hit / (Base * ShipMod * TargetMod) = 1 - Range*Falloff
                # Range*Falloff = 1 - (Hit / Denom)
                # Range = (1 - (Hit / Denom)) / Falloff
                
                denom = base_acc * ship_offense * target_defense
                if denom == 0:
                    range_for_threshold = None
                else:
                    ratio = threshold / denom
                    if ratio > 1.0:
                        range_for_threshold = None # Impossible to reach this accuracy
                    else:
                        range_for_threshold = (1.0 - ratio) / falloff
            else:
                # No falloff - either always or never hits at this threshold
                effective_base = base_acc * ship_offense * target_defense
                if effective_base >= threshold:
                    range_for_threshold = max_range  # Achievable at max range
                else:
                    range_for_threshold = None  # Never reaches this threshold
            
            # Clamp to weapon's max range
            if range_for_threshold is not None:
                if range_for_threshold <= 0:
                    range_for_threshold = 0
                elif range_for_threshold > max_range:
                    range_for_threshold = None  # Unreachable within weapon range
                    
            results.append((threshold, range_for_threshold, damage))
            
        return results
    
    def update(self):
        """Update weapon list and calculations."""
        ship = self.builder.ship
        self._weapons_cache = self._get_all_weapons(ship)
        # Find max range across all weapons
        self._max_range = 0
        for weapon in self._weapons_cache:
            weapon_range = getattr(weapon, 'range', 0)
            if weapon_range > self._max_range:
                self._max_range = weapon_range
        # Update Scrollbar
        total_height = len(self._weapons_cache) * self.WEAPON_ROW_HEIGHT
        visible_height = self.rect.height - 50 # minus header/padding
        
        if total_height > visible_height:
            self.scroll_bar.show()
            self.scroll_bar.set_visible_percentage(visible_height / total_height)
        else:
            self.scroll_bar.hide()
            self.scroll_bar.set_visible_percentage(1.0)
            self.scroll_bar.set_scroll_from_start_percentage(0.0)  # Reset if not needed

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_proj:
                self.filter_states['projectile'] = not self.filter_states['projectile']
                self._update_button_colors()
            elif event.ui_element == self.btn_beam:
                self.filter_states['beam'] = not self.filter_states['beam']
                self._update_button_colors()
            elif event.ui_element == self.btn_seek:
                self.filter_states['seeker'] = not self.filter_states['seeker']
                self._update_button_colors()
            elif event.ui_element == self.btn_all:
                self.filter_states['projectile'] = True
                self.filter_states['beam'] = True
                self.filter_states['seeker'] = True
                self._update_button_colors()
        
        # Handle mouse wheel scrolling when cursor is over the panel
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.rect.collidepoint(mx, my):
                # Calculate scroll step (3 rows per wheel notch)
                total_height = len(self._weapons_cache) * self.WEAPON_ROW_HEIGHT
                visible_height = self.rect.height - 50
                if total_height > visible_height:
                    # Scroll amount as percentage of scrollable content
                    scroll_step = (self.WEAPON_ROW_HEIGHT * 3) / (total_height - visible_height)
                    # Adjust current position (event.y is positive for scroll up, negative for scroll down)
                    new_pct = self.scroll_bar.start_percentage - (event.y * scroll_step * (1.0 - visible_height / total_height))
                    new_pct = max(0.0, min(1.0, new_pct))
                    self.scroll_bar.set_scroll_from_start_percentage(new_pct)

    # === Drawing Helper Methods ===
    
    def _draw_scale_markers(self, screen, start_x, bar_width, draw_start_y, content_height):
        """Draw background scale lines and range labels."""
        if self._max_range <= 0:
            return
            
        max_range_x = start_x + bar_width
        
        # Max range line
        pygame.draw.line(screen, self.COLOR_SCALE_LINE, 
                       (max_range_x, draw_start_y - 5), 
                       (max_range_x, draw_start_y + content_height + 5), 1)
        
        # Max range label
        range_label = self.small_font.render(f"{int(self._max_range)}", True, (150, 150, 200))
        screen.blit(range_label, (max_range_x - range_label.get_width()//2, draw_start_y - self.SCALE_LABEL_OFFSET))
        
        # Intermediate scale markers
        for pct in self.SCALE_MARKERS:
            scale_x = start_x + int(pct * bar_width)
            pygame.draw.line(screen, self.COLOR_SCALE_LINE, (scale_x, draw_start_y - 3), 
                           (scale_x, draw_start_y + content_height), 1)
            scale_label = self.small_font.render(f"{int(self._max_range * pct)}", True, self.COLOR_SCALE_LABEL)
            screen.blit(scale_label, (scale_x - scale_label.get_width()//2, draw_start_y - self.SCALE_LABEL_OFFSET))

    def _draw_beam_weapon_bar(self, screen, weapon, ship, bar_y, start_x, bar_width, weapon_bar_width, weapon_range, damage):
        """Draw beam weapon range bar with accuracy and damage markers."""
        pygame.draw.line(screen, self.BEAM_BAR_COLOR, (start_x, bar_y), (start_x + weapon_bar_width, bar_y), self.BAR_HEIGHT)
        
        # Calculate stats for start/end
        base_acc = getattr(weapon, 'base_accuracy', 1.0)
        falloff = getattr(weapon, 'accuracy_falloff', 0.0)
        ship_mod = getattr(ship, 'baseline_to_hit_offense', 1.0)
        target_mod = self.target_defense_mod
        
        factor_at_0 = max(0.0, 1.0 - (0 * falloff))
        factor_at_max = max(0.0, 1.0 - (weapon_range * falloff))
        
        chance_at_0 = max(0.0, min(1.0, base_acc * factor_at_0 * ship_mod * target_mod))
        chance_at_max = max(0.0, min(1.0, base_acc * factor_at_max * ship_mod * target_mod))
        
        # Calculate damage at start/end
        if hasattr(weapon, 'get_damage'):
            dmg_at_0 = weapon.get_damage(0)
            dmg_at_max = weapon.get_damage(weapon_range)
        else:
            dmg_at_0 = dmg_at_max = damage
        
        # Draw Start: Accuracy ABOVE, Damage BELOW
        start_label_color = (0, 200, 0) if chance_at_0 > 0.5 else (200, 100, 0)
        if chance_at_0 < 0.2: start_label_color = (200, 50, 50)
        
        s_acc_label = self.small_font.render(f"{int(chance_at_0 * 100)}%", True, start_label_color)
        screen.blit(s_acc_label, (start_x - s_acc_label.get_width() - 5, bar_y - 10))
        
        s_dmg_label = self.small_font.render(f"D:{int(dmg_at_0)}", True, self.COLOR_DAMAGE_LABEL)
        screen.blit(s_dmg_label, (start_x + 2, bar_y + self.LABEL_BELOW_OFFSET))
        
        # Draw End: Accuracy ABOVE, Damage BELOW, Range indicator
        end_label_color = (0, 200, 0) if chance_at_max > 0.5 else (200, 100, 0)
        if chance_at_max < 0.2: end_label_color = (200, 50, 50)
        
        end_x = start_x + weapon_bar_width
        e_acc_label = self.small_font.render(f"{int(chance_at_max * 100)}%", True, end_label_color)
        screen.blit(e_acc_label, (end_x + 5, bar_y - 10))
        
        e_dmg_label = self.small_font.render(f"D:{int(dmg_at_max)}", True, self.COLOR_DAMAGE_LABEL)
        screen.blit(e_dmg_label, (end_x - e_dmg_label.get_width() - 2, bar_y + self.LABEL_BELOW_OFFSET))
        
        # Range indicator at max range
        range_label = self.small_font.render(f"R:{int(weapon_range)}", True, self.COLOR_RANGE_LABEL)
        screen.blit(range_label, (end_x + 5, bar_y + self.LABEL_BELOW_OFFSET))
        
        # Intermediate threshold markers
        threshold_data = self._calculate_threshold_ranges(weapon, ship)
        
        for j, (threshold, range_val, dmg) in enumerate(threshold_data):
            if range_val is not None and range_val > (weapon_range * 0.10) and range_val < (weapon_range * 0.90):
                marker_x = start_x + int((range_val / self._max_range) * bar_width)
                color = self.THRESHOLD_COLORS[j] if j < len(self.THRESHOLD_COLORS) else (150, 150, 150)
                
                pygame.draw.circle(screen, color, (marker_x, bar_y), self.MARKER_RADIUS)
                
                pct_text = f"{int(threshold * 100)}%"
                pct_label = self.small_font.render(pct_text, True, color)
                screen.blit(pct_label, (marker_x - pct_label.get_width()//2, bar_y - self.LABEL_ABOVE_OFFSET - 2))
        
        # Mid-range breakpoint labels
        for bp_idx, bp_pct in enumerate(self.BREAKPOINTS_MID):
            bp_range = int(weapon_range * bp_pct)
            bp_x = start_x + int(bp_pct * weapon_bar_width)
            
            range_surf = self.small_font.render(f"{int(bp_range)}", True, self.COLOR_RANGE_SCALE)
            screen.blit(range_surf, (bp_x - range_surf.get_width()//2, bar_y + self.LABEL_BELOW_RANGE_OFFSET))
            
            if hasattr(weapon, 'get_damage'):
                bp_damage = weapon.get_damage(bp_range)
            else:
                bp_damage = damage
            dmg_surf = self.small_font.render(f"D:{int(bp_damage)}", True, self.BEAM_MID_COLORS[bp_idx])
            screen.blit(dmg_surf, (bp_x - dmg_surf.get_width()//2, bar_y + self.LABEL_BELOW_OFFSET))

    def _draw_projectile_weapon_bar(self, screen, weapon, bar_y, start_x, bar_width, weapon_bar_width, weapon_range, damage, is_seeker):
        """Draw projectile/seeker weapon range bar with damage breakpoints."""
        bar_color = self.SEEKER_BAR_COLOR if is_seeker else self.PROJECTILE_BAR_COLOR
        pygame.draw.line(screen, bar_color, (start_x, bar_y), (start_x + weapon_bar_width, bar_y), self.BAR_HEIGHT)
        
        # Draw damage at range breakpoints
        for bp_idx, bp_pct in enumerate(self.BREAKPOINTS_FULL):
            bp_range = int(weapon_range * bp_pct)
            if hasattr(weapon, 'get_damage'):
                bp_damage = weapon.get_damage(bp_range)
            else:
                bp_damage = damage
            
            bp_x = start_x + int(bp_pct * weapon_bar_width)
            bp_color = self.DAMAGE_GRADIENT_COLORS[bp_idx]
            
            pygame.draw.circle(screen, bp_color, (bp_x, bar_y), self.MARKER_RADIUS)
            
            dmg_surf = self.small_font.render(f"D:{int(bp_damage)}", True, bp_color)
            screen.blit(dmg_surf, (bp_x - dmg_surf.get_width()//2, bar_y + self.LABEL_BELOW_OFFSET))
            
            if bp_pct > 0:
                range_surf = self.small_font.render(f"{int(bp_range)}", True, self.COLOR_RANGE_SCALE)
                screen.blit(range_surf, (bp_x - range_surf.get_width()//2, bar_y - self.LABEL_ABOVE_OFFSET))
        
        # Range end label
        end_x = start_x + weapon_bar_width
        range_label = self.small_font.render(f"R:{int(weapon_range)}", True, self.COLOR_RANGE_LABEL)
        screen.blit(range_label, (end_x + 5, bar_y - 4))

    def _draw_tooltip(self, screen):
        """Draw the hover tooltip if data is available."""
        if not self._tooltip_data:
            return
            
        mx, my = self._tooltip_data['pos']
        
        if self.verbose_tooltip and self._tooltip_data.get('verbose'):
            v = self._tooltip_data['verbose']
            lines = [
                f"Range: {self._tooltip_data['range']}",
                f"Base Accuracy: {v['base_acc']:.2f}",
                f"Range Factor: x{v['range_factor']:.3f} (1 - {self._tooltip_data['range']} * {v['falloff']})",
                f"Ship Offense Mod: x{v['ship_mod']:.2f}",
                f"Target Defense Mod: x{v['target_mod']:.2f}",
                f"----------------",
                f"Final Accuracy: {self._tooltip_data['accuracy']}",
                f"Damage: {self._tooltip_data['damage']}"
            ]
        else:
            lines = [
                f"Range: {self._tooltip_data['range']}",
                f"Accuracy: {self._tooltip_data['accuracy']}",
                f"Damage: {self._tooltip_data['damage']}"
            ]
        
        max_w = 0
        surfs = []
        
        for line in lines:
            s = self.small_font.render(line, True, (255, 255, 255))
            surfs.append(s)
            max_w = max(max_w, s.get_width())
        
        tt_w = max_w + self.TOOLTIP_PADDING * 2
        tt_h = len(lines) * self.TOOLTIP_LINE_HEIGHT + self.TOOLTIP_PADDING * 2
        
        tt_rect = pygame.Rect(mx + 15, my - tt_h - 10, tt_w, tt_h)
        
        # Keep on screen
        if tt_rect.right > screen.get_width():
            tt_rect.x -= (tt_rect.width + 30)
        if tt_rect.top < 0:
            tt_rect.y = my + 10
            
        pygame.draw.rect(screen, self.TOOLTIP_BG_COLOR, tt_rect)
        pygame.draw.rect(screen, self.TOOLTIP_BORDER_COLOR, tt_rect, 1)
        
        for i, s in enumerate(surfs):
            screen.blit(s, (tt_rect.x + self.TOOLTIP_PADDING, tt_rect.y + self.TOOLTIP_PADDING + i * self.TOOLTIP_LINE_HEIGHT))

    
    def draw(self, screen):
        """Draw the weapons report visualization."""
        # Draw target info if active
        if self.target_name:
            target_text = f"Target: {self.target_name} (Def Mod: {self.target_defense_mod:.2f})"
            target_surf = self.target_font.render(target_text, True, self.COLOR_TARGET_INFO)
            screen.blit(target_surf, (self.rect.x + 300, self.rect.y + 5))
            
        if not self._weapons_cache:
            # No weapons to display
            text = self.font.render("No weapons equipped", True, self.COLOR_NO_WEAPONS)
            screen.blit(text, (self.rect.x + 10, self.rect.y + 40))
            return
            
        ship = self.builder.ship
        
        # Drawing area
        start_x = self.rect.x + self.WEAPON_NAME_WIDTH + self.RANGE_BAR_LEFT_MARGIN
        bar_width = self.rect.width - self.WEAPON_NAME_WIDTH - self.RANGE_BAR_LEFT_MARGIN - 60 - self.scroll_bar_width
        start_y = self.rect.y + 40
        
        # Define clip rect for content
        content_rect = pygame.Rect(self.rect.x, start_y, self.rect.width - self.scroll_bar_width, self.rect.height - 50)
        old_clip = screen.get_clip()
        screen.set_clip(content_rect.clip(old_clip))
        
        # Recalculate scroll offset dynamically (scrollbar position may have changed)
        total_height = len(self._weapons_cache) * self.WEAPON_ROW_HEIGHT
        visible_height = self.rect.height - 50
        if total_height > visible_height:
            # start_percentage goes from 0 to (1 - visible_percentage)
            # Normalize to get full scroll range
            visible_pct = visible_height / total_height
            max_start_pct = max(0.001, 1.0 - visible_pct)  # Avoid division by zero
            normalized_scroll = self.scroll_bar.start_percentage / max_start_pct
            self.scroll_offset = normalized_scroll * (total_height - visible_height)
        else:
            self.scroll_offset = 0
        
        # Adjust start_y by scroll offset
        draw_start_y = start_y - int(self.scroll_offset)
        
        # Draw scale markers
        content_height = len(self._weapons_cache) * self.WEAPON_ROW_HEIGHT
        self._draw_scale_markers(screen, start_x, bar_width, draw_start_y, content_height)
        
        # Reset tooltip data and hovered weapon
        self._tooltip_data = None
        self.hovered_weapon = None
        current_mouse_pos = pygame.mouse.get_pos()
        
        # Draw each weapon row
        for i, weapon in enumerate(self._weapons_cache):
            row_y = draw_start_y + i * self.WEAPON_ROW_HEIGHT
            
            # Optimization: Skip if outside visible area
            if row_y + self.WEAPON_ROW_HEIGHT < content_rect.top or row_y > content_rect.bottom:
                continue
            
            # Draw weapon icon
            sprite = self.sprite_mgr.get_sprite(weapon.sprite_index)
            if sprite:
                scaled = pygame.transform.scale(sprite, (self.WEAPON_ICON_SIZE, self.WEAPON_ICON_SIZE))
                screen.blit(scaled, (self.rect.x + self.WEAPON_ICON_X_OFFSET, row_y + self.WEAPON_ICON_Y_OFFSET))
            
            # Draw weapon name (truncated if needed)
            name = weapon.name
            if len(name) > self.WEAPON_NAME_MAX_LEN:
                name = name[:self.WEAPON_NAME_TRUNCATE_LEN] + ".."
            name_surf = self.font.render(name, True, self.COLOR_WEAPON_NAME)
            screen.blit(name_surf, (self.rect.x + self.WEAPON_NAME_X_OFFSET, row_y + self.WEAPON_NAME_Y_OFFSET))
            
            # Draw range bar
            bar_y = row_y + self.BAR_Y_OFFSET
            weapon_range = getattr(weapon, 'range', 0)
            damage = getattr(weapon, 'damage', 0)
            
            if self._max_range > 0 and weapon_range > 0:
                weapon_bar_width = int((weapon_range / self._max_range) * bar_width)
                
                # Check weapon type to determine display style
                is_beam = isinstance(weapon, BeamWeapon)
                is_seeker = isinstance(weapon, SeekerWeapon)
                is_projectile = isinstance(weapon, ProjectileWeapon)
                
                if is_beam:
                    self._draw_beam_weapon_bar(screen, weapon, ship, bar_y, start_x, bar_width, weapon_bar_width, weapon_range, damage)
                else:
                    self._draw_projectile_weapon_bar(screen, weapon, bar_y, start_x, bar_width, weapon_bar_width, weapon_range, damage, is_seeker)
            
            # Check for weapon row hover (for firing arc display)
            weapon_row_rect = pygame.Rect(self.rect.x, row_y, self.rect.width - self.scroll_bar_width, self.WEAPON_ROW_HEIGHT)
            if weapon_row_rect.collidepoint(current_mouse_pos) and content_rect.collidepoint(current_mouse_pos):
                self.hovered_weapon = weapon
            
            # Check for tooltip hover (use content_rect to ensure we don't hover hidden items)
            if content_rect.collidepoint(current_mouse_pos):
                hit_rect = pygame.Rect(start_x, bar_y - 10, weapon_bar_width, self.BAR_HEIGHT + 20)
                if hit_rect.collidepoint(current_mouse_pos):
                    # Calculate range at cursor
                    dist_px = current_mouse_pos[0] - start_x
                    dist_ratio = dist_px / bar_width
                    hover_range = dist_ratio * self._max_range
                    
                    # Clamp range
                    if hover_range < 0: hover_range = 0
                    if hover_range > weapon_range: hover_range = weapon_range
                    
                    # Calculate stats
                    base_acc = getattr(weapon, 'base_accuracy', 1.0)
                    falloff = getattr(weapon, 'accuracy_falloff', 0.0)
                    ship_mod = getattr(ship, 'baseline_to_hit_offense', 1.0)
                    target_mod = self.target_defense_mod
                    damage = getattr(weapon, 'damage', 0)
                    
                    if isinstance(weapon, BeamWeapon):
                        # Multiplicative logic
                        range_factor = max(0.0, 1.0 - (hover_range * falloff))
                        hit_chance = base_acc * range_factor * ship_mod * target_mod
                        hit_chance = max(0.0, min(1.0, hit_chance))
                        acc_text = f"{int(hit_chance * 100)}%"
                        
                        verbose_info = {
                            'base_acc': base_acc,
                            'falloff': falloff, 
                            'range_factor': range_factor,
                            'ship_mod': ship_mod,
                            'target_mod': target_mod
                        }
                    else:
                        acc_text = "N/A"
                        verbose_info = None
                    
                    # Calculate damage at this range using get_damage if available
                    if hasattr(weapon, 'get_damage'):
                        hover_damage = weapon.get_damage(hover_range)
                    else:
                        hover_damage = damage
                        
                    self._tooltip_data = {
                        'pos': current_mouse_pos,
                        'range': int(hover_range),
                        'accuracy': acc_text,
                        'damage': int(hover_damage),
                        'verbose': verbose_info
                    }

        # Restore clipping
        screen.set_clip(old_clip)

        # Draw tooltip LAST so it's on top of everything
        self._draw_tooltip(screen)
