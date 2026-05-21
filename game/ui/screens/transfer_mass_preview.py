"""Mass-remaining preview math for the transfer dialog (PROJ-437 Phase 2).

Pure-Python projection of "source / target mass remaining after every
pending transfer applies." Consumed by ``TransferDialog`` after every
arrow / Max / Zero / Clear-All mutation (OD3 = (a) per-input
granularity).

Extracted out of :mod:`game.ui.screens.transfer_view_model` to keep
that module under the 500-LOC production-file ceiling; the view model
re-exports :class:`MassPreview` and exposes
:meth:`TransferViewModel.compute_mass_preview` as a thin classmethod
wrapper so existing callers keep the single entry point.

Coverage:

* RESOURCE cargo keys (``"metals"``, ``"fuel"``, …) use
  ``ResourceCatalog.get_mass_per_unit``.
* POPULATION keys (``"passengers"``, ``"passengers_<species>"``) use
  the default 0.1 tons / individual.
* ITEM keys (``"drop_pod:..."``, ``"vehicle:..."``) are mass-neutral
  here — Phase 3 mixed-content folds them in.
* Unknown cargo keys are mass-neutral so a catalog drift does not
  crash the preview; Phase 5 consult catches genuinely bad keys.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


# Tons per individual member of a species. Mirrors
# `game.strategy.data.containable.SPECIES_DEFAULT_MASS_PER_UNIT`.
# Duplicated as a module-local literal to keep this file pygame-free
# and dependency-minimal; if PROJ-436 ships per-species mass overrides
# the lookup moves to a single call site here.
_PASSENGER_DEFAULT_MASS_PER_UNIT: float = 0.1


@dataclass(frozen=True)
class MassPreview:
    """Projected mass-remaining for the transfer dialog.

    Attributes:
        source_mass_remaining_after: Source side's mass_remaining once
            every pending transfer applies. May be negative for very
            large LOAD pendings — the renderer styles accordingly.
        target_mass_remaining_after: Target side's mass_remaining once
            every pending transfer applies. May be negative.
        source_capacity_mass: Source side's total capacity (for
            "X / Y tons" labelling).
        target_capacity_mass: Target side's total capacity.
        target_over_capacity: True iff the projected target mass would
            exceed its capacity. Infinite capacity never flips this.
    """

    source_mass_remaining_after: float
    target_mass_remaining_after: float
    source_capacity_mass: float
    target_capacity_mass: float
    target_over_capacity: bool


def compute_mass_preview(
    source_containers,
    target_containers,
    pending_transfers: Dict[str, Any],
    *,
    max_load_sentinel: Any,
    max_drop_sentinel: Any,
) -> MassPreview:
    """Project source / target mass-remaining after pending applies.

    Convention (matches the dialog's UI mental model):

    * Positive ``pending_transfers`` values are LOAD arrows — cargo
      flows target → source, so source mass_used rises and target
      mass_used falls.
    * Negative values are DROP arrows — cargo flows source → target.
    * ``max_load_sentinel`` resolves to the target's current quantity
      of ``cargo_key``.
    * ``max_drop_sentinel`` resolves to the negative of the source's
      current quantity.

    Sentinels are injected by ``TransferViewModel.compute_mass_preview``
    so this module stays unaware of the view model's class-level
    ``MAX_LOAD`` / ``MAX_DROP`` constants and the indirection between
    them is explicit at the one call site.
    """
    source_capacity = sum(s.capacity_mass for s in source_containers)
    target_capacity = sum(s.capacity_mass for s in target_containers)
    source_used = sum(s.mass_used for s in source_containers)
    target_used = sum(s.mass_used for s in target_containers)

    for cargo_key, signed_amount in pending_transfers.items():
        qty = _resolve_pending_qty(
            cargo_key, signed_amount,
            source_containers, target_containers,
            max_load_sentinel=max_load_sentinel,
            max_drop_sentinel=max_drop_sentinel,
        )
        mass_per_unit = _mass_per_unit_for_cargo_key(cargo_key)
        mass_delta = qty * mass_per_unit
        source_used += mass_delta
        target_used -= mass_delta

    target_over = (
        target_capacity != float("inf")
        and target_used > target_capacity + 1e-9
    )
    return MassPreview(
        source_mass_remaining_after=source_capacity - source_used,
        target_mass_remaining_after=target_capacity - target_used,
        source_capacity_mass=source_capacity,
        target_capacity_mass=target_capacity,
        target_over_capacity=target_over,
    )


def _resolve_pending_qty(
    cargo_key: str,
    signed_amount: Any,
    source_containers,
    target_containers,
    *,
    max_load_sentinel: Any,
    max_drop_sentinel: Any,
) -> int:
    """Translate a pending dict entry to a concrete signed quantity."""
    if signed_amount == max_load_sentinel:
        return _qty_for_cargo_key(cargo_key, target_containers)
    if signed_amount == max_drop_sentinel:
        return -_qty_for_cargo_key(cargo_key, source_containers)
    try:
        return int(signed_amount)
    except (TypeError, ValueError):
        return 0


def _mass_per_unit_for_cargo_key(cargo_key: str) -> float:
    """Return tons-per-unit for a pending-dict cargo key.

    See module docstring for the coverage table. Unknown / item keys
    return 0.0 (mass-neutral).
    """
    if cargo_key == "passengers" or cargo_key.startswith("passengers_"):
        return _PASSENGER_DEFAULT_MASS_PER_UNIT
    if cargo_key.startswith("drop_pod:") or cargo_key.startswith("vehicle:"):
        return 0.0
    catalog = _get_catalog()
    defn = catalog.get(cargo_key)
    if defn is None:
        return 0.0
    return defn.mass_per_unit


def _qty_for_cargo_key(cargo_key: str, snapshots) -> int:
    """Aggregate the quantity of ``cargo_key`` across container snapshots."""
    # Local import keeps the module pygame-free.
    from game.strategy.data.containable import ContainableKind

    if cargo_key.startswith("passengers_"):
        species_id = cargo_key[len("passengers_"):]
        return sum(
            int(e.quantity)
            for s in snapshots
            for e in s.entries
            if e.kind is ContainableKind.POPULATION and e.type_id == species_id
        )
    if cargo_key == "passengers":
        return sum(
            int(e.quantity)
            for s in snapshots
            for e in s.entries
            if e.kind is ContainableKind.POPULATION
        )
    if cargo_key.startswith("drop_pod:") or cargo_key.startswith("vehicle:"):
        return 0
    return sum(
        int(e.quantity)
        for s in snapshots
        for e in s.entries
        if e.kind is ContainableKind.RESOURCE and e.type_id == cargo_key
    )


_catalog = None


def _get_catalog():
    """Lazy-load the resource catalog once per process.

    Same pattern as :mod:`game.ui.screens.transfer_view_model` —
    catalog reads from ``data/resources.json`` on first use, then
    re-used. PROJ-471 Task 2.10 added :func:`_clear_catalog` so tests (and
    any future catalog swap) can invalidate this process cache.
    """
    global _catalog
    if _catalog is None:
        from game.core.resources import ResourceCatalog
        _catalog = ResourceCatalog.from_json()
    return _catalog


def _clear_catalog() -> None:
    """Invalidate the lazy catalog cache (PROJ-471 Task 2.10 test seam).

    Forces the next :func:`_get_catalog` to reload, removing the
    stale-catalog-in-tests hazard the docstring previously warned about.
    """
    global _catalog
    _catalog = None


__all__ = [
    "MassPreview",
    "compute_mass_preview",
]
