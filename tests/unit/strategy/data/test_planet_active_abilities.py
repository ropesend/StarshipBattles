"""Tests for Planet.active_abilities as a derived property.

The active_abilities property should be derived from facility.component_states,
not stored as a separate field. This ensures the source of truth is always
the per-component activation state.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)


def _make_facility(instance_id="fac-1", design_data=None, component_states=None):
    """Create a mock facility with activation state support."""
    facility = MagicMock()
    facility.instance_id = instance_id
    facility.name = f"Facility {instance_id}"
    facility.design_data = design_data or {"layers": {}}
    facility.is_operational = True
    facility.component_states = component_states or {}
    return facility


def _make_planet(facilities=None):
    """Create a minimal Planet for testing active_abilities derivation."""
    from game.strategy.data.planet import Planet
    from game.core.hex_math import HexCoord

    planet = Planet(
        name="TestPlanet",
        location=HexCoord(0, 0),
        orbit_distance=1,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515.0,
        surface_gravity=9.8,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.71,
        tectonic_activity=0.5,
        magnetic_field=1.0,
    )
    planet.facilities = facilities or []
    return planet


class TestActiveAbilitiesDerived:
    """active_abilities should be derived from facility component_states."""

    def test_no_facilities_returns_empty(self):
        """Planet with no facilities has no active abilities."""
        planet = _make_planet()
        assert planet.active_abilities == {}

    def test_no_active_components_returns_empty(self):
        """Planet with facilities but no active components returns empty."""
        facility = _make_facility(component_states={
            "OUTER:0:shield": ComponentActivationState(
                phase=ActivationPhase.INACTIVE,
            ).to_dict(),
        })
        planet = _make_planet(facilities=[facility])
        assert planet.active_abilities == {}

    def test_one_active_component(self):
        """Active component shows in active_abilities."""
        facility = _make_facility(component_states={
            "OUTER:0:shield": ComponentActivationState(
                phase=ActivationPhase.ACTIVE,
                ability_name="PlanetaryShield",
            ).to_dict(),
        })
        planet = _make_planet(facilities=[facility])
        assert planet.active_abilities == {"PlanetaryShield": True}

    def test_activating_component_not_active(self):
        """Component in ACTIVATING phase is NOT in active_abilities."""
        facility = _make_facility(component_states={
            "OUTER:0:shield": ComponentActivationState(
                phase=ActivationPhase.ACTIVATING,
                progress_ticks=50,
                required_ticks=250,
                ability_name="PlanetaryShield",
            ).to_dict(),
        })
        planet = _make_planet(facilities=[facility])
        assert planet.active_abilities.get("PlanetaryShield", False) is False

    def test_deactivating_component_not_active(self):
        """Component in DEACTIVATING phase is NOT in active_abilities."""
        facility = _make_facility(component_states={
            "OUTER:0:shield": ComponentActivationState(
                phase=ActivationPhase.DEACTIVATING,
                progress_ticks=10,
                required_ticks=150,
                ability_name="PlanetaryShield",
            ).to_dict(),
        })
        planet = _make_planet(facilities=[facility])
        assert planet.active_abilities.get("PlanetaryShield", False) is False

    def test_two_facilities_same_ability_both_active(self):
        """Two facilities with same ability name: both ACTIVE -> ability is True."""
        fac1 = _make_facility(instance_id="fac-1", component_states={
            "OUTER:0:geo_sector": ComponentActivationState(
                phase=ActivationPhase.ACTIVE,
                ability_name="GeologicStabilizer",
            ).to_dict(),
        })
        fac2 = _make_facility(instance_id="fac-2", component_states={
            "OUTER:0:geo_system": ComponentActivationState(
                phase=ActivationPhase.ACTIVE,
                ability_name="GeologicStabilizer",
            ).to_dict(),
        })
        planet = _make_planet(facilities=[fac1, fac2])
        assert planet.active_abilities["GeologicStabilizer"] is True

    def test_two_facilities_same_ability_one_active_one_not(self):
        """One active, one inactive: summary still shows True (ANY active)."""
        fac1 = _make_facility(instance_id="fac-1", component_states={
            "OUTER:0:geo_sector": ComponentActivationState(
                phase=ActivationPhase.ACTIVE,
                ability_name="GeologicStabilizer",
            ).to_dict(),
        })
        fac2 = _make_facility(instance_id="fac-2", component_states={
            "OUTER:0:geo_system": ComponentActivationState(
                phase=ActivationPhase.INACTIVE,
                ability_name="GeologicStabilizer",
            ).to_dict(),
        })
        planet = _make_planet(facilities=[fac1, fac2])
        assert planet.active_abilities["GeologicStabilizer"] is True

    def test_multiple_different_abilities(self):
        """Multiple different ability names from different components."""
        facility = _make_facility(component_states={
            "OUTER:0:shield": ComponentActivationState(
                phase=ActivationPhase.ACTIVE,
                ability_name="PlanetaryShield",
            ).to_dict(),
            "OUTER:1:stabilizer": ComponentActivationState(
                phase=ActivationPhase.ACTIVE,
                ability_name="GeologicStabilizer",
            ).to_dict(),
            "OUTER:2:stellar": ComponentActivationState(
                phase=ActivationPhase.INACTIVE,
                ability_name="StellarStabilizer",
            ).to_dict(),
        })
        planet = _make_planet(facilities=[facility])
        abilities = planet.active_abilities
        assert abilities["PlanetaryShield"] is True
        assert abilities["GeologicStabilizer"] is True
        assert "StellarStabilizer" not in abilities

    def test_derived_reflects_state_changes(self):
        """After changing component_states, active_abilities reflects the change."""
        facility = _make_facility(component_states={
            "OUTER:0:shield": ComponentActivationState(
                phase=ActivationPhase.INACTIVE,
                ability_name="PlanetaryShield",
            ).to_dict(),
        })
        planet = _make_planet(facilities=[facility])
        assert planet.active_abilities.get("PlanetaryShield", False) is False

        # Activate it
        facility.component_states["OUTER:0:shield"] = ComponentActivationState(
            phase=ActivationPhase.ACTIVE,
            ability_name="PlanetaryShield",
        ).to_dict()
        assert planet.active_abilities["PlanetaryShield"] is True

    def test_serialization_does_not_include_active_abilities(self):
        """Planet.to_dict() should NOT serialize active_abilities (it's derived)."""
        facility = _make_facility(component_states={
            "OUTER:0:shield": ComponentActivationState(
                phase=ActivationPhase.ACTIVE,
                ability_name="PlanetaryShield",
            ).to_dict(),
        })
        planet = _make_planet(facilities=[facility])
        data = planet.to_dict()
        assert "active_abilities" not in data

    def test_is_ability_active_helper(self):
        """is_ability_active() uses derived property."""
        facility = _make_facility(component_states={
            "OUTER:0:shield": ComponentActivationState(
                phase=ActivationPhase.ACTIVE,
                ability_name="PlanetaryShield",
            ).to_dict(),
        })
        planet = _make_planet(facilities=[facility])
        assert planet.is_ability_active("PlanetaryShield") is True
        assert planet.is_ability_active("GeologicStabilizer") is False
