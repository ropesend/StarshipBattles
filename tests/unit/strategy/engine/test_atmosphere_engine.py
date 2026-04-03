"""Tests for AtmosphereEngine — per-turn atmosphere modification."""
import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Any

from game.strategy.engine.atmosphere_engine import AtmosphereEngine


@dataclass
class MockFacility:
    design_data: Dict[str, Any]
    is_operational: bool = True


@dataclass
class MockPlanet:
    name: str = "Test"
    atmosphere: Dict[str, float] = field(default_factory=dict)
    atmosphere_target: Dict[str, float] = field(default_factory=dict)
    surface_pressure: float = 101325.0  # 1 atm in Pa
    surface_area: float = 5.1e14  # Earth m^2
    surface_gravity: float = 9.8  # m/s^2
    facilities: List = field(default_factory=list)


@dataclass
class MockEmpire:
    id: int = 0
    colonies: List = field(default_factory=list)


def _make_atmo_facility(rate=1e12):
    return MockFacility(design_data={
        "layers": {"CORE": [
            {"id": "atmosphere_modifier",
             "abilities": {"AtmosphereModifier": {
                 "modification_rate": rate
             }}}
        ]}
    })


class TestAtmosphereEngine:

    def test_no_target_no_change(self):
        """No atmosphere_target means no modification."""
        planet = MockPlanet(
            atmosphere={"N2": 79000.0, "O2": 21000.0},
            atmosphere_target={},
            facilities=[_make_atmo_facility()]
        )
        empire = MockEmpire(colonies=[planet])
        engine = AtmosphereEngine()

        engine.process_atmosphere([empire])

        assert planet.atmosphere["N2"] == pytest.approx(79000.0)
        assert planet.atmosphere["O2"] == pytest.approx(21000.0)

    def test_moves_toward_target(self):
        """Atmosphere should move toward target values."""
        planet = MockPlanet(
            atmosphere={"N2": 79000.0, "O2": 21000.0},
            atmosphere_target={"N2": 79000.0, "O2": 25000.0},  # Want more O2
            facilities=[_make_atmo_facility(1e15)]  # High rate for visible change
        )
        empire = MockEmpire(colonies=[planet])
        engine = AtmosphereEngine()

        engine.process_atmosphere([empire])

        # O2 should have increased toward 25000
        assert planet.atmosphere["O2"] > 21000.0

    def test_does_not_overshoot(self):
        """Should not overshoot the target value."""
        planet = MockPlanet(
            atmosphere={"O2": 20000.0},
            atmosphere_target={"O2": 20100.0},  # Very close to target
            facilities=[_make_atmo_facility(1e18)]  # Massive rate
        )
        empire = MockEmpire(colonies=[planet])
        engine = AtmosphereEngine()

        engine.process_atmosphere([empire])

        assert planet.atmosphere["O2"] == pytest.approx(20100.0)

    def test_small_planet_changes_faster(self):
        """Smaller planet (less atmosphere mass) should change faster."""
        # Small planet: low gravity, small area
        small = MockPlanet(
            name="Small",
            atmosphere={"O2": 10000.0},
            atmosphere_target={"O2": 20000.0},
            surface_pressure=10000.0,
            surface_area=1e12,  # Tiny
            surface_gravity=1.0,
            facilities=[_make_atmo_facility(1e12)]
        )
        # Large planet
        large = MockPlanet(
            name="Large",
            atmosphere={"O2": 10000.0},
            atmosphere_target={"O2": 20000.0},
            surface_pressure=10000.0,
            surface_area=1e16,  # Huge
            surface_gravity=25.0,
            facilities=[_make_atmo_facility(1e12)]
        )

        engine = AtmosphereEngine()
        engine.process_atmosphere([MockEmpire(colonies=[small])])
        engine.process_atmosphere([MockEmpire(colonies=[large])])

        # Small planet should have changed more
        small_delta = small.atmosphere["O2"] - 10000.0
        large_delta = large.atmosphere["O2"] - 10000.0
        assert small_delta > large_delta

    def test_multiple_facilities_stack(self):
        """Multiple facilities should increase total modification rate."""
        single = MockPlanet(
            name="Single",
            atmosphere={"O2": 10000.0},
            atmosphere_target={"O2": 20000.0},
            facilities=[_make_atmo_facility(1e14)]
        )
        double = MockPlanet(
            name="Double",
            atmosphere={"O2": 10000.0},
            atmosphere_target={"O2": 20000.0},
            facilities=[_make_atmo_facility(1e14), _make_atmo_facility(1e14)]
        )

        engine = AtmosphereEngine()
        engine.process_atmosphere([MockEmpire(colonies=[single])])
        engine.process_atmosphere([MockEmpire(colonies=[double])])

        single_delta = single.atmosphere["O2"] - 10000.0
        double_delta = double.atmosphere["O2"] - 10000.0
        assert double_delta == pytest.approx(single_delta * 2, rel=0.01)

    def test_can_reduce_gas(self):
        """Should be able to reduce a gas toward target."""
        planet = MockPlanet(
            atmosphere={"CO2": 50000.0},
            atmosphere_target={"CO2": 10000.0},
            facilities=[_make_atmo_facility(1e15)]
        )
        empire = MockEmpire(colonies=[planet])
        engine = AtmosphereEngine()

        engine.process_atmosphere([empire])

        assert planet.atmosphere["CO2"] < 50000.0

    def test_can_add_new_gas(self):
        """Should be able to add a gas that doesn't currently exist."""
        planet = MockPlanet(
            atmosphere={"N2": 80000.0},
            atmosphere_target={"N2": 80000.0, "O2": 20000.0},
            facilities=[_make_atmo_facility(1e15)]
        )
        empire = MockEmpire(colonies=[planet])
        engine = AtmosphereEngine()

        engine.process_atmosphere([empire])

        assert "O2" in planet.atmosphere
        assert planet.atmosphere["O2"] > 0

    def test_skips_nonoperational(self):
        """Non-operational facilities should not contribute."""
        fac = _make_atmo_facility(1e15)
        fac.is_operational = False
        planet = MockPlanet(
            atmosphere={"O2": 10000.0},
            atmosphere_target={"O2": 20000.0},
            facilities=[fac]
        )
        empire = MockEmpire(colonies=[planet])
        engine = AtmosphereEngine()

        engine.process_atmosphere([empire])

        assert planet.atmosphere["O2"] == pytest.approx(10000.0)
