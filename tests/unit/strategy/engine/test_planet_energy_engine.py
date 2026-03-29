"""Tests for PlanetEnergyEngine (PROJ-237)."""

import pytest
from unittest.mock import MagicMock
from game.strategy.engine.planet_energy_engine import PlanetEnergyEngine


def _make_facility(design_data, is_operational=True):
    """Create a mock PlanetaryFacility with design_data."""
    facility = MagicMock()
    facility.design_data = design_data
    facility.is_operational = is_operational
    facility.component_states = {}

    def set_component_active(comp_id, active):
        if comp_id not in facility.component_states:
            facility.component_states[comp_id] = {}
        facility.component_states[comp_id]['active'] = active

    facility.set_component_active = set_component_active
    return facility


def _make_planet(name="TestPlanet", facilities=None):
    """Create a mock Planet with energy fields."""
    planet = MagicMock()
    planet.name = name
    planet.facilities = facilities or []
    planet.energy = 0.0
    planet.energy_capacity = 0.0
    planet.energy_generation = 0.0
    planet.shield_active = False
    return planet


def _make_empire(colonies=None):
    """Create a mock Empire."""
    empire = MagicMock()
    empire.colonies = colonies or []
    return empire


def _generator_design(generation_rate=50.0):
    """Design data with a PlanetaryEnergyGenerator component."""
    return {
        "layers": {
            "OUTER": [
                {
                    "id": "planetary_energy_generator",
                    "abilities": {
                        "PlanetaryEnergyGenerator": {"generation_rate": generation_rate}
                    }
                }
            ]
        }
    }


def _battery_design(capacity=5000.0):
    """Design data with a PlanetaryEnergyStorage component."""
    return {
        "layers": {
            "OUTER": [
                {
                    "id": "planetary_energy_battery",
                    "abilities": {
                        "PlanetaryEnergyStorage": {"capacity": capacity}
                    }
                }
            ]
        }
    }


def _shield_design(energy_drain_rate=25.0):
    """Design data with a PlanetaryShield component."""
    return {
        "layers": {
            "OUTER": [
                {
                    "id": "planetary_shield_generator",
                    "abilities": {
                        "PlanetaryShield": {
                            "energy_drain_rate": energy_drain_rate,
                            "activation_time": 50,
                            "deactivation_time": 10
                        }
                    }
                }
            ]
        }
    }


