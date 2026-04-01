"""
Tests for DamageCalculator - extracted damage logic from ShipCombatEngine.

Follows TDD: Tests written first, then implementation.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.core.math import Vector2
from game.core.constants import LayerType
from game.simulation.entities.layer_data import LayerData


class TestDamageCalculatorCreation:
    """Tests for DamageCalculator instantiation."""

    def test_damage_calculator_can_be_created(self):
        """DamageCalculator can be instantiated."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()
        assert calculator is not None

    def test_damage_calculator_has_required_methods(self):
        """DamageCalculator has all required public methods."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()
        assert hasattr(calculator, 'apply_damage')


class TestEmissiveArmorReduction:
    """Tests for emissive armor damage reduction."""

    def test_emissive_armor_reduces_damage(self):
        """Emissive armor reduces overflow damage after shields."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 5
        ship.shield_regenerating_armor = 0
        ship.current_shields = 0  # No shields so emissive is tested
        ship.max_shields = 0
        ship.layers = {
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[]),
        }
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # Pipeline: shields=0 (skip), emissive reduces 10-5=5, SRA=0 (skip), hull=empty
        # 5 remaining damage passes through empty layers
        calculator.apply_damage(ship, 10)

        # Shields unchanged (were 0)
        assert ship.current_shields == 0

    def test_emissive_armor_blocks_all_when_greater(self):
        """Emissive armor blocks all overflow when greater than remaining damage."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 10
        ship.shield_regenerating_armor = 0
        ship.current_shields = 0  # No shields so emissive is tested
        ship.max_shields = 0
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # Pipeline: shields=0 (skip), emissive blocks all 5 (10>5), early return
        calculator.apply_damage(ship, 5)

        # No damage reached hull, methods not called
        ship.recalculate_stats.assert_not_called()
        ship.update_derelict_status.assert_not_called()
        assert ship.current_shields == 0


class TestShieldRegeneratingArmorAbsorption:
    """Tests for shield regenerating armor absorption and shield recharge."""

    def test_shield_regenerating_armor_absorbs_and_recharges(self):
        """Crystalline armor absorbs overflow and recharges shields."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 10
        ship.current_shields = 5  # Low shields so damage overflows to SRA
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 20 damage:
        # Shields absorb 5: remaining=15, shields=0
        # Emissive=0 (skip)
        # SRA absorbs min(10,15)=10: remaining=5, shields+=10 -> shields=10
        # No hull layers, remaining=5
        # Callbacks called (5 < 20)
        calculator.apply_damage(ship, 20)

        assert ship.current_shields == 10

    def test_shield_regenerating_armor_caps_shield_recharge(self):
        """Crystalline armor shield recharge is capped at max shields."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 20
        ship.current_shields = 5  # Low shields so damage overflows to SRA
        ship.max_shields = 10  # Low max to test cap
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 30 damage:
        # Shields absorb 5: remaining=25, shields=0
        # Emissive=0 (skip)
        # SRA absorbs min(20,25)=20: remaining=5, shields += 20 -> 20, capped at 10
        # No hull layers
        calculator.apply_damage(ship, 30)

        assert ship.current_shields == 10


class TestShieldAbsorption:
    """Tests for shield damage absorption."""

    def test_shields_absorb_before_layers(self):
        """Shields absorb damage before hull layers."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 0
        ship.current_shields = 100
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        calculator.apply_damage(ship, 50)

        assert ship.current_shields == 50

    def test_shields_fully_depleted(self):
        """Shields can be fully depleted."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 0
        ship.current_shields = 30
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 50 damage, shields only 30
        calculator.apply_damage(ship, 50)

        assert ship.current_shields == 0


class TestLayerDamage:
    """Tests for hull layer damage application."""

    def test_damage_layers_by_radius(self):
        """Damage is applied to layers ordered by radius (outermost first)."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        # Create components with HP
        outer_comp = MagicMock()
        outer_comp.current_hp = 50
        outer_comp.max_hp = 50
        outer_comp.take_damage = MagicMock()

        inner_comp = MagicMock()
        inner_comp.current_hp = 50
        inner_comp.max_hp = 50
        inner_comp.take_damage = MagicMock()

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 0
        ship.current_shields = 0  # No shields
        ship.max_shields = 0
        ship.layers = {
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[outer_comp]),
            LayerType.INNER: LayerData(radius_pct=0.4, components=[inner_comp]),
        }
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # Apply 30 damage - should hit outer layer first
        calculator.apply_damage(ship, 30)

        # Outer component should have been damaged
        outer_comp.take_damage.assert_called()

    def test_damage_spreads_to_inner_layers(self):
        """Damage spreads to inner layers when outer is destroyed."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        # Outer component with low HP
        outer_comp = MagicMock()
        outer_comp.current_hp = 10
        outer_comp.max_hp = 50

        def outer_take_damage(amount):
            outer_comp.current_hp = max(0, outer_comp.current_hp - amount)

        outer_comp.take_damage = outer_take_damage

        # Inner component
        inner_comp = MagicMock()
        inner_comp.current_hp = 50
        inner_comp.max_hp = 50

        def inner_take_damage(amount):
            inner_comp.current_hp = max(0, inner_comp.current_hp - amount)

        inner_comp.take_damage = inner_take_damage

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 0
        ship.current_shields = 0
        ship.max_shields = 0
        ship.layers = {
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[outer_comp]),
            LayerType.INNER: LayerData(radius_pct=0.4, components=[inner_comp]),
        }
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # Apply 30 damage
        # Outer has 10 HP, absorbs 10, leaving 20 damage
        # Inner absorbs remaining 20
        calculator.apply_damage(ship, 30)

        assert outer_comp.current_hp == 0
        assert inner_comp.current_hp == 30  # 50 - 20 = 30


class TestDeadShipHandling:
    """Tests for dead ship damage handling."""

    def test_damage_skipped_when_dead(self):
        """Damage is not applied to dead ships."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        ship = MagicMock()
        ship.is_alive = False
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        calculator.apply_damage(ship, 100)

        ship.recalculate_stats.assert_not_called()
        ship.update_derelict_status.assert_not_called()


