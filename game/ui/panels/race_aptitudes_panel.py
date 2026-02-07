"""
Race Aptitudes Panel - Point-buy aptitude configuration for races.

PROJ-66 Phase 5: Panel for configuring race aptitudes using a point-buy system.
Displays remaining budget prominently and allows adjustment of 9 aptitude stats.

Provides UI controls for:
- 9 aptitude sliders (Strength, Intelligence, etc.)
- Point budget display with color coding
- Tolerance cost display (read-only, reflects Environment tab choices)
"""
import pygame
import pygame_gui
from typing import Dict, Optional, TYPE_CHECKING

from game.strategy.data.race_point_budget import RacePointBudget

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


# Aptitude display names (nicer formatting for UI)
APTITUDE_DISPLAY_NAMES = {
    "strength": "Strength",
    "intelligence": "Intelligence",
    "constitution": "Constitution",
    "dexterity": "Dexterity",
    "tolerance_other_species": "Species Tolerance",
    "cooperation": "Cooperation",
    "happiness": "Happiness",
    "population_growth": "Population Growth",
    "conflict_tolerance": "Conflict Tolerance",
}

# Order of aptitudes in UI
APTITUDE_ORDER = [
    "strength",
    "intelligence",
    "constitution",
    "dexterity",
    "tolerance_other_species",
    "cooperation",
    "happiness",
    "population_growth",
    "conflict_tolerance",
]


