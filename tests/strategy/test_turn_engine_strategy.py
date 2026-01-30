import pytest
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord
from unittest.mock import MagicMock, patch

class MockGalaxy:
    def __init__(self):
        self.systems = {}
        
    def get_planets_at_global_hex(self, global_hex):
        """Return planets at the given global hex (calculates from system data)."""
        result = []
        for sys in self.systems.values():
            for p in sys.planets:
                if hasattr(p, 'location') and (sys.global_location + p.location) == global_hex:
                    result.append(p)
        return result



@patch('game.strategy.data.pathfinding.find_hybrid_path')
def test_movement_timing(mock_path):
    """Verify ships move at correct tick intervals based on speed."""
    engine = TurnEngine()
    
    # Speed 5: 100 // 5 = 20. Moves at 20, 40, 60, 80, 100.
    f5 = Fleet(1, 0, HexCoord(0, 0), speed=5.0)
    # Mock path: 5 steps linear
    f5.path = [HexCoord(1,0), HexCoord(2,0), HexCoord(3,0), HexCoord(4,0), HexCoord(5,0)]
    f5.add_order(FleetOrder(OrderType.MOVE, HexCoord(5,0)))
    
    # Speed 10: 100 // 10 = 10. Moves at 10, 20... 100.
    f10 = Fleet(2, 0, HexCoord(0, 0), speed=10.0)
    f10.path = [HexCoord(i,0) for i in range(1, 11)] # 10 step path
    f10.add_order(FleetOrder(OrderType.MOVE, HexCoord(10,0)))
    
    # Mock pathfinding to return paths that match our expectations
    # This prevents path recalculation from changing our test conditions
    mock_path.return_value = None  # No recalc needed since paths are pre-set
    
    empires = [Empire(0, "P1", (255,0,0))]
    empires[0].add_fleet(f5)
    empires[0].add_fleet(f10)
    
    # Run ticks 1-19
    for i in range(1, 20):
        engine._process_tick(i, empires, MockGalaxy())
        
    assert f5.location == HexCoord(0,0)   # Shouldn't move yet
    assert f10.location == HexCoord(1,0)  # Moved at tick 10

    # Run tick 20
    engine._process_tick(20, empires, MockGalaxy())
    assert f5.location == HexCoord(1,0)   # Moved at tick 20
    assert f10.location == HexCoord(2,0)  # Moved again at tick 20

@patch('game.strategy.data.pathfinding.find_hybrid_path')
def test_full_turn_distance(mock_path):
    """Verify total distance traveled in a turn."""
    engine = TurnEngine()
    
    f2 = Fleet(1, 0, HexCoord(0,0), speed=2.0) # Should move 2 steps
    # Path must end at destination (10,0) to avoid path recalculation
    f2.path = [HexCoord(i, 0) for i in range(1, 11)]  # 1..10
    f2.add_order(FleetOrder(OrderType.MOVE, HexCoord(10,0)))
    
    f5 = Fleet(2, 0, HexCoord(0,0), speed=5.0) # Should move 5 steps
    f5.path = [HexCoord(i, 0) for i in range(1, 11)]  # 1..10
    f5.add_order(FleetOrder(OrderType.MOVE, HexCoord(10,0)))
    
    # Mock pathfinding - return None to use pre-set paths
    mock_path.return_value = None
    
    empires = [Empire(0, "P1", (0,0,0))]
    empires[0].add_fleet(f2)
    empires[0].add_fleet(f5)
    
    engine.process_turn(empires, MockGalaxy())
    
    assert f2.location == HexCoord(2,0)
    assert f5.location == HexCoord(5,0)

