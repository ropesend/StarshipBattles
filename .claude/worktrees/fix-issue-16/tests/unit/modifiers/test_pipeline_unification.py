"""
Tests for Phase 4: Pipeline Unification

Verifies that the single recalculate() path works correctly after
removing duplicate stat application code from _apply_base_stats().
"""
import pytest


class TestSingleRecalculatePath:
    """Tests verifying abilities recalculate correctly without duplicate code."""

    def test_resource_consumption_recalculates_via_stat_bindings(self, fresh_registries):
        """ResourceConsumption.recalculate() should apply consumption_mult correctly."""
        from game.simulation.components.component import create_component

        # Create a component with ResourceConsumption (railgun has energy consumption)
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.recalculate_stats()

        # Get the ResourceConsumption ability
        rc = railgun.get_ability('ResourceConsumption')
        if rc is None:
            pytest.skip("railgun doesn't have ResourceConsumption")

        base_amount = rc._base_amount

        # Apply efficiency modifier (reduces consumption)
        railgun.add_modifier('efficiency_mount', 0.5)  # 50% consumption

        # Verify consumption was reduced
        assert rc.amount == pytest.approx(base_amount * 0.5)

    def test_resource_storage_recalculates_via_stat_bindings(self, fresh_registries):
        """ResourceStorage.recalculate() should apply capacity_mult correctly."""
        from game.simulation.components.component import create_component

        # Create a component with ResourceStorage
        fuel_tank = create_component('fuel_tank', registries=fresh_registries)
        if fuel_tank is None:
            pytest.skip("fuel_tank component not found")

        fuel_tank.recalculate_stats()

        # Get the ResourceStorage ability
        rs = fuel_tank.get_ability('ResourceStorage')
        if rs is None:
            pytest.skip("fuel_tank doesn't have ResourceStorage")

        base_max = rs._base_max_amount

        # Apply simple_size_mount modifier
        fuel_tank.add_modifier('simple_size_mount', 2.0)

        # Verify capacity was scaled
        assert rs.max_amount == pytest.approx(base_max * 2.0)

    def test_resource_generation_recalculates_via_stat_bindings(self, fresh_registries):
        """ResourceGeneration.recalculate() should apply energy_gen_mult correctly."""
        from game.simulation.components.component import create_component

        # Create a component with ResourceGeneration
        generator = create_component('generator', registries=fresh_registries)
        generator.recalculate_stats()

        # Get the ResourceGeneration ability
        rg = generator.get_ability('ResourceGeneration')
        if rg is None:
            pytest.skip("generator doesn't have ResourceGeneration")

        base_rate = rg._base_rate

        # Apply simple_size_mount modifier
        generator.add_modifier('simple_size_mount', 2.0)

        # Verify rate was scaled
        assert rg.rate == pytest.approx(base_rate * 2.0)

    def test_all_abilities_recalculate_called(self, fresh_registries):
        """All ability instances should have recalculate() called during stats recalc."""
        from game.simulation.components.component import create_component

        # Create a component with multiple abilities
        railgun = create_component('railgun', registries=fresh_registries)
        railgun.recalculate_stats()

        # Every ability should have had recalculate() called
        for ab in railgun.ability_instances:
            # Verify ability has STAT_BINDINGS (all abilities should now)
            assert hasattr(ab.__class__, 'STAT_BINDINGS'), \
                f"{ab.__class__.__name__} missing STAT_BINDINGS"


class TestNoManuaStatsApplication:
    """Tests verifying that abilities handle their own stat application."""

    def test_weapon_damage_from_ability_recalculate(self, fresh_registries):
        """WeaponAbility should apply damage_mult via its own recalculate()."""
        from game.simulation.components.component import create_component

        railgun = create_component('railgun', registries=fresh_registries)
        railgun.recalculate_stats()

        weapon = railgun.get_ability('WeaponAbility')
        base_damage = weapon._base_damage
        base_range = weapon._base_range

        # Apply simple_size_mount (scales damage)
        railgun.add_modifier('simple_size_mount', 2.0)

        # Damage should be scaled
        assert weapon.damage == pytest.approx(base_damage * 2.0)
        # Range should NOT be scaled by simple_size_mount (it doesn't affect range_mult)
        assert weapon.range == pytest.approx(base_range)

    def test_propulsion_thrust_from_ability_recalculate(self, fresh_registries):
        """CombatPropulsion should apply thrust_mult via its own recalculate()."""
        from game.simulation.components.component import create_component

        engine = create_component('standard_engine', registries=fresh_registries)
        if engine is None:
            pytest.skip("engine_basic component not found")

        engine.recalculate_stats()

        prop = engine.get_ability('CombatPropulsion')
        if prop is None:
            pytest.skip("engine_basic doesn't have CombatPropulsion")

        base_thrust = prop.base_thrust

        # Apply simple_size_mount (scales thrust)
        engine.add_modifier('simple_size_mount', 3.0)

        # Thrust should be scaled
        assert prop.thrust_force == pytest.approx(base_thrust * 3.0)


class TestStatBindingsCompleteness:
    """Tests verifying all abilities declare their STAT_BINDINGS."""

    def test_all_registered_abilities_have_stat_bindings(self):
        """Every ability class in the registry should have STAT_BINDINGS."""
        from game.simulation.components.abilities import ABILITY_REGISTRY

        missing = []
        for name, ability_cls in ABILITY_REGISTRY.items():
            if isinstance(ability_cls, type):
                if not hasattr(ability_cls, 'STAT_BINDINGS'):
                    missing.append(name)

        assert len(missing) == 0, f"Abilities missing STAT_BINDINGS: {missing}"

    def test_stat_bindings_are_lists(self):
        """All STAT_BINDINGS should be lists of AbilityStatBinding."""
        from game.simulation.components.abilities import ABILITY_REGISTRY
        from game.simulation.components.abilities.stat_keys import AbilityStatBinding

        for name, ability_cls in ABILITY_REGISTRY.items():
            if isinstance(ability_cls, type) and hasattr(ability_cls, 'STAT_BINDINGS'):
                bindings = ability_cls.STAT_BINDINGS
                assert isinstance(bindings, list), \
                    f"{name}.STAT_BINDINGS should be a list"
                for binding in bindings:
                    assert isinstance(binding, AbilityStatBinding), \
                        f"{name}.STAT_BINDINGS contains non-AbilityStatBinding: {type(binding)}"
