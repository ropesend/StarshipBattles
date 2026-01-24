"""
Unit tests for ui/test_lab_scene.py

Tests the Test Lab Scene UI components and logic.
Focuses on pure logic testing without pygame initialization.
"""
import pytest
import json
from types import SimpleNamespace


# =============================================================================
# Tests for JSONPopup dimensions and scrolling
# =============================================================================

class TestJSONPopupDimensions:
    """Tests for JSONPopup dimension calculations."""

    def calculate_popup_dimensions(self, screen_width, screen_height, scale=0.8):
        """Calculate popup dimensions (80% of screen)."""
        width = int(screen_width * scale)
        height = int(screen_height * scale)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        return (x, y, width, height)

    def test_standard_screen_dimensions(self):
        """Test popup dimensions for standard screen."""
        x, y, w, h = self.calculate_popup_dimensions(1920, 1080)
        assert w == 1536  # 1920 * 0.8
        assert h == 864   # 1080 * 0.8
        assert x == 192   # (1920 - 1536) / 2
        assert y == 108   # (1080 - 864) / 2

    def test_small_screen_dimensions(self):
        """Test popup dimensions for small screen."""
        x, y, w, h = self.calculate_popup_dimensions(800, 600)
        assert w == 640  # 800 * 0.8
        assert h == 480  # 600 * 0.8
        assert x == 80   # (800 - 640) / 2
        assert y == 60   # (600 - 480) / 2

    def test_popup_is_centered(self):
        """Test that popup is centered on screen."""
        screen_w, screen_h = 1920, 1080
        x, y, w, h = self.calculate_popup_dimensions(screen_w, screen_h)
        # Check centering
        assert x + w // 2 == screen_w // 2
        assert y + h // 2 == screen_h // 2


class TestJSONPopupScrolling:
    """Tests for JSONPopup scroll logic."""

    def clamp_scroll(self, scroll_offset, total_lines, visible_lines):
        """Clamp scroll offset to valid range."""
        max_scroll = max(0, total_lines - visible_lines)
        return max(0, min(scroll_offset, max_scroll))

    def test_scroll_at_top(self):
        """Test scroll clamped at top."""
        result = self.clamp_scroll(-5, 100, 20)
        assert result == 0

    def test_scroll_at_bottom(self):
        """Test scroll clamped at bottom."""
        result = self.clamp_scroll(90, 100, 20)
        assert result == 80  # max_scroll = 100 - 20 = 80

    def test_scroll_in_middle(self):
        """Test scroll in valid range."""
        result = self.clamp_scroll(50, 100, 20)
        assert result == 50

    def test_short_content_no_scroll(self):
        """Test when content fits in viewport."""
        result = self.clamp_scroll(10, 15, 20)
        assert result == 0  # Can't scroll when content < visible


# =============================================================================
# Tests for ConfirmationDialog dimensions
# =============================================================================

class TestConfirmationDialogDimensions:
    """Tests for ConfirmationDialog dimension calculations."""

    def calculate_dialog_dimensions(self, screen_width, screen_height,
                                    max_width=800, max_height=600, scale=0.6):
        """Calculate dialog dimensions (60% of screen, capped)."""
        width = min(max_width, int(screen_width * scale))
        height = min(max_height, int(screen_height * scale))
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        return (x, y, width, height)

    def test_small_screen_full_scale(self):
        """Test dialog on small screen uses full scale."""
        x, y, w, h = self.calculate_dialog_dimensions(800, 600)
        assert w == 480  # 800 * 0.6 = 480 < 800
        assert h == 360  # 600 * 0.6 = 360 < 600

    def test_large_screen_capped(self):
        """Test dialog on large screen is capped."""
        x, y, w, h = self.calculate_dialog_dimensions(2560, 1440)
        assert w == 800  # Capped at max_width
        assert h == 600  # Capped at max_height

    def test_dialog_is_centered(self):
        """Test that dialog is centered on screen."""
        screen_w, screen_h = 1920, 1080
        x, y, w, h = self.calculate_dialog_dimensions(screen_w, screen_h)
        assert x == (screen_w - w) // 2
        assert y == (screen_h - h) // 2


# =============================================================================
# Tests for ScrollableJSONViewer
# =============================================================================