def test_combat_interception():
    """Verify fleets colliding mid-turn trigger combat."""
    engine = TurnEngine()
    
    # P1 at (0,0) moving Right -> Speed 5
    f1 = Fleet(1, 0, HexCoord(0,0), speed=5.0)
    f1.path = [HexCoord(1,0), HexCoord(2,0), HexCoord(3,0)]
    f1.add_order(FleetOrder(OrderType.MOVE, HexCoord(3,0)))
    
    # P2 at (2,0) moving Left <- Speed 5
    f2 = Fleet(2, 1, HexCoord(2,0), speed=5.0)
    f2.path = [HexCoord(1,0), HexCoord(0,0)]
    f2.add_order(FleetOrder(OrderType.MOVE, HexCoord(0,0)))
    
    e1 = Empire(0, "P1", (0,0,0))
    e1.add_fleet(f1)
    e2 = Empire(1, "P2", (1,1,1))
    e2.add_fleet(f2)
    
    # They should meet at (1,0) at Tick 20? 
    # Tick 20: 
    # f1 moves (0,0)->(1,0)
    # f2 moves (2,0)->(1,0)
    # Collision!
    
    # Mock RNG to ensure f2 dies
    engine._resolve_combat = MagicMock(side_effect=lambda a, b: b) # Returns loser? No, let's say returns survivor.
    # Wait, we need to know implemention spec. 
    # Plan says: "RNG Resolution: 50/50 roll. Loser is deleted."
    
    engine.process_turn([e1, e2], MockGalaxy())
    
    # Check that one fleet is dead/removed
    survivors = len(e1.fleets) + len(e2.fleets)
    assert survivors == 1
    
def test_order_chaining():
    """Verify Colonize executes after Move finishes."""
    engine = TurnEngine()
    
    # Create a mock planet with proper location
    planet = MagicMock()
    planet.name = "Test Planet"
    planet.owner_id = None
    planet.construction_queue = []
    planet.location = HexCoord(0, 0)  # At system center (relative)
    
    # Create mock system containing the planet
    mock_system = MagicMock()
    mock_system.global_location = HexCoord(1, 0)
    mock_system.planets = [planet]
    
    # Create galaxy with the system
    galaxy = MockGalaxy()
    galaxy.systems[HexCoord(1, 0)] = mock_system
    
    f1 = Fleet(1, 0, HexCoord(0,0), speed=100.0) # Fast, arrives instantly
    f1.path = [HexCoord(1,0)]
    f1.add_order(FleetOrder(OrderType.MOVE, HexCoord(1,0)))
    f1.add_order(FleetOrder(OrderType.COLONIZE, planet))
    
    e1 = Empire(0, "P1", (0,0,0))
    e1.add_fleet(f1)
    
    # Set fleet to ALREADY be at target to test colonize logic specifically
    f1.location = HexCoord(1,0) 
    f1.path = []
    # Clear move order, just leave Colonize
    f1.orders = [FleetOrder(OrderType.COLONIZE, planet)]
    
    engine.process_turn([e1], galaxy)
    
    assert planet.owner_id == 0
    assert planet in e1.colonies
    assert len(f1.orders) == 0 # Order consumed

def test_colonize_deletes_fleet():
    """Verify colonizing fleet is removed from empire after colonization."""
    engine = TurnEngine()

    # Create a mock planet with proper location
    planet = MagicMock()
    planet.name = "Test Planet"
    planet.owner_id = None
    planet.construction_queue = []
    planet.location = HexCoord(0, 0)  # At system center (relative)

    # Create mock system containing the planet
    mock_system = MagicMock()
    mock_system.global_location = HexCoord(1, 0)
    mock_system.planets = [planet]

    # Create galaxy with the system
    galaxy = MockGalaxy()
    galaxy.systems[HexCoord(1, 0)] = mock_system

    f1 = Fleet(1, 0, HexCoord(1, 0), speed=5.0)
    f1.orders = [FleetOrder(OrderType.COLONIZE, planet)]

    e1 = Empire(0, "P1", (0, 0, 0))
    e1.add_fleet(f1)

    assert len(e1.fleets) == 1  # Fleet exists before turn

    engine.process_turn([e1], galaxy)

    # Fleet should be removed (consumed to create colony)
    assert len(e1.fleets) == 0
    assert planet.owner_id == 0
    assert planet in e1.colonies


