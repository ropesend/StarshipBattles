"""Regression tests for staging yard spawn crashes.

Crash 1: _spawn_to_staging_yard passed empire.id (int) to _load_design(),
which then tried .id on the int again -> AttributeError.

Crash 2: Mass calculation called .get('mass') on a Component object
(returned by registries.components), which has no .get() method.
"""

import pytest
from unittest.mock import MagicMock, patch
from game.strategy.engine.production_spawner import ProductionSpawner
from game.strategy.events.event_types import EventType, EventCategory


def _make_empire(empire_id: int = 1) -> MagicMock:
    empire = MagicMock()
    empire.id = empire_id
    return empire


def _make_planet() -> MagicMock:
    planet = MagicMock()
    planet.name = "TestPlanet"
    planet.add_to_staging_yard = MagicMock(return_value=True)
    return planet


class TestSpawnToStagingYardEmpireParam:
    """Regression: _spawn_to_staging_yard must pass Empire object to _load_design."""

    def test_load_design_receives_empire_object_not_int(self):
        """When design_data is not cached in the item, _load_design must
        receive the Empire object (not empire.id) so it can access .id itself."""
        spawner = ProductionSpawner(registries=MagicMock())
        empire = _make_empire(empire_id=42)
        planet = _make_planet()
        item = {'design_id': 'fighter_mk1', 'type': 'fighter'}

        with patch.object(spawner, '_load_design', return_value={'name': 'Fighter'}) as mock_load:
            spawner._spawn_to_staging_yard(planet, 'fighter_mk1', item, empire)

        # The critical assertion: _load_design receives the Empire object, not an int
        mock_load.assert_called_once_with('fighter_mk1', empire)

    def test_spawn_to_staging_yard_no_crash_with_real_empire(self):
        """End-to-end: calling _spawn_to_staging_yard with an Empire object
        must not raise AttributeError on empire.id."""
        spawner = ProductionSpawner(registries=MagicMock())
        empire = _make_empire(empire_id=7)
        planet = _make_planet()
        item = {'design_id': 'drop_pod_1', 'type': 'drop_pod',
                'design_data': {'name': 'DropPod', 'components': []}}

        # Should not raise - design_data is in the item so _load_design is skipped
        spawner._spawn_to_staging_yard(planet, 'drop_pod_1', item, empire)
        planet.add_to_staging_yard.assert_called_once()

    def test_spawn_to_staging_yard_uses_empire_id_for_owner(self):
        """The staging entry should land in the planet's staging yard.

        PROJ-450 Phase 2: fighter / mine / satellite vehicle types now
        spawn as typed :class:`CarriedVehicle` entries (which do not
        carry ``owner_id``; the owning empire is recovered via the
        planet that holds the staging yard). For ``drop_pod`` and other
        types that route through :class:`DropPod`, ``owner_id`` lives
        in :attr:`DropPod.payload`. This test pins the typed-construction
        contract for the design-backed CarriedVehicle path.
        """
        from game.strategy.data.carried_vehicle import CarriedVehicle

        spawner = ProductionSpawner(registries=MagicMock())
        empire = _make_empire(empire_id=99)
        planet = _make_planet()
        item = {'design_id': 'fighter_x', 'type': 'fighter',
                'design_data': {'name': 'FighterX'}}

        spawner._spawn_to_staging_yard(planet, 'fighter_x', item, empire)

        staging_entry = planet.add_to_staging_yard.call_args[0][0]
        assert isinstance(staging_entry, CarriedVehicle)
        assert staging_entry.design_id == 'fighter_x'
        assert staging_entry.vehicle_type == 'fighter'


class TestSpawnToStagingYardMassCalculation:
    """Mass calculation uses ShipStatsCalculator (single source of truth)."""

    def test_mass_calculated_via_stats_calculator(self):
        """Mass should be calculated by ShipStatsCalculator with modifiers applied."""
        from game.core.registry import GameRegistries
        from game.simulation.components.component import load_components_data, load_modifiers_data
        from game.simulation.entities.ship_loader import load_vehicle_classes_data

        minimal = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
        registries = GameRegistries(
            components=load_components_data(registries=minimal),
            modifiers=load_modifiers_data(),
            vehicle_classes=load_vehicle_classes_data(),
            resources={}
        )

        spawner = ProductionSpawner(registries=registries)
        empire = _make_empire(empire_id=1)
        planet = _make_planet()
        # Design with a real component and size modifier (0.5 = half mass)
        design_data = {
            'name': 'TestPod',
            'ship_class': 'Drop Pod (Small)',
            'layers': {
                'CORE': [{'id': 'crew_quarters', 'modifiers': [
                    {'id': 'simple_size_mount', 'value': 0.5}
                ]}]
            }
        }
        item = {'design_id': 'pod_1', 'type': 'drop_pod',
                'design_data': design_data}

        spawner._spawn_to_staging_yard(planet, 'pod_1', item, empire)

        # PROJ-450 Phase 2: typed staging entry (DropPod for drop_pod type).
        staging_entry = planet.add_to_staging_yard.call_args[0][0]
        # crew_quarters base mass=30, with 0.5 size modifier = 15, plus hull base mass
        # Ship mass includes hull base mass from the vehicle class
        assert staging_entry.mass > 0
        assert staging_entry.mass == pytest.approx(65.0, abs=1.0)


