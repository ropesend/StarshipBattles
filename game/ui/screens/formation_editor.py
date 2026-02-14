"""
Formation Editor - Screen for creating and editing fleet formations.

Allows players to arrange ships in tactical formations for combat deployment.

DUP-UI2-001: Tkinter initialization now uses shared tkinter_utils module.
"""
from __future__ import annotations

import json
import math
import os
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Tuple

import pygame
import pygame_gui

from game.core.logger import log_error, log_info
from game.ui.screens.formation.input_handler import FormationInputHandler
from game.ui.screens.formation.renderer import FormationRenderer
from game.ui.services.tkinter_utils import (
    is_tkinter_available,
    open_load_dialog,
    open_save_dialog,
)

if TYPE_CHECKING:
    from pygame import Rect, Surface

class FormationCore:
    """Core data model for formation editor, managing arrow positions and attributes."""

    arrows: List[List[float]]
    arrow_attrs: List[Dict[str, str]]
    selected_indices: Set[int]
    shape_count: int

    def __init__(self) -> None:
        # Data
        # list of [x, y] coordinates (World Space)
        self.arrows: List[List[float]] = []
        # Parallel list of attributes: [{'rotation_mode': 'relative'}, ...]
        self.arrow_attrs: List[Dict[str, str]] = []
        # Multi-selection: set of indices
        self.selected_indices: Set[int] = set()
        self.shape_count: int = 5

    def add_arrow(self, pos: Tuple[float, float]) -> None:
        """Add a new arrow at the given world position."""
        self.arrows.append(list(pos))
        self.arrow_attrs.append({'rotation_mode': 'relative'})
        self.selected_indices = {len(self.arrows) - 1}

    def move_arrow(self, from_idx: int, to_idx: int) -> None:
        """Move an arrow from one index to another in the list order."""
        if from_idx == to_idx: return
        # Adjust indices if needed to prevent OOB
        if from_idx < 0 or from_idx >= len(self.arrows): return
        if to_idx < 0: to_idx = 0
        if to_idx >= len(self.arrows): to_idx = len(self.arrows) - 1

        item = self.arrows.pop(from_idx)
        self.arrows.insert(to_idx, item)
        attr = self.arrow_attrs.pop(from_idx)
        self.arrow_attrs.insert(to_idx, attr)
        # Update selection to follow the item
        self.selected_indices = {to_idx}

    def delete_selected(self) -> None:
        """Delete all currently selected arrows."""
        if not self.selected_indices: return
        to_delete = sorted(list(self.selected_indices), reverse=True)
        for idx in to_delete:
            if 0 <= idx < len(self.arrows):
                self.arrows.pop(idx)
                self.arrow_attrs.pop(idx)
        self.selected_indices = set()

    def clone_selection(self, offset: float) -> None:
        """Clone selected arrows with an offset."""
        if not self.selected_indices: return
        sorted_indices = sorted(list(self.selected_indices))
        new_indices: Set[int] = set()
        for idx in sorted_indices:
            ax, ay = self.arrows[idx]
            self.arrows.append([ax + offset, ay + offset])
            self.arrow_attrs.append(self.arrow_attrs[idx].copy())
            new_indices.add(len(self.arrows) - 1)
        self.selected_indices = new_indices

    def clear_all(self) -> None:
        """Clear all arrows and selection."""
        self.arrows = []
        self.arrow_attrs = []
        self.selected_indices = set()

    def generate_shape(self, shape_type: str, center_pos: Tuple[float, float], radius: float = 200) -> None:
        # Use Core's shape_count
        count = self.shape_count
        cx, cy = center_pos
             
        new_indices = set()
        start_idx = len(self.arrows)
        
        if shape_type == 'circle':
            for i in range(count):
                angle = (2 * math.pi * i) / count
                angle -= math.pi / 2
                ax = cx + math.cos(angle) * radius
                ay = cy + math.sin(angle) * radius
                # Don't snap here, keep float precision
                self.arrows.append([ax, ay])
                self.arrow_attrs.append({'rotation_mode': 'relative'})
                new_indices.add(start_idx + i)

        elif shape_type == 'disc':
            # Use Phyllotaxis Spiral (Sunflower pattern) for even packing
            golden_angle = math.pi * (3 - math.sqrt(5))
            for i in range(count):
                if count > 1:
                    t = i / (count - 1)
                else: 
                    t = 0
                
                # Sqrt for area preservation (uniform density)
                r_dist = math.sqrt(t) * radius
                theta = i * golden_angle
                
                ax = cx + math.cos(theta) * r_dist
                ay = cy + math.sin(theta) * r_dist
                
                self.arrows.append([ax, ay])
                self.arrow_attrs.append({'rotation_mode': 'relative'})
                new_indices.add(start_idx + i)
                
        elif shape_type == 'x':
            arm1_count = count // 2
            arm2_count = count - arm1_count
            for i in range(arm1_count):
                t = i / max(1, arm1_count - 1)
                ax = cx - radius + (2*radius * t)
                ay = cy - radius + (2*radius * t)
                # Don't snap here
                self.arrows.append([ax, ay])
                self.arrow_attrs.append({'rotation_mode': 'relative'})
                new_indices.add(start_idx + i)
            for i in range(arm2_count):
                t = i / max(1, arm2_count - 1)
                ax = cx + radius - (2*radius * t)
                ay = cy - radius + (2*radius * t)
                # Don't snap here
                self.arrows.append([ax, ay])
                self.arrow_attrs.append({'rotation_mode': 'relative'})
                new_indices.add(start_idx + arm1_count + i)
                
        elif shape_type == 'line':
            width = radius * 2
            for i in range(count):
                t = i / max(1, count - 1)
                ax = cx - radius + (width * t)
                ay = cy
                # Don't snap here
                self.arrows.append([ax, ay])
                self.arrow_attrs.append({'rotation_mode': 'relative'})
                new_indices.add(start_idx + i)

        self.selected_indices = new_indices

    def toggle_rotation_mode(self) -> None:
        """Toggle rotation mode between 'relative' and 'fixed' for selected arrows."""
        if not self.selected_indices: return

        # Check current state of selection
        any_relative = False
        for idx in self.selected_indices:
            if self.arrow_attrs[idx].get('rotation_mode', 'relative') == 'relative':
                any_relative = True
                break

        new_mode = 'fixed' if any_relative else 'relative'
        for idx in self.selected_indices:
            self.arrow_attrs[idx]['rotation_mode'] = new_mode

    def save_to_file(self, filename: str) -> None:
        """Save formation to JSON file."""
        try:
            # Serialize to new format (List of Dicts) if mixed, or just Dicts
            out_arrows: List[Dict[str, Any]] = []
            for i, pos in enumerate(self.arrows):
                attr = self.arrow_attrs[i]
                # Format: {"pos": [x, y], "rotation_mode": "relative"}
                out_arrows.append({
                    "pos": pos,
                    "rotation_mode": attr.get('rotation_mode', 'relative')
                })

            data = {'arrows': out_arrows}
            with open(filename, 'w') as f: json.dump(data, f, indent=4)
            log_info(f"Formation saved to {filename}")
        except OSError as e:
            log_error(f"Error saving formation (file error): {e}")
        except (TypeError, ValueError) as e:
            log_error(f"Error saving formation (serialization error): {e}")

    def load_from_file(self, filename: str) -> None:
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                if 'arrows' in data:
                    raw_arrows = data['arrows']
                    self.arrows = []
                    self.arrow_attrs = []
                    for item in raw_arrows:
                        # PROJ-42 Phase 4: Removed legacy list format support
                        # Arrows must be dict format: {"pos": [x, y], "rotation_mode": "..."}
                        if not isinstance(item, dict):
                            raise ValueError(f"Arrow must be dict format, got {type(item).__name__}")
                        self.arrows.append(item.get('pos', [0, 0]))
                        self.arrow_attrs.append({'rotation_mode': item.get('rotation_mode', 'relative')})

                    self.selected_indices = set()
                    log_info(f"Formation loaded from {filename} ({len(self.arrows)} arrows)")
        except FileNotFoundError:
            log_error(f"Formation file not found: {filename}")
        except json.JSONDecodeError as e:
            log_error(f"Invalid JSON in formation file {filename}: {e}")
        except (KeyError, ValueError) as e:
            log_error(f"Invalid formation data in {filename}: {e}")
        except OSError as e:
            log_error(f"Error reading formation file {filename}: {e}")

