"""Container snapshot DTO for the UI layer (PROJ-437 Phase 1a).

Read-only projection of a strategy-layer ``Container`` exposed to UI
code without leaking the mutable ``Container`` instance across the
facade boundary. Pairs with
``facade.fleets.get_containers(fleet_id)`` and
``facade.planets.get_containers(planet_id)``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from game.strategy.data.containable import ContainableKind
from game.strategy.data.container import ContainerEntry


@dataclass(frozen=True)
class ContainerSnapshotInfo:
    """Immutable snapshot of a Container for UI consumption.

    Attributes:
        container_id: Stable identity unique per ``(owner_kind,
            owner_id, container_id)`` triple. UI uses this as a stable
            key for selection and pending-transfer routing.
        owner_kind: ``"fleet"`` or ``"planet"``.
        owner_id: ID of the owning fleet or planet.
        label: Human-readable label (e.g. ``"USS Indomitable"`` or
            ``"Alpha Colony — Stockpile"``).
        capacity_mass: Container capacity in tons. May be ``inf`` for
            uncapped projections (planet stockpile during the legacy
            transition or ship containers whose capacity cannot be
            resolved).
        mass_used: Mass currently occupied across the unified slices.
        allowed_kinds: Policy kinds the container accepts.
        entries: Snapshot of ``Container.contents()`` as an immutable
            tuple preserving the resource → item → population order.
    """

    container_id: str
    owner_kind: str
    owner_id: int
    label: str
    capacity_mass: float
    mass_used: float
    allowed_kinds: frozenset[ContainableKind]
    entries: Tuple[ContainerEntry, ...]

    @property
    def mass_remaining(self) -> float:
        return self.capacity_mass - self.mass_used


__all__ = ["ContainerSnapshotInfo"]
