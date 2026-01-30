"""Tests for BattleScreen logic."""
import pytest
from unittest.mock import MagicMock, patch
import sys
import os
import pygame



from game.ui.screens.battle_scene import BattleScreen
from game.simulation.entities.ship import Ship, LayerType
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components.component import create_component, load_components
from game.core.registry import RegistryManager


class TestBattleScreen:

    @pytest.fixture(autouse=True)
    def setup_scene_and_ships(self):
        """Setup scene and ships for each test."""
        # Note: pygame, registry, and data loading handled by conftest fixtures
        # initialize_ship_data() and load_components() are patched to be no-ops
        # because the reset_game_state fixture already loaded the data
        # Patch BattleInterface to avoid UI overhead
        with patch('game.ui.screens.battle_screen.BattleInterface') as MockUI:
            scene = BattleScreen(800, 600)
            scene.ui = MockUI.return_value
            scene.ui.show_overlay = False

            # Create basic ships
            ship1 = Ship("Hero", 0, 0, (0, 0, 255))
            ship1.add_component(create_component('bridge'), LayerType.CORE)
            ship1.add_component(create_component('crew_quarters'), LayerType.CORE)
            ship1.add_component(create_component('life_support'), LayerType.CORE)
            ship1.add_component(create_component('standard_engine'), LayerType.OUTER)  # Add engine
            ship1.recalculate_stats()

            ship2 = Ship("Villain", 1000, 0, (255, 0, 0))
            ship2.add_component(create_component('bridge'), LayerType.CORE)
            ship2.add_component(create_component('crew_quarters'), LayerType.CORE)
            ship2.add_component(create_component('life_support'), LayerType.CORE)
            ship2.add_component(create_component('standard_engine'), LayerType.OUTER)  # Add engine
            ship2.recalculate_stats()

            self.scene = scene
            self.ship1 = ship1
            self.ship2 = ship2

            yield

        # Note: pygame and registry cleanup is handled by conftest fixtures
        # (pygame_display_reset and reset_game_state)
        # DO NOT call pygame.quit() here as it conflicts with session-level fixture

    def test_start_initialization(self):
        """Test battle initialization."""
        self.scene.start([self.ship1], [self.ship2], headless=True)

        assert len(self.scene.ships) == 2
        assert len(self.scene.ai_controllers) == 2
        assert self.ship1.team_id == 0
        assert self.ship2.team_id == 1
        assert self.scene.sim_tick_counter == 0

    def test_battle_over_condition(self):
        """Test win/loss detection."""
        self.scene.start([self.ship1], [self.ship2], headless=True)


        # Both alive
        assert not self.scene.is_battle_over()

        # Kill one
        self.ship2.is_alive = False
        assert self.scene.is_battle_over()

        # Winner should be team 0
        assert self.scene.get_winner() == 0

    def test_update_increment_sim_tick(self):
        """Test simulation tick counter increases."""
        self.scene.start([self.ship1], [self.ship2], headless=True)
        self.scene.update([])
        assert self.scene.sim_tick_counter == 1

    def test_projectile_registration(self):
        """Test that fired projectiles are registered in scene."""
        self.scene.start([self.ship1], [self.ship2], headless=True)

        # Mock projectile
        proj = MagicMock()
        proj.type = 'projectile'
        proj.is_alive = True
        proj.position = pygame.Vector2(0,0)
        proj.velocity = pygame.Vector2(10,0)
        proj.damage = 10
        proj.team_id = 0

        # Configure ship to fire this projectile
        self.ship1.comp_trigger_pulled = True

        # We must mock fire_weapons to return our projectile
        # But Ship.fire_weapons is a method on the instance.
        # We can patch it on the instance or class.
        with patch.object(self.ship1, 'fire_weapons', return_value=[proj]):
            self.scene.update([])

        assert proj in self.scene.projectiles

    def test_projectile_cleanup(self):
        """Test dead projectiles are removed."""
        self.scene.start([self.ship1], [self.ship2], headless=True)

        proj = MagicMock()
        proj.type = 'projectile'
        proj.is_alive = False  # Already dead
        proj.position = pygame.Vector2(0,0)
        proj.velocity = pygame.Vector2(0,0)

        self.scene.projectiles.append(proj)
        self.scene.update([])

        assert proj not in self.scene.projectiles

    def test_ui_service_property_available(self):
        """Test that ui_service property is available (PROJ-43)."""
        from game.ui.services.battle_ui_service import BattleUIService
        from game.ui.interfaces.battle_ui import IBattleUI

        self.scene.start([self.ship1], [self.ship2], headless=True)

        # ui_service should be available
        assert hasattr(self.scene, 'ui_service')
        assert self.scene.ui_service is not None
        assert isinstance(self.scene.ui_service, BattleUIService)
        assert isinstance(self.scene.ui_service, IBattleUI)

    def test_ui_service_returns_ship_dtos(self):
        """Test that ui_service returns ShipDTOs for ships (PROJ-43)."""
        from game.ui.interfaces.battle_ui import ShipDTO

        self.scene.start([self.ship1], [self.ship2], headless=True)

        ship_dtos = self.scene.ui_service.get_ships()
        assert len(ship_dtos) == 2
        assert all(isinstance(dto, ShipDTO) for dto in ship_dtos)

        # Verify ship names are correct
        names = {dto.name for dto in ship_dtos}
        assert "Hero" in names
        assert "Villain" in names
