"""
Tests for ShipCombatEngine combat cooldowns.

Tests shield regeneration, repair rate application, and energy consumption
during cooldown updates.

PROJ-118: Phase 2 Task 2.17 - ShipCombatEngine cooldown test coverage.
"""

import pytest
from unittest.mock import MagicMock, PropertyMock

from game.core.constants import CombatConstants
from game.simulation.components.component_constants import ComponentStatus


class TestCooldownUpdateBasics:
    """Tests for basic update_combat_cooldowns behavior."""

    def test_update_cooldowns_does_nothing_when_ship_is_dead(self):
        """update_combat_cooldowns returns early if ship is not alive."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = False
        ship.current_shields = 50
        ship.max_shields = 100
        ship.shield_regen_rate = 60.0

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Ship attributes should not be modified
        assert ship.current_shields == 50

    def test_update_cooldowns_processes_when_ship_is_alive(self):
        """update_combat_cooldowns processes when ship is alive."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 50
        ship.max_shields = 100
        ship.shield_regen_rate = 60.0  # 0.6 per tick
        ship.shield_regen_cost = 0.0
        ship.repair_rate = 0

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Shield should have regenerated
        assert ship.current_shields == pytest.approx(50.6)


class TestShieldRegeneration:
    """Tests for shield regeneration during cooldown updates.

    PROJ-495 T3.5: parametrized the 5 shield-regen tests on
    ``(initial_shields, max_shields, regen_rate, ticks, expected_shields)``.
    All five share the same is_alive=True / shield_regen_cost=0 /
    repair_rate=0 setup; only the four numerical params and the tick count
    vary.
    """

    @pytest.mark.parametrize(
        "initial_shields,max_shields,regen_rate,ticks,expected_shields",
        [
            # below-max: rate 100.0/tick interval gives +1.0 per tick
            (80, 100, 100.0, 1, pytest.approx(81.0)),
            # cap at max even when rate would overshoot
            (99.5, 100, 100.0, 1, 100),
            # at max: no regen
            (100, 100, 100.0, 1, 100),
            # zero rate: no regen
            (50, 100, 0.0, 1, 50),
            # 10 ticks at 50.0 (0.5/tick) accumulates to 5.0
            (0, 100, 50.0, 10, pytest.approx(5.0)),
        ],
        ids=[
            "below_max_increments",
            "caps_at_max",
            "no_regen_at_max",
            "zero_rate_no_regen",
            "multi_tick_accumulates",
        ],
    )
    def test_shield_regen(
        self,
        initial_shields,
        max_shields,
        regen_rate,
        ticks,
        expected_shields,
    ):
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = initial_shields
        ship.max_shields = max_shields
        ship.shield_regen_rate = regen_rate
        ship.shield_regen_cost = 0.0
        ship.repair_rate = 0

        engine = ShipCombatEngine(ship)
        for _ in range(ticks):
            engine.update_combat_cooldowns()

        assert ship.current_shields == expected_shields


