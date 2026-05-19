"""
TransferValidator - Validates TRANSFER orders for fleets.

PROJ-68: Validates cargo transfer operations between fleets and colonies.

PROJ-436 Phase 7: the legacy ``VALID_CARGO_TYPES`` hardcoded whitelist is
gone. The cargo-type acceptance check now consults
``ResourceCatalog.has(...)`` for resource IDs and a tiny set of categorical
sentinels (``"passengers"`` for population, ``"drop_pod"`` / ``"vehicle"``
for the ``BayInventory`` item slices). The resource list is now driven by
``data/resources.json`` as the single source of truth — adding a new
resource there makes it transferrable automatically, no validator update
needed.
"""
import logging
from typing import Any, Dict
from game.core.resources import ResourceCatalog
from game.core.validation import ValidationResult

logger = logging.getLogger(__name__)


# Categorical (non-resource) cargo-type sentinels.
#
# These three are recognised in addition to any resource ID in the
# Core-layer ``ResourceCatalog``:
#
# * ``"passengers"`` — population transfer (Container POPULATION slice;
#   on fleets, currently aggregated as one bucket).
# * ``"drop_pod"`` — :class:`DropPod` item transfer via
#   :class:`BayInventory.pods` / :attr:`Planet.staging_yard`.
# * ``"vehicle"`` — design-backed :class:`CarriedVehicle` item transfer
#   via the same bay/staging substrate (PROJ-FMS-A).
#
# Each maps to a distinct dispatch branch in
# :mod:`game.strategy.engine.order_handlers.transfer_branches`. They are
# NOT resources and intentionally live outside ``data/resources.json``.
_CATEGORICAL_CARGO_TYPES: frozenset[str] = frozenset({
    "passengers",
    "drop_pod",
    "vehicle",
})


# Module-level catalog handle. Lazy-loaded on first access so import
# order does not require ``data/resources.json`` to be present. Tests
# may not need to override this — the canonical catalog covers the
# eight production resource IDs.
_resource_catalog: ResourceCatalog | None = None


def _get_resource_catalog() -> ResourceCatalog:
    global _resource_catalog
    if _resource_catalog is None:
        _resource_catalog = ResourceCatalog.from_json()
    return _resource_catalog


def _is_known_cargo_type(cargo_type: str) -> bool:
    """Return True iff ``cargo_type`` is a recognised transfer kind.

    A cargo type is recognised when it is either:

    * one of the categorical sentinels (``"passengers"``,
      ``"drop_pod"``, ``"vehicle"``), or
    * a resource ID present in the Core-layer
      :class:`ResourceCatalog` (which loads ``data/resources.json``).

    PROJ-436 Phase 7: replaces the deleted ``VALID_CARGO_TYPES``
    hardcoded set. New resources added to ``data/resources.json``
    become transferrable automatically.
    """
    if cargo_type in _CATEGORICAL_CARGO_TYPES:
        return True
    return _get_resource_catalog().has(cargo_type)


