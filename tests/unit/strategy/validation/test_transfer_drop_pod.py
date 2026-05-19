"""Tests for drop_pod transfer validation.

Verifies that drop_pod transfers work correctly through the TransferValidator,
including transfers from uncolonized planets with staging yards.
"""
from unittest.mock import MagicMock
from game.strategy.validation.transfer_validator import TransferValidator
from game.core.validation import ValidationResult


def _make_planet(owner_id=None, staging_items=None):
    # Use spec-free mock but delete fleet attributes so is_fleet() returns False
    planet = MagicMock()
    planet.id = 1
    planet.name = "TestPlanet"
    planet.owner_id = owner_id
    planet.planet_type = MagicMock()  # Ensures is_planet() returns True
    planet.staging_yard = list(staging_items or [])
    planet.total_population = 0
    planet.populations = []
    # Remove fleet-like attributes so is_fleet() returns False
    del planet.ships
    del planet.orders
    return planet


def _make_fleet(pod_capacity=2000.0, pod_mass_used=0.0):
    fleet = MagicMock()
    fleet.id = 10
    fleet.location = MagicMock()
    fleet.resources.get_fleet_pod_capacity.return_value = pod_capacity
    fleet.resources.get_fleet_pod_mass_used.return_value = pod_mass_used
    return fleet


def _pod_item(name="Colony Pod", mass=500.0):
    return {'vehicle_type': 'drop_pod', 'name': name, 'mass': mass}


def _make_galaxy(fleet, planet):
    galaxy = MagicMock()
    # Both fleet and planet resolve to the same system
    shared_system = MagicMock()
    shared_system.planets = [planet]
    galaxy.get_system_at_location.return_value = shared_system
    galaxy.systems = {'sys1': shared_system}
    return galaxy


class TestDropPodTransferValidation:
    """Test that drop_pod transfers pass validation correctly."""

    def test_drop_pod_load_from_uncolonized_planet_succeeds(self):
        """Loading a drop_pod from an uncolonized planet's staging yard should succeed."""
        planet = _make_planet(owner_id=None, staging_items=[_pod_item()])
        fleet = _make_fleet(pod_capacity=2000.0)
        galaxy = _make_galaxy(fleet, planet)

        result = TransferValidator.validate(
            galaxy, fleet, planet, "drop_pod", "load", 1,
            species_id="Colony Pod", skip_location_check=True
        )
        assert result.is_valid, f"Expected valid, got: {result.message}"

    def test_drop_pod_load_from_colonized_planet_succeeds(self):
        """Loading a drop_pod from a colonized planet should also succeed."""
        planet = _make_planet(owner_id=0, staging_items=[_pod_item()])
        fleet = _make_fleet(pod_capacity=2000.0)
        galaxy = _make_galaxy(fleet, planet)

        result = TransferValidator.validate(
            galaxy, fleet, planet, "drop_pod", "load", 1,
            species_id="Colony Pod", skip_location_check=True
        )
        assert result.is_valid

    def test_drop_pod_load_empty_staging_yard_fails(self):
        """Loading a drop_pod from empty staging yard should fail."""
        planet = _make_planet(owner_id=0, staging_items=[])
        fleet = _make_fleet(pod_capacity=2000.0)
        galaxy = _make_galaxy(fleet, planet)

        result = TransferValidator.validate(
            galaxy, fleet, planet, "drop_pod", "load", 1,
            skip_location_check=True
        )
        assert not result.is_valid
        assert result.error_code == "NO_STAGING_ITEMS"

    def test_drop_pod_load_no_fleet_capacity_fails(self):
        """Loading a drop_pod when fleet has no pod capacity should fail."""
        planet = _make_planet(owner_id=0, staging_items=[_pod_item()])
        fleet = _make_fleet(pod_capacity=0.0)
        galaxy = _make_galaxy(fleet, planet)

        result = TransferValidator.validate(
            galaxy, fleet, planet, "drop_pod", "load", 1,
            skip_location_check=True
        )
        assert not result.is_valid
        assert result.error_code == "NO_POD_CAPACITY"

    def test_drop_pod_load_fleet_full_fails(self):
        """Loading when fleet pod storage is full should fail."""
        planet = _make_planet(owner_id=0, staging_items=[_pod_item()])
        fleet = _make_fleet(pod_capacity=1000.0, pod_mass_used=1000.0)
        galaxy = _make_galaxy(fleet, planet)

        result = TransferValidator.validate(
            galaxy, fleet, planet, "drop_pod", "load", 1,
            skip_location_check=True
        )
        assert not result.is_valid
        assert result.error_code == "NO_POD_CAPACITY"

    def test_regular_cargo_from_uncolonized_planet_still_fails(self):
        """Non-drop_pod transfers from uncolonized planets should still fail."""
        planet = _make_planet(owner_id=None)
        fleet = _make_fleet()
        galaxy = _make_galaxy(fleet, planet)

        result = TransferValidator.validate(
            galaxy, fleet, planet, "metals", "load", 100
        )
        assert not result.is_valid
        assert result.error_code == "NOT_COLONIZED"

    def test_drop_pod_unload_succeeds(self):
        """Unloading a drop_pod to a planet should succeed."""
        from game.strategy.data.bay_inventory import BayInventory, DropPod
        planet = _make_planet(owner_id=0)
        fleet = _make_fleet()
        fleet.ships = [MagicMock()]
        pod = _pod_item()
        fleet.ships[0].bay_inventory = BayInventory(bay=[], pods=[DropPod(
            design_id='colony_pod', design_data={}, mass=pod['mass'],
            payload={'name': pod['name'], 'vehicle_type': 'drop_pod'},
        )])
        galaxy = _make_galaxy(fleet, planet)

        result = TransferValidator.validate(
            galaxy, fleet, planet, "drop_pod", "unload", 1,
            skip_location_check=True
        )
        assert result.is_valid


