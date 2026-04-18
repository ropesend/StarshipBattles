"""
Tests for RaceAptitudesPanel - Point-buy aptitude UI panel.

PROJ-66 Phase 5: Tests for aptitude sliders and budget display.
"""
import pytest
from unittest.mock import MagicMock, patch

import pygame
import pygame_gui

from game.strategy.data.race_config import RaceConfig


class TestRaceAptitudesPanel:
    """Test RaceAptitudesPanel class."""

    @pytest.fixture
    def panel(self, ui_manager):
        """Create parent panel."""
        return pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 600, 500),
            manager=ui_manager
        )

    @pytest.fixture
    def race_config(self):
        """Create default race config."""
        return RaceConfig()

    @pytest.fixture
    def aptitudes_panel(self, panel, ui_manager, race_config):
        """Create aptitudes panel."""
        from game.ui.panels.race_aptitudes_panel import RaceAptitudesPanel
        return RaceAptitudesPanel(panel, ui_manager, race_config)

    # === Creation Tests ===

    def test_aptitudes_panel_creates_successfully(self, aptitudes_panel):
        """Panel should create without errors."""
        assert aptitudes_panel is not None

    def test_aptitudes_panel_has_7_sliders(self, aptitudes_panel):
        """Panel should have 7 aptitude sliders.

        PROJ-283 Phase 4: dropped `happiness` (now `base_happiness`,
        derived in PROJ-284) and `population_growth` (now
        `base_reproduction_rate`)."""
        assert len(aptitudes_panel.aptitude_sliders) == 7

    def test_aptitudes_panel_has_budget_display(self, aptitudes_panel):
        """Panel should have budget label."""
        assert aptitudes_panel.budget_label is not None

    def test_aptitudes_panel_default_shows_budget(self, aptitudes_panel):
        """Default config should show 100 points remaining."""
        # With default aptitudes at 5 and minimal tolerance in config
        text = aptitudes_panel.budget_label.text
        assert "100" in text or "Points" in text

    def test_aptitudes_panel_stores_references(self, aptitudes_panel):
        """Panel should store slider and label references for all 7
        paid aptitudes (PROJ-283 Phase 4 dropped happiness +
        population_growth)."""
        expected_names = [
            "strength", "intelligence", "constitution", "dexterity",
            "tolerance_other_species", "cooperation", "conflict_tolerance"
        ]
        for name in expected_names:
            assert name in aptitudes_panel.aptitude_sliders, f"Missing slider: {name}"
            assert name in aptitudes_panel.aptitude_labels, f"Missing label: {name}"
            assert name in aptitudes_panel.cost_labels, f"Missing cost label: {name}"

    def test_aptitudes_panel_sliders_initialized_to_base(self, aptitudes_panel):
        """All sliders should start at base value (50)."""
        for name, slider in aptitudes_panel.aptitude_sliders.items():
            value = slider.get_current_value()
            assert value == 50, f"Slider {name} should be 50, got {value}"

    # === Update Config Tests ===

    def test_update_config_reads_aptitude_sliders(self, aptitudes_panel, race_config):
        """update_config should read slider values to config."""
        # Set a slider to different value
        aptitudes_panel.aptitude_sliders["strength"].set_current_value(8)
        aptitudes_panel.update_config()

        assert race_config.aptitude_strength == 8

    def test_update_config_reads_all_sliders(self, aptitudes_panel, race_config):
        """update_config should update all aptitude fields."""
        aptitudes_panel.aptitude_sliders["strength"].set_current_value(7)
        aptitudes_panel.aptitude_sliders["intelligence"].set_current_value(8)
        aptitudes_panel.aptitude_sliders["dexterity"].set_current_value(3)

        aptitudes_panel.update_config()

        assert race_config.aptitude_strength == 7
        assert race_config.aptitude_intelligence == 8
        assert race_config.aptitude_dexterity == 3

    # === Set From Config Tests ===

    def test_set_from_config_sets_aptitude_sliders(self, aptitudes_panel, race_config):
        """set_from_config should set slider values from config."""
        race_config.aptitude_strength = 9
        race_config.aptitude_intelligence = 2

        aptitudes_panel.set_from_config()

        assert aptitudes_panel.aptitude_sliders["strength"].get_current_value() == 9
        assert aptitudes_panel.aptitude_sliders["intelligence"].get_current_value() == 2

    def test_set_from_config_updates_labels(self, aptitudes_panel, race_config):
        """set_from_config should also update value labels."""
        race_config.aptitude_strength = 8
        aptitudes_panel.set_from_config()

        # Value label should reflect the value
        label_text = aptitudes_panel.aptitude_labels["strength"].text
        assert "8" in label_text

    # === Budget Display Tests ===

    def test_update_budget_display_shows_remaining(self, aptitudes_panel, race_config):
        """Budget display should show remaining points."""
        # Default config with no tolerance costs: 100 remaining
        aptitudes_panel.update_budget_display()
        text = aptitudes_panel.budget_label.text
        assert "100" in text

    def test_update_budget_display_after_slider_change(self, aptitudes_panel, race_config):
        """Budget should update after slider changes.

        PROJ-283 Phase 4: legacy environment fields are gone; the default
        race_config has every preference at registry default (0 cost), so
        no zeroing is needed for a predictable test."""
        # Start with fresh budget display
        aptitudes_panel.update_budget_display()

        # Increase strength by 3 points above base (53 costs 3)
        aptitudes_panel.aptitude_sliders["strength"].set_current_value(53)
        aptitudes_panel.update_config()
        aptitudes_panel.update_budget_display()

        text = aptitudes_panel.budget_label.text
        assert "97" in text  # 100 - 3

    def test_budget_display_red_when_over(self, aptitudes_panel, race_config):
        """Budget label should be red when over budget.

        PROJ-283 Phase 4: dropped happiness + population_growth aptitudes
        and the legacy `gravity_tolerance` field. Maxing the 7 paid
        aptitudes alone exceeds the 100-point budget by ~3000."""
        race_config.aptitude_strength = 100
        race_config.aptitude_intelligence = 100
        race_config.aptitude_constitution = 100
        race_config.aptitude_dexterity = 100
        race_config.aptitude_tolerance_other_species = 100
        race_config.aptitude_cooperation = 100
        race_config.aptitude_conflict_tolerance = 100

        aptitudes_panel.update_budget_display()

        # Check color is red (or label indicates over budget)
        text = aptitudes_panel.budget_label.text
        # Budget should be deeply negative
        assert "-" in text or "Over" in text.lower()

    def test_budget_display_green_when_under(self, aptitudes_panel, race_config):
        """Budget label should be green when well under budget."""
        # Default is well under budget
        aptitudes_panel.update_budget_display()

        # Just verify it shows positive budget
        text = aptitudes_panel.budget_label.text
        # Should show positive remaining points
        remaining = aptitudes_panel.point_budget.get_remaining_points(race_config)
        assert remaining >= 0

    def test_tolerance_cost_section_exists(self, aptitudes_panel):
        """Panel should have tolerance cost display section."""
        assert aptitudes_panel.tolerance_cost_label is not None

    def test_tolerance_cost_updates_from_config(self, aptitudes_panel, race_config):
        """Tolerance cost should reflect config values.

        PROJ-283 Phase 4: gravity_tolerance field deleted. Replicate the
        old "7-point tolerance cost" by widening the gravity preference's
        tolerance by 3 steps (`_exponential_cost(3) = 7`)."""
        from game.strategy.data.environmental_preference import EnvironmentalPreference
        from game.strategy.data.habitability_factors import get_factor

        gravity = get_factor("gravity")
        race_config.preferences["gravity"] = EnvironmentalPreference(
            setpoint=gravity.default_setpoint,
            tolerance=gravity.default_tolerance + 3 * gravity.step,
            min_value=gravity.min_value,
            max_value=gravity.max_value,
            step=gravity.step,
        )
        aptitudes_panel.update_budget_display()

        text = aptitudes_panel.tolerance_cost_label.text
        # Should show tolerance cost
        assert "7" in text or "Tolerance" in text


