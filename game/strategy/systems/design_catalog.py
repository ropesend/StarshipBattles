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
        self._list_view: List[DesignMetadata] = []
        self._pending_built: Dict[str, int] = {}

    # ------------------------------------------------------------------
    # Lookup / list
    # ------------------------------------------------------------------

    def lookup(self, design_id: str) -> Optional[DesignMetadata]:
        """Return the ``DesignMetadata`` for ``design_id`` or ``None``."""
        return self._by_id.get(design_id)

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
        designs = repository.scan_designs()
        self._list_view = list(designs)
        self._by_id = {d.design_id: d for d in designs}
