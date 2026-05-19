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


def test_constructor_records_registries_and_event_bus():
    """Constructor-injected collaborators are stored for spawn helpers."""
    registries = MagicMock()
    event_bus = MagicMock()

    spawner = ProductionSpawner(registries=registries, event_bus=event_bus)

    assert spawner._registries is registries
    assert spawner._event_bus is event_bus


def _wire_catalog(spawner, empire_id: int, design_data: dict | None = None):
    """PROJ-427 Phase 3: install a per-empire DesignCatalog containing
    a single design for every test design_id we expect to be looked up.
    Returns the catalog so tests can assert on
    ``pending_built_counts`` etc.
    """
    from game.strategy.systems.design_catalog import DesignCatalog
    cat = DesignCatalog(empire_id=empire_id)
    data = design_data if design_data is not None else {"name": "Test"}
    # Populate every design_id used by the test set.
    for design_id in (
        "ferrite_mine", "frig", "yard", "pod", "any", "any_id", "missing",
        "complex",
    ):
        cat._data_by_id[design_id] = data
    spawner.set_design_catalogs_by_empire({empire_id: cat})
    return cat


def test_spawn_dispatches_complex_to_create_and_place_facility_for_colony():
    """Colony + 'complex' type → `_create_and_place_facility` mutates planet.facilities.

    PROJ-427 Phase 3: design data resolved via the in-memory DesignCatalog.
    """
    spawner = ProductionSpawner(registries=MagicMock())
    item = {"design_id": "ferrite_mine", "type": "complex"}
    planet = _planet()
    empire = _empire()
    _wire_catalog(spawner, empire.id, {"name": "Ferrite Mine"})

    spawner.spawn_completed_item(item, empire, planet, MagicMock(), 1)

    assert len(planet.facilities) == 1
    facility = planet.facilities[0]
    assert facility.design_id == "ferrite_mine"
    assert facility.name == "Ferrite Mine"
    assert facility.is_operational is True


def test_spawn_dispatches_drop_pod_to_staging_yard_for_colony():
    """Colony + 'drop_pod' type → `_spawn_to_staging_yard`."""
    spawner = ProductionSpawner(registries=MagicMock())
    item = {"design_id": "pod1", "type": "drop_pod"}
    empire = _empire()
    planet = _planet()
    galaxy = MagicMock()

    with patch.object(spawner, "_spawn_to_staging_yard") as mock_stage:
        spawner.spawn_completed_item(item, empire, planet, galaxy, 1)
    mock_stage.assert_called_once_with(planet, "pod1", item, empire)


def test_spawn_dispatches_default_ship_path_for_colony_default_type():
    """Colony + 'ship' type → real `_spawn_ship` creates a Fleet with the ship.

    PROJ-427 Phase 3: design comes from the catalog; built count flows to
    the catalog's pending map (no DesignLibrary).
    """
    spawner = ProductionSpawner(registries=MagicMock())
    item = {"design_id": "frig", "type": "ship"}
    planet = _planet()
    empire = _empire()
    galaxy = MagicMock()
    galaxy.get_next_fleet_id.return_value = 42
    galaxy.get_system_of_planet.return_value = None  # take fallback path

    cat = _wire_catalog(spawner, empire.id, {"name": "Frigate"})
    fake_ship = MagicMock()
    fake_ship.name = "Frigate"
    fake_ship.design_data = {"name": "Frigate", "layers": {}, "vehicle_type": "Ship"}
    fake_ship.get_calculated_stats.return_value = {
        "mass": 100.0, "strategic_movement": 5.0,
    }

    with patch(
        "game.strategy.engine.production_spawner.ShipInstance.create",
        return_value=fake_ship,
    ) as mock_create:
        spawner.spawn_completed_item(item, empire, planet, galaxy, 1)

    assert cat.pending_built_counts.get("frig") == 1
    # PROJ-353A Tier-7 (T2.2): pin concrete kwargs flowing into
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
    """Fleet + 'ship' type → real `_spawn_fleet_ship` adds ship to fleet."""
    spawner = ProductionSpawner(registries=MagicMock())
    item = {"design_id": "frig", "type": "ship"}
    fleet = _fleet_at(HexCoord(0, 0))
    empire = _empire()

    cat = _wire_catalog(spawner, empire.id, {"name": "Frigate"})
    fake_ship = MagicMock()
    fake_ship.name = "Frigate"
    fake_ship.design_data = {"name": "Frigate", "layers": {}, "vehicle_type": "Ship"}
    fake_ship.get_calculated_stats.return_value = {
        "mass": 100.0, "strategic_movement": 5.0,
    }

    with patch(
        "game.strategy.engine.production_spawner.ShipInstance.create",
        return_value=fake_ship,
    ) as mock_create:
        spawner.spawn_completed_item(item, empire, fleet, MagicMock(), 1)

    mock_create.assert_called_once_with(
        design_id="frig",
        design_data={"name": "Frigate"},
        owner_id=empire.id,
        name="Frigate",
        empire=empire,
        registries=spawner._registries,
    )
    assert cat.pending_built_counts.get("frig") == 1
    fleet.add_ship.assert_called_once_with(fake_ship)
    empire.add_fleet.assert_not_called()


