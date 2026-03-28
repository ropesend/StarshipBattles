"""Strategy UI panel creation and layout management.

This module contains factory functions for creating the StrategyUI panel layout
and handling resize operations. Extracted from StrategyUI to reduce god class size.

PROJ-86: God Class Decomposition - UI Tier
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

import pygame
import pygame_gui
import pygame_gui.elements as ui

from game.ui.config import UIConfig
from game.core.input_actions import InputAction
from game.core.paths import Paths
from game.ui.panels.strategy_widgets import SpectrumGraph, AtmosphereGraph
from game.ui.panels.system_tree_panel import SystemTreePanel
from game.ui.screens.strategy_menu_panel import StrategyMenuPanel, PANEL_WIDTH, PANEL_HEIGHT

if TYPE_CHECKING:
    from game.core.input_system import InputMapper


@dataclass
class StrategyWidgets:
    """Container for all StrategyUI widget references.

    Returned by create_strategy_panels() to provide organized access
    to all created widgets.
    """
    # Main panels
    system_panel: Any = None
    sector_panel: Any = None
    detail_panel: Any = None
    top_bar: Any = None
    resource_bar: Any = None

    # System panel widgets
    system_header: Any = None
    system_tree: Any = None

    # Sector panel widgets
    sector_header: Any = None
    sector_tree: Any = None

    # Detail panel widgets
    portrait_image: Any = None
    detail_text: Any = None
    graph_image: Any = None
    graph_rect: pygame.Rect = None
    btn_raw_data: Any = None
    btn_colonize: Any = None
    btn_build_yard: Any = None
    btn_orders: Any = None
    btn_fleet_report: Any = None
    btn_build_fleet: Any = None

    # Top bar widgets
    btn_prev_colony: Any = None
    lbl_colony: Any = None
    btn_next_colony: Any = None
    btn_prev_fleet: Any = None
    lbl_fleet: Any = None
    btn_next_fleet: Any = None
    btn_planets: Any = None
    btn_stars: Any = None
    btn_empire: Any = None
    btn_research: Any = None
    btn_design: Any = None
    btn_build_queues: Any = None
    btn_all_queues: Any = None
    btn_menu: Any = None
    btn_events: Any = None
    btn_next_turn: Any = None
    lbl_current_player: Any = None

    # Resource bar widgets
    lbl_resources: Any = None

    # Graph widgets (non-UI)
    spectrum_graph: Any = None
    atmosphere_graph: Any = None

    # Panel list for show/hide
    panels: list = field(default_factory=list)


def create_strategy_panels(
    manager: pygame_gui.UIManager,
    width: int,
    height: int,
    sidebar_width: int,
    on_ui_selection_callback: callable
) -> StrategyWidgets:
    """Create all StrategyUI panels and widgets.

    Args:
        manager: The pygame_gui UIManager instance.
        width: Screen width.
        height: Screen height.
        sidebar_width: Width of the right sidebar.
        on_ui_selection_callback: Callback for tree panel selection events.

    Returns:
        StrategyWidgets dataclass containing all widget references.
    """
    widgets = StrategyWidgets()

    # --- Right Sidebar Layout (Three Panels) ---
    gap = UIConfig.PANEL_GAP
    panel_h_approx = (height - 20) / 3

    # 1. System Panel (Top)
    rect_system = pygame.Rect(-sidebar_width + 10, 10, sidebar_width - 20, panel_h_approx - gap)

    widgets.system_panel = pygame_gui.elements.UIPanel(
        relative_rect=rect_system,
        manager=manager,
        anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
    )

    widgets.system_header = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(10, 10, sidebar_width - 40, 30),
        text="System: Deep Space",
        manager=manager,
        container=widgets.system_panel
    )

    widgets.system_tree = SystemTreePanel(
        relative_rect=pygame.Rect(10, 40, sidebar_width - 40, rect_system.height - 50),
        manager=manager,
        container=widgets.system_panel
    )
    widgets.system_tree.set_selection_callback(on_ui_selection_callback)

    # 2. Sector Panel (Middle)
    rect_sector = pygame.Rect(-sidebar_width + 10, 10 + panel_h_approx, sidebar_width - 20, panel_h_approx - gap)

    widgets.sector_panel = pygame_gui.elements.UIPanel(
        relative_rect=rect_sector,
        manager=manager,
        anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
    )

    widgets.sector_header = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(10, 10, sidebar_width - 40, 30),
        text="Sector: Unknown",
        manager=manager,
        container=widgets.sector_panel
    )

    widgets.sector_tree = SystemTreePanel(
        relative_rect=pygame.Rect(10, 40, sidebar_width - 40, rect_sector.height - 50),
        manager=manager,
        container=widgets.sector_panel
    )
    widgets.sector_tree.set_selection_callback(on_ui_selection_callback)

    # 3. Detail Panel (Bottom)
    rect_detail = pygame.Rect(-sidebar_width + 10, 10 + 2*panel_h_approx, sidebar_width - 20, panel_h_approx - gap)

    widgets.detail_panel = pygame_gui.elements.UIPanel(
        relative_rect=rect_detail,
        manager=manager,
        anchors={'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
    )

    # Portrait Image
    widgets.portrait_image = pygame_gui.elements.UIImage(
        relative_rect=pygame.Rect(10, 10, 150, 150),
        image_surface=pygame.Surface((150, 150)),
        manager=manager,
        container=widgets.detail_panel
    )

    # Info Text (Right of Portrait)
    text_w = sidebar_width - 180
    text_h = rect_detail.height - 20
    widgets.detail_text = pygame_gui.elements.UITextBox(
        html_text="Select an object for details.",
        relative_rect=pygame.Rect(170, 10, text_w, text_h),
        manager=manager,
        container=widgets.detail_panel
    )

    # Graph Image (Below Portrait)
    graph_y = 170
    graph_h = rect_detail.height - 180
    if graph_h < 50:
        graph_h = 50

    widgets.graph_rect = pygame.Rect(10, graph_y, 150, graph_h)
    widgets.graph_image = pygame_gui.elements.UIImage(
        relative_rect=widgets.graph_rect,
        image_surface=pygame.Surface((150, graph_h)),
        manager=manager,
        container=widgets.detail_panel
    )

    # Raw Data Button (Top Right of Graph Box)
    btn_x = widgets.graph_rect.right - 22
    btn_y = widgets.graph_rect.top + 2

    widgets.btn_raw_data = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(btn_x, btn_y, 20, 20),
        text="",
        manager=manager,
        container=widgets.detail_panel,
        anchors={'left': 'left', 'right': 'left', 'top': 'top', 'bottom': 'top'},
        object_id="@small_icon_button"
    )
    widgets.btn_raw_data.hide()

    # Spectrum and Atmosphere graphs (SWAPPED dimensions for rotation)
    widgets.spectrum_graph = SpectrumGraph(int(widgets.graph_rect.height), int(widgets.graph_rect.width))
    widgets.atmosphere_graph = AtmosphereGraph(int(widgets.graph_rect.height), int(widgets.graph_rect.width))

    # --- Top Bar ---
    widgets.top_bar = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(0, 0, width - sidebar_width, 50),
        manager=manager,
        anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
    )

    button_width = 150
    start_x = 230

    # --- Nav Buttons ---
    # Group 1: Colony (Width ~140)
    widgets.btn_prev_colony = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(start_x, 5, 30, 40), text="<", manager=manager,
        container=widgets.top_bar, object_id='@nav_btn'
    )
    widgets.lbl_colony = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(start_x + 30, 5, 80, 40), text="Colony",
        manager=manager, container=widgets.top_bar
    )
    widgets.btn_next_colony = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(start_x + 110, 5, 30, 40), text=">", manager=manager,
        container=widgets.top_bar, object_id='@nav_btn'
    )

    # Group 2: Fleet (Width ~140)
    fleet_start_x = start_x + 140 + 20

    widgets.btn_prev_fleet = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(fleet_start_x, 5, 30, 40), text="<", manager=manager,
        container=widgets.top_bar, object_id='@nav_btn'
    )
    widgets.lbl_fleet = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(fleet_start_x + 30, 5, 80, 40), text="Fleet",
        manager=manager, container=widgets.top_bar
    )
    widgets.btn_next_fleet = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(fleet_start_x + 110, 5, 30, 40), text=">", manager=manager,
        container=widgets.top_bar, object_id='@nav_btn'
    )

    # --- Main Buttons ---
    main_start_x = fleet_start_x + 140 + 40
    btn_w = 100
    gap = 10

    widgets.btn_planets = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(main_start_x, 5, btn_w, 40), text="Planets",
        manager=manager, container=widgets.top_bar
    )
    widgets.btn_stars = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(main_start_x + 1*(btn_w+gap), 5, btn_w, 40), text="Stars",
        manager=manager, container=widgets.top_bar
    )
    widgets.btn_empire = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(main_start_x + 2*(btn_w+gap), 5, btn_w, 40), text="Empire",
        manager=manager, container=widgets.top_bar
    )
    widgets.btn_research = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(main_start_x + 3*(btn_w+gap), 5, btn_w, 40), text="Research",
        manager=manager, container=widgets.top_bar
    )
    widgets.btn_design = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(main_start_x + 4*(btn_w+gap), 5, btn_w, 40), text="Design",
        manager=manager, container=widgets.top_bar
    )
    widgets.btn_build_queues = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(main_start_x + 5*(btn_w+gap), 5, btn_w, 40), text="Build Yards",
        manager=manager, container=widgets.top_bar
    )
    widgets.btn_all_queues = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(main_start_x + 6*(btn_w+gap), 5, btn_w, 40), text="All Queues",
        manager=manager, container=widgets.top_bar
    )
    widgets.btn_menu = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(main_start_x + 7*(btn_w+gap), 5, btn_w, 40), text="Menu",
        manager=manager, container=widgets.top_bar
    )
    widgets.btn_events = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(main_start_x + 8*(btn_w+gap), 5, btn_w, 40), text="Log",
        manager=manager, container=widgets.top_bar
    )
    widgets.btn_next_turn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(main_start_x + 9*(btn_w+gap), 5, 150, 40), text="End Turn",
        manager=manager, container=widgets.top_bar
    )

    # Player indicator label (far left of top bar)
    widgets.lbl_current_player = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(10, 5, 200, 40), text="Player 1's Turn",
        manager=manager, container=widgets.top_bar
    )

    # Empire resource display (below top bar)
    resource_bar_y = 50
    resource_bar_height = 24
    widgets.resource_bar = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(0, resource_bar_y, width - sidebar_width, resource_bar_height),
        manager=manager,
        anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
    )
    widgets.lbl_resources = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(10, 0, width - sidebar_width - 20, resource_bar_height),
        text="",
        manager=manager,
        container=widgets.resource_bar
    )

    # Contextual Buttons (Detail Panel)
    widgets.btn_colonize = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(220, rect_detail.height - 50, 120, 40),
        text="Colonize",
        manager=manager,
        container=widgets.detail_panel,
        visible=0
    )

    widgets.btn_build_yard = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(350, rect_detail.height - 50, 120, 40),
        text="Build Yard",
        manager=manager,
        container=widgets.detail_panel,
        visible=0
    )

    widgets.btn_orders = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(80, rect_detail.height - 50, 120, 40),
        text="Orders",
        manager=manager,
        container=widgets.detail_panel,
        visible=0
    )

    widgets.btn_fleet_report = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(210, rect_detail.height - 50, 120, 40),
        text="Fleet Report",
        manager=manager,
        container=widgets.detail_panel,
        visible=0
    )

    widgets.btn_build_fleet = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(340, rect_detail.height - 50, 120, 40),
        text="Build",
        manager=manager,
        container=widgets.detail_panel,
        visible=0
    )

    # Panel list for show/hide operations
    widgets.panels = [
        widgets.top_bar,
        widgets.resource_bar,
        widgets.system_panel,
        widgets.sector_panel,
        widgets.detail_panel
    ]

    return widgets


def resize_strategy_panels(
    ui: 'StrategyUI',
    manager: pygame_gui.UIManager,
    width: int,
    height: int,
    sidebar_width: int
) -> None:
    """Handle resize of strategy UI panels.

    Args:
        ui: The StrategyUI instance (for accessing widget references).
        manager: The pygame_gui UIManager instance.
        width: New screen width.
        height: New screen height.
        sidebar_width: Width of the right sidebar.
    """
    panel_h_approx = (height - 20) / 3
    gap = 5

    # System (Top)
    ui.system_panel.set_dimensions((sidebar_width - 20, panel_h_approx - gap))
    ui.system_panel.set_relative_position((-sidebar_width + 10, 10))
    ui.system_tree.set_dimensions((sidebar_width - 40, panel_h_approx - 60))

    # Sector (Middle)
    ui.sector_panel.set_dimensions((sidebar_width - 20, panel_h_approx - gap))
    ui.sector_panel.set_relative_position((-sidebar_width + 10, 10 + panel_h_approx))
    ui.sector_tree.set_dimensions((sidebar_width - 40, panel_h_approx - 60))

    # Detail (Bottom)
    ui.detail_panel.set_dimensions((sidebar_width - 20, panel_h_approx - gap))
    ui.detail_panel.set_relative_position((-sidebar_width + 10, 10 + 2*panel_h_approx))

    # Detail Text (Right side)
    text_w = sidebar_width - 180
    text_h = ui.detail_panel.rect.height - 20
    ui.detail_text.set_dimensions((text_w, text_h))
    ui.detail_text.set_relative_position((170, 10))

    # Graph (Left side, under Portrait)
    graph_y = 170
    graph_h = ui.detail_panel.rect.height - 180
    if graph_h < 50:
        graph_h = 50

    ui.graph_rect = pygame.Rect(10, graph_y, 150, graph_h)
    ui.graph_image.set_dimensions((150, graph_h))
    ui.graph_image.set_relative_position((10, graph_y))

    # Re-init graphs with new size (SWAPPED for rotation)
    ui.spectrum_graph = SpectrumGraph(int(ui.graph_rect.height), int(ui.graph_rect.width))
    ui.atmosphere_graph = AtmosphereGraph(int(ui.graph_rect.height), int(ui.graph_rect.width))

    # Position Raw Data Button: Top-Right of Graph
    btn_x = ui.graph_rect.right - 22
    btn_y = ui.graph_rect.top + 2
    ui.btn_raw_data.set_relative_position((btn_x, btn_y))


def apply_hotkey_tooltips(
    ui: 'StrategyUI',
    input_mapper: Optional['InputMapper']
) -> None:
    """Apply hotkey hint tooltips to strategy UI buttons.

    Uses the InputMapper to look up the display text for each button's
    associated action. If the mapper is None or an action is unbound,
    the button retains its default tooltip (none).

    Args:
        ui: The StrategyUI instance (for accessing button references).
        input_mapper: The InputMapper instance for looking up bindings.
    """
    if not input_mapper:
        return

    # Map buttons to their InputAction
    button_actions = {
        ui.btn_next_turn: InputAction.STRATEGY_NEXT_TURN,
        ui.btn_planets: InputAction.STRATEGY_OPEN_PLANETS,
        ui.btn_empire: InputAction.STRATEGY_OPEN_EMPIRE,
        ui.btn_research: InputAction.STRATEGY_OPEN_RESEARCH,
        ui.btn_design: InputAction.STRATEGY_OPEN_DESIGN,
        ui.btn_build_queues: InputAction.STRATEGY_OPEN_BUILD_QUEUES,
        ui.btn_prev_colony: InputAction.STRATEGY_PREV_COLONY,
        ui.btn_next_colony: InputAction.STRATEGY_NEXT_COLONY,
        ui.btn_prev_fleet: InputAction.STRATEGY_PREV_FLEET,
        ui.btn_next_fleet: InputAction.STRATEGY_NEXT_FLEET,
        ui.btn_colonize: InputAction.FLEET_COLONIZE,
        ui.btn_orders: InputAction.DETAIL_PANEL_ORDERS,
        ui.btn_fleet_report: InputAction.DETAIL_PANEL_FLEET_REPORT,
        ui.btn_build_fleet: InputAction.DETAIL_PANEL_BUILD,
    }

    for btn, action in button_actions.items():
        hint = input_mapper.get_display_text(action)
        if hint:
            btn.set_tooltip(hint)
