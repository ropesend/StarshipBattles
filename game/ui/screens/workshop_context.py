"""
Workshop Context Configuration

Defines how the Design Workshop is launched and what features are available.
Supports two modes:
1. STANDALONE: Development/testing mode with tech preset selection
2. INTEGRATED: Strategy layer integration with empire context
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Callable


class WorkshopMode(Enum):
    """Launch mode for Design Workshop."""
    STANDALONE = "standalone"
    INTEGRATED = "integrated"


@dataclass
class WorkshopContext:
    """
    Configuration for how the Design Workshop is launched.

    This context object is passed to DesignWorkshopGUI to determine:
    - Which UI buttons are visible
    - How tech filtering works (preset vs empire tech)
    - Where designs are saved/loaded from
    - How to return to the calling screen

    Attributes:
        mode: Whether workshop is standalone or integrated with strategy layer
        tech_preset_name: Tech preset to use (standalone mode only)
        available_tech_ids: List of unlocked tech IDs (integrated mode only)
        empire_id: Current empire ID (integrated mode only)
        savegame_path: Path to save designs (integrated mode only)
        on_return: Callback function to call when exiting workshop
        return_state: App state to return to (for app.py state machine)
    """
    mode: WorkshopMode

    # Tech system
    tech_preset_name: Optional[str] = None  # For standalone mode
    available_tech_ids: Optional[List[str]] = None  # For integrated mode

    # Strategy integration
    empire_id: Optional[int] = None  # Current empire in integrated mode
    savegame_path: Optional[str] = None  # Path to save designs in integrated mode

    # Return callback
    on_return: Optional[Callable] = None
    return_state: Optional[str] = None  # For app.py state management

    @classmethod
    def standalone(cls, tech_preset_name: str = "default") -> 'WorkshopContext':
        """
        Create standalone workshop context for development/testing.

        In standalone mode:
        - All debug buttons are visible
        - Tech is filtered by preset (e.g., "early_game", "default")
        - Designs save/load from global ships/ folder
        - Returns to main menu

        Args:
            tech_preset_name: Name of tech preset to use (default: "default")

        Returns:
            WorkshopContext configured for standalone mode

        Example:
            >>> context = WorkshopContext.standalone(tech_preset_name="early_game")
            >>> workshop = DesignWorkshopGUI(800, 600, context)
        """
        return cls(
            mode=WorkshopMode.STANDALONE,
            tech_preset_name=tech_preset_name
        )

    @classmethod
    def integrated(cls,
                   empire_id: int,
                   savegame_path: str,
                   available_tech_ids: Optional[List[str]] = None) -> 'WorkshopContext':
        """
        Create integrated workshop context for strategy layer.

        In integrated mode:
        - Debug buttons are hidden
        - Tech is filtered by empire's unlocked tech
        - Designs save/load from savegame's designs/ folder
        - Returns to strategy scene

        Args:
            empire_id: ID of the empire designing ships
            savegame_path: Path to current savegame folder
            available_tech_ids: List of tech IDs available to this empire (default: empty list)

        Returns:
            WorkshopContext configured for integrated mode

        Example:
            >>> context = WorkshopContext.integrated(
            ...     empire_id=1,
            ...     savegame_path="saves/game1",
            ...     available_tech_ids=["laser_cannon", "railgun"]
            ... )
            >>> workshop = DesignWorkshopGUI(800, 600, context)
        """
        return cls(
            mode=WorkshopMode.INTEGRATED,
            empire_id=empire_id,
            savegame_path=savegame_path,
            available_tech_ids=available_tech_ids if available_tech_ids is not None else []
        )

    def is_standalone(self) -> bool:
        """Check if context is in standalone mode."""
        return self.mode == WorkshopMode.STANDALONE

    def is_integrated(self) -> bool:
        """Check if context is in integrated mode."""
        return self.mode == WorkshopMode.INTEGRATED
