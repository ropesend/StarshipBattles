"""Extended tests for battle panels: ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel.

PROJ-111 Phase 3 Task 3.2: Battle Panels Extended Coverage
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
from game.simulation.entities.layer_data import LayerData


class MockRect:
    """Mock pygame.Rect for testing."""
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


class TestShipStatsPanelExtended:
    """Extended tests for ShipStatsPanel."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks and patch pygame."""
        mock_pygame = MagicMock()
        mock_pygame.K_LSHIFT = 1
        mock_pygame.K_RSHIFT = 2
        mock_pygame.SRCALPHA = 0
        mock_pygame.Rect = MockRect

        modules_patcher = patch.dict(sys.modules, {'pygame': mock_pygame})
        modules_patcher.start()

        from game.ui.panels import battle_panels
        import importlib
        importlib.reload(battle_panels)
        self.module = battle_panels
        self.mock_scene = MagicMock()
        self.mock_scene.ships = []

        mock_keys = {mock_pygame.K_LSHIFT: False, mock_pygame.K_RSHIFT: False}
        mock_pygame.key.get_pressed.return_value = mock_keys

        self.mock_pygame = mock_pygame

        yield

        modules_patcher.stop()

    def create_mock_ship(self, team_id, name="Ship"):
        """Create a mock ship object."""
        ship = MagicMock()
        ship.id = name  # Use name as ID for test clarity
        ship.team_id = team_id
        ship.name = name
        ship.is_alive = True
        ship.is_derelict = False
        ship.max_shields = 100
        ship.layers = {
            'outer': LayerData(),
            'inner': LayerData(),
            'core': LayerData(),
            'armor': LayerData()
        }
        ship.max_hp = 100
        ship.hp = 100
        ship.current_speed = 0
        ship.max_speed = 100
        ship.resources.set_max_value.return_value = None
        ship.resources.get_value.return_value = 50
        ship.ai_strategy = "aggressive"
        return ship

    def test_get_ships_with_ui_service_available(self):
        """Test _get_ships() with ui_service available returns DTO list."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship_dto = MagicMock()
        ship_dto.team_id = 0
        ship_dto.name = "Hero"
        self.mock_scene.ui_service.get_ships.return_value = [ship_dto]

        ships = panel._get_ships()

        assert len(ships) == 1
        assert ships[0].name == "Hero"

    def test_get_ships_with_ui_service_none_falls_back(self):
        """Test _get_ships() with ui_service None falls back to scene.ships."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship = self.create_mock_ship(0, "Fallback")
        self.mock_scene.ships = [ship]
        self.mock_scene.ui_service = None

        ships = panel._get_ships()

        assert len(ships) == 1
        assert ships[0].name == "Fallback"

    def test_get_ships_with_ui_service_exception_falls_back(self):
        """Test _get_ships() with ui_service.get_ships() raising exception falls back."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship = self.create_mock_ship(0, "Fallback")
        self.mock_scene.ships = [ship]
        self.mock_scene.ui_service.get_ships.side_effect = AttributeError("No method")

        ships = panel._get_ships()

        assert len(ships) == 1
        assert ships[0].name == "Fallback"

    def test_multiple_teams_display(self):
        """Test display of multiple teams (team 0 and team 1)."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship1 = self.create_mock_ship(0, "Team0Ship")
        ship2 = self.create_mock_ship(1, "Team1Ship")
        self.mock_scene.ui_service.get_ships.return_value = [ship1, ship2]

        ships = panel._get_ships()

        team0 = [s for s in ships if s.team_id == 0]
        team1 = [s for s in ships if s.team_id == 1]
        assert len(team0) == 1
        assert len(team1) == 1

    def test_empty_ship_list(self):
        """Test empty ship list (no ships in battle)."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        self.mock_scene.ui_service.get_ships.return_value = []

        ships = panel._get_ships()

        assert len(ships) == 0

    def test_expanded_ship_details_tracked_by_id(self):
        """Test expanded ship details uses ID-based tracking."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship = self.create_mock_ship(0, "Expandable")
        self.mock_scene.ui_service.get_ships.return_value = [ship]

        # Click to expand
        panel.handle_click(10, 50)

        # Should track by ship name (fallback ID)
        assert "Expandable" in panel.expanded_ships

    def test_get_ship_id_with_dto_id(self):
        """Test _get_ship_id() uses .id attribute for DTOs."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        dto = MagicMock()
        dto.id = "dto_id_123"
        dto.name = "DTO Ship"

        ship_id = panel._get_ship_id(dto)

        assert ship_id == "dto_id_123"

    def test_is_expanded_uses_id(self):
        """Test _is_expanded() uses ID-based lookup."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship = MagicMock()
        ship.id = "test_id"
        ship.name = "Test"

        assert not panel._is_expanded(ship)

        panel.expanded_ships.add("test_id")
        assert panel._is_expanded(ship)

    def test_toggle_expanded_adds_and_removes(self):
        """Test _toggle_expanded() adds and removes IDs."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship = MagicMock()
        ship.id = "toggle_id"
        ship.name = "Toggle"

        # Add
        panel._toggle_expanded(ship)
        assert "toggle_id" in panel.expanded_ships

        # Remove
        panel._toggle_expanded(ship)
        assert "toggle_id" not in panel.expanded_ships

    def test_handle_click_returns_false_for_miss(self):
        """Test handle_click returns False for clicks outside ship entries."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        self.mock_scene.ui_service.get_ships.return_value = []

        result = panel.handle_click(10, 500)

        assert result is False