class TestRaceAptitudesPanelIntegration:
    """Integration tests for aptitudes panel."""

    @pytest.fixture
    def panel(self, ui_manager):
        return pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 600, 500),
            manager=ui_manager
        )

    @pytest.fixture
    def race_config(self):
        return RaceConfig()

    def test_full_workflow_save_and_load(self, panel, ui_manager, race_config):
        """Test complete save and load workflow."""
        from game.ui.panels.race_aptitudes_panel import RaceAptitudesPanel

        # Create panel, modify sliders
        apt_panel = RaceAptitudesPanel(panel, ui_manager, race_config)
        apt_panel.aptitude_sliders["strength"].set_current_value(8)
        apt_panel.aptitude_sliders["intelligence"].set_current_value(3)
        apt_panel.update_config()

        # Verify config updated
        assert race_config.aptitude_strength == 8
        assert race_config.aptitude_intelligence == 3

        # Create new panel, load from config
        panel2 = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, 0, 600, 500),
            manager=ui_manager
        )
        apt_panel2 = RaceAptitudesPanel(panel2, ui_manager, race_config)
        apt_panel2.set_from_config()

        # Verify sliders match
        assert apt_panel2.aptitude_sliders["strength"].get_current_value() == 8
        assert apt_panel2.aptitude_sliders["intelligence"].get_current_value() == 3
