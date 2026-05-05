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


def _stub_design_library(design_data: dict | None = None):
    """Build a DesignLibrary stub used by both _load_design and
    _load_and_create_ship. Returns the (cls, library, result) triple so
    tests can assert call counts on cls (constructor) and library (load).
    """
    result = MagicMock()
    result.success = True
    result.data = design_data if design_data is not None else {"name": "Test"}
    library = MagicMock()
    library.load_design_data.return_value = result
    library.increment_built_count = MagicMock()
    cls = MagicMock(return_value=library)
    return cls, library, result


def test_spawn_dispatches_complex_to_create_and_place_facility_for_colony():
    """Colony + 'complex' type → real `_create_and_place_facility` mutates planet.facilities.

    PROJ-345 T3.4: un-patches `_create_and_place_facility`. Uses a real
    DesignLibrary stub at the module boundary so the inner method runs
    in full (load → PlanetaryFacility() → planet.facilities.append).
    """
    spawner = ProductionSpawner()
    item = {"design_id": "ferrite_mine", "type": "complex"}
    planet = _planet()
    empire = _empire()
    cls, library, _ = _stub_design_library({"name": "Ferrite Mine"})

    with patch(
        "game.strategy.engine.production_spawner.DesignLibrary", cls,
    ):
        spawner.spawn_completed_item(item, empire, planet, MagicMock(), "/tmp", 1)

    # Real `_create_and_place_facility` ran: design loaded, facility appended.
    cls.assert_called_once_with("/tmp", empire.id)
    library.load_design_data.assert_called_once_with("ferrite_mine")
    assert len(planet.facilities) == 1
    facility = planet.facilities[0]
    assert facility.design_id == "ferrite_mine"
    assert facility.name == "Ferrite Mine"
    assert facility.is_operational is True


def test_spawn_dispatches_drop_pod_to_staging_yard_for_colony():
    """Colony + 'drop_pod' type → `_spawn_to_staging_yard`.

    Staging-yard helper kept patched per phase_1_checklist scope (task
    only un-patches `_load_and_create_ship`, `_create_and_place_facility`,
    `_spawn_fleet_ship`).
    """
    spawner = ProductionSpawner()
    item = {"design_id": "pod1", "type": "drop_pod"}
    empire = _empire()
    planet = _planet()
    galaxy = MagicMock()

    with patch.object(spawner, "_spawn_to_staging_yard") as mock_stage:
        spawner.spawn_completed_item(item, empire, planet, galaxy, None, 1)
    # PROJ-353 Tier-7 (T2.2): pin concrete dispatch args, not just call count.
    mock_stage.assert_called_once_with(planet, "pod1", item, empire, None)


def test_spawn_dispatches_default_ship_path_for_colony_default_type():
    """Colony + 'ship' type → real `_spawn_ship` creates a Fleet with the ship.

    PROJ-345 T3.4: un-patches `_load_and_create_ship` (called by
    `_spawn_ship`). DesignLibrary, ShipInstance.create, and the Fleet
    constructor are stubbed at the module boundary; `_spawn_ship` runs
    in full and calls `empire.add_fleet` with a Fleet that contains the
    created ship.
    """
    spawner = ProductionSpawner(registries=MagicMock())
    item = {"design_id": "frig", "type": "ship"}
    planet = _planet()
    empire = _empire()
    galaxy = MagicMock()
    galaxy.get_next_fleet_id.return_value = 42
    galaxy.get_system_of_planet.return_value = None  # take fallback path

    cls, library, _ = _stub_design_library({"name": "Frigate"})
    # Bare MagicMock (not spec=ShipInstance) so Fleet.add_ship's downstream
    # speed recalc can reach design_data + calculated stats.
    fake_ship = MagicMock()
    fake_ship.name = "Frigate"
    fake_ship.design_data = {"name": "Frigate", "layers": {}, "vehicle_type": "Ship"}
    fake_ship.get_calculated_stats.return_value = {
        "mass": 100.0, "strategic_movement": 5.0,
    }

    with patch(
        "game.strategy.engine.production_spawner.DesignLibrary", cls,
    ), patch(
        "game.strategy.engine.production_spawner.ShipInstance.create",
        return_value=fake_ship,
    ) as mock_create:
        spawner.spawn_completed_item(item, empire, planet, galaxy, "/tmp", 1)

    # Real `_spawn_ship` ran end-to-end: design loaded, ShipInstance.create
    # called, built count incremented, a real Fleet constructed with the
    # galaxy fleet_id, ship added to fleet, fleet added to empire.
    library.load_design_data.assert_called_once_with("frig")
    library.increment_built_count.assert_called_once_with("frig")
    # PROJ-353 Tier-7 (T2.2): pin concrete kwargs flowing into
    # ShipInstance.create — design_id/owner_id/name routing.
    mock_create.assert_called_once_with(
        design_id="frig",
        design_data={"name": "Frigate"},
        owner_id=empire.id,
        name="Frigate",
        empire=empire,
        registries=spawner._registries,
    )
    galaxy.get_next_fleet_id.assert_called_once_with()
    empire.add_fleet.assert_called_once()
    new_fleet = empire.add_fleet.call_args[0][0]
    assert isinstance(new_fleet, Fleet)
    assert new_fleet.id == 42
    assert new_fleet.owner_id == empire.id
    assert fake_ship in new_fleet.ships