class TestSeekerMonitorPanelExtended:
    """Extended tests for SeekerMonitorPanel."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks and patch pygame."""
        mock_pygame = MagicMock()
        mock_pygame.K_LSHIFT = 1
        mock_pygame.K_RSHIFT = 2
        mock_pygame.SRCALPHA = 0
        mock_pygame.Rect = MockRect

        modules_patcher = patch.dict(sys.modules, {'pygame': mock_pygame})
        modules_patcher.start()

        from game.ui.panels import battle_panels
        import importlib
        importlib.reload(battle_panels)
        self.module = battle_panels
        self.mock_scene = MagicMock()

        self.mock_pygame = mock_pygame

        yield

        modules_patcher.stop()

    def create_mock_seeker(self, status='active', seeker_id=None):
        """Create a mock seeker/projectile."""
        seeker = MagicMock()
        seeker.id = seeker_id if seeker_id else str(id(seeker))
        seeker.status = status
        seeker.velocity = MagicMock()
        seeker.velocity.length.return_value = 100
        seeker.hp = 50
        seeker.max_hp = 100
        seeker.endurance = 5.0
        seeker.max_endurance = 10.0
        seeker.damage = 25
        seeker.target = MagicMock()
        seeker.target.name = "Target Ship"
        return seeker

    def test_add_seeker_multiple_statuses(self):
        """Test add_seeker() with multiple seekers of different statuses."""
        panel = self.module.SeekerMonitorPanel(self.mock_scene, 0, 0, 300, 600)

        s1 = self.create_mock_seeker('active')
        s2 = self.create_mock_seeker('hit')
        s3 = self.create_mock_seeker('miss')
        s4 = self.create_mock_seeker('destroyed')

        panel.add_seeker(s1)
        panel.add_seeker(s2)
        panel.add_seeker(s3)
        panel.add_seeker(s4)

        assert len(panel.tracked_seekers) == 4

    def test_clear_inactive_removes_only_non_active(self):
        """Test clear_inactive() removes only non-active seekers."""
        panel = self.module.SeekerMonitorPanel(self.mock_scene, 0, 0, 300, 600)

        s_active = self.create_mock_seeker('active')
        s_hit = self.create_mock_seeker('hit')
        s_miss = self.create_mock_seeker('miss')

        panel.add_seeker(s_active)
        panel.add_seeker(s_hit)
        panel.add_seeker(s_miss)

        panel.clear_inactive()

        assert len(panel.tracked_seekers) == 1
        assert panel.tracked_seekers[0] == s_active

    def test_scroll_state_with_many_seekers(self):
        """Test scroll state handling with many seekers (overflow)."""
        panel = self.module.SeekerMonitorPanel(self.mock_scene, 0, 0, 300, 600)

        # Add many seekers
        for i in range(20):
            panel.add_seeker(self.create_mock_seeker('active'))

        assert len(panel.tracked_seekers) == 20
        assert panel.scroll.offset == 0  # Initial offset

        # Set scroll offset
        panel.scroll.offset = 100
        assert panel.scroll.offset == 100

    def test_get_projectile_id_with_dto_id(self):
        """Test _get_projectile_id() uses .id for DTOs."""
        panel = self.module.SeekerMonitorPanel(self.mock_scene, 0, 0, 300, 600)

        dto = MagicMock()
        dto.id = "proj_123"

        proj_id = panel._get_projectile_id(dto)

        assert proj_id == "proj_123"

    def test_seeker_expansion_toggle(self):
        """Test seeker expansion toggle via _toggle_seeker_expanded."""
        panel = self.module.SeekerMonitorPanel(self.mock_scene, 0, 0, 300, 600)

        seeker = self.create_mock_seeker('active', seeker_id='seeker_001')

        # Toggle on
        panel._toggle_seeker_expanded(seeker)
        assert seeker.id in panel.expanded_seekers

        # Toggle off
        panel._toggle_seeker_expanded(seeker)
        assert seeker.id not in panel.expanded_seekers

    def test_is_seeker_expanded_uses_id(self):
        """Test _is_seeker_expanded() uses ID-based lookup."""
        panel = self.module.SeekerMonitorPanel(self.mock_scene, 0, 0, 300, 600)

        seeker = self.create_mock_seeker('active')
        seeker_id = str(id(seeker))

        assert not panel._is_seeker_expanded(seeker)

        panel.expanded_seekers.add(seeker_id)
        assert panel._is_seeker_expanded(seeker)

    def test_handle_click_clear_button(self):
        """Test handle_click() on clear button removes inactive seekers."""
        panel = self.module.SeekerMonitorPanel(self.mock_scene, 0, 0, 300, 600)

        s_active = self.create_mock_seeker('active')
        s_hit = self.create_mock_seeker('hit')
        panel.add_seeker(s_active)
        panel.add_seeker(s_hit)

        # Set up clear button rect
        panel.clear_btn_rect = MockRect(10, 560, 280, 30)

        # Click on clear button
        result = panel.handle_click(50, 570)

        assert result is True
        assert len(panel.tracked_seekers) == 1

    def test_handle_click_x_button_removes_inactive_seeker(self):
        """Test clicking X button removes inactive seeker."""
        panel = self.module.SeekerMonitorPanel(self.mock_scene, 0, 0, 300, 600)

        seeker = self.create_mock_seeker('hit')
        panel.add_seeker(seeker)

        # X button is at rel_x in [panel_w-25, panel_w-5] = [275, 295]
        # Seeker entry at y=40 (10+30 header), height 22, so range [40, 62)
        # To hit X button: abs_x = 0 + 280 = 280, abs_y = 0 + 45 = 45
        result = panel.handle_click(280, 45)

        assert result is True
        assert seeker not in panel.tracked_seekers

    def test_handle_click_toggle_seeker_expansion(self):
        """Test clicking seeker entry toggles expansion."""
        panel = self.module.SeekerMonitorPanel(self.mock_scene, 0, 0, 300, 600)

        seeker = self.create_mock_seeker('active')
        panel.add_seeker(seeker)

        # Click on seeker entry (not X button)
        # Entry at y=40, click at x=50
        result = panel.handle_click(50, 45)

        assert result is True
        seeker_id = str(id(seeker))
        assert seeker_id in panel.expanded_seekers