def test_spawn_dispatches_to_fleet_complex_when_fleet_and_complex_type():
    """Fleet + 'complex' type → `_spawn_fleet_complex` lands facility on planet."""
    spawner = ProductionSpawner(registries=MagicMock())
    item = {"design_id": "yard", "type": "complex"}
    fleet = _fleet_at(HexCoord(5, 5))
    planet = _planet(planet_id=1, name="Alpha")
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [planet]
    galaxy.get_system_of_planet.return_value = None
    empire = _empire()
    _wire_catalog(spawner, empire.id, {"name": "Space Yard"})

    spawner.spawn_completed_item(item, empire, fleet, galaxy, 1)

    galaxy.get_planets_at_global_hex.assert_called_once_with(fleet.location)
    assert len(planet.facilities) == 1
    facility = planet.facilities[0]
    assert facility.design_id == "yard"
    assert facility.name == "Space Yard"


# ---------------------------------------------------------------------------
# _load_design fallback semantics (PROJ-427 Phase 3: catalog-based)
# ---------------------------------------------------------------------------


def test_load_design_returns_empty_dict_when_no_catalog():
    """Missing catalog → empty dict (NOT None)."""
    spawner = ProductionSpawner(registries=MagicMock())
    result = spawner._load_design("any", _empire())
    assert result == {}


def test_load_design_returns_empty_dict_when_design_missing():
    """Catalog without the design returns empty dict."""
    from game.strategy.systems.design_catalog import DesignCatalog
    spawner = ProductionSpawner(registries=MagicMock())
    empire = _empire()
    cat = DesignCatalog(empire_id=empire.id)
    # Catalog wired but design absent.
    spawner.set_design_catalogs_by_empire({empire.id: cat})
    assert spawner._load_design("missing", empire) == {}


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
        spawner._spawn_ship(planet, "frig", empire, galaxy)

    # PROJ-353A Tier-7 (T2.2): pin no-arg shape of get_next_fleet_id().
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
        spawner._spawn_ship(planet, "frig", empire, galaxy)

    # Third positional arg to Fleet() is the spawn location
    spawn_loc_arg = fake_fleet_cls.call_args[0][2]
    assert spawn_loc_arg == HexCoord(11, 1)


def test_spawn_ship_without_galaxy_uses_local_location_and_fleet_id_zero():
    """Missing galaxy uses the planet's local hex and logs empty system fields."""
    event_bus = MagicMock()
    spawner = ProductionSpawner(registries=MagicMock(), event_bus=event_bus)
    empire = _empire()
    planet = _planet()
    planet.location = HexCoord(3, -2)
    fake_ship = MagicMock()
    fake_ship.name = "NoGalaxy"

    fake_fleet_cls = MagicMock()
    constructed_fleet = MagicMock()
    constructed_fleet.id = 0
    fake_fleet_cls.return_value = constructed_fleet

    with patch.object(spawner, "_load_and_create_ship", return_value=fake_ship), \
            patch("game.strategy.engine.production_spawner.Fleet", fake_fleet_cls):
        spawner._spawn_ship(planet, "frig", empire, galaxy=None)

    fake_fleet_cls.assert_called_once()
    assert fake_fleet_cls.call_args[0][0] == 0
    assert fake_fleet_cls.call_args[0][2] == planet.location
    empire.add_fleet.assert_called_once_with(constructed_fleet)
    event_kwargs = event_bus.log_event.call_args.kwargs
    assert event_kwargs["location_hex"] == [3, -2]
    assert event_kwargs["system_name"] == ""
    assert event_kwargs["local_hex"] is None


# ---------------------------------------------------------------------------
# _resolve_planet_location: event metadata edge cases
# ---------------------------------------------------------------------------


