from dataclasses import dataclass
import pygame

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
    
    # Colors
    BG_COLOR_INDIVIDUAL: str = "#151515"
    BG_COLOR_GROUP: str = "#202020"
    SELECTION_COLOR: tuple = (80, 100, 130, 120)
    
    # Panel Anchors (Standardized)
    ANCHOR_TOP_LEFT: dict = None
    ANCHOR_TOP_RIGHT: dict = None
    
    def __post_init__(self):
        self.ANCHOR_TOP_LEFT = {'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        self.ANCHOR_TOP_RIGHT = {'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
