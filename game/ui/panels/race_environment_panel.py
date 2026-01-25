"""
Race Environment Panel - Environmental preferences configuration for races.

PROJ-12 Phase 4: Extracted from RaceSetupScreen to decompose the god class.

Provides UI controls for configuring:
- Gravity preferences (ideal and tolerance)
- Temperature preferences (ideal and tolerance)
- Radiation tolerance
- Atmosphere gas preferences
"""
import pygame
import pygame_gui
from typing import Dict, Optional, TYPE_CHECKING

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

        self.atmosphere_sliders: Dict[str, pygame_gui.elements.UIHorizontalSlider] = {}
        self.atmosphere_labels: Dict[str, pygame_gui.elements.UILabel] = {}

        self._create_content()

    def _create_content(self):
        """Create all panel content."""
        panel_width = self.panel.get_relative_rect().width - 20
        y = 5

        # Section 1: Gravity
        y = self._create_gravity_section(y, panel_width)
        y += 15

        # Section 2: Temperature
        y = self._create_temperature_section(y, panel_width)
        y += 15

        # Section 3: Radiation Tolerance
        y = self._create_radiation_section(y, panel_width)
        y += 15

        # Section 4: Atmosphere Preferences
        y = self._create_atmosphere_section(y, panel_width)

    def _create_gravity_section(self, y: int, width: int) -> int:
        """Create gravity preference controls."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 200, 25),
            text="Gravity Preferences:",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#section_header"
        )
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
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 200, 25),
            text="Temperature Preferences:",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#section_header"
        )
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
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 200, 25),
            text="Radiation Tolerance:",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#section_header"
        )
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

    def _create_atmosphere_section(self, y: int, width: int) -> int:
        """Create atmosphere preference controls."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 300, 25),
            text="Atmosphere Preferences (-100 toxic to +100 beneficial):",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#section_header"
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
                relative_rect=pygame.Rect(x_offset, y_pos, 80, 22),
                text=f"{gas}:",
                manager=self.ui_manager,
                container=self.panel
            )

            # Slider: -100 to +100
            slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect(x_offset + 85, y_pos, col_width - 145, 22),
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

        for gas, slider in self.atmosphere_sliders.items():
            if gas in self.atmosphere_labels:
                val = slider.get_current_value()
                self.atmosphere_labels[gas].set_text(self._format_atmosphere(val))

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

        for gas, slider in self.atmosphere_sliders.items():
            if gas in self.race_config.atmosphere_preferences:
                slider.set_current_value(self.race_config.atmosphere_preferences[gas])

        self.update_labels()