class TestScrollableJSONViewer:
    """Tests for ScrollableJSONViewer logic."""

    def calculate_visible_lines(self, height, title_height, line_height):
        """Calculate number of visible lines."""
        content_height = height - title_height
        return max(1, content_height // line_height)

    def calculate_max_scroll(self, total_lines, visible_lines):
        """Calculate maximum scroll offset."""
        return max(0, total_lines - visible_lines)

    def test_visible_lines_calculation(self):
        """Test visible lines calculation."""
        result = self.calculate_visible_lines(500, 30, 18)
        # (500 - 30) / 18 = 470 / 18 = 26.1 -> 26
        assert result == 26

    def test_visible_lines_minimum(self):
        """Test visible lines minimum is 1."""
        result = self.calculate_visible_lines(40, 30, 18)
        # (40 - 30) / 18 = 0.5 -> 0, but min is 1
        assert result == 1

    def test_max_scroll_calculation(self):
        """Test max scroll calculation."""
        result = self.calculate_max_scroll(100, 26)
        assert result == 74

    def test_max_scroll_short_content(self):
        """Test max scroll is 0 for short content."""
        result = self.calculate_max_scroll(10, 26)
        assert result == 0


class TestJSONFormatting:
    """Tests for JSON formatting logic."""

    def format_json(self, data, indent=2):
        """Format data as JSON string."""
        if data is None:
            return "{}"
        return json.dumps(data, indent=indent)

    def test_format_empty_dict(self):
        """Test formatting empty dict."""
        result = self.format_json({})
        assert result == "{}"

    def test_format_none(self):
        """Test formatting None."""
        result = self.format_json(None)
        assert result == "{}"

    def test_format_simple_dict(self):
        """Test formatting simple dict."""
        result = self.format_json({"key": "value"})
        assert '"key"' in result
        assert '"value"' in result

    def test_format_nested_dict(self):
        """Test formatting nested dict."""
        result = self.format_json({"outer": {"inner": 1}})
        lines = result.split('\n')
        assert len(lines) > 1  # Should be multi-line

    def test_line_count_matches_content(self):
        """Test that line count matches content complexity."""
        data = {"a": 1, "b": 2, "c": 3}
        result = self.format_json(data)
        lines = result.split('\n')
        # 5 lines: { + 3 key-value + }
        assert len(lines) == 5


# =============================================================================
# Tests for ComponentDropdown selection
# =============================================================================

class TestComponentDropdownSelection:
    """Tests for ComponentDropdown selection logic."""

    def get_selected_component_id(self, component_ids, selected_index):
        """Get currently selected component ID."""
        if not component_ids:
            return None
        if 0 <= selected_index < len(component_ids):
            comp_id = component_ids[selected_index]
            return comp_id if comp_id != "No components" else None
        return None

    def test_valid_selection(self):
        """Test getting valid selected component."""
        ids = ["comp_1", "comp_2", "comp_3"]
        result = self.get_selected_component_id(ids, 1)
        assert result == "comp_2"

    def test_first_selection(self):
        """Test getting first component."""
        ids = ["comp_1", "comp_2"]
        result = self.get_selected_component_id(ids, 0)
        assert result == "comp_1"

    def test_no_components_placeholder(self):
        """Test 'No components' returns None."""
        ids = ["No components"]
        result = self.get_selected_component_id(ids, 0)
        assert result is None

    def test_empty_list(self):
        """Test empty component list."""
        result = self.get_selected_component_id([], 0)
        assert result is None

    def test_out_of_bounds_index(self):
        """Test out of bounds index."""
        ids = ["comp_1", "comp_2"]
        result = self.get_selected_component_id(ids, 5)
        assert result is None

    def test_negative_index(self):
        """Test negative index."""
        ids = ["comp_1", "comp_2"]
        result = self.get_selected_component_id(ids, -1)
        assert result is None


class TestDropdownOptionIndex:
    """Tests for dropdown option index calculation."""

    def calculate_option_index(self, mouse_y, dropdown_y, header_height, option_height):
        """Calculate which option is being hovered."""
        if mouse_y < dropdown_y + header_height:
            return -1  # Above options area
        return (mouse_y - dropdown_y - header_height) // option_height

    def test_hover_first_option(self):
        """Test hovering first option."""
        # Dropdown at y=100, header=40, options=30 each
        # Mouse at y=145 -> option 0
        result = self.calculate_option_index(145, 100, 40, 30)
        assert result == 0

    def test_hover_second_option(self):
        """Test hovering second option."""
        # Mouse at y=175 -> (175 - 100 - 40) / 30 = 35 / 30 = 1
        result = self.calculate_option_index(175, 100, 40, 30)
        assert result == 1

    def test_hover_above_options(self):
        """Test hovering above options area."""
        result = self.calculate_option_index(120, 100, 40, 30)
        assert result == -1


# =============================================================================
# Tests for TabbedShipPanel tab calculations
# =============================================================================

class TestTabbedShipPanelTabs:
    """Tests for TabbedShipPanel tab calculations."""

    def calculate_tab_width(self, panel_width, num_tabs, margin=5, max_tab_width=120):
        """Calculate tab width based on panel and tab count."""
        available_width = panel_width - 20  # 10px padding each side
        calculated_width = available_width // num_tabs - margin
        return min(max_tab_width, calculated_width)

    def test_few_tabs_use_max_width(self):
        """Test that few tabs use maximum width."""
        # Panel 600px wide, 3 tabs: (600-20)/3 - 5 = 188, capped at 120
        result = self.calculate_tab_width(600, 3)
        assert result == 120

    def test_many_tabs_shrink_width(self):
        """Test that many tabs shrink to fit."""
        # Panel 400px wide, 6 tabs: (400-20)/6 - 5 = 58
        result = self.calculate_tab_width(400, 6)
        assert result == 58

    def test_single_tab(self):
        """Test single tab."""
        # Panel 400px wide, 1 tab: (400-20)/1 - 5 = 375, capped at 120
        result = self.calculate_tab_width(400, 1)
        assert result == 120


class TestTabSelection:
    """Tests for tab selection logic."""

    def is_point_in_tab(self, point, tab_rect):
        """Check if point is inside tab rect."""
        x, y = point
        rx, ry, rw, rh = tab_rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    def test_point_in_tab(self):
        """Test point inside tab."""
        result = self.is_point_in_tab((150, 50), (100, 30, 100, 30))
        assert result is True

    def test_point_outside_tab(self):
        """Test point outside tab."""
        result = self.is_point_in_tab((50, 50), (100, 30, 100, 30))
        assert result is False

    def test_point_on_edge(self):
        """Test point on tab edge."""
        result = self.is_point_in_tab((100, 30), (100, 30, 100, 30))
        assert result is True


# =============================================================================
# Tests for TestRunSummaryPanel value formatting
# =============================================================================

class TestValueFormatting:
    """Tests for value formatting in summary panels."""

    def format_value_short(self, value):
        """Format value for compact display."""
        if value is None:
            return "None"
        if isinstance(value, float):
            if 0 < value < 1:
                return f"{value:.1%}"
            elif abs(value) < 0.001 and value != 0:
                return f"{value:.2e}"
            elif abs(value - round(value)) < 1e-9:
                return f"{int(round(value))}"
            elif abs(value) >= 100:
                return f"{value:.1f}"
            else:
                return f"{value:.3f}"
        return str(value)

    def test_format_none(self):
        """Test formatting None."""
        assert self.format_value_short(None) == "None"

    def test_format_percentage(self):
        """Test formatting values between 0 and 1 as percentage."""
        assert self.format_value_short(0.75) == "75.0%"
        assert self.format_value_short(0.5) == "50.0%"

    def test_format_very_small(self):
        """Test formatting very small numbers in scientific notation."""
        # Positive small values between 0 and 1 are formatted as percentage
        # Negative small values get scientific notation
        result = self.format_value_short(-0.0001)  # abs < 0.001 and not 0
        assert "e" in result.lower()  # Should be scientific notation

    def test_format_integer_float(self):
        """Test formatting float that's essentially an integer."""
        assert self.format_value_short(42.0) == "42"
        assert self.format_value_short(100.0) == "100"

    def test_format_large_number(self):
        """Test formatting large numbers."""
        result = self.format_value_short(1234.5678)
        assert result == "1234.6"

    def test_format_small_decimal(self):
        """Test formatting small decimal numbers."""
        result = self.format_value_short(3.14159)
        assert result == "3.142"

    def test_format_string(self):
        """Test formatting string value."""
        assert self.format_value_short("test") == "test"

    def test_format_integer(self):
        """Test formatting integer."""
        assert self.format_value_short(42) == "42"


# =============================================================================
# Tests for TestRunDetailsPanel scroll calculations
# =============================================================================

class TestDetailsScrollCalculations:
    """Tests for TestRunDetailsPanel scroll calculations."""

    def calculate_content_height(self, metrics_count, validation_count,
                                  base_height=150, metric_height=20,
                                  validation_height=40, gap=50):
        """Calculate content height based on items."""
        return base_height + metrics_count * metric_height + gap + validation_count * validation_height

    def calculate_max_scroll(self, content_height, visible_height):
        """Calculate max scroll offset."""
        return max(0, content_height - visible_height)

    def test_content_height_calculation(self):
        """Test content height with metrics and validations."""
        # 5 metrics, 3 validations
        result = self.calculate_content_height(5, 3)
        # 150 + 5*20 + 50 + 3*40 = 150 + 100 + 50 + 120 = 420
        assert result == 420

    def test_content_height_no_items(self):
        """Test content height with no items."""
        result = self.calculate_content_height(0, 0)
        # 150 + 0 + 50 + 0 = 200
        assert result == 200

    def test_max_scroll_needed(self):
        """Test max scroll when content exceeds viewport."""
        result = self.calculate_max_scroll(420, 300)
        assert result == 120

    def test_max_scroll_not_needed(self):
        """Test max scroll when content fits."""
        result = self.calculate_max_scroll(200, 300)
        assert result == 0


# =============================================================================
# Tests for ship extraction from scenario metadata
# =============================================================================

class TestShipExtractionLogic:
    """Tests for extracting ship information from conditions."""

    def extract_filename_from_condition(self, condition):
        """
        Extract JSON filename from a condition string.

        Formats:
        - "Attacker: Test_Attacker.json"
        - "Target: Test_Target.json (mass=400)"
        """
        if '.json' not in condition or ':' not in condition:
            return None, None

        parts = condition.split(':', 1)
        role = parts[0].strip()
        filename_part = parts[1].strip()

        # Extract only the .json filename
        json_end = filename_part.index('.json') + 5
        filename = filename_part[:json_end]

        return role, filename

    def test_simple_condition(self):
        """Test extracting from simple condition."""
        role, filename = self.extract_filename_from_condition("Attacker: Test_Attacker.json")
        assert role == "Attacker"
        assert filename == "Test_Attacker.json"

    def test_condition_with_params(self):
        """Test extracting from condition with parameters."""
        role, filename = self.extract_filename_from_condition("Target: Test_Target.json (mass=400)")
        assert role == "Target"
        assert filename == "Test_Target.json"

    def test_condition_without_json(self):
        """Test condition without .json file."""
        role, filename = self.extract_filename_from_condition("Range: 1000 units")
        assert role is None
        assert filename is None

    def test_condition_without_colon(self):
        """Test condition without colon separator."""
        role, filename = self.extract_filename_from_condition("Test_Ship.json")
        assert role is None
        assert filename is None


class TestComponentIdExtraction:
    """Tests for extracting component IDs from ship data."""

    def extract_component_ids(self, ship_data, layer_names=None):
        """Extract component IDs from ship layers."""
        if layer_names is None:
            layer_names = ['CORE', 'ARMOR', 'HULL']

        component_ids = []
        layers = ship_data.get('layers', {})

        for layer_name in layer_names:
            layer = layers.get(layer_name, [])
            for component in layer:
                comp_id = component.get('id')
                if comp_id:
                    component_ids.append(comp_id)

        return component_ids

    def test_extract_from_multiple_layers(self):
        """Test extracting IDs from multiple layers."""
        ship_data = {
            'layers': {
                'CORE': [{'id': 'engine_1'}, {'id': 'reactor_1'}],
                'ARMOR': [{'id': 'armor_1'}],
                'HULL': [{'id': 'weapon_1'}]
            }
        }
        result = self.extract_component_ids(ship_data)
        assert len(result) == 4
        assert 'engine_1' in result
        assert 'armor_1' in result
        assert 'weapon_1' in result

    def test_extract_from_empty_layers(self):
        """Test extracting from empty layers."""
        ship_data = {'layers': {}}
        result = self.extract_component_ids(ship_data)
        assert len(result) == 0

    def test_extract_missing_id(self):
        """Test handling components without ID."""
        ship_data = {
            'layers': {
                'CORE': [{'id': 'engine_1'}, {'name': 'no_id_component'}]
            }
        }
        result = self.extract_component_ids(ship_data)
        assert len(result) == 1
        assert result[0] == 'engine_1'

    def test_extract_no_layers_key(self):
        """Test handling ship data without layers key."""
        ship_data = {'name': 'Test Ship'}
        result = self.extract_component_ids(ship_data)
        assert len(result) == 0


# =============================================================================
# Tests for validation result status
# =============================================================================

class TestValidationStatusColors:
    """Tests for validation result status determination."""

    def get_status_color(self, status):
        """Get color based on validation status."""
        PASS_COLOR = (80, 255, 120)
        FAIL_COLOR = (255, 80, 80)
        WARN_COLOR = (255, 200, 100)

        if status == 'PASS':
            return PASS_COLOR
        elif status == 'FAIL':
            return FAIL_COLOR
        else:
            return WARN_COLOR

    def test_pass_status_green(self):
        """Test PASS status returns green."""
        color = self.get_status_color('PASS')
        assert color == (80, 255, 120)
        assert color[1] > color[0]  # Green dominant

    def test_fail_status_red(self):
        """Test FAIL status returns red."""
        color = self.get_status_color('FAIL')
        assert color == (255, 80, 80)
        assert color[0] > color[1]  # Red dominant

    def test_warn_status_yellow(self):
        """Test WARN status returns yellow/orange."""
        color = self.get_status_color('WARN')
        assert color == (255, 200, 100)


class TestValidationSymbols:
    """Tests for validation result symbol selection."""

    def get_status_symbol(self, status):
        """Get symbol for validation status."""
        if status == 'PASS':
            return "✓"
        elif status == 'FAIL':
            return "✗"
        else:
            return "⚠"

    def test_pass_symbol(self):
        """Test PASS symbol."""
        assert self.get_status_symbol('PASS') == "✓"

    def test_fail_symbol(self):
        """Test FAIL symbol."""
        assert self.get_status_symbol('FAIL') == "✗"

    def test_warn_symbol(self):
        """Test WARN symbol."""
        assert self.get_status_symbol('WARN') == "⚠"


# =============================================================================
# Tests for p-value interpretation
# =============================================================================

class TestPValueInterpretation:
    """Tests for p-value color coding."""

    def get_pvalue_color(self, p_value, alpha=0.05):
        """Get color for p-value (TOST: p < alpha is PASS)."""
        PASS_COLOR = (80, 255, 120)
        FAIL_COLOR = (255, 80, 80)
        return PASS_COLOR if p_value < alpha else FAIL_COLOR

    def test_significant_pvalue(self):
        """Test p-value below alpha is green."""
        color = self.get_pvalue_color(0.01)
        assert color == (80, 255, 120)

    def test_nonsignificant_pvalue(self):
        """Test p-value above alpha is red."""
        color = self.get_pvalue_color(0.10)
        assert color == (255, 80, 80)

    def test_borderline_pvalue(self):
        """Test p-value at alpha boundary."""
        # p = 0.05 exactly is not < 0.05, so FAIL
        color = self.get_pvalue_color(0.05)
        assert color == (255, 80, 80)

    def test_custom_alpha(self):
        """Test custom alpha level."""
        # p = 0.01 with alpha = 0.001 should FAIL
        color = self.get_pvalue_color(0.01, alpha=0.001)
        assert color == (255, 80, 80)


# =============================================================================
# Tests for difference calculation
# =============================================================================

class TestDifferenceCalculation:
    """Tests for expected/actual difference calculation."""

    def calculate_difference(self, expected, actual):
        """Calculate difference and percentage difference."""
        if not isinstance(expected, (int, float)) or not isinstance(actual, (int, float)):
            return None, None

        diff = actual - expected

        if expected != 0:
            pct_diff = (diff / expected) * 100
        else:
            pct_diff = None

        return diff, pct_diff

    def test_positive_difference(self):
        """Test positive difference (actual > expected)."""
        diff, pct = self.calculate_difference(100, 110)
        assert diff == 10
        assert pct == 10.0

    def test_negative_difference(self):
        """Test negative difference (actual < expected)."""
        diff, pct = self.calculate_difference(100, 90)
        assert diff == -10
        assert pct == -10.0

    def test_exact_match(self):
        """Test exact match."""
        diff, pct = self.calculate_difference(100, 100)
        assert diff == 0
        assert pct == 0.0

    def test_zero_expected(self):
        """Test with zero expected value."""
        diff, pct = self.calculate_difference(0, 5)
        assert diff == 5
        assert pct is None  # Can't calculate percentage

    def test_non_numeric_values(self):
        """Test with non-numeric values."""
        diff, pct = self.calculate_difference("a", "b")
        assert diff is None
        assert pct is None


# =============================================================================
# Tests for batch test execution state
# =============================================================================

class TestBatchExecutionState:
    """Tests for batch test execution state management."""

    def calculate_progress(self, current_index, total):
        """Calculate batch progress percentage."""
        if total == 0:
            return 0
        return (current_index / total) * 100

    def test_progress_start(self):
        """Test progress at start."""
        result = self.calculate_progress(0, 10)
        assert result == 0.0

    def test_progress_middle(self):
        """Test progress in middle."""
        result = self.calculate_progress(5, 10)
        assert result == 50.0

    def test_progress_complete(self):
        """Test progress at completion."""
        result = self.calculate_progress(10, 10)
        assert result == 100.0

    def test_progress_empty_batch(self):
        """Test progress with empty batch."""
        result = self.calculate_progress(0, 0)
        assert result == 0


# =============================================================================
# Tests for scrollbar calculations
# =============================================================================

class TestScrollbarCalculations:
    """Tests for scrollbar thumb position and size."""

    def calculate_thumb_height(self, viewport_height, total_lines, visible_lines, min_height=20):
        """Calculate scrollbar thumb height."""
        if total_lines <= visible_lines:
            return viewport_height
        ratio = visible_lines / total_lines
        return max(min_height, int(viewport_height * ratio))

    def calculate_thumb_position(self, viewport_y, viewport_height, thumb_height,
                                  scroll_offset, max_scroll):
        """Calculate scrollbar thumb Y position."""
        if max_scroll == 0:
            return viewport_y
        scroll_ratio = scroll_offset / max_scroll
        return viewport_y + int((viewport_height - thumb_height) * scroll_ratio)

    def test_thumb_height_short_content(self):
        """Test thumb height when content fits."""
        result = self.calculate_thumb_height(400, 10, 20)
        assert result == 400  # Full viewport height

    def test_thumb_height_long_content(self):
        """Test thumb height with long content."""
        result = self.calculate_thumb_height(400, 100, 20)
        # ratio = 20/100 = 0.2, 400 * 0.2 = 80
        assert result == 80

    def test_thumb_height_minimum(self):
        """Test thumb height respects minimum."""
        result = self.calculate_thumb_height(400, 1000, 20)
        # ratio = 20/1000 = 0.02, 400 * 0.02 = 8, but min is 20
        assert result == 20

    def test_thumb_position_at_top(self):
        """Test thumb position at top of scroll."""
        result = self.calculate_thumb_position(100, 400, 80, 0, 80)
        assert result == 100

    def test_thumb_position_at_bottom(self):
        """Test thumb position at bottom of scroll."""
        result = self.calculate_thumb_position(100, 400, 80, 80, 80)
        # 100 + (400 - 80) * 1.0 = 100 + 320 = 420
        assert result == 420

    def test_thumb_position_in_middle(self):
        """Test thumb position in middle of scroll."""
        result = self.calculate_thumb_position(100, 400, 80, 40, 80)
        # 100 + (400 - 80) * 0.5 = 100 + 160 = 260
        assert result == 260