class TestDamageCallbacks:
    """Tests for post-damage callbacks."""

    def test_recalculate_stats_called_on_damage(self):
        """recalculate_stats is called when damage reaches hull layers."""
        from game.simulation.combat.damage_calculator import DamageCalculator

        calculator = DamageCalculator()

        comp = MagicMock()
        comp.current_hp = 100
        comp.max_hp = 100
        def take_damage(amount):
            comp.current_hp = max(0, comp.current_hp - amount)
        comp.take_damage = take_damage

        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 0
        ship.current_shields = 0  # No shields so damage reaches hull
        ship.max_shields = 0
        ship.layers = {
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[comp])
        }
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        calculator.apply_damage(ship, 50)

        ship.recalculate_stats.assert_called_once()
        ship.update_derelict_status.assert_called_once()


# =============================================================================
# PROJ-118 Phase 2: _damage_layer weighted distribution tests
# =============================================================================


@pytest.fixture
def damage_calculator():
    """Create a DamageCalculator instance for testing."""
    from game.simulation.combat.damage_calculator import DamageCalculator
    return DamageCalculator()


@pytest.fixture
def mock_component():
    """Factory fixture for creating mock components with configurable HP."""
    def _create(current_hp: float, max_hp: float = None):
        if max_hp is None:
            max_hp = current_hp
        comp = MagicMock()
        comp.current_hp = current_hp
        comp.max_hp = max_hp

        def take_damage(amount):
            comp.current_hp = max(0, comp.current_hp - amount)

        comp.take_damage = take_damage
        return comp
    return _create


@pytest.fixture
def mock_ship():
    """Factory fixture for creating mock ships with configurable layers."""
    def _create(layers: dict):
        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 0
        ship.current_shields = 0
        ship.max_shields = 0
        ship.layers = layers
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()
        return ship
    return _create


