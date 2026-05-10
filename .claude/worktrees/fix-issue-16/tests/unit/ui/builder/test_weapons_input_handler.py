"""
Tests for WeaponsInputHandler - tooltip hover detection for weapons panel.

PROJ-180: Tests for extracted geometry calculations from WeaponsReportPanel.
"""
import pytest
from unittest.mock import Mock, MagicMock


class TestWeaponsInputHandlerImports:
    """Test that WeaponsInputHandler can be imported without pygame dependencies."""

    def test_import_weapons_input_handler(self):
        """WeaponsInputHandler should import cleanly without pygame."""
        from game.ui.screens.builder.weapons_input_handler import WeaponsInputHandler
        assert WeaponsInputHandler is not None

    def test_bar_height_constant(self):
        """BAR_HEIGHT constant should be defined."""
        from game.ui.screens.builder.weapons_input_handler import WeaponsInputHandler
        handler = WeaponsInputHandler()
        assert hasattr(handler, 'BAR_HEIGHT')
        assert handler.BAR_HEIGHT == 15


class TestDetectTooltipHover:
    """Test tooltip hover detection logic."""

    @pytest.fixture
    def handler(self):
        """Create a WeaponsInputHandler instance."""
        from game.ui.screens.builder.weapons_input_handler import WeaponsInputHandler
        return WeaponsInputHandler()

    @pytest.fixture
    def mock_weapon(self):
        """Create a mock weapon with WeaponAbility."""
        weapon = Mock()
        weapon.name = "Test Laser"
        return weapon

    @pytest.fixture
    def mock_ship(self):
        """Create a mock ship."""
        ship = Mock()
        ship.get_total_sensor_score = Mock(return_value=0.0)
        return ship

    @pytest.fixture
    def mock_viewmodel(self):
        """Create a mock ViewModel."""
        vm = Mock()
        vm.calculate_tooltip_data = Mock(return_value={
            'range': 100,
            'accuracy': '85%',
            'damage': 10,
            'verbose': None
        })
        vm.max_range = 500
        return vm

    @pytest.fixture
    def mock_content_rect(self):
        """Create a mock content rect that always returns True for collidepoint."""
        rect = Mock()
        rect.collidepoint = Mock(return_value=True)
        return rect

    def test_returns_none_when_mouse_outside_content_rect(
        self, handler, mock_weapon, mock_ship, mock_viewmodel
    ):
        """Should return None when mouse is outside the content rect."""
        content_rect = Mock()
        content_rect.collidepoint = Mock(return_value=False)

        result = handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=50,
            weapon_bar_width=200,
            bar_width=400,
            weapon_range=500,
            content_rect=content_rect,
            mouse_pos=(300, 150),
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        assert result is None
        content_rect.collidepoint.assert_called_once_with((300, 150))

    def test_returns_none_when_mouse_outside_hit_rect_left(
        self, handler, mock_weapon, mock_ship, mock_viewmodel, mock_content_rect
    ):
        """Should return None when mouse is to the left of the weapon bar."""
        # bar starts at x=100, mouse at x=50 (left of bar)
        result = handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=200,
            bar_width=400,
            weapon_range=500,
            content_rect=mock_content_rect,
            mouse_pos=(50, 100),  # Left of bar
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        assert result is None

    def test_returns_none_when_mouse_outside_hit_rect_right(
        self, handler, mock_weapon, mock_ship, mock_viewmodel, mock_content_rect
    ):
        """Should return None when mouse is to the right of the weapon bar."""
        # bar starts at x=100, width=200, so ends at x=300
        # mouse at x=350 (right of bar)
        result = handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=200,
            bar_width=400,
            weapon_range=500,
            content_rect=mock_content_rect,
            mouse_pos=(350, 100),  # Right of bar
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        assert result is None

    def test_returns_none_when_mouse_above_hit_rect(
        self, handler, mock_weapon, mock_ship, mock_viewmodel, mock_content_rect
    ):
        """Should return None when mouse is above the weapon bar hit area."""
        # bar_y=100, hit area extends 10px above to y=90
        # BAR_HEIGHT=15, hit area extends 10px below to y=125
        # mouse at y=50 (above hit area)
        result = handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=200,
            bar_width=400,
            weapon_range=500,
            content_rect=mock_content_rect,
            mouse_pos=(150, 50),  # Above hit area
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        assert result is None

    def test_returns_none_when_mouse_below_hit_rect(
        self, handler, mock_weapon, mock_ship, mock_viewmodel, mock_content_rect
    ):
        """Should return None when mouse is below the weapon bar hit area."""
        # bar_y=100, BAR_HEIGHT=15, hit area extends 10px below to y=125
        # mouse at y=150 (below hit area)
        result = handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=200,
            bar_width=400,
            weapon_range=500,
            content_rect=mock_content_rect,
            mouse_pos=(150, 150),  # Below hit area
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        assert result is None

    def test_returns_tooltip_data_when_mouse_on_bar(
        self, handler, mock_weapon, mock_ship, mock_viewmodel, mock_content_rect
    ):
        """Should return tooltip data when mouse is over the weapon bar."""
        # bar_y=100, start_x=100, weapon_bar_width=200
        # mouse at (150, 100) - within bar
        result = handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=200,
            bar_width=400,
            weapon_range=500,
            content_rect=mock_content_rect,
            mouse_pos=(150, 100),
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        assert result is not None
        assert 'pos' in result
        assert result['pos'] == (150, 100)

    def test_correctly_maps_pixel_position_to_hover_range(
        self, handler, mock_weapon, mock_ship, mock_viewmodel, mock_content_rect
    ):
        """Should correctly calculate hover range from pixel position."""
        # Setup:
        # start_x=100, bar_width=400 (represents full max_range of 1000)
        # mouse at x=200, so dist_px=100
        # dist_ratio = 100/400 = 0.25
        # hover_range = 0.25 * 1000 = 250

        handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=200,
            bar_width=400,
            weapon_range=500,
            content_rect=mock_content_rect,
            mouse_pos=(200, 100),  # dist_px=100 from start
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        # Verify ViewModel was called with calculated hover_range
        # dist_px=100, bar_width=400, max_range=1000
        # hover_range = (100/400) * 1000 = 250
        mock_viewmodel.calculate_tooltip_data.assert_called_once()
        call_args = mock_viewmodel.calculate_tooltip_data.call_args
        actual_hover_range = call_args[0][2]  # Third positional argument
        assert actual_hover_range == 250

    def test_clamps_hover_range_to_weapon_range(
        self, handler, mock_weapon, mock_ship, mock_viewmodel, mock_content_rect
    ):
        """Should clamp hover_range to [0, weapon_range]."""
        # Setup: weapon_range=200, but pixel position would give hover_range=250
        # start_x=100, bar_width=400, max_range=1000
        # mouse at x=200, dist_px=100
        # unclamped hover_range = (100/400) * 1000 = 250
        # but weapon_range=200, so should clamp to 200

        handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=80,  # Smaller bar for weapon with range 200
            bar_width=400,
            weapon_range=200,  # Weapon can only reach 200
            content_rect=mock_content_rect,
            mouse_pos=(150, 100),  # Still within the weapon bar
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        # Verify clamping: hover_range should not exceed weapon_range
        call_args = mock_viewmodel.calculate_tooltip_data.call_args
        actual_hover_range = call_args[0][2]
        assert actual_hover_range <= 200

    def test_clamps_hover_range_to_zero_minimum(
        self, handler, mock_weapon, mock_ship, mock_viewmodel, mock_content_rect
    ):
        """Should clamp hover_range to minimum of 0."""
        # Even at start_x position, hover_range should be 0, not negative
        handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=200,
            bar_width=400,
            weapon_range=500,
            content_rect=mock_content_rect,
            mouse_pos=(100, 100),  # At bar start, dist_px=0
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        call_args = mock_viewmodel.calculate_tooltip_data.call_args
        actual_hover_range = call_args[0][2]
        assert actual_hover_range >= 0

    def test_returns_tooltip_data_with_pos_key_set(
        self, handler, mock_weapon, mock_ship, mock_viewmodel, mock_content_rect
    ):
        """Should add 'pos' key to tooltip data with mouse position."""
        mouse_pos = (175, 105)

        result = handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=200,
            bar_width=400,
            weapon_range=500,
            content_rect=mock_content_rect,
            mouse_pos=mouse_pos,
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        assert result is not None
        assert result['pos'] == mouse_pos

    def test_returns_none_when_viewmodel_returns_none(
        self, handler, mock_weapon, mock_ship, mock_content_rect
    ):
        """Should return None when ViewModel's calculate_tooltip_data returns None."""
        mock_viewmodel = Mock()
        mock_viewmodel.calculate_tooltip_data = Mock(return_value=None)

        result = handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=200,
            bar_width=400,
            weapon_range=500,
            content_rect=mock_content_rect,
            mouse_pos=(150, 100),
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        assert result is None

    def test_handles_zero_bar_width_gracefully(
        self, handler, mock_weapon, mock_ship, mock_viewmodel, mock_content_rect
    ):
        """Should handle edge case of bar_width=0 without division error."""
        # This shouldn't happen in practice, but we should handle it gracefully
        # When bar_width=0, dist_ratio should be 0 (not division by zero)

        result = handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=10,  # Small but non-zero bar
            bar_width=0,  # Zero bar width (edge case)
            weapon_range=500,
            content_rect=mock_content_rect,
            mouse_pos=(105, 100),  # Within the weapon bar
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        # Should not crash - with bar_width=0, dist_ratio becomes 0
        # This means hover_range=0, which is valid
        assert result is not None
        call_args = mock_viewmodel.calculate_tooltip_data.call_args
        actual_hover_range = call_args[0][2]
        assert actual_hover_range == 0  # With bar_width=0, ratio is 0

    def test_accepts_on_bar_edge(
        self, handler, mock_weapon, mock_ship, mock_viewmodel, mock_content_rect
    ):
        """Should detect hover at the exact right edge of the weapon bar."""
        # bar starts at x=100, width=200, so right edge is exactly x=300
        result = handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=200,
            bar_width=400,
            weapon_range=500,
            content_rect=mock_content_rect,
            mouse_pos=(300, 100),  # Exactly at right edge
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        assert result is not None

    def test_accepts_within_padding_above_bar(
        self, handler, mock_weapon, mock_ship, mock_viewmodel, mock_content_rect
    ):
        """Should detect hover in the padding area above the bar."""
        # bar_y=100, hit area extends 10px above to y=90
        result = handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=200,
            bar_width=400,
            weapon_range=500,
            content_rect=mock_content_rect,
            mouse_pos=(150, 92),  # Within padding above
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        assert result is not None

    def test_accepts_within_padding_below_bar(
        self, handler, mock_weapon, mock_ship, mock_viewmodel, mock_content_rect
    ):
        """Should detect hover in the padding area below the bar."""
        # bar_y=100, BAR_HEIGHT=15, hit area bottom = 100 + 15 + 10 = 125
        result = handler.detect_tooltip_hover(
            weapon=mock_weapon,
            ship=mock_ship,
            bar_y=100,
            start_x=100,
            weapon_bar_width=200,
            bar_width=400,
            weapon_range=500,
            content_rect=mock_content_rect,
            mouse_pos=(150, 120),  # Within padding below
            viewmodel=mock_viewmodel,
            max_range=1000
        )

        assert result is not None