class RaceAptitudesPanel:
    """
    Panel for configuring race aptitudes with point-buy system.

    Creates and manages sliders for 9 aptitude stats, displays remaining
    budget, and shows tolerance cost from environment choices.
    """

    def __init__(
        self,
        panel: pygame_gui.elements.UIPanel,
        manager: pygame_gui.UIManager,
        race_config: 'RaceConfig'
    ):
        """
        Create aptitudes configuration panel content.

        Args:
            panel: Parent UIPanel to add controls to
            manager: pygame_gui UIManager
            race_config: RaceConfig to read/write values from/to
        """
        self.panel = panel
        self.ui_manager = manager
        self.race_config = race_config

        # Point budget calculator
        self.point_budget = RacePointBudget()

        # UI element references
        self.budget_label: Optional[pygame_gui.elements.UILabel] = None
        self.tolerance_cost_label: Optional[pygame_gui.elements.UILabel] = None
        self.aptitude_cost_label: Optional[pygame_gui.elements.UILabel] = None

        # Slider and label dictionaries
        self.aptitude_sliders: Dict[str, pygame_gui.elements.UIHorizontalSlider] = {}
        self.aptitude_labels: Dict[str, pygame_gui.elements.UILabel] = {}
        self.cost_labels: Dict[str, pygame_gui.elements.UILabel] = {}

        self._create_content()

    def _create_content(self):
        """Create all panel content."""
        panel_width = self.panel.get_relative_rect().width - 20
        y = 5

        # Section 1: Budget Display (prominent at top)
        y = self._create_budget_section(y, panel_width)
        y += 15

        # Section 2: Aptitude Sliders
        y = self._create_aptitude_section(y, panel_width)
        y += 15

        # Section 3: Cost Breakdown
        y = self._create_cost_breakdown_section(y, panel_width)

    def _create_budget_section(self, y: int, width: int) -> int:
        """Create budget display section."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 200, 25),
            text="Point Budget:",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#section_header"
        )
        y += 28

        # Large, prominent budget display
        remaining = self.point_budget.get_remaining_points(self.race_config)
        self.budget_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, width - 40, 30),
            text=f"Points Remaining: {remaining} / {self.point_budget.total_budget}",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#budget_display"
        )
        y += 35

        return y

    def _create_aptitude_section(self, y: int, width: int) -> int:
        """Create aptitude slider controls."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 200, 25),
            text="Aptitudes (1-10, base 5):",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#section_header"
        )
        y += 28

        # Create a slider row for each aptitude
        for apt_name in APTITUDE_ORDER:
            display_name = APTITUDE_DISPLAY_NAMES[apt_name]
            current_value = self._get_aptitude_value(apt_name)

            # Name label
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(20, y, 130, 22),
                text=f"{display_name}:",
                manager=self.ui_manager,
                container=self.panel
            )

            # Slider (1-10, start at current or base)
            slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect(155, y, width - 280, 22),
                start_value=current_value,
                value_range=(1, 10),
                manager=self.ui_manager,
                container=self.panel,
                click_increment=1
            )
            self.aptitude_sliders[apt_name] = slider

            # Value label
            value_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(width - 120, y, 40, 22),
                text=str(current_value),
                manager=self.ui_manager,
                container=self.panel
            )
            self.aptitude_labels[apt_name] = value_label

            # Cost label
            cost = current_value - self.point_budget.APTITUDE_BASE
            cost_text = self._format_cost(cost)
            cost_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(width - 75, y, 55, 22),
                text=cost_text,
                manager=self.ui_manager,
                container=self.panel
            )
            self.cost_labels[apt_name] = cost_label

            y += 26

        return y

    def _create_cost_breakdown_section(self, y: int, width: int) -> int:
        """Create cost breakdown display section."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 200, 25),
            text="Cost Breakdown:",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#section_header"
        )
        y += 28

        # Aptitude cost total
        apt_cost = self.point_budget.calculate_aptitude_cost(self.race_config)
        self.aptitude_cost_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, width - 40, 22),
            text=f"Aptitude Cost: {apt_cost}",
            manager=self.ui_manager,
            container=self.panel
        )
        y += 24

        # Tolerance cost (from environment tab)
        tol_cost = self.point_budget.calculate_tolerance_cost(self.race_config)
        self.tolerance_cost_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, width - 40, 22),
            text=f"Tolerance Cost: {tol_cost} (set on Environment tab)",
            manager=self.ui_manager,
            container=self.panel
        )
        y += 24

        # Help text
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, width - 40, 40),
            text="Tolerance costs 2^n per step. Broad tolerance is expensive!",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#help_text"
        )
        y += 44

        return y

    def _get_aptitude_value(self, apt_name: str) -> int:
        """Get current aptitude value from config."""
        attr_name = f"aptitude_{apt_name}"
        return getattr(self.race_config, attr_name, 5)

    def _set_aptitude_value(self, apt_name: str, value: int):
        """Set aptitude value in config."""
        attr_name = f"aptitude_{apt_name}"
        setattr(self.race_config, attr_name, int(value))

    def _format_cost(self, cost: int) -> str:
        """Format cost for display."""
        if cost > 0:
            return f"+{cost}"
        elif cost < 0:
            return str(cost)
        else:
            return "0"

    def update_config(self):
        """Update race_config from slider values."""
        for apt_name, slider in self.aptitude_sliders.items():
            value = int(slider.get_current_value())
            self._set_aptitude_value(apt_name, value)

    def set_from_config(self):
        """Set slider values from race_config."""
        for apt_name, slider in self.aptitude_sliders.items():
            value = self._get_aptitude_value(apt_name)
            slider.set_current_value(value)

        self.update_labels()
        self.update_budget_display()

    def update_labels(self):
        """Update value and cost labels from slider values."""
        for apt_name, slider in self.aptitude_sliders.items():
            value = int(slider.get_current_value())

            # Update value label
            if apt_name in self.aptitude_labels:
                self.aptitude_labels[apt_name].set_text(str(value))

            # Update cost label
            if apt_name in self.cost_labels:
                cost = value - self.point_budget.APTITUDE_BASE
                self.cost_labels[apt_name].set_text(self._format_cost(cost))

    def update_budget_display(self):
        """Update budget display with current remaining points."""
        remaining = self.point_budget.get_remaining_points(self.race_config)
        total = self.point_budget.total_budget

        # Update main budget label
        if self.budget_label:
            self.budget_label.set_text(f"Points Remaining: {remaining} / {total}")

        # Update aptitude cost label
        if self.aptitude_cost_label:
            apt_cost = self.point_budget.calculate_aptitude_cost(self.race_config)
            self.aptitude_cost_label.set_text(f"Aptitude Cost: {apt_cost}")

        # Update tolerance cost label
        if self.tolerance_cost_label:
            tol_cost = self.point_budget.calculate_tolerance_cost(self.race_config)
            self.tolerance_cost_label.set_text(f"Tolerance Cost: {tol_cost} (set on Environment tab)")
