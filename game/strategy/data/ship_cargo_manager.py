"""
ShipCargoManager - Handles cargo operations for ShipInstance.

Extracted from ShipInstance to separate cargo management concerns.

PROJ-FMS-A Phase 3: added carried-vehicle helpers (``load_vehicle``,
``unload_vehicle``, ``get_vehicle_bay_capacity``). Bay capacity comes from
:class:`~game.simulation.components.abilities.vehicle_bay.VehicleBayAbility`
components in the ship's design; current usage is the sum of
:class:`~game.strategy.data.carried_vehicle.CarriedVehicle` masses in the
ship's ``carried_items`` list.

PROJ-FMS-D audit Fix 2: per-bay typed allocation.

Previously, :meth:`_allowed_vehicle_types` unioned every active bay's
``allowed_types`` and :meth:`can_accept_vehicle` only checked the
aggregate ``bay_capacity_mass``. A mixed-bay carrier (e.g. one
fighter-only bay + one satellite-only bay) therefore wrongly accepted
either type up to the SUM of all bay capacities — defeating the
separate-capacity design. The cargo manager now enumerates bays
individually, computes live per-bay usage from ``carried_items``, and
places each load into a specific accepting bay (first-fit, deterministic
order).
"""
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple

from game.strategy.data.carried_vehicle import CarriedVehicle

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


@dataclass
class _BaySlot:
    """One :class:`VehicleBayAbility` instance + its current live usage.

    ``index`` is the position of this bay in the deterministic
    enumeration order (stable across calls — used as the bay key in
    :func:`load_vehicle` placement and as the recovery target for
    :meth:`unload_vehicle`). ``allowed_types`` is the bay's filter;
    ``capacity_mass`` is its max; ``current_mass`` is the sum of
    CarriedVehicles already assigned to this bay.
    """

    index: int
    allowed_types: frozenset[str]
    capacity_mass: float
    current_mass: float

    def remaining(self) -> float:
        return max(0.0, self.capacity_mass - self.current_mass)

    def accepts(self, vehicle_type: str) -> bool:
        return vehicle_type.lower() in self.allowed_types