# ---------------------------------------------------------------------------
# QA Observation 4: staged-yard spawn must emit a SHIP_BUILT event so the
# user sees feedback when fighter/mine/satellite/drop-pod queues complete.
# Prior to this fix, ``_spawn_to_staging_yard`` only logged to the python
# logger -- the in-game event log stayed silent and players had no way to
# tell whether their shipyard queue was actually producing anything.
# ---------------------------------------------------------------------------


def _planet_with_open_staging() -> MagicMock:
    """A planet whose staging yard accepts the next item."""
    planet = MagicMock()
    planet.id = 17
    planet.name = "OutpostPrime"
    planet.add_to_staging_yard = MagicMock(return_value=True)
    return planet


def _planet_with_full_staging() -> MagicMock:
    """A planet whose staging yard rejects the next item (full)."""
    planet = MagicMock()
    planet.id = 18
    planet.name = "OverflowWorld"
    planet.add_to_staging_yard = MagicMock(return_value=False)
    return planet


class TestStagingYardEmitsProductionEvent:
    """QA-OBS-4: every successful staging-yard spawn must emit SHIP_BUILT."""

    def test_successful_staging_spawn_emits_ship_built_event(self):
        event_bus = MagicMock()
        spawner = ProductionSpawner(registries=MagicMock(), event_bus=event_bus)
        empire = _make_empire(empire_id=7)
        planet = _planet_with_open_staging()
        item = {
            'design_id': 'fighter_mk1',
            'type': 'fighter',
            'design_data': {'name': 'Razor MK1'},
        }

        spawner._spawn_to_staging_yard(planet, 'fighter_mk1', item, empire)

        event_bus.log_event.assert_called_once()
        call = event_bus.log_event.call_args
        # Positional event_type
        assert call.args[0] == EventType.SHIP_BUILT
        assert call.kwargs['category'] == EventCategory.PRODUCTION
        assert call.kwargs['empire_id'] == 7
        # Message should call out the planet name so the event log is useful
        assert 'OutpostPrime' in call.kwargs['message']
        assert 'Razor MK1' in call.kwargs['message']

    def test_staging_full_emits_failure_event(self):
        """Production output discarded when staging full -- must still emit
        an event so the player can react (clear staging or pause queue)."""
        event_bus = MagicMock()
        spawner = ProductionSpawner(registries=MagicMock(), event_bus=event_bus)
        empire = _make_empire(empire_id=9)
        planet = _planet_with_full_staging()
        item = {
            'design_id': 'mine_v2',
            'type': 'mine',
            'design_data': {'name': 'Mk2 Mine'},
        }

        spawner._spawn_to_staging_yard(planet, 'mine_v2', item, empire)

        event_bus.log_event.assert_called_once()
        call = event_bus.log_event.call_args
        assert call.args[0] == EventType.SHIP_BUILT
        assert call.kwargs['category'] == EventCategory.PRODUCTION
        assert call.kwargs['empire_id'] == 9
        msg = call.kwargs['message']
        # Failure message should make it clear output was dropped
        assert 'OverflowWorld' in msg
        assert 'full' in msg.lower() or 'discarded' in msg.lower()

    def test_staging_spawn_with_no_event_bus_does_not_crash(self):
        """Backwards-compat: spawner constructed without an event_bus
        must still complete the spawn (event emission is a no-op)."""
        spawner = ProductionSpawner(registries=MagicMock(), event_bus=None)
        empire = _make_empire(empire_id=3)
        planet = _planet_with_open_staging()
        item = {
            'design_id': 'sat_relay',
            'type': 'satellite',
            'design_data': {'name': 'CommSat'},
        }
        # Should not raise
        spawner._spawn_to_staging_yard(planet, 'sat_relay', item, empire)
        planet.add_to_staging_yard.assert_called_once()
