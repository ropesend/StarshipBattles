"""Per-handler tests for `TransferHandler` (PROJ-368 Phase 3).

Drives the handler directly. Covers all 7 explicit dispatch branches +
BUG-70 LOAD_POPULATION auto-resolve + PROJ-343 T1.1 target_fleet_id
resolution path.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.species_population import SpeciesPopulation
from game.strategy.engine.order_handlers.transfer import TransferHandler


def _bay_ship(*, name: str = "Ship", pods: list | None = None) -> MagicMock:
    """PROJ-436 Phase 9 helper: MagicMock ship with a wired-up typed
    :class:`BayInventory` and a ``set_bay_inventory`` write-through.
    The legacy ``carried_items`` mirror is gone — production code
    reads the typed ``bay_inventory.pods`` slot directly.
    """
    ship = MagicMock()
    ship.name = name
    pods = list(pods or [])

    def _typed_pod(p) -> DropPod:
        if isinstance(p, DropPod):
            return p
        if isinstance(p, dict):
            return DropPod(
                design_id=str(p.get("design_id", "")),
                design_data=dict(p.get("design_data", {})),
                mass=float(p.get("mass", 0.0)),
                payload={
                    k: v for k, v in p.items()
                    if k not in {"design_id", "design_data", "mass"}
                },
            )
        return DropPod(design_id="", design_data={}, mass=0.0, payload={})

    typed_pods = [_typed_pod(p) for p in pods]
    ship.bay_inventory = BayInventory(bay=[], pods=typed_pods)

    def _set_bay_inventory(bi: BayInventory) -> None:
        ship.bay_inventory = bi

    ship.set_bay_inventory = _set_bay_inventory
    return ship


def _fleet(fleet_id: int = 1, location: HexCoord = HexCoord(0, 0)):
    f = MagicMock(spec=Fleet)
    f.id = fleet_id
    f.location = location
    f.ships = []
    f.orders = []  # required for is_fleet() protocol check
    f.pop_order = MagicMock()
    return f


def _planet(planet_id: int = 1, name: str = "P", *, owner_id: int = 0):
    p = MagicMock()
    p.id = planet_id
    p.name = name
    p.owner_id = owner_id
    p.populations = []
    p.facilities = []
    p.staging_yard = []
    p.planet_type = "continental"
    return p


def _empire(empire_id: int = 0):
    e = MagicMock()
    e.id = empire_id
    e.fleets = []
    e.race_config = MagicMock(race_id="humans")
    return e


def _ok_validation():
    v = MagicMock()
    v.is_valid = True
    return v


# ---------------------------------------------------------------------------
# Early-out / validation branches
# ---------------------------------------------------------------------------


def test_no_order_returns_failure():
    handler = TransferHandler()
    fleet = MagicMock(spec=Fleet)
    fleet.get_current_order.return_value = None
    result = handler.execute_action_order(fleet, _empire(), MagicMock())
    assert result.success is False


def test_invalid_params_pops_and_returns_failure():
    handler = TransferHandler()
    fleet = _fleet()
    fleet.get_current_order.return_value = Order(OrderType.TRANSFER, "not_a_dict")
    result = handler.execute_action_order(fleet, _empire(), MagicMock())
    assert result.success is False
    fleet.pop_order.assert_called_once()


def test_validation_failure_pops_and_returns_failure():
    handler = TransferHandler()
    fleet = _fleet()
    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = _planet()
    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {"direction": "load", "cargo_type": "metals", "amount": 5, "planet_id": 1},
    )
    bad = MagicMock()
    bad.is_valid = False
    bad.message = "nope"
    bad.error_code = "X"
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=bad,
    ):
        result = handler.execute_action_order(fleet, _empire(), galaxy)
    assert result.success is False
    fleet.pop_order.assert_called_once()


# ---------------------------------------------------------------------------
# Branch 1: planet -> fleet, resource cargo
# ---------------------------------------------------------------------------


def test_dispatch_load_planet_resource():
    handler = TransferHandler()
    fleet = _fleet()
    fleet.resources.get_fleet_cargo_capacity.return_value = 100
    fleet.resources.get_fleet_cargo_current.return_value = 0
    fleet.resources.load_cargo_to_fleet = MagicMock()
    planet = _planet()
    planet.get_stockpile.return_value = 50.0
    planet.consume_from_stockpile = MagicMock()

    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = planet

    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {"direction": "load", "cargo_type": "metals", "amount": 30, "planet_id": 1},
    )
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = handler.execute_action_order(fleet, _empire(), galaxy)
    assert result.success is True
    assert result.amount_transferred == 30
    planet.consume_from_stockpile.assert_called_once_with("metals", 30.0)
    fleet.resources.load_cargo_to_fleet.assert_called_once_with("metals", 30)


# ---------------------------------------------------------------------------
# Branch 2: planet -> fleet, passengers
# ---------------------------------------------------------------------------


def test_dispatch_load_planet_passengers_specific_species():
    handler = TransferHandler()
    fleet = _fleet()
    fleet.resources.get_fleet_cargo_capacity.return_value = 100
    fleet.resources.get_fleet_cargo_current.return_value = 0
    fleet.resources.load_cargo_to_fleet = MagicMock()

    planet = _planet()
    pop_humans = SpeciesPopulation(race_id="humans", count=20, happiness=0.5)
    pop_zorgs = SpeciesPopulation(race_id="zorgs", count=15, happiness=0.5)
    planet.populations = [pop_zorgs, pop_humans]  # zorgs FIRST to verify filter

    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = planet

    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {
            "direction": "load",
            "cargo_type": "passengers",
            "amount": 10,
            "planet_id": 1,
            "species_id": "humans",
        },
    )
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = handler.execute_action_order(fleet, _empire(), galaxy)
    assert result.success is True
    assert pop_humans.count == 10  # 20 - 10
    assert pop_zorgs.count == 15   # untouched
    fleet.resources.load_cargo_to_fleet.assert_called_once_with("passengers", 10)


# ---------------------------------------------------------------------------
# Branch 3: planet -> fleet, drop_pod (staging yard reverse iteration)
# ---------------------------------------------------------------------------


def test_dispatch_drop_pod_load_reverse_iteration():
    handler = TransferHandler()
    fleet = _fleet()

    ship = _bay_ship(name="Carrier")
    ship.get_pod_storage_capacity.return_value = 100
    ship.get_pod_storage_used.return_value = 0
    ship.can_carry_pod.return_value = True
    fleet.ships = [ship]

    planet = _planet()
    pod_a = {"name": "PodA", "mass": 10}
    pod_b = {"name": "PodB", "mass": 10}
    planet.staging_yard = [pod_a, pod_b]
    planet.remove_from_staging_yard = MagicMock(side_effect=lambda i: planet.staging_yard.pop(i))

    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = planet

    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {
            "direction": "load",
            "cargo_type": "drop_pod",
            "amount": 1,
            "planet_id": 1,
            "species_id": "PodB",  # request specifically PodB
        },
    )
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = handler.execute_action_order(fleet, _empire(), galaxy)
    assert result.success is True
    assert result.amount_transferred == 1
    # PodB was loaded; PodA remains in staging.
    # PROJ-431 Phase 1d: pods now live on bay_inventory.pods. The legacy
    # carried_items mirror is preserved by ``_bay_ship`` for tests that
    # still assert on that shape.
    assert len(ship.bay_inventory.pods) == 1
    assert ship.bay_inventory.pods[0].payload.get("name") == "PodB"
    assert planet.staging_yard == [pod_a]


# ---------------------------------------------------------------------------
# Branch 4: fleet -> planet, resource cargo
# ---------------------------------------------------------------------------


def test_dispatch_unload_planet_resource():
    handler = TransferHandler()
    fleet = _fleet()
    fleet.resources.get_fleet_cargo_current.return_value = 25
    fleet.resources.unload_cargo_from_fleet = MagicMock(return_value=20)

    planet = _planet()
    planet.add_to_stockpile = MagicMock()

    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = planet

    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {"direction": "unload", "cargo_type": "metals", "amount": 20, "planet_id": 1},
    )
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = handler.execute_action_order(fleet, _empire(), galaxy)
    assert result.success is True
    assert result.amount_transferred == 20
    planet.add_to_stockpile.assert_called_once_with("metals", 20.0)


# ---------------------------------------------------------------------------
# Branch 5: fleet -> planet, passengers (creates SpeciesPopulation if missing)
# ---------------------------------------------------------------------------


def test_dispatch_unload_planet_passengers_creates_species_population():
    handler = TransferHandler()
    fleet = _fleet()
    fleet.resources.get_fleet_cargo_current.return_value = 5
    fleet.resources.unload_cargo_from_fleet = MagicMock(return_value=5)

    planet = _planet()
    planet.populations = []  # no existing population, must be created

    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = planet

    fleet.get_current_order.return_value = Order(
        OrderType.UNLOAD_POPULATION,
        {
            "direction": "unload",
            "cargo_type": "passengers",
            "amount": 5,
            "planet_id": 1,
            "species_id": "humans",
        },
    )
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = handler.execute_action_order(fleet, _empire(), galaxy)
    assert result.success is True
    assert len(planet.populations) == 1
    assert planet.populations[0].race_id == "humans"
    assert planet.populations[0].count == 5


def test_dispatch_unload_planet_passengers_existing_species_increments():
    handler = TransferHandler()
    fleet = _fleet()
    fleet.resources.get_fleet_cargo_current.return_value = 5
    fleet.resources.unload_cargo_from_fleet = MagicMock(return_value=5)

    planet = _planet()
    pop = SpeciesPopulation(race_id="humans", count=3, happiness=0.5)
    planet.populations = [pop]

    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = planet

    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {
            "direction": "unload",
            "cargo_type": "passengers",
            "amount": 5,
            "planet_id": 1,
            "species_id": "humans",
        },
    )
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        handler.execute_action_order(fleet, _empire(), galaxy)
    assert pop.count == 8


# ---------------------------------------------------------------------------
# Branch 6: fleet -> planet, drop_pod (unload to staging yard)
# ---------------------------------------------------------------------------


def test_dispatch_drop_pod_unload():
    handler = TransferHandler()
    fleet = _fleet()
    pod_x = {"name": "PodX", "design_id": "drop_pod_basic", "mass": 0.0}
    ship = _bay_ship(pods=[pod_x])
    fleet.ships = [ship]

    planet = _planet()
    planet.add_to_staging_yard = MagicMock(return_value=True)

    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = planet

    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {
            "direction": "unload",
            "cargo_type": "drop_pod",
            "amount": 1,
            "planet_id": 1,
        },
    )
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = handler.execute_action_order(fleet, _empire(), galaxy)
    assert result.success is True
    assert result.amount_transferred == 1
    # The pod arrives at staging as a flattened dict. The handler
    # rebuilds the dict at the boundary, so its exact shape is implementation
    # detail — assert it carries the pod identity rather than identity-equal.
    assert planet.add_to_staging_yard.call_count == 1
    delivered = planet.add_to_staging_yard.call_args.args[0]
    assert delivered.get("name") == "PodX"
    assert delivered.get("design_id") == "drop_pod_basic"
    # PROJ-436 Phase 9: ship's bay_inventory.pods is drained.
    assert ship.bay_inventory.pods == []


# ---------------------------------------------------------------------------
# F-B-002 regression: carried-vehicle load rollback respects capacity API
# ---------------------------------------------------------------------------


def test_dispatch_carried_vehicle_load_rollback_routes_through_capacity_check():
    """PROJ-445 Phase 2 (F-B-002) — when ``_dispatch_carried_vehicle_load``
    has to roll back a removed staging-yard item because the carrier's
    ``load_vehicle`` returned False, the restore MUST go through
    :meth:`Planet.add_to_staging_yard` (the capacity-checked API), not
    through the raw ``staging_yard.append``. Without this contract,
    any future change to ``add_to_staging_yard`` (e.g., adding a type
    check, an ownership check, or a max-count cap) would be silently
    bypassed by the rollback path.

    The scenario: one fighter is staged on the planet; the fleet has a
    ship that ``can_accept_vehicle`` (so it becomes the load target)
    but whose ``load_vehicle`` returns False (so the dispatch enters
    the rollback branch). Assert ``planet.add_to_staging_yard`` was
    called exactly once with the rolled-back item.
    """
    handler = TransferHandler()
    fleet = _fleet()
    fighter_dict = {
        "design_id": "fighter_alpha",
        "design_data": {"name": "fighter_alpha"},
        "vehicle_type": "fighter",
        "mass": 20.0,
        "current_hp": 80,
    }

    ship = MagicMock()
    ship.name = "Carrier"
    ship._cargo_mgr.can_accept_vehicle = MagicMock(return_value=True)
    ship._cargo_mgr.load_vehicle = MagicMock(return_value=False)  # forces rollback
    fleet.ships = [ship]

    planet = _planet()
    planet.staging_yard = [fighter_dict]
    planet.remove_from_staging_yard = MagicMock(
        side_effect=lambda i: planet.staging_yard.pop(i)
    )
    planet.add_to_staging_yard = MagicMock(return_value=True)

    galaxy = MagicMock()
    galaxy.get_planet_by_id.return_value = planet

    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {
            "direction": "load",
            "cargo_type": "vehicle",
            "amount": 1,
            "planet_id": 1,
            "species_id": "fighter_alpha",
        },
    )

    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        handler.execute_action_order(fleet, _empire(), galaxy)

    planet.add_to_staging_yard.assert_called_once()
    restored = planet.add_to_staging_yard.call_args.args[0]
    assert restored is fighter_dict, (
        "Rollback must restore the originally-removed item, unchanged."
    )


# ---------------------------------------------------------------------------
# Branch 7: fleet <-> fleet
# ---------------------------------------------------------------------------


def test_dispatch_fleet_to_fleet_load_direction():
    """Load direction means: target_fleet -> fleet."""
    handler = TransferHandler()
    fleet = _fleet(fleet_id=1)
    target = _fleet(fleet_id=2)
    target.resources.get_fleet_cargo_current.return_value = 30  # source has cargo
    fleet.resources.get_fleet_cargo_capacity.return_value = 50
    fleet.resources.get_fleet_cargo_current.return_value = 0
    target.resources.unload_cargo_from_fleet = MagicMock(return_value=20)
    fleet.resources.load_cargo_to_fleet = MagicMock()

    empire = _empire()
    empire.fleets = [fleet, target]
    galaxy = MagicMock(spec=[])  # no `empires` attr
    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {
            "direction": "load",
            "cargo_type": "metals",
            "amount": 20,
            "target_fleet_id": 2,
        },
    )
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success is True
    assert result.amount_transferred == 20
    target.resources.unload_cargo_from_fleet.assert_called_once_with("metals", 20)
    fleet.resources.load_cargo_to_fleet.assert_called_once_with("metals", 20)


def test_dispatch_fleet_to_fleet_unload_direction():
    """Unload direction means: fleet -> target_fleet."""
    handler = TransferHandler()
    fleet = _fleet(fleet_id=1)
    target = _fleet(fleet_id=2)
    fleet.resources.get_fleet_cargo_current.return_value = 30  # source has cargo
    target.resources.get_fleet_cargo_capacity.return_value = 50
    target.resources.get_fleet_cargo_current.return_value = 0
    fleet.resources.unload_cargo_from_fleet = MagicMock(return_value=20)
    target.resources.load_cargo_to_fleet = MagicMock()

    empire = _empire()
    empire.fleets = [fleet, target]
    galaxy = MagicMock(spec=[])
    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {
            "direction": "unload",
            "cargo_type": "metals",
            "amount": 20,
            "target_fleet_id": 2,
        },
    )
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success is True
    fleet.resources.unload_cargo_from_fleet.assert_called_once_with("metals", 20)
    target.resources.load_cargo_to_fleet.assert_called_once_with("metals", 20)


# ---------------------------------------------------------------------------
# PROJ-445 Phase 2 (F-B-003 + DI-2026-05-18-001 fleet-to-fleet half):
# drop_pod and vehicle cargo_types route through bay_inventory, not the
# generic resource path. Previously these silently returned 0.
# ---------------------------------------------------------------------------


def test_dispatch_fleet_to_fleet_drop_pod_moves_pod_to_target_bay():
    """Source fleet's ship has a drop_pod; target fleet's ship has bay
    capacity; the pod ends up in the target ship's typed pod slot and
    the source ship's pod slot is drained. Pre-fix this returned 0
    because the generic cargo path doesn't know about
    ``bay_inventory.pods``.
    """
    handler = TransferHandler()

    pod_payload = {"name": "PodAlpha", "design_id": "drop_pod_basic", "mass": 100.0}
    src_ship = _bay_ship(name="Carrier-S", pods=[pod_payload])
    src_ship._cargo_mgr = MagicMock()
    src_ship._cargo_mgr.can_carry_pod = MagicMock(return_value=False)  # source full

    dst_ship = _bay_ship(name="Carrier-D")
    dst_ship._cargo_mgr = MagicMock()
    dst_ship._cargo_mgr.can_carry_pod = MagicMock(return_value=True)

    fleet = _fleet(fleet_id=1)
    fleet.ships = [src_ship]
    target = _fleet(fleet_id=2)
    target.ships = [dst_ship]

    empire = _empire()
    empire.fleets = [fleet, target]
    galaxy = MagicMock(spec=[])
    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {
            "direction": "unload",
            "cargo_type": "drop_pod",
            "amount": 1,
            "target_fleet_id": 2,
        },
    )
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = handler.execute_action_order(fleet, empire, galaxy)

    assert result.success is True
    assert result.amount_transferred == 1
    assert src_ship.bay_inventory.pods == []
    assert len(dst_ship.bay_inventory.pods) == 1
    assert dst_ship.bay_inventory.pods[0].payload.get("name") == "PodAlpha"


def test_dispatch_fleet_to_fleet_vehicle_moves_carried_vehicle_to_target():
    """Source fleet's ship carries a vehicle; target fleet's ship has
    bay capacity; ``load_vehicle`` is called on the destination ship
    and ``unload_vehicle(idx)`` is called on the source. Pre-fix this
    returned 0 because the generic cargo path doesn't know about the
    bay's typed CarriedVehicle list.
    """
    from game.strategy.data.carried_vehicle import CarriedVehicle

    handler = TransferHandler()
    cv = CarriedVehicle(
        design_id="fighter_alpha",
        design_data={"name": "fighter_alpha", "vehicle_class": "Fighter (Small)"},
        vehicle_type="fighter",
        mass=20.0,
        current_hp=80,
    )

    src_ship = MagicMock()
    src_ship.name = "Src"
    src_ship._cargo_mgr = MagicMock()
    src_ship._cargo_mgr.get_carried_vehicles = MagicMock(return_value=[cv])
    src_ship._cargo_mgr.can_accept_vehicle = MagicMock(return_value=False)

    dst_ship = MagicMock()
    dst_ship.name = "Dst"
    dst_ship._cargo_mgr = MagicMock()
    dst_ship._cargo_mgr.can_accept_vehicle = MagicMock(return_value=True)
    dst_ship._cargo_mgr.load_vehicle = MagicMock(return_value=True)

    fleet = _fleet(fleet_id=1)
    fleet.ships = [src_ship]
    target = _fleet(fleet_id=2)
    target.ships = [dst_ship]

    empire = _empire()
    empire.fleets = [fleet, target]
    galaxy = MagicMock(spec=[])
    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {
            "direction": "unload",
            "cargo_type": "vehicle",
            "amount": 1,
            "target_fleet_id": 2,
            "species_id": "fighter_alpha",
        },
    )
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = handler.execute_action_order(fleet, empire, galaxy)

    assert result.success is True
    assert result.amount_transferred == 1
    dst_ship._cargo_mgr.load_vehicle.assert_called_once_with(cv)
    src_ship._cargo_mgr.unload_vehicle.assert_called_once_with(0)


def test_dispatch_fleet_to_fleet_drop_pod_returns_zero_when_dest_full():
    """When the destination fleet has no ship with pod capacity, the
    pod stays on the source ship and the transferred count is 0."""
    handler = TransferHandler()
    pod_payload = {"name": "PodAlpha", "design_id": "drop_pod_basic", "mass": 100.0}

    src_ship = _bay_ship(name="Src", pods=[pod_payload])
    src_ship._cargo_mgr = MagicMock()

    dst_ship = _bay_ship(name="Dst")
    dst_ship._cargo_mgr = MagicMock()
    dst_ship._cargo_mgr.can_carry_pod = MagicMock(return_value=False)  # full

    fleet = _fleet(fleet_id=1)
    fleet.ships = [src_ship]
    target = _fleet(fleet_id=2)
    target.ships = [dst_ship]

    empire = _empire()
    empire.fleets = [fleet, target]
    galaxy = MagicMock(spec=[])
    fleet.get_current_order.return_value = Order(
        OrderType.TRANSFER,
        {
            "direction": "unload",
            "cargo_type": "drop_pod",
            "amount": 1,
            "target_fleet_id": 2,
        },
    )
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = handler.execute_action_order(fleet, empire, galaxy)

    assert result.success is True
    assert result.amount_transferred == 0
    assert len(src_ship.bay_inventory.pods) == 1  # pod still on source
    assert dst_ship.bay_inventory.pods == []


# ---------------------------------------------------------------------------
# BUG-70: LOAD_POPULATION auto-resolve at fleet hex
# ---------------------------------------------------------------------------


def test_bug_70_load_population_auto_resolves_owned_colony():
    handler = TransferHandler()
    fleet = _fleet(location=HexCoord(2, 3))
    empire = _empire()
    colony = _planet(planet_id=5, name="Home", owner_id=empire.id)
    pop = SpeciesPopulation(race_id="humans", count=10, happiness=0.5)
    colony.populations = [pop]
    colony.total_population = 10

    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [colony]

    fleet.resources.get_fleet_cargo_capacity.return_value = 100
    fleet.resources.get_fleet_cargo_current.return_value = 0
    fleet.resources.load_cargo_to_fleet = MagicMock()

    fleet.get_current_order.return_value = Order(
        OrderType.LOAD_POPULATION,
        # PROJ-393: species_id is now required; legacy first-species fallback removed.
        {"direction": "load", "cargo_type": "passengers", "amount": 5, "species_id": "humans"},
    )
    with patch(
        "game.strategy.validation.TransferValidator.validate",
        return_value=_ok_validation(),
    ):
        result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success is True
    assert pop.count == 5
    fleet.resources.load_cargo_to_fleet.assert_called_once_with("passengers", 5)


def test_bug_70_no_owned_colony_skips_silently():
    handler = TransferHandler()
    fleet = _fleet(location=HexCoord(0, 0))
    empire = _empire()

    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = []

    fleet.get_current_order.return_value = Order(
        OrderType.LOAD_POPULATION,
        {"direction": "load", "cargo_type": "passengers", "amount": 5},
    )
    result = handler.execute_action_order(fleet, empire, galaxy)
    assert result.success is True
    assert "skipped" in result.message.lower()
    fleet.pop_order.assert_called_once()


# ---------------------------------------------------------------------------
# Target-fleet resolver
# ---------------------------------------------------------------------------


def test_target_fleet_resolves_via_galaxy_empires():
    handler = TransferHandler()
    fleet_a = _fleet(fleet_id=1)
    fleet_b = _fleet(fleet_id=99)
    other_empire = MagicMock()
    other_empire.fleets = [fleet_b]

    empire = _empire()
    empire.fleets = [fleet_a]

    galaxy = MagicMock()
    galaxy.empires = [empire, other_empire]

    target = handler._resolve_target_fleet_by_id(99, empire, galaxy)
    assert target is fleet_b


def test_target_fleet_resolves_via_empire_fleets_fallback():
    """When `galaxy.empires` is missing/empty, the fallback scan finds the fleet."""
    handler = TransferHandler()
    fleet_a = _fleet(fleet_id=1)
    fleet_b = _fleet(fleet_id=99)
    empire = _empire()
    empire.fleets = [fleet_a, fleet_b]

    galaxy = MagicMock(spec=[])  # no `empires` attr at all

    target = handler._resolve_target_fleet_by_id(99, empire, galaxy)
    assert target is fleet_b


def test_target_fleet_not_found_returns_none():
    handler = TransferHandler()
    empire = _empire()
    empire.fleets = []
    galaxy = MagicMock(spec=[])
    assert handler._resolve_target_fleet_by_id(99, empire, galaxy) is None
