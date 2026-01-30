import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock Rect to allow logic validation
class MockRect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.topleft = (x, y)
        self.bottomleft = (x, y + h)
        self.center = (x + w//2, y + h//2)
        self.centerx = x + w//2
        self.bottom = y + h
        self.size = (w, h)

    def collidepoint(self, *args):
        if len(args) == 1:
            px, py = args[0]
        else:
            px, py = args
        return self.x <= px < self.x + self.width and self.y <= py < self.y + self.height

    def inflate(self, *args):
        return self


class TestBattlePanels:

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks and patch pygame."""
        mock_pygame = MagicMock()
        mock_pygame.K_LSHIFT = 1
        mock_pygame.K_RSHIFT = 2
        mock_pygame.SRCALPHA = 0
        mock_pygame.Rect = MockRect

        # Patch sys.modules
        modules_patcher = patch.dict(sys.modules, {'pygame': mock_pygame})
        modules_patcher.start()

        # Prepare sys.path
        orig_path = list(sys.path)

        # Import module under test
        # Handle reload if needed
        from game.ui.panels import battle_panels
        import importlib
        importlib.reload(battle_panels)
        self.module = battle_panels
        self.mock_scene = MagicMock()
        self.mock_scene.ships = []

        # Default key state: Not pressing shift
        mock_keys = {mock_pygame.K_LSHIFT: False, mock_pygame.K_RSHIFT: False}
        mock_pygame.key.get_pressed.return_value = mock_keys

        self.mock_pygame = mock_pygame

        yield

        # Restore modules and path
        modules_patcher.stop()
        sys.path = orig_path

    def create_mock_ship(self, team_id, name="Ship"):
        ship = MagicMock()
        ship.team_id = team_id
        ship.name = name
        ship.is_alive = True
        ship.is_derelict = False
        ship.max_shields = 100
        ship.layers = {
            'outer': {'components': []},
            'inner': {'components': []},
            'core': {'components': []},
            'armor': {'components': []}
        }
        # Needed for height calc
        ship.max_hp = 100
        ship.hp = 100
        ship.current_speed = 0
        ship.max_speed = 100
        ship.resources.set_max_value('fuel', 100)
        ship.resources.set_max_value('energy', 100)
        ship.resources.set_max_value('ammo', 100)
        ship.ai_strategy = "aggressive"
        return ship

    def test_stats_panel_expansion(self):
        """Test toggling ship expansion in stats panel."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship1 = self.create_mock_ship(0, "Hero")
        self.mock_scene.ships = [ship1]

        # Calculate where the click should be
        # y starts at 10 - scroll(0)
        # Title "Team 1": y=10. Draws text. y+=30 -> 40.
        # Ship 1: drawn at 40. Height 25. Range [40, 65).

        # Test 1: Expand
        handled = panel.handle_click(10, 50)
        assert handled is True
        # PROJ-43: expanded_ships now tracks ship IDs (name used as fallback ID)
        assert "Hero" in panel.expanded_ships

        # Test 2: Collapse
        handled = panel.handle_click(10, 50)
        assert handled is True
        assert "Hero" not in panel.expanded_ships

    def test_stats_panel_scroll_offset(self):
        """Test that scroll offset shifts the click targets."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)
        ship1 = self.create_mock_ship(0, "Hero")

        # Add a second ship to Team 2 to ensure we test deep list items
        ship2 = self.create_mock_ship(1, "Villain")
        self.mock_scene.ships = [ship1, ship2]

        # Initial Logic:
        # Team 1 Header: 10
        # Ship 1: 40 [40, 65)
        # Spacer: 65 -> +45 = 110
        # Team 2 ships loop logic in handle_click starts at 110.
        # Ship 2: 110 [110, 135)

        # Test clicking Ship 2 WITHOUT scroll
        handled = panel.handle_click(10, 120)
        assert handled is True
        # PROJ-43: expanded_ships now tracks ship IDs (name used as fallback ID)
        assert "Villain" in panel.expanded_ships
        panel.expanded_ships.clear()

        # Test clicking Ship 2 WITH scroll
        # Set Scroll Offset = 50.
        # This effectively "moves the view down", so top items move up (negative y).
        # But handle_click adds scroll_offset to input `my` to get "virtual Y".
        # So clicking at screen Y=70 should map to Virtual Y=120?
        # rel_y = 70 + 50 = 120.
        # This matches the interval [110, 135).

        panel.scroll_offset = 50
        handled = panel.handle_click(10, 70)
        assert handled is True, "Click at 70 with scroll 50 should map to 120 and hit ship2"
        assert "Villain" in panel.expanded_ships

        # Verify clicking original screen spot (120) now maps to 170 -> miss
        panel.expanded_ships.clear()
        handled = panel.handle_click(10, 120)  # rel_y = 170
        assert handled is False

    def test_seeker_monitor_state(self):
        """Test seeker add and clear inactive logic."""
        panel = self.module.SeekerMonitorPanel(self.mock_scene, 0, 0, 300, 600)

        # Mock seekers
        s1 = MagicMock()
        s1.status = 'active'
        s2 = MagicMock()
        s2.status = 'hit'  # Inactive
        s3 = MagicMock()
        s3.status = 'miss'  # Inactive

        panel.add_seeker(s1)
        panel.add_seeker(s2)
        panel.add_seeker(s3)

        assert len(panel.tracked_seekers) == 3

        panel.clear_inactive()
        assert len(panel.tracked_seekers) == 1
        assert panel.tracked_seekers[0] == s1

    def test_seeker_panel_coordinate_logic(self):
        """Test relative coordinate logic in Seeker Panel."""
        # Panel at x=100, y=100.
        panel = self.module.SeekerMonitorPanel(self.mock_scene, 100, 100, 300, 600)

        s1 = MagicMock()
        s1.status = 'active'
        s1.velocity = MagicMock()
        s1.velocity.length.return_value = 0
        panel.add_seeker(s1)

        # handle_click(mx, my) where mx, my are Absolute.
        # Logic: rel_x = mx - rect.x = mx - 100
        #        rel_y = my - rect.y + scroll = my - 100 + 0

        # Item 1 is at y_pos = 10 + 30 = 40. Range [40, 62).

        # To hit Item 1:
        # rel_y in [40, 62).
        # my - 100 = 40 => my = 140.
        # mx needs to be inside panel? Panel X [100, 400).
        # Let's say mx = 150.

        handled = panel.handle_click(150, 140)
        assert handled is True
        # PROJ-43: expanded_seekers now tracks projectile IDs (Python id used as fallback)
        s1_id = str(id(s1))
        assert s1_id in panel.expanded_seekers

        # Test clicking X button (Inactive seeker)
        s1.status = 'hit'
        # X button is at rel_x in [panel_w-25, panel_w-5]. panel_w=300. [275, 295].
        # Abs mx = 100 + 280 = 380.

        handled = panel.handle_click(380, 140)
        assert handled is True
        assert s1 not in panel.tracked_seekers

    def test_battle_end_control(self):
        """Test BattleControlPanel end battle button."""
        panel = self.module.BattleControlPanel(self.mock_scene, 0, 0, 800, 600)

        # Manually set rects as if draw() was called, or just test logic if rects exist
        # draw() sets self.end_battle_early_rect
        btn_rect = self.mock_pygame.Rect(10, 70, 120, 30)
        panel.end_battle_early_rect = btn_rect

        # Click inside
        res = panel.handle_click(15, 75)  # 10 < 15 < 130, 70 < 75 < 100
        assert res == "end_battle"

        # Click outside
        res = panel.handle_click(200, 200)
        assert res is False


# =============================================================================
# PROJ-43 Task 12.5: Tests for DTO-Based Panel Access
# =============================================================================
# These tests verify that panels work correctly with ShipDTO objects
# instead of direct Ship domain object access.

class TestBattlePanelsDTOIntegration:
    """Tests for panels using DTOs from ui_service (PROJ-43)."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks and patch pygame."""
        mock_pygame = MagicMock()
        mock_pygame.K_LSHIFT = 1
        mock_pygame.K_RSHIFT = 2
        mock_pygame.SRCALPHA = 0
        mock_pygame.Rect = MockRect

        # Patch sys.modules
        modules_patcher = patch.dict(sys.modules, {'pygame': mock_pygame})
        modules_patcher.start()

        # Import module under test
        from game.ui.panels import battle_panels
        import importlib
        importlib.reload(battle_panels)
        self.module = battle_panels
        self.mock_scene = MagicMock()

        # Default key state: Not pressing shift
        mock_keys = {mock_pygame.K_LSHIFT: False, mock_pygame.K_RSHIFT: False}
        mock_pygame.key.get_pressed.return_value = mock_keys

        self.mock_pygame = mock_pygame

        yield

        # Restore modules
        modules_patcher.stop()

    def create_mock_ship_dto(self, ship_id, team_id, name="Ship"):
        """Create a mock ShipDTO for testing."""
        dto = MagicMock()
        dto.id = ship_id
        dto.team_id = team_id
        dto.name = name
        dto.is_alive = True
        dto.is_derelict = False
        dto.max_shields = 100
        dto.current_shields = 50
        dto.max_hp = 100
        dto.hp = 75
        dto.current_speed = 0
        dto.max_speed = 100
        dto.total_shots_fired = 5
        dto.crew_onboard = 10
        dto.crew_required = 10
        dto.current_target_name = None
        dto.secondary_target_names = []
        dto.max_targets = 1
        dto.ai_strategy = "aggressive"
        dto.source_file = None
        dto.resources = []
        dto.components = []
        return dto

    def test_expanded_ships_uses_ship_ids(self):
        """Verify expanded_ships tracks ship IDs, not object references (PROJ-43)."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        # Create ShipDTO mocks with IDs
        ship1 = self.create_mock_ship_dto("ship_001", 0, "Hero")
        ship2 = self.create_mock_ship_dto("ship_002", 1, "Villain")

        # Configure scene to return ships via ui_service
        self.mock_scene.ui_service.get_ships.return_value = [ship1, ship2]

        # Simulate clicking on ship1 entry
        # With DTO-based approach, expanded_ships should contain ship ID
        handled = panel.handle_click(10, 50)
        assert handled is True

        # Check that expanded_ships contains string ID, not object
        assert len(panel.expanded_ships) == 1
        expanded_id = list(panel.expanded_ships)[0]
        assert isinstance(expanded_id, str), "expanded_ships should contain string IDs"
        assert expanded_id == "ship_001"

    def test_panel_uses_ui_service_for_ships(self):
        """Verify panel retrieves ships from ui_service.get_ships() (PROJ-43)."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship1 = self.create_mock_ship_dto("ship_001", 0, "Hero")
        self.mock_scene.ui_service.get_ships.return_value = [ship1]

        # Trigger a click to force panel to query ships
        panel.handle_click(10, 50)

        # Verify ui_service.get_ships() was called
        self.mock_scene.ui_service.get_ships.assert_called()

    def test_toggle_expansion_with_dto_ids(self):
        """Test toggle expand/collapse using DTO ship IDs (PROJ-43)."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship1 = self.create_mock_ship_dto("ship_001", 0, "Hero")
        self.mock_scene.ui_service.get_ships.return_value = [ship1]

        # Expand
        panel.handle_click(10, 50)
        assert "ship_001" in panel.expanded_ships

        # Collapse
        panel.handle_click(10, 50)
        assert "ship_001" not in panel.expanded_ships

    def test_focus_ship_returns_ship_id(self):
        """Test shift-click returns ship ID for camera focus (PROJ-43)."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship1 = self.create_mock_ship_dto("ship_001", 0, "Hero")
        self.mock_scene.ui_service.get_ships.return_value = [ship1]

        # Enable shift key
        mock_keys = {self.mock_pygame.K_LSHIFT: True, self.mock_pygame.K_RSHIFT: False}
        self.mock_pygame.key.get_pressed.return_value = mock_keys

        # Click on ship entry with shift held
        result = panel.handle_click(10, 50)

        # Should return focus_ship tuple with ship ID
        assert isinstance(result, tuple)
        assert result[0] == "focus_ship"
        assert result[1] == "ship_001"