class ShipCargoManager:
    """
    Manages cargo loading/unloading for a ShipInstance.

    Extracted to separate cargo management from core ShipInstance logic.
    Uses facade pattern: ShipInstance creates and delegates to this manager.
    """

    def __init__(self, ship_instance: 'ShipInstance') -> None:
        """
        Initialize cargo manager.

        Args:
            ship_instance: The ShipInstance to manage cargo for.
        """
        self._ship = ship_instance

    def get_cargo_capacity(self, cargo_type: str) -> int:
        """
        Get maximum cargo capacity for a specific cargo type.

        Args:
            cargo_type: Type of cargo (e.g., 'passengers', 'generic')

        Returns:
            Maximum capacity for this cargo type, or 0 if not available.
        """
        stats = self._ship.get_calculated_stats()
        cargo_storage = stats.get('cargo_storage', {})
        return int(cargo_storage.get(cargo_type, 0))

    def get_current_cargo(self, cargo_type: str) -> int:
        """
        Get current amount of cargo loaded for a specific type.

        Args:
            cargo_type: Type of cargo (e.g., 'passengers', 'generic')

        Returns:
            Current cargo amount, or 0 if none loaded.
        """
        return self._ship.cargo_contents.get(cargo_type, 0)

    def get_cargo_space_available(self, cargo_type: str) -> int:
        """
        Get available space for a specific cargo type.

        Args:
            cargo_type: Type of cargo (e.g., 'passengers', 'generic')

        Returns:
            Available space (capacity - current).
        """
        capacity = self.get_cargo_capacity(cargo_type)
        current = self.get_current_cargo(cargo_type)
        return max(0, capacity - current)

    def load_cargo(self, cargo_type: str, amount: int) -> int:
        """
        Load cargo onto this ship.

        Args:
            cargo_type: Type of cargo to load
            amount: Amount to load (will be capped at available space)

        Returns:
            Actual amount loaded (may be less than requested if space limited).
        """
        if amount <= 0:
            return 0

        available_space = self.get_cargo_space_available(cargo_type)
        actual_load = min(amount, available_space)

        if actual_load > 0:
            current = self._ship.cargo_contents.get(cargo_type, 0)
            self._ship.cargo_contents[cargo_type] = current + actual_load

        return actual_load

    # ------------------------------------------------------------------
    # PROJ-FMS-A Phase 3: carried-vehicle helpers
    # PROJ-FMS-D audit Fix 2: per-bay typed allocation
    # ------------------------------------------------------------------

    def _enumerate_bays(self) -> List[_BaySlot]:
        """Walk the ship's design and return one :class:`_BaySlot` per
        active :class:`VehicleBayAbility`.

        Bay ordering: stable, follows the design's layer iteration order
        + component-position-within-layer. This gives :meth:`load_vehicle`
        a deterministic first-fit target so a save/load round trip can
        reconstruct identical bay assignments without recording a bay
        index on each ``CarriedVehicle``.

        ``current_mass`` is NOT populated here — callers that need live
        per-bay usage call :meth:`_assign_carried_to_bays` (which packs
        existing :attr:`carried_items` into bays using the same first-fit
        rule that :meth:`load_vehicle` uses).
        """
        from game.simulation.components.abilities.vehicle_bay import (
            VehicleBayAbility,
        )
        from game.simulation.entities.ship import Ship
        registries = getattr(self._ship, "_registries", None)
        design = getattr(self._ship, "design_data", None)
        if registries is None or not design:
            return []
        try:
            ship = Ship.from_dict(design, registries=registries)
            ship.recalculate_stats()
        except Exception:  # Intentional broad catch: Ship.from_dict() raises across many failure modes (missing component, malformed layer); a missing bay is a "no capacity" signal, not a crash.
            return []
        bays: List[_BaySlot] = []
        for layer_data in ship.layers.values():
            for comp in getattr(layer_data, "components", []):
                if not getattr(comp, "is_active", True):
                    continue
                for ab in getattr(comp, "ability_instances", []):
                    if not isinstance(ab, VehicleBayAbility):
                        continue
                    bays.append(
                        _BaySlot(
                            index=len(bays),
                            allowed_types=frozenset(
                                t.lower() for t in ab.allowed_types
                            ),
                            capacity_mass=float(ab.capacity_mass),
                            current_mass=0.0,
                        )
                    )
        return bays

    def _assign_carried_to_bays(
        self, bays: List[_BaySlot],
    ) -> List[Optional[int]]:
        """Pack existing :attr:`carried_items` into the bay list.

        Mutates each :class:`_BaySlot`'s ``current_mass`` and returns a
        list parallel to :attr:`carried_items` indicating which bay each
        carried vehicle was assigned to (``None`` for drop-pod-shaped
        entries that aren't CarriedVehicles, or vehicles that don't fit
        any bay — those drop through to the legacy untyped path).

        Packing rule: first-fit by bay index, iterating carried items
        in their stored order. Stable across calls so save/load round
        trips produce identical assignments.
        """
        assignments: List[Optional[int]] = []
        for item in self._ship.carried_items:
            cv = CarriedVehicle.from_any(item)
            if cv is None:
                assignments.append(None)
                continue
            placed: Optional[int] = None
            for bay in bays:
                if not bay.accepts(cv.vehicle_type):
                    continue
                if bay.remaining() < cv.mass:
                    continue
                bay.current_mass += cv.mass
                placed = bay.index
                break
            assignments.append(placed)
        return assignments

    def _allowed_vehicle_types(self) -> set[str]:
        """Union of every active VehicleBay's ``allowed_types``.

        Retained as a backwards-compatible helper for external callers
        / tests that inspect the ship-wide accepted set. The corrected
        per-bay enforcement lives in :meth:`can_accept_vehicle` /
        :meth:`load_vehicle`; this union is no longer the gating check.
        """
        allowed: set[str] = set()
        for bay in self._enumerate_bays():
            allowed.update(bay.allowed_types)
        return allowed

    def get_vehicle_bay_capacity(self) -> Tuple[float, float]:
        """Return (current_mass, max_mass) of carried CarriedVehicles.

        ``max_mass`` is the SUM of all bay capacities. ``current_mass``
        sums the masses of ``CarriedVehicle``-shaped entries already
        stored in ``carried_items``. Drop-pod-shaped entries are ignored.

        PROJ-FMS-D audit Fix 2: now derives ``max_mass`` directly from
        the enumerated bays rather than the cached ``bay_capacity_mass``
        stat, so that the value stays consistent with the per-bay
        enforcement path. The cached stat (from
        ``stat_contributors/launch.py``) is still computed for design-
        time UI display.
        """
        bays = self._enumerate_bays()
        if not bays:
            # Fall back to the cached stat if registries / design are
            # unavailable (test fixtures with minimal stub designs).
            try:
                stats = self._ship.get_calculated_stats()
                fallback_max = float(stats.get("bay_capacity_mass", 0.0))
            except Exception:  # Intentional broad catch: stats path raises for ships built without registries (test fixtures); treat as zero capacity.
                fallback_max = 0.0
            current = 0.0
            for item in self._ship.carried_items:
                cv = CarriedVehicle.from_any(item)
                if cv is not None:
                    current += cv.mass
            return current, fallback_max
        max_mass = sum(bay.capacity_mass for bay in bays)
        current = 0.0
        for item in self._ship.carried_items:
            cv = CarriedVehicle.from_any(item)
            if cv is not None:
                current += cv.mass
        return current, max_mass

    def can_accept_vehicle(self, vehicle: CarriedVehicle) -> bool:
        """True iff at least one bay accepts the vehicle's type AND has
        live remaining capacity ≥ ``vehicle.mass``.

        PROJ-FMS-D audit Fix 2: per-bay check replaces the previous
        ship-wide union + aggregate-capacity check. A 200-mass fighter
        will be rejected on a carrier whose only fighter-accepting bay
        has 150 mass free, even if total ship capacity has room — that
        spare capacity lives in a satellite-only bay which cannot accept
        fighters.
        """
        bays = self._enumerate_bays()
        if not bays:
            return False
        self._assign_carried_to_bays(bays)
        for bay in bays:
            if not bay.accepts(vehicle.vehicle_type):
                continue
            if bay.remaining() >= vehicle.mass:
                return True
        return False

    def load_vehicle(self, vehicle: CarriedVehicle) -> bool:
        """Append a CarriedVehicle to the ship's bay (first-fit per type).

        Returns False if no bay accepts the vehicle's type with enough
        remaining capacity. Mutates ``ship.carried_items`` on success —
        stored as the vehicle's serialised dict, so the existing fleet
        save/load path can round-trip the entry without a schema change.

        Placement rule (PROJ-FMS-D audit Fix 2): walk bays in enumeration
        order, place into the first bay that accepts this vehicle's type
        AND has remaining capacity ≥ ``vehicle.mass``. Bay enumeration
        order is stable across calls, so save/load reconstructs the same
        per-bay packing.
        """
        bays = self._enumerate_bays()
        if not bays:
            return False
        self._assign_carried_to_bays(bays)
        for bay in bays:
            if not bay.accepts(vehicle.vehicle_type):
                continue
            if bay.remaining() < vehicle.mass:
                continue
            self._ship.carried_items.append(vehicle.to_dict())
            return True
        return False

    def unload_vehicle(self, vehicle_index: int) -> CarriedVehicle:
        """Pop and return the vehicle at ``vehicle_index``.

        ``vehicle_index`` indexes into the CarriedVehicle-shaped entries
        only (drop-pod entries are skipped). Raises IndexError if out of
        range. HP and component states preserved through the round-trip.
        """
        vehicle_entries: list[tuple[int, CarriedVehicle]] = []
        for raw_idx, item in enumerate(self._ship.carried_items):
            cv = CarriedVehicle.from_any(item)
            if cv is not None:
                vehicle_entries.append((raw_idx, cv))
        if vehicle_index < 0 or vehicle_index >= len(vehicle_entries):
            raise IndexError(
                f"unload_vehicle: index {vehicle_index} out of range "
                f"({len(vehicle_entries)} carried vehicles)"
            )
        raw_idx, cv = vehicle_entries[vehicle_index]
        self._ship.carried_items.pop(raw_idx)
        return cv

    def get_carried_vehicles(self) -> List[CarriedVehicle]:
        """Return all CarriedVehicle entries (skipping drop-pod dicts)."""
        results: List[CarriedVehicle] = []
        for item in self._ship.carried_items:
            cv = CarriedVehicle.from_any(item)
            if cv is not None:
                results.append(cv)
        return results

    def get_carried_vehicles_by_type(
        self, vehicle_type: str
    ) -> List[CarriedVehicle]:
        """Filter ``get_carried_vehicles()`` by ``vehicle_type``."""
        vt = vehicle_type.lower()
        return [cv for cv in self.get_carried_vehicles() if cv.vehicle_type == vt]

    def unload_cargo(self, cargo_type: str, amount: int) -> int:
        """
        Unload cargo from this ship.

        Args:
            cargo_type: Type of cargo to unload
            amount: Amount to unload (will be capped at current amount)

        Returns:
            Actual amount unloaded (may be less than requested if not enough cargo).
        """
        if amount <= 0:
            return 0

        current = self._ship.cargo_contents.get(cargo_type, 0)
        actual_unload = min(amount, current)

        if actual_unload > 0:
            new_amount = current - actual_unload
            if new_amount <= 0:
                # Remove zero entries to keep dict clean
                self._ship.cargo_contents.pop(cargo_type, None)
            else:
                self._ship.cargo_contents[cargo_type] = new_amount

        return actual_unload
