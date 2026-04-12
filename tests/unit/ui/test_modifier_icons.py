import pytest
from unittest.mock import MagicMock, patch
import pygame
import os
from game.ui.services.modifier_icon_service import ModifierIconService
from game.simulation.components.component_constants import Modifier, ApplicationModifier

class TestModifierIconLogic:

    @pytest.fixture(autouse=True)
    def setup_display(self):
        """Ensure pygame is ready for surface operations."""
        if not pygame.get_init():
            pygame.init()
        if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.NOFRAME)
        yield

    def test_detect_non_default_modifiers(self):
        # Setup mock modifier definition
        mod_def = MagicMock(spec=Modifier)
        mod_def.id = "hardened_mount"
        mod_def.default_val = 1.0
        
        # Default value -> should have same value as default_val
        app_mod_default = ApplicationModifier(mod_def, 1.0)
        assert app_mod_default.value == mod_def.default_val
        
        # Non-default value -> should have different value
        app_mod_modified = ApplicationModifier(mod_def, 1.5)
        assert app_mod_modified.value != mod_def.default_val

    def test_icon_service_caching(self):
        """Test that ModifierIconService caches loaded icons."""
        service = ModifierIconService(icon_size=26)
        
        # Create a real surface to return from mock
        test_surf = pygame.Surface((64, 64))
        
        with patch('pygame.image.load', return_value=test_surf) as mock_load:
            with patch('os.path.exists', return_value=True):
                # First call
                surf1 = service.get_icon("hardened_mount")
                assert surf1 is not None
                assert surf1.get_width() == 26
                assert mock_load.call_count == 1
                
                # Second call (should hit cache)
                surf2 = service.get_icon("hardened_mount")
                assert surf2 is surf1
                assert mock_load.call_count == 1

    def test_icon_mapping_exceptions(self):
        """Verify that mapping exceptions (like facing -> mod_facing_angle.png) work."""
        service = ModifierIconService(icon_size=26)
        
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch('pygame.image.load', return_value=pygame.Surface((64, 64))):
                # Standard ID
                service.get_icon("hardened_mount")
                called_path = mock_exists.call_args[0][0]
                assert "mod_hardened_mount.png" in called_path
                
                # Special mapping: facing -> mod_facing_angle.png
                service.get_icon("facing")
                called_path = mock_exists.call_args[0][0]
                assert "mod_facing_angle.png" in called_path

    def test_icon_fallback(self):
        """Verify that IDs not in explicit map still try a mod_{id}.png fallback."""
        service = ModifierIconService(icon_size=26)
        
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch('pygame.image.load', return_value=pygame.Surface((64, 64))):
                service.get_icon("something_new")
                called_path = mock_exists.call_args[0][0]
                assert "mod_something_new.png" in called_path

    def test_ui_item_icon_creation(self):
        """Verify that IndividualComponentItem creates the expected number of UIImage children."""
        from game.ui.screens.builder.structure_list_items import IndividualComponentItem
        from game.ui.screens.builder.panel_layout_config import ComponentItemContext, StructurePanelLayoutConfig
        
        # Setup mocks
        ctx = MagicMock(spec=ComponentItemContext)
        ctx.manager = MagicMock()
        ctx.container = MagicMock()
        ctx.width = 400
        ctx.sprite_mgr = MagicMock()
        ctx.sprite_mgr.get_sprite.return_value = pygame.Surface((64, 64))
        ctx.event_handler = MagicMock()
        ctx.config = StructurePanelLayoutConfig()
        
        # Mock modifier service
        ctx.modifier_icon_service = MagicMock(spec=ModifierIconService)
        ctx.modifier_icon_service.get_icon.return_value = pygame.Surface((26, 26))
        
        # Component with 2 modified parameters
        component = MagicMock()
        component.name = "Test Component"
        component.sprite_index = 0
        component.mass = 100
        
        mod1 = MagicMock()
        mod1.definition.id = "mod1"
        mod1.definition.name = "Mod 1"
        mod1.definition.default_val = 1.0
        mod1.value = 2.0  # Modified
        
        mod2 = MagicMock()
        mod2.definition.id = "mod2"
        mod2.definition.name = "Mod 2"
        mod2.definition.default_val = 0.0
        mod2.value = 0.0  # Default
        
        mod3 = MagicMock()
        mod3.definition.id = "mod3"
        mod3.definition.name = "Mod 3"
        mod3.definition.default_val = 5.0
        mod3.value = 10.0  # Modified
        
        component.modifiers = [mod1, mod2, mod3]
        
        # Patch UIPanel/UILabel/UIImage to avoid full initialization
        with patch('game.ui.screens.builder.structure_list_items.UIPanel'), \
             patch('game.ui.screens.builder.structure_list_items.UILabel'), \
             patch('game.ui.screens.builder.structure_list_items.UIButton'), \
             patch('game.ui.screens.builder.structure_list_items.UIImage') as mock_ui_image:
            
            item = IndividualComponentItem(ctx, component, 1000, 0, False)
            
            # Should have called get_icon for mod1 and mod3 (the modified ones)
            assert ctx.modifier_icon_service.get_icon.call_count == 2
            
            # The modifier_icons list should have 2 elements
            assert len(item.modifier_icons) == 2