class TestShieldRegenEnergyCost:
    """Tests for shield regeneration energy consumption."""

    def test_shield_regen_consumes_energy(self):
        """Shield regeneration consumes energy when cost > 0."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 50
        ship.max_shields = 100
        ship.shield_regen_rate = 100.0  # 1.0 per tick
        ship.shield_regen_cost = 50.0   # 0.5 per tick
        ship.repair_rate = 0

        # Create energy resource mock
        energy_res = MagicMock()
        energy_res.current_value = 100
        energy_res.consume = MagicMock()

        resources = MagicMock()
        resources.get_resource = MagicMock(return_value=energy_res)
        ship.resources = resources

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Energy should be consumed
        energy_res.consume.assert_called_once_with(0.5)
        # Shield should regenerate
        assert ship.current_shields == pytest.approx(51.0)

    def test_shield_regen_blocked_when_no_energy(self):
        """Shield regeneration is blocked when insufficient energy."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 50
        ship.max_shields = 100
        ship.shield_regen_rate = 100.0
        ship.shield_regen_cost = 50.0
        ship.repair_rate = 0

        # Energy resource with insufficient energy
        energy_res = MagicMock()
        energy_res.current_value = 0.1  # Less than cost (0.5)

        resources = MagicMock()
        resources.get_resource = MagicMock(return_value=energy_res)
        ship.resources = resources

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Shield should NOT regenerate
        assert ship.current_shields == 50

    # DELETED: test_shield_regen_works_without_resources_attribute
    # Reason: Duck typing replaced with explicit protocols in PROJ-190.
    # Ships must now have resources attribute.

    def test_shield_regen_with_zero_cost_skips_energy_check(self):
        """Zero cost skips energy consumption entirely."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 50
        ship.max_shields = 100
        ship.shield_regen_rate = 100.0
        ship.shield_regen_cost = 0.0
        ship.repair_rate = 0

        resources = MagicMock()
        resources.get_resource = MagicMock()
        ship.resources = resources

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # get_resource should not be called when cost is 0
        resources.get_resource.assert_not_called()
        assert ship.current_shields == pytest.approx(51.0)


class TestRepairSystem:
    """Tests for ship repair during cooldown updates."""

    def test_repair_applies_to_damaged_component(self, fresh_registries):
        """Repair rate heals the most damaged component."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="RepairTest",
            add_bridge=True,
            add_engine=True,
            registries=fresh_registries
        )
        ship.repair_rate = 100.0  # 1.0 HP per tick

        # Find a component and damage it
        components = list(ship.get_all_components())
        target_comp = components[0]
        original_hp = target_comp.current_hp
        target_comp.current_hp = target_comp.max_hp * 0.5  # Damage to 50%
        target_comp.mark_hp_cache_dirty()

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Component should have gained HP
        assert target_comp.current_hp > target_comp.max_hp * 0.5

    def test_repair_does_nothing_with_zero_rate(self, fresh_registries):
        """No repair occurs when repair_rate is zero."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="NoRepairTest",
            add_bridge=True,
            add_engine=True,
            registries=fresh_registries
        )
        ship.repair_rate = 0

        # Damage a component
        components = list(ship.get_all_components())
        target_comp = components[0]
        damaged_hp = target_comp.max_hp * 0.5
        target_comp.current_hp = damaged_hp
        target_comp.mark_hp_cache_dirty()

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # HP should remain unchanged
        assert target_comp.current_hp == damaged_hp

    def test_repair_selects_most_damaged_component(self, fresh_registries):
        """Repair prioritizes component with lowest HP ratio."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="PriorityRepairTest",
            add_bridge=True,
            add_engine=True,
            registries=fresh_registries
        )
        ship.repair_rate = 100.0  # 1.0 HP per tick

        # Get two components and damage them differently
        components = list(ship.get_all_components())
        if len(components) >= 2:
            comp_a = components[0]
            comp_b = components[1]

            # Damage comp_a to 70% HP
            comp_a.current_hp = comp_a.max_hp * 0.7
            comp_a.mark_hp_cache_dirty()

            # Damage comp_b to 30% HP (more damaged)
            comp_b.current_hp = comp_b.max_hp * 0.3
            comp_b.mark_hp_cache_dirty()

            hp_before_b = comp_b.current_hp

            engine = ShipCombatEngine(ship)
            engine.update_combat_cooldowns()

            # comp_b (more damaged) should receive repair
            assert comp_b.current_hp > hp_before_b

    def test_repair_does_nothing_when_all_components_full(self, fresh_registries):
        """No repair occurs when all components are at full HP."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="FullHpTest",
            add_bridge=True,
            add_engine=True,
            registries=fresh_registries
        )
        ship.repair_rate = 100.0

        # Ensure all components are at full HP
        for comp in ship.get_all_components():
            comp.current_hp = comp.max_hp
            comp.mark_hp_cache_dirty()

        # Store original HP values
        hp_values = {id(c): c.current_hp for c in ship.get_all_components()}

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # All HP values should remain unchanged
        for comp in ship.get_all_components():
            assert comp.current_hp == hp_values[id(comp)]

    def test_repair_does_not_heal_destroyed_components(self, fresh_registries):
        """Repair skips components with zero HP (destroyed)."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="DestroyedCompTest",
            add_bridge=True,
            add_engine=True,
            registries=fresh_registries
        )
        ship.repair_rate = 100.0

        # Find a component and destroy it (0 HP)
        components = list(ship.get_all_components())
        destroyed_comp = components[0]
        destroyed_comp.current_hp = 0
        destroyed_comp.mark_hp_cache_dirty()

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Destroyed component should NOT be repaired
        assert destroyed_comp.current_hp == 0

    def test_repair_caps_at_max_hp(self, fresh_registries):
        """Repair does not exceed component max HP."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="RepairCapTest",
            add_bridge=True,
            add_engine=True,
            registries=fresh_registries
        )
        ship.repair_rate = 1000.0  # 10 HP per tick - high rate

        # Slightly damage a component
        components = list(ship.get_all_components())
        target_comp = components[0]
        target_comp.current_hp = target_comp.max_hp - 0.1  # Only 0.1 HP missing
        target_comp.mark_hp_cache_dirty()

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Should be capped at max HP
        assert target_comp.current_hp == target_comp.max_hp


class TestRepairStatusRestoration:
    """Tests for component status restoration during repair."""

    def test_repair_reactivates_disabled_component(self, fresh_registries):
        """Repair restores inactive component when HP exceeds threshold."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="ReactivateTest",
            add_bridge=True,
            add_engine=True,
            registries=fresh_registries
        )
        # High repair rate to exceed threshold in one tick
        ship.repair_rate = 5000.0  # 50 HP per tick

        # Find a component and disable it
        components = list(ship.get_all_components())
        target_comp = components[0]

        # Set HP below threshold and mark inactive
        target_comp.current_hp = target_comp.max_hp * 0.4  # Below 50% threshold
        target_comp.is_active = False
        target_comp.status = ComponentStatus.DAMAGED
        target_comp.mark_hp_cache_dirty()

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # After repair, HP should exceed threshold and status restored
        if target_comp.hp_ratio > CombatConstants.DEFAULT_DAMAGE_THRESHOLD:
            assert target_comp.is_active is True
            assert target_comp.status == ComponentStatus.ACTIVE


