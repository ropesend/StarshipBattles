"""ViewModel for ``TransferDialog`` (PROJ-328 Phase C).

Pure-Python state and logic for the cargo/population transfer dialog:

* Source/target dropdown selection state.
* Pending-transfer math (per-cargo-key signed integer; MAX sentinels).
* Row construction from FleetInfo / PlanetInfo DTOs (resources +
  per-species population + drop-pod designs).
* Pending-transfer formatting for label display.

No pygame, no pygame_gui. Construct + drive freely in tests without
``bypass_init``.

Per the consensus refactor plan
(``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``)
TransferDialog is the highest-risk single class — the class-by-class
table prescribes "split pending-transfer state and row data into a
ViewModel".
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


# All resource types in display order.
RESOURCE_TYPES = [
    "metals", "organics", "vapors", "radioactives", "exotics",
    "fuel", "energy", "ammo",
]

RESOURCE_DISPLAY_NAMES = {
    "metals": "Metals", "organics": "Organics", "vapors": "Vapors",
    "radioactives": "Radioactives", "exotics": "Exotics",
    "fuel": "Fuel", "energy": "Energy", "ammo": "Ammo",
}


class TransferViewModel:
    """Pure-data ViewModel for the transfer dialog.

    Owns:

    * ``available_sources`` / ``available_targets`` — list of
      ``{label, type, id}`` dicts the dropdowns render.
    * ``current_source`` / ``current_target`` — currently selected
      entries (or ``None``).
    * ``pending_transfers`` — ``cargo_key -> signed amount`` map.
      Positive = load (target → fleet), negative = drop (fleet →
      target). Sentinel values ``MAX_LOAD`` / ``MAX_DROP`` mean
      "transfer all available at execution time".
    * ``row_data`` — current grid rows (each ``{cargo_key,
      display_name, source_amt, target_amt}``).
    * ``filter_empty`` — when True, ``visible_rows`` excludes rows
      with both source and target amount of 0.
    * ``all_pod_names`` — known drop-pod design names that should
      always show (even at 0/0).
    """

    # Sentinel values for "transfer all available". The engine
    # convention is amount=0 meaning all-available; the dialog needs
    # a distinguishable in-memory marker so the user can see "Load
    # Max" before confirming. ``float('inf')`` is intentional — any
    # numeric arrow click falls back into normal int territory after
    # the sentinel check resets it to 0.
    MAX_LOAD: float = float("inf")
    MAX_DROP: float = float("-inf")

    def __init__(self, all_pod_names: Optional[List[str]] = None) -> None:
        self.available_sources: List[dict] = []
        self.available_targets: List[dict] = []
        self.current_source: Optional[dict] = None
        self.current_target: Optional[dict] = None

        self.pending_transfers: Dict[str, Any] = {}
        self.row_data: List[dict] = []
        self.filter_empty: bool = False
        self.all_pod_names: List[str] = list(all_pod_names or [])

    # ------------------------------------------------------------------
    # Pending-transfer math
    # ------------------------------------------------------------------

    def apply_arrow(self, cargo_key: str, delta: int) -> Any:
        """Adjust pending transfer by ``delta``.

        If currently at MAX_LOAD / MAX_DROP, reset to 0 first then
        add ``delta`` — clicking a small-increment arrow after Max
        should move from "all" to a specific small amount, not add
        on top of infinity.

        Returns the new value.
        """
        current = self.pending_transfers.get(cargo_key, 0)
        if current in (self.MAX_LOAD, self.MAX_DROP):
            current = 0
        new_value = current + delta
        self.pending_transfers[cargo_key] = new_value
        return new_value

    def apply_max(self, cargo_key: str, direction: str) -> Any:
        """Set pending to MAX_LOAD or MAX_DROP for ``cargo_key``.

        ``direction`` is ``'load'`` or ``'drop'``. Returns the new
        sentinel value.
        """
        if direction == "load":
            self.pending_transfers[cargo_key] = self.MAX_LOAD
        else:
            self.pending_transfers[cargo_key] = self.MAX_DROP
        return self.pending_transfers[cargo_key]

    def set_pending_zero(self, cargo_key: str) -> None:
        """Reset pending for one cargo key to 0."""
        self.pending_transfers[cargo_key] = 0

    def clear_all_pending(self) -> None:
        """Reset every existing pending entry to 0."""
        for key in self.pending_transfers:
            self.pending_transfers[key] = 0

    def reset_pending(self) -> None:
        """Drop the pending dict entirely (used when source/target
        changes — old transfers no longer make sense)."""
        self.pending_transfers.clear()

    def get_pending(self, cargo_key: str) -> Any:
        """Return current pending value for ``cargo_key`` (default 0)."""
        return self.pending_transfers.get(cargo_key, 0)

    @classmethod
    def format_pending(cls, amount: Any) -> str:
        """Format a pending amount for label display."""
        if amount == cls.MAX_LOAD:
            return "Load Max"
        if amount == cls.MAX_DROP:
            return "Drop Max"
        if isinstance(amount, (int, float)) and amount > 0:
            return f"Load {int(amount)}"
        if isinstance(amount, (int, float)) and amount < 0:
            return f"Drop {int(abs(amount))}"
        return "0"

    def toggle_filter_empty(self) -> bool:
        """Flip ``filter_empty`` and return the new value."""
        self.filter_empty = not self.filter_empty
        return self.filter_empty

    # ------------------------------------------------------------------
    # Source/target selection
    # ------------------------------------------------------------------

    def set_sources(self, sources: List[dict]) -> None:
        """Replace the available-sources list."""
        self.available_sources = list(sources)

    def select_source(self, label: str) -> Optional[dict]:
        """Select a source by label.

        Side-effect: rebuilds ``available_targets`` to exclude the
        selected source, and selects the first remaining target as
        ``current_target``. Returns the new ``current_source`` (or
        ``None`` if label not found).
        """
        source = next(
            (s for s in self.available_sources if s["label"] == label),
            None,
        )
        if source is None:
            return None
        self.current_source = source
        self.available_targets = [
            s for s in self.available_sources if s["label"] != label
        ]
        if self.available_targets:
            self.current_target = self.available_targets[0]
        else:
            self.current_target = None
        return source

    def select_target(self, label: str) -> Optional[dict]:
        """Select a target by label. Returns ``current_target``."""
        self.current_target = next(
            (t for t in self.available_targets if t["label"] == label),
            None,
        )
        return self.current_target

    def target_labels(self) -> List[str]:
        return [t["label"] for t in self.available_targets]

    def source_labels(self) -> List[str]:
        return [s["label"] for s in self.available_sources]

    # ------------------------------------------------------------------
    # Row building
    # ------------------------------------------------------------------

    @staticmethod
    def get_amounts(info_obj) -> Dict[str, int]:
        """Extract resource/population/passengers amounts from a DTO.

        Returns a dict mapping cargo_key → integer amount. Passenger
        species use the ``passengers_<race_id>`` key; bare
        ``passengers`` is the fleet-side single bucket.
        """
        amounts: Dict[str, int] = {}
        if not info_obj:
            return amounts

        # Local imports — DTOs only, no pygame.
        from game.strategy.facade.dto.fleet_dto import FleetInfo
        from game.strategy.facade.dto.planet_dto import PlanetInfo

        if isinstance(info_obj, FleetInfo):
            for res, amt in getattr(info_obj, "cargo_resources", ()):
                amounts[res] = int(amt)
            amounts["passengers"] = info_obj.passengers_current
        elif isinstance(info_obj, PlanetInfo):
            for res, amt in getattr(info_obj, "stockpile", ()):
                amounts[res] = int(amt)
            for race_id, count, _ in info_obj.population_details:
                amounts[f"passengers_{race_id}"] = count

        return amounts

    def build_row_data(self, source_obj, target_obj) -> List[dict]:
        """Rebuild ``row_data`` from a pair of DTOs and return it.

        The order is: 8 canonical resources, then any species seen
        on either side (sorted), then drop-pod rows.
        """
        source_amounts = self.get_amounts(source_obj)
        target_amounts = self.get_amounts(target_obj)

        rows: List[dict] = []

        for res in RESOURCE_TYPES:
            rows.append({
                "cargo_key": res,
                "display_name": RESOURCE_DISPLAY_NAMES.get(res, res.capitalize()),
                "source_amt": source_amounts.get(res, 0),
                "target_amt": target_amounts.get(res, 0),
            })

        species_seen = set()
        for key in list(source_amounts.keys()) + list(target_amounts.keys()):
            if key.startswith("passengers_"):
                species_seen.add(key)
            elif key == "passengers":
                species_seen.add("passengers")

        for species_key in sorted(species_seen):
            if species_key == "passengers":
                display = "Population"
            else:
                display = species_key.replace("passengers_", "")
            rows.append({
                "cargo_key": species_key,
                "display_name": display,
                "source_amt": source_amounts.get(species_key, 0),
                "target_amt": target_amounts.get(species_key, 0),
            })

        rows.extend(self._build_pod_rows(source_obj, target_obj))

        self.row_data = rows
        return rows

    def _build_pod_rows(self, source_obj, target_obj) -> List[dict]:
        """Return drop-pod rows merging known pod designs with any
        pods actually present on either side."""
        from game.strategy.facade.dto.fleet_dto import FleetInfo
        from game.strategy.facade.dto.planet_dto import PlanetInfo

        source_pods: Dict[str, int] = {}
        if isinstance(source_obj, PlanetInfo):
            for name, _vtype, _mass, count in getattr(
                    source_obj, "staging_yard_summary", ()):
                source_pods[name] = source_pods.get(name, 0) + count
        elif isinstance(source_obj, FleetInfo):
            for name, _vtype, _mass, count in getattr(
                    source_obj, "carried_items_summary", ()):
                source_pods[name] = source_pods.get(name, 0) + count

        target_pods: Dict[str, int] = {}
        if isinstance(target_obj, PlanetInfo):
            for name, _vtype, _mass, count in getattr(
                    target_obj, "staging_yard_summary", ()):
                target_pods[name] = target_pods.get(name, 0) + count
        elif isinstance(target_obj, FleetInfo):
            for name, _vtype, _mass, count in getattr(
                    target_obj, "carried_items_summary", ()):
                target_pods[name] = target_pods.get(name, 0) + count

        all_pod_names = set(self.all_pod_names)
        all_pod_names.update(source_pods.keys())
        all_pod_names.update(target_pods.keys())

        out: List[dict] = []
        for pod_name in sorted(all_pod_names):
            out.append({
                "cargo_key": f"drop_pod:{pod_name}",
                "display_name": pod_name,
                "source_amt": source_pods.get(pod_name, 0),
                "target_amt": target_pods.get(pod_name, 0),
            })
        return out

    def visible_rows(self) -> List[dict]:
        """Return the subset of ``row_data`` to render given
        ``filter_empty``."""
        if not self.filter_empty:
            return list(self.row_data)
        return [r for r in self.row_data
                if r["source_amt"] != 0 or r["target_amt"] != 0]


__all__ = [
    "RESOURCE_TYPES",
    "RESOURCE_DISPLAY_NAMES",
    "TransferViewModel",
]