class FormationEditorScreen:
    """Main UI screen for the formation editor with canvas, toolbar, and event handling.

    Delegates rendering to FormationRenderer and input state management to FormationInputHandler.
    """

    def __init__(self, screen_width: int, screen_height: int, on_return_menu: Callable[[], None]) -> None:
        self.width: int = screen_width
        self.height: int = screen_height
        self.on_return_menu: Callable[[], None] = on_return_menu

        # Layout
        self.toolbar_height = 80

        # Instantiate Core Model
        self.core = FormationCore()

        # Instantiate Renderer (handles drawing and coordinate transforms)
        self.renderer = FormationRenderer(screen_width, screen_height, self.toolbar_height)

        # Instantiate Input Handler (manages interaction state machine)
        self.input_handler = FormationInputHandler()

        # Settings (synced with renderer)
        self.shape_count = 5  # Default count for shape generation

        # Renumbering
        self.renumber_mode = False
        self.renumber_target = 1

        # UI Manager
        self.ui_manager = pygame_gui.UIManager((screen_width, screen_height))

        # Setup UI
        self._create_ui()

    def _create_ui(self):
        btn_y = self.height - 70
        btn_w = 110
        btn_h = 30
        spacing = 5
        start_x = 10
        
        # Top Row of Toolbar
        current_x = start_x
        
        self.clear_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, btn_w, btn_h),
            text="Clear All",
            manager=self.ui_manager
        )
        current_x += btn_w + spacing
        
        self.snap_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, btn_w, btn_h),
            text="Snap: ON",
            manager=self.ui_manager
        )
        current_x += btn_w + spacing

        self.clone_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, btn_w, btn_h),
            text="Clone Group",
            manager=self.ui_manager
        )
        current_x += btn_w + spacing
        
        self.delete_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, btn_w, btn_h),
            text="Delete",
            manager=self.ui_manager
        )
        current_x += btn_w + spacing
        
        self.save_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, btn_w, btn_h),
            text="Save",
            manager=self.ui_manager
        )
        current_x += btn_w + spacing
        
        self.load_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, btn_w, btn_h),
            text="Load",
            manager=self.ui_manager
        )
        current_x += btn_w + spacing
        
        self.rotation_mode_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, 140, btn_h),
            text="Rot: Relative",
            manager=self.ui_manager
        )
        current_x += 140 + spacing
        
        self.info_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(current_x, btn_y, 250, btn_h),
            text="Arrows: 0",
            manager=self.ui_manager
        )
        
        # Bottom Row of Toolbar (Shape generation)
        btn_y += 35
        current_x = start_x
        
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(current_x, btn_y, 80, btn_h),
            text="Shape Gen:",
            manager=self.ui_manager
        )
        current_x += 80 + spacing

        self.count_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(current_x, btn_y, 150, btn_h),
            start_value=5,
            value_range=(2, 50),
            manager=self.ui_manager
        )
        current_x += 150 + spacing
        
        self.count_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(current_x, btn_y, 50, btn_h),
            manager=self.ui_manager
        )
        self.count_entry.set_text("5")
        current_x += 50 + spacing
        
        self.circle_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, 80, btn_h),
            text="Circle",
            manager=self.ui_manager
        )
        current_x += 80 + spacing
        
        self.disc_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, 80, btn_h),
            text="Disc",
            manager=self.ui_manager
        )
        current_x += 80 + spacing
        
        self.x_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, 80, btn_h),
            text="X Shape",
            manager=self.ui_manager
        )
        current_x += 80 + spacing

        self.line_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, 80, btn_h),
            text="Line",
            manager=self.ui_manager
        )
        current_x += 80 + spacing

        # Renumber Controls
        self.renumber_mode_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(current_x, btn_y, 110, btn_h),
            text="Renumber: OFF",
            manager=self.ui_manager
        )
        current_x += 110 + spacing

        self.renumber_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(current_x, btn_y, 100, btn_h),
            start_value=1,
            value_range=(1, 50),
            manager=self.ui_manager
        )
        current_x += 100 + spacing
        
        self.renumber_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(current_x, btn_y, 40, btn_h),
            manager=self.ui_manager
        )
        self.renumber_entry.set_text("1")
        current_x += 40 + spacing

        self.return_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.width - 120, btn_y, 110, btn_h),
            text="Return",
            manager=self.ui_manager
        )

    @property
    def arrows(self) -> List[List[float]]:
        """List of arrow positions in world coordinates."""
        return self.core.arrows

    @property
    def arrow_attrs(self) -> List[Dict[str, str]]:
        """List of arrow attributes (rotation mode, etc.)."""
        return self.core.arrow_attrs

    @property
    def selected_indices(self) -> Set[int]:
        """Set of currently selected arrow indices."""
        return self.core.selected_indices

    @selected_indices.setter
    def selected_indices(self, val: Set[int]) -> None:
        self.core.selected_indices = val

    # --- Delegate properties to renderer ---
    @property
    def camera_zoom(self) -> float:
        """Camera zoom level."""
        return self.renderer.camera_zoom

    @camera_zoom.setter
    def camera_zoom(self, val: float) -> None:
        self.renderer.camera_zoom = val

    @property
    def camera_pan(self) -> List[float]:
        """Camera pan offset."""
        return self.renderer.camera_pan

    @camera_pan.setter
    def camera_pan(self, val: List[float]) -> None:
        self.renderer.camera_pan = val

    @property
    def grid_size(self) -> int:
        """Grid size for snapping."""
        return self.renderer.grid_size

    @grid_size.setter
    def grid_size(self, val: int) -> None:
        self.renderer.grid_size = val

    @property
    def snap_enabled(self) -> bool:
        """Whether snap to grid is enabled."""
        return self.renderer.snap_enabled

    @snap_enabled.setter
    def snap_enabled(self, val: bool) -> None:
        self.renderer.snap_enabled = val

    @property
    def show_grid(self) -> bool:
        """Whether to show the grid."""
        return self.renderer.show_grid

    @show_grid.setter
    def show_grid(self, val: bool) -> None:
        self.renderer.show_grid = val

    @property
    def canvas_rect(self) -> pygame.Rect:
        """Get the canvas drawing area."""
        return self.renderer.get_canvas_rect()

    @property
    def state(self) -> str:
        """Current interaction state."""
        return self.input_handler.state

    @state.setter
    def state(self, val: str) -> None:
        if val == 'IDLE':
            self.input_handler.reset_state()
        else:
            self.input_handler.state = val

    # --- Coordinate Transforms (delegate to renderer) ---
    def world_to_screen(self, wx: float, wy: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates."""
        return self.renderer.world_to_screen(wx, wy)

    def move_arrow(self, from_idx: int, to_idx: int) -> None:
        """Move an arrow from one list position to another."""
        self.core.move_arrow(from_idx, to_idx)
        self.update_info()

    def screen_to_world(self, sx: float, sy: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        return self.renderer.screen_to_world(sx, sy)

    def snap(self, val: float) -> float:
        """Snap value to grid if snap is enabled."""
        return self.renderer.snap(val)

    def get_selection_bounds(self) -> Optional[pygame.Rect]:
        """Get bounding rectangle of selected arrows, or None if no selection."""
        return self.renderer.get_selection_bounds(self.arrows, self.selected_indices)

    def get_resize_handles(self, bounds_rect: Optional[pygame.Rect]) -> Dict[str, pygame.Rect]:
        """Get resize handle rectangles for selection bounds."""
        return self.renderer.get_resize_handles(bounds_rect)

    # --- Interaction ---
    def handle_event(self, event: pygame.event.Event) -> None:
        """Process pygame events for the formation editor."""
        self.ui_manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button_pressed(event)

        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            self._handle_slider_moved(event)

        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            self._handle_text_entry(event)

        elif event.type == pygame.MOUSEWHEEL:
            self._handle_mousewheel(event)

        elif event.type == pygame.KEYDOWN:
            self._handle_keydown(event)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_button_down(event)

        elif event.type == pygame.MOUSEBUTTONUP:
            self._handle_mouse_button_up(event)

        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)

    def _handle_left_down(self, screen_pos):
        wx, wy = self.screen_to_world(screen_pos[0], screen_pos[1])
        clicked_idx = self._get_arrow_at(wx, wy)
        
        # Renumber Mode Handling
        if self.renumber_mode and clicked_idx is not None:
             # Move clicked arrow to target position
             target_idx = self.renumber_target - 1 # 1-based to 0-based
             # Clamp target
             target_idx = max(0, min(len(self.arrows)-1, target_idx))
             self.move_arrow(clicked_idx, target_idx)
             return # Swallow event
             
        keys = pygame.key.get_pressed()
        shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        bounds = self.get_selection_bounds()
        if bounds:
            handles = self.get_resize_handles(bounds)
            for name, rect in handles.items():
                if rect.collidepoint(screen_pos):
                    self.input_handler.start_resizing_group(
                        handle_name=name,
                        bounds=bounds,
                        arrows=self.arrows,
                        selected=self.selected_indices,
                        screen_pos=screen_pos,
                        grid_size=self.grid_size
                    )
                    return
        
        # Re-fetch index if handle check failed (it might have been cleared by early return above, but safe to fetch again)
        # Actually logic flow: if handle clicked, we return. 
        # So hereafter, either we clicked arrow or blank.
        
        if clicked_idx is not None:
            if shift:
                if clicked_idx in self.selected_indices:
                    self.selected_indices.remove(clicked_idx)
                else:
                    self.selected_indices.add(clicked_idx)
            else:
                if clicked_idx not in self.selected_indices:
                    self.selected_indices = {clicked_idx}

            if self.selected_indices:
                self.input_handler.start_dragging_items(
                    (wx, wy), self.arrows, self.selected_indices
                )
            return
        
        # Clicked Blank Space
        # If selection exists and no handle/arrow clicked, we first check if it's a drag or click in mouse_up.
        # But if user just wants to deselect, logic happens later.
        self.input_handler.start_potential_click(screen_pos, (wx, wy))

    def _check_renumber_arrows(self, screen_pos, idx):
        """Check if click is on up/down reorder arrows for single selection."""
        up_rect, down_rect = self.renderer.get_renumber_arrow_rects(
            self.arrows, {idx}
        )

        if up_rect and up_rect.collidepoint(screen_pos):
            return 'up'
        if down_rect and down_rect.collidepoint(screen_pos):
            return 'down'
        return None

    def _handle_mouse_motion(self, screen_pos):
        if self.state == 'PANNING':
            new_pan = self.input_handler.calculate_pan_delta(screen_pos)
            self.camera_pan[0] = new_pan[0]
            self.camera_pan[1] = new_pan[1]

        elif self.state == 'DRAGGING_ITEMS':
            wx, wy = self.screen_to_world(screen_pos[0], screen_pos[1])
            new_positions = self.input_handler.calculate_new_positions(
                (wx, wy), snap_func=self.snap
            )
            for idx, pos in new_positions.items():
                self.arrows[idx] = pos

        elif self.state == 'RESIZING_GROUP':
            self._update_group_resize(screen_pos)

        elif self.state == 'POTENTIAL_CLICK':
            if self.input_handler.should_transition_to_box_select(screen_pos):
                self.input_handler.start_box_select(
                    self.input_handler.drag_start_screen,
                    self.input_handler.drag_start_world
                )
                keys = pygame.key.get_pressed()
                if not (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
                    self.selected_indices = set()
                     
    def _handle_mousewheel(self, event: pygame.event.Event) -> None:
        """Handle MOUSEWHEEL events for zooming."""
        if event.y > 0:
            self.camera_zoom *= 1.1
        elif event.y < 0:
            self.camera_zoom /= 1.1

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle KEYDOWN events."""
        if event.key == pygame.K_SPACE:
            mx, my = pygame.mouse.get_pos()
            if self.canvas_rect.collidepoint((mx, my)):
                wx, wy = self.screen_to_world(mx, my)
                if self.snap_enabled:
                    wx = self.snap(wx)
                    wy = self.snap(wy)
                self.add_arrow((wx, wy))

    def _handle_mouse_button_up(self, event: pygame.event.Event) -> None:
        """Handle MOUSEBUTTONUP events."""
        if event.button == 1:
            self._handle_left_up(event.pos)
        elif event.button == 3:
            if self.state == 'PANNING':
                self.state = 'IDLE'

    def _handle_slider_moved(self, event: pygame.event.Event) -> None:
        """Handle UI_HORIZONTAL_SLIDER_MOVED events."""
        if event.ui_element == self.count_slider:
            val = int(event.value)
            self.shape_count = val
            self.core.shape_count = val
            self.count_entry.set_text(str(val))
        elif event.ui_element == self.renumber_slider:
            val = int(event.value)
            self.renumber_target = val
            self.renumber_entry.set_text(str(val))

    def _handle_text_entry(self, event: pygame.event.Event) -> None:
        """Handle UI_TEXT_ENTRY_FINISHED events."""
        if event.ui_element == self.count_entry:
            try:
                val = int(event.text)
                val = max(2, min(100, val))
                self.shape_count = val
                self.core.shape_count = val
                self.count_slider.set_current_value(val)
            except ValueError:
                self.count_entry.set_text(str(self.shape_count))
        elif event.ui_element == self.renumber_entry:
            try:
                val = int(event.text)
                val = max(1, min(len(self.arrows), val))
                self.renumber_target = val
                self.renumber_slider.set_current_value(val)
            except ValueError:
                self.renumber_entry.set_text(str(self.renumber_target))

    def _handle_mouse_button_down(self, event: pygame.event.Event) -> None:
        """Handle MOUSEBUTTONDOWN events on the canvas."""
        if not self.canvas_rect.collidepoint(event.pos):
            return

        # Check Up/Down Arrow Clicks first (Screen Space UI)
        if len(self.selected_indices) == 1:
            idx = list(self.selected_indices)[0]
            res = self._check_renumber_arrows(event.pos, idx)
            if res == 'up':  # Decrease Index (Move to 1)
                self.move_arrow(idx, max(0, idx - 1))
                return
            elif res == 'down':  # Increment Index (Move to End)
                self.move_arrow(idx, min(len(self.arrows) - 1, idx + 1))
                return

        if event.button == 3:  # Right click -> Pan
            self.input_handler.start_panning(event.pos, self.camera_pan)
        elif event.button == 1:  # Left click
            self._handle_left_down(event.pos)

    def _handle_button_pressed(self, event: pygame.event.Event) -> None:
        """Handle UI_BUTTON_PRESSED events."""
        if event.ui_element == self.snap_btn:
            self.snap_enabled = not self.snap_enabled
            self.snap_btn.set_text(f"Snap: {'ON' if self.snap_enabled else 'OFF'}")
        elif event.ui_element == self.clone_btn:
            self.clone_selection()
        elif event.ui_element == self.delete_btn:
            self.delete_selected()
        elif event.ui_element == self.save_btn:
            self.save_formation()
        elif event.ui_element == self.load_btn:
            self.load_formation()
        elif event.ui_element == self.rotation_mode_btn:
            self._toggle_rotation_mode()
        elif event.ui_element == self.return_btn:
            self.on_return_menu()
        elif event.ui_element == self.clear_btn:
            self.clear_all()
        elif event.ui_element == self.circle_btn:
            self.generate_shape('circle')
        elif event.ui_element == self.disc_btn:
            self.generate_shape('disc')
        elif event.ui_element == self.x_btn:
            self.generate_shape('x')
        elif event.ui_element == self.line_btn:
            self.generate_shape('line')
        elif event.ui_element == self.renumber_mode_btn:
            self.renumber_mode = not self.renumber_mode
            self.renumber_mode_btn.set_text(f"Renumber: {'ON' if self.renumber_mode else 'OFF'}")
            if self.renumber_mode:
                self.state = 'IDLE'

    def _toggle_rotation_mode(self):
        self.core.toggle_rotation_mode()
        self.update_info()

    def _update_group_resize(self, screen_pos):
        """Update arrow positions during group resize using input handler."""
        new_positions = self.input_handler.calculate_resize_positions(
            screen_pos=screen_pos,
            screen_to_world=self.screen_to_world,
            snap_func=self.snap,
            grid_size=self.grid_size
        )
        # Do NOT snap here to preserve floating point relative positions during scaling
        # Visual snapping happens in draw()
        for idx, pos in new_positions.items():
            self.arrows[idx] = pos

    def _handle_left_up(self, screen_pos):
        if self.state == 'POTENTIAL_CLICK':
            # This was a click (no drag)
            keys = pygame.key.get_pressed()
            shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

            if self.selected_indices and not shift:
                self.selected_indices = set()

            self.input_handler.reset_state()

        elif self.state == 'BOX_SELECT':
            keys = pygame.key.get_pressed()
            shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

            new_selection = self.input_handler.find_arrows_in_box(
                screen_pos, self.arrows, self.screen_to_world
            )
            if shift:
                self.selected_indices.update(new_selection)
            else:
                self.selected_indices = new_selection

            self.input_handler.reset_state()
        else:
            self.input_handler.reset_state()

        self.update_info()

    def _get_arrow_at(self, wx, wy):
        """Find arrow at given world position."""
        return self.input_handler.get_arrow_at(
            (wx, wy), self.arrows, self.world_to_screen, click_radius=25
        )

    def add_arrow(self, pos: Tuple[float, float]) -> None:
        """Add a new arrow at the given world position."""
        self.core.add_arrow(pos)
        self.update_info()

    def delete_selected(self) -> None:
        """Delete all selected arrows."""
        self.core.delete_selected()
        self.update_info()

    def clone_selection(self) -> None:
        """Clone selected arrows with offset based on grid settings."""
        offset = self.grid_size if self.snap_enabled else 20
        self.core.clone_selection(offset)
        self.update_info()

    def clear_all(self) -> None:
        """Clear all arrows from the formation."""
        self.core.clear_all()
        self.update_info()

    def generate_shape(self, shape_type: str) -> None:
        """Generate arrows in a predefined shape pattern."""
        cx, cy = self.screen_to_world(self.width/2, (self.height - self.toolbar_height)/2)
        if self.snap_enabled:
             cx = self.snap(cx)
             cy = self.snap(cy)

        self.core.shape_count = self.shape_count
        self.core.generate_shape(shape_type, (cx, cy))
        self.update_info()

    def save_formation(self) -> None:
        """Save formation to file via dialog."""
        if not is_tkinter_available():
            return
        base_path = os.path.dirname(os.path.abspath(__file__))
        initial_dir = os.path.join(base_path, "data", "formations")
        if not os.path.exists(initial_dir):
            os.makedirs(initial_dir)

        filename = open_save_dialog(
            initialdir=initial_dir,
            initialfile="formation.json",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Save Formation"
        )
        if filename:
            self.core.save_to_file(filename)

    def load_formation(self) -> None:
        """Load formation from file via dialog."""
        if not is_tkinter_available():
            return
        base_path = os.path.dirname(os.path.abspath(__file__))
        initial_dir = os.path.join(base_path, "data", "formations")
        if not os.path.exists(initial_dir):
            os.makedirs(initial_dir)

        filename = open_load_dialog(
            initialdir=initial_dir,
            filetypes=[("JSON Files", "*.json")],
            title="Load Formation"
        )
        if filename:
            self.core.load_from_file(filename)
            self.update_info()

    def update_info(self) -> None:
        """Update the UI info label to reflect current arrow count and selection."""
        count = len(self.arrows)
        sel_count = len(self.selected_indices)
        sel_str = f" | Selected: {sel_count}" if sel_count > 0 else ""
        self.info_label.set_text(f"Arrows: {count}{sel_str}")
        
        # Update Rotation Btn text based on selection
        if hasattr(self, 'rotation_mode_btn'):
            if not self.selected_indices:
                self.rotation_mode_btn.set_text("Rot: -")
                self.rotation_mode_btn.disable()
            else:
                self.rotation_mode_btn.enable()
                # Check consistency
                modes = set()
                for idx in self.selected_indices:
                    modes.add(self.arrow_attrs[idx].get('rotation_mode', 'relative'))
                
                if len(modes) > 1:
                    self.rotation_mode_btn.set_text("Rot: Mixed")
                elif 'fixed' in modes:
                    self.rotation_mode_btn.set_text("Rot: Fixed")
                else:
                    self.rotation_mode_btn.set_text("Rot: Relative")
        
        # Manually update slider range if possible, or just clamp input
        if hasattr(self, 'renumber_slider'):
             # Pygame_gui doesn't easy exposure of range adjustment without rebuilding, 
             # but we can try setting the value range directly if accessible, or rebuild.
             # Rebuilding is expensive in update loop.
             # Let's just assume 50 is enough or create it with dynamic max if we rebuild whole UI.
             pass

    def update(self, dt: float) -> None:
        """Update UI manager and animations."""
        self.ui_manager.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the formation editor canvas and UI.

        Delegates to FormationRenderer for all drawing operations.
        """
        self.renderer.draw(
            screen=screen,
            arrows=self.arrows,
            arrow_attrs=self.arrow_attrs,
            selected_indices=self.selected_indices,
            state=self.state,
            drag_start_screen=self.input_handler.drag_start_screen
        )
        self.ui_manager.draw_ui(screen)

    def handle_resize(self, w: int, h: int) -> None:
        """Handle window resize by updating dimensions and rebuilding UI."""
        self.width = w
        self.height = h
        self.renderer.handle_resize(w, h)
        self.ui_manager.set_window_resolution((w, h))
        self.ui_manager.clear_and_reset()
        self._create_ui()