class TestDropPodTransferAgainstRealPlanet:
    """PROJ-450 codex-audit regression: TransferValidator must accept
    the tuple returned by the real Planet.staging_yard property, not
    just the list returned by MagicMock fixtures.

    Pre-fix: ``_validate_load`` did ``if not isinstance(staging, list):
    staging = []``. The real ``Planet.staging_yard`` is a typed
    read-only tuple (PROJ-450 Phase 3), so the isinstance check rejected
    it and planets with pods validated as empty.
    """

    def test_drop_pod_load_accepts_tuple_from_real_planet(self):
        """A real Planet has staging_yard as a tuple, not a list. Validator
        must accept it and detect the pod inside."""
        from game.core.hex_math import HexCoord
        from game.strategy.data.bay_inventory import DropPod
        from game.strategy.data.planet import Planet, PlanetType

        real_planet = Planet(
            name="RealPlanet",
            location=HexCoord(0, 0),
            orbit_distance=3,
            mass=5.97e24,
            radius=6.371e6,
            surface_area=5.1e14,
            density=5514.0,
            surface_gravity=9.81,
            surface_pressure=101325.0,
            surface_temperature=288.0,
            surface_water=0.71,
            tectonic_activity=0.6,
            magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL,
            owner_id=0,
        )
        real_planet.add_to_staging_yard(
            DropPod(
                design_id="colony_pod",
                design_data={},
                mass=500.0,
                payload={"name": "Colony Pod", "vehicle_type": "drop_pod"},
            )
        )
        # Sanity: the property really does return a tuple.
        assert isinstance(real_planet.staging_yard, tuple)
        assert len(real_planet.staging_yard) == 1

        fleet = _make_fleet(pod_capacity=2000.0)
        galaxy = _make_galaxy(fleet, real_planet)

        result = TransferValidator.validate(
            galaxy, fleet, real_planet, "drop_pod", "load", 1,
            species_id="Colony Pod", skip_location_check=True,
        )
        assert result.is_valid, (
            f"Validator must accept the tuple from real Planet.staging_yard; "
            f"got: {result.message}"
        )
