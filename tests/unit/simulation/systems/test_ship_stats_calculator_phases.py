"""
Tests for ShipStatsCalculator helper method extraction (Phase 8, Task 8.1).
Verify that the refactored calculate() method produces identical results.
"""
import pytest
import sys
from unittest.mock import MagicMock, patch


class TestShipStatsCalculatorPhases:
    """Test ShipStatsCalculator phase extraction."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Load test data once."""
        self.modules_patcher = patch.dict(sys.modules, {
            'pygame': MagicMock(),
            'pygame.mixer': MagicMock(),
            'pygame.font': MagicMock()
        })
        self.modules_patcher.start()

        from game.core.registry import RegistryManager
        from game.simulation.components.component import Component, load_components, load_modifiers
        from game.simulation.systems.stats import ShipStatsCalculator
        from game.core.constants import LayerType
        from game.simulation.systems.resource_manager import ResourceRegistry

        self.Component = Component
        self.ShipStatsCalculator = ShipStatsCalculator
        self.LayerType = LayerType
        self.ResourceRegistry = ResourceRegistry
        self.vehicle_classes = RegistryManager.instance().vehicle_classes
        self.RegistryManager = RegistryManager

        load_components()
        load_modifiers()

        yield

        self.modules_patcher.stop()
        RegistryManager.instance().clear()

    def _create_mock_ship(self, components, vehicle_type="Ship"):
        """Create a mock ship with the given components."""
        ship = MagicMock()
        ship.layers = {
            self.LayerType.CORE: {
                'components': components,
                'mass': 0,
                'max_mass_pct': 0.3
            }
        }
        ship.base_mass = 100
        ship.mass = 100
        ship.current_mass = 0
        ship.ship_class = "Corvette"
        ship.vehicle_type = vehicle_type
        ship.resources = self.ResourceRegistry()
        ship._resources_initialized = False
        ship._prev_max_fuel = 0
        ship._prev_max_ammo = 0
        ship._prev_max_energy = 0
        ship._prev_max_shields = 0
        ship.current_shields = 0
        ship.max_shields = 0
        ship.max_hp = 100
        ship.max_weapon_range = 500

        def get_all_components():
            result = []
            for layer_data in ship.layers.values():
                result.extend(layer_data['components'])
            return result

        def iter_components():
            for layer_type, layer_data in ship.layers.items():
                for comp in layer_data['components']:
                    yield layer_type, comp

        ship.get_all_components = get_all_components
        ship.iter_components = iter_components

        for c in components:
            c.ship = ship
            c.recalculate_stats()

        return ship

    def test_damage_check_phase_marks_damaged_components(self):
        """Verify Phase 1 correctly marks components as damaged at 50% HP threshold."""
        # Create component with low HP (below 50% threshold)
        comp_data = {
            'id': 'test_comp',
            'name': 'Test Component',
            'type': 'Electronics',
            'mass': 50,
            'hp': 100,  # max_hp = 100
            'abilities': {}
        }
        comp = self.Component(comp_data)
        comp.current_hp = 40  # 40% HP - below 50% threshold

        ship = self._create_mock_ship([comp])
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)

        # Component should be marked as damaged/inactive
        from game.simulation.components.component_constants import ComponentStatus
        assert comp.is_active == False
        assert comp.status == ComponentStatus.DAMAGED

    def test_damage_check_phase_keeps_healthy_components_active(self):
        """Verify Phase 1 keeps components above 50% HP active."""
        comp_data = {
            'id': 'test_comp',
            'name': 'Test Component',
            'type': 'Electronics',
            'mass': 50,
            'hp': 100,
            'abilities': {}
        }
        comp = self.Component(comp_data)
        comp.current_hp = 60  # 60% HP - above 50% threshold

        ship = self._create_mock_ship([comp])
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)

        from game.simulation.components.component_constants import ComponentStatus
        assert comp.is_active == True
        assert comp.status == ComponentStatus.ACTIVE

    def test_crew_allocation_phase_deactivates_uncrewed_components(self):
        """Verify Phase 2 deactivates components that don't have crew."""
        # Component requiring crew but no crew quarters
        weapon_data = {
            'id': 'test_weapon',
            'name': 'Test Weapon',
            'type': 'Weapon',
            'mass': 50,
            'hp': 50,
            'abilities': {
                'CrewRequired': 2,
                'WeaponAbility': {
                    'damage': 10,
                    'range': 500,
                    'reload_time': 1.0
                }
            }
        }
        weapon = self.Component(weapon_data)

        ship = self._create_mock_ship([weapon])
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)

        from game.simulation.components.component_constants import ComponentStatus
        assert weapon.is_active == False
        assert weapon.status == ComponentStatus.NO_CREW

    def test_crew_allocation_phase_activates_crewed_components(self):
        """Verify Phase 2 keeps components active when crew is available."""
        # Crew quarters providing crew
        quarters_data = {
            'id': 'test_quarters',
            'name': 'Test Quarters',
            'type': 'CrewQuarters',
            'mass': 30,
            'hp': 30,
            'abilities': {
                'CrewCapacity': 5,
                'LifeSupportCapacity': 10
            }
        }
        # Component requiring crew
        weapon_data = {
            'id': 'test_weapon',
            'name': 'Test Weapon',
            'type': 'Weapon',
            'mass': 50,
            'hp': 50,
            'abilities': {
                'CrewRequired': 2,
                'WeaponAbility': {
                    'damage': 10,
                    'range': 500,
                    'reload_time': 1.0
                }
            }
        }
        quarters = self.Component(quarters_data)
        weapon = self.Component(weapon_data)

        ship = self._create_mock_ship([quarters, weapon])
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)

        from game.simulation.components.component_constants import ComponentStatus
        assert weapon.is_active == True
        assert weapon.status == ComponentStatus.ACTIVE

    def test_satellite_ignores_crew_requirements(self):
        """Verify Satellites ignore crew requirements (Phase 2 exception)."""
        weapon_data = {
            'id': 'test_weapon',
            'name': 'Test Weapon',
            'type': 'Weapon',
            'mass': 50,
            'hp': 50,
            'abilities': {
                'CrewRequired': 2,
                'WeaponAbility': {
                    'damage': 10,
                    'range': 500,
                    'reload_time': 1.0
                }
            }
        }
        weapon = self.Component(weapon_data)

        ship = self._create_mock_ship([weapon], vehicle_type="Satellite")
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)

        from game.simulation.components.component_constants import ComponentStatus
        assert weapon.is_active == True
        assert weapon.status == ComponentStatus.ACTIVE

    def test_stats_aggregation_phase_sums_thrust(self):
        """Verify Phase 3 correctly aggregates thrust from engines."""
        engine1_data = {
            'id': 'engine1',
            'name': 'Engine 1',
            'type': 'Engine',
            'mass': 100,
            'hp': 50,
            'abilities': {
                'CombatPropulsion': {'value': 1000}
            }
        }
        engine2_data = {
            'id': 'engine2',
            'name': 'Engine 2',
            'type': 'Engine',
            'mass': 100,
            'hp': 50,
            'abilities': {
                'CombatPropulsion': {'value': 1500}
            }
        }
        engine1 = self.Component(engine1_data)
        engine2 = self.Component(engine2_data)

        ship = self._create_mock_ship([engine1, engine2])
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)

        assert ship.total_thrust == 2500

    def test_stats_aggregation_phase_sums_shields(self):
        """Verify Phase 3 correctly aggregates shield capacity."""
        shield1_data = {
            'id': 'shield1',
            'name': 'Shield 1',
            'type': 'Shield',
            'mass': 50,
            'hp': 30,
            'abilities': {
                'ShieldProjection': 300
            }
        }
        shield2_data = {
            'id': 'shield2',
            'name': 'Shield 2',
            'type': 'Shield',
            'mass': 50,
            'hp': 30,
            'abilities': {
                'ShieldProjection': 200
            }
        }
        shield1 = self.Component(shield1_data)
        shield2 = self.Component(shield2_data)

        ship = self._create_mock_ship([shield1, shield2])
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)

        assert ship.max_shields == 500.0

    def test_physics_limits_phase_calculates_acceleration(self):
        """Verify Phase 4 calculates physics-based acceleration."""
        engine_data = {
            'id': 'test_engine',
            'name': 'Test Engine',
            'type': 'Engine',
            'mass': 100,
            'hp': 50,
            'abilities': {
                'CombatPropulsion': {'value': 2000}
            }
        }
        engine = self.Component(engine_data)

        ship = self._create_mock_ship([engine])
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)

        # Verify acceleration was calculated (non-zero with thrust)
        assert ship.acceleration_rate > 0
        assert ship.max_speed > 0

    def test_combat_stats_phase_calculates_defense_score(self):
        """Verify Phase 5 calculates to-hit defense score."""
        engine_data = {
            'id': 'test_engine',
            'name': 'Test Engine',
            'type': 'Engine',
            'mass': 100,
            'hp': 50,
            'abilities': {
                'CombatPropulsion': {'value': 2000}
            }
        }
        thruster_data = {
            'id': 'test_thruster',
            'name': 'Test Thruster',
            'type': 'Thruster',
            'mass': 50,
            'hp': 30,
            'abilities': {
                'ManeuveringThruster': {'value': 90.0}
            }
        }
        engine = self.Component(engine_data)
        thruster = self.Component(thruster_data)

        ship = self._create_mock_ship([engine, thruster])
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)

        # Verify defense score exists and is a number
        assert hasattr(ship, 'total_defense_score')
        assert isinstance(ship.total_defense_score, (int, float))

    def test_calculate_orchestrates_all_phases(self):
        """Integration test: verify calculate() orchestrates all phases correctly."""
        # Complex ship with multiple component types
        engine_data = {
            'id': 'engine',
            'name': 'Engine',
            'type': 'Engine',
            'mass': 100,
            'hp': 50,
            'abilities': {
                'CombatPropulsion': {'value': 1500}
            }
        }
        shield_data = {
            'id': 'shield',
            'name': 'Shield',
            'type': 'Shield',
            'mass': 50,
            'hp': 30,
            'abilities': {
                'ShieldProjection': 400
            }
        }
        quarters_data = {
            'id': 'quarters',
            'name': 'Quarters',
            'type': 'CrewQuarters',
            'mass': 30,
            'hp': 30,
            'abilities': {
                'CrewCapacity': 10,
                'LifeSupportCapacity': 15
            }
        }

        engine = self.Component(engine_data)
        shield = self.Component(shield_data)
        quarters = self.Component(quarters_data)

        ship = self._create_mock_ship([engine, shield, quarters])
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        calculator.calculate(ship)

        # Verify all phases ran
        assert ship.total_thrust == 1500  # Phase 3
        assert ship.max_shields == 400.0  # Phase 3
        assert ship.acceleration_rate > 0  # Phase 4
        assert hasattr(ship, 'total_defense_score')  # Phase 5
        assert ship.crew_onboard == 10  # Phase 1 & 2


