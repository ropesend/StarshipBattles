"""
ResearchControlPanel - Sidebar UI for the research tree scene.

Contains:
- Node detail panel (when a node is selected)
- RP allocation slider
- RP budget configuration
- Turn controls (Next Turn, Reset)
- Event log
"""
import pygame
import pygame_gui
from pygame_gui.elements import (
    UIPanel, UILabel, UIButton, UIHorizontalSlider,
    UITextBox, UITextEntryLine
)
from typing import Callable, Optional, List, Dict, Any

from game.research.data.tech_node import TechNode
from game.research.data.tech_tree import TechTree
from game.research.data.research_tracker import ResearchTracker


class ResearchControlPanel:
    """
    Control panel for the research tree scene.

    Manages all sidebar UI elements and their interactions.
    """

    def __init__(self, rect: pygame.Rect, manager: pygame_gui.UIManager,
                 tracker: ResearchTracker, tech_tree: TechTree,
                 on_next_turn: Callable, on_close: Callable, on_reset: Callable,
                 on_auto_spread_changed: Callable = None):
        """
        Initialize the control panel.

        Args:
            rect: Rectangle for the panel area
            manager: pygame_gui UI manager
            tracker: Research tracker instance
            tech_tree: Tech tree for auto-spread calculations
            on_next_turn: Callback for Next Turn button
            on_close: Callback for Close button
            on_reset: Callback for Reset button
            on_auto_spread_changed: Callback when auto-spread is toggled
        """
        self.rect = rect
        self.manager = manager
        self.tracker = tracker
        self.tech_tree = tech_tree
        self.on_next_turn = on_next_turn
        self.on_close = on_close
        self.on_reset = on_reset
        self.on_auto_spread_changed = on_auto_spread_changed

        self._selected_node: Optional[TechNode] = None

        self._create_ui()

    def _create_ui(self):
        """Create all UI elements."""
        x = self.rect.left + 10
        width = self.rect.width - 20
        y = 10

        # --- Turn Info Section ---
        self.lbl_turn = UILabel(
            relative_rect=pygame.Rect(x, y, width, 25),
            text=f"Turn: {self.tracker.turn_number}",
            manager=self.manager
        )
        y += 30

        # --- RP Budget Section ---
        UILabel(
            relative_rect=pygame.Rect(x, y, width, 20),
            text="RP Budget per Turn:",
            manager=self.manager
        )
        y += 22

        self.slider_budget = UIHorizontalSlider(
            relative_rect=pygame.Rect(x, y, width - 60, 25),
            start_value=self.tracker.rp_budget,
            value_range=(ResearchTracker.MIN_RP_BUDGET, ResearchTracker.MAX_RP_BUDGET),
            manager=self.manager
        )
        self.lbl_budget_value = UILabel(
            relative_rect=pygame.Rect(x + width - 55, y, 55, 25),
            text=str(self.tracker.rp_budget),
            manager=self.manager
        )
        y += 30

        # Allocated / Remaining
        self.lbl_allocated = UILabel(
            relative_rect=pygame.Rect(x, y, width, 20),
            text=f"Allocated: {self.tracker.get_total_allocated()} / {self.tracker.rp_budget}",
            manager=self.manager
        )
        y += 25

        # Auto-Spread toggle button
        self.btn_auto_spread = UIButton(
            relative_rect=pygame.Rect(x, y, width, 30),
            text="Auto-Spread: OFF",
            manager=self.manager
        )
        y += 35

        # Separator
        y += 5

        # --- Node Detail Section ---
        UILabel(
            relative_rect=pygame.Rect(x, y, width, 20),
            text="Selected Node:",
            manager=self.manager
        )
        y += 22

        self.lbl_node_name = UILabel(
            relative_rect=pygame.Rect(x, y, width, 25),
            text="(None)",
            manager=self.manager
        )
        y += 28

        self.lbl_node_level = UILabel(
            relative_rect=pygame.Rect(x, y, width, 20),
            text="Level: -",
            manager=self.manager
        )
        y += 22

        self.lbl_node_chance = UILabel(
            relative_rect=pygame.Rect(x, y, width, 20),
            text="Chance: -",
            manager=self.manager
        )
        y += 22

        self.lbl_node_decay = UILabel(
            relative_rect=pygame.Rect(x, y, width, 20),
            text="Decay: -",
            manager=self.manager
        )
        y += 22

        self.lbl_node_volatility = UILabel(
            relative_rect=pygame.Rect(x, y, width, 20),
            text="Volatility: -",
            manager=self.manager
        )
        y += 22

        self.lbl_node_price = UILabel(
            relative_rect=pygame.Rect(x, y, width, 20),
            text="Price: -",
            manager=self.manager
        )
        y += 22

        self.lbl_node_status = UILabel(
            relative_rect=pygame.Rect(x, y, width, 20),
            text="Status: -",
            manager=self.manager
        )
        y += 30

        # --- RP Allocation for Selected Node ---
        UILabel(
            relative_rect=pygame.Rect(x, y, width, 20),
            text="RP Allocation:",
            manager=self.manager
        )
        y += 22

        self.slider_allocation = UIHorizontalSlider(
            relative_rect=pygame.Rect(x, y, width - 60, 25),
            start_value=0,
            value_range=(0, self.tracker.rp_budget),
            manager=self.manager
        )
        self.slider_allocation.disable()

        self.lbl_allocation_value = UILabel(
            relative_rect=pygame.Rect(x + width - 55, y, 55, 25),
            text="0",
            manager=self.manager
        )
        y += 35

        # Separator
        y += 10

        # --- Event Log Section ---
        UILabel(
            relative_rect=pygame.Rect(x, y, width, 20),
            text="Event Log:",
            manager=self.manager
        )
        y += 22

        log_height = self.rect.height - y - 120  # Leave room for buttons
        self.log_box = UITextBox(
            relative_rect=pygame.Rect(x, y, width, log_height),
            html_text="<i>No events yet. Click 'Next Turn' to simulate.</i>",
            manager=self.manager
        )
        y += log_height + 10

        # --- Action Buttons ---
        btn_width = (width - 10) // 2

        self.btn_next_turn = UIButton(
            relative_rect=pygame.Rect(x, y, btn_width, 35),
            text="Next Turn",
            manager=self.manager
        )

        self.btn_reset = UIButton(
            relative_rect=pygame.Rect(x + btn_width + 10, y, btn_width, 35),
            text="Reset",
            manager=self.manager
        )
        y += 45

        self.btn_close = UIButton(
            relative_rect=pygame.Rect(x, y, width, 35),
            text="Close",
            manager=self.manager
        )

    def handle_event(self, event: pygame.event, selected_node_id: Optional[str],
                     tech_tree: TechTree) -> bool:
        """
        Handle pygame_gui events.

        Args:
            event: pygame event
            selected_node_id: Currently selected node ID
            tech_tree: Tech tree for status checks

        Returns:
            True if event was handled
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_next_turn:
                self.on_next_turn()
                return True
            elif event.ui_element == self.btn_reset:
                self.on_reset()
                return True
            elif event.ui_element == self.btn_close:
                self.on_close()
                return True
            elif event.ui_element == self.btn_auto_spread:
                self._toggle_auto_spread()
                return True

        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.slider_budget:
                new_budget = int(self.slider_budget.get_current_value())
                self.tracker.set_rp_budget(new_budget)
                self.lbl_budget_value.set_text(str(new_budget))
                self.update_budget_display()
                self._update_allocation_slider_range()
                return True

            elif event.ui_element == self.slider_allocation:
                if self._selected_node and selected_node_id:
                    new_allocation = int(self.slider_allocation.get_current_value())
                    self.tracker.set_allocation(selected_node_id, new_allocation)
                    actual = self.tracker.get_state(selected_node_id).rp_allocation
                    self.lbl_allocation_value.set_text(str(actual))
                    self.update_budget_display()
                    return True

        return False

    def update_selected_node(self, node: TechNode, tracker: ResearchTracker):
        """
        Update the UI to show details for a selected node.

        Args:
            node: The selected TechNode
            tracker: Research tracker for state
        """
        self._selected_node = node
        self.tracker = tracker

        state = tracker.get_state(node.id)
        tech_levels = tracker.get_all_tech_levels()
        status = node.get_status(state.current_level, tech_levels)

        self.lbl_node_name.set_text(node.name)
        self.lbl_node_level.set_text(f"Level: {state.current_level} / {node.max_levels}")
        self.lbl_node_chance.set_text(f"Chance: {state.current_chance * 100:.1f}%")
        self.lbl_node_decay.set_text(f"Decay: {node.base_decay * 100:.1f}% / turn")
        self.lbl_node_volatility.set_text(f"Volatility: {node.volatility:.2f}")
        # Show effective price for next level
        target_level = state.current_level + 1
        if target_level <= node.max_levels:
            eff_price = node.get_effective_price(target_level)
            self.lbl_node_price.set_text(f"Price: {eff_price:.1f}x ({node.price_curve})")
        else:
            self.lbl_node_price.set_text("Price: - (maxed)")
        self.lbl_node_status.set_text(f"Status: {status.capitalize()}")

        # Enable allocation slider for available nodes
        if status == 'available':
            self.slider_allocation.enable()
            self._update_allocation_slider_range()
            self.slider_allocation.set_current_value(state.rp_allocation)
            self.lbl_allocation_value.set_text(str(state.rp_allocation))
        else:
            self.slider_allocation.disable()
            self.slider_allocation.set_current_value(0)
            self.lbl_allocation_value.set_text("-")

    def clear_selection(self):
        """Clear the node selection display."""
        self._selected_node = None
        self.lbl_node_name.set_text("(None)")
        self.lbl_node_level.set_text("Level: -")
        self.lbl_node_chance.set_text("Chance: -")
        self.lbl_node_decay.set_text("Decay: -")
        self.lbl_node_volatility.set_text("Volatility: -")
        self.lbl_node_price.set_text("Price: -")
        self.lbl_node_status.set_text("Status: -")
        self.slider_allocation.disable()
        self.slider_allocation.set_current_value(0)
        self.lbl_allocation_value.set_text("-")

    def update_budget_display(self):
        """Update the allocated/remaining display."""
        allocated = self.tracker.get_total_allocated()
        budget = self.tracker.rp_budget
        self.lbl_allocated.set_text(f"Allocated: {allocated} / {budget}")
        self.lbl_budget_value.set_text(str(budget))

    def _toggle_auto_spread(self):
        """Toggle auto-spread mode and apply if enabled."""
        self.tracker.auto_spread_enabled = not self.tracker.auto_spread_enabled
        self._update_auto_spread_button()

        if self.tracker.auto_spread_enabled:
            # Apply spread immediately when enabled
            self.tracker.spread_rp_evenly(self.tech_tree)
            self.update_budget_display()

        # Notify callback
        if self.on_auto_spread_changed:
            self.on_auto_spread_changed(self.tracker.auto_spread_enabled)

    def _update_auto_spread_button(self):
        """Update auto-spread button text based on current state."""
        if self.tracker.auto_spread_enabled:
            self.btn_auto_spread.set_text("Auto-Spread: ON")
        else:
            self.btn_auto_spread.set_text("Auto-Spread: OFF")

    def _update_allocation_slider_range(self):
        """Update allocation slider max based on available RP."""
        if self._selected_node:
            current_allocation = self.tracker.get_state(self._selected_node.id).rp_allocation
            remaining = self.tracker.get_remaining_rp()
            max_allocation = current_allocation + remaining
            # Update slider range
            self.slider_allocation.value_range = (0, max(1, max_allocation))

    def update_turn_log(self, events: List[Dict[str, Any]], turn_number: int):
        """
        Update the event log with turn results.

        Args:
            events: List of event dictionaries
            turn_number: Current turn number
        """
        self.lbl_turn.set_text(f"Turn: {turn_number}")

        if not events:
            log_text = f"<b>Turn {turn_number}:</b> No events."
        else:
            lines = [f"<b>Turn {turn_number}:</b>"]
            for evt in events:
                node_name = evt['details'].get('name', evt['node_id'])
                event_type = evt['event']

                if event_type == 'breakthrough':
                    new_level = evt['details']['new_level']
                    max_level = evt['details']['max_level']
                    chance = evt['details']['chance'] * 100
                    roll = evt['details']['roll'] * 100
                    lines.append(
                        f"<font color='#80FF80'>BREAKTHROUGH!</font> {node_name} "
                        f"-> Lv {new_level}/{max_level} "
                        f"(rolled {roll:.0f}% < {chance:.0f}%)"
                    )
                elif event_type == 'progress':
                    chance = evt['details']['chance'] * 100
                    roll = evt['details']['roll'] * 100
                    rp = evt['details'].get('rp_invested', 0)
                    lines.append(
                        f"{node_name}: {chance:.1f}% "
                        f"(rolled {roll:.0f}%, {rp} RP)"
                    )
                elif event_type == 'decay':
                    old = evt['details']['old_chance'] * 100
                    new = evt['details']['new_chance'] * 100
                    lines.append(
                        f"<font color='#AAAAAA'>{node_name}: decay {old:.1f}% -> {new:.1f}%</font>"
                    )

            log_text = "<br>".join(lines)

        # Prepend new events to existing log
        current_html = self.log_box.html_text
        if "<i>No events yet" in current_html:
            new_html = log_text
        else:
            new_html = log_text + "<br><br>" + current_html

        # Limit log length (keep last 5 turns for performance)
        if new_html.count("<b>Turn") > 5:
            # Truncate old entries
            parts = new_html.split("<br><br>")
            new_html = "<br><br>".join(parts[:5])

        self.log_box.html_text = new_html
        self.log_box.rebuild()

    def clear_log(self):
        """Clear the event log."""
        self.lbl_turn.set_text(f"Turn: {self.tracker.turn_number}")
        self.log_box.html_text = "<i>No events yet. Click 'Next Turn' to simulate.</i>"
        self.log_box.rebuild()

    def reset(self, tracker: ResearchTracker, tech_tree: TechTree):
        """
        Reset the control panel with new tracker and tech tree instances.

        This method provides a proper interface for resetting the control panel's
        state, avoiding direct attribute mutation from external code. It ensures
        all UI elements are updated consistently.

        Args:
            tracker: New ResearchTracker instance
            tech_tree: New TechTree instance (may have re-resolved requirements)
        """
        self.tracker = tracker
        self.tech_tree = tech_tree
        self.clear_selection()
        self.update_budget_display()
        self.clear_log()
        self._update_auto_spread_button()
