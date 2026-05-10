"""
Tests for ShipStatsCalculator helper method extraction (Phase 8, Task 8.1).
Verify that the refactored calculate() method produces identical results.

PROJ-51: Updated to import from entities/ship_stats.py (canonical location).
Updated to use fresh_registries fixture for PROJ-50 strict DI.
"""
import pytest
from unittest.mock import MagicMock

from game.simulation.entities.ship_stats import ShipStatsCalculator
from game.simulation.components.component import Component
from game.simulation.components.component_constants import ComponentStatus
from game.core.constants import LayerType
from game.simulation.systems.resource_manager import ResourceRegistry
from game.simulation.entities.layer_data import LayerData


class TestShipStatsCalculatorPhases:
    """Test ShipStatsCalculator phase extraction."""

    @pytest.fixture(autouse=True)
    def setup(self, fresh_registries):
        """Set up test fixtures with DI registries."""
        self.registries = fresh_registries
        self.vehicle_classes = fresh_registries.vehicle_classes

    def _create_mock_ship(self, components, vehicle_type="Ship"):
        """Create a mock ship with the given components."""
        ship = MagicMock()
        ship.layers = {
            LayerType.CORE: LayerData(
                components=components,
                mass=0,
                max_mass_pct=0.3
            )
        }
        ship.base_mass = 100
        ship.mass = 100
        ship.current_mass = 0
        ship.ship_class = "Corvette"
        ship.vehicle_type = vehicle_type
        ship.resources = ResourceRegistry()
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
                result.extend(layer_data.components)
            return result

        def iter_components():
            for layer_type, layer_data in ship.layers.items():
                for comp in layer_data.components:
                    yield layer_type, comp

        ship.get_all_components = get_all_components
        ship.iter_components = iter_components

        for c in components:
            c.ship = ship
            c.recalculate_stats()

        return ship

    def test_damage_check_phase_marks_damaged_components(self):
        """Verify Phase 1 correctly marks components as damaged at 50% HP threshold."""
        comp_data = {
            'id': 'test_comp',
            'name': 'Test Component',
            'type': 'Electronics',
            'mass': 50,
            'hp': 100,
            'abilities': {}
        }
        comp = Component(comp_data, registries=self.registries)
        comp.current_hp = 40  # 40% HP - below 50% threshold

        ship = self._create_mock_ship([comp])
        calculator = ShipStatsCalculator(self.vehicle_classes, resource_catalog=self.registries.resource_catalog)
        calculator.calculate(ship)

        assert comp.is_active is False
        assert comp.status == ComponentStatus.DAMAGED

    def test_calculate_uses_injected_planetary_resource_ids(self):
        """Injected planetary resource IDs should be used for construction_cost keys."""
        ship = self._create_mock_ship([])
        calculator = ShipStatsCalculator(
            self.vehicle_classes,
            planetary_resource_ids=['metals', 'organics'],
        )
        calculator.calculate(ship)
        assert ship.construction_cost == {'metals': 0, 'organics': 0}

    def test_resource_catalog_injection_populates_planetary_ids(self):
        """Passing resource_catalog= should derive planetary resource IDs from it."""
        from game.core.resources import ResourceCatalog
        real_catalog = ResourceCatalog.from_json()

        calculator = ShipStatsCalculator(
            self.vehicle_classes,
            resource_catalog=real_catalog,
        )
        # Lazy — resolve via accessor
        assert len(calculator._get_or_resolve_planetary_ids()) > 0

    def test_no_resource_catalog_raises_on_calculate(self):
        """Omitting resource_catalog and planetary_resource_ids should raise on calculate()."""
        calculator = ShipStatsCalculator(self.vehicle_classes)
        ship = self._create_mock_ship([])
        with pytest.raises(TypeError):
            calculator.calculate(ship)

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
        comp = Component(comp_data, registries=self.registries)
        comp.current_hp = 60  # 60% HP - above 50% threshold

        ship = self._create_mock_ship([comp])
        calculator = ShipStatsCalculator(self.vehicle_classes, resource_catalog=self.registries.resource_catalog)
        calculator.calculate(ship)

        assert comp.is_active is True
        assert comp.status == ComponentStatus.ACTIVE

    def test_crew_allocation_phase_deactivates_uncrewed_components(self):
        """Verify Phase 2 deactivates components that don't have crew."""
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
        weapon = Component(weapon_data, registries=self.registries)

        ship = self._create_mock_ship([weapon])
        calculator = ShipStatsCalculator(self.vehicle_classes, resource_catalog=self.registries.resource_catalog)
        calculator.calculate(ship)

        assert weapon.is_active is False
        assert weapon.status == ComponentStatus.NO_CREW

    def test_crew_allocation_phase_activates_crewed_components(self):
        """Verify Phase 2 keeps components active when crew is available."""
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
        quarters = Component(quarters_data, registries=self.registries)
        weapon = Component(weapon_data, registries=self.registries)

        ship = self._create_mock_ship([quarters, weapon])
        calculator = ShipStatsCalculator(self.vehicle_classes, resource_catalog=self.registries.resource_catalog)
        calculator.calculate(ship)

        assert weapon.is_active is True
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
        engine1 = Component(engine1_data, registries=self.registries)
        engine2 = Component(engine2_data, registries=self.registries)

        ship = self._create_mock_ship([engine1, engine2])
        calculator = ShipStatsCalculator(self.vehicle_classes, resource_catalog=self.registries.resource_catalog)
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
        shield1 = Component(shield1_data, registries=self.registries)
        shield2 = Component(shield2_data, registries=self.registries)

        ship = self._create_mock_ship([shield1, shield2])
        calculator = ShipStatsCalculator(self.vehicle_classes, resource_catalog=self.registries.resource_catalog)
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
        engine = Component(engine_data, registries=self.registries)

        ship = self._create_mock_ship([engine])
        calculator = ShipStatsCalculator(self.vehicle_classes, resource_catalog=self.registries.resource_catalog)
        calculator.calculate(ship)

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
        engine = Component(engine_data, registries=self.registries)
        thruster = Component(thruster_data, registries=self.registries)

        ship = self._create_mock_ship([engine, thruster])
        calculator = ShipStatsCalculator(self.vehicle_classes, resource_catalog=self.registries.resource_catalog)
        calculator.calculate(ship)

        assert hasattr(ship, 'total_defense_score')
        assert isinstance(ship.total_defense_score, (int, float))

    def test_calculate_orchestrates_all_phases(self):
        """Integration test: verify calculate() orchestrates all phases correctly."""
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

        engine = Component(engine_data, registries=self.registries)
        shield = Component(shield_data, registries=self.registries)
        quarters = Component(quarters_data, registries=self.registries)

        ship = self._create_mock_ship([engine, shield, quarters])
        calculator = ShipStatsCalculator(self.vehicle_classes, resource_catalog=self.registries.resource_catalog)
        calculator.calculate(ship)

        # Verify all phases ran
        assert ship.total_thrust == 1500  # Phase 3
        assert ship.max_shields == 400.0  # Phase 3
        assert ship.acceleration_rate > 0  # Phase 4
        assert hasattr(ship, 'total_defense_score')  # Phase 5
        assert ship.crew_onboard == 10  # Phase 1 & 2


