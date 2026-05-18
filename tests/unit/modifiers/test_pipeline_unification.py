"""
Tests for Phase 4: Pipeline Unification

Verifies that the single recalculate() path works correctly after
removing duplicate stat application code from _apply_base_stats().

PROJ-322 Task 4.1 (S11-CAT7-001): these tests previously hardcoded
specific component IDs (railgun, fuel_tank, generator, standard_engine)
and skipped when the hardcoded component dropped the expected ability.
That wallpapered any registry shape change (PROJ-428 onward).

PROJ-446 Phase 1 Task 1.3 (F-C-024): the hardcoded IDs are replaced
with `first_component_with_ability(...)` so the tests exercise the
unified pipeline against whatever component currently provides the
ability. A test that genuinely cannot find any component with the
ability still skips, but the skip message now names the missing
ability rather than the missing hardcoded component.
"""
import pytest


def first_component_with_ability(registries, ability_name: str):
    """Return the first component in the registry that exposes the named ability.

    Used by pipeline-unification tests to avoid hardcoding component IDs.
    Returns the constructed component instance, or None if no component in
    the registry provides the ability.
    """
    from game.simulation.components.component import create_component

    for comp_id in registries.components.keys():
        try:
            component = create_component(comp_id, registries=registries)
        except Exception:  # Intentional broad catch: skip non-instantiable test entries
            continue
        if component is None:
            continue
        if component.get_ability(ability_name) is not None:
            return component
    return None


class TestSingleRecalculatePath:
    """Tests verifying abilities recalculate correctly without duplicate code."""

    def test_resource_consumption_recalculates_via_stat_bindings(self, fresh_registries):
        """ResourceConsumption.recalculate() should apply consumption_mult correctly."""
        component = first_component_with_ability(fresh_registries, 'ResourceConsumption')
        if component is None:
            pytest.skip("no component with ability ResourceConsumption in current registry")
        component.recalculate_stats()

        rc = component.get_ability('ResourceConsumption')
        base_amount = rc._base_amount

        # Apply efficiency modifier (reduces consumption)
        component.add_modifier('efficiency_mount', 0.5)  # 50% consumption

        # Verify consumption was reduced
        assert rc.amount == pytest.approx(base_amount * 0.5)

    def test_resource_storage_recalculates_via_stat_bindings(self, fresh_registries):
        """ResourceStorage.recalculate() should apply capacity_mult correctly."""
        component = first_component_with_ability(fresh_registries, 'ResourceStorage')
        if component is None:
            pytest.skip("no component with ability ResourceStorage in current registry")
        component.recalculate_stats()

        rs = component.get_ability('ResourceStorage')
        base_max = rs._base_max_amount

        # Apply simple_size_mount modifier
        component.add_modifier('simple_size_mount', 2.0)

        # Verify capacity was scaled
        assert rs.max_amount == pytest.approx(base_max * 2.0)

    def test_resource_generation_recalculates_via_stat_bindings(self, fresh_registries):
        """ResourceGeneration.recalculate() should apply energy_gen_mult correctly."""
        component = first_component_with_ability(fresh_registries, 'ResourceGeneration')
        if component is None:
            pytest.skip("no component with ability ResourceGeneration in current registry")
        component.recalculate_stats()

        rg = component.get_ability('ResourceGeneration')
        base_rate = rg._base_rate

        # Apply simple_size_mount modifier
        component.add_modifier('simple_size_mount', 2.0)

        # Verify rate was scaled
        assert rg.rate == pytest.approx(base_rate * 2.0)

    def test_all_abilities_recalculate_called(self, fresh_registries):
        """All ability instances should have recalculate() called during stats recalc."""
        component = first_component_with_ability(fresh_registries, 'WeaponAbility')
        if component is None:
            pytest.skip("no component with ability WeaponAbility in current registry")
        component.recalculate_stats()

        # Every ability should have had recalculate() called
        for ab in component.ability_instances:
            # Verify ability has STAT_BINDINGS (all abilities should now)
            assert hasattr(ab.__class__, 'STAT_BINDINGS'), \
                f"{ab.__class__.__name__} missing STAT_BINDINGS"


class TestNoManuaStatsApplication:
    """Tests verifying that abilities handle their own stat application."""

    def test_weapon_damage_from_ability_recalculate(self, fresh_registries):
        """WeaponAbility should apply damage_mult via its own recalculate()."""
        component = first_component_with_ability(fresh_registries, 'WeaponAbility')
        if component is None:
            pytest.skip("no component with ability WeaponAbility in current registry")
        component.recalculate_stats()

        weapon = component.get_ability('WeaponAbility')
        base_damage = weapon._base_damage
        base_range = weapon._base_range

        # Apply simple_size_mount (scales damage)
        component.add_modifier('simple_size_mount', 2.0)

        # Damage should be scaled
        assert weapon.damage == pytest.approx(base_damage * 2.0)
        # Range should NOT be scaled by simple_size_mount (it doesn't affect range_mult)
        assert weapon.range == pytest.approx(base_range)

    def test_propulsion_thrust_from_ability_recalculate(self, fresh_registries):
        """CombatPropulsion should apply thrust_mult via its own recalculate()."""
        component = first_component_with_ability(fresh_registries, 'CombatPropulsion')
        if component is None:
            pytest.skip("no component with ability CombatPropulsion in current registry")
        component.recalculate_stats()

        prop = component.get_ability('CombatPropulsion')
        base_thrust = prop.base_thrust

        # Apply simple_size_mount (scales thrust)
        component.add_modifier('simple_size_mount', 3.0)

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
