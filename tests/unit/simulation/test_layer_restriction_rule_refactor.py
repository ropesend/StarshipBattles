"""
Tests for LayerRestrictionDefinitionRule refactoring (Phase 8, Task 8.2).
Verify that the refactored validate() method produces identical results.
"""
import pytest
import sys
from unittest.mock import MagicMock, patch


class TestLayerRestrictionRuleRefactor:
    """Test LayerRestrictionDefinitionRule helper methods after refactor."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Set up test fixtures."""
        self.modules_patcher = patch.dict(sys.modules, {
            'pygame': MagicMock(),
            'pygame.mixer': MagicMock(),
            'pygame.font': MagicMock()
        })
        self.modules_patcher.start()

        from game.simulation.ship_validator import LayerRestrictionDefinitionRule
        from game.core.constants import LayerType

        self.LayerRestrictionDefinitionRule = LayerRestrictionDefinitionRule
        self.LayerType = LayerType

        yield

        self.modules_patcher.stop()

    def _create_mock_ship(self, restrictions):
        """Create a mock ship with given layer restrictions."""
        ship = MagicMock()
        ship.layers = {
            self.LayerType.CORE: {
                'components': [],
                'restrictions': restrictions
            }
        }
        return ship

    def _create_mock_component(self, comp_id, classification=None, abilities=None):
        """Create a mock component."""
        comp = MagicMock()
        comp.id = comp_id
        comp.data = {'major_classification': classification} if classification else {}
        comp.abilities = abilities or {}

        def has_ability(name):
            return name in comp.abilities

        comp.has_ability = has_ability
        return comp

    def test_check_block_rules_exists(self):
        """Verify _check_block_rules method exists after refactor."""
        rule = self.LayerRestrictionDefinitionRule()
        assert hasattr(rule, '_check_block_rules')

    def test_check_allow_rules_exists(self):
        """Verify _check_allow_rules method exists after refactor."""
        rule = self.LayerRestrictionDefinitionRule()
        assert hasattr(rule, '_check_allow_rules')

    def test_block_classification_rule_blocks_matching_component(self):
        """Verify block_classification rule blocks components with matching classification."""
        restrictions = ['block_classification:Weapon']
        ship = self._create_mock_ship(restrictions)
        comp = self._create_mock_component('laser_1', classification='Weapon')

        rule = self.LayerRestrictionDefinitionRule()
        result = rule.validate(ship, comp, self.LayerType.CORE)

        assert result.is_valid is False
        assert any("blocked" in err.lower() for err in result.errors)

    def test_block_classification_rule_allows_non_matching_component(self):
        """Verify block_classification rule allows components with different classification."""
        restrictions = ['block_classification:Weapon']
        ship = self._create_mock_ship(restrictions)
        comp = self._create_mock_component('engine_1', classification='Propulsion')

        rule = self.LayerRestrictionDefinitionRule()
        result = rule.validate(ship, comp, self.LayerType.CORE)

        assert result.is_valid is True

    def test_block_id_rule_blocks_matching_component(self):
        """Verify block_id rule blocks components with matching ID."""
        restrictions = ['block_id:illegal_component']
        ship = self._create_mock_ship(restrictions)
        comp = self._create_mock_component('illegal_component')

        rule = self.LayerRestrictionDefinitionRule()
        result = rule.validate(ship, comp, self.LayerType.CORE)

        assert result.is_valid is False
        assert any("blocked" in err.lower() for err in result.errors)

    def test_deny_ability_rule_blocks_component_with_ability(self):
        """Verify deny_ability rule blocks components with the denied ability."""
        restrictions = ['deny_ability:WeaponAbility']
        ship = self._create_mock_ship(restrictions)
        comp = self._create_mock_component('weapon_1', abilities={'WeaponAbility': True})

        rule = self.LayerRestrictionDefinitionRule()
        result = rule.validate(ship, comp, self.LayerType.CORE)

        assert result.is_valid is False
        assert any("blocked" in err.lower() for err in result.errors)

    def test_allow_classification_accepts_matching_component(self):
        """Verify allow_classification rule accepts matching components."""
        restrictions = ['allow_classification:Propulsion']
        ship = self._create_mock_ship(restrictions)
        comp = self._create_mock_component('engine_1', classification='Propulsion')

        rule = self.LayerRestrictionDefinitionRule()
        result = rule.validate(ship, comp, self.LayerType.CORE)

        assert result.is_valid is True

    def test_allow_classification_rejects_non_matching_component(self):
        """Verify allow_classification rule rejects non-matching components."""
        restrictions = ['allow_classification:Propulsion']
        ship = self._create_mock_ship(restrictions)
        comp = self._create_mock_component('laser_1', classification='Weapon')

        rule = self.LayerRestrictionDefinitionRule()
        result = rule.validate(ship, comp, self.LayerType.CORE)

        assert result.is_valid is False

    def test_allow_id_accepts_matching_component(self):
        """Verify allow_id rule accepts matching components."""
        restrictions = ['allow_id:special_component']
        ship = self._create_mock_ship(restrictions)
        comp = self._create_mock_component('special_component')

        rule = self.LayerRestrictionDefinitionRule()
        result = rule.validate(ship, comp, self.LayerType.CORE)

        assert result.is_valid is True

    def test_allow_ability_accepts_component_with_ability(self):
        """Verify allow_ability rule accepts components with the ability."""
        restrictions = ['allow_ability:CombatPropulsion']
        ship = self._create_mock_ship(restrictions)
        comp = self._create_mock_component('engine_1', abilities={'CombatPropulsion': True})

        rule = self.LayerRestrictionDefinitionRule()
        result = rule.validate(ship, comp, self.LayerType.CORE)

        assert result.is_valid is True

    def test_hull_only_restriction_accepts_hull_components(self):
        """Verify HullOnly restriction accepts hull_ prefixed components."""
        restrictions = ['HullOnly']
        ship = self._create_mock_ship(restrictions)
        comp = self._create_mock_component('hull_standard')

        rule = self.LayerRestrictionDefinitionRule()
        result = rule.validate(ship, comp, self.LayerType.CORE)

        assert result.is_valid is True

    def test_hull_only_restriction_rejects_non_hull_components(self):
        """Verify HullOnly restriction rejects non-hull components."""
        restrictions = ['HullOnly']
        ship = self._create_mock_ship(restrictions)
        comp = self._create_mock_component('engine_1')

        rule = self.LayerRestrictionDefinitionRule()
        result = rule.validate(ship, comp, self.LayerType.CORE)

        assert result.is_valid is False

    def test_no_restrictions_allows_all_components(self):
        """Verify no restrictions means all components are allowed."""
        restrictions = []
        ship = self._create_mock_ship(restrictions)
        comp = self._create_mock_component('any_component', classification='Weapon')

        rule = self.LayerRestrictionDefinitionRule()
        result = rule.validate(ship, comp, self.LayerType.CORE)

        assert result.is_valid is True

    def test_combined_block_and_allow_rules(self):
        """Verify block rules take precedence over allow rules."""
        restrictions = [
            'allow_classification:Weapon',
            'block_id:banned_weapon'
        ]
        ship = self._create_mock_ship(restrictions)
        comp = self._create_mock_component('banned_weapon', classification='Weapon')

        rule = self.LayerRestrictionDefinitionRule()
        result = rule.validate(ship, comp, self.LayerType.CORE)

        # Should be blocked even though classification is allowed
        assert result.is_valid is False