def test_resolve_planet_location_without_galaxy_returns_empty_metadata():
    """No galaxy context should leave event location metadata empty."""
    spawner = ProductionSpawner(registries=MagicMock())

    assert spawner._resolve_planet_location(_planet(), None) == (None, "", None)


def test_resolve_planet_location_without_lookup_method_returns_empty_metadata():
    """Galaxy-like objects without planet lookup are ignored."""
    spawner = ProductionSpawner(registries=MagicMock())
    galaxy = object()

    assert spawner._resolve_planet_location(_planet(), galaxy) == (None, "", None)


def test_resolve_planet_location_with_system_and_planet_location_returns_hex_lists():
    """Resolved systems provide global and local hex lists for event payloads."""
    spawner = ProductionSpawner(registries=MagicMock())
    planet = _planet()
    planet.location = HexCoord(2, -1)
    system = MagicMock()
    system.name = "Vega"
    system.global_location = HexCoord(10, 5)
    galaxy = MagicMock()
    galaxy.get_system_of_planet.return_value = system

    location_hex, system_name, local_hex = spawner._resolve_planet_location(planet, galaxy)

    assert location_hex == [12, 4]
    assert system_name == "Vega"
    assert local_hex == [2, -1]


def test_resolve_planet_location_with_system_but_no_planet_location_keeps_hexes_empty():
    """A resolved system still omits hex metadata when the planet has no location."""
    spawner = ProductionSpawner(registries=MagicMock())
    planet = _planet()
    planet.location = None
    system = MagicMock()
    system.name = "Vega"
    galaxy = MagicMock()
    galaxy.get_system_of_planet.return_value = system

    location_hex, system_name, local_hex = spawner._resolve_planet_location(planet, galaxy)

    assert location_hex is None
    assert system_name == "Vega"
    assert local_hex is None


# ---------------------------------------------------------------------------
# _spawn_to_staging_yard: design_data preference + staging-yard-full warning
# ---------------------------------------------------------------------------


def test_spawn_to_staging_yard_uses_design_data_from_item_when_present():
    """If `item['design_data']` is set, `_load_design` is NOT called."""
    spawner = ProductionSpawner(registries=MagicMock())
    item = {"design_id": "pod", "type": "drop_pod",
            "design_data": {"name": "InlinePod"}}
    planet = _planet()

    with patch.object(spawner, "_load_design") as mock_load:
        spawner._spawn_to_staging_yard(planet, "pod", item, _empire())

    mock_load.assert_not_called()
    # PROJ-450 Phase 2: drop_pod routes through typed DropPod; the
    # inline ``name`` lands in :attr:`DropPod.payload`.
    staged = planet.add_to_staging_yard.call_args[0][0]
    assert staged.payload["name"] == "InlinePod"


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
        spawner._spawn_to_staging_yard(planet, "pod", item, _empire())

    # PROJ-353A Tier-7 (T2.2): pin the cross-layer call with concrete args
    # — design_data dict + registries instance — so a future signature
    # change registers as a test failure.
    mock_calc.assert_called_once_with({"name": "TestPod"}, spawner._registries)
    # PROJ-450 Phase 2: the mass landed on the typed staging entry.
    staged = planet.add_to_staging_yard.call_args[0][0]
    assert staged.mass == 4200.0


def test_production_spawner_requires_registries():
    """PROJ-382 Phase 3 (Pattern #3 strategy-layer DI tightening):
    ``registries`` is a required keyword-only argument.

    Replaces the prior ``test_spawn_to_staging_yard_skips_mass_calculation_when_no_registries``
    which asserted the silent-fallback path that has been removed; the
    silent fallback hid construction-time DI failures, and the
    refactored contract surfaces them at the construction call instead.
    """
    import pytest
    with pytest.raises(TypeError, match="requires registries"):
        ProductionSpawner(registries=None)


def test_spawn_to_staging_yard_logs_warning_when_full(caplog):
    """`add_to_staging_yard` returning False emits a 'Staging yard full' warning."""
    spawner = ProductionSpawner(registries=MagicMock())
    planet = _planet()
    planet.add_to_staging_yard = MagicMock(return_value=False)
    item = {"design_id": "pod", "type": "drop_pod",
            "design_data": {"name": "Pod"}}

    import logging
    with caplog.at_level(logging.WARNING):
        spawner._spawn_to_staging_yard(planet, "pod", item, _empire())
    assert "Staging yard full" in caplog.text


# ---------------------------------------------------------------------------
# _spawn_fleet_complex: target_planet_id resolution
# ---------------------------------------------------------------------------


