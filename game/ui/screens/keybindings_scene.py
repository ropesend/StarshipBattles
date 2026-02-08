"""
KeybindingsScene - Full-screen keybinding editor (PROJ-71 Phase 4).

Provides a settings screen where the player can:
- View all bindable actions grouped by context
- Rebind any action by clicking Rebind and pressing a key
- Detect and resolve key conflicts
- Save overrides to disk or reset to defaults
- Close with unsaved-changes confirmation

Implements the IScene protocol (handle_event, update, draw, handle_resize).
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UIPanel
from pygame_gui.windows import UIConfirmationDialog

from game.core.input_actions import (
    ACTION_DISPLAY_NAMES,
    ACTION_GROUPS,
    InputAction,
    KeyBinding,
)
from game.core.input_mapper import InputMapper
from game.core.logger import log_debug, log_info

# ── Layout constants ────────────────────────────────────────────────
_TITLE_HEIGHT = 60
_FOOTER_HEIGHT = 60
_ROW_HEIGHT = 36
_GROUP_HEADER_HEIGHT = 32
_GROUP_GAP = 8
_COL_ACTION_W = 280
_COL_BINDING_W = 160
_COL_REBIND_W = 90
_COL_RESET_W = 70
_ROW_PADDING = 10

# Modifier-only pygame key constants (ignored during capture)
_MODIFIER_KEYS = frozenset({
    pygame.K_LSHIFT, pygame.K_RSHIFT,
    pygame.K_LCTRL, pygame.K_RCTRL,
    pygame.K_LALT, pygame.K_RALT,
})

# Reverse map: pygame key int -> key name string (e.g., 109 -> "K_m")
_PYGAME_KEY_NAMES: Dict[int, str] = {}


def _build_key_name_map() -> None:
    """Build a reverse lookup from pygame key constants to their names."""
    if _PYGAME_KEY_NAMES:
        return
    for attr in dir(pygame):
        if attr.startswith("K_") and isinstance(getattr(pygame, attr), int):
            _PYGAME_KEY_NAMES[getattr(pygame, attr)] = attr


class KeybindingsScene:
    """Full-screen keybinding editor implementing IScene.

    Attributes:
        _width: Current scene width in pixels.
        _height: Current scene height in pixels.
        _mapper: The InputMapper providing binding data.
        _on_close_callback: Called when the scene should close.
    """

    def __init__(
        self,
        width: int,
        height: int,
        input_mapper: InputMapper,
        on_close_callback: Callable[[], None],
    ) -> None:
        _build_key_name_map()

        self._width = width
        self._height = height
        self._mapper = input_mapper
        self._on_close_callback = on_close_callback

        # State
        self._has_unsaved_changes = False
        self._capturing_action: Optional[InputAction] = None
        self._pending_conflict: Optional[Dict[str, Any]] = None
        self._pending_discard = False
        self._pending_reset_all = False

        # UI manager
        self._ui_manager = pygame_gui.UIManager((width, height))

        # Row data indexed by action / group name
        self._action_rows: Dict[InputAction, Dict[str, Any]] = {}
        self._group_rows: Dict[str, Any] = {}

        # UI element lists for teardown
        self._ui_elements: List[Any] = []

        self._build_ui()

    # ────────────────────────────────────────────────────────────────
    # UI construction
    # ────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        """Create all UI elements (title, scrollable action list, footer)."""
        self._clear_ui()

        # Title
        title_rect = pygame.Rect(0, 0, self._width, _TITLE_HEIGHT)
        title = UILabel(
            relative_rect=title_rect,
            text="Keybindings",
            manager=self._ui_manager,
        )
        self._ui_elements.append(title)

        # Content area (between title and footer)
        content_top = _TITLE_HEIGHT
        content_height = self._height - _TITLE_HEIGHT - _FOOTER_HEIGHT

        # Build rows inside a panel (acts as scrollable container visually)
        self._build_action_rows(content_top, content_height)

        # Footer buttons
        self._build_footer()

    def _build_action_rows(self, top: int, max_height: int) -> None:
        """Populate action rows grouped by context."""
        y = top + _GROUP_GAP
        content_left = max(0, (self._width - (_COL_ACTION_W + _COL_BINDING_W + _COL_REBIND_W + _COL_RESET_W + _ROW_PADDING * 4)) // 2)

        for group_name, actions in ACTION_GROUPS.items():
            # Group header
            header_rect = pygame.Rect(content_left, y, _COL_ACTION_W + _COL_BINDING_W + _COL_REBIND_W + _COL_RESET_W + _ROW_PADDING * 3, _GROUP_HEADER_HEIGHT)
            header = UILabel(
                relative_rect=header_rect,
                text=f"  {group_name}",
                manager=self._ui_manager,
            )
            self._ui_elements.append(header)
            self._group_rows[group_name] = {"label": header}
            y += _GROUP_HEADER_HEIGHT

            for action in actions:
                self._build_action_row(action, content_left, y)
                y += _ROW_HEIGHT

            y += _GROUP_GAP

    def _build_action_row(self, action: InputAction, x: int, y: int) -> None:
        """Build one row: [Action Name] [Binding] [Rebind] [Reset]."""
        display_name = ACTION_DISPLAY_NAMES.get(action, action.value)
        binding = self._mapper.get_binding(action)
        binding_text = binding.display_text() if binding else "Unbound"

        cx = x

        # Action name label
        name_label = UILabel(
            relative_rect=pygame.Rect(cx, y, _COL_ACTION_W, _ROW_HEIGHT),
            text=f"  {display_name}",
            manager=self._ui_manager,
        )
        self._ui_elements.append(name_label)
        cx += _COL_ACTION_W + _ROW_PADDING

        # Binding display label
        binding_label = UILabel(
            relative_rect=pygame.Rect(cx, y, _COL_BINDING_W, _ROW_HEIGHT),
            text=binding_text,
            manager=self._ui_manager,
        )
        self._ui_elements.append(binding_label)
        cx += _COL_BINDING_W + _ROW_PADDING

        # Rebind button
        rebind_btn = UIButton(
            relative_rect=pygame.Rect(cx, y, _COL_REBIND_W, _ROW_HEIGHT),
            text="Rebind",
            manager=self._ui_manager,
        )
        self._ui_elements.append(rebind_btn)
        cx += _COL_REBIND_W + _ROW_PADDING

        # Reset button (only if non-default)
        reset_btn = UIButton(
            relative_rect=pygame.Rect(cx, y, _COL_RESET_W, _ROW_HEIGHT),
            text="Reset",
            manager=self._ui_manager,
        )
        self._ui_elements.append(reset_btn)

        # Check if binding matches default
        default_binding = self._mapper._defaults.get(action)
        if binding == default_binding:
            reset_btn.hide()

        self._action_rows[action] = {
            "name_label": name_label,
            "binding_label": binding_label,
            "binding_text": binding_text,
            "rebind_btn": rebind_btn,
            "reset_btn": reset_btn,
        }

    def _build_footer(self) -> None:
        """Create footer buttons: [Save & Close] [Reset All] [Close]."""
        btn_w = 140
        btn_h = 40
        spacing = 20
        total_w = btn_w * 3 + spacing * 2
        start_x = (self._width - total_w) // 2
        y = self._height - _FOOTER_HEIGHT + (_FOOTER_HEIGHT - btn_h) // 2

        self._btn_save_close = UIButton(
            relative_rect=pygame.Rect(start_x, y, btn_w, btn_h),
            text="Save & Close",
            manager=self._ui_manager,
        )
        self._ui_elements.append(self._btn_save_close)

        self._btn_reset_all = UIButton(
            relative_rect=pygame.Rect(start_x + btn_w + spacing, y, btn_w, btn_h),
            text="Reset All",
            manager=self._ui_manager,
        )
        self._ui_elements.append(self._btn_reset_all)

        self._btn_close = UIButton(
            relative_rect=pygame.Rect(start_x + 2 * (btn_w + spacing), y, btn_w, btn_h),
            text="Close",
            manager=self._ui_manager,
        )
        self._ui_elements.append(self._btn_close)

    def _clear_ui(self) -> None:
        """Kill all managed UI elements."""
        for elem in self._ui_elements:
            elem.kill()
        self._ui_elements.clear()
        self._action_rows.clear()
        self._group_rows.clear()

    # ────────────────────────────────────────────────────────────────
    # IScene protocol
    # ────────────────────────────────────────────────────────────────

    def handle_event(self, event: Any) -> None:
        """Handle a pygame event."""
        # Key capture intercepts all key events first
        if self._capturing_action is not None:
            if event.type == pygame.KEYDOWN:
                self._handle_key_capture(event)
                return

        # Confirmation dialog events
        if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            self._handle_dialog_confirmed(event)
            return

        # Let pygame_gui process the event
        self._ui_manager.process_events(event)

        # Button clicks
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button_press(event)

    def update(self, dt: float) -> None:
        """Update UI manager."""
        self._ui_manager.update(dt)

    def draw(self, screen: Any) -> None:
        """Draw the scene."""
        screen.fill((20, 25, 35))

        # Draw UI elements
        self._ui_manager.draw_ui(screen)

        # Draw capture overlay if active
        if self._capturing_action is not None:
            self._draw_capture_overlay(screen)

    def handle_resize(self, width: int, height: int) -> None:
        """Handle window resize."""
        self._width = width
        self._height = height
        self._ui_manager = pygame_gui.UIManager((width, height))
        self._build_ui()

    # ────────────────────────────────────────────────────────────────
    # Key capture
    # ────────────────────────────────────────────────────────────────

    def _start_capture(self, action: InputAction) -> None:
        """Enter key capture mode for the given action."""
        self._capturing_action = action
        log_debug(f"KeybindingsScene: Capturing key for {action.value}")

    def _handle_key_capture(self, event: Any) -> None:
        """Process a KEYDOWN event during capture mode."""
        key = event.key

        # ESC cancels capture
        if key == pygame.K_ESCAPE:
            self._capturing_action = None
            return

        # Ignore modifier-only presses
        if key in _MODIFIER_KEYS:
            return

        # Build KeyBinding from the pressed key
        key_name = _PYGAME_KEY_NAMES.get(key)
        if key_name is None:
            self._capturing_action = None
            return

        modifiers = InputMapper._extract_modifiers(event.mod)
        new_binding = KeyBinding(key=key_name, modifiers=modifiers)

        action = self._capturing_action
        action_context = action.value.split(".")[0]

        # Check for conflicts (exclude the action being rebound)
        conflicts = self._mapper.get_conflicts(new_binding, action_context)
        conflicts = [c for c in conflicts if c != action]

        if conflicts:
            # Store pending conflict for confirmation dialog
            self._pending_conflict = {
                "action": action,
                "binding": new_binding,
                "conflicts": conflicts,
            }
            self._capturing_action = None
            # Show confirmation dialog
            conflict_names = ", ".join(
                ACTION_DISPLAY_NAMES.get(c, c.value) for c in conflicts
            )
            self._conflict_dialog = UIConfirmationDialog(
                rect=pygame.Rect(
                    (self._width - 400) // 2,
                    (self._height - 200) // 2,
                    400, 200,
                ),
                manager=self._ui_manager,
                action_long_desc=(
                    f"'{new_binding.display_text()}' is already bound to: "
                    f"{conflict_names}. Reassign?"
                ),
                window_title="Key Conflict",
            )
        else:
            # No conflict: apply immediately
            self._apply_binding(action, new_binding)
            self._capturing_action = None

    def _apply_binding(
        self,
        action: InputAction,
        binding: KeyBinding,
        clear_conflicts: Optional[List[InputAction]] = None,
    ) -> None:
        """Apply a new binding to the mapper and update display."""
        # Clear conflicting bindings if requested
        if clear_conflicts:
            for conflict_action in clear_conflicts:
                self._mapper.set_binding(conflict_action, None)
                self._refresh_action_row(conflict_action)

        self._mapper.set_binding(action, binding)
        self._has_unsaved_changes = True
        self._refresh_action_row(action)
        log_debug(f"KeybindingsScene: Bound {action.value} -> {binding.display_text()}")

    def _refresh_action_row(self, action: InputAction) -> None:
        """Update the display for a single action row."""
        if action not in self._action_rows:
            return

        row = self._action_rows[action]
        binding = self._mapper.get_binding(action)
        binding_text = binding.display_text() if binding else "Unbound"
        row["binding_text"] = binding_text
        row["binding_label"].set_text(binding_text)

        # Show/hide reset button based on whether binding matches default
        default_binding = self._mapper._defaults.get(action)
        current_binding = self._mapper.get_binding(action)
        if current_binding == default_binding:
            row["reset_btn"].hide()
        else:
            row["reset_btn"].show()

    def _draw_capture_overlay(self, screen: Any) -> None:
        """Draw the semi-transparent capture overlay."""
        overlay = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        action_name = ACTION_DISPLAY_NAMES.get(self._capturing_action, self._capturing_action.value)
        font = pygame.font.SysFont("arial", 28)
        text = font.render(
            f"Press a key for '{action_name}'...  (ESC to cancel)",
            True, (255, 255, 255),
        )
        text_rect = text.get_rect(center=(self._width // 2, self._height // 2))
        screen.blit(text, text_rect)

    # ────────────────────────────────────────────────────────────────
    # Button handlers
    # ────────────────────────────────────────────────────────────────

    def _handle_button_press(self, event: Any) -> None:
        """Route button press events to the correct handler."""
        btn = event.ui_element

        # Footer buttons
        if btn == self._btn_save_close:
            self._on_save_and_close()
            return
        if btn == self._btn_reset_all:
            self._on_reset_all_clicked()
            return
        if btn == self._btn_close:
            self._on_close()
            return

        # Per-row rebind / reset buttons
        for action, row in self._action_rows.items():
            if btn == row["rebind_btn"]:
                self._start_capture(action)
                return
            if btn == row["reset_btn"]:
                self._reset_single_action(action)
                return

    def _handle_dialog_confirmed(self, event: Any) -> None:
        """Handle confirmation dialog result."""
        if self._pending_conflict:
            conflict_data = self._pending_conflict
            self._pending_conflict = None
            self._apply_binding(
                conflict_data["action"],
                conflict_data["binding"],
                clear_conflicts=conflict_data["conflicts"],
            )
        elif self._pending_reset_all:
            self._pending_reset_all = False
            self._on_reset_confirmed()
        elif self._pending_discard:
            self._pending_discard = False
            self._mapper.reset_to_defaults()
            # Reload from files so the mapper restores its actual state
            from game.core.paths import Paths
            self._mapper.load(Paths.DEFAULT_KEYBINDINGS_FILE, Paths.USER_KEYBINDINGS_FILE)
            self._on_close_callback()

    # ────────────────────────────────────────────────────────────────
    # Save / Reset / Close
    # ────────────────────────────────────────────────────────────────

    def _on_save_and_close(self) -> None:
        """Save user overrides and close."""
        self._mapper.save_user_overrides()
        self._has_unsaved_changes = False
        log_info("KeybindingsScene: Saved user keybinding overrides")
        self._on_close_callback()

    def _on_reset_all_clicked(self) -> None:
        """Show confirmation for reset all."""
        self._pending_reset_all = True
        self._reset_dialog = UIConfirmationDialog(
            rect=pygame.Rect(
                (self._width - 400) // 2,
                (self._height - 200) // 2,
                400, 200,
            ),
            manager=self._ui_manager,
            action_long_desc="Reset all keybindings to their default values?",
            window_title="Reset All",
        )

    def _on_reset_confirmed(self) -> None:
        """Execute reset all to defaults."""
        self._mapper.reset_to_defaults()
        self._has_unsaved_changes = False
        self._refresh_all_rows()
        log_info("KeybindingsScene: Reset all keybindings to defaults")

    def _on_close(self) -> None:
        """Close with unsaved-changes guard."""
        if self._has_unsaved_changes:
            self._pending_discard = True
            self._discard_dialog = UIConfirmationDialog(
                rect=pygame.Rect(
                    (self._width - 400) // 2,
                    (self._height - 200) // 2,
                    400, 200,
                ),
                manager=self._ui_manager,
                action_long_desc="You have unsaved changes. Discard them?",
                window_title="Unsaved Changes",
            )
        else:
            self._on_close_callback()

    def _reset_single_action(self, action: InputAction) -> None:
        """Reset a single action to its default binding."""
        default_binding = self._mapper._defaults.get(action)
        self._mapper.set_binding(action, default_binding)
        self._has_unsaved_changes = True
        self._refresh_action_row(action)
        log_debug(f"KeybindingsScene: Reset {action.value} to default")

    def _refresh_all_rows(self) -> None:
        """Refresh every action row's display text and reset button."""
        for action in self._action_rows:
            self._refresh_action_row(action)
