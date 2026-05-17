"""PROJ-425 Phase 6 (TD-06 batch 5c) — forwarder demolition contract test.

Pins the absence of the cargo / carried-vehicle / pod-storage forwarder
methods on ``ShipInstance``. Phase 6 migrates all callers to
``ShipCargoManager`` (accessible via ``ship._cargo_mgr``) and removes
the thin wrappers from the entity.

If any of these assertions starts failing, a forwarder has been
re-introduced — either route the caller through ``_cargo_mgr`` instead
or update the canonical surface intentionally.
"""
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.ship_cargo_manager import ShipCargoManager


REMOVED_FORWARDERS = (
    # Cargo queries / mutators
    "get_cargo_capacity",
    "get_current_cargo",
    "get_cargo_space_available",
    "load_cargo",
    "unload_cargo",
    # Carried-vehicle queries
    "get_carried_vehicles",
    "get_carried_vehicles_by_type",
    "get_carried_vehicle_mass",
    "get_vehicle_bay_capacity",
    # Pod-storage helpers
    "get_pod_storage_capacity",
    "get_pod_storage_used",
    "can_carry_pod",
)


def test_ship_instance_no_longer_exposes_cargo_forwarders() -> None:
    """``ShipInstance`` must not define cargo/deployable forwarder methods."""
    for name in REMOVED_FORWARDERS:
        assert not hasattr(ShipInstance, name), (
            f"ShipInstance.{name} is still defined — this forwarder was "
            f"removed in PROJ-425 Phase 6. Callers must go through "
            f"`ship._cargo_mgr.{name}(...)`."
        )


def test_ship_cargo_manager_owns_the_full_surface() -> None:
    """``ShipCargoManager`` must expose the migrated surface."""
    for name in REMOVED_FORWARDERS:
        assert hasattr(ShipCargoManager, name), (
            f"ShipCargoManager.{name} is missing — Phase 6 expected the "
            f"manager to own this method as the canonical entry point."
        )