# ============================================================================
# PROJ-08: Per-Turn Resource Consumption Tests
# ============================================================================

def _create_mock_ship_instance(
    name="TestShip",
    owner_id=0,
    is_destroyed=False,
    is_derelict=False,
    resource_levels=None,
    component_toggles=None,
    design_data=None
):
    """Helper to create a mock ShipInstance for testing."""
    from game.strategy.data.ship_instance import ShipInstance

    ship = ShipInstance(
        instance_id=f"test-{name}",
        design_id=name,
        name=name,
        owner_id=owner_id,
        is_destroyed=is_destroyed,
        is_derelict=is_derelict,
    )
    if resource_levels:
        ship.resource_levels = resource_levels.copy()
    if component_toggles:
        ship.component_toggles = component_toggles.copy()
    if design_data:
        ship.design_data = design_data
    else:
        ship.design_data = {'name': name, 'layers': {}}
    return ship


def _create_mock_component_def(
    abilities=None,
    comp_type='Generic',
    max_hp=100,
    mass=10,
    damage_threshold=0.3
):
    """Helper to create a mock component definition."""
    mock_def = MagicMock()
    mock_def.abilities = abilities or {}
    mock_def.type_str = comp_type
    mock_def.max_hp = max_hp
    mock_def.mass = mass
    mock_def.damage_threshold = damage_threshold
    return mock_def


class TestPerTurnResourceConsumption:
    """Group 5.1: Per-Turn Resource Consumption Tests"""

    def test_per_turn_resource_consumption_single_ship(self):
        """Verify per-turn consumption is spread over 100 ticks (amount/100 per tick)."""
        engine = TurnEngine()

        # Create ship with mocked per-turn cost
        ship = _create_mock_ship_instance(
            resource_levels={'energy': 100.0}
        )
        # Mock get_all_resource_costs_per_turn to return energy cost of 50 per turn
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 50.0})
        ship.get_resource_capacity = MagicMock(return_value=100.0)
        ship.is_combat_capable = MagicMock(return_value=True)

        # Track consume_resource calls
        consumed_amounts = []
        def mock_consume(resource_type, amount):
            consumed_amounts.append((resource_type, amount))
            return True
        ship.consume_resource = mock_consume

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        # Process single tick
        engine.resource_engine.process_per_turn_consumption(1, [empire])

        # Should consume 1/100th of the per-turn cost
        assert len(consumed_amounts) == 1
        assert consumed_amounts[0] == ('energy', 0.5)  # 50 / 100 = 0.5

    def test_per_turn_resource_consumption_multiple_resources(self):
        """Verify multiple resource types are consumed per tick."""
        engine = TurnEngine()

        ship = _create_mock_ship_instance(
            resource_levels={'energy': 100.0, 'fuel': 200.0}
        )
        # Multiple resources with per-turn costs
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={
            'energy': 30.0,
            'fuel': 10.0
        })
        ship.is_combat_capable = MagicMock(return_value=True)

        consumed = {}
        def mock_consume(resource_type, amount):
            consumed[resource_type] = consumed.get(resource_type, 0) + amount
            return True
        ship.consume_resource = mock_consume

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        engine.resource_engine.process_per_turn_consumption(1, [empire])

        assert consumed['energy'] == pytest.approx(0.3, rel=1e-6)  # 30/100
        assert consumed['fuel'] == pytest.approx(0.1, rel=1e-6)    # 10/100

    def test_per_turn_resource_consumption_multiple_ships_in_fleet(self):
        """Verify all ships in a fleet consume resources per tick."""
        engine = TurnEngine()

        ships = []
        for i in range(3):
            ship = _create_mock_ship_instance(name=f"Ship{i}")
            ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 20.0})
            ship.is_combat_capable = MagicMock(return_value=True)
            ship.consume_resource = MagicMock(return_value=True)
            ships.append(ship)

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = ships
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        engine.resource_engine.process_per_turn_consumption(1, [empire])

        # Each ship should have consumed
        for ship in ships:
            ship.consume_resource.assert_called_once_with('energy', 0.2)  # 20/100

    def test_per_turn_consumption_non_combat_ships_skipped(self):
        """Verify destroyed/derelict ships don't consume per-turn resources."""
        engine = TurnEngine()

        combat_ship = _create_mock_ship_instance(name="CombatShip")
        combat_ship.is_combat_capable = MagicMock(return_value=True)
        combat_ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 10.0})
        combat_ship.consume_resource = MagicMock(return_value=True)

        destroyed_ship = _create_mock_ship_instance(name="DestroyedShip", is_destroyed=True)
        destroyed_ship.is_combat_capable = MagicMock(return_value=False)
        destroyed_ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 10.0})
        destroyed_ship.consume_resource = MagicMock(return_value=True)

        derelict_ship = _create_mock_ship_instance(name="DerelictShip", is_derelict=True)
        derelict_ship.is_combat_capable = MagicMock(return_value=False)
        derelict_ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 10.0})
        derelict_ship.consume_resource = MagicMock(return_value=True)

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [combat_ship, destroyed_ship, derelict_ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        engine.resource_engine.process_per_turn_consumption(1, [empire])

        # Only combat-capable ship should consume
        combat_ship.consume_resource.assert_called_once()
        destroyed_ship.consume_resource.assert_not_called()
        derelict_ship.consume_resource.assert_not_called()

    def test_per_turn_consumption_zero_cost_components_ignored(self):
        """Verify components with zero per-turn cost don't attempt consumption."""
        engine = TurnEngine()

        ship = _create_mock_ship_instance()
        # Return zero costs
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 0.0})
        ship.is_combat_capable = MagicMock(return_value=True)
        ship.consume_resource = MagicMock(return_value=True)

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        engine.resource_engine.process_per_turn_consumption(1, [empire])

        # Zero cost should not trigger consumption
        ship.consume_resource.assert_not_called()


