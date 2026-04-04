"""UI layout and sizing configuration.

This module consolidates UI magic numbers that were scattered across screens.
When adding new UI code, check here for existing constants before creating
hardcoded values. When migrating existing code, replace magic numbers with
these constants.

Usage:
    from game.ui.config import UIConfig
    toast_rect = pygame.Rect(0, 0, UIConfig.TOAST_WIDTH, UIConfig.TOAST_HEIGHT)

See also:
    - game.ui.screens.builder_utils: Builder-specific layout constants
"""


class UIConfig:
    """UI layout and sizing configuration."""

    # Default panel margins
    PANEL_PADDING: int = 5

    # Panel gaps and spacing
    PANEL_GAP: int = 5
    ELEMENT_SPACING: int = 20
    INDENT: int = 20

    # Toast notification dimensions
    TOAST_WIDTH: int = 300
    TOAST_HEIGHT: int = 60

    # Confirmation dialog dimensions
    CONFIRM_DIALOG_WIDTH: int = 400
    CONFIRM_DIALOG_HEIGHT: int = 200

    # Font sizes (pygame.font.Font None-font sizes)
    FONT_TITLE: int = 28
    FONT_NAME: int = 22
    FONT_STAT: int = 18
    # Battle screen panel dimensions
    STATS_PANEL_WIDTH: int = 900
    SEEKER_PANEL_WIDTH: int = 300

    # Strategy screen dimensions
    STRATEGY_SIDEBAR_WIDTH: int = 600

    # Progress/stat bar dimensions
    BAR_WIDTH: int = 200
    BAR_HEIGHT: int = 10
    BANNER_HEIGHT: int = 22

    # Ship entry dimensions in panels
    SHIP_ENTRY_HEIGHT: int = 25

    # Panel transparency (alpha values 0-255)
    PANEL_ALPHA: int = 230

    # Battle screen
    GRID_SPACING: int = 5000
    TRAIL_LENGTH: int = 100

    # Common dimensions
    ROW_HEIGHT_STANDARD: int = 40
    ROW_HEIGHT_LARGE: int = 50
    SIDEBAR_WIDTH: int = 300
    HEADER_HEIGHT: int = 40
