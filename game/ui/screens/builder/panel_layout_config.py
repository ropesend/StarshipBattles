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
    
    # Field Widths
    STATS_WIDTH: int = 200
    NAME_WIDTH: int = 220
    MASS_WIDTH: int = 60
    PCT_WIDTH: int = 50
    
    # Colors
    # Colors
    BG_COLOR_INDIVIDUAL: str = "#1a1e26" 
    BG_COLOR_GROUP: str = "#202530" # Slightly lighter than individual? No, usually group headers are darker or distinct. Let's use #14181f (Dark) for group background or keep it distinct. 
    # Actually, style guide says: "Dark Background: Panel interiors". 
    # Let's use Base (#1a1e26) for Individual (standard panel items).
    # And Dark (#14181f) for Group/Layer headers? Or Elevated (#1e2530)?
    # Existing was Individual #151515 (Darker), Group #202020 (Lighter).
    # Let's try: Individual: #1a1e26 (Base), Group: #1e2530 (Elevated) or #14181f (Deep).
    # Let's use #14181f for Individual (deeper) and #1a1e26 for Group (base).
    BG_COLOR_INDIVIDUAL: str = "#14181f" 
    BG_COLOR_GROUP: str = "#1a1e26"
    SELECTION_COLOR: tuple = (68, 136, 221, 50) # Primary Accent with alpha
    TREE_LINE_COLOR: str = "#2a3545" # Normal Border
    
    # Panel Anchors (Standardized)
    ANCHOR_TOP_LEFT: dict = None
    ANCHOR_TOP_RIGHT: dict = None
    
    def __post_init__(self):
        self.ANCHOR_TOP_LEFT = {'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'top'}
        self.ANCHOR_TOP_RIGHT = {'left': 'right', 'right': 'right', 'top': 'top', 'bottom': 'top'}