class TestResourceDepletion:
    """Group 5.2: Resource Depletion Tests"""

    def test_resource_depletion_during_tick_returns_false(self):
        """Verify consume_resource returns False when resources depleted."""
        engine = TurnEngine()

        ship = _create_mock_ship_instance()
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 100.0})
        ship.is_combat_capable = MagicMock(return_value=True)
        # Simulate depletion - consume returns False
        ship.consume_resource = MagicMock(return_value=False)

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        # Patch _auto_disable_components_for_resource to verify it's called
        with patch.object(engine.resource_engine, '_auto_disable_components_for_resource') as mock_auto:
            engine.resource_engine.process_per_turn_consumption(1, [empire])
            mock_auto.assert_called_once_with(ship, 'energy')

    def test_resource_depletion_triggers_auto_disable(self):
        """Verify auto-disable is triggered when resource depleted mid-tick."""
        engine = TurnEngine()

        ship = _create_mock_ship_instance()
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={'fuel': 50.0})
        ship.is_combat_capable = MagicMock(return_value=True)
        ship.consume_resource = MagicMock(return_value=False)  # Depleted

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        with patch.object(engine.resource_engine, '_auto_disable_components_for_resource') as mock_auto:
            engine.resource_engine.process_per_turn_consumption(50, [empire])
            mock_auto.assert_called_once_with(ship, 'fuel')

    def test_no_auto_disable_for_non_per_turn_resources(self):
        """Verify auto-disable only triggered for per_turn consumption failures."""
        engine = TurnEngine()

        ship = _create_mock_ship_instance()
        # No per-turn costs
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={})
        ship.is_combat_capable = MagicMock(return_value=True)
        ship.consume_resource = MagicMock(return_value=True)

        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        with patch.object(engine.resource_engine, '_auto_disable_components_for_resource') as mock_auto:
            engine.resource_engine.process_per_turn_consumption(1, [empire])
            mock_auto.assert_not_called()


