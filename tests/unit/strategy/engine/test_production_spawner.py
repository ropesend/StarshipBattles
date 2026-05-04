"""PROJ-333 Phase 1: ProductionSpawner characterization.

Pins dispatch routing in `spawn_completed_item` (colony complex /
drop pod / default ship / fleet ship / fleet complex) and the
helper-method behaviors documented in PROJ-333 design.md
(empty-dict design fallback, target_planet_id resolution with
fallback to first planet, staging-yard full warning).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.engine.production_spawner import ProductionSpawner


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _empire(empire_id: int = 1):
    emp = MagicMock()
    emp.id = empire_id
    emp.add_fleet = MagicMock()
    emp.get_next_fleet_display_number = MagicMock(return_value=2)
    return emp


def _planet(planet_id: int = 100, name: str = "TestPlanet"):
    planet = MagicMock()
    planet.id = planet_id
    planet.name = name
    planet.facilities = []
    planet.location = HexCoord(0, 0)
    planet.add_to_staging_yard = MagicMock(return_value=True)
    return planet


def _fleet_at(location: HexCoord, fleet_id: int = 1):
    fleet = MagicMock(spec=Fleet)
    fleet.id = fleet_id
    fleet.location = location
    fleet.add_ship = MagicMock()
    return fleet


# ---------------------------------------------------------------------------
# spawn_completed_item dispatch
# ---------------------------------------------------------------------------


def test_spawn_dispatches_complex_to_create_and_place_facility_for_colony():
    """Colony + 'complex' type → `_create_and_place_facility`."""
    spawner = ProductionSpawner()
    item = {"design_id": "ferrite_mine", "type": "complex"}
    planet = _planet()

    with patch.object(spawner, "_create_and_place_facility") as mock_facility:
        spawner.spawn_completed_item(item, _empire(), planet, MagicMock(), None, 1)
    mock_facility.assert_called_once()


def test_spawn_dispatches_drop_pod_to_staging_yard_for_colony():
    """Colony + 'drop_pod' type → `_spawn_to_staging_yard`."""
    spawner = ProductionSpawner()
    item = {"design_id": "pod1", "type": "drop_pod"}

    with patch.object(spawner, "_spawn_to_staging_yard") as mock_stage:
        spawner.spawn_completed_item(item, _empire(), _planet(), MagicMock(), None, 1)
    mock_stage.assert_called_once()


def test_spawn_dispatches_default_ship_path_for_colony_default_type():
    """Colony + missing/'ship' type → `_spawn_ship`."""
    spawner = ProductionSpawner()
    item = {"design_id": "frig", "type": "ship"}
    with patch.object(spawner, "_spawn_ship") as mock_ship:
        spawner.spawn_completed_item(item, _empire(), _planet(), MagicMock(), None, 1)
    mock_ship.assert_called_once()


def test_spawn_dispatches_to_fleet_ship_when_owner_is_fleet():
    """Fleet + non-complex → `_spawn_fleet_ship`."""
    spawner = ProductionSpawner()
    item = {"design_id": "frig", "type": "ship"}
    fleet = _fleet_at(HexCoord(0, 0))
    with patch.object(spawner, "_spawn_fleet_ship") as mock_fs:
        spawner.spawn_completed_item(item, _empire(), fleet, MagicMock(), None, 1)
    mock_fs.assert_called_once()


def test_spawn_dispatches_to_fleet_complex_when_fleet_and_complex_type():
    """Fleet + 'complex' type → `_spawn_fleet_complex`."""
    spawner = ProductionSpawner()
    item = {"design_id": "yard", "type": "complex"}
    fleet = _fleet_at(HexCoord(0, 0))
    with patch.object(spawner, "_spawn_fleet_complex") as mock_fc:
        spawner.spawn_completed_item(item, _empire(), fleet, MagicMock(), None, 1)
    mock_fc.assert_called_once()


# ---------------------------------------------------------------------------
# _load_design fallback semantics
# ---------------------------------------------------------------------------


def test_load_design_returns_empty_dict_when_no_save_path():
    """Missing save_path → empty dict (NOT None) per design.md observation."""
    spawner = ProductionSpawner()
    result = spawner._load_design("any", _empire(), None)
    assert result == {}


def test_load_design_returns_empty_dict_when_load_fails():
    """DesignLibrary failure → empty dict, NOT raised."""
    spawner = ProductionSpawner()
    failing = MagicMock()
    failing.success = False
    failing.error = "not found"
    fake_lib = MagicMock()
    fake_lib.load_design_data.return_value = failing

    with patch(
        "game.strategy.engine.production_spawner.DesignLibrary",
        return_value=fake_lib,
    ):
        result = spawner._load_design("missing", _empire(), "/tmp/save")
    assert result == {}


# ---------------------------------------------------------------------------
# _spawn_ship: fleet creation and location resolution
# ---------------------------------------------------------------------------


def test_spawn_ship_creates_new_fleet_with_unique_id_from_galaxy():
    """`_spawn_ship` requests `galaxy.get_next_fleet_id()` and adds the fleet."""
    spawner = ProductionSpawner(registries=MagicMock())
    empire = _empire()
    planet = _planet()

    fake_ship = MagicMock()
    fake_ship.name = "Frigate-A"

    galaxy = MagicMock()
    galaxy.get_next_fleet_id.return_value = 77
    galaxy.get_system_of_planet.return_value = None  # take fallback path

    fake_fleet_cls = MagicMock()
    constructed_fleet = MagicMock()
    constructed_fleet.id = 77
    fake_fleet_cls.return_value = constructed_fleet

    with patch.object(spawner, "_load_and_create_ship", return_value=fake_ship), \
            patch("game.strategy.engine.production_spawner.Fleet", fake_fleet_cls):
        spawner._spawn_ship(planet, "frig", empire, galaxy, save_path="/tmp")

    galaxy.get_next_fleet_id.assert_called_once()
    # Fleet constructor received the fleet_id from galaxy
    assert fake_fleet_cls.call_args[0][0] == 77
    empire.add_fleet.assert_called_once_with(constructed_fleet)


def test_spawn_ship_calculates_global_location_via_system_resolution():
    """When galaxy resolves a system, spawn loc = system.global + planet.location."""
    spawner = ProductionSpawner(registries=MagicMock())
    empire = _empire()
    planet = _planet()
    planet.location = HexCoord(1, 1)

    fake_system = MagicMock()
    fake_system.global_location = HexCoord(10, 0)
    fake_system.name = "Sol"

    galaxy = MagicMock()
    galaxy.get_system_of_planet.return_value = fake_system
    galaxy.get_next_fleet_id.return_value = 1

    fake_fleet_cls = MagicMock()
    fake_fleet_cls.return_value = MagicMock()

    with patch.object(spawner, "_load_and_create_ship", return_value=MagicMock(name="ship")), \
            patch("game.strategy.engine.production_spawner.Fleet", fake_fleet_cls):
        spawner._spawn_ship(planet, "frig", empire, galaxy, save_path="/tmp")

    # Third positional arg to Fleet() is the spawn location
    spawn_loc_arg = fake_fleet_cls.call_args[0][2]
    assert spawn_loc_arg == HexCoord(11, 1)


# ---------------------------------------------------------------------------
# _spawn_to_staging_yard: design_data preference + staging-yard-full warning
# ---------------------------------------------------------------------------


def test_spawn_to_staging_yard_uses_design_data_from_item_when_present():
    """If `item['design_data']` is set, `_load_design` is NOT called."""
    spawner = ProductionSpawner()
    item = {"design_id": "pod", "type": "drop_pod",
            "design_data": {"name": "InlinePod"}}
    planet = _planet()

    with patch.object(spawner, "_load_design") as mock_load:
        spawner._spawn_to_staging_yard(planet, "pod", item, _empire(), "/tmp")

    mock_load.assert_not_called()
    # Inline name flowed through to staging item
    staged = planet.add_to_staging_yard.call_args[0][0]
    assert staged["name"] == "InlinePod"


def test_spawn_to_staging_yard_logs_warning_when_full(caplog):
    """`add_to_staging_yard` returning False emits a 'Staging yard full' warning."""
    spawner = ProductionSpawner()
    planet = _planet()
    planet.add_to_staging_yard = MagicMock(return_value=False)
    item = {"design_id": "pod", "type": "drop_pod",
            "design_data": {"name": "Pod"}}

    import logging
    with caplog.at_level(logging.WARNING):
        spawner._spawn_to_staging_yard(planet, "pod", item, _empire(), "/tmp")
    assert "Staging yard full" in caplog.text


# ---------------------------------------------------------------------------
# _spawn_fleet_complex: target_planet_id resolution
# ---------------------------------------------------------------------------


def test_spawn_fleet_complex_uses_target_planet_id_when_specified():
    """`target_planet_id` matching a planet at the hex picks that planet."""
    spawner = ProductionSpawner()
    fleet = _fleet_at(HexCoord(5, 5))
    p1 = _planet(planet_id=1, name="Alpha")
    p2 = _planet(planet_id=2, name="Beta")
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [p1, p2]
    galaxy.get_system_of_planet.return_value = None

    with patch.object(spawner, "_create_and_place_facility") as mock_create:
        spawner._spawn_fleet_complex(
            fleet, "complex", _empire(), galaxy, save_path="/tmp",
            target_planet_id=2,
        )
    chosen_planet = mock_create.call_args[0][0]
    assert chosen_planet is p2


def test_spawn_fleet_complex_falls_back_to_first_planet_when_target_id_missing():
    """`target_planet_id` not matching any planet → first planet (silent)."""
    spawner = ProductionSpawner()
    fleet = _fleet_at(HexCoord(5, 5))
    p1 = _planet(planet_id=1, name="Alpha")
    p2 = _planet(planet_id=2, name="Beta")
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [p1, p2]
    galaxy.get_system_of_planet.return_value = None

    with patch.object(spawner, "_create_and_place_facility") as mock_create:
        spawner._spawn_fleet_complex(
            fleet, "complex", _empire(), galaxy, save_path="/tmp",
            target_planet_id=999,  # nonexistent
        )
    chosen_planet = mock_create.call_args[0][0]
    # Pinned silent-wrong-planet behavior per design.md surprise #3.
    assert chosen_planet is p1