class TestDamageLayerWeightedDistribution:
    """Tests for _damage_layer weighted random selection based on component HP."""

    def test_single_component_receives_all_damage(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Single component in layer receives all damage."""
        comp = mock_component(current_hp=100)
        ship = mock_ship({
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[comp])
        })

        damage_calculator.apply_damage(ship, 30)

        assert comp.current_hp == 70

    def test_weighted_selection_favors_higher_hp_components(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Components with higher HP are more likely to be selected.

        Uses statistical verification over many runs to validate weighting.
        """
        import random
        random.seed(42)  # Reproducible test

        # Track hit counts over many damage applications
        hit_counts = {'high_hp': 0, 'low_hp': 0}

        for _ in range(100):
            # Fresh components each iteration
            high_hp_comp = mock_component(current_hp=90)
            low_hp_comp = mock_component(current_hp=10)

            ship = mock_ship({
                LayerType.OUTER: LayerData(
                    radius_pct=0.8,
                    components=[high_hp_comp, low_hp_comp]
                )
            })

            # Apply small damage to force single selection
            damage_calculator.apply_damage(ship, 5)

            # Check which was hit
            if high_hp_comp.current_hp < 90:
                hit_counts['high_hp'] += 1
            if low_hp_comp.current_hp < 10:
                hit_counts['low_hp'] += 1

        # With 90:10 weight ratio, high_hp should be hit ~90% of the time
        # Allow tolerance for randomness
        assert hit_counts['high_hp'] > hit_counts['low_hp']
        assert hit_counts['high_hp'] >= 70  # Should be ~90, allow margin

    def test_equal_hp_gives_equal_selection_probability(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Components with equal HP have equal selection probability.

        Uses statistical verification over many runs.
        """
        import random
        random.seed(42)

        hit_counts = {'comp_a': 0, 'comp_b': 0}

        for _ in range(200):
            comp_a = mock_component(current_hp=50)
            comp_b = mock_component(current_hp=50)

            ship = mock_ship({
                LayerType.OUTER: LayerData(
                    radius_pct=0.8,
                    components=[comp_a, comp_b]
                )
            })

            damage_calculator.apply_damage(ship, 5)

            if comp_a.current_hp < 50:
                hit_counts['comp_a'] += 1
            if comp_b.current_hp < 50:
                hit_counts['comp_b'] += 1

        # With equal weights, should be roughly 50/50
        # Allow 20% tolerance
        total = hit_counts['comp_a'] + hit_counts['comp_b']
        ratio = hit_counts['comp_a'] / total
        assert 0.30 <= ratio <= 0.70

    def test_destroyed_component_not_selected(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Components with 0 HP are not selected for damage."""
        destroyed_comp = mock_component(current_hp=0, max_hp=50)
        alive_comp = mock_component(current_hp=50)

        ship = mock_ship({
            LayerType.OUTER: LayerData(
                radius_pct=0.8,
                components=[destroyed_comp, alive_comp]
            )
        })

        damage_calculator.apply_damage(ship, 20)

        # Dead component stays at 0
        assert destroyed_comp.current_hp == 0
        # Alive component takes all damage
        assert alive_comp.current_hp == 30

    def test_damage_continues_until_fully_applied(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Damage continues until fully absorbed or no targets remain."""
        comp1 = mock_component(current_hp=20)
        comp2 = mock_component(current_hp=30)

        ship = mock_ship({
            LayerType.OUTER: LayerData(
                radius_pct=0.8,
                components=[comp1, comp2]
            )
        })

        # Apply 50 damage - exactly total HP of both components
        damage_calculator.apply_damage(ship, 50)

        # Both should be destroyed
        assert comp1.current_hp == 0
        assert comp2.current_hp == 0


class TestDamageLayerEdgeCases:
    """Edge cases for _damage_layer method."""

    def test_empty_layer_returns_full_damage(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Empty layer returns all damage to pass to next layer."""
        inner_comp = mock_component(current_hp=100)

        ship = mock_ship({
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[]),
            LayerType.INNER: LayerData(
                radius_pct=0.4,
                components=[inner_comp]
            )
        })

        damage_calculator.apply_damage(ship, 30)

        # Inner component should receive all damage since outer is empty
        assert inner_comp.current_hp == 70

    def test_all_components_destroyed_passes_remaining_damage(
        self, damage_calculator, mock_component, mock_ship
    ):
        """When all components are destroyed, remaining damage passes through."""
        outer_comp = mock_component(current_hp=20)
        inner_comp = mock_component(current_hp=100)

        ship = mock_ship({
            LayerType.OUTER: LayerData(
                radius_pct=0.8,
                components=[outer_comp]
            ),
            LayerType.INNER: LayerData(
                radius_pct=0.4,
                components=[inner_comp]
            )
        })

        # Apply 50 damage - outer has 20, should pass 30 to inner
        damage_calculator.apply_damage(ship, 50)

        assert outer_comp.current_hp == 0
        assert inner_comp.current_hp == 70

    def test_layer_with_all_dead_components(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Layer with all dead components passes damage through."""
        dead_comp1 = mock_component(current_hp=0, max_hp=50)
        dead_comp2 = mock_component(current_hp=0, max_hp=50)
        alive_comp = mock_component(current_hp=100)

        ship = mock_ship({
            LayerType.OUTER: LayerData(
                radius_pct=0.8,
                components=[dead_comp1, dead_comp2]
            ),
            LayerType.INNER: LayerData(
                radius_pct=0.4,
                components=[alive_comp]
            )
        })

        damage_calculator.apply_damage(ship, 40)

        # Dead components stay dead
        assert dead_comp1.current_hp == 0
        assert dead_comp2.current_hp == 0
        # Alive component takes all damage
        assert alive_comp.current_hp == 60

    def test_multiple_components_some_destroyed_mid_attack(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Components destroyed mid-attack are excluded from further selection."""
        import random
        random.seed(123)

        # One weak, one strong
        weak_comp = mock_component(current_hp=5)
        strong_comp = mock_component(current_hp=100)

        ship = mock_ship({
            LayerType.OUTER: LayerData(
                radius_pct=0.8,
                components=[weak_comp, strong_comp]
            )
        })

        # Apply enough damage to destroy weak and hit strong
        damage_calculator.apply_damage(ship, 50)

        # Total HP = 105, damage = 50, so 55 HP should remain
        total_remaining = weak_comp.current_hp + strong_comp.current_hp
        assert total_remaining == 55


class TestDamageLayerBoundaryConditions:
    """Boundary conditions for _damage_layer method."""

    def test_zero_damage_does_nothing(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Zero damage leaves all components unchanged."""
        comp = mock_component(current_hp=50)

        ship = mock_ship({
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[comp])
        })

        damage_calculator.apply_damage(ship, 0)

        assert comp.current_hp == 50

    def test_damage_exactly_equals_component_hp(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Damage exactly equal to component HP destroys it exactly."""
        comp = mock_component(current_hp=50)

        ship = mock_ship({
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[comp])
        })

        damage_calculator.apply_damage(ship, 50)

        assert comp.current_hp == 0

    def test_damage_exactly_equals_total_layer_hp(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Damage exactly equal to total layer HP destroys all components."""
        comp1 = mock_component(current_hp=30)
        comp2 = mock_component(current_hp=20)

        ship = mock_ship({
            LayerType.OUTER: LayerData(
                radius_pct=0.8,
                components=[comp1, comp2]
            )
        })

        damage_calculator.apply_damage(ship, 50)

        assert comp1.current_hp == 0
        assert comp2.current_hp == 0

    def test_fractional_damage_applied_correctly(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Fractional damage values are applied correctly."""
        comp = mock_component(current_hp=100.0)

        ship = mock_ship({
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[comp])
        })

        damage_calculator.apply_damage(ship, 33.33)

        assert abs(comp.current_hp - 66.67) < 0.01

    def test_very_small_damage_applied(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Very small damage values are applied correctly."""
        comp = mock_component(current_hp=100.0)

        ship = mock_ship({
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[comp])
        })

        damage_calculator.apply_damage(ship, 0.001)

        assert abs(comp.current_hp - 99.999) < 0.0001

    def test_large_damage_exceeds_all_layers(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Large damage that exceeds all layers is handled gracefully."""
        comp1 = mock_component(current_hp=50)
        comp2 = mock_component(current_hp=50)

        ship = mock_ship({
            LayerType.OUTER: LayerData(
                radius_pct=0.8,
                components=[comp1]
            ),
            LayerType.INNER: LayerData(
                radius_pct=0.4,
                components=[comp2]
            )
        })

        # Apply 1000 damage - far exceeds total HP of 100
        damage_calculator.apply_damage(ship, 1000)

        assert comp1.current_hp == 0
        assert comp2.current_hp == 0

    def test_component_with_one_hp(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Component with exactly 1 HP is handled correctly."""
        comp = mock_component(current_hp=1)

        ship = mock_ship({
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[comp])
        })

        damage_calculator.apply_damage(ship, 1)

        assert comp.current_hp == 0

    def test_many_components_in_layer(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Many components in a single layer are handled correctly."""
        import random
        random.seed(42)

        # Create 10 components with varying HP
        components = [mock_component(current_hp=10 * (i + 1)) for i in range(10)]
        # Total HP = 10 + 20 + 30 + ... + 100 = 550

        ship = mock_ship({
            LayerType.OUTER: LayerData(
                radius_pct=0.8,
                components=components
            )
        })

        damage_calculator.apply_damage(ship, 200)

        # Total remaining HP should be 350
        total_remaining = sum(c.current_hp for c in components)
        assert total_remaining == 350


class TestDamageLayerDirectMethod:
    """Direct tests for _damage_layer method (not through apply_damage)."""

    def test_damage_layer_returns_remaining_damage(self, damage_calculator):
        """_damage_layer returns remaining damage after absorption."""
        comp = MagicMock()
        comp.current_hp = 30
        comp.max_hp = 30

        def take_damage(amount):
            comp.current_hp = max(0, comp.current_hp - amount)
        comp.take_damage = take_damage

        ship = MagicMock()
        ship.layers = {
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[comp])
        }

        # Apply 50 damage to layer with 30 HP
        remaining = damage_calculator._damage_layer(ship, LayerType.OUTER, 50)

        assert remaining == 20
        assert comp.current_hp == 0

    def test_damage_layer_returns_zero_when_fully_absorbed(
        self, damage_calculator
    ):
        """_damage_layer returns 0 when all damage is absorbed."""
        comp = MagicMock()
        comp.current_hp = 100
        comp.max_hp = 100

        def take_damage(amount):
            comp.current_hp = max(0, comp.current_hp - amount)
        comp.take_damage = take_damage

        ship = MagicMock()
        ship.layers = {
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[comp])
        }

        # Apply 30 damage to layer with 100 HP
        remaining = damage_calculator._damage_layer(ship, LayerType.OUTER, 30)

        assert remaining == 0
        assert comp.current_hp == 70

    def test_damage_layer_empty_returns_full_damage(self, damage_calculator):
        """_damage_layer with empty component list returns full damage."""
        ship = MagicMock()
        ship.layers = {
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[])
        }

        remaining = damage_calculator._damage_layer(ship, LayerType.OUTER, 100)

        assert remaining == 100

    def test_damage_layer_all_dead_returns_full_damage(self, damage_calculator):
        """_damage_layer with all dead components returns full damage."""
        dead_comp = MagicMock()
        dead_comp.current_hp = 0
        dead_comp.max_hp = 50

        ship = MagicMock()
        ship.layers = {
            LayerType.OUTER: LayerData(
                radius_pct=0.8,
                components=[dead_comp]
            )
        }

        remaining = damage_calculator._damage_layer(ship, LayerType.OUTER, 100)

        assert remaining == 100


# =============================================================================
# PROJ-118 Phase 2: Additional Edge Cases and Combined Scenarios
# =============================================================================


class TestCombinedArmorScenarios:
    """Tests for combined emissive and shield regenerating armor scenarios."""

    def test_emissive_then_shield_regenerating_armor(self, damage_calculator, mock_ship):
        """Shields absorb first, then emissive reduces overflow, then SRA absorbs rest."""
        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 10  # Reduces 10 flat
        ship.shield_regenerating_armor = 15  # Absorbs up to 15
        ship.current_shields = 5  # Low shields so damage overflows
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 30 damage:
        # Shields absorb 5: remaining=25, shields=0
        # Emissive reduces: 25-10=15 remaining
        # SRA absorbs min(15,15)=15: remaining=0, shields+=15 -> shields=15
        damage_calculator.apply_damage(ship, 30)

        assert ship.current_shields == 15

    def test_emissive_blocks_before_crystalline_activates(
        self, damage_calculator, mock_ship
    ):
        """If emissive blocks all overflow after shields, crystalline doesn't activate."""
        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 20
        ship.shield_regenerating_armor = 10
        ship.current_shields = 0  # No shields so emissive is tested
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 15 damage:
        # Shields=0 (skip)
        # Emissive blocks all 15 (20>15), early return
        # Crystalline never activated
        damage_calculator.apply_damage(ship, 15)

        # Shields unchanged - crystalline never activated
        assert ship.current_shields == 0


class TestShieldRegeneratingArmorEdgeCases:
    """Additional edge cases for shield regenerating armor."""

    def test_shield_regenerating_armor_with_zero_max_shields(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Crystalline armor works but can't recharge shields with zero max."""
        comp = mock_component(current_hp=100)
        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 20
        ship.current_shields = 0
        ship.max_shields = 0  # No shields equipped
        ship.layers = {
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[comp])
        }
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 50 damage:
        # - Crystalline absorbs 20 (can't recharge shields since max=0)
        # - Remaining 30 hits hull
        damage_calculator.apply_damage(ship, 50)

        assert ship.current_shields == 0
        assert comp.current_hp == 70

    def test_shield_regenerating_armor_partial_absorption(
        self, damage_calculator, mock_ship
    ):
        """Crystalline armor absorbs less than full capacity with small overflow."""
        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 50  # Large capacity
        ship.current_shields = 0  # No shields so damage reaches SRA
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 30 damage:
        # Shields=0 (skip)
        # Emissive=0 (skip)
        # SRA absorbs min(50,30)=30: remaining=0, shields+=30 -> shields=30
        damage_calculator.apply_damage(ship, 30)

        assert ship.current_shields == 30


class TestNegativeDamageHandling:
    """Tests for negative damage edge cases."""

    def test_negative_damage_treated_as_no_damage(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Negative damage values don't heal or cause errors."""
        comp = mock_component(current_hp=50)
        ship = mock_ship({
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[comp])
        })

        # Negative damage - should not modify anything
        damage_calculator.apply_damage(ship, -10)

        assert comp.current_hp == 50
        ship.recalculate_stats.assert_not_called()


class TestMultipleLayerScenarios:
    """Tests for ships with three or more layers."""

    def test_three_layer_damage_propagation(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Damage propagates through three layers correctly."""
        outer = mock_component(current_hp=20)
        middle = mock_component(current_hp=30)
        inner = mock_component(current_hp=50)

        ship = mock_ship({
            LayerType.OUTER: LayerData(radius_pct=0.9, components=[outer]),
            LayerType.ARMOR: LayerData(radius_pct=0.6, components=[middle]),
            LayerType.INNER: LayerData(radius_pct=0.3, components=[inner]),
        })

        # 70 damage:
        # - Outer absorbs 20, remaining 50
        # - Middle absorbs 30, remaining 20
        # - Inner absorbs 20, remaining 0
        damage_calculator.apply_damage(ship, 70)

        assert outer.current_hp == 0
        assert middle.current_hp == 0
        assert inner.current_hp == 30

    def test_damage_stops_when_absorbed_in_middle_layer(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Damage stops propagating when fully absorbed mid-chain."""
        outer = mock_component(current_hp=20)
        middle = mock_component(current_hp=100)  # Large HP
        inner = mock_component(current_hp=50)

        ship = mock_ship({
            LayerType.OUTER: LayerData(radius_pct=0.9, components=[outer]),
            LayerType.ARMOR: LayerData(radius_pct=0.6, components=[middle]),
            LayerType.INNER: LayerData(radius_pct=0.3, components=[inner]),
        })

        # 50 damage:
        # - Outer absorbs 20, remaining 30
        # - Middle absorbs 30, remaining 0
        # - Inner untouched
        damage_calculator.apply_damage(ship, 50)

        assert outer.current_hp == 0
        assert middle.current_hp == 70
        assert inner.current_hp == 50  # Unchanged


class TestLayerSortingBehavior:
    """Tests to verify layers are processed in correct order."""

    def test_layers_sorted_by_radius_descending(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Layers are sorted by radius_pct descending (outermost first)."""
        # Add layers in non-sorted order
        layer_a = mock_component(current_hp=10)  # radius 0.5
        layer_b = mock_component(current_hp=10)  # radius 0.9 (outermost)
        layer_c = mock_component(current_hp=10)  # radius 0.2 (innermost)

        ship = mock_ship({
            LayerType.ARMOR: LayerData(radius_pct=0.5, components=[layer_a]),
            LayerType.OUTER: LayerData(radius_pct=0.9, components=[layer_b]),
            LayerType.INNER: LayerData(radius_pct=0.2, components=[layer_c]),
        })

        # 15 damage should hit outermost (B) first, then armor (A)
        damage_calculator.apply_damage(ship, 15)

        assert layer_b.current_hp == 0  # Outermost hit first
        assert layer_a.current_hp == 5  # Armor hit second
        assert layer_c.current_hp == 10  # Inner untouched


class TestShieldDamageEdgeCases:
    """Edge cases for shield damage absorption."""

    def test_shields_take_exact_remaining_damage(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Shields absorb exact remaining damage amount."""
        comp = mock_component(current_hp=100)
        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 0
        ship.current_shields = 25
        ship.max_shields = 100
        ship.layers = {
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[comp])
        }
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 25 damage exactly depletes shields
        damage_calculator.apply_damage(ship, 25)

        assert ship.current_shields == 0
        assert comp.current_hp == 100  # No hull damage

    def test_shields_overflow_damage_to_hull(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Damage exceeding shields overflows to hull."""
        comp = mock_component(current_hp=100)
        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 0
        ship.current_shields = 10
        ship.max_shields = 100
        ship.layers = {
            LayerType.OUTER: LayerData(radius_pct=0.8, components=[comp])
        }
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # 30 damage: 10 to shields, 20 to hull
        damage_calculator.apply_damage(ship, 30)

        assert ship.current_shields == 0
        assert comp.current_hp == 80


class TestDamageCallbackConditions:
    """Tests for when callbacks are and aren't called."""

    def test_callbacks_not_called_when_all_blocked(
        self, damage_calculator, mock_ship
    ):
        """No callbacks when all damage is blocked by armor."""
        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 100
        ship.shield_regenerating_armor = 0
        ship.current_shields = 50
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        damage_calculator.apply_damage(ship, 50)

        ship.recalculate_stats.assert_not_called()
        ship.update_derelict_status.assert_not_called()

    def test_callbacks_not_called_when_shields_absorb_all(
        self, damage_calculator, mock_ship
    ):
        """Callbacks NOT called when shields fully absorb damage (early return)."""
        ship = MagicMock()
        ship.is_alive = True
        ship.emissive_armor = 0
        ship.shield_regenerating_armor = 0
        ship.current_shields = 100
        ship.max_shields = 100
        ship.layers = {}
        ship.recalculate_stats = MagicMock()
        ship.update_derelict_status = MagicMock()

        # Shields absorb all 50, early return before callbacks
        damage_calculator.apply_damage(ship, 50)

        ship.recalculate_stats.assert_not_called()
        ship.update_derelict_status.assert_not_called()


class TestComponentDamageDistributionEdgeCases:
    """Edge cases for component damage distribution within layers."""

    def test_three_components_weighted_selection(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Three components with varying HP get weighted selection."""
        import random
        random.seed(42)

        # Track which component gets hit
        hit_counts = {'low': 0, 'med': 0, 'high': 0}

        for _ in range(100):
            low = mock_component(current_hp=10)
            med = mock_component(current_hp=50)
            high = mock_component(current_hp=100)

            ship = mock_ship({
                LayerType.OUTER: LayerData(
                    radius_pct=0.8,
                    components=[low, med, high]
                )
            })

            damage_calculator.apply_damage(ship, 5)

            if low.current_hp < 10:
                hit_counts['low'] += 1
            if med.current_hp < 50:
                hit_counts['med'] += 1
            if high.current_hp < 100:
                hit_counts['high'] += 1

        # High HP should be hit most often (weight 100/160)
        # Medium should be second (weight 50/160)
        # Low should be least (weight 10/160)
        assert hit_counts['high'] > hit_counts['med']
        assert hit_counts['med'] > hit_counts['low']

    def test_component_destroyed_mid_loop_excluded(
        self, damage_calculator, mock_component, mock_ship
    ):
        """Component destroyed during damage loop is excluded from further hits."""
        import random
        random.seed(999)

        # Create components that will be destroyed
        weak1 = mock_component(current_hp=3)
        weak2 = mock_component(current_hp=3)
        strong = mock_component(current_hp=100)

        ship = mock_ship({
            LayerType.OUTER: LayerData(
                radius_pct=0.8,
                components=[weak1, weak2, strong]
            )
        })

        # Apply 20 damage - will destroy weak components and hit strong
        damage_calculator.apply_damage(ship, 20)

        # Total HP was 106, damage was 20, remaining should be 86
        total_remaining = weak1.current_hp + weak2.current_hp + strong.current_hp
        assert total_remaining == 86
