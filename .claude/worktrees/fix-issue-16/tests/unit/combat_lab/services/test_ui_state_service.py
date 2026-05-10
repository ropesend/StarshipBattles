"""
Unit tests for UIStateService.

Covers selection (category / group / test), group expansion, hover state,
headless running flag, tag filters, and seed control. Each of these is a
live consumer of the service — the service itself is pure state with no
observer or notification side-effects.
"""

import pytest
from combat_lab.services.ui_state_service import UIStateService


class TestUIStateServiceInit:
    """Default state after construction."""

    def test_init_defaults(self):
        service = UIStateService()

        assert service.get_selected_category() is None
        assert service.get_selected_test_id() is None
        assert service.get_selected_group() is None
        assert service.get_category_hover() is None
        assert service.get_test_hover() is None
        assert service.is_headless_running() is False
        assert service.get_seed_mode() == "random"
        assert service.get_custom_seed() is None
        assert service.get_active_tag_filters() == []
        assert service.get_excluded_tags() == []


class TestCategorySelection:
    """Category selection."""

    def test_select_category(self):
        service = UIStateService()
        service.select_category("Beam Weapons")
        assert service.get_selected_category() == "Beam Weapons"

    def test_select_category_clears_test(self):
        service = UIStateService()
        service.select_test("TEST-001")
        service.select_category("Beam Weapons")
        assert service.get_selected_test_id() is None

    def test_select_category_clears_group(self):
        service = UIStateService()
        service.select_group("Propulsion")
        service.select_category("Beam Weapons")
        assert service.get_selected_group() is None

    def test_select_category_none(self):
        service = UIStateService()
        service.select_category("Beam Weapons")
        service.select_category(None)
        assert service.get_selected_category() is None

    def test_select_category_changes_value(self):
        service = UIStateService()
        service.select_category("Beam Weapons")
        service.select_category("Seeker Weapons")
        assert service.get_selected_category() == "Seeker Weapons"


class TestGroupSelection:
    """Group selection."""

    def test_select_group(self):
        service = UIStateService()
        service.select_group("Weapons")
        assert service.get_selected_group() == "Weapons"

    def test_select_group_clears_category_and_test(self):
        service = UIStateService()
        service.select_category("Beam Weapons")
        service.select_test("TEST-001")
        service.select_group("Weapons")
        assert service.get_selected_category() is None
        assert service.get_selected_test_id() is None


class TestGroupExpansion:
    """Sidebar group expand/collapse state."""

    def test_toggle_group_expands_then_collapses(self):
        service = UIStateService()
        assert service.is_group_expanded("Weapons") is False

        service.toggle_group("Weapons")
        assert service.is_group_expanded("Weapons") is True

        service.toggle_group("Weapons")
        assert service.is_group_expanded("Weapons") is False

    def test_multiple_groups_independent(self):
        service = UIStateService()
        service.toggle_group("Weapons")
        service.toggle_group("Defense")

        assert service.is_group_expanded("Weapons") is True
        assert service.is_group_expanded("Defense") is True
        assert service.is_group_expanded("Propulsion") is False


class TestTestSelection:
    """Test selection."""

    def test_select_test(self):
        service = UIStateService()
        service.select_test("TEST-001")
        assert service.get_selected_test_id() == "TEST-001"

    def test_select_test_none(self):
        service = UIStateService()
        service.select_test("TEST-001")
        service.select_test(None)
        assert service.get_selected_test_id() is None

    def test_select_test_changes_value(self):
        service = UIStateService()
        service.select_test("TEST-001")
        service.select_test("TEST-002")
        assert service.get_selected_test_id() == "TEST-002"


class TestHoverState:
    """Hover tracking for UI highlights."""

    def test_set_category_hover(self):
        service = UIStateService()
        service.set_category_hover("Beam Weapons")
        assert service.get_category_hover() == "Beam Weapons"

    def test_set_category_hover_none(self):
        service = UIStateService()
        service.set_category_hover("Beam Weapons")
        service.set_category_hover(None)
        assert service.get_category_hover() is None

    def test_set_test_hover(self):
        service = UIStateService()
        service.set_test_hover("TEST-001")
        assert service.get_test_hover() == "TEST-001"

    def test_set_test_hover_none(self):
        service = UIStateService()
        service.set_test_hover("TEST-001")
        service.set_test_hover(None)
        assert service.get_test_hover() is None


class TestHeadlessRunningState:
    """Headless test running flag."""

    def test_set_headless_running_true(self):
        service = UIStateService()
        service.set_headless_running(True)
        assert service.is_headless_running() is True

    def test_set_headless_running_false(self):
        service = UIStateService()
        service.set_headless_running(True)
        service.set_headless_running(False)
        assert service.is_headless_running() is False


