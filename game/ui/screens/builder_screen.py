"""
DEPRECATED: Use workshop_screen.py instead.
This file provides backward compatibility aliases and maintains import namespace for test mocking.
"""

# Import everything that workshop_screen imports so tests can mock them at this module level
import math
import tkinter
from tkinter import simpledialog, filedialog
import os
import pygame
import pygame_gui
from pygame_gui.elements import (
    UIPanel, UILabel, UIButton, UIDropDownMenu,
    UITextEntryLine, UISelectionList, UIWindow
)
from pygame_gui.windows import UIConfirmationDialog
from game.core.profiling import profile_action, profile_block
from game.simulation.entities.ship import LayerType
from game.core.registry import RegistryManager, get_component_registry, get_modifier_registry, get_vehicle_classes
from game.simulation.components.component import get_all_components
from game.ui.renderer.sprites import SpriteManager
from game.simulation.preset_manager import PresetManager
from game.simulation.systems.persistence import ShipIO
from game.ui.panels.builder_widgets import ModifierEditorPanel
from game.simulation.ship_theme import ShipThemeManager
from ui.builder import BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel, LayerPanel
from ui.builder.schematic_view import SchematicView
from ui.builder.interaction_controller import InteractionController
from ui.builder.event_bus import EventBus
from game.ui.screens.builder_utils import PANEL_WIDTHS, PANEL_HEIGHTS, MARGINS, BuilderEvents, calculate_dynamic_layer_width
from game.core.screenshot_manager import ScreenshotManager
from game.ui.screens.workshop_event_router import WorkshopEventRouter as BuilderEventRouter
from game.ui.screens.workshop_data_loader import WorkshopDataLoader as BuilderDataLoader
from game.ui.screens.workshop_viewmodel import WorkshopViewModel as BuilderViewModel
from game.ui.screens.builder_selection import process_selection_change, get_primary_selection
from ui.colors import COLORS
from game.core.logger import log_error, log_info, log_warning, log_debug
from ui.builder.detail_panel import ComponentDetailPanel

# Import the main class and context
from game.ui.screens.workshop_screen import DesignWorkshopGUI
from game.ui.screens.workshop_context import WorkshopContext


# Wrapper class for backward compatibility with old signature
class BuilderSceneGUI:
    """
    DEPRECATED: Backward compatibility wrapper for DesignWorkshopGUI.

    Old code calls: BuilderSceneGUI(width, height, on_return_callback)
    New code calls: DesignWorkshopGUI(width, height, WorkshopContext(...))

    This wrapper creates a default standalone context and delegates to DesignWorkshopGUI.
    """
    # Copy class-level method references for tests that use unbound methods
    _load_ship = DesignWorkshopGUI._load_ship
    _save_ship = DesignWorkshopGUI._save_ship
    _clear_design = DesignWorkshopGUI._clear_design
    update_stats = DesignWorkshopGUI.update_stats
    rebuild_modifier_ui = DesignWorkshopGUI.rebuild_modifier_ui
    on_selection_changed = DesignWorkshopGUI.on_selection_changed

    # Copy properties for backward compatibility
    @property
    def ship(self):
        """Proxy property for backward compatibility - delegates to ViewModel."""
        return self.viewmodel.ship

    @ship.setter
    def ship(self, value):
        self.viewmodel.ship = value

    @property
    def template_modifiers(self):
        """Proxy property for backward compatibility - delegates to ViewModel."""
        return self.viewmodel.template_modifiers

    @template_modifiers.setter
    def template_modifiers(self, value):
        self.viewmodel.template_modifiers = value

    @property
    def selected_components(self):
        """Proxy property for backward compatibility - delegates to ViewModel."""
        return self.viewmodel.selected_components

    @selected_components.setter
    def selected_components(self, value):
        # Direct assignment to internal list for backward compat
        self.viewmodel._selected_components = value

    @property
    def selected_component(self):
        """Proxy property for backward compatibility - delegates to controller."""
        # Handle case where controller doesn't exist (test __new__ pattern)
        if not hasattr(self, 'controller'):
            return None
        return self.controller.selected_component

    @selected_component.setter
    def selected_component(self, value):
        if hasattr(self, 'controller'):
            self.controller.selected_component = value

    def __init__(self, screen_width, screen_height, on_start_battle, context=None):
        """
        Initialize BuilderSceneGUI wrapper.

        Args:
            screen_width: Screen width
            screen_height: Screen height
            on_start_battle: Callback when returning from workshop
            context: Optional WorkshopContext. If None, creates standalone context.
        """
        # Use provided context or create standalone context
        if context is None:
            context = WorkshopContext.standalone(tech_preset_name="default")

        context.on_return = on_start_battle

        # Create the real workshop GUI
        self._workshop = DesignWorkshopGUI(screen_width, screen_height, context)

    def __getattr__(self, name):
        """
        Delegate all attribute access to the wrapped workshop instance.

        This is called only when attribute lookup fails on the instance and class dictionaries.
        """
        # Prevent infinite recursion if _workshop doesn't exist
        if name == '_workshop':
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '_workshop'")

        # Try to delegate to wrapped workshop
        try:
            workshop = object.__getattribute__(self, '_workshop')
        except AttributeError:
            # _workshop doesn't exist - instance created with __new__ without __init__
            # This happens in tests - just raise AttributeError
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        return getattr(workshop, name)

    def __setattr__(self, name, value):
        """
        Intercept attribute setting to handle test mocking patterns.

        Tests often do: gui.ship = MagicMock()
        We need to set this on the wrapped workshop, not create instance attributes.
        """
        # Special handling for initialization
        if name == '_workshop':
            object.__setattr__(self, name, value)
            return

        # If _workshop exists, delegate to it (for test mocking compatibility)
        try:
            workshop = object.__getattribute__(self, '_workshop')
            # Delegate setting to the wrapped workshop
            setattr(workshop, name, value)
        except AttributeError:
            # _workshop doesn't exist yet (during __init__ or test __new__)
            # Set as instance attribute
            object.__setattr__(self, name, value)


# Explicit re-exports
__all__ = ['BuilderSceneGUI', 'BuilderViewModel', 'BuilderEventRouter', 'BuilderDataLoader']
