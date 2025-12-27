import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# --- Scaffolding & Mocks ---
# We must mock pygame before importing battle_panels
mock_pygame = MagicMock()
sys.modules['pygame'] = mock_pygame

# Define basic constants used
mock_pygame.K_LSHIFT = 1
mock_pygame.K_RSHIFT = 2
mock_pygame.SRCALPHA = 0

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

mock_pygame.Rect = MockRect

# Ensure valid import of logic
try:
    import battle_panels
    from battle_panels import ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel, BattlePanel
except ImportError:
    # If explicit import fails, try adding CWD
    sys.path.append(os.getcwd())
    import battle_panels
    from battle_panels import ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel, BattlePanel

class TestBattlePanels(unittest.TestCase):
    def setUp(self):
        self.mock_scene = MagicMock()
        self.mock_scene.ships = []
        
        # Default key state: Not pressing shift
        self.mock_keys = {mock_pygame.K_LSHIFT: False, mock_pygame.K_RSHIFT: False}
        mock_pygame.key.get_pressed.return_value = self.mock_keys

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
        ship.max_fuel = 100
        ship.max_energy = 100
        ship.max_ammo = 100
        ship.ai_strategy = "aggressive"
        return ship

    def test_stats_panel_expansion(self):
        """Test toggling ship expansion in stats panel."""
        panel = ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)
        
        ship1 = self.create_mock_ship(0, "Hero")
        self.mock_scene.ships = [ship1]
        
        # Calculate where the click should be
        # y starts at 10 - scroll(0)
        # Title "Team 1": y=10. Draws text. y+=30 -> 40.
        # Ship 1: drawn at 40. Height 25. Range [40, 65).
        
        # Test 1: Expand
        handled = panel.handle_click(10, 50)
        self.assertTrue(handled)
        self.assertIn(ship1, panel.expanded_ships)
        
        # Test 2: Collapse
        handled = panel.handle_click(10, 50)
        self.assertTrue(handled)
        self.assertNotIn(ship1, panel.expanded_ships)

    def test_stats_panel_scroll_offset(self):
        """Test that scroll offset shifts the click targets."""
        panel = ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)
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
        self.assertTrue(handled)
        self.assertIn(ship2, panel.expanded_ships)
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
        self.assertTrue(handled, "Click at 70 with scroll 50 should map to 120 and hit ship2")
        self.assertIn(ship2, panel.expanded_ships)
        
        # Verify clicking original screen spot (120) now maps to 170 -> miss
        panel.expanded_ships.clear()
        handled = panel.handle_click(10, 120) # rel_y = 170
        self.assertFalse(handled)

    def test_seeker_monitor_state(self):
        """Test seeker add and clear inactive logic."""
        panel = SeekerMonitorPanel(self.mock_scene, 0, 0, 300, 600)
        
        # Mock seekers
        s1 = MagicMock()
        s1.status = 'active'
        s2 = MagicMock()
        s2.status = 'hit' # Inactive
        s3 = MagicMock()
        s3.status = 'miss' # Inactive
        
        panel.add_seeker(s1)
        panel.add_seeker(s2)
        panel.add_seeker(s3)
        
        self.assertEqual(len(panel.tracked_seekers), 3)
        
        panel.clear_inactive()
        self.assertEqual(len(panel.tracked_seekers), 1)
        self.assertEqual(panel.tracked_seekers[0], s1)

    def test_seeker_panel_coordinate_logic(self):
        """Test relative coordinate logic in Seeker Panel."""
        # Panel at x=100, y=100.
        panel = SeekerMonitorPanel(self.mock_scene, 100, 100, 300, 600)
        
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
        self.assertTrue(handled)
        self.assertIn(s1, panel.expanded_seekers)
        
        # Test clicking X button (Inactive seeker)
        s1.status = 'hit'
        # X button is at rel_x in [panel_w-25, panel_w-5]. panel_w=300. [275, 295].
        # Abs mx = 100 + 280 = 380.
        
        handled = panel.handle_click(380, 140)
        self.assertTrue(handled)
        self.assertNotIn(s1, panel.tracked_seekers)

    def test_battle_end_control(self):
        """Test BattleControlPanel end battle button."""
        panel = BattleControlPanel(self.mock_scene, 0, 0, 800, 600)
        
        # Manually set rects as if draw() was called, or just test logic if rects exist
        # draw() sets self.end_battle_early_rect
        btn_rect = mock_pygame.Rect(10, 70, 120, 30)
        panel.end_battle_early_rect = btn_rect
        
        # Click inside
        res = panel.handle_click(15, 75) # 10 < 15 < 130, 70 < 75 < 100
        self.assertEqual(res, "end_battle")
        
        # Click outside
        res = panel.handle_click(200, 200)
        self.assertFalse(res)

if __name__ == '__main__':
    unittest.main()
