"""PROJ-282 Phase 3: `BattleSetupViewModel`.

View state for `FleetBattleSetupScreen`: selection indices, scanned
design data, and small derived helpers used by renderer + input handler.

Pure data — no pygame imports. Mirrors the TestLab MVVM pattern
(`game/ui/screens/test_lab/viewmodel.py`) at reduced scope — PROJ-282
doesn't need the EventBus layer because the screen still rebuilds the
pygame_gui tree on every mutation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class BattleSetupViewModel:
    """Mutable view state for the fleet-based battle setup screen.

    Holds only selection/derived state. Business data lives on
    `BattleSetupState`; UI elements live on the renderer.

    Constructed in isolation for unit tests — no state or registries
    required. Attributes are plain dataclass fields (mutable).
    """

    # Which side (team) is currently being edited.
    active_side: int = 0

    # Index into `state.sides[active_side].fleets`.
    active_fleet_index: int = 0

    # Current selection within the active fleet's hierarchy.
    # `None` means nothing selected at that level.
    selected_tf_index: Optional[int] = None
    selected_sq_index: Optional[int] = None
    selected_ship_index: Optional[int] = None

    # Ship designs discovered on disk by the controller's `_scan_designs`.
    # Consumers iterate this list to build the right-panel design library.
    available_designs: List[Any] = field(default_factory=list)

    # --- helpers ----------------------------------------------------------

    def clear_selection(self) -> None:
        """Reset TF/SQ/ship selection. Called when active side or fleet
        changes — selection doesn't carry across those boundaries."""
        self.selected_tf_index = None
        self.selected_sq_index = None
        self.selected_ship_index = None

    def has_tf_selection(self) -> bool:
        return self.selected_tf_index is not None

    def has_sq_selection(self) -> bool:
        return (
            self.selected_tf_index is not None
            and self.selected_sq_index is not None
        )