def test_spawn_fleet_complex_uses_target_planet_id_when_specified():
    """`target_planet_id` matching a planet at the hex picks that planet."""
    spawner = ProductionSpawner(registries=MagicMock())
    fleet = _fleet_at(HexCoord(5, 5))
    p1 = _planet(planet_id=1, name="Alpha")
    p2 = _planet(planet_id=2, name="Beta")
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [p1, p2]
    galaxy.get_system_of_planet.return_value = None

    with patch.object(spawner, "_create_and_place_facility") as mock_create:
        spawner._spawn_fleet_complex(
            fleet, "complex", _empire(), galaxy,
            target_planet_id=2,
        )
    chosen_planet = mock_create.call_args[0][0]
    assert chosen_planet is p2


def test_spawn_fleet_complex_falls_back_to_first_planet_when_target_id_missing():
    """`target_planet_id` not matching any planet → first planet (silent)."""
    spawner = ProductionSpawner(registries=MagicMock())
    fleet = _fleet_at(HexCoord(5, 5))
    p1 = _planet(planet_id=1, name="Alpha")
    p2 = _planet(planet_id=2, name="Beta")
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = [p1, p2]
    galaxy.get_system_of_planet.return_value = None

    with patch.object(spawner, "_create_and_place_facility") as mock_create:
        spawner._spawn_fleet_complex(
            fleet, "complex", _empire(), galaxy,
            target_planet_id=999,  # nonexistent
        )
    chosen_planet = mock_create.call_args[0][0]
    # Pinned silent-wrong-planet behavior per design.md surprise #3.
    assert chosen_planet is p1


def test_spawn_fleet_complex_returns_when_galaxy_missing():
    """Fleet complex spawning requires galaxy context for planet lookup."""
    spawner = ProductionSpawner(registries=MagicMock())
    fleet = _fleet_at(HexCoord(5, 5))

    with patch.object(spawner, "_create_and_place_facility") as mock_create:
        spawner._spawn_fleet_complex(
            fleet, "complex", _empire(), galaxy=None,
        )

    mock_create.assert_not_called()


def test_spawn_fleet_complex_returns_when_fleet_not_at_planet_hex():
    """No planet at the fleet hex cancels complex placement."""
    spawner = ProductionSpawner(registries=MagicMock())
    fleet = _fleet_at(HexCoord(5, 5))
    galaxy = MagicMock()
    galaxy.get_planets_at_global_hex.return_value = []

    with patch.object(spawner, "_create_and_place_facility") as mock_create:
        spawner._spawn_fleet_complex(
            fleet, "complex", _empire(), galaxy=galaxy,
        )

    galaxy.get_planets_at_global_hex.assert_called_once_with(fleet.location)
    mock_create.assert_not_called()


# ---------------------------------------------------------------------------
# PROJ-427 Phase 3: invert the Phase 0 characterization. The spawn chain
# now uses DesignCatalog and no longer imports DesignLibrary.
# ---------------------------------------------------------------------------


def test_proj427_production_spawner_does_not_import_design_library():
    """PROJ-427 Phase 3: ProductionSpawner no longer imports DesignLibrary."""
    import inspect
    import game.strategy.engine.production_spawner as ps_mod

    assert not hasattr(ps_mod, "DesignLibrary"), (
        "PROJ-427 Phase 3: DesignLibrary must NOT be imported into the "
        "production spawner module."
    )
    src = inspect.getsource(ps_mod)
    assert "from game.strategy.systems.design_library" not in src


def test_proj427_load_design_helpers_use_catalog():
    """PROJ-427 Phase 3: spawn helpers fall back to {}/None when no
    catalog is wired (replacing the prior save_path coupling)."""
    spawner = ProductionSpawner(registries=MagicMock())
    empire = _empire()

    assert spawner._load_design("any_id", empire) == {}
    assert spawner._load_and_create_ship("any_id", empire) is None


def test_proj427_spawn_uses_catalog_no_design_library():
    """PROJ-427 Phase 3: colony complex spawn pulls design data from the
    catalog — no DesignLibrary construction."""
    spawner = ProductionSpawner(registries=MagicMock())
    item = {"design_id": "ferrite_mine", "type": "complex"}
    planet = _planet()
    empire = _empire()
    _wire_catalog(spawner, empire.id, {"name": "Ferrite Mine"})

    spawner.spawn_completed_item(item, empire, planet, MagicMock(), 1)

    assert len(planet.facilities) == 1
    assert planet.facilities[0].name == "Ferrite Mine"