class TestPlanetEnergyEngine:
    """Tests for PlanetEnergyEngine."""

    def test_energy_generation_increases_energy(self):
        """Generator produces energy each tick."""
        engine = PlanetEnergyEngine()
        facility = _make_facility(_generator_design(generation_rate=100.0))
        battery = _make_facility(_battery_design(capacity=5000.0))
        planet = _make_planet(facilities=[facility, battery])
        empire = _make_empire(colonies=[planet])

        engine.process_energy_tick(1, [empire])

        assert planet.energy == pytest.approx(1.0)  # 100.0 / 100
        assert planet.energy_capacity == 5000.0
        assert planet.energy_generation == 100.0

    def test_energy_capped_at_capacity(self):
        """Energy cannot exceed battery capacity."""
        engine = PlanetEnergyEngine()
        battery = _make_facility(_battery_design(capacity=10.0))
        generator = _make_facility(_generator_design(generation_rate=100.0))
        planet = _make_planet(facilities=[generator, battery])
        planet.energy = 9.5  # Close to capacity
        empire = _make_empire(colonies=[planet])

        engine.process_energy_tick(1, [empire])

        assert planet.energy == 10.0  # Clamped to capacity

    def test_no_generators_no_energy(self):
        """Planet with no generators stays at zero energy."""
        engine = PlanetEnergyEngine()
        battery = _make_facility(_battery_design(capacity=5000.0))
        planet = _make_planet(facilities=[battery])
        empire = _make_empire(colonies=[planet])

        engine.process_energy_tick(1, [empire])

        assert planet.energy == 0.0
        assert planet.energy_capacity == 5000.0

    def test_shield_drains_energy(self):
        """Active shield consumes energy each tick."""
        engine = PlanetEnergyEngine()
        battery = _make_facility(_battery_design(capacity=5000.0))
        shield = _make_facility(_shield_design(energy_drain_rate=50.0))
        planet = _make_planet(facilities=[battery, shield])
        planet.energy = 100.0
        planet.shield_active = True
        empire = _make_empire(colonies=[planet])

        engine.process_energy_tick(1, [empire])

        # Drain: 50.0 / 100 = 0.5 per tick
        assert planet.energy == pytest.approx(99.5)

    def test_shield_auto_deactivates_on_energy_depletion(self):
        """Shield auto-deactivates when energy runs out."""
        engine = PlanetEnergyEngine()
        battery = _make_facility(_battery_design(capacity=5000.0))
        shield = _make_facility(_shield_design(energy_drain_rate=50.0))
        planet = _make_planet(facilities=[battery, shield])
        planet.energy = 0.3  # Less than drain_per_tick (0.5)
        planet.shield_active = True
        empire = _make_empire(colonies=[planet])

        engine.process_energy_tick(1, [empire])

        assert planet.shield_active is False
        assert planet.energy == 0.0

    def test_shield_deactivates_when_facility_destroyed(self):
        """Shield deactivates if shield facility is removed."""
        engine = PlanetEnergyEngine()
        battery = _make_facility(_battery_design(capacity=5000.0))
        # No shield facility — but shield_active is True (facility was destroyed)
        planet = _make_planet(facilities=[battery])
        planet.energy = 100.0
        planet.shield_active = True
        empire = _make_empire(colonies=[planet])

        engine.process_energy_tick(1, [empire])

        assert planet.shield_active is False

    def test_multiple_generators_stack(self):
        """Multiple generators' rates are summed."""
        engine = PlanetEnergyEngine()
        gen1 = _make_facility(_generator_design(generation_rate=50.0))
        gen2 = _make_facility(_generator_design(generation_rate=30.0))
        battery = _make_facility(_battery_design(capacity=5000.0))
        planet = _make_planet(facilities=[gen1, gen2, battery])
        empire = _make_empire(colonies=[planet])

        engine.process_energy_tick(1, [empire])

        assert planet.energy_generation == 80.0
        assert planet.energy == pytest.approx(0.8)  # 80 / 100

    def test_multiple_batteries_stack(self):
        """Multiple batteries' capacities are summed."""
        engine = PlanetEnergyEngine()
        bat1 = _make_facility(_battery_design(capacity=3000.0))
        bat2 = _make_facility(_battery_design(capacity=2000.0))
        planet = _make_planet(facilities=[bat1, bat2])
        empire = _make_empire(colonies=[planet])

        engine.process_energy_tick(1, [empire])

        assert planet.energy_capacity == 5000.0

    def test_non_operational_facility_ignored(self):
        """Non-operational facilities don't contribute energy."""
        engine = PlanetEnergyEngine()
        gen = _make_facility(_generator_design(generation_rate=100.0), is_operational=False)
        battery = _make_facility(_battery_design(capacity=5000.0))
        planet = _make_planet(facilities=[gen, battery])
        empire = _make_empire(colonies=[planet])

        engine.process_energy_tick(1, [empire])

        assert planet.energy_generation == 0.0
        assert planet.energy == 0.0

    def test_no_batteries_means_zero_capacity(self):
        """Without batteries, energy capacity is zero and energy is clamped."""
        engine = PlanetEnergyEngine()
        gen = _make_facility(_generator_design(generation_rate=100.0))
        planet = _make_planet(facilities=[gen])
        planet.energy = 50.0  # Leftover from before batteries were destroyed
        empire = _make_empire(colonies=[planet])

        engine.process_energy_tick(1, [empire])

        assert planet.energy_capacity == 0.0
        assert planet.energy == 0.0  # Clamped to 0 (no storage)

    def test_generation_and_drain_balance(self):
        """Shield drains and generator produces in same tick."""
        engine = PlanetEnergyEngine()
        gen = _make_facility(_generator_design(generation_rate=50.0))
        battery = _make_facility(_battery_design(capacity=5000.0))
        shield = _make_facility(_shield_design(energy_drain_rate=50.0))
        planet = _make_planet(facilities=[gen, battery, shield])
        planet.energy = 100.0
        planet.shield_active = True
        empire = _make_empire(colonies=[planet])

        engine.process_energy_tick(1, [empire])

        # Generation: +0.5, Drain: -0.5, Net: 0
        assert planet.energy == pytest.approx(100.0)

    def test_empty_planet_no_error(self):
        """Planet with no facilities processes without error."""
        engine = PlanetEnergyEngine()
        planet = _make_planet(facilities=[])
        empire = _make_empire(colonies=[planet])

        engine.process_energy_tick(1, [empire])

        assert planet.energy == 0.0
        assert planet.energy_capacity == 0.0