class TransferValidator:
    """Validates TRANSFER orders for cargo operations between fleets and colonies."""

    # Valid directions
    VALID_DIRECTIONS = {"load", "unload"}  # str values match TransferDirection enum

    @staticmethod
    def validate(
        galaxy: Any,
        fleet: Any,
        target: Any,
        cargo_type: str,
        direction: str,
        amount: int,
        species_id: str = None,
        skip_location_check: bool = False,
        projected_cargo: int = None
    ) -> ValidationResult:
        """
        Validate if a fleet can perform a transfer operation with a colony or another fleet.

        Args:
            galaxy: The Galaxy object
            fleet: The Fleet object attempting the transfer (source for unload, target for load)
            target: The Planet or Fleet object to transfer with
            cargo_type: Type of cargo to transfer (e.g., 'passengers')
            direction: 'load' (target->fleet) or 'unload' (fleet->target)
            amount: Units to transfer (0 = all available)

        Returns:
            ValidationResult with error codes
        """
        # 1. Validate fleet exists
        if not fleet:
            return ValidationResult.error("Fleet does not exist.", code="FLEET_NOT_FOUND")

        # 2. Validate target exists
        if not target:
            return ValidationResult.error("Target does not exist.", code="TARGET_NOT_FOUND")

        # 3. Validate direction
        if direction not in TransferValidator.VALID_DIRECTIONS:
            return ValidationResult.error(
                f"Invalid direction '{direction}'. Must be 'load' or 'unload'.",
                code="INVALID_DIRECTION"
            )

        # 4. Validate cargo_type via the registry-driven contract
        #    (PROJ-436 Phase 7). Resource IDs come from the Core-layer
        #    ``ResourceCatalog`` (``data/resources.json``); the three
        #    categorical sentinels ("passengers" / "drop_pod" /
        #    "vehicle") cover the non-resource transfer kinds.
        if not _is_known_cargo_type(cargo_type):
            return ValidationResult.error(
                f"Invalid cargo type '{cargo_type}'.",
                code="INVALID_CARGO_TYPE"
            )

        # 5. Validate location (skip when queuing orders with auto-move)
        from game.core.protocols import is_planet, is_fleet

        if is_planet(target) and not skip_location_check:
            # PROJ-68: Check if fleet is in the system containing the target planet
            fleet_system = galaxy.get_system_at_location(fleet.location)
            target_system = None

            # Find system containing target planet
            for sys in galaxy.systems.values():
                if target in sys.planets:
                    target_system = sys
                    break

            if fleet_system != target_system:
                return ValidationResult.error(
                    f"Fleet is not at {target.name}'s system.",
                    code="NOT_AT_PLANET"
                )
            # drop_pod and vehicle transfers use the staging yard, which
            # does not require the planet to be colonized.
            if target.owner_id is None and cargo_type not in ("drop_pod", "vehicle"):
                return ValidationResult.error(
                    f"Planet {target.name} is not colonized.",
                    code="NOT_COLONIZED"
                )
        elif is_fleet(target):
            if fleet.location != target.location:
                return ValidationResult.error(
                    "Fleets are not at the same location.",
                    code="NOT_CO_LOCATED"
                )
            if fleet.id == target.id:
                return ValidationResult.error(
                    "Cannot transfer cargo to the same fleet.",
                    code="SAME_ENTITY"
                )

        # 6. Direction-specific validation
        if is_planet(target):
            if direction == "load":
                return TransferValidator._validate_load(fleet, target, cargo_type, amount, species_id, projected_cargo)
            else:  # unload
                return TransferValidator._validate_unload(fleet, target, cargo_type, amount, species_id, projected_cargo)
        else: # fleet
            return TransferValidator._validate_fleet_transfer(fleet, target, cargo_type, direction, amount, species_id)

    @staticmethod
    def _validate_fleet_transfer(
        fleet: Any,
        target_fleet: Any,
        cargo_type: str,
        direction: str,
        amount: int,
        species_id: str = None
    ) -> ValidationResult:
        """Validate a transfer between two fleets."""
        if cargo_type == "passengers":
            source = fleet if direction == "unload" else target_fleet
            dest = target_fleet if direction == "unload" else fleet

            # Check source has cargo
            current_cargo = source.get_fleet_cargo_current("passengers")
            if current_cargo <= 0:
                return ValidationResult.error(
                    f"Source fleet {source.id} has no passengers to transfer.",
                    code="NO_CARGO_TO_UNLOAD"
                )

            # Check destination has space
            capacity = dest.get_fleet_cargo_capacity("passengers")
            current = dest.get_fleet_cargo_current("passengers")
            if current >= capacity:
                return ValidationResult.error(
                    f"Destination fleet {dest.id} has no passenger capacity.",
                    code="NO_CARGO_SPACE"
                )

        return ValidationResult.success()

    @staticmethod
    def _validate_load(
        fleet: Any,
        planet: Any,
        cargo_type: str,
        amount: int,
        species_id: str = None,
        projected_cargo: int = None
    ) -> ValidationResult:
        """Validate a load operation (colony -> fleet)."""
        if cargo_type == "drop_pod":
            # Validate staging yard has items
            staging = getattr(planet, 'staging_yard', [])
            if not isinstance(staging, list):
                staging = []
            if not staging:
                return ValidationResult.error(
                    f"{planet.name} has no items in staging yard.",
                    code="NO_STAGING_ITEMS"
                )
            # Validate fleet has pod storage capacity
            try:
                capacity = fleet.resources.get_fleet_pod_capacity()
                used = fleet.resources.get_fleet_pod_mass_used()
                if capacity <= 0 or used >= capacity:
                    return ValidationResult.error(
                        "Fleet has no pod storage capacity.",
                        code="NO_POD_CAPACITY"
                    )
            except (AttributeError, TypeError):
                return ValidationResult.error(
                    "Fleet has no pod storage capacity.",
                    code="NO_POD_CAPACITY"
                )
            return ValidationResult.success()

        if cargo_type == "vehicle":
            # PROJ-FMS-A: design-backed carried-vehicle load. Mirrors the
            # drop_pod path: staging yard must contain at least one
            # CarriedVehicle-shaped entry, and the fleet must have at
            # least one ship with VehicleBay capacity remaining.
            return TransferValidator._validate_vehicle_load(
                fleet, planet, species_id
            )

        # For passengers, check fleet has cargo capacity
        # PROJ-210: Use fleet.resources delegate for cargo operations
        if cargo_type == "passengers":
            # PROJ-401 (B-02): species_id is required for passenger LOAD.
            # PROJ-393 deleted the executor's first-species fallback in
            # transfer_branches.py:101-111, so a missing species_id no-ops at
            # runtime. Validation must reject the same shape so orders are not
            # queued only to silently transfer 0 at execution time.
            if species_id is None:
                return ValidationResult.error(
                    f"Passenger load on {planet.name} requires a species selection.",
                    code="MISSING_SPECIES_ID"
                )

            capacity = fleet.resources.get_fleet_cargo_capacity("passengers")
            # Use projected cargo if provided (accounts for earlier queued orders)
            current = projected_cargo if projected_cargo is not None else fleet.resources.get_fleet_cargo_current("passengers")
            available_space = capacity - current
            logger.info(f"DIAG _validate_load: capacity={capacity}, current/projected={current}, available_space={available_space}, projected_cargo_param={projected_cargo}")

            if available_space <= 0:
                logger.info(f"DIAG _validate_load: REJECTED - NO_CARGO_SPACE")
                return ValidationResult.error(
                    "Fleet has no available passenger capacity.",
                    code="NO_CARGO_SPACE"
                )

            # Check colony has population
            if planet.total_population <= 0:
                logger.info(f"DIAG _validate_load: REJECTED - NO_POPULATION on {planet.name}")
                return ValidationResult.error(
                    f"{planet.name} has no population to load.",
                    code="NO_POPULATION"
                )

            if species_id:
                has_species = any(p.race_id == species_id and p.count > 0 for p in planet.populations)
                logger.info(f"DIAG _validate_load: species_id={species_id}, has_species={has_species}")
                if not has_species:
                    return ValidationResult.error(
                        f"{planet.name} has no {species_id} population to load.",
                        code="NO_POPULATION"
                    )

        logger.info(f"DIAG _validate_load: PASSED")
        return ValidationResult.success()


    @staticmethod
    def _validate_unload(
        fleet: Any,
        planet: Any,
        cargo_type: str,
        amount: int,
        species_id: str = None,
        projected_cargo: int = None
    ) -> ValidationResult:
        """Validate an unload operation (fleet -> colony)."""
        # Check fleet has cargo to unload (use projected if available)
        # PROJ-210: Use fleet.resources delegate for cargo operations
        if cargo_type == "passengers":
            current_cargo = projected_cargo if projected_cargo is not None else fleet.resources.get_fleet_cargo_current("passengers")
            if current_cargo <= 0:
                return ValidationResult.error(
                    "Fleet has no passengers to unload.",
                    code="NO_CARGO_TO_UNLOAD"
                )

        if cargo_type == "vehicle":
            # PROJ-FMS-A: design-backed carried-vehicle unload. Fleet
            # must have at least one CarriedVehicle entry; the planet
            # staging yard must have capacity for at least the smallest
            # carried vehicle. (Per-item capacity is re-checked by
            # ``planet.add_to_staging_yard`` at execution time.)
            return TransferValidator._validate_vehicle_unload(fleet, planet, species_id)

        return ValidationResult.success()

    @staticmethod
    def _validate_vehicle_load(
        fleet: Any,
        planet: Any,
        design_id: str = None,
    ) -> ValidationResult:
        """PROJ-FMS-A: validate planet -> fleet carried-vehicle load.

        Mirrors the drop-pod path: planet staging yard must contain at
        least one ``CarriedVehicle``-shaped entry (optionally matching
        ``design_id``), and the fleet must have at least one ship with
        ``VehicleBay`` capacity remaining for the smallest matching item.

        PROJ-431 Phase 1d: the legacy ``CarriedVehicle.from_any(...)``
        discriminator is replaced by an explicit dict-shape match
        against ``VALID_VEHICLE_TYPES``. The planet staging yard is
        still on the legacy dict substrate (its migration is a later
        phase); we only avoid the runtime discriminator in this file.
        """
        from game.strategy.data.carried_vehicle import CarriedVehicle

        staging = getattr(planet, "staging_yard", [])
        candidate: Any = None
        # PROJ-450 Phase 3: substrate is typed
        # ``List[CarriedVehicle | DropPod]``. DropPod entries are skipped
        # — only CarriedVehicle satisfies the vehicle-load branch.
        for item in staging:
            if isinstance(item, CarriedVehicle):
                cv = item
            else:
                continue
            if design_id and cv.design_id != design_id:
                continue
            candidate = cv
            break
        if candidate is None:
            return ValidationResult.error(
                f"{planet.name} has no matching carried vehicle in staging yard.",
                code="NO_STAGING_VEHICLE",
            )
        # Need at least one ship with a bay that can accept the smallest matching vehicle.
        for ship in getattr(fleet, "ships", []):
            mgr = getattr(ship, "_cargo_mgr", None)
            if mgr is None:
                continue
            try:
                if mgr.can_accept_vehicle(candidate):
                    return ValidationResult.success()
            except Exception as exc:  # Intentional broad catch: capability probe; missing registry => no capacity.
                _ = exc
                continue
        return ValidationResult.error(
            "Fleet has no vehicle-bay capacity for this vehicle.",
            code="NO_BAY_CAPACITY",
        )

    @staticmethod
    def _validate_vehicle_unload(
        fleet: Any,
        planet: Any,
        design_id: str = None,
    ) -> ValidationResult:
        """PROJ-FMS-A: validate fleet -> planet carried-vehicle unload.

        Fleet must have at least one ``CarriedVehicle`` entry matching
        ``design_id`` (or any, if ``design_id`` is None). Planet staging
        capacity is re-checked per-item by
        ``planet.add_to_staging_yard`` at execution time; we only verify
        there is capacity for the smallest matching item up-front so we
        don't queue an order that cannot transfer anything.
        """
        candidate: Any = None
        for ship in getattr(fleet, "ships", []):
            cargo_mgr = getattr(ship, "_cargo_mgr", None)
            if cargo_mgr is None:
                continue
            try:
                carried = cargo_mgr.get_carried_vehicles()
            except Exception as exc:  # Intentional broad catch: facade probe; treat missing accessor as empty.
                _ = exc
                continue
            for cv in carried:
                if design_id and cv.design_id != design_id:
                    continue
                if candidate is None or cv.mass < candidate.mass:
                    candidate = cv
        if candidate is None:
            return ValidationResult.error(
                "Fleet has no matching carried vehicle to unload.",
                code="NO_CARGO_TO_UNLOAD",
            )
        # Check planet staging yard has at least enough capacity for the smallest vehicle.
        max_staging = float(getattr(planet, "max_staging_mass", 0.0) or 0.0)
        if max_staging > 0:
            current = float(planet.get_staging_mass())
            if current + candidate.mass > max_staging:
                return ValidationResult.error(
                    f"{planet.name} staging yard has no capacity for this vehicle.",
                    code="NO_STAGING_CAPACITY",
                )
        return ValidationResult.success()
