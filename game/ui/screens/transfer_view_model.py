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

from game.core.resources import ResourceCatalog, ResourceDefinition
from game.ui.screens.transfer_container_rows import (
    build_row_data_from_containers as _build_row_data_from_containers,
)
from game.ui.screens.transfer_mass_preview import (
    MassPreview,
    compute_mass_preview as _compute_mass_preview,
)


# Module-level catalog handle. Lazy-loaded on first access so import
# order does not require ``data/resources.json`` to be present.
_resource_catalog: ResourceCatalog | None = None


def _get_resource_catalog() -> ResourceCatalog:
    global _resource_catalog
    if _resource_catalog is None:
        _resource_catalog = ResourceCatalog.from_json()
    return _resource_catalog


def _iter_resource_definitions() -> List[ResourceDefinition]:
    """Return the canonical resource list in display order.

    PROJ-436 Phase 7: replaces the deleted ``RESOURCE_TYPES`` hardcoded
    list. The display order comes directly from ``data/resources.json``
    (the catalog preserves insertion order). The display label for each
    resource is :attr:`ResourceDefinition.name`, replacing the deleted
    ``RESOURCE_DISPLAY_NAMES`` mapping.

    Note: ``ResourceDefinition.name`` is the canonical label. With the
    current ``data/resources.json`` this means the ammo row now reads
    "Ammunition" instead of the old hardcoded "Ammo" — the JSON name
    field is the single source of truth.
    """
    return _get_resource_catalog().all_definitions()


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
    """

    # Sentinel values for "transfer all available". The engine
    # convention is amount=0 meaning all-available; the dialog needs
    # a distinguishable in-memory marker so the user can see "Load
    # Max" before confirming. ``float('inf')`` is intentional — any
    # numeric arrow click falls back into normal int territory after
    # the sentinel check resets it to 0.
    MAX_LOAD: float = float("inf")
    MAX_DROP: float = float("-inf")

    def __init__(self) -> None:
        self.available_sources: List[dict] = []
        self.available_targets: List[dict] = []
        self.current_source: Optional[dict] = None
        self.current_target: Optional[dict] = None

        self.pending_transfers: Dict[str, Any] = {}
        self.row_data: List[dict] = []
        self.filter_empty: bool = False

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
    def get_amounts_from_containers(
        snapshots,
    ) -> Dict[str, int]:
        """Aggregate resource + population amounts across container snapshots.

        PROJ-437 Phase 1b. Returns a ``cargo_key → int`` mapping
        consumed (historically) by the legacy row builder. Post-
        Phase-4 the dialog drives its row data through
        :meth:`build_row_data_from_containers` and this method is
        retained as a focused helper for callers that need only the
        resource/population aggregation.

        Mapping rules:

        * ``ContainableKind.RESOURCE`` entries → ``{type_id: int(qty)}``.
          Quantities from multiple snapshots aggregate.
        * ``ContainableKind.POPULATION`` entries →
          ``{f"passengers_{species_id}": int(count)}``.
        * ``ContainableKind.ITEM`` entries are skipped.
        """
        # Local import keeps the module pygame-free and avoids circular
        # imports — the DTO module sits below the UI layer.
        from game.strategy.data.containable import ContainableKind

        amounts: Dict[str, int] = {}
        for snapshot in snapshots:
            for entry in snapshot.entries:
                if entry.kind is ContainableKind.RESOURCE:
                    amounts[entry.type_id] = (
                        amounts.get(entry.type_id, 0) + int(entry.quantity)
                    )
                elif entry.kind is ContainableKind.POPULATION:
                    key = f"passengers_{entry.type_id}"
                    amounts[key] = amounts.get(key, 0) + int(entry.quantity)
                # ITEM entries handled in Phase 3.
        return amounts

    # ------------------------------------------------------------------
    # PROJ-437 Phase 2 — Mass-remaining preview
    # ------------------------------------------------------------------

    @classmethod
    def compute_mass_preview(
        cls,
        source_containers,
        target_containers,
        pending_transfers: Dict[str, Any],
    ) -> MassPreview:
        """Project mass-remaining on source and target after pending.

        Thin wrapper over
        :func:`game.ui.screens.transfer_mass_preview.compute_mass_preview`
        that injects the view-model's :attr:`MAX_LOAD` / :attr:`MAX_DROP`
        sentinels so the helper module stays sentinel-agnostic.
        See the helper module's docstring for cargo-key coverage,
        sign conventions, and OD3 rationale.
        """
        return _compute_mass_preview(
            source_containers,
            target_containers,
            pending_transfers,
            max_load_sentinel=cls.MAX_LOAD,
            max_drop_sentinel=cls.MAX_DROP,
        )

    # ------------------------------------------------------------------
    # PROJ-437 Phase 3a — container-driven row builder (substrate)
    # ------------------------------------------------------------------

    @classmethod
    def build_row_data_from_containers(
        cls,
        source_containers,
        target_containers,
        *,
        filter_empty: bool = False,
    ) -> List[dict]:
        """Build the dialog's row list directly from container snapshots.

        Thin wrapper over
        :func:`game.ui.screens.transfer_container_rows.build_row_data_from_containers`
        that injects the canonical resource list so that helper module
        stays pygame-/catalog-free. See the helper module's docstring
        for row-dict shape, ordering, and Phase 3a scope notes.
        """
        return _build_row_data_from_containers(
            source_containers,
            target_containers,
            resource_definitions=_iter_resource_definitions(),
            filter_empty=filter_empty,
        )

    def visible_rows(self) -> List[dict]:
        """Return the subset of ``row_data`` to render given
        ``filter_empty``."""
        if not self.filter_empty:
            return list(self.row_data)
        return [r for r in self.row_data
                if r["source_amt"] != 0 or r["target_amt"] != 0]


__all__ = [
    "MassPreview",
    "TransferViewModel",
]
