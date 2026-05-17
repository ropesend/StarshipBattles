"""PROJ-427 Phase 2: DesignCatalog (in-memory runtime design lookup).

The catalog is the per-empire runtime view introduced in Phase 2:

- ``lookup(design_id)`` — pure in-memory dict access; no filesystem
  call, no JSON parsing.
- ``list_designs()`` / filtered views — UI's per-turn read path.
- ``record_built(design_id)`` — increments an in-memory pending-count
  dict. Phase 4 flushes those increments through ``DesignRepository``
  at save time. **No disk write during a production tick.**
- ``repopulate_from(repository)`` — the explicit refresh entry point.
  Called at session bootstrap and after explicit refresh events (e.g.
  a workshop save). **Never** called during a production tick — Phase
  3 adds an integration assertion to that effect.

Phase 2 is additive: no existing ``DesignLibrary`` caller is migrated.
The catalog plus its owning ``DesignRepository`` is exposed through
``SessionRuntimeServices`` per the PROJ-423 cross-plan absorption note.
"""
from __future__ import annotations

from typing import Dict, List, Optional, TYPE_CHECKING

from game.strategy.data.design_metadata import DesignMetadata

if TYPE_CHECKING:
    from game.strategy.systems.design_repository import DesignRepository


class DesignCatalog:
    """Per-empire in-memory design lookup + pending built-count map.

    Construct one catalog per empire. Initial state is empty; call
    ``repopulate_from(repository)`` to seed it from disk. After the
    initial bootstrap, the runtime production tick and the UI both
    read through the same catalog instance, which is what unifies the
    per-empire view today split between ``DesignLibrary`` (engine
    side) and ``FacadeSessionState.designs_by_empire`` (UI side).

    The catalog deliberately has no filesystem dependency: this is
    what allows Phase 3 to drop ``save_path`` from the runtime spawn
    chain entirely.
    """

    def __init__(self, *, empire_id: int) -> None:
        self.empire_id = empire_id
        self._by_id: Dict[str, DesignMetadata] = {}
        self._data_by_id: Dict[str, dict] = {}
        self._list_view: List[DesignMetadata] = []
        self._pending_built: Dict[str, int] = {}

    # ------------------------------------------------------------------
    # Lookup / list
    # ------------------------------------------------------------------

    def lookup(self, design_id: str) -> Optional[DesignMetadata]:
        """Return the ``DesignMetadata`` for ``design_id`` or ``None``."""
        return self._by_id.get(design_id)

    def lookup_data(self, design_id: str) -> Optional[dict]:
        """Return the full design data dict for ``design_id`` or ``None``.

        PROJ-427 Phase 3: this is the runtime spawn lookup. Returns the
        same JSON-equivalent dict shape that ``DesignRepository.load_design_data``
        delivers from disk, but serves it from the in-memory cache so a
        production tick triggers zero filesystem reads.
        """
        return self._data_by_id.get(design_id)

    def has_design(self, design_id: str) -> bool:
        """Return ``True`` if the catalog knows about ``design_id``."""
        return design_id in self._by_id

    def upsert_design(self, design_id: str, data: dict) -> None:
        """Refresh the in-memory entry for ``design_id`` from ``data``.

        Used by UI write paths (workshop save) to keep the runtime catalog
        coherent without forcing a full repository rescan. Rebuilds the
        list view so ordering matches the underlying dict iteration order.
        """
        try:
            metadata = DesignMetadata.from_design_data(data, design_id)
        except Exception:  # Intentional broad catch: schema-validation failures during upsert must not corrupt the catalog — fall back to dropping the entry.
            self._data_by_id[design_id] = data
            self._by_id.pop(design_id, None)
            self._list_view = list(self._by_id.values())
            return
        self._by_id[design_id] = metadata
        self._data_by_id[design_id] = data
        self._list_view = list(self._by_id.values())

    def remove_design(self, design_id: str) -> None:
        """Drop ``design_id`` from the catalog (UI deletion / rename)."""
        self._by_id.pop(design_id, None)
        self._data_by_id.pop(design_id, None)
        self._list_view = list(self._by_id.values())

    def list_designs(self) -> List[DesignMetadata]:
        """Return the cached per-empire ``DesignMetadata`` list.

        Repeated calls within the same catalog return the same list
        object (object identity); ``repopulate_from`` rebuilds it.
        """
        return self._list_view

    # ------------------------------------------------------------------
    # Pending built-count increments — in-memory only
    # ------------------------------------------------------------------

    @property
    def pending_built_counts(self) -> Dict[str, int]:
        """Read-only view of the in-memory pending-increment map.

        Returned as a live dict so tests can assert exact contents.
        Phase 4 introduces ``flush_pending_built_counts(repository)``
        that drains this map through ``DesignRepository.increment_built_count``.
        """
        return self._pending_built

    def record_built(self, design_id: str) -> None:
        """Bump the in-memory ``pending_built_counts[design_id]`` by 1.

        No disk write occurs; the flush happens at save time
        (Phase 4).
        """
        self._pending_built[design_id] = (
            self._pending_built.get(design_id, 0) + 1
        )

    # ------------------------------------------------------------------
    # Refresh from repository
    # ------------------------------------------------------------------

    def repopulate_from(self, repository: "DesignRepository") -> None:
        """Rebuild the in-memory lookup map from a repository scan.

        Called at session bootstrap and after explicit refresh events
        (workshop saves, etc.). Phase 3 asserts via integration test
        that this method is NOT called during a production tick.
        """
        pairs = repository.scan_designs_with_data()
        self._by_id = {meta.design_id: meta for meta, _ in pairs}
        self._data_by_id = {meta.design_id: data for meta, data in pairs}
        self._list_view = list(self._by_id.values())

    def flush_pending_built_counts(self, repository: "DesignRepository") -> int:
        """Persist pending built-count increments through ``repository``.

        PROJ-427 Phase 4: called by ``SaveGameService.save_game(...)``
        before the save dict is written, so the on-disk
        ``_metadata.times_built`` counter reflects every spawn that
        happened since the last save. No mid-tick disk write.

        Returns the number of distinct ``design_id`` flushed.
        """
        if not self._pending_built:
            return 0
        flushed = 0
        # Drain the pending map; repeated calls on the same catalog within
        # one save are idempotent.
        pending = self._pending_built
        self._pending_built = {}
        for design_id, count in pending.items():
            for _ in range(count):
                repository.increment_built_count(design_id)
            flushed += 1
        return flushed