class TestCooldownEdgeCases:
    """Tests for edge cases in cooldown handling."""

    def test_negative_shield_regen_rate_does_nothing(self):
        """Negative regen rate does not affect shields."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 50
        ship.max_shields = 100
        ship.shield_regen_rate = -10.0  # Invalid negative rate
        ship.shield_regen_cost = 0.0
        ship.repair_rate = 0

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Shields should remain unchanged (condition fails: rate > 0)
        assert ship.current_shields == 50

    def test_very_small_regen_rate_accumulates(self):
        """Very small regen rates still accumulate over time."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 0
        ship.max_shields = 100
        ship.shield_regen_rate = 0.01  # Very small: 0.0001 per tick
        ship.shield_regen_cost = 0.0
        ship.repair_rate = 0

        engine = ShipCombatEngine(ship)

        # Simulate many ticks
        for _ in range(10000):
            engine.update_combat_cooldowns()

        # Should have accumulated 10000 * 0.0001 = 1.0
        assert ship.current_shields == pytest.approx(1.0)

    def test_concurrent_shield_regen_and_repair(self, fresh_registries):
        """Both shield regen and repair occur in same tick."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="ConcurrentTest",
            add_bridge=True,
            add_engine=True,
            add_shields=1,
            registries=fresh_registries
        )

        ship.shield_regen_rate = 100.0  # 1.0 per tick
        ship.shield_regen_cost = 0.0
        ship.repair_rate = 100.0  # 1.0 HP per tick

        # Set up initial state
        initial_shields = ship.current_shields - 10  # Drain some shields
        ship.current_shields = initial_shields

        # Damage a component
        components = list(ship.get_all_components())
        target_comp = components[0]
        initial_hp = target_comp.current_hp * 0.5
        target_comp.current_hp = initial_hp
        target_comp.mark_hp_cache_dirty()

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Both should have updated
        assert ship.current_shields > initial_shields
        assert target_comp.current_hp > initial_hp

    # DELETED: test_missing_repair_rate_attribute
    # Reason: Duck typing replaced with explicit protocols in PROJ-190.
    # Ships must now have repair_rate attribute.


class TestApplyRepairPrivateMethod:
    """Tests for _apply_repair private method behavior."""

    def test_apply_repair_with_zero_amount_does_nothing(self, fresh_registries):
        """_apply_repair with zero amount has no effect."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="ZeroRepairTest",
            add_bridge=True,
            registries=fresh_registries
        )

        # Damage a component
        components = list(ship.get_all_components())
        target_comp = components[0]
        damaged_hp = target_comp.max_hp * 0.5
        target_comp.current_hp = damaged_hp
        target_comp.mark_hp_cache_dirty()

        engine = ShipCombatEngine(ship)
        engine._apply_repair(0)

        # HP should remain unchanged
        assert target_comp.current_hp == damaged_hp

    def test_apply_repair_with_negative_amount_does_nothing(self, fresh_registries):
        """_apply_repair with negative amount has no effect."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="NegativeRepairTest",
            add_bridge=True,
            registries=fresh_registries
        )

        # Damage a component
        components = list(ship.get_all_components())
        target_comp = components[0]
        damaged_hp = target_comp.max_hp * 0.5
        target_comp.current_hp = damaged_hp
        target_comp.mark_hp_cache_dirty()

        engine = ShipCombatEngine(ship)
        engine._apply_repair(-10)

        # HP should remain unchanged
        assert target_comp.current_hp == damaged_hp


class TestIntegrationWithRealShip:
    """Integration tests using real Ship objects."""

    def test_full_cooldown_cycle_with_real_ship(self, fresh_registries):
        """Complete cooldown cycle with real ship instance."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="IntegrationTest",
            add_bridge=True,
            add_engine=True,
            add_shields=1,
            registries=fresh_registries
        )

        # Get initial values
        initial_shields = ship.current_shields

        # Drain shields
        ship.current_shields = initial_shields * 0.5

        engine = ShipCombatEngine(ship)

        # Run multiple cooldown cycles
        for _ in range(100):
            engine.update_combat_cooldowns()

        # Shields should have regenerated (if ship has regen rate)
        if ship.shield_regen_rate > 0:
            assert ship.current_shields > initial_shields * 0.5

    def test_cooldowns_respect_ship_death(self, fresh_registries):
        """Cooldowns stop processing when ship dies."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="DeathTest",
            add_bridge=True,
            add_engine=True,
            registries=fresh_registries
        )

        # Set up regen
        ship.shield_regen_rate = 100.0
        ship.shield_regen_cost = 0.0
        ship.current_shields = 50
        ship.max_shields = 100

        # Kill the ship
        ship.is_alive = False

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Shields should not have changed
        assert ship.current_shields == 50


class TestShieldRegenEdgeCases:
    """Additional edge cases for shield regeneration."""

    def test_shield_regen_with_very_large_rate(self):
        """Very large regen rate caps at max shields."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 0
        ship.max_shields = 100
        ship.shield_regen_rate = 100000.0  # Extremely high rate (1000 per tick)
        ship.shield_regen_cost = 0.0
        ship.repair_rate = 0

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Should be capped at max shields
        assert ship.current_shields == 100

    def test_shield_regen_with_fractional_shields(self):
        """Shield regeneration with fractional current value."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 50.333
        ship.max_shields = 100
        ship.shield_regen_rate = 100.0  # 1.0 per tick
        ship.shield_regen_cost = 0.0
        ship.repair_rate = 0

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        assert ship.current_shields == pytest.approx(51.333)

    def test_energy_consumption_exact_amount_available(self):
        """Shield regen when energy exactly matches cost."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 50
        ship.max_shields = 100
        ship.shield_regen_rate = 100.0
        ship.shield_regen_cost = 100.0  # 1.0 per tick, exact match

        energy_res = MagicMock()
        energy_res.current_value = 1.0  # Exact amount needed
        energy_res.consume = MagicMock()

        resources = MagicMock()
        resources.get_resource = MagicMock(return_value=energy_res)
        ship.resources = resources
        ship.repair_rate = 0

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Should consume energy and regenerate
        energy_res.consume.assert_called_once()
        assert ship.current_shields == pytest.approx(51.0)

    def test_energy_resource_not_found(self):
        """Shield regen when energy resource doesn't exist."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.current_shields = 50
        ship.max_shields = 100
        ship.shield_regen_rate = 100.0
        ship.shield_regen_cost = 50.0
        ship.repair_rate = 0

        resources = MagicMock()
        resources.get_resource = MagicMock(return_value=None)  # Resource not found
        ship.resources = resources

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Should still regenerate (no energy check fails gracefully)
        assert ship.current_shields == pytest.approx(51.0)


class TestRepairEdgeCases:
    """Additional edge cases for repair system."""

    def test_repair_with_fractional_hp(self, fresh_registries):
        """Repair with fractional HP values."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="FractionalRepairTest",
            add_bridge=True,
            registries=fresh_registries
        )
        ship.repair_rate = 50.0  # 0.5 HP per tick

        components = list(ship.get_all_components())
        target_comp = components[0]
        initial_hp = target_comp.max_hp * 0.333  # Fractional HP
        target_comp.current_hp = initial_hp
        target_comp.mark_hp_cache_dirty()

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Should have partial repair applied
        assert target_comp.current_hp > initial_hp

    def test_repair_multiple_damaged_components(self, fresh_registries):
        """Repair only heals one component per tick (most damaged)."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="MultiDamageTest",
            add_bridge=True,
            add_engine=True,
            registries=fresh_registries
        )
        ship.repair_rate = 100.0  # 1.0 HP per tick

        components = list(ship.get_all_components())
        if len(components) >= 2:
            # Damage both components equally
            for comp in components[:2]:
                comp.current_hp = comp.max_hp * 0.5
                comp.mark_hp_cache_dirty()

            hp_before = [c.current_hp for c in components[:2]]

            engine = ShipCombatEngine(ship)
            engine.update_combat_cooldowns()

            hp_after = [c.current_hp for c in components[:2]]

            # Only one should be healed (whichever has lower hp_ratio)
            healed_count = sum(1 for i in range(2) if hp_after[i] > hp_before[i])
            assert healed_count == 1

    def test_repair_preserves_max_hp_boundary(self, fresh_registries):
        """Repair amount that would exceed max HP is capped."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine
        from tests.fixtures.ships import create_test_ship

        ship = create_test_ship(
            name="CapBoundaryTest",
            add_bridge=True,
            registries=fresh_registries
        )
        ship.repair_rate = 10000.0  # 100 HP per tick - very high

        components = list(ship.get_all_components())
        target_comp = components[0]
        target_comp.current_hp = target_comp.max_hp - 0.001  # Very close to max
        target_comp.mark_hp_cache_dirty()

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Should be exactly at max, not over
        assert target_comp.current_hp == target_comp.max_hp


