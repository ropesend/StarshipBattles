# game/ui/screens/builder_utils.py
"""
Centralized layout constants for Ship Builder UI.

This module provides a single source of truth for all panel dimensions,
spacing, and layout configuration across the Ship Builder screen.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class PanelWidths:
    """Fixed panel widths (in pixels)."""
    component_palette: int = 400   # Left panel - component selection
    layer_panel: int = 400         # Layer/structure view
    right_panel: int = 750         # Ship stats and portrait
    detail_panel: int = 500        # Component detail overlay


@dataclass(frozen=True)
class PanelHeights:
    """Fixed panel heights (in pixels)."""
    bottom_bar: int = 60           # Bottom button bar
    weapons_report: int = 500      # Weapons report panel
    modifier_panel: int = 360      # Modifier editor at bottom


@dataclass(frozen=True)
class Margins:
    """Standard spacing values."""
    edge: int = 20                 # Edge padding from screen borders
    gutter: int = 10               # Gap between adjacent panels
    section: int = 20              # Space between logical sections


@dataclass(frozen=True)
class BuilderSpacing:
    """Standard spacing values for builder UI."""
    EDGE: int = 10
    SMALL: int = 5
    MEDIUM: int = 10
    LARGE: int = 20


@dataclass(frozen=True)
class BuilderButtons:
    """Standard button sizes for builder UI."""
    HEIGHT_SMALL: int = 25
    HEIGHT_MEDIUM: int = 30
    HEIGHT_LARGE: int = 40


# Singleton instances for easy import
PANEL_WIDTHS = PanelWidths()
PANEL_HEIGHTS = PanelHeights()
MARGINS = Margins()
BUILDER_SPACING = BuilderSpacing()
BUILDER_BUTTONS = BuilderButtons()


def calculate_center_width(screen_width: int) -> int:
    """
    Calculate available width for center content area.
    
    Args:
        screen_width: Total screen width in pixels
        
    Returns:
        Available width between left palette and right stats panel
    """
    return screen_width - PANEL_WIDTHS.component_palette - PANEL_WIDTHS.right_panel


def calculate_schematic_rect(screen_width: int, screen_height: int):
    """
    Calculate the rect for the schematic view.
    
    Args:
        screen_width: Total screen width
        screen_height: Total screen height
        
    Returns:
        pygame.Rect for the schematic view area
    """
    import pygame
    
    x = PANEL_WIDTHS.component_palette + PANEL_WIDTHS.layer_panel
    y = 0
    width = screen_width - x - PANEL_WIDTHS.right_panel
    height = screen_height - PANEL_HEIGHTS.bottom_bar - PANEL_HEIGHTS.weapons_report
    
    return pygame.Rect(x, y, width, height)


def calculate_dynamic_layer_width(screen_width: int) -> int:
    """
    Calculate a responsive layer panel width based on available space.
    
    For very wide screens (>1920px), the layer panel can grow slightly.
    For narrower screens, it maintains minimum usability.
    
    Args:
        screen_width: Total screen width
        
    Returns:
        Dynamic layer panel width
    """
    center = calculate_center_width(screen_width)
    
    # Layer panel takes 30% of center, capped between 300-500px
    dynamic_width = int(center * 0.3)
    return max(300, min(500, dynamic_width))


# Event types for UI synchronization
class BuilderEvents:
    """Event type constants for the Builder EventBus."""
    SHIP_UPDATED = 'SHIP_UPDATED'
    SELECTION_CHANGED = 'SELECTION_CHANGED'
    REGISTRY_RELOADED = 'REGISTRY_RELOADED'
    TEMPLATE_MODIFIERS_CHANGED = 'TEMPLATE_MODIFIERS_CHANGED'
    DRAG_STATE_CHANGED = 'DRAG_STATE_CHANGED'
    HULL_LAYER_VISIBILITY_CHANGED = 'HULL_LAYER_VISIBILITY_CHANGED'
