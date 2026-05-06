"""Tests for WaterEngine — per-turn water level modification."""
import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from game.strategy.engine.water_engine import WaterEngine


@dataclass
class MockFacility:
    design_data: Dict[str, Any]
    is_operational: bool = True


@dataclass
class MockPlanet:
    name: str = "Test"
    surface_water: float = 0.3
    water_target: Optional[float] = None
    facilities: List = field(default_factory=list)


@dataclass
class MockEmpire:
    id: int = 0
    colonies: List = field(default_factory=list)


def _make_water_facility(rate=0.005):
    return MockFacility(design_data={
        "layers": {"CORE": [
            {"id": "water_modifier",
             "abilities": {"WaterModifier": {
                 "modification_rate": rate
             }}}
        ]}
    })


def _make_registry_water_facility(component_id="registry_water_modifier"):
    return MockFacility(design_data={
        "layers": {"CORE": [
            {"id": component_id}
        ]}
    })


class TestWaterEngine:

    def test_no_target_no_change(self):
        """No water_target means no modification."""
        planet = MockPlanet(
            surface_water=0.3,
            water_target=None,
            facilities=[_make_water_facility()]
        )
        empire = MockEmpire(colonies=[planet])
        engine = WaterEngine()

        engine.process_water_modification([empire])

        assert planet.surface_water == pytest.approx(0.3)

    def test_moves_toward_target(self):
        """Water level should move toward target."""
        planet = MockPlanet(
            surface_water=0.3,
            water_target=0.5,
            facilities=[_make_water_facility(0.01)]
        )
        empire = MockEmpire(colonies=[planet])
        engine = WaterEngine()

        engine.process_water_modification([empire])

        assert planet.surface_water > 0.3

    def test_does_not_overshoot(self):
        """Should not overshoot the target value."""
        planet = MockPlanet(
            surface_water=0.49,
            water_target=0.50,
            facilities=[_make_water_facility(0.1)]  # Rate exceeds remaining delta
        )
        empire = MockEmpire(colonies=[planet])
        engine = WaterEngine()

        engine.process_water_modification([empire])

        assert planet.surface_water == pytest.approx(0.50)

    def test_can_reduce_water(self):
        """Should reduce water level toward lower target."""
        planet = MockPlanet(
            surface_water=0.8,
            water_target=0.5,
            facilities=[_make_water_facility(0.01)]
        )
        empire = MockEmpire(colonies=[planet])
        engine = WaterEngine()

        engine.process_water_modification([empire])

        assert planet.surface_water < 0.8

    def test_clamps_to_zero(self):
        """Water level should not go below 0.0."""
        planet = MockPlanet(
            surface_water=0.001,
            water_target=0.0,
            facilities=[_make_water_facility(0.1)]
        )
        empire = MockEmpire(colonies=[planet])
        engine = WaterEngine()

        engine.process_water_modification([empire])

        assert planet.surface_water >= 0.0

    def test_clamps_to_one(self):
        """Water level should not exceed 1.0."""
        planet = MockPlanet(
            surface_water=0.999,
            water_target=1.0,
            facilities=[_make_water_facility(0.1)]
        )
        empire = MockEmpire(colonies=[planet])
        engine = WaterEngine()

        engine.process_water_modification([empire])

        assert planet.surface_water <= 1.0

    def test_multiple_facilities_stack(self):
        """Multiple facilities should stack their rates."""
        planet_single = MockPlanet(
            name="Single",
            surface_water=0.3,
            water_target=0.8,
            facilities=[_make_water_facility(0.01)]
        )
        planet_double = MockPlanet(
            name="Double",
            surface_water=0.3,
            water_target=0.8,
            facilities=[_make_water_facility(0.01), _make_water_facility(0.01)]
        )

        engine = WaterEngine()
        engine.process_water_modification([MockEmpire(colonies=[planet_single])])
        engine.process_water_modification([MockEmpire(colonies=[planet_double])])

        single_delta = planet_single.surface_water - 0.3
        double_delta = planet_double.surface_water - 0.3
        assert double_delta == pytest.approx(single_delta * 2)

    def test_list_form_water_modifier_entries_stack(self):
        """List-valued WaterModifier entries should all contribute."""
        facility = MockFacility(design_data={
            "layers": {"CORE": [
                {"id": "water_modifier",
                 "abilities": {"WaterModifier": [
                     {"modification_rate": 0.01},
                     {"modification_rate": 0.02},
                 ]}}
            ]}
        })
        planet = MockPlanet(
            surface_water=0.3,
            water_target=0.8,
            facilities=[facility],
        )
        empire = MockEmpire(colonies=[planet])
        engine = WaterEngine()

        engine.process_water_modification([empire])

        assert planet.surface_water == pytest.approx(0.33)

    def test_registry_defined_water_modifier_uses_injected_registries(
        self, fresh_registries
    ):
        """Components without inline abilities should resolve through DI."""
        fresh_registries.components["registry_water_modifier"] = {
            "abilities": {
                "WaterModifier": {"modification_rate": 0.025}
            }
        }
        planet = MockPlanet(
            surface_water=0.3,
            water_target=0.8,
            facilities=[_make_registry_water_facility()],
        )
        empire = MockEmpire(colonies=[planet])
        engine = WaterEngine(registries=fresh_registries)

        engine.process_water_modification([empire])

        assert planet.surface_water == pytest.approx(0.325)

    def test_malformed_water_modifier_data_does_not_change_water(self):
        """Malformed WaterModifier data (scalar) contributes no rate.

        PROJ-375: after consolidating the extract→iterate logic into
        component_inspector.iter_facility_ability_entries, scalar payloads are
        wrapped as {"value": x} but lack 'modification_rate' so they
        contribute 0 — leaving surface_water unchanged.
        """
        bad_facility = MockFacility(design_data={
            "layers": {"CORE": [
                {"id": "bad_water_modifier",
                 "abilities": {"WaterModifier": True}}
            ]}
        })
        planet = MockPlanet(
            surface_water=0.3,
            water_target=0.5,
            facilities=[bad_facility],
        )
        empire = MockEmpire(colonies=[planet])
        engine = WaterEngine()

        engine.process_water_modification([empire])

        assert planet.surface_water == pytest.approx(0.3)

    def test_skips_nonoperational_facility(self):
        """Non-operational facilities should not contribute."""
        facility = _make_water_facility(0.01)
        facility.is_operational = False

        planet = MockPlanet(
            surface_water=0.3,
            water_target=0.5,
            facilities=[facility]
        )
        empire = MockEmpire(colonies=[planet])
        engine = WaterEngine()

        engine.process_water_modification([empire])

        assert planet.surface_water == pytest.approx(0.3)

    def test_no_facility_no_change(self):
        """No WaterModifier facility means no change even with target."""
        planet = MockPlanet(
            surface_water=0.3,
            water_target=0.5,
            facilities=[]
        )
        empire = MockEmpire(colonies=[planet])
        engine = WaterEngine()

        engine.process_water_modification([empire])

        assert planet.surface_water == pytest.approx(0.3)
