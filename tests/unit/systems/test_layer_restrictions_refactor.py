from unittest.mock import MagicMock
from game.simulation.validation.ship_validator import LayerRestrictionDefinitionRule
from game.core.validation import ValidationResult
from game.simulation.components.component import Component
from game.core.constants import LayerType
from game.simulation.entities.layer_data import LayerData


class TestLayerRestrictionsRefactor:

    def setup_method(self):
        self.rule = LayerRestrictionDefinitionRule()
        self.ship = MagicMock()
        self.ship.layers = {
            LayerType.CORE: LayerData(restrictions=["block_classification:Weapons"]),
            LayerType.ARMOR: LayerData(restrictions=["allow_classification:Armor"]),
            LayerType.INNER: LayerData(restrictions=[])  # No restrictions
        }

    def create_mock_component(self, comp_id, classification, type_str):
        comp = MagicMock(spec=Component)
        comp.id = comp_id
        comp.data = {'major_classification': classification}
        comp.type_str = type_str
        return comp

    def test_block_classification(self):
        # CORE blocks Weapons
        weapon = self.create_mock_component("gun", "Weapons", "ProjectileWeapon")
        result = self.rule.validate(self.ship, weapon, LayerType.CORE)
        assert result.is_valid is False
        assert "Classification 'Weapons' blocked" in result.errors[0]

        # CORE should allow Engines (if not blocked) - checking partial block
        engine = self.create_mock_component("eng", "Engines", "Engine")
        result = self.rule.validate(self.ship, engine, LayerType.CORE)
        assert result.is_valid is True

    def test_allow_classification_only(self):
        # ARMOR layer allows ONLY Armor
        armor = self.create_mock_component("plate", "Armor", "Armor")
        result = self.rule.validate(self.ship, armor, LayerType.ARMOR)
        assert result.is_valid is True

        # Should reject weapon
        weapon = self.create_mock_component("gun", "Weapons", "ProjectileWeapon")
        result = self.rule.validate(self.ship, weapon, LayerType.ARMOR)
        assert result.is_valid is False
        assert "Layer restricts components" in result.errors[0]

    def test_no_restrictions(self):
        # INNER has no restrictions -> Allow All
        weapon = self.create_mock_component("gun", "Weapons", "ProjectileWeapon")
        result = self.rule.validate(self.ship, weapon, LayerType.INNER)
        assert result.is_valid is True

    def test_block_classification_armor(self):
        """BUG-116: block_classification:Armor must reject armor components
        in non-ARMOR layers (mirrors test_block_classification for the
        Armor classification)."""
        ship = MagicMock()
        ship.layers = {
            LayerType.CORE: LayerData(restrictions=["block_classification:Armor"]),
            LayerType.OUTER: LayerData(restrictions=["block_classification:Armor"]),
            LayerType.ARMOR: LayerData(restrictions=["allow_classification:Armor"]),
        }

        armor = self.create_mock_component("plate", "Armor", "Armor")

        for blocking_layer in (LayerType.CORE, LayerType.OUTER):
            result = self.rule.validate(ship, armor, blocking_layer)
            assert result.is_valid is False, (
                f"Armor must be blocked in {blocking_layer.name}"
            )
            assert "Classification 'Armor' blocked" in result.errors[0]

        # ARMOR layer should still accept armor
        result = self.rule.validate(ship, armor, LayerType.ARMOR)
        assert result.is_valid is True

        # Non-armor components must remain unaffected by the new block rule
        engine = self.create_mock_component("eng", "Engines", "Engine")
        result = self.rule.validate(ship, engine, LayerType.CORE)
        assert result.is_valid is True
