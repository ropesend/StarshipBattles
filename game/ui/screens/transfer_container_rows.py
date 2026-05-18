"""Container-driven row builder for the transfer dialog (PROJ-437 Phase 3a).

Substrate for the mixed-content (resources / items / population)
display rework. ``build_row_data_from_containers`` walks both sides'
``ContainerSnapshotInfo.entries``, aggregates by ``(kind, type_id)``,
and returns the row list the dialog renders.

Extracted out of :mod:`game.ui.screens.transfer_view_model` to keep
that module under the 500-LOC production-file ceiling; the view
model exposes
:meth:`TransferViewModel.build_row_data_from_containers` as a thin
classmethod wrapper that injects the resource-definition iterable so
this module stays pygame-free and catalog-agnostic.

Row dict shape::

    {
      "cargo_key": str,           # "<resource_id>" / "passengers_<species>" / "drop_pod:<design_id>"
      "display_name": str,
      "kind": ContainableKind,    # NEW additive field
      "source_amt": int,
      "target_amt": int,
    }

Order: resources in catalog order (canonical 8 always emitted — UX
parity with the legacy ``build_row_data`` so the user can see all
load targets); population alphabetical by species; items
alphabetical by ``cargo_key``.

Phase-3a scope notes:

* Items always use the ``"drop_pod:<design_id>"`` prefix. Vehicle vs
  drop-pod discrimination needs ``ItemRef.state`` to reach the
  snapshot, which is a Container-substrate change owned by PROJ-436.
  Until that lands, the legacy DTO path (``_build_pod_rows``) retains
  the ``"vehicle:<name>"`` prefix differentiation.
* Population display name falls back to ``species_id``; a richer
  species label registry hook is Phase 3b polish.
* Phase 3a leaves the dialog calling the legacy DTO path —
  ``build_row_data_from_containers`` ships additively. Cutover is
  Phase 3b / Phase 4.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple


def build_row_data_from_containers(
    source_containers,
    target_containers,
    *,
    resource_definitions: Iterable,
    filter_empty: bool = False,
) -> List[dict]:
    """Aggregate snapshot entries into the dialog's row list.

    See module docstring for row-dict shape, ordering, and Phase 3a
    scope notes. ``resource_definitions`` is the canonical resource
    list (typically
    ``ResourceCatalog.from_json().all_definitions()``) — injected to
    keep this module pygame-/catalog-free.
    """
    # Local import keeps the module pygame-free and avoids a circular
    # import from the strategy layer at module load time.
    from game.strategy.data.containable import ContainableKind

    source_by_key = _aggregate_quantities_by_cargo_key(source_containers)
    target_by_key = _aggregate_quantities_by_cargo_key(target_containers)

    rows: List[dict] = []

    # Resources (canonical catalog order; always emitted).
    for defn in resource_definitions:
        cargo_key = defn.id
        rows.append({
            "cargo_key": cargo_key,
            "display_name": defn.name,
            "kind": ContainableKind.RESOURCE,
            "source_amt": source_by_key.get(("resource", cargo_key), 0),
            "target_amt": target_by_key.get(("resource", cargo_key), 0),
        })

    seen_keys = set(source_by_key) | set(target_by_key)

    # Population (only emitted when present on either side).
    for species_id in sorted(
        type_id for kind_marker, type_id in seen_keys if kind_marker == "population"
    ):
        rows.append({
            "cargo_key": f"passengers_{species_id}",
            "display_name": species_id,
            "kind": ContainableKind.POPULATION,
            "source_amt": source_by_key.get(("population", species_id), 0),
            "target_amt": target_by_key.get(("population", species_id), 0),
        })

    # Items (only emitted when present).
    for design_id in sorted(
        type_id for kind_marker, type_id in seen_keys if kind_marker == "item"
    ):
        rows.append({
            "cargo_key": f"drop_pod:{design_id}",
            "display_name": design_id,
            "kind": ContainableKind.ITEM,
            "source_amt": source_by_key.get(("item", design_id), 0),
            "target_amt": target_by_key.get(("item", design_id), 0),
        })

    if filter_empty:
        rows = [
            r for r in rows
            if r["source_amt"] != 0 or r["target_amt"] != 0
        ]
    return rows


def _aggregate_quantities_by_cargo_key(snapshots) -> Dict[Tuple[str, str], int]:
    """Aggregate snapshot entry quantities into a ``(kind_marker, type_id) -> int`` map.

    ``kind_marker`` is the lowercased ``ContainableKind`` value
    (``"resource"`` / ``"population"`` / ``"item"``) so callers can
    look up by a stable string key without pulling the enum into the
    dict key — keeps the contract debug-friendly.
    """
    from game.strategy.data.containable import ContainableKind

    totals: Dict[Tuple[str, str], int] = {}
    for snapshot in snapshots:
        for entry in snapshot.entries:
            if entry.kind is ContainableKind.RESOURCE:
                key = ("resource", entry.type_id)
            elif entry.kind is ContainableKind.POPULATION:
                key = ("population", entry.type_id)
            elif entry.kind is ContainableKind.ITEM:
                key = ("item", entry.type_id)
            else:
                continue
            totals[key] = totals.get(key, 0) + int(entry.quantity)
    return totals


__all__ = ["build_row_data_from_containers"]
