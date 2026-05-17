"""
Workshop Context Configuration

Defines how the Design Workshop is launched and what features are available.
Supports two modes:
1. STANDALONE: Development/testing mode with tech preset selection
2. INTEGRATED: Strategy layer integration with empire context

PROJ-38: Added registries parameter for dependency injection.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.strategy.facade.slices._facade_state import FacadeSessionState


class WorkshopMode(Enum):
    """Launch mode for Design Workshop."""
    STANDALONE = "standalone"
    INTEGRATED = "integrated"


@dataclass
class WorkshopContext:
    """
    Configuration for how the Design Workshop is launched.

    This context object is passed to DesignWorkshopScreen to determine:
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
        empire_theme_id: Ship theme for the empire (integrated mode only)
        built_designs: Set of design IDs that have been built (prevents overwriting)
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
    empire_theme_id: Optional[str] = None  # Ship theme for the empire in integrated mode
    built_designs: set = field(default_factory=set)  # Design IDs that have been built

    # Return callback
    on_return: Optional[Callable] = None
    return_state: Optional[str] = None  # For app.py state management

    # PROJ-38: Dependency injection for registries
    registries: Optional['GameRegistries'] = None

    # PROJ-411 Phase 1 / QA Obs 3 (2026-05-16) / PROJ-434 Phase 2:
    # Optional reference to the strategy session's FacadeSessionState.
    # When supplied, ``WorkshopShipIO`` resolves the per-empire
    # ``DesignCatalog`` from ``facade_state.session.services.design_catalogs_by_empire``
    # so workshop saves flow through ``catalog.save_design`` and the
    # QA-Obs-3 cache invalidation hits the same in-memory list view the
    # Build Queue reads from. ``None`` for standalone mode (no facade
    # exists) and for legacy construction paths that don't yet thread
    # the live facade through.
    facade_state: Optional['FacadeSessionState'] = None


    @classmethod
    def standalone(cls, tech_preset_name: str = "default",
                   *, registries: 'GameRegistries') -> 'WorkshopContext':
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
            >>> workshop = DesignWorkshopScreen(800, 600, context)
        """
        if registries is None:
            raise ValueError("registries is required for WorkshopContext.standalone()")
        return cls(
            mode=WorkshopMode.STANDALONE,
            tech_preset_name=tech_preset_name,
            registries=registries
        )

    @classmethod
    def integrated(cls,
                   empire_id: int,
                   savegame_path: str,
                   available_tech_ids: Optional[List[str]] = None,
                   built_designs: Optional[set] = None,
                   empire_theme_id: Optional[str] = None,
                   *,
                   registries: 'GameRegistries',
                   facade_state: Optional['FacadeSessionState'] = None) -> 'WorkshopContext':
        """
        Create integrated workshop context for strategy layer.

        In integrated mode:
        - Debug buttons are hidden
        - Tech is filtered by empire's unlocked tech
        - Designs save/load from savegame's designs/ folder
        - Ship theme is locked to empire's theme
        - Returns to strategy scene

        Args:
            empire_id: ID of the empire designing ships
            savegame_path: Path to current savegame folder
            available_tech_ids: List of tech IDs available to this empire (default: empty list)
            built_designs: Set of design IDs that have been built (default: empty set)
            empire_theme_id: Ship theme for the empire (default: None)
            facade_state: Optional FacadeSessionState from the live strategy
                session. When supplied, ``WorkshopShipIO`` resolves the
                per-empire ``DesignCatalog`` from
                ``facade_state.session.services.design_catalogs_by_empire``;
                ``catalog.save_design`` then refreshes the in-memory list
                view the Build Queue reads from (QA Obs 3 contract,
                PROJ-434 Phase 2).

        Returns:
            WorkshopContext configured for integrated mode

        Example:
            >>> context = WorkshopContext.integrated(
            ...     empire_id=1,
            ...     savegame_path="saves/game1",
            ...     available_tech_ids=["laser_cannon", "railgun"],
            ...     built_designs={"cruiser_mk1"},
            ...     empire_theme_id="Federation"
            ... )
            >>> workshop = DesignWorkshopScreen(800, 600, context)
        """
        if registries is None:
            raise ValueError("registries is required for WorkshopContext.integrated()")
        return cls(
            mode=WorkshopMode.INTEGRATED,
            empire_id=empire_id,
            savegame_path=savegame_path,
            available_tech_ids=available_tech_ids if available_tech_ids is not None else [],
            built_designs=built_designs if built_designs is not None else set(),
            empire_theme_id=empire_theme_id,
            registries=registries,
            facade_state=facade_state,
        )

    def is_standalone(self) -> bool:
        """Check if context is in standalone mode."""
        return self.mode == WorkshopMode.STANDALONE

    def is_integrated(self) -> bool:
        """Check if context is in integrated mode."""
        return self.mode == WorkshopMode.INTEGRATED