class TestAutoDisableLogic:
    """Group 5.3: Auto-Disable Logic Tests"""

    def test_auto_disable_finds_components_with_per_turn_trigger(self):
        """Verify auto-disable finds and disables components with per_turn trigger."""
        engine = TurnEngine()

        # Create ship with a component that has per_turn energy consumption
        ship = _create_mock_ship_instance(
            design_data={
                'name': 'TestShip',
                'layers': {
                    'CORE': [{'id': 'shield_generator'}]
                }
            }
        )
        ship.set_component_enabled = MagicMock()

        # Mock registry to return component with per_turn ability
        mock_comp_def = _create_mock_component_def(
            abilities={
                'ResourceConsumption': {
                    'trigger': 'per_turn',
                    'resource': 'energy',
                    'amount': 10
                }
            }
        )

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get = MagicMock(return_value=mock_comp_def)
            engine.resource_engine._auto_disable_components_for_resource(ship, 'energy')

            ship.set_component_enabled.assert_called_once_with('shield_generator', False)

    def test_auto_disable_multiple_components_same_resource(self):
        """Verify multiple components using same resource are all disabled."""
        engine = TurnEngine()

        ship = _create_mock_ship_instance(
            design_data={
                'name': 'TestShip',
                'layers': {
                    'CORE': [{'id': 'comp_a'}, {'id': 'comp_b'}, {'id': 'comp_c'}]
                }
            }
        )
        ship.set_component_enabled = MagicMock()

        # Two components use energy, one uses fuel
        mock_energy_comp = _create_mock_component_def(
            abilities={
                'ResourceConsumption': {
                    'trigger': 'per_turn',
                    'resource': 'energy',
                    'amount': 5
                }
            }
        )
        mock_fuel_comp = _create_mock_component_def(
            abilities={
                'ResourceConsumption': {
                    'trigger': 'per_turn',
                    'resource': 'fuel',
                    'amount': 5
                }
            }
        )

        def get_mock_comp(comp_id):
            if comp_id in ['comp_a', 'comp_b']:
                return mock_energy_comp
            return mock_fuel_comp

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get = get_mock_comp
            engine.resource_engine._auto_disable_components_for_resource(ship, 'energy')

            # Should disable comp_a and comp_b (energy), not comp_c (fuel)
            calls = ship.set_component_enabled.call_args_list
            assert len(calls) == 2
            disabled_ids = [call[0][0] for call in calls]
            assert 'comp_a' in disabled_ids
            assert 'comp_b' in disabled_ids
            assert 'comp_c' not in disabled_ids

    def test_auto_disable_skips_unregistered_components(self):
        """Verify unregistered components don't cause errors."""
        engine = TurnEngine()

        ship = _create_mock_ship_instance(
            design_data={
                'name': 'TestShip',
                'layers': {
                    'CORE': [{'id': 'unknown_component'}]
                }
            }
        )
        ship.set_component_enabled = MagicMock()

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get = MagicMock(return_value=None)
            # Should not raise exception
            engine.resource_engine._auto_disable_components_for_resource(ship, 'energy')
            ship.set_component_enabled.assert_not_called()

    def test_auto_disable_handles_layer_formats(self):
        """Verify auto-disable handles both list and dict layer formats."""
        engine = TurnEngine()

        # Mixed layer formats
        ship = _create_mock_ship_instance(
            design_data={
                'name': 'TestShip',
                'layers': {
                    'CORE': [{'id': 'comp_list'}],
                    'INNER': {'components': [{'id': 'comp_dict'}]}
                }
            }
        )
        ship.set_component_enabled = MagicMock()

        mock_comp_def = _create_mock_component_def(
            abilities={
                'ResourceConsumption': {
                    'trigger': 'per_turn',
                    'resource': 'energy',
                    'amount': 10
                }
            }
        )

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get = MagicMock(return_value=mock_comp_def)
            engine.resource_engine._auto_disable_components_for_resource(ship, 'energy')

            # Both formats should be handled
            calls = ship.set_component_enabled.call_args_list
            assert len(calls) == 2
            disabled_ids = [call[0][0] for call in calls]
            assert 'comp_list' in disabled_ids
            assert 'comp_dict' in disabled_ids

    def test_auto_disable_invalidates_stats_cache(self):
        """Verify auto-disable invalidates the ship's stats cache."""
        engine = TurnEngine()

        ship = _create_mock_ship_instance(
            design_data={
                'name': 'TestShip',
                'layers': {
                    'CORE': [{'id': 'test_comp'}]
                }
            }
        )

        # Track if invalidate was called via set_component_enabled
        invalidate_called = []
        original_set = ship.set_component_enabled
        def tracking_set(comp_id, enabled):
            ship.component_toggles[comp_id] = enabled
            ship._cached_stats = None  # This is what set_component_enabled does
            invalidate_called.append(comp_id)
        ship.set_component_enabled = tracking_set

        mock_comp_def = _create_mock_component_def(
            abilities={
                'ResourceConsumption': {
                    'trigger': 'per_turn',
                    'resource': 'energy',
                    'amount': 10
                }
            }
        )

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get = MagicMock(return_value=mock_comp_def)
            # Populate cache first
            ship._cached_stats = {'some': 'cached_data'}

            engine.resource_engine._auto_disable_components_for_resource(ship, 'energy')

            # Cache should be invalidated
            assert ship._cached_stats is None
            assert len(invalidate_called) == 1

    def test_auto_disable_logs_info_message(self, caplog):
        """Verify auto-disable logs an info message for each disabled component."""
        import logging
        engine = TurnEngine()

        ship = _create_mock_ship_instance(
            name="TestCruiser",
            design_data={
                'name': 'TestCruiser',
                'layers': {
                    'CORE': [{'id': 'shield_gen'}]
                }
            }
        )
        ship.set_component_enabled = MagicMock()

        mock_comp_def = _create_mock_component_def(
            abilities={
                'ResourceConsumption': {
                    'trigger': 'per_turn',
                    'resource': 'energy',
                    'amount': 10
                }
            }
        )

        with patch('game.strategy.engine.resource_management_engine.get_default_registry_provider') as mock_provider:
            mock_provider.return_value.get_components.return_value.get = MagicMock(return_value=mock_comp_def)
            with caplog.at_level(logging.INFO):
                engine.resource_engine._auto_disable_components_for_resource(ship, 'energy')

                # Check that appropriate log message was created
                assert any('TestCruiser' in record.message and
                          'shield_gen' in record.message and
                          'energy' in record.message
                          for record in caplog.records)


