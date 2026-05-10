import pytest
import math
from game.simulation.components.component import Component
from game.simulation.components.component_stats_calculator import ComponentStatsCalculator
from game.core.constants import LayerType
from game.simulation.components.component_constants import ComponentStatus
from game.simulation.validation.ship_validator import ResourceDependencyRule
from game.core.validation import ValidationResult
from game.simulation.entities.ship import Ship
from game.simulation.components.abilities import ABILITY_REGISTRY, create_ability
from game.simulation.components.abilities.resources import ResourceStorage, ResourceConsumption
from game.simulation.components.abilities import CrewRequired


class TestBugFixRegressions:
    """
    Regression tests for bugs fixed in Jan 2026 session.
    - Bug 1: Crew Update Delay (CrewRequired missing updates)
    - Bug 2: Weapons Panel Missing Stats (AttributeError on Component)
    - Bug 3: Resource Validation (AttributeError / Logic Flaws)
    """

    def test_bug1_crew_requirement_update(self, fresh_registries):
        """
        Bug 1: Crew Required stat should update when modifiers change 'crew_req_mult'.
        Root cause: CrewRequired ability wasn't accepting 'amount' key (defaulting to 0)
        and potential logic gap.
        """
        # 1. Setup Component with 10 crew req
        comp_data = {
            'id': 'bridge_test', 'name': 'Bridge', 'type': 'Bridge', 'mass': 100, 'hp': 100,
            'abilities': {
                'CrewRequired': {'amount': 10}  # 'amount' key was previously ignored
            }
        }
        c = Component(comp_data, registries=fresh_registries)

        # Verify initial
        ab = c.get_ability('CrewRequired')
        assert ab is not None, "CrewRequired should exist"
        assert ab.amount == 10, "Should read 'amount' correctly (Fix applied)"

        # 2. Simulate Modifier Calculation
        # We manually inject stats to simulate a modifier (e.g. Size Mod)
        # Recalculate logic: amount = base * sqrt(mass_mult) * crew_req_mult
        stats = {
            'mass_mult': 1.0,
            'hp_mult': 1.0,
            'crew_req_mult': 2.5,  # The modifier effect
            'properties': {},
            'mass_add': 0.0, 'cost_mult': 1.0, 'consumption_mult': 1.0, 'capacity_mult': 1.0, 'energy_gen_mult': 1.0
        }

        # Inject stats and trigger update
        c.stats = stats
        ComponentStatsCalculator.apply_base_stats(c, stats, 100)  # This triggers ab.recalculate()

        # Verify update
        # 10 * 1.0 * 2.5 = 25
        assert ab.amount == 25, "Crew requirement should update based on multipliers"

    def test_bug3_resource_validation_logic(self, fresh_registries):
        """
        Bug 3: Validator crashed on 'resource_name' attribute error for Storage,
        and logic needs to ensure specific resources are checked.
        """
        ship = Ship("Test Ship", 0, 0, (0, 0, 0), registries=fresh_registries)
        rule = ResourceDependencyRule()

        # 1. Add Fuel Consumer (Engine)
        engine = Component({
            'id': 'engine', 'name': 'Engine', 'type': 'Engine', 'mass': 10, 'hp': 10,
            'abilities': {'ResourceConsumption': [{'resource': 'fuel', 'amount': 1}]}
        }, registries=fresh_registries)
        ship.add_component(engine, LayerType.CORE)

        # 2. Add Ammo Storage (Should NOT satisfy Fuel)
        ammo_tank = Component({
            'id': 'ammo', 'name': 'Ammo', 'type': 'Tank', 'mass': 10, 'hp': 10,
            'abilities': {'ResourceStorage': [{'resource': 'ammo', 'amount': 100}]}
        }, registries=fresh_registries)
        ship.add_component(ammo_tank, LayerType.CORE)

        # 3. Validate
        res = rule.validate(ship)

        # Check warnings
        warnings = res.warnings
        assert any("Needs Fuel Storage" in w for w in warnings), \
            f"Warning for Fuel should exist. Got: {warnings}"

    def test_bug2_weapon_ability_access(self, fresh_registries):
        """
        Bug 2: WeaponsPanel was using getattr(comp, 'range') which doesn't exist.
        Fix ensures we use comp.get_ability('WeaponAbility').range.
        We verify the data structure supports this.
        """
        comp_data = {
            'id': 'laser', 'name': 'Laser', 'type': 'Weapon', 'mass': 10, 'hp': 10,
            'abilities': {
                'WeaponAbility': {'range': 1000, 'damage': 50}
            }
        }
        c = Component(comp_data, registries=fresh_registries)

        # Verify Component NO LONGER has range property (Shim Removed)
        assert not hasattr(c, 'range'), "Component should NOT have 'range' attribute shim (Phase 11 Removal)"


        # Verify Ability access works
        ab = c.get_ability('WeaponAbility')
        assert ab is not None
        assert ab.range == 1000
        assert ab.damage == 50
