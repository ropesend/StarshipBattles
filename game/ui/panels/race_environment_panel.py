"""
Race Environment Panel - Environmental preferences configuration for races.

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.
PROJ-66 Phase 4: Added homeworld dropdown, water sliders, and preset auto-populate.

Provides UI controls for configuring:
- Homeworld type selection with presets
- Gravity preferences (ideal and tolerance)
- Temperature preferences (ideal and tolerance)
- Water preferences (ideal and tolerance)
- Radiation tolerance
- Atmosphere gas preferences
"""
import pygame
import pygame_gui
from typing import Dict, List, Optional, TYPE_CHECKING

from game.strategy.data.homeworld_presets import (
    get_available_homeworld_names,
    get_preset_for_planet_type,
    get_preset_id_from_name,
    load_homeworld_presets,
)
from game.ui.utils import create_section_header

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


class RaceEnvironmentPanel:
    """
    Panel for configuring race environmental preferences.

    Creates and manages sliders for gravity, temperature, radiation,
    and atmosphere preferences.
    """

    # Default atmosphere gases
    DEFAULT_GASES = [
        "Oxygen",
        "Nitrogen",
        "Carbon Dioxide",
        "Methane",
        "Hydrogen",
        "Helium",
    ]

    def __init__(
        self,
        panel: pygame_gui.elements.UIPanel,
        manager: pygame_gui.UIManager,
        race_config: 'RaceConfig'
    ):
        """
        Create environment configuration panel content.

        Args:
            panel: Parent UIPanel to add controls to
            manager: pygame_gui UIManager
            race_config: RaceConfig to read/write values from/to
        """
        self.panel = panel
        self.ui_manager = manager
        self.race_config = race_config

        # Slider references
        self.gravity_ideal_slider: Optional[pygame_gui.elements.UIHorizontalSlider] = None
        self.gravity_tolerance_slider: Optional[pygame_gui.elements.UIHorizontalSlider] = None
        self.gravity_ideal_label: Optional[pygame_gui.elements.UILabel] = None
        self.gravity_tolerance_label: Optional[pygame_gui.elements.UILabel] = None

        self.temp_ideal_slider: Optional[pygame_gui.elements.UIHorizontalSlider] = None
        self.temp_tolerance_slider: Optional[pygame_gui.elements.UIHorizontalSlider] = None
        self.temp_ideal_label: Optional[pygame_gui.elements.UILabel] = None
        self.temp_tolerance_label: Optional[pygame_gui.elements.UILabel] = None

        self.radiation_slider: Optional[pygame_gui.elements.UIHorizontalSlider] = None
        self.radiation_label: Optional[pygame_gui.elements.UILabel] = None

        self.water_ideal_slider: Optional[pygame_gui.elements.UIHorizontalSlider] = None
        self.water_tolerance_slider: Optional[pygame_gui.elements.UIHorizontalSlider] = None
        self.water_ideal_label: Optional[pygame_gui.elements.UILabel] = None
        self.water_tolerance_label: Optional[pygame_gui.elements.UILabel] = None

        self.homeworld_dropdown: Optional[pygame_gui.elements.UIDropDownMenu] = None

        self.atmosphere_sliders: Dict[str, pygame_gui.elements.UIHorizontalSlider] = {}
        self.atmosphere_labels: Dict[str, pygame_gui.elements.UILabel] = {}

        self.points_label: Optional[pygame_gui.elements.UILabel] = None

        self._create_content()

    def _create_content(self):
        """Create all panel content."""
        panel_width = self.panel.get_relative_rect().width - 20
        y = 5

        # Points display (BUG-58)
        self.points_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, panel_width, 25),
            text="",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#points_display"
        )
        self._update_points_display()
        y += 30

        # Section 0: Homeworld Type (preset selector)
        y = self._create_homeworld_section(y, panel_width)
        y += 15

        # Section 1: Gravity
        y = self._create_gravity_section(y, panel_width)
        y += 15

        # Section 2: Temperature
        y = self._create_temperature_section(y, panel_width)
        y += 15

        # Section 3: Radiation Tolerance
        y = self._create_radiation_section(y, panel_width)
        y += 15

        # Section 4: Water Preferences
        y = self._create_water_section(y, panel_width)
        y += 15

        # Section 5: Atmosphere Preferences
        y = self._create_atmosphere_section(y, panel_width)

    def _create_homeworld_section(self, y: int, width: int) -> int:
        """Create homeworld type dropdown for preset selection."""
        create_section_header("Homeworld Type:", y, 200, self.ui_manager, self.panel)
        y += 28

        # Build dropdown options: all planet types + Custom
        presets = load_homeworld_presets()
        options = [preset["name"] for preset in presets.values()]
        options.append("(Custom)")

        # Determine starting selection
        starting_option = "(Custom)"
        if self.race_config.homeworld_type:
            preset = presets.get(self.race_config.homeworld_type)
            if preset:
                starting_option = preset["name"]

        self.homeworld_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=options,
            starting_option=starting_option,
            relative_rect=pygame.Rect(20, y, width - 30, 28),
            manager=self.ui_manager,
            container=self.panel
        )
        y += 32

        return y

    def _create_gravity_section(self, y: int, width: int) -> int:
        """Create gravity preference controls."""
        create_section_header("Gravity Preferences:", y, 200, self.ui_manager, self.panel)
        y += 28

        # Ideal gravity: 0.1 - 3.0 g
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 100, 22),
            text="Ideal (g):",
            manager=self.ui_manager,
            container=self.panel
        )
        self.gravity_ideal_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(120, y, width - 200, 22),
            start_value=self.race_config.gravity_ideal,
            value_range=(0.1, 3.0),
            manager=self.ui_manager,
            container=self.panel,
            click_increment=0.1
        )
        self.gravity_ideal_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(width - 70, y, 60, 22),
            text=f"{self.race_config.gravity_ideal:.1f}",
            manager=self.ui_manager,
            container=self.panel
        )
        y += 26

        # Tolerance: 0.0 - 1.0 g
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 100, 22),
            text="Tolerance:",
            manager=self.ui_manager,
            container=self.panel
        )
        self.gravity_tolerance_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(120, y, width - 200, 22),
            start_value=self.race_config.gravity_tolerance,
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
            container=self.panel,
            click_increment=0.05
        )
        self.gravity_tolerance_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(width - 70, y, 60, 22),
            text=f"±{self.race_config.gravity_tolerance:.2f}",
            manager=self.ui_manager,
            container=self.panel
        )
        y += 26

        return y

    def _create_temperature_section(self, y: int, width: int) -> int:
        """Create temperature preference controls."""
        create_section_header("Temperature Preferences:", y, 200, self.ui_manager, self.panel)
        y += 28

        # Ideal temperature: 200 - 400 K
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 100, 22),
            text="Ideal (K):",
            manager=self.ui_manager,
            container=self.panel
        )
        self.temp_ideal_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(120, y, width - 200, 22),
            start_value=self.race_config.temperature_ideal,
            value_range=(200, 400),
            manager=self.ui_manager,
            container=self.panel,
            click_increment=5
        )
        self.temp_ideal_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(width - 70, y, 60, 22),
            text=f"{self.race_config.temperature_ideal:.0f}",
            manager=self.ui_manager,
            container=self.panel
        )
        y += 26

        # Tolerance: 0 - 100 K
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 100, 22),
            text="Tolerance:",
            manager=self.ui_manager,
            container=self.panel
        )
        self.temp_tolerance_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(120, y, width - 200, 22),
            start_value=self.race_config.temperature_tolerance,
            value_range=(0, 100),
            manager=self.ui_manager,
            container=self.panel,
            click_increment=5
        )
        self.temp_tolerance_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(width - 70, y, 60, 22),
            text=f"±{self.race_config.temperature_tolerance:.0f}",
            manager=self.ui_manager,
            container=self.panel
        )
        y += 26

        return y

    def _create_radiation_section(self, y: int, width: int) -> int:
        """Create radiation tolerance control."""
        create_section_header("Radiation Tolerance:", y, 200, self.ui_manager, self.panel)
        y += 28

        # Radiation: -100 (sensitive) to +100 (resistant)
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 100, 22),
            text="Tolerance:",
            manager=self.ui_manager,
            container=self.panel
        )
        self.radiation_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(120, y, width - 200, 22),
            start_value=self.race_config.radiation_tolerance,
            value_range=(-100, 100),
            manager=self.ui_manager,
            container=self.panel,
            click_increment=5
        )
        self.radiation_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(width - 70, y, 60, 22),
            text=self._format_radiation(self.race_config.radiation_tolerance),
            manager=self.ui_manager,
            container=self.panel
        )
        y += 26

        return y

    def _create_water_section(self, y: int, width: int) -> int:
        """Create water preference controls."""
        create_section_header("Water Preferences:", y, 200, self.ui_manager, self.panel)
        y += 28

        # Ideal water: 0.0 - 1.0
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 100, 22),
            text="Ideal:",
            manager=self.ui_manager,
            container=self.panel
        )
        self.water_ideal_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(120, y, width - 200, 22),
            start_value=self.race_config.water_ideal,
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
            container=self.panel,
            click_increment=0.05
        )
        self.water_ideal_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(width - 70, y, 60, 22),
            text=self._format_water(self.race_config.water_ideal),
            manager=self.ui_manager,
            container=self.panel
        )
        y += 26

        # Tolerance: 0.0 - 1.0
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 100, 22),
            text="Tolerance:",
            manager=self.ui_manager,
            container=self.panel
        )
        self.water_tolerance_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(120, y, width - 200, 22),
            start_value=self.race_config.water_tolerance,
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
            container=self.panel,
            click_increment=0.05
        )
        self.water_tolerance_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(width - 70, y, 60, 22),
            text=self._format_water_tolerance(self.race_config.water_tolerance),
            manager=self.ui_manager,
            container=self.panel
        )
        y += 26

        return y

    def _create_atmosphere_section(self, y: int, width: int) -> int:
        """Create atmosphere preference controls."""
        create_section_header(
            "Atmosphere Preferences (-100 toxic to +100 beneficial):",
            y, width, self.ui_manager, self.panel
        )
        y += 28

        # Create two columns of atmosphere sliders
        gases = list(self.race_config.atmosphere_preferences.keys())
        col_width = (width - 30) // 2

        for i, gas in enumerate(gases):
            col = i % 2
            row = i // 2
            x_offset = 10 + col * (col_width + 10)
            y_pos = y + row * 28

            # Gas label
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(x_offset, y_pos, 110, 22),
                text=f"{gas}:",
                manager=self.ui_manager,
                container=self.panel
            )

            # Slider: -100 to +100
            slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect(x_offset + 115, y_pos, col_width - 175, 22),
                start_value=self.race_config.atmosphere_preferences.get(gas, 0),
                value_range=(-100, 100),
                manager=self.ui_manager,
                container=self.panel,
                click_increment=5
            )
            self.atmosphere_sliders[gas] = slider

            # Value label
            value = self.race_config.atmosphere_preferences.get(gas, 0)
            label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(x_offset + col_width - 55, y_pos, 50, 22),
                text=self._format_atmosphere(value),
                manager=self.ui_manager,
                container=self.panel
            )
            self.atmosphere_labels[gas] = label

        # Calculate final y position
        rows = (len(gases) + 1) // 2
        y += rows * 28

        return y

    def _format_radiation(self, value: float) -> str:
        """Format radiation tolerance value for display."""
        if value < -50:
            return f"{value:.0f} Sens"
        elif value > 50:
            return f"+{value:.0f} Res"
        elif value >= 0:
            return f"+{value:.0f}"
        else:
            return f"{value:.0f}"

    def _format_atmosphere(self, value: float) -> str:
        """Format atmosphere preference value for display."""
        if value >= 0:
            return f"+{value:.0f}"
        else:
            return f"{value:.0f}"

    def _format_water(self, value: float) -> str:
        """Format water value as percentage."""
        return f"{value * 100:.0f}%"

    def _format_water_tolerance(self, value: float) -> str:
        """Format water tolerance value as ± percentage."""
        return f"±{value * 100:.0f}%"

    def _update_points_display(self):
        """Update the racial points display label (BUG-58)."""
        if not getattr(self, 'points_label', None):
            return
        try:
            from game.strategy.data.race_point_budget import RacePointBudget
            budget = RacePointBudget()
            remaining = budget.get_remaining_points(self.race_config)
            total = budget.total_budget
            tolerance_cost = budget.calculate_tolerance_cost(self.race_config)
            self.points_label.set_text(
                f"Points: {remaining} / {total} remaining  |  Environment cost: {tolerance_cost}"
            )
        except Exception:
            self.points_label.set_text("")

    def update_config(self):
        """Update race_config from slider values."""
        if self.gravity_ideal_slider:
            self.race_config.gravity_ideal = self.gravity_ideal_slider.get_current_value()
        if self.gravity_tolerance_slider:
            self.race_config.gravity_tolerance = self.gravity_tolerance_slider.get_current_value()
        if self.temp_ideal_slider:
            self.race_config.temperature_ideal = self.temp_ideal_slider.get_current_value()
        if self.temp_tolerance_slider:
            self.race_config.temperature_tolerance = self.temp_tolerance_slider.get_current_value()
        if self.radiation_slider:
            self.race_config.radiation_tolerance = self.radiation_slider.get_current_value()
        if self.water_ideal_slider:
            self.race_config.water_ideal = self.water_ideal_slider.get_current_value()
        if self.water_tolerance_slider:
            self.race_config.water_tolerance = self.water_tolerance_slider.get_current_value()

        for gas, slider in self.atmosphere_sliders.items():
            self.race_config.atmosphere_preferences[gas] = slider.get_current_value()

    def update_labels(self):
        """Update display labels from slider values."""
        if self.gravity_ideal_slider and self.gravity_ideal_label:
            val = self.gravity_ideal_slider.get_current_value()
            self.gravity_ideal_label.set_text(f"{val:.1f}")

        if self.gravity_tolerance_slider and self.gravity_tolerance_label:
            val = self.gravity_tolerance_slider.get_current_value()
            self.gravity_tolerance_label.set_text(f"±{val:.2f}")

        if self.temp_ideal_slider and self.temp_ideal_label:
            val = self.temp_ideal_slider.get_current_value()
            self.temp_ideal_label.set_text(f"{val:.0f}")

        if self.temp_tolerance_slider and self.temp_tolerance_label:
            val = self.temp_tolerance_slider.get_current_value()
            self.temp_tolerance_label.set_text(f"±{val:.0f}")

        if self.radiation_slider and self.radiation_label:
            val = self.radiation_slider.get_current_value()
            self.radiation_label.set_text(self._format_radiation(val))

        if self.water_ideal_slider and self.water_ideal_label:
            val = self.water_ideal_slider.get_current_value()
            self.water_ideal_label.set_text(self._format_water(val))

        if self.water_tolerance_slider and self.water_tolerance_label:
            val = self.water_tolerance_slider.get_current_value()
            self.water_tolerance_label.set_text(self._format_water_tolerance(val))

        for gas, slider in self.atmosphere_sliders.items():
            if gas in self.atmosphere_labels:
                val = slider.get_current_value()
                self.atmosphere_labels[gas].set_text(self._format_atmosphere(val))

        self._update_points_display()

    def set_from_config(self):
        """Set slider values from race_config (for loading saved races)."""
        if self.gravity_ideal_slider:
            self.gravity_ideal_slider.set_current_value(self.race_config.gravity_ideal)
        if self.gravity_tolerance_slider:
            self.gravity_tolerance_slider.set_current_value(self.race_config.gravity_tolerance)
        if self.temp_ideal_slider:
            self.temp_ideal_slider.set_current_value(self.race_config.temperature_ideal)
        if self.temp_tolerance_slider:
            self.temp_tolerance_slider.set_current_value(self.race_config.temperature_tolerance)
        if self.radiation_slider:
            self.radiation_slider.set_current_value(self.race_config.radiation_tolerance)
        if self.water_ideal_slider:
            self.water_ideal_slider.set_current_value(self.race_config.water_ideal)
        if self.water_tolerance_slider:
            self.water_tolerance_slider.set_current_value(self.race_config.water_tolerance)

        for gas, slider in self.atmosphere_sliders.items():
            if gas in self.race_config.atmosphere_preferences:
                slider.set_current_value(self.race_config.atmosphere_preferences[gas])

        self.update_labels()

    def apply_homeworld_preset(self, planet_type_name: str) -> None:
        """
        Apply a homeworld preset to all environment sliders.

        Args:
            planet_type_name: Planet type ID (e.g., "CONTINENTAL") or "(Custom)"
        """
        # Custom means leave everything as-is
        if planet_type_name == "(Custom)":
            return

        # Get the preset data
        preset = get_preset_for_planet_type(planet_type_name)
        if preset is None:
            return

        # Update race_config
        self.race_config.homeworld_type = planet_type_name

        # Set all slider values from preset
        if self.gravity_ideal_slider:
            self.gravity_ideal_slider.set_current_value(preset["gravity_ideal"])
        if self.gravity_tolerance_slider:
            self.gravity_tolerance_slider.set_current_value(preset["gravity_tolerance"])
        if self.temp_ideal_slider:
            self.temp_ideal_slider.set_current_value(preset["temperature_ideal"])
        if self.temp_tolerance_slider:
            self.temp_tolerance_slider.set_current_value(preset["temperature_tolerance"])
        if self.water_ideal_slider:
            self.water_ideal_slider.set_current_value(preset["water_ideal"])
        if self.water_tolerance_slider:
            self.water_tolerance_slider.set_current_value(preset["water_tolerance"])
        if self.radiation_slider:
            self.radiation_slider.set_current_value(preset["radiation_tolerance"])

        # Set atmosphere preferences
        for gas, value in preset["atmosphere_preferences"].items():
            if gas in self.atmosphere_sliders:
                self.atmosphere_sliders[gas].set_current_value(value)

        # Update all labels to reflect new values
        self.update_labels()

    def handle_dropdown_change(self, event) -> bool:
        """
        Handle dropdown change events.

        PROJ-66 Phase 6: Added to support centralized event routing.

        Args:
            event: pygame_gui UI_DROP_DOWN_MENU_CHANGED event

        Returns:
            True if event was handled
        """
        if hasattr(event, 'ui_element') and event.ui_element == self.homeworld_dropdown:
            # Get selected option (display name, e.g. "Continental")
            selected = self.homeworld_dropdown.selected_option
            if isinstance(selected, tuple):
                selected = selected[0]

            # Convert display name to preset ID (e.g. "CONTINENTAL")
            preset_id = get_preset_id_from_name(selected)
            self.apply_homeworld_preset(preset_id if preset_id else selected)
            self.update_config()
            return True
        return False