class TestTagFilters:
    """Three-state tag filter: neutral -> include -> exclude -> neutral."""

    def test_cycle_neutral_to_include(self):
        service = UIStateService()
        service.cycle_tag_state("accuracy")

        assert service.is_tag_active("accuracy") is True
        assert service.is_tag_excluded("accuracy") is False
        assert service.get_active_tag_filters() == ["accuracy"]
        assert service.get_excluded_tags() == []

    def test_cycle_include_to_exclude(self):
        service = UIStateService()
        service.cycle_tag_state("accuracy")  # include
        service.cycle_tag_state("accuracy")  # exclude

        assert service.is_tag_active("accuracy") is False
        assert service.is_tag_excluded("accuracy") is True
        assert service.get_active_tag_filters() == []
        assert service.get_excluded_tags() == ["accuracy"]

    def test_cycle_exclude_to_neutral(self):
        service = UIStateService()
        service.cycle_tag_state("accuracy")  # include
        service.cycle_tag_state("accuracy")  # exclude
        service.cycle_tag_state("accuracy")  # back to neutral

        assert service.is_tag_active("accuracy") is False
        assert service.is_tag_excluded("accuracy") is False

    def test_clear_tag_filters(self):
        service = UIStateService()
        service.cycle_tag_state("accuracy")
        service.cycle_tag_state("range")
        service.cycle_tag_state("range")  # exclude

        service.clear_tag_filters()

        assert service.get_active_tag_filters() == []
        assert service.get_excluded_tags() == []

    def test_multiple_tags_independent(self):
        service = UIStateService()
        service.cycle_tag_state("accuracy")  # include
        service.cycle_tag_state("range")
        service.cycle_tag_state("range")  # exclude

        assert service.is_tag_active("accuracy") is True
        assert service.is_tag_excluded("range") is True

    def test_get_active_tag_filters_returns_copy(self):
        service = UIStateService()
        service.cycle_tag_state("accuracy")

        filters = service.get_active_tag_filters()
        filters.append("mutation")

        assert service.get_active_tag_filters() == ["accuracy"]

    def test_get_excluded_tags_returns_copy(self):
        service = UIStateService()
        service.cycle_tag_state("accuracy")
        service.cycle_tag_state("accuracy")  # exclude

        excluded = service.get_excluded_tags()
        excluded.append("mutation")

        assert service.get_excluded_tags() == ["accuracy"]


class TestSeedControl:
    """Seed mode + custom-seed state used by test execution."""

    def test_default_seed_mode_is_random(self):
        service = UIStateService()
        assert service.get_seed_mode() == "random"

    def test_set_seed_mode_metadata(self):
        service = UIStateService()
        service.set_seed_mode("metadata")
        assert service.get_seed_mode() == "metadata"

    def test_set_seed_mode_invalid_raises(self):
        service = UIStateService()
        with pytest.raises(ValueError):
            service.set_seed_mode("bogus")

    def test_set_custom_seed_switches_mode_to_custom(self):
        service = UIStateService()
        service.set_custom_seed(12345)

        assert service.get_custom_seed() == 12345
        assert service.get_seed_mode() == "custom"

    def test_set_custom_seed_none_does_not_switch_mode(self):
        service = UIStateService()
        service.set_seed_mode("metadata")
        service.set_custom_seed(None)

        assert service.get_custom_seed() is None
        assert service.get_seed_mode() == "metadata"

    def test_get_effective_seed_metadata_mode(self):
        service = UIStateService()
        service.set_seed_mode("metadata")
        assert service.get_effective_seed(42) == 42

    def test_get_effective_seed_custom_mode(self):
        service = UIStateService()
        service.set_custom_seed(9999)
        assert service.get_effective_seed(42) == 9999

    def test_get_effective_seed_random_mode_ignores_metadata(self):
        service = UIStateService()  # default mode is random
        seed = service.get_effective_seed(42)

        assert 0 <= seed < 2**31
        # random seeds should not equal the metadata seed by coincidence
        # (this is not guaranteed but extremely likely)


class TestResetSelection:
    """reset_selection clears category, test, and group."""

    def test_reset_selection_clears_everything(self):
        service = UIStateService()
        service.select_category("Beam Weapons")
        service.select_test("TEST-001")
        service.select_group("Weapons")

        service.reset_selection()

        assert service.get_selected_category() is None
        assert service.get_selected_test_id() is None
        assert service.get_selected_group() is None


class TestComplexStateTransitions:
    """Cross-cutting behaviour of multiple state fields."""

    def test_category_change_clears_only_test_selection(self):
        service = UIStateService()
        service.select_category("Beam Weapons")
        service.select_test("TEST-001")
        service.set_category_hover("Seeker Weapons")
        service.set_test_hover("TEST-002")

        service.select_category("Projectile Weapons")

        assert service.get_selected_category() == "Projectile Weapons"
        assert service.get_selected_test_id() is None
        # Hover state is independent of selection
        assert service.get_category_hover() == "Seeker Weapons"
        assert service.get_test_hover() == "TEST-002"
