"""Strategy detail formatter for StrategyUI.

Handles detail report rendering, production calculations, and raw data popups
for the strategy screen's detail panel.

PROJ-86: Extracted from strategy_ui.py to reduce god class size.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

import pygame
import pygame_gui
import pygame_gui.windows

from game.core.protocols import (
    is_star_system, is_star, is_planet, is_fleet,
    is_warp_point, is_sector_environment, is_storm
)
from game.ui.panels.planet_report_panel import PlanetReportPanel, compute_planet_production
from game.ui.screens.strategy_detail_fmt import (
    format_spectrum_html, format_atmosphere_raw, get_label_for_object,
    format_fleet_info
)

if TYPE_CHECKING:
    import pygame_gui.elements


class StrategyDetailFormatter:
    """Handles detail report formatting and display for the strategy UI.

    Responsible for:
    - Rendering detailed reports for selected objects (stars, planets, fleets, etc.)
    - Computing planet production rates
    - Showing raw data popups
    - Managing the planet report panel lifecycle

    Args:
        scene: Reference to StrategyScreen for current_empire, galaxy, turn_engine access
        manager: pygame_gui.UIManager for creating UI elements
        detail_panel: UIPanel container for the detail display
        widgets: Dict of UI widget references (portrait_image, detail_text, etc.)
        graphs: Dict with spectrum_graph and atmosphere_graph references
        graph_rect: pygame.Rect for graph positioning
        screen_size: Tuple of (width, height) for popup positioning
    """

    def __init__(
        self,
        scene,
        manager: pygame_gui.UIManager,
        detail_panel,
        widgets: Dict[str, Any],
        graphs: Dict[str, Any],
        graph_rect: pygame.Rect,
        screen_size: tuple[int, int],
    ):
        self.scene = scene
        self.manager = manager
        self.detail_panel = detail_panel
        self._widgets = widgets
        self._graphs = graphs
        self.graph_rect = graph_rect
        self._screen_width, self._screen_height = screen_size

        # State
        self.current_selection = None
        self.current_raw_data = ""
        self.planet_report_panel: Optional[PlanetReportPanel] = None

    # =========================================================================
    # Widget Accessors
    # =========================================================================

    @property
    def portrait_image(self):
        return self._widgets['portrait_image']

    @property
    def detail_text(self):
        return self._widgets['detail_text']

    @property
    def graph_image(self):
        return self._widgets['graph_image']

    @property
    def btn_raw_data(self):
        return self._widgets['btn_raw_data']

    @property
    def btn_colonize(self):
        return self._widgets['btn_colonize']

    @property
    def btn_build_yard(self):
        return self._widgets['btn_build_yard']

    @property
    def btn_orders(self):
        return self._widgets['btn_orders']

    @property
    def btn_fleet_report(self):
        return self._widgets['btn_fleet_report']

    @property
    def btn_build_fleet(self):
        return self._widgets['btn_build_fleet']

    @property
    def spectrum_graph(self):
        return self._graphs['spectrum_graph']

    @property
    def atmosphere_graph(self):
        return self._graphs['atmosphere_graph']

    # =========================================================================
    # Thin Wrappers to strategy_detail_fmt
    # =========================================================================

    def _get_label_for_obj(self, obj) -> str:
        """Get display label for an object."""
        return get_label_for_object(obj)

    def _format_spectrum(self, star) -> str:
        """Format star spectrum as HTML."""
        return format_spectrum_html(star)

    def _format_atmosphere_raw(self, planet) -> str:
        """Format planet atmosphere as raw data string."""
        return format_atmosphere_raw(planet)

    # =========================================================================
    # Production Calculation
    # =========================================================================

    def compute_planet_production(self, planet) -> Dict[str, float]:
        """Compute per-resource production rates for a colony planet.

        Delegates to shared compute_planet_production() function.

        Args:
            planet: Planet object to compute production for

        Returns:
            Dict mapping resource name to production rate per turn
        """
        return compute_planet_production(planet)

    # =========================================================================
    # Raw Data Popup
    # =========================================================================

    def show_raw_data_popup(self) -> None:
        """Show raw data in a message window."""
        if self.current_raw_data:
            win_rect = pygame.Rect(0, 0, 400, 400)
            win_rect.center = (self._screen_width / 2, self._screen_height / 2)
            pygame_gui.windows.UIMessageWindow(
                rect=win_rect,
                html_message=self.current_raw_data,
                manager=self.manager,
                window_title="Raw Data Analysis"
            )

    # =========================================================================
    # Detail Report Display
    # =========================================================================

    def show_detailed_report(self, obj, portrait_surface=None) -> None:
        """Update the detail report for the selected object.

        Handles all object types: star systems, stars, planets, fleets,
        warp points, and sector environments.

        Args:
            obj: The object to display details for
            portrait_surface: Optional portrait image surface
        """
        self.current_selection = obj

        # Reset state
        self.btn_raw_data.hide()
        self.graph_image.hide()

        # Default hidden, shown based on context below
        self.btn_colonize.hide()
        self.btn_build_yard.hide()
        self.btn_orders.hide()
        self.btn_fleet_report.hide()
        self.btn_build_fleet.hide()
        self.current_raw_data = ""

        # Clean up planet report panel if switching to non-planet object
        if self.planet_report_panel is not None:
            self.planet_report_panel.kill()
            self.planet_report_panel = None
            # Show the old widgets again for non-planet objects
            self.portrait_image.show()
            self.detail_text.show()

        # Determine Current Player
        # NOTE: hasattr check is intentional - scene may or may not have current_empire
        current_empire_id = -1
        if hasattr(self.scene, 'current_empire'):
            current_empire_id = self.scene.current_empire.id

        self.current_raw_data = ""

        if portrait_surface:
            scaled = pygame.transform.smoothscale(portrait_surface, (150, 150))
            self.portrait_image.set_image(scaled)
        else:
            self.portrait_image.set_image(pygame.Surface((150, 150)))

        if not obj:
            self.detail_text.set_text("Select an object for details.")
            return

        text = ""

        if is_star_system(obj):
            text = self._format_star_system(obj)
        elif is_star(obj):
            text = self._format_star(obj)
        elif is_planet(obj):
            self._show_planet_report(obj, portrait_surface, current_empire_id)
            text = ""
        elif is_sector_environment(obj):
            text = self._format_sector_environment(obj)
        elif is_fleet(obj):
            text = self._format_fleet(obj, current_empire_id)
        elif is_warp_point(obj):
            text = self._format_warp_point(obj)
        elif is_storm(obj):
            text = self._format_storm(obj)

        self.detail_text.html_text = text
        self.detail_text.rebuild()

    def _format_star_system(self, obj) -> str:
        """Format star system details."""
        primary = obj.primary_star
        if primary:
            text = f"<b>System:</b> {obj.name}<br>"
            text += f"<b>Primary:</b> {primary.name}<br>"
            text += f"<b>Type:</b> {primary.star_type.name}<br>"
            text += f"<b>Mass:</b> {primary.mass:.2f} Sol<br>"
            text += f"<b>Temp:</b> {int(primary.temperature)} K<br>"
            text += f"<b>Stars:</b> {len(obj.stars)}<br>"

            # Graph
            self.graph_image.show()
            self.btn_raw_data.show()
            surface = self.spectrum_graph.render(primary, vertical=True)
            surface = pygame.transform.rotate(surface, -90)
            self.graph_image.set_image(surface)
            self.current_raw_data = self._format_spectrum(primary)
            return text
        else:
            return f"<b>System:</b> {obj.name}<br>(Empty System)"

    def _format_star(self, obj) -> str:
        """Format star details."""
        text = f"<b>Star:</b> {obj.name}<br>"
        text += f"<b>Type:</b> {obj.star_type.name}<br>"
        text += f"<b>Mass:</b> {obj.mass:.2f} Sol<br>"
        text += f"<b>Temp:</b> {int(obj.temperature)} K<br>"
        text += f"<b>Diam:</b> {obj.diameter_hexes:.1f} Hex<br>"

        self.graph_image.show()
        self.btn_raw_data.show()
        surface = self.spectrum_graph.render(obj, vertical=True)
        surface = pygame.transform.rotate(surface, -90)
        self.graph_image.set_image(surface)
        self.current_raw_data = self._format_spectrum(obj)
        return text

    def _show_planet_report(self, obj, portrait_surface, current_empire_id: int) -> None:
        """Show planet report panel."""
        # Hide old widgets - using PlanetReportPanel instead
        self.portrait_image.hide()
        self.detail_text.hide()

        # Calculate available height for panel
        detail_panel_height = self.detail_panel.rect.height
        button_relative_y = self.btn_build_yard.relative_rect.y
        panel_max_height = min(detail_panel_height - 60, button_relative_y - 20)

        # Create planet report panel (NO complexes for strategy UI)
        production_rates = self.compute_planet_production(obj)
        self.planet_report_panel = PlanetReportPanel(
            manager=self.manager,
            rect=pygame.Rect(10, 10, 580, panel_max_height),
            planet=obj,
            container=self.detail_panel,
            portrait_surface=portrait_surface,
            show_complexes=False,
            production_rates=production_rates
        )

        # Show Build Yard button for owned planets
        if obj.owner_id == current_empire_id:
            self.btn_build_yard.show()

    def _format_sector_environment(self, obj) -> str:
        """Format sector environment details."""
        spec = obj.calculate_radiation()

        # Mock a star-like object so _format_spectrum works
        class MockStar:
            spectrum = spec

        text = f"<b>Local Environment</b><br>"
        text += f"<b>System:</b> {obj.system.name}<br>"
        text += f"<b>Local:</b> {obj.local_hex}<br>"
        text += f"<br><b>Total Incident Radiation:</b><br>"
        text += f"{spec.get_total_output():.2e} W/m^2 (relative)<br>"

        self.graph_image.show()
        self.btn_raw_data.show()
        surface = self.spectrum_graph.render(MockStar, vertical=True)
        surface = pygame.transform.rotate(surface, -90)
        self.graph_image.set_image(surface)
        self.current_raw_data = self._format_spectrum(MockStar)
        return text

    def _format_fleet(self, obj, current_empire_id: int) -> str:
        """Format fleet details."""
        text = format_fleet_info(obj)

        # Show Fleet Buttons
        if obj.owner_id == current_empire_id:
            self.btn_orders.show()
            self.btn_fleet_report.show()

            # PROJ-67: Show Build button for fleets with space shipyard
            if obj.has_space_shipyard:
                self.btn_build_fleet.show()

            # Check if we can colonize
            # NOTE: hasattr check is intentional - scene may or may not have turn_engine
            if hasattr(self.scene, 'turn_engine'):
                res = self.scene.turn_engine.validate_colonize_order(self.scene.galaxy, obj, None)
                if res.is_valid:
                    self.btn_colonize.show()

        return text

    def _format_warp_point(self, obj) -> str:
        """Format warp point details."""
        text = f"<b>Warp Point</b><br>"
        text += f"<b>To:</b> {obj.destination_id}<br>"
        text += f"<b>Local Loc:</b> {obj.location}<br>"
        return text

    def _format_storm(self, obj) -> str:
        """Format storm details (PROJ-189).

        Displays storm name, type, and environmental effects as
        percentage reductions and per-turn damage/drain values.
        """
        # Storm type display names
        type_names = {
            'ion_storm': 'Ion Storm',
            'plasma_storm': 'Plasma Storm',
            'gravitational_anomaly': 'Gravitational Anomaly',
            'radiation_belt': 'Radiation Belt',
            'dark_nebula': 'Dark Nebula',
        }
        type_display = type_names.get(obj.storm_type, obj.storm_type)

        text = f"<b>Storm:</b> {obj.name}<br>"
        text += f"<b>Type:</b> {type_display}<br>"
        text += f"<b>Size:</b> {len(obj.occupied_hexes)} hexes<br>"
        text += f"<br><b>Effects:</b><br>"

        effects = obj.effects

        # Format multipliers as percentage reductions
        if effects.shield_capacity_mult < 1.0:
            reduction = int((1.0 - effects.shield_capacity_mult) * 100)
            text += f"  Shields: -{reduction}%<br>"

        if effects.strategic_mult < 1.0:
            reduction = int((1.0 - effects.strategic_mult) * 100)
            text += f"  Speed: -{reduction}%<br>"

        if effects.thrust_mult < 1.0:
            reduction = int((1.0 - effects.thrust_mult) * 100)
            text += f"  Thrust: -{reduction}%<br>"

        # Format damage/drain as per-turn rates
        if effects.damage_per_tick > 0:
            # 100 ticks per turn
            damage_per_turn = effects.damage_per_tick * 100
            text += f"  Damage: {damage_per_turn:.0f}/turn<br>"

        if effects.fuel_drain_per_tick > 0:
            drain_per_turn = effects.fuel_drain_per_tick * 100
            text += f"  Fuel Drain: {drain_per_turn:.0f}/turn<br>"

        return text

    # =========================================================================
    # Resize Support
    # =========================================================================

    def update_screen_size(self, width: int, height: int) -> None:
        """Update screen size for popup positioning."""
        self._screen_width = width
        self._screen_height = height

    def update_graph_rect(self, graph_rect: pygame.Rect) -> None:
        """Update graph rect reference after resize."""
        self.graph_rect = graph_rect

    def update_graphs(self, spectrum_graph, atmosphere_graph) -> None:
        """Update graph widget references after resize."""
        self._graphs['spectrum_graph'] = spectrum_graph
        self._graphs['atmosphere_graph'] = atmosphere_graph
