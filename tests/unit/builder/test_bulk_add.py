from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component
from game.core.constants import LayerType
from game.simulation.components.component_constants import ComponentStatus


class TestBulkAdd:

    def test_bulk_add_success(self, fresh_registries):
        """Test adding multiple components in bulk."""
        ship = Ship("Test Ship", 0, 0, (255, 255, 255), registries=fresh_registries)
        ship._initialize_layers()  # Ensure layers exist

        # Mock component
        comp_data = {
            "id": "armor_std",
            "name": "Standard Armor",
            "type": "Armor",
            "mass": 10,
            "hp": 100,
            # allowed_layers removed
            "major_classification": "Armor"
        }
        comp = Component(comp_data, registries=fresh_registries)

        count = 10
        ship.add_components_bulk(comp, LayerType.ARMOR, count)

        components = ship.layers[LayerType.ARMOR].components
        assert len(components) == 10
        # add_components_bulk clones each instance, so identity differs but the
        # clone must preserve the source component's id and classification —
        # otherwise the test could pass with the wrong component in place.
        for clone in components:
            assert clone is not comp  # cloned, not aliased
            assert clone.id == comp.id == "armor_std"
            assert clone.major_classification == "Armor"
        assert ship.current_mass == 100  # 10 * 10
