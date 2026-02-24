from dataclasses import dataclass, field
from typing import Any, Optional
import pygame
from game.ui.colors import BUILDER_ITEM_BG, BUILDER_GROUP_BG, BUILDER_TREE_LINE


@dataclass
class ComponentItemContext:
    """
    Bundles common dependencies for component list items.

    Reduces constructor parameter count by grouping:
    - manager: pygame_gui UIManager
    - container: Parent UI container
    - width: Available width for the item
    - sprite_mgr: Sprite manager for component icons
    - event_handler: Handler for item actions
    - config: Layout configuration
    """
    manager: Any  # pygame_gui.UIManager
    container: Any  # pygame_gui container
    width: int
    sprite_mgr: Any  # SpriteManager
    event_handler: Any  # Event handler with handle_item_action method
    config: 'StructurePanelLayoutConfig' = None

    def __post_init__(self):
        if self.config is None:
            self.config = StructurePanelLayoutConfig()


@dataclass
class StructurePanelLayoutConfig:
    """Central configuration for Ship Structure Panel layout."""
    
    # Row Dimensions
    ROW_HEIGHT: int = 30
    HEADER_HEIGHT: int = 30
    LAYER_ROW_HEIGHT: int = 40
    
    # Icons
    ICON_SIZE: int = 20
    LAYER_ICON_SIZE: int = 32
    
    # Indentation and Spacing
    INDENT_STEP: int = 25
    LABEL_OFFSET_X: int = 50
    LAYER_NAME_OFFSET_X: int = 65
    
    # Field Widths
    STATS_WIDTH: int = 200
    NAME_WIDTH: int = 220
    MASS_WIDTH: int = 60
    PCT_WIDTH: int = 50
    
    # Colors - imported from game.ui.colors for centralization
    BG_COLOR_INDIVIDUAL: str = BUILDER_ITEM_BG
    BG_COLOR_GROUP: str = BUILDER_GROUP_BG
    SELECTION_COLOR: tuple = (68, 136, 221, 50)  # Primary Accent with alpha
    TREE_LINE_COLOR: str = BUILDER_TREE_LINE
    
    # Panel Anchors (Standardized)
    ANCHOR_TOP_LEFT: dict = None
    ANCHOR_TOP_RIGHT: dict = None
    
    def __post_init__(self):
        self.ANCHOR_TOP_LEFT = {'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        self.ANCHOR_TOP_RIGHT = {'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
