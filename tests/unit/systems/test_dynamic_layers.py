import pytest
import math

from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component
from game.core.constants import LayerType


class TestDynamicLayers:

    def test_fighter_layers(self, fresh_registries):
        """Fighter (Small) should have CORE and ARMOR only."""
        ship = Ship("Test Fighter", 0, 0, (255, 0, 0), ship_class="Fighter (Small)", registries=fresh_registries)

        assert LayerType.CORE in ship.layers
        assert LayerType.ARMOR in ship.layers
        # Should NOT have OUTER or INNER
        assert LayerType.OUTER not in ship.layers
        assert LayerType.INNER not in ship.layers

        # Check radii
        assert ship.layers[LayerType.CORE].radius_pct == pytest.approx(0.877, abs=0.001)
        assert ship.layers[LayerType.ARMOR].radius_pct == 1.0

    def test_satellite_layers(self, fresh_registries):
        """Satellite (Small) should have CORE, OUTER, ARMOR."""
        ship = Ship("Test Satellite", 0, 0, (255, 0, 0), ship_class="Satellite (Small)", registries=fresh_registries)

        assert LayerType.CORE in ship.layers
        assert LayerType.OUTER in ship.layers
        assert LayerType.ARMOR in ship.layers
        assert LayerType.INNER not in ship.layers

    def test_cruiser_layers(self, fresh_registries):
        """Cruiser should have all 4 layers."""
        ship = Ship("Test Cruiser", 0, 0, (255, 0, 0), ship_class="Cruiser", registries=fresh_registries)

        assert LayerType.CORE in ship.layers
        assert LayerType.INNER in ship.layers
        assert LayerType.OUTER in ship.layers
        assert LayerType.ARMOR in ship.layers

    def test_restriction_logic(self, fresh_registries):
        """Test that layer restrictions block components correctly."""
        # To test restrictions, we need a ship class that HAS a restriction.
        # But our current vehicleclasses.json doesn't have any explicit restriction strings added yet.
        # So we will mock one for this test instance.

        ship = Ship("Restricted Ship", 0, 0, (255, 0, 0), ship_class="Escort", registries=fresh_registries)
        # Add a fake restriction to OUTER layer
        ship.layers[LayerType.OUTER].restrictions.append("block_classification:Weapons")
        # Clear restrictions on CORE to ensure test isolation (since Escort now has default blocks)
        ship.layers[LayerType.CORE].restrictions = []

        # Create a mock Weapon component
        # We can simulate a component nicely
        weapon_data = {
            "id": "test_weapon",
            "name": "Test Weapon",
            "type": "Weapon",
            "mass": 10, "hp": 10,
            # allowed_layers removed
            "allowed_vehicle_types": ["Ship"],
            "major_classification": "Weapons"
        }
        weapon = Component(weapon_data, registries=fresh_registries)

        # Try to add to OUTER (should fail)
        success = ship.add_component(weapon, LayerType.OUTER)
        assert not success, "Should satisfy block_classification:Weapons restriction"

        # Try to add to CORE (should succeed if allowed)
        success = ship.add_component(weapon, LayerType.CORE)
        assert success, "Should allow in non-restricted layer"

    @pytest.mark.parametrize("ship_class,armor_id", [
        ("Escort",                     "armor_plate"),        # Capital_Escort
        ("Cruiser",                    "armor_plate"),        # Capital_Standard
        ("Battleship",                 "armor_plate"),        # Capital_Standard
        ("Fighter (Small)",            "mini_armor"),         # Fighter_Standard
        ("Satellite (Small)",          "armor_plate"),        # Satellite_Standard
        ("Planetary Complex (Tier 1)", "armor_plate"),        # Planetary_Complex
    ])
    def test_block_classification_armor_rejects_in_non_armor_layers(
        self, fresh_registries, ship_class, armor_id
    ):
        """BUG-116: armor components must be rejected by every non-ARMOR layer
        on every vehicle template, and accepted by ARMOR.

        Round-trip via ship.add_component to confirm the data fix in
        data/vehiclelayers.json (block_classification:Armor on CORE/INNER/OUTER)
        wires through the LayerRestrictionDefinitionRule end-to-end. Uses
        real armor components so allowed_vehicle_types is satisfied (Fighter
        templates use mini_armor; Capital/Satellite/Planetary use armor_plate).
        """
        from game.simulation.components.component import create_component

        ship = Ship(
            "Armor Restriction Test", 0, 0, (255, 0, 0),
            ship_class=ship_class, registries=fresh_registries,
        )

        for layer_type in ship.layers:
            if layer_type == LayerType.HULL:
                continue
            armor = create_component(armor_id, registries=fresh_registries)
            success = ship.add_component(armor, layer_type)
            if layer_type == LayerType.ARMOR:
                assert success, (
                    f"Armor must be accepted in ARMOR for {ship_class}"
                )
            else:
                assert not success, (
                    f"Armor must be rejected in {layer_type.name} for "
                    f"{ship_class} (block_classification:Armor missing?)"
                )
