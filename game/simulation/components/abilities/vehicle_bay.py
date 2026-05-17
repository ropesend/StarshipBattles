"""PROJ-FMS-A Phase 3 — VehicleBayAbility.

Strategic-layer storage ability that holds design-backed vehicles
(mines / fighters / satellites) inside a ship. Mass is the capacity gate.
Generalises the previous drop-pod-specific ``carried_items`` flow into a
typed substrate. Actual load/unload bookkeeping is performed by the
:class:`~game.strategy.data.ship_cargo_manager.ShipCargoManager` extensions
that read ``capacity_mass`` off this ability and ``allowed_types`` to gate
which vehicle types can be stowed.

Data shape:
    Dict:   {"capacity_mass": <int>, "allowed_types": ["mine", "fighter"]}
    Scalar: 100  (treated as capacity_mass; default allowed_types)

``allowed_types`` defaults to all three small-craft kinds: mine, fighter,
satellite. Drop pods retain their separate PodStorage path.

QA-C: ``capacity_mass`` now scales via :class:`AbilityStatBinding` with
``bay_capacity_mult`` so ``simple_size_mount`` drives bay size linearly
with the modifier param. This replaces the old small/medium/large tier
proliferation with a single component that scales.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .base import Ability, AbilityLayer
from .stat_keys import AbilityStatBinding, StatKey
from .ui_colors import HINT_NEUTRAL


_DEFAULT_ALLOWED_TYPES: tuple[str, ...] = ("mine", "fighter", "satellite")


class VehicleBayAbility(Ability):
    """Per-instance storage for design-backed vehicles.

    Attributes:
        capacity_mass: Maximum stored mass (sum of CarriedVehicle.mass).
        allowed_types: Vehicle types this bay can hold (default: all three
            small-craft kinds).
    """

    layer = AbilityLayer.STRATEGIC

    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(
            StatKey.BAY_CAPACITY_MULT,
            attribute_name="capacity_mass",
            operation="multiply",
            base_attribute="_base_capacity_mass",
        ),
    ]

    def _parse_attrs(self, data: Any) -> None:
        if isinstance(data, dict):
            cap = float(data.get("capacity_mass", 0))
            allowed = data.get("allowed_types")
            if allowed is None:
                self.allowed_types = list(_DEFAULT_ALLOWED_TYPES)
            else:
                self.allowed_types = [str(a).lower() for a in allowed]
        elif isinstance(data, (int, float)):
            cap = float(data)
            self.allowed_types = list(_DEFAULT_ALLOWED_TYPES)
        else:
            cap = 0.0
            self.allowed_types = list(_DEFAULT_ALLOWED_TYPES)
        self._base_capacity_mass = cap
        self.capacity_mass = cap

    def recalculate(self) -> None:
        """Apply ``bay_capacity_mult`` to ``capacity_mass``."""
        mult = self.get_effective_stat("bay_capacity_mult", 1.0)
        self.capacity_mass = self._base_capacity_mass * mult

    def accepts(self, vehicle_type: str) -> bool:
        """True iff this bay accepts the given vehicle type."""
        return vehicle_type.lower() in self.allowed_types

    def get_primary_value(self) -> float:
        return float(self.capacity_mass)

    def get_ui_rows(self) -> List[Dict[str, Any]]:
        types_str = "/".join(self.allowed_types)
        return [{
            "label": "Vehicle Bay",
            "value": f"{self.capacity_mass:.0f} mass ({types_str})",
            "color_hint": HINT_NEUTRAL,
        }]
