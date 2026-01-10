import pytest
from unittest.mock import MagicMock, patch
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import Component, Modifier
from ui.builder.stats_config import get_crew_required

class TestBug01CrewDelay:
    
    @pytest.fixture
    def ship(self):
        return Ship("Test Ship", 0, 0, (255, 255, 255))

    def test_crew_stat_update_on_modifier_change(self, ship):
        """
        Reproduction test for BUG-01: Crew required stat update delay.
        We verify that changing a modifier (Mount Size) immediately updates the 
        CrewRequired ability total after recalculation.
        """
        # 1. Setup a component with CrewRequired
        # Component expects a dictionary
        comp_data = {
            "id": "test_weapon",
            "name": "Test Weapon",
            "mass": 10,
            "hp": 100,
            "type": "Weapon",
            "abilities": {
                "CrewRequired": 5 # Base crew
            },
            "allowed_layers": ["OUTER", "INNER"] # Needed if we validated, but Component might ignore
        }
        
        # Create Component
        comp = Component(comp_data)
        
        # Add to ship
        ship.add_component(comp, LayerType.OUTER)
        ship.recalculate_stats()
        
        # 2. Verify Initial Crew
        initial_crew = get_crew_required(ship)
        # Should be 5
        assert initial_crew == 5.0, f"Initial crew should be 5.0, got {initial_crew}"
        
        # 3. Add Modifier (Mount Size)
        # We need to simulate the 'mount_size' modifier effect.
        # In the real app, this is likely an ApplicationModifier applied to the component.
        
        # Let's inspect how abilities change.
        # We'll rely on the fact that Component.recalculate_stats() applies modifiers.
        
        # Mocking get_ability_value IS A SHORTCUT, but if the bug is cache invalidation, it's valid.
        # However, to be more robust, let's try to actually USE the modifier system if possible.
        # But 'CrewRequired' isn't standard in `_calculate_modifier_stats` unless we add 'crew_req_mult'.
        # I saw 'crew_req_mult' in component.py line 374! 
        # So we can use a real modifier that targets 'crew_req_mult'.
        
        mod_data = {
            "id": "mount_size_test",
            "name": "Mount Size",
            "type": "linear",
            "effects": {
                "crew_req_mult": 1.0 # +100% = Double crew req
            }
        }
        
        mod_def = Modifier(mod_data)
        
        # Apply Modifier
        # Component.add_modifier requires logic to check registry. 
        # Let's manually inject it to avoid registry dependency issues in test.
        # component.py:277 add_modifier checks REGISTRY.
        # We can mock the registry or just manually append to self.modifiers and call recalculate.
        
        from game.simulation.components.component import ApplicationModifier
        app_mod = ApplicationModifier(mod_def, 2.0) # Value doesn't matter for linear unless formula uses it? 
        # Modifier.create_modifier uses value. 
        # apply_modifier_effects in modifiers.py uses it.
        # For simplicity, let's assume effects are static in this test or handled correctly.
        
        comp.modifiers.append(app_mod)
        
        # Trigger Recalculate (The Step being tested)
        # We must call recalculate on the component AND the ship.
        # The Bug Report says "Crew required stat doesn't update immediately".
        # This implies the UI is reading stale data.
        
        comp.recalculate_stats() # Component level
        ship.recalculate_stats() # Ship level aggregation
        
        # Verify Update
        new_crew = get_crew_required(ship)
        
        # 'crew_req_mult' in component.py is calculated but IS IT APPLIED to the ability?
        # component.py:411 iterates abilities.
        # CrewRequired likely is NOT a ResourceConsumption/Storage/Generation class instance?
        # If it's just a value in `comp.abilities['CrewRequired']`, it might NOT be updated!
        
        # This test will reveal if the component logic actually updates the ability value.
        
        assert new_crew == 10.0, f"Crew should update to 10.0, got {new_crew}"