class TestBattleControlPanelExtended:
    """Extended tests for BattleControlPanel."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks and patch pygame."""
        mock_pygame = MagicMock()
        mock_pygame.K_LSHIFT = 1
        mock_pygame.K_RSHIFT = 2
        mock_pygame.SRCALPHA = 0
        mock_pygame.Rect = MockRect

        modules_patcher = patch.dict(sys.modules, {'pygame': mock_pygame})
        modules_patcher.start()

        from game.ui.panels import battle_panels
        import importlib
        importlib.reload(battle_panels)
        self.module = battle_panels
        self.mock_scene = MagicMock()

        self.mock_pygame = mock_pygame

        yield

        modules_patcher.stop()

    def test_handle_click_no_rects_set_returns_false(self):
        """Test handle_click() with no rects set (draw not called yet) returns False."""
        panel = self.module.BattleControlPanel(self.mock_scene, 0, 0, 800, 600)

        # Neither rect is set initially
        assert panel.battle_end_button_rect is None
        assert panel.end_battle_early_rect is None

        result = panel.handle_click(100, 100)

        assert result is False

    def test_handle_click_end_battle_early_button(self):
        """Test handle_click() on end battle early button."""
        panel = self.module.BattleControlPanel(self.mock_scene, 0, 0, 800, 600)

        # Simulate draw() having set the rect
        panel.end_battle_early_rect = MockRect(10, 70, 120, 30)

        result = panel.handle_click(50, 80)

        assert result == "end_battle"

    def test_handle_click_battle_end_button(self):
        """Test handle_click() on battle end button (victory screen)."""
        panel = self.module.BattleControlPanel(self.mock_scene, 0, 0, 800, 600)

        # Simulate draw() having set the rect (victory state)
        panel.battle_end_button_rect = MockRect(275, 300, 250, 50)

        result = panel.handle_click(400, 320)

        assert result == "end_battle"

    def test_handle_click_outside_buttons(self):
        """Test handle_click() outside all buttons returns False."""
        panel = self.module.BattleControlPanel(self.mock_scene, 0, 0, 800, 600)

        panel.end_battle_early_rect = MockRect(10, 70, 120, 30)

        result = panel.handle_click(500, 500)

        assert result is False

    def test_get_ships_used_for_battle_state(self):
        """Test _get_ships() is used to determine battle state."""
        panel = self.module.BattleControlPanel(self.mock_scene, 0, 0, 800, 600)

        ship1 = MagicMock()
        ship1.team_id = 0
        ship1.is_alive = True
        ship1.is_derelict = False

        ship2 = MagicMock()
        ship2.team_id = 1
        ship2.is_alive = True
        ship2.is_derelict = False

        self.mock_scene.ui_service.get_ships.return_value = [ship1, ship2]

        # _get_ships is called during draw, but we can test it directly
        ships = panel._get_ships()

        assert len(ships) == 2


