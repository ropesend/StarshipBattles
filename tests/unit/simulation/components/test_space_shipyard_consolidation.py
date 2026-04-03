"""Tests for consolidated space_shipyard component.

The space_shipyard component replaces both the old space_shipyard (planet-only)
and fleet_space_yard (ship-only) into a single component that works on
Ship, Planetary Complex, and Drop Pod vehicle types.
"""
import pytest
from game.simulation.components.component import create_component


class TestConsolidatedSpaceShipyard:
    """Verify the consolidated space_shipyard works for all vehicle types."""

    def test_space_shipyard_exists(self, fresh_registries):
        """space_shipyard component should exist in registry."""
        comp = create_component('space_shipyard', registries=fresh_registries)
        assert comp is not None

    def test_fleet_space_yard_removed(self, fresh_registries):
        """fleet_space_yard should no longer exist."""
        comp = fresh_registries.components.get('fleet_space_yard')
        assert comp is None

    def test_allowed_on_ship(self, fresh_registries):
        """space_shipyard should be allowed on Ship vehicle type."""
        comp = fresh_registries.components.get('space_shipyard')
        allowed = comp.data.get('allowed_vehicle_types', [])
        assert 'Ship' in allowed

    def test_allowed_on_planetary_complex(self, fresh_registries):
        """space_shipyard should be allowed on Planetary Complex vehicle type."""
        comp = fresh_registries.components.get('space_shipyard')
        allowed = comp.data.get('allowed_vehicle_types', [])
        assert 'Planetary Complex' in allowed

    def test_allowed_on_drop_pod(self, fresh_registries):
        """space_shipyard should be allowed on Drop Pod vehicle type."""
        comp = fresh_registries.components.get('space_shipyard')
        allowed = comp.data.get('allowed_vehicle_types', [])
        assert 'Drop Pod' in allowed

    def test_production_rates_30000(self, fresh_registries):
        """space_shipyard production rates should be 30000 per resource."""
        comp = create_component('space_shipyard', registries=fresh_registries)
        ability = comp.get_ability('SpaceShipyard')
        assert ability is not None
        for resource in ['metals', 'organics', 'radioactives', 'vapors', 'exotics']:
            assert ability.production_rates.get(resource) == 30000, (
                f"{resource} rate should be 30000"
            )

    def test_mass_is_600(self, fresh_registries):
        """Consolidated component should use 600kg mass."""
        comp = create_component('space_shipyard', registries=fresh_registries)
        assert comp.base_mass == 600

    def test_hp_is_800(self, fresh_registries):
        """Consolidated component should use 800hp."""
        comp = create_component('space_shipyard', registries=fresh_registries)
        assert comp.base_max_hp == 800
