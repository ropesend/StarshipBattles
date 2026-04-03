"""Tests for QualityEngine — per-turn resource quality improvement."""
import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Any

from game.strategy.engine.quality_engine import QualityEngine


@dataclass
class MockFacility:
    design_data: Dict[str, Any]
    is_operational: bool = True


@dataclass
class MockPlanet:
    name: str = "Test"
    deposits: Dict[str, dict] = field(default_factory=dict)
    facilities: List = field(default_factory=list)


@dataclass
class MockEmpire:
    id: int = 0
    colonies: List = field(default_factory=list)


def _make_quality_facility(resource_type, rate=0.1):
    return MockFacility(design_data={
        "layers": {"CORE": [
            {"id": f"quality_improver_{resource_type}",
             "abilities": {"QualityImprovement": {
                 "resource_type": resource_type,
                 "improvement_rate": rate
             }}}
        ]}
    })


class TestQualityEngine:

    def test_improves_quality_by_rate(self):
        """Quality should increase by improvement_rate per turn."""
        planet = MockPlanet(
            deposits={"metals": {"quantity": 5000, "quality": 50.0}},
            facilities=[_make_quality_facility("metals", 0.1)]
        )
        empire = MockEmpire(colonies=[planet])
        engine = QualityEngine()

        engine.process_quality_improvement([empire])

        assert planet.deposits["metals"]["quality"] == pytest.approx(50.1)

    def test_caps_at_100(self):
        """Quality should not exceed 100."""
        planet = MockPlanet(
            deposits={"metals": {"quantity": 5000, "quality": 99.95}},
            facilities=[_make_quality_facility("metals", 0.1)]
        )
        empire = MockEmpire(colonies=[planet])
        engine = QualityEngine()

        engine.process_quality_improvement([empire])

        assert planet.deposits["metals"]["quality"] == 100.0

    def test_resource_specific(self):
        """Only the target resource should be affected."""
        planet = MockPlanet(
            deposits={
                "metals": {"quantity": 5000, "quality": 50.0},
                "organics": {"quantity": 3000, "quality": 40.0},
            },
            facilities=[_make_quality_facility("metals", 0.1)]
        )
        empire = MockEmpire(colonies=[planet])
        engine = QualityEngine()

        engine.process_quality_improvement([empire])

        assert planet.deposits["metals"]["quality"] == pytest.approx(50.1)
        assert planet.deposits["organics"]["quality"] == pytest.approx(40.0)

    def test_multiple_facilities_stack(self):
        """Multiple facilities for same resource should stack additively."""
        planet = MockPlanet(
            deposits={"metals": {"quantity": 5000, "quality": 50.0}},
            facilities=[
                _make_quality_facility("metals", 0.1),
                _make_quality_facility("metals", 0.1),
            ]
        )
        empire = MockEmpire(colonies=[planet])
        engine = QualityEngine()

        engine.process_quality_improvement([empire])

        assert planet.deposits["metals"]["quality"] == pytest.approx(50.2)

    def test_skips_nonoperational_facility(self):
        """Non-operational facilities should not contribute."""
        fac = _make_quality_facility("metals", 0.1)
        fac.is_operational = False
        planet = MockPlanet(
            deposits={"metals": {"quantity": 5000, "quality": 50.0}},
            facilities=[fac]
        )
        empire = MockEmpire(colonies=[planet])
        engine = QualityEngine()

        engine.process_quality_improvement([empire])

        assert planet.deposits["metals"]["quality"] == pytest.approx(50.0)

    def test_skips_missing_resource(self):
        """Should not crash if resource not in deposits."""
        planet = MockPlanet(
            deposits={"organics": {"quantity": 3000, "quality": 40.0}},
            facilities=[_make_quality_facility("metals", 0.1)]
        )
        empire = MockEmpire(colonies=[planet])
        engine = QualityEngine()

        engine.process_quality_improvement([empire])
        # No crash, organics unchanged
        assert planet.deposits["organics"]["quality"] == pytest.approx(40.0)