class TestBattlePanelBaseClass:
    """Tests for BattlePanel base class functionality."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks and patch pygame."""
        mock_pygame = MagicMock()
        mock_pygame.SRCALPHA = 0
        mock_pygame.Rect = MockRect

        modules_patcher = patch.dict(sys.modules, {'pygame': mock_pygame})
        modules_patcher.start()

        from game.ui.panels import battle_panels
        import importlib
        importlib.reload(battle_panels)
        self.module = battle_panels
        self.mock_scene = MagicMock()

        yield

        modules_patcher.stop()

    def test_base_panel_init(self):
        """Test BattlePanel initialization."""
        panel = self.module.BattlePanel(self.mock_scene, 100, 100, 200, 300)

        assert panel.scene == self.mock_scene
        assert panel.rect.x == 100
        assert panel.rect.y == 100
        assert panel.rect.width == 200
        assert panel.rect.height == 300

    def test_base_panel_handle_click_returns_false(self):
        """Test BattlePanel.handle_click() default returns False."""
        panel = self.module.BattlePanel(self.mock_scene, 100, 100, 200, 300)

        result = panel.handle_click(150, 150)

        assert result is False

    def test_base_panel_draw_raises_not_implemented(self):
        """Test BattlePanel.draw() raises NotImplementedError."""
        panel = self.module.BattlePanel(self.mock_scene, 100, 100, 200, 300)
        screen = MagicMock()

        with pytest.raises(NotImplementedError):
            panel.draw(screen)

    def test_get_ships_fallback_chain(self):
        """Test _get_ships() fallback chain: ui_service -> scene.ships."""
        panel = self.module.BattlePanel(self.mock_scene, 100, 100, 200, 300)

        # Case 1: ui_service works
        dto = MagicMock()
        dto.name = "DTO"
        self.mock_scene.ui_service.get_ships.return_value = [dto]

        ships = panel._get_ships()
        assert len(ships) == 1
        assert ships[0].name == "DTO"

        # Case 2: ui_service returns non-list (mock auto-result)
        self.mock_scene.ui_service.get_ships.return_value = MagicMock()
        self.mock_scene.ships = [MagicMock(name="Direct")]

        ships = panel._get_ships()
        assert len(ships) == 1

        # Case 3: No ui_service
        self.mock_scene.ui_service = None
        direct_ship = MagicMock()
        direct_ship.name = "Direct"
        self.mock_scene.ships = [direct_ship]

        ships = panel._get_ships()
        assert len(ships) == 1


class TestShipStatsPanelGetExpandedHeight:
    """Tests for ShipStatsPanel.get_expanded_height()."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks."""
        mock_pygame = MagicMock()
        mock_pygame.SRCALPHA = 0
        mock_pygame.Rect = MockRect

        modules_patcher = patch.dict(sys.modules, {'pygame': mock_pygame})
        modules_patcher.start()

        from game.ui.panels import battle_panels
        import importlib
        importlib.reload(battle_panels)
        self.module = battle_panels
        self.mock_scene = MagicMock()

        yield

        modules_patcher.stop()

    def test_get_expanded_height_no_shields(self):
        """Test get_expanded_height() for ship without shields."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship = MagicMock()
        ship.max_shields = 0
        ship.get_all_components.return_value = []

        height = panel.get_expanded_height(ship)

        # Base 180, no shield, no components, +5 padding
        assert height == 180 + 5

    def test_get_expanded_height_with_shields(self):
        """Test get_expanded_height() for ship with shields."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship = MagicMock()
        ship.max_shields = 100
        ship.get_all_components.return_value = []

        height = panel.get_expanded_height(ship)

        # Base 180, shield (+20), no components, +5 padding
        assert height == 180 + 20 + 5

    def test_get_expanded_height_with_components(self):
        """Test get_expanded_height() for ship with components."""
        panel = self.module.ShipStatsPanel(self.mock_scene, 800, 0, 200, 600)

        ship = MagicMock()
        ship.max_shields = 0
        ship.components = [MagicMock(), MagicMock(), MagicMock()]

        height = panel.get_expanded_height(ship)

        # Base 180, no shield, 3 components * 20 = 60, +5 padding
        assert height == 180 + 60 + 5
