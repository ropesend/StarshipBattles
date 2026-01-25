import pytest
import pygame
from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components import load_components, LayerType
from game.core.registry import RegistryManager
from game.simulation.systems.battle_engine import BattleEngine
from game.core.constants import AttackType
from game.ai import StrategyManager
from tests.fixtures.paths import get_unit_test_data_dir


@pytest.fixture(autouse=True)
def setup_game_data():
    """Initialize game data before each test."""
    initialize_ship_data()
    load_components()
    pygame.init()
    manager = StrategyManager.instance()
    manager.load_data(
         str(get_unit_test_data_dir()),
         targeting_file="test_targeting_policies.json",
         movement_file="test_movement_policies.json",
         strategy_file="test_combat_strategies.json"
    )
    manager._loaded = True


class TestFighterLaunch:

    def test_hangar_initialization(self):
        """Test Hangar component loads correctly."""
        hangar = RegistryManager.instance().components.get("fighter_launch_bay")
        assert hangar is not None
        assert hangar.type_str == "Hangar"

        # Verify ability attributes instead of legacy component attributes
        vl = hangar.get_ability('VehicleLaunch')
        assert vl is not None
        assert vl.data.get('max_launch_mass', 0) == 50
        assert vl.cycle_time == 5.0

    def test_launch_logic(self):
        """Test launching mechanism on a ship."""
        ship = Ship("Carrier", 0, 0, (255, 0, 0), ship_class="Cruiser")
        comps = RegistryManager.instance().components
        hangar = comps["fighter_launch_bay"].clone()
        # Add Bridge to prevent derelict status
        bridge = comps["bridge"].clone()
        bridge.abilities.pop("CrewRequired", None)
        ship.add_component(bridge, LayerType.CORE)
        bridge.current_hp = bridge.max_hp # Fix 0 HP initialization due to formula

        # Add Engine to prevent derelict status (Thrust > 0)
        ship_engine = RegistryManager.instance().components["standard_engine"].clone()
        ship.add_component(ship_engine, LayerType.INNER)

        # Remove crew requirement for test
        hangar.abilities.pop("CrewRequired", None)

        if not ship.add_component(hangar, LayerType.INNER):
            pass

        ship.recalculate_stats()

        # Ensure active
        assert ship.is_alive, f"Ship should be alive. HP: {ship.hp}/{ship.max_hp}"
        assert hangar.is_active, f"Hangar should be active. HP: {hangar.current_hp}/{hangar.max_hp}"

        vl = hangar.get_ability('VehicleLaunch')
        assert vl is not None
        assert vl.cooldown <= 0

        # Simulate Combat
        ship.current_target = Ship("Enemy", 1000, 0, (0, 0, 255))

        # Fire weapons (triggers launch)
        attacks = ship.fire_weapons()

        # Check if launch event occurred
        launch_events = [a for a in attacks if isinstance(a, dict) and a.get('type') == AttackType.LAUNCH]
        assert len(launch_events) == 1

        # Check cooldown on ABILITY
        assert vl.cooldown > 0
        assert vl.cooldown == pytest.approx(vl.cycle_time)

    def test_battle_engine_launch_processing(self):
        """Test BattleEngine processes launch events and creates ships."""
        engine = BattleEngine()

        carrier = Ship("Carrier", 0, 0, (255, 0, 0), team_id=0, ship_class="Cruiser")

        # Add Bridge
        bridge = RegistryManager.instance().components["bridge"].clone()
        bridge.abilities.pop("CrewRequired", None)
        carrier.add_component(bridge, LayerType.CORE)
        bridge.current_hp = bridge.max_hp # Fix 0 HP initialization


        # Add Engine
        comps = RegistryManager.instance().components
        ship_engine = comps["standard_engine"].clone()
        carrier.add_component(ship_engine, LayerType.INNER)

        hangar = comps["fighter_launch_bay"].clone()
        # Remove crew requirement for test
        hangar.abilities.pop("CrewRequired", None)

        carrier.add_component(hangar, LayerType.INNER)
        carrier.recalculate_stats()

        enemy = Ship("Enemy", 1000, 0, (0, 0, 255), team_id=1)

        engine.start([carrier], [enemy])

        # Assert initial state
        assert len(engine.ships) == 2

        # Force a launch event manually (or run update loop)
        engine.update()

        # Check carrier target
        if not carrier.current_target:
            carrier.current_target = enemy # Force target

        # Run another tick to fire
        engine.update()

        # We expect 3 ships now
        assert len(engine.ships) == 3
        new_ship = engine.ships[-1]
        assert "Wing" in new_ship.name
        assert new_ship.team_id == 0
        assert new_ship.ship_class == "Fighter (Small)"

    def test_stats_aggregation(self):
        """Test ShipStatsCalculator aggregates Hangar stats."""
        ship = Ship("Carrier", 0, 0, (255, 0, 0), ship_class="Cruiser")
        comps = RegistryManager.instance().components
        hangar = comps["fighter_launch_bay"].clone()

        # Add Bridge & Engine for validity (optional for stats but good practice)
        bridge = comps["bridge"].clone()
        bridge.abilities.pop("CrewRequired", None)
        ship.add_component(bridge, LayerType.CORE)
        engine = comps["standard_engine"].clone()
        ship.add_component(engine, LayerType.INNER)
        ship.add_component(hangar, LayerType.INNER)

        # Remove crew requirement for test coverage of stats
        # Must modify data because recalculate_stats reloads abilities from data!
        if 'CrewRequired' in hangar.data['abilities']:
            del hangar.data['abilities']['CrewRequired']

        ship.recalculate_stats()

        # Verify stats
        assert getattr(ship, 'fighter_capacity', 0) == 50 # Updated to 50 based on user edit

        # New Stats
        assert getattr(ship, 'fighters_per_wave', 0) == 1
        assert getattr(ship, 'fighter_size_cap', 0) == 50
        assert getattr(ship, 'launch_cycle', 0) == 5.0

    def test_fighter_launch_speed_uses_config(self):
        """Test launched fighters receive BattleConfig.FIGHTER_LAUNCH_SPEED velocity boost."""
        from game.core.config import BattleConfig
        from game.core.math import Vector2

        engine = BattleEngine()

        # Create stationary carrier at origin facing right (angle=0)
        carrier = Ship("Carrier", 0, 0, (255, 0, 0), team_id=0, ship_class="Cruiser")
        carrier.velocity = Vector2(0, 0)
        carrier.angle = 0  # Facing right

        # Add Bridge
        comps = RegistryManager.instance().components
        bridge = comps["bridge"].clone()
        bridge.abilities.pop("CrewRequired", None)
        carrier.add_component(bridge, LayerType.CORE)
        bridge.current_hp = bridge.max_hp

        # Add Engine
        ship_engine = comps["standard_engine"].clone()
        carrier.add_component(ship_engine, LayerType.INNER)

        # Add Hangar
        hangar = comps["fighter_launch_bay"].clone()
        hangar.abilities.pop("CrewRequired", None)
        carrier.add_component(hangar, LayerType.INNER)
        carrier.recalculate_stats()

        enemy = Ship("Enemy", 1000, 0, (0, 0, 255), team_id=1)

        engine.start([carrier], [enemy])

        # Run updates until fighter is launched
        for _ in range(3):
            carrier.current_target = enemy
            engine.update()
            if len(engine.ships) > 2:
                break

        # Verify fighter was created
        assert len(engine.ships) == 3, "Fighter should have been launched"
        fighter = engine.ships[-1]

        # Fighter velocity should be approximately FIGHTER_LAUNCH_SPEED in the forward direction
        # Since carrier is at origin, stationary, facing right (angle=0),
        # the launch direction is (1, 0) and velocity should be (100, 0)
        expected_speed = BattleConfig.FIGHTER_LAUNCH_SPEED
        assert abs(fighter.velocity.x) == pytest.approx(expected_speed, abs=5), \
            f"Fighter X velocity should be ~{expected_speed}, got {fighter.velocity.x}"
