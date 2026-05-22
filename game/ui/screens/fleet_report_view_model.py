"""
Fleet List View Model - Manages filtering, sorting, and ship list state.

PROJ-44 Phase 7 Task 7.4: Extracted from FleetReportWindow for testability.
PROJ-220: Replaced 16 binary filter attributes with FilterStateManager.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Any

from game.ui.filters.filter_state import FilterState
from game.ui.filters.filter_state_manager import FilterStateManager
from game.ui.screens.fleet_report_filters import filter_ships, sort_ships

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance

# Tri-state filter attribute labels for display
_TRI_STATE_LABELS = {
    'warp_capable': 'Warp Capable',
    'has_spaceyard': 'Has Spaceyard',
    'has_cargo': 'Has Cargo',
    'destroy_planet': 'Destroy Planet',
    'open_warp': 'Open Warp',
    'close_warp': 'Close Warp',
    'destroy_star': 'Destroy Star',
    'create_sphere': 'Create Sphere',
}

# Status filter labels for display
_STATUS_LABELS = {
    'damaged': 'Damaged',
    'undamaged': 'Undamaged',
    'derelict': 'Derelict',
    'destroyed': 'Destroyed',
}


class FleetListViewModel:
    """Manages ship list state for FleetReportWindow.

    Handles:
    - Tri-state filter state via FilterStateManager (warp, spaceyard, cargo, special caps)
    - Status filter state (damaged, undamaged, derelict, destroyed) as bools
    - Sort state (column and direction)
    - Filtering and sorting ships
    """

    def __init__(self, ships: List[ShipInstance] = None):
        self._ships = ships or []

        # PROJ-475 Phase 2 Task 2.6: facade-projected ``instance_id ->
        # has_spaceyard`` map. The report runs on raw ``ShipInstance`` lists,
        # so the spaceyard column / filter / sort consult this bridge instead
        # of calling ``FleetCapabilityCalculator`` in the UI. Empty until the
        # window sets it from ``facade.fleets.get(fleet_id).ships``.
        self._spaceyard_lookup: Dict[str, bool] = {}

        # Status filters (4-state, not binary — kept as bools)
        self.filter_show_damaged = True
        self.filter_show_undamaged = True
        self.filter_show_derelict = True
        self.filter_show_destroyed = False  # Destroyed hidden by default

        # Tri-state filters via FilterStateManager
        self._filter_mgr = FilterStateManager({
            'warp_capable': FilterState.IGNORE,
            'has_spaceyard': FilterState.IGNORE,
            'has_cargo': FilterState.IGNORE,
            'destroy_planet': FilterState.IGNORE,
            'open_warp': FilterState.IGNORE,
            'close_warp': FilterState.IGNORE,
            'destroy_star': FilterState.IGNORE,
            'create_sphere': FilterState.IGNORE,
        })

        # Sort state
        self.sort_column_id = 'serial'
        self.sort_descending = False

        # Cached filtered list
        self._filtered_ships: List[ShipInstance] = []
        self._needs_refresh = True

    @property
    def filter_manager(self) -> FilterStateManager:
        """Access the tri-state filter manager."""
        return self._filter_mgr

    def update_ships(self, ships: List[ShipInstance]) -> None:
        """Update the source ship list."""
        self._ships = ships or []
        self._needs_refresh = True

    def set_spaceyard_lookup(self, lookup: Dict[str, bool]) -> None:
        """Set the facade-projected ``instance_id -> has_spaceyard`` map.

        PROJ-475 Phase 2 Task 2.6. Called by the window after fetching
        ``facade.fleets.get(fleet_id)``; the spaceyard filter / sort / column
        formatter read through :meth:`has_spaceyard`.
        """
        self._spaceyard_lookup = dict(lookup or {})
        self._needs_refresh = True

    def has_spaceyard(self, instance_id: str) -> bool:
        """Whether the ship has a spaceyard, per the facade-projected lookup."""
        return bool(self._spaceyard_lookup.get(instance_id, False))

    def toggle_filter(self, filter_id: str) -> bool:
        """Toggle a status filter on/off. For tri-state, use set_filter_state().

        Args:
            filter_id: Status filter identifier ('damaged', 'undamaged', 'derelict', 'destroyed')

        Returns:
            New filter state (True = showing, False = hiding)
        """
        if filter_id == 'damaged':
            self.filter_show_damaged = not self.filter_show_damaged
            result = self.filter_show_damaged
        elif filter_id == 'undamaged':
            self.filter_show_undamaged = not self.filter_show_undamaged
            result = self.filter_show_undamaged
        elif filter_id == 'derelict':
            self.filter_show_derelict = not self.filter_show_derelict
            result = self.filter_show_derelict
        elif filter_id == 'destroyed':
            self.filter_show_destroyed = not self.filter_show_destroyed
            result = self.filter_show_destroyed
        else:
            return False

        self._needs_refresh = True
        return result

    def set_filter_state(self, attribute: str, state: FilterState) -> None:
        """Set a tri-state filter to a specific state.

        Args:
            attribute: Filter attribute name (e.g., 'warp_capable', 'has_cargo')
            state: New FilterState value
        """
        self._filter_mgr.set_state(attribute, state)
        self._needs_refresh = True

    def get_tri_state(self, attribute: str) -> FilterState:
        """Get the current FilterState for a tri-state filter attribute."""
        return self._filter_mgr.get_state(attribute)

    def set_sort(self, column_id: str) -> None:
        """Set sort column. If same column, toggles direction."""
        if self.sort_column_id == column_id:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column_id = column_id
            self.sort_descending = False
        self._needs_refresh = True

    def get_filter_state(self) -> Dict[str, Any]:
        """Get current filter state as dict for filter_ships function.

        Returns dict with status filter bools and tri-state FilterState values.
        """
        state: Dict[str, Any] = {
            'show_damaged': self.filter_show_damaged,
            'show_undamaged': self.filter_show_undamaged,
            'show_derelict': self.filter_show_derelict,
            'show_destroyed': self.filter_show_destroyed,
        }
        state.update(self._filter_mgr.get_all_states())
        return state

    def get_filtered_ships(self) -> List[ShipInstance]:
        """Get filtered and sorted ship list."""
        if self._needs_refresh:
            self._refresh()
        return self._filtered_ships

    def _refresh(self) -> None:
        """Refresh the filtered/sorted ship list."""
        filtered = filter_ships(
            self._ships,
            self.get_filter_state(),
            spaceyard_lookup=self._spaceyard_lookup,
        )
        self._filtered_ships = sort_ships(
            filtered,
            self.sort_column_id,
            self.sort_descending,
            spaceyard_lookup=self._spaceyard_lookup,
        )
        self._needs_refresh = False

    def get_ship_count(self) -> int:
        """Get count of filtered ships."""
        return len(self.get_filtered_ships())

    def get_total_ship_count(self) -> int:
        """Get total ship count (unfiltered)."""
        return len(self._ships)

    def get_filter_label(self, filter_id: str) -> str:
        """Get display label for a filter attribute."""
        if filter_id in _STATUS_LABELS:
            return _STATUS_LABELS[filter_id]
        if filter_id in _TRI_STATE_LABELS:
            return _TRI_STATE_LABELS[filter_id]
        return filter_id