def test_spawn_dispatches_to_fleet_ship_when_owner_is_fleet():
    """Fleet + 'ship' type → real `_spawn_fleet_ship` adds ship to fleet.

    PROJ-345 T3.4: un-patches `_spawn_fleet_ship`. The real method calls
    `_load_and_create_ship` (also un-patched), which is stubbed at the
    DesignLibrary + ShipInstance.create boundaries. End state: the
    building fleet receives the new ship via `fleet.add_ship`.
    """
    spawner = ProductionSpawner(registries=MagicMock())
    item = {"design_id": "frig", "type": "ship"}
    fleet = _fleet_at(HexCoord(0, 0))
    empire = _empire()

    cls, library, _ = _stub_design_library({"name": "Frigate"})
    # Bare MagicMock (not spec=ShipInstance) so Fleet.add_ship's downstream
    # speed recalc can reach design_data + calculated stats.
    fake_ship = MagicMock()
    fake_ship.name = "Frigate"
    fake_ship.design_data = {"name": "Frigate", "layers": {}, "vehicle_type": "Ship"}
    fake_ship.get_calculated_stats.return_value = {
        "mass": 100.0, "strategic_movement": 5.0,
    }

    with patch(
        "game.strategy.engine.production_spawner.DesignLibrary", cls,
    ), patch(
        "game.strategy.engine.production_spawner.ShipInstance.create",
        return_value=fake_ship,
    ) as mock_create:
        spawner.spawn_completed_item(item, empire, fleet, MagicMock(), "/tmp", 1)

    # Real `_spawn_fleet_ship` ran: ship added to the building fleet,
    # built count incremented, NO new fleet allocated on the empire.
    library.load_design_data.assert_called_once_with("frig")
    # PROJ-353 Tier-7 (T2.2): pin ShipInstance.create kwargs.
    mock_create.assert_called_once_with(
        design_id="frig",
        design_data={"name": "Frigate"},
        owner_id=empire.id,
        name="Frigate",
        empire=empire,
        registries=spawner._registries,
    )
    library.increment_built_count.assert_called_once_with("frig")
    fleet.add_ship.assert_called_once_with(fake_ship)
    empire.add_fleet.assert_not_called()


def test_spawn_dispatches_to_fleet_complex_when_fleet_and_complex_type():
    """Fleet + 'complex' type → real `_spawn_fleet_complex` lands facility on planet.

    PROJ-345 T3.4: un-patches `_create_and_place_facility` (called by
    `_spawn_fleet_complex`). With a planet at the fleet's hex, the real
    chain runs: `_spawn_fleet_complex` → `_create_and_place_facility` →
    `planet.facilities.append`.
    """
    spawner = ProductionSpawner()
    item = {"design_id": "yard", "type": "complex"}
    fleet = _fleet_at(HexCoord(5, 5))
    planet = _planet(planet_id=1, name="Alpha")
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [planet]
    galaxy.get_system_of_planet.return_value = None
    empire = _empire()
    cls, library, _ = _stub_design_library({"name": "Space Yard"})

    with patch(
        "game.strategy.engine.production_spawner.DesignLibrary", cls,
    ):
        spawner.spawn_completed_item(item, empire, fleet, galaxy, "/tmp", 1)

    # Real chain ran: planet was looked up at the fleet's hex; facility
    # was constructed from loaded design data and appended to the planet.
    galaxy.get_planets_at_global_hex.assert_called_once_with(fleet.location)
    library.load_design_data.assert_called_once_with("yard")
    assert len(planet.facilities) == 1
    facility = planet.facilities[0]
    assert facility.design_id == "yard"
    assert facility.name == "Space Yard"


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

    # PROJ-353 Tier-7 (T2.2): pin no-arg shape of get_next_fleet_id().
    galaxy.get_next_fleet_id.assert_called_once_with()
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


def test_spawn_to_staging_yard_reaches_into_simulation_for_mass_calculation():
    """design.md surprise #2: `_spawn_to_staging_yard` performs an
    in-method import of `game.simulation.entities.ship_design_stats`
    and calls `calculate_design_stats` to compute the staging item's
    mass. This pins the cross-layer reach-in (strategy → simulation)
    so a future layering refactor that breaks the import path fails
    the test rather than silently shipping mass=0.0 staging items.

    Pins production at production_spawner.py:251-254.
    """
    spawner = ProductionSpawner(registries=MagicMock())
    item = {"design_id": "pod", "type": "drop_pod",
            "design_data": {"name": "TestPod"}}
    planet = _planet()

    with patch(
        "game.simulation.entities.ship_design_stats.calculate_design_stats",
        return_value={"mass": 4200.0},
    ) as mock_calc:
        spawner._spawn_to_staging_yard(planet, "pod", item, _empire(), "/tmp")

    # PROJ-353 Tier-7 (T2.2): pin the cross-layer call with concrete args
    # — design_data dict + registries instance — so a future signature
    # change registers as a test failure.
    mock_calc.assert_called_once_with({"name": "TestPod"}, spawner._registries)
    # The mass landed on the staging item.
    staged = planet.add_to_staging_yard.call_args[0][0]
    assert staged["mass"] == 4200.0


def test_spawn_to_staging_yard_skips_mass_calculation_when_no_registries():
    """When `_registries` is None, the simulation reach-in is skipped
    and the staged item gets mass=0.0. Pins the guard at
    production_spawner.py:251 (`if self._registries:`)."""
    spawner = ProductionSpawner()  # registries default = None
    item = {"design_id": "pod", "type": "drop_pod",
            "design_data": {"name": "NoRegPod"}}
    planet = _planet()

    with patch(
        "game.simulation.entities.ship_design_stats.calculate_design_stats",
    ) as mock_calc:
        spawner._spawn_to_staging_yard(planet, "pod", item, _empire(), "/tmp")

    mock_calc.assert_not_called()
    staged = planet.add_to_staging_yard.call_args[0][0]
    assert staged["mass"] == 0.0


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
