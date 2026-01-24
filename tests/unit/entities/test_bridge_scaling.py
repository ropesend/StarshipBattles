import pytest
import math

from game.simulation.components.component import Component, load_components
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_data_dir


class MockShip:
    def __init__(self, max_mass):
        self.max_mass_budget = max_mass


@pytest.fixture
def bridge_def():
    """Load components and return bridge definition."""
    load_components(str(get_data_dir() / "components.json"))
    bridge = RegistryManager.instance().components.get("bridge")
    yield bridge
    # Cleanup is optional here since tests don't need strict isolation


class TestBridgeScaling:
    def test_bridge_scaling_1000(self, bridge_def):
        # Base case: 1000 mass
        # Sqrt(1) = 1
        # Mass = 50 * 1 = 50
        # HP = 200 * 1 = 200
        # Crew = ceil(5 * 1) = 5

        comp = bridge_def.clone()
        ship = MockShip(1000)
        comp.ship = ship

        comp.recalculate_stats()

        assert comp.mass == pytest.approx(50.0)
        assert comp.max_hp == 200
        assert comp.abilities['CrewRequired'] == 5

    def test_bridge_scaling_4000(self, bridge_def):
        # 4000 mass -> scale = sqrt(4) = 2
        # Mass = 50 * 2 = 100
        # HP = 200 * 2 = 400
        # Crew = ceil(5 * 2) = 10

        comp = bridge_def.clone()
        ship = MockShip(4000)
        comp.ship = ship

        comp.recalculate_stats()

        assert comp.mass == pytest.approx(100.0)
        assert comp.max_hp == 400
        assert comp.abilities['CrewRequired'] == 10

    def test_bridge_scaling_odd(self, bridge_def):
        # 2000 mass -> scale = sqrt(2) = 1.4142...
        # Mass = 50 * 1.414 = 70.71...
        # HP = 200 * 1.414 = 282.84... -> int(282)
        # Crew = ceil(5 * 1.414) = ceil(7.07) = 8

        scale = math.sqrt(2000 / 1000)

        comp = bridge_def.clone()
        ship = MockShip(2000)
        comp.ship = ship

        comp.recalculate_stats()

        assert comp.mass == pytest.approx(50 * scale)
        assert comp.max_hp == int(200 * scale)
        assert comp.abilities['CrewRequired'] == math.ceil(5 * scale)
        assert comp.abilities['CrewRequired'] == 8