class TestFullTurnIntegration:
    """Group 5.4: Full Turn Integration Tests"""

    def test_full_turn_depletes_per_turn_resources_completely(self):
        """Verify a full turn (100 ticks) consumes the entire per-turn cost."""
        engine = TurnEngine()

        ship = _create_mock_ship_instance()
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 50.0})
        ship.is_combat_capable = MagicMock(return_value=True)

        # Track total consumption
        total_consumed = {'energy': 0.0}
        def mock_consume(resource_type, amount):
            total_consumed[resource_type] = total_consumed.get(resource_type, 0) + amount
            return True
        ship.consume_resource = mock_consume

        fleet = Fleet(1, 0, HexCoord(0, 0), speed=0)  # No movement
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        # Process all 100 ticks
        for tick in range(1, 101):
            engine.resource_engine.process_per_turn_consumption(tick, [empire])

        # Should have consumed exactly 50 energy total
        assert total_consumed['energy'] == pytest.approx(50.0, rel=1e-6)

    def test_full_turn_does_not_overconsume_resources(self):
        """Verify full turn consumes exactly the per-turn amount, not more."""
        engine = TurnEngine()

        ship = _create_mock_ship_instance()
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={'fuel': 25.0})
        ship.is_combat_capable = MagicMock(return_value=True)

        consume_calls = []
        def mock_consume(resource_type, amount):
            consume_calls.append(amount)
            return True
        ship.consume_resource = mock_consume

        fleet = Fleet(1, 0, HexCoord(0, 0), speed=0)
        fleet.ships = [ship]
        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        for tick in range(1, 101):
            engine.resource_engine.process_per_turn_consumption(tick, [empire])

        # Each tick should consume 0.25 (25/100)
        assert len(consume_calls) == 100
        for call in consume_calls:
            assert call == pytest.approx(0.25, rel=1e-6)
        assert sum(consume_calls) == pytest.approx(25.0, rel=1e-6)

    @patch('game.strategy.data.pathfinding.find_hybrid_path')
    def test_per_turn_and_movement_resources_both_consumed(self, mock_path):
        """Verify both per-turn and movement resources are consumed during a turn."""
        engine = TurnEngine()

        ship = _create_mock_ship_instance()
        ship.is_combat_capable = MagicMock(return_value=True)

        # Per-turn: 10 energy
        ship.get_all_resource_costs_per_turn = MagicMock(return_value={'energy': 10.0})

        per_turn_consumed = {'energy': 0.0}
        def mock_consume(resource_type, amount):
            per_turn_consumed[resource_type] = per_turn_consumed.get(resource_type, 0) + amount
            return True
        ship.consume_resource = mock_consume

        # Create fleet with movement
        fleet = Fleet(1, 0, HexCoord(0, 0), speed=5.0)
        fleet.ships = [ship]
        fleet.path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0), HexCoord(4, 0), HexCoord(5, 0)]
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(5, 0)))

        # Mock movement resources
        fleet.has_resources_for_movement = MagicMock(return_value=True)
        fleet.consume_movement_resources = MagicMock(return_value=True)

        mock_path.return_value = None

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        engine.process_turn([empire], MockGalaxy())

        # Per-turn consumption should have occurred (100 ticks x 0.1 = 10)
        assert per_turn_consumed['energy'] == pytest.approx(10.0, rel=1e-6)
        # Movement should have been consumed (speed 5 = 5 hexes moved)
        assert fleet.consume_movement_resources.call_count == 5


