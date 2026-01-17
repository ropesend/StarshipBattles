import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIVerticalScrollBar
from ui.colors import COLORS

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
    INTEREST_POINTS_RANGE = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    INTEREST_POINTS_ACCURACY = [0.99, 0.90, 0.80, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10, 0.01]
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
    COLOR_WEAPON_NAME = COLORS['text_bright']
    COLOR_DAMAGE_LABEL = (200, 200, 100) # Keep yellow for contrast
    COLOR_RANGE_LABEL = COLORS['text_normal']
    COLOR_RANGE_SCALE = COLORS['text_subtle']
    COLOR_SCALE_LINE = COLORS['border_subtle']
    COLOR_SCALE_LABEL = COLORS['text_disabled']
    COLOR_NO_WEAPONS = COLORS['text_disabled']
    COLOR_TARGET_INFO = COLORS['text_highlight']
    
    # === Accuracy Label Colors ===
    COLOR_ACC_HIGH = (0, 200, 0)      # > 50%
    COLOR_ACC_MEDIUM = (200, 100, 0)  # 20-50%
    COLOR_ACC_LOW = (200, 50, 50)     # < 20%
    
    # === Tooltip Constants ===
    TOOLTIP_PADDING = 10
    TOOLTIP_LINE_HEIGHT = 20
    TOOLTIP_BG_COLOR = COLORS['bg_dark']
    TOOLTIP_BORDER_COLOR = COLORS['border_active']
    
    # === Font Configuration ===
    FONT_NAME = "Arial"
    FONT_SIZE_NORMAL = 16
    FONT_SIZE_SMALL = 14
    
    def __init__(self, builder, manager, rect, sprite_mgr):
        self.builder = builder
        self.manager = manager
        self.rect = rect
        self.sprite_mgr = sprite_mgr
        
        # Cached fonts (avoid recreating every frame)
        self.font = pygame.font.SysFont(self.FONT_NAME, self.FONT_SIZE_NORMAL)
        self.small_font = pygame.font.SysFont(self.FONT_NAME, self.FONT_SIZE_SMALL)
        self.target_font = pygame.font.SysFont(self.FONT_NAME, self.FONT_SIZE_NORMAL)


        # Target ship for calculations
        self.target_ship = None
        self.target_defense_mod = 0.0 # Score
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
        
        # Button dimensions
        btn_w_proj = 110
        btn_w_beam = 110
        btn_w_seek = 110
        btn_w_all = 60
        
        self.btn_proj = UIButton(pygame.Rect(start_x, btn_y, btn_w_proj, btn_h), "Projectiles", manager=manager, container=self.panel)
        self.btn_beam = UIButton(pygame.Rect(start_x + btn_w_proj + spacing, btn_y, btn_w_beam, btn_h), "Beams", manager=manager, container=self.panel)
        self.btn_seek = UIButton(pygame.Rect(start_x + btn_w_proj + btn_w_beam + spacing * 2, btn_y, btn_w_seek, btn_h), "Seekers", manager=manager, container=self.panel)
        self.btn_all = UIButton(pygame.Rect(start_x + btn_w_proj + btn_w_beam + btn_w_seek + spacing * 3, btn_y, btn_w_all, btn_h), "All", manager=manager, container=self.panel)
        
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
        self._name_cache = {}  # weapon.name -> surface
        self.verbose_tooltip = False  # Toggle for detailed stats
        self.hovered_weapon = None  # Track weapon being hovered for firing arc display
        self._icon_cache = {}  # weapon.sprite_index -> scaled surface

    def _group_weapons(self, weapons):
        """Group identical weapons into stacks."""
        grouped = []
        
        # Helper to create a unique key for valid stacking
        def get_key(w):
            # Key: (ID, Modifiers (sorted), Facing, Arc)
            ab = w.get_ability('WeaponAbility')
            if not ab: return (w.id, (), 0, 0)
            
            mods = []
            for m in w.modifiers:
                mods.append((m.definition.id, m.value))
            mods.sort()
            return (w.id, tuple(mods), ab.facing_angle, ab.firing_arc)

        # Dictionary to build stacks: key -> {'weapon': w, 'count': n}
        stacks = {}
        
        for w in weapons:
            k = get_key(w)
            if k in stacks:
                stacks[k]['count'] += 1
            else:
                stacks[k] = {'weapon': w, 'count': 1}
        
        # Convert back to list, preserving order of first appearance if possible
        # Or just sort by name?
        # To preserve order, we might iterate weapons again or maintain list of keys
        
        # Simple approach: Sort by name, then ID
        sorted_stacks = sorted(stacks.values(), key=lambda x: x['weapon'].name)
        return sorted_stacks
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
        # Use target's total defense score
        self.target_defense_mod = getattr(ship, 'total_defense_score', 0.0)
        
    def clear_target(self):
        """Reset to default target parameters."""
        self.target_ship = None
        self.target_name = None
        self.target_defense_mod = 0.0
        
    def _get_all_weapons(self, ship):
        """Get list of all weapon components from ship, filtered."""
        weapons = []
        for comp in ship.get_components_by_ability('WeaponAbility'):
            # Filter by weapon ability type
            if comp.has_ability('ProjectileWeaponAbility') and not self.filter_states['projectile']:
                continue
            if comp.has_ability('BeamWeaponAbility') and not self.filter_states['beam']:
                continue
            if comp.has_ability('SeekerWeaponAbility') and not self.filter_states['seeker']:
                continue

            weapons.append(comp)
        return weapons
    
    def _calculate_accuracy_for_range(self, weapon, ship, range_val):
        """Calculate hit probability at a specific range using Sigmoid logic."""
        import math
        ab = weapon.get_ability('WeaponAbility')
        if not ab: return 0.0
        
        base_acc = getattr(ab, 'base_accuracy', 2.0)
        falloff = getattr(ab, 'accuracy_falloff', 0.001)
        
        attack_score = 0.0
        if hasattr(ship, 'get_total_sensor_score'):
            attack_score = ship.get_total_sensor_score()
            
        defense_score = self.target_defense_mod
        
        net_score = (base_acc + attack_score) - (range_val * falloff + defense_score)
        clamped = max(-20.0, min(20.0, net_score))
        return 1.0 / (1.0 + math.exp(-clamped))

    def _get_points_of_interest(self, weapon, ship):
        """
        Get a prioritized list of points to marker on the range bar.
        Points include range percentages and accuracy thresholds.
        Returns list of dicts: {'range': val, 'accuracy': val, 'damage': val, 'priority': int, 'color_key': int}
        Priority: 0 (Highest - Limits), 1 (Accuracy Thresholds), 2 (Intermediate Range)
        """
        points = []
        ab = weapon.get_ability('WeaponAbility')
        if not ab: return []
        
        weapon_range = ab.range
        damage = ab.damage
        is_beam = weapon.has_ability('BeamWeaponAbility')

        # 1. Add Range Percentages
        for pct in self.INTEREST_POINTS_RANGE:
            r = weapon_range * pct
            acc = self._calculate_accuracy_for_range(weapon, ship, r) if is_beam else None
            priority = 0 if (pct == 0.0 or pct == 1.0) else 2
            points.append({
                'range': r,
                'accuracy': acc,
                'damage': damage, # Future: scaled damage
                'priority': priority,
                'type': 'range',
                'marker_color': None # Use default for range markers
            })

        # 2. Add Accuracy Thresholds (Beams only)
        if is_beam:
            import math
            base_acc = getattr(ab, 'base_accuracy', 2.0)
            falloff = getattr(ab, 'accuracy_falloff', 0.001)
            attack_score = 0.0
            if hasattr(ship, 'get_total_sensor_score'):
                attack_score = ship.get_total_sensor_score()
            defense_score = self.target_defense_mod
            net_starting_score = (base_acc + attack_score) - defense_score

            for i, threshold in enumerate(self.INTEREST_POINTS_ACCURACY):
                p = max(0.0001, min(0.9999, threshold))
                logit_p = math.log(p / (1.0 - p))
                
                if falloff > 0:
                    r = (net_starting_score - logit_p) / falloff
                    if 0 < r < weapon_range:
                        points.append({
                            'range': r,
                            'accuracy': threshold,
                            'damage': damage,
                            'priority': 1,
                            'type': 'accuracy',
                            'marker_color': self.THRESHOLD_COLORS[i] if i < len(self.THRESHOLD_COLORS) else (150, 150, 150)
                        })
        
        # Sort by range
        points.sort(key=lambda x: x['range'])
        return points

    def _draw_unified_weapon_bar(self, screen, weapon, ship, bar_y, start_x, total_bar_width, weapon_bar_width, weapon_range):
        """Draw unified weapon bar with intelligent marker placement and collision detection."""
        # 1. Draw base bar
        is_beam = weapon.has_ability('BeamWeaponAbility')
        is_seeker = weapon.has_ability('SeekerWeaponAbility')
        
        bar_color = self.BEAM_BAR_COLOR if is_beam else (self.SEEKER_BAR_COLOR if is_seeker else self.PROJECTILE_BAR_COLOR)
        pygame.draw.line(screen, bar_color, (start_x, bar_y), (start_x + weapon_bar_width, bar_y), self.BAR_HEIGHT)

        # 2. Collect and filter points of interest
        all_points = self._get_points_of_interest(weapon, ship)
        
        # Filter for visibility and overlaps
        visible_points = []
        min_label_spacing = 35 # Pixels
        
        # Sort by priority first to ensure high-priority points are kept
        sorted_by_priority = sorted(all_points, key=lambda x: x['priority'])
        
        occupied_x = [] # List of (x_start, x_end) for labels
        
        for p in sorted_by_priority:
            px = start_x + int((p['range'] / self._max_range) * total_bar_width)
            
            # Simple collision check for labels
            # We assume labels are approx 30px wide
            label_half_w = 15
            overlaps = False
            for ox_min, ox_max in occupied_x:
                if px + label_half_w > ox_min and px - label_half_w < ox_max:
                    overlaps = True
                    break
            
            if not overlaps or p['priority'] == 0:
                visible_points.append(p)
                occupied_x.append((px - label_half_w - 5, px + label_half_w + 5))

        # 3. Draw visible points
        for p in visible_points:
            px = start_x + int((p['range'] / self._max_range) * total_bar_width)
            
            # Marker
            if p['type'] == 'accuracy':
                pygame.draw.circle(screen, p['marker_color'], (px, bar_y), self.MARKER_RADIUS)
            elif p['priority'] == 0: # Limits
                pygame.draw.circle(screen, (200, 200, 255), (px, bar_y), self.MARKER_RADIUS + 1, 1)
            else:
                pygame.draw.circle(screen, (150, 150, 150), (px, bar_y), self.MARKER_RADIUS - 1)

            # Accuracy Label (Above)
            if p['accuracy'] is not None:
                acc_color = self._get_accuracy_color(p['accuracy'])
                acc_text = f"{int(p['accuracy'] * 100)}%"
                acc_surf = self.small_font.render(acc_text, True, acc_color)
                screen.blit(acc_surf, (px - acc_surf.get_width()//2, bar_y - self.LABEL_ABOVE_OFFSET - 2))

            # Damage Label (Below)
            dmg_surf = self.small_font.render(f"D:{int(p['damage'])}", True, self.COLOR_DAMAGE_LABEL)
            screen.blit(dmg_surf, (px - dmg_surf.get_width()//2, bar_y + self.LABEL_BELOW_OFFSET))
            
            # Range Label (Far Below if it's a primary range point)
            if p['type'] == 'range' and p['range'] > 0:
                r_text = f"R:{int(p['range'])}" if p['priority'] == 0 else f"{int(p['range'])}"
                r_surf = self.small_font.render(r_text, True, self.COLOR_RANGE_SCALE)
                offset = self.LABEL_BELOW_RANGE_OFFSET if is_beam else self.LABEL_BELOW_OFFSET + 14
                screen.blit(r_surf, (px - r_surf.get_width()//2, bar_y + offset))
    
    def update(self):
        """Update weapon list and calculations."""
        ship = self.builder.ship
        raw_weapons = self._get_all_weapons(ship)
        self._weapons_cache = self._group_weapons(raw_weapons)
        
        # Find max range across all weapons
        self._max_range = 0
        for item in self._weapons_cache:
            weapon = item['weapon']
            ab = weapon.get_ability('WeaponAbility')
            weapon_range = ab.range if ab else 0
            if weapon_range > self._max_range:
                self._max_range = weapon_range
        
        # Clear icon cache when weapons change
        old_indices = set(self._icon_cache.keys())
        new_indices = set(item['weapon'].sprite_index for item in self._weapons_cache)
        if old_indices != new_indices:
            self._icon_cache.clear()

        # Clear name cache when weapons change
        old_names = set(self._name_cache.keys())
        new_names = set(item['weapon'].name for item in self._weapons_cache)
        if old_names != new_names:
            self._name_cache.clear()
            
        # Update Scrollbar
        total_height = len(self._weapons_cache) * self.WEAPON_ROW_HEIGHT
        visible_height = self.rect.height - 50 # minus header/padding
        
        if total_height > visible_height:
            self.scroll_bar.show()
            self.scroll_bar.set_visible_percentage(visible_height / total_height)
        else:
            self.scroll_bar.hide()
            self.scroll_bar.set_visible_percentage(1.0)
            self.scroll_bar.set_scroll_from_start_percentage(0.0)

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

    def _check_tooltip_hover(self, weapon, ship, bar_y, start_x, weapon_bar_width, bar_width, weapon_range, content_rect, current_mouse_pos):
        """Check if mouse is hovering over weapon bar and collect tooltip data if so."""
        if not content_rect.collidepoint(current_mouse_pos):
            return None
            
        hit_rect = pygame.Rect(start_x, bar_y - 10, weapon_bar_width, self.BAR_HEIGHT + 20)
        if not hit_rect.collidepoint(current_mouse_pos):
            return None
            
        # Calculate range at cursor
        dist_px = current_mouse_pos[0] - start_x
        dist_ratio = dist_px / bar_width
        hover_range = dist_ratio * self._max_range
        
        # Clamp range
        hover_range = max(0, min(hover_range, weapon_range))
        
        # Calculate stats
        ab = weapon.get_ability('WeaponAbility')
        if not ab: return None
        
        base_acc = getattr(ab, 'base_accuracy', 1.0)
        falloff = getattr(ab, 'accuracy_falloff', 0.0)
        ship_mod = getattr(ship, 'baseline_to_hit_offense', 1.0)
        target_mod = self.target_defense_mod
        damage = ab.damage
        
        if weapon.has_ability('BeamWeaponAbility'):
            # Sigmoid Logic
            import math
            
            # Scores
            attack_score = 0.0
            if hasattr(ship, 'get_total_sensor_score'):
                attack_score = ship.get_total_sensor_score()
            
            defense_score = self.target_defense_mod
                
            net_score = (base_acc + attack_score) - (hover_range * falloff + defense_score)
            
            # Sigmoid
            clamped = max(-20.0, min(20.0, net_score))
            hit_chance = 1.0 / (1.0 + math.exp(-clamped))
            
            acc_text = f"{int(hit_chance * 100)}%"
            verbose_info = {
                'base_acc': base_acc,
                'attack_score': attack_score,
                'defense_score': defense_score,
                'range_penalty': hover_range * falloff,
                'net_score': net_score
            }
        else:
            acc_text = "N/A"
            verbose_info = None
        
        # Calculate damage at this range
        # Future: Use ability specific damage scaling if needed
        hover_damage = damage
            
        return {
            'pos': current_mouse_pos,
            'range': int(hover_range),
            'accuracy': acc_text,
            'damage': int(hover_damage),
            'verbose': verbose_info
        }

    def _get_accuracy_color(self, chance):
        """Get color for accuracy label based on hit chance value."""
        if chance < 0.2:
            return self.COLOR_ACC_LOW
        elif chance > 0.5:
            return self.COLOR_ACC_HIGH
        else:
            return self.COLOR_ACC_MEDIUM

    # === Drawing Helper Methods ===

    def _get_scaled_icon(self, weapon):
        """Get cached scaled weapon icon, creating if needed."""
        idx = weapon.sprite_index
        if idx not in self._icon_cache:
            sprite = self.sprite_mgr.get_sprite(idx)
            if sprite:
                self._icon_cache[idx] = pygame.transform.scale(sprite, (self.WEAPON_ICON_SIZE, self.WEAPON_ICON_SIZE))
            else:
                return None
        return self._icon_cache.get(idx)

    def _get_weapon_name_surface(self, weapon, count):
        """Get cached weapon name surface, creating if needed."""
        name = weapon.name
        key = f"{name}_{count}" # Cache key must include count if we draw it here? 
        # Actually user asked for x2 to be added. 
        # Let's render "Name x2" or "Name (x2)"
        
        if key not in self._name_cache:
            display_name = name
            if len(name) > self.WEAPON_NAME_MAX_LEN:
                display_name = name[:self.WEAPON_NAME_TRUNCATE_LEN] + ".."
            
            if count > 1:
                display_name += f" x{count}"
                
            surf = self.font.render(display_name, True, self.COLOR_WEAPON_NAME)
            self._name_cache[key] = surf
        return self._name_cache[key]

    def _draw_direction_indicator(self, screen, cx, cy, weapon):
        """Draw a small visual indicator of firing arc and direction."""
        # Visual Constants
        RADIUS = 8
        COLOR_BG = (30, 30, 40)
        COLOR_OUTLINE = (100, 100, 120)
        COLOR_ARC = (200, 150, 50)
        COLOR_ARROW = (255, 255, 255)
        
        # Draw background circle
        pygame.draw.circle(screen, COLOR_BG, (cx, cy), RADIUS)
        pygame.draw.circle(screen, COLOR_OUTLINE, (cx, cy), RADIUS, 1)
        
        # Angles
        # Facing: 0 is Right, -90 is Up.
        # Ship Forward is typically Up (-90) in top-down, or Right (0)? 
        # If we assume 0 is component forward relative to ship, and ship forward is -90 (Up)
        # Visualizing 'facing_angle' as rotation.
        # Let's assume standard math: 0 deg = Right.
        
        ab = weapon.get_ability('WeaponAbility')
        if not ab: return
        
        facing = ab.facing_angle
        arc = ab.firing_arc
        
        # Convert to radians
        import math
        
        # We want to represent the arc.
        # If arc is 360, it's a full circle.
        if arc >= 360:
             pygame.draw.circle(screen, COLOR_ARC, (cx, cy), RADIUS - 2, 1)
        else:
            # Draw arc wedge
            # Start angle, End angle.
            # Pygame arc takes rect and start/stop angle in radians.
            # 0 is right, clockwise? No, pygame is radians, 0 is right, clockwise (positive y is down).
            
            # facing is the center of the arc.
            start_angle = math.radians(facing - arc/2)
            end_angle = math.radians(facing + arc/2)
            
            # Draw simplified arc using lines if small, or polylines
            # For a small icon, 2 lines + arc is good.
            
            # But pygame.draw.arc is thin.
            # Let's draw a few lines to simulate the wedge
            
            center = (cx, cy)
            
            # Start Vector
            # Note: Pygame coordinate system: +y is down. So -90 is up.
            # Angle 0: Right (1, 0).
            # We want visual representation.
            # -facing (because y is inverted usually in math vs screen? no, standard math on screen: 0 right, 90 down.)
            # If `facing_angle` follows standard math (0 right, 90 down).
            
            # Let's trust facing_angle is in degrees, standard pygame circle coordinates.
            
            p1_angle = math.radians(-facing - arc/2) # Invert for Y-up logic if needed? 
            # Actually, let's Stick to standard screen coords: x = cos(a), y = sin(a). +y is down.
            
            a1 = math.radians(facing - arc/2)
            a2 = math.radians(facing + arc/2)
            
            p1 = (cx + (RADIUS-2)*math.cos(a1), cy + (RADIUS-2)*math.sin(a1))
            p2 = (cx + (RADIUS-2)*math.cos(a2), cy + (RADIUS-2)*math.sin(a2))
            
            # Draw wedge lines
            pygame.draw.line(screen, COLOR_ARC, center, p1, 1)
            pygame.draw.line(screen, COLOR_ARC, center, p2, 1)
            
            # Draw arc segment (approximated)
            # rect for arc
            rect = pygame.Rect(cx-RADIUS+2, cy-RADIUS+2, (RADIUS-2)*2, (RADIUS-2)*2)
            # pygame.draw.arc(screen, COLOR_ARC, rect, -a2, -a1) # Angles are inverted in pygame? "0 is right, increasing counter-clockwise"? 
            # Docs: "start_angle, stop_angle: Radians." 0 is right. Counter-clockwise is positive? 
            # No, in screen space (+y down), 0 is right. Positive angle usually goes Clockwise (towards +y).
            # Wait, standard math: +y is Up. Screen: +y Down.
            # cos(0)=1, sin(0)=0 (Right).
            # cos(90)=0, sin(90)=1 (Down).
            # So Positive Angle = Clockwise.
            
            # So if facing=0 (Right), and arc=90. Range -45 to +45.
            # start = -45 (Up-Right). Stop = 45 (Down-Right).
            
            pygame.draw.arc(screen, COLOR_ARC, rect, -a2, -a1) # Try standard first. 
            
            # Draw small arrow for direction
            dir_rad = math.radians(facing)
            arrow_len = RADIUS
            end_pos = (cx + arrow_len*math.cos(dir_rad), cy + arrow_len*math.sin(dir_rad))
            pygame.draw.line(screen, COLOR_ARROW, center, end_pos, 2)
    
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


    def _draw_tooltip(self, screen):
        """Draw the hover tooltip if data is available."""
        if not self._tooltip_data:
            return
            
        mx, my = self._tooltip_data['pos']
        
        if self.verbose_tooltip and self._tooltip_data.get('verbose'):
            v = self._tooltip_data['verbose']
            lines = [
                f"Range: {self._tooltip_data['range']}",
                f"Base Score: {v['base_acc']:.2f}",
                f"Attack Score: +{v['attack_score']:.2f}",
                f"Range Penalty: -{v['range_penalty']:.2f}",
                f"Defense Score: -{v['defense_score']:.2f}",
                f"Net Score: {v['net_score']:.2f}",
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
            screen.blit(target_surf, (self.rect.x + 660, self.rect.y + 5))
            
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
        for i, item in enumerate(self._weapons_cache):
            weapon = item['weapon']
            count = item['count']
            
            row_y = draw_start_y + i * self.WEAPON_ROW_HEIGHT
            
            # Optimization: Skip if outside visible area
            if row_y + self.WEAPON_ROW_HEIGHT < content_rect.top or row_y > content_rect.bottom:
                continue
            
            # Draw weapon icon
            scaled = self._get_scaled_icon(weapon)
            if scaled:
                screen.blit(scaled, (self.rect.x + self.WEAPON_ICON_X_OFFSET, row_y + self.WEAPON_ICON_Y_OFFSET))
            
            # Draw weapon name (with count)
            name_surf = self._get_weapon_name_surface(weapon, count)
            screen.blit(name_surf, (self.rect.x + self.WEAPON_NAME_X_OFFSET, row_y + self.WEAPON_NAME_Y_OFFSET))
            
            # Draw Direction/Arc Indicator (Right of name)
            # Place it after name (or fixed column?). Name truncated len is approx 150-200px?
            # WEAPON_NAME_WIDTH = 250.
            # Let's put it at X = 200 relative to panel?
            # Or just after the text? 
            # Fixed position is cleaner.
            indicator_x = self.rect.x + 220
            indicator_y = row_y + self.WEAPON_ROW_HEIGHT // 2
            self._draw_direction_indicator(screen, indicator_x, indicator_y, weapon)

            # Draw range bar
            bar_y = row_y + self.BAR_Y_OFFSET
            # Safe Range/Damage Access via Ability
            ab = weapon.get_ability('WeaponAbility')
            weapon_range = ab.range if ab else 0
            damage = ab.damage if ab else 0
            
            weapon_bar_width = 0
            if self._max_range > 0 and weapon_range > 0:
                weapon_bar_width = int((weapon_range / self._max_range) * bar_width)
                
                self._draw_unified_weapon_bar(screen, weapon, ship, bar_y, start_x, bar_width, weapon_bar_width, weapon_range)
            
            # Check for weapon row hover (for firing arc display)
            weapon_row_rect = pygame.Rect(self.rect.x, row_y, self.rect.width - self.scroll_bar_width, self.WEAPON_ROW_HEIGHT)
            if weapon_row_rect.collidepoint(current_mouse_pos) and content_rect.collidepoint(current_mouse_pos):
                self.hovered_weapon = weapon
            
            # Check for tooltip hover (use content_rect to ensure we don't hover hidden items)
            tooltip_data = self._check_tooltip_hover(
                weapon, ship, bar_y, start_x, weapon_bar_width, bar_width, 
                weapon_range, content_rect, current_mouse_pos
            )
            if tooltip_data:
                self._tooltip_data = tooltip_data

        # Restore clipping
        screen.set_clip(old_clip)

        # Draw tooltip LAST so it's on top of everything
        self._draw_tooltip(screen)