class TestPhaseHelperMethods:
    """Test individual phase helper methods after extraction."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Load test data once."""
        self.modules_patcher = patch.dict(sys.modules, {
            'pygame': MagicMock(),
            'pygame.mixer': MagicMock(),
            'pygame.font': MagicMock()
        })
        self.modules_patcher.start()

        from game.core.registry import RegistryManager
        from game.simulation.components.component import Component, load_components, load_modifiers
        from game.simulation.systems.stats import ShipStatsCalculator
        from game.core.constants import LayerType
        from game.simulation.systems.resource_manager import ResourceRegistry

        self.Component = Component
        self.ShipStatsCalculator = ShipStatsCalculator
        self.LayerType = LayerType
        self.ResourceRegistry = ResourceRegistry
        self.vehicle_classes = RegistryManager.instance().vehicle_classes
        self.RegistryManager = RegistryManager

        load_components()
        load_modifiers()

        yield

        self.modules_patcher.stop()
        RegistryManager.instance().clear()

    def test_check_damage_and_gather_resources_exists(self):
        """Verify _check_damage_and_gather_resources method exists after refactor."""
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        assert hasattr(calculator, '_check_damage_and_gather_resources')

    def test_allocate_crew_and_life_support_exists(self):
        """Verify _allocate_crew_and_life_support method exists after refactor."""
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        assert hasattr(calculator, '_allocate_crew_and_life_support')

    def test_aggregate_component_stats_exists(self):
        """Verify _aggregate_component_stats method exists after refactor."""
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        assert hasattr(calculator, '_aggregate_component_stats')

    def test_apply_physics_limits_exists(self):
        """Verify _apply_physics_limits method exists after refactor."""
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        assert hasattr(calculator, '_apply_physics_limits')

    def test_calculate_combat_stats_exists(self):
        """Verify _calculate_combat_stats method exists after refactor."""
        calculator = self.ShipStatsCalculator(self.vehicle_classes)
        assert hasattr(calculator, '_calculate_combat_stats')