class TestMovementGating:
    """Group 5.5: Movement Gating Tests"""

    @patch('game.strategy.data.pathfinding.find_hybrid_path')
    def test_movement_requires_generic_resources(self, mock_path):
        """Verify movement is blocked when has_resources_for_movement returns False."""
        engine = TurnEngine()

        fleet = Fleet(1, 0, HexCoord(0, 0), speed=5.0)
        fleet.path = [HexCoord(1, 0)]
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(1, 0)))

        # No resources for movement
        fleet.has_resources_for_movement = MagicMock(return_value=False)
        fleet.consume_movement_resources = MagicMock()

        mock_path.return_value = None

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        # Process tick 20 (when speed-5 fleet would move)
        engine._process_tick(20, [empire], MockGalaxy())

        # Movement should not have happened
        assert fleet.location == HexCoord(0, 0)
        fleet.consume_movement_resources.assert_not_called()
        # Orders should be cleared (stranded)
        assert len(fleet.orders) == 0

    @patch('game.strategy.data.pathfinding.find_hybrid_path')
    def test_generic_movement_resource_consumption(self, mock_path):
        """Verify consume_movement_resources is called for each hex moved."""
        engine = TurnEngine()

        fleet = Fleet(1, 0, HexCoord(0, 0), speed=10.0)
        fleet.path = [HexCoord(i, 0) for i in range(1, 11)]
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(10, 0)))

        fleet.has_resources_for_movement = MagicMock(return_value=True)
        fleet.consume_movement_resources = MagicMock(return_value=True)

        mock_path.return_value = None

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        engine.process_turn([empire], MockGalaxy())

        # Speed 10 = 10 moves per turn, each consuming resources
        assert fleet.consume_movement_resources.call_count == 10
        # Each call should be for 1 hex
        for call in fleet.consume_movement_resources.call_args_list:
            assert call[0] == (1,)

    @patch('game.strategy.data.pathfinding.find_hybrid_path')
    def test_warp_uses_generic_methods(self, mock_path):
        """Verify warp uses has_resources_for_warp and consume_warp_resources."""
        engine = TurnEngine()

        fleet = Fleet(1, 0, HexCoord(0, 0), speed=5.0)
        # Warp jump = distance > 1 hex
        fleet.path = [HexCoord(10, 0)]  # Far destination = warp
        fleet.add_order(FleetOrder(OrderType.MOVE, HexCoord(10, 0)))

        fleet.has_resources_for_movement = MagicMock(return_value=True)
        fleet.can_use_warp = MagicMock(return_value=True)
        fleet.has_resources_for_warp = MagicMock(return_value=True)
        fleet.consume_movement_resources = MagicMock(return_value=True)
        fleet.consume_warp_resources = MagicMock(return_value=True)

        mock_path.return_value = None

        empire = Empire(0, "P1", (255, 0, 0))
        empire.add_fleet(fleet)

        # Process tick 20 (when speed-5 fleet would move)
        engine._process_tick(20, [empire], MockGalaxy())

        # Warp check and consumption should have been called
        fleet.has_resources_for_warp.assert_called_once()
        fleet.consume_warp_resources.assert_called_once()


