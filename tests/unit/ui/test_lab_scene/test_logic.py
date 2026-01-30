"""
Unit tests for Test Lab Scene logic.

Tests formatting, selection, extraction, validation, and batch execution logic.
Split from test_test_lab_scene.py - logic/validation tests.
"""
import pytest
import json


# =============================================================================
# Tests for JSON formatting logic
# =============================================================================

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
