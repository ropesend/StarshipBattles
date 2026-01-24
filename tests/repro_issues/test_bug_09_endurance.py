import math
import pytest
import pygame

from game.simulation.entities.ship import Ship, initialize_ship_data
from game.simulation.components.component import load_components, create_component, LayerType
from game.simulation.entities.ship_stats import ShipStatsCalculator
from game.core.constants import COMPONENTS_FILE
from tests.fixtures.paths import get_project_root


class TestBug09Endurance:

    @pytest.fixture(autouse=True)
    def setup(self):
        pygame.init()
        # Initialize shared data
        initialize_ship_data(str(get_project_root()))
        load_components(COMPONENTS_FILE)
        ship = Ship("EnduranceRepro", 0, 0, (255, 255, 255), ship_class="Cruiser")
        calculator = ShipStatsCalculator(ship.vehicle_classes if hasattr(ship, 'vehicle_classes') else {})
        print(f"[DEBUG] Ship Layers keys: {list(ship.layers.keys())}")
        yield ship, calculator

    def test_fuel_endurance_infinite(self, setup):
        """
        Reproduce BUG-09: Fuel Endurance is infinite despite having engine and fuel.
        """
        ship, calculator = setup
        # 1. Add Fuel Tank (Capacity)
        tank = create_component('fuel_tank')
        ship.add_component(tank, LayerType.INNER)

        # 2. Add Standard Engine (Consumption)
        engine = create_component('standard_engine')
        ship.add_component(engine, LayerType.OUTER)

        # 3. Recalculate Stats
        ship.recalculate_stats()

        # 4. Inpsect Results (Ship Stats)
        print(f"\n[DEBUG] Fuel Consumption (Ship Prop): {ship.fuel_consumption}")
        print(f"[DEBUG] Fuel Endurance (Ship Prop): {ship.fuel_endurance}")

        # 5. Inspect UI Logic (Stats Config)
        import ui.builder.stats_config as stats_config
        ui_consumption = stats_config.get_resource_consumption(ship, 'fuel')
        print(f"[DEBUG] Fuel Consumption (UI Getter): {ui_consumption}")

        calculated_endurance = ship.fuel_endurance
        formatted_str = stats_config.fmt_time(calculated_endurance)
        print(f"[DEBUG] Formatted String: {formatted_str}")

        # Test the getter used by the UI row
        # Row definition: getter=lambda s, n=r_name: get_resource_consumption(s, n)

        # ASSERTIONS
        # Consumption should be > 0 for a standard engine
        assert ship.fuel_consumption > 0, "Ship.fuel_consumption should be positive"
        assert ui_consumption > 0, "UI get_resource_consumption should be positive"

        # Endurance should be finite
        assert ship.fuel_endurance != float('inf'), "Fuel endurance should not be infinite"
        assert not math.isinf(ship.fuel_endurance), "Fuel endurance is infinite"

        # CRITICAL REPRO: exact string match for 'Infinite' when it should be finite
        # If this assertion PASSES, we have reproduced the bug (that it says Infinite when it shouldn't)
        # Wait, usually we write tests that FAIL when the bug is present.
        # But here I want to CONFIRM it says Infinite.

        # Correct logic for "Fail if bug is present":
        # assert formatted_str != "Infinite", "Endurance showed 'Infinite' but should be finite time"

        assert formatted_str != "Infinite", "Stats Panel shows 'Infinite' for finite fuel endurance"
