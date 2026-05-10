"""Per-handler tests for `TransferHandler` (PROJ-368 Phase 3).

Drives the handler directly. Covers all 7 explicit dispatch branches +
BUG-70 LOAD_POPULATION auto-resolve + PROJ-343 T1.1 target_fleet_id
resolution path.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.planet import SpeciesPopulation
from game.strategy.engine.order_handlers.transfer import TransferHandler


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

    ship = MagicMock()
    ship.name = "Carrier"
    ship.carried_items = []
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
    assert ship.carried_items == [pod_b]
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
    ship = MagicMock()
    pod_x = {"name": "PodX"}
    ship.carried_items = [pod_x]
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
    planet.add_to_staging_yard.assert_called_once_with(pod_x)
    assert ship.carried_items == []


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