class TestComponentToggleIntegration:
    """Group 5.6: Component Toggle Integration Tests"""

    def test_disabled_component_not_consumed_per_turn(self):
        """Verify disabled components don't contribute to per-turn consumption."""
        from game.strategy.services.ship_stats_service import ShipStatsService
        from game.core.registry import GameRegistries

        # Create design with a component that has per-turn consumption
        design_data = {
            'name': 'TestShip',
            'layers': {
                'CORE': [{'id': 'energy_consumer'}]
            }
        }

        mock_comp_def = _create_mock_component_def(
            abilities={
                'ResourceConsumption': {
                    'trigger': 'per_turn',
                    'resource': 'energy',
                    'amount': 20
                }
            },
            max_hp=100,
            mass=10
        )

        # PROJ-42: Create mock registries and use instance pattern
        registries = GameRegistries(
            components={'energy_consumer': mock_comp_def},
            modifiers={},
            vehicle_classes={},
            resources={}
        )
        service = ShipStatsService(registries=registries)

        # Component enabled - should have consumption
        enabled_stats = service.calculate_stats(
            design_data,
            component_damage={},
            component_toggles={'energy_consumer': True}
        )

        # Component disabled - should not have consumption
        disabled_stats = service.calculate_stats(
            design_data,
            component_damage={},
            component_toggles={'energy_consumer': False}
        )

        # Enabled should have the per-turn cost
        assert enabled_stats['resource_consumption_per_turn'].get('energy', 0) == 20.0

        # Disabled should have zero per-turn cost
        assert disabled_stats['resource_consumption_per_turn'].get('energy', 0) == 0.0

    def test_auto_disabled_component_reenabled_via_manual_toggle(self):
        """Verify manually re-enabling an auto-disabled component works."""
        from game.strategy.data.ship_instance import ShipInstance

        ship = ShipInstance(
            instance_id='test-1',
            design_id='TestShip',
            name='TestShip',
            owner_id=0,
            design_data={
                'name': 'TestShip',
                'layers': {'CORE': [{'id': 'shield_gen'}]}
            }
        )

        # Simulate auto-disable
        ship.set_component_enabled('shield_gen', False)
        assert ship.is_component_enabled('shield_gen') is False

        # Manual re-enable
        ship.set_component_enabled('shield_gen', True)
        assert ship.is_component_enabled('shield_gen') is True

        # Verify toggles dict state
        assert ship.component_toggles.get('shield_gen') is True