class TestCombatEngineSharedState:
    """Tests for ShipCombatEngine subsystem ownership.

    PROJ-471 Task 1.2: subsystems are now PER-INSTANCE (no class-level
    sharing). The previous ``test_multiple_engines_share_subsystems`` pinned
    the cross-instance/cross-battle state-leak bug and was inverted here.
    """

    def test_multiple_standalone_engines_have_distinct_subsystems(self):
        """Standalone engines own distinct subsystems (no class-level leak)."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship1 = MagicMock()
        ship1.is_alive = True
        ship2 = MagicMock()
        ship2.is_alive = True

        engine1 = ShipCombatEngine(ship1)
        engine2 = ShipCombatEngine(ship2)

        # No class-level shared subsystem state.
        assert ShipCombatEngine.__dict__.get("_targeting_system") is None
        assert ShipCombatEngine.__dict__.get("_damage_calculator") is None
        assert ShipCombatEngine.__dict__.get("_weapon_firing_system") is None
        # Each engine owns its own subsystems.
        assert engine1._targeting_system is not engine2._targeting_system
        assert engine1._damage_calculator is not engine2._damage_calculator
        assert engine1._weapon_firing_system is not engine2._weapon_firing_system

    def test_engine_stores_ship_reference(self):
        """Engine stores correct ship reference."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.name = "TestShip"

        engine = ShipCombatEngine(ship)

        assert engine._ship is ship
        assert engine._ship.name == "TestShip"


class TestCooldownInteractionWithDerelict:
    """Tests for cooldown behavior with derelict ships."""

    def test_derelict_ship_processed_if_alive(self):
        """Derelict ship still processes cooldowns if is_alive is True."""
        from game.simulation.entities.ship_combat_engine import ShipCombatEngine

        ship = MagicMock()
        ship.is_alive = True
        ship.is_derelict = True  # Derelict but still alive
        ship.current_shields = 50
        ship.max_shields = 100
        ship.shield_regen_rate = 100.0
        ship.shield_regen_cost = 0.0
        ship.repair_rate = 0

        engine = ShipCombatEngine(ship)
        engine.update_combat_cooldowns()

        # Should still process since is_alive is True
        assert ship.current_shields == pytest.approx(51.0)
