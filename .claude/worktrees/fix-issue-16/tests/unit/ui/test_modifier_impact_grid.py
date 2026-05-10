"""Tests for ModifierImpactGrid widget."""
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch


class TestModifierImpactGrid:
    """Test the ModifierImpactGrid widget for displaying modifier effects."""

    def setup_method(self):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        self.manager = pygame_gui.UIManager((800, 600))
        self.container = pygame_gui.elements.UIPanel(
            pygame.Rect(0, 0, 500, 400), manager=self.manager
        )

    def teardown_method(self):
        pass  # Don't quit pygame for session isolation

    def test_init_creates_panel(self):
        """Test that constructor creates a panel."""
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid

        rect = pygame.Rect(10, 10, 400, 300)
        grid = ModifierImpactGrid(self.manager, self.container, rect)

        assert grid.panel is not None
        assert grid.rect == rect

    def test_update_with_no_component(self):
        """Test update with None component shows placeholder."""
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid

        rect = pygame.Rect(10, 10, 400, 300)
        grid = ModifierImpactGrid(self.manager, self.container, rect)

        # Should not raise
        grid.update(None)
        assert grid.current_component is None

    def test_update_with_component_no_modifiers(self):
        """Test update with component that has no modifiers."""
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid

        rect = pygame.Rect(10, 10, 400, 300)
        grid = ModifierImpactGrid(self.manager, self.container, rect)

        mock_component = MagicMock()
        mock_component.modifiers = []
        mock_component.get_all_modifier_effects.return_value = []
        mock_component.get_modifier_stat_summary.return_value = {}

        grid.update(mock_component)

        assert grid.current_component == mock_component

    def test_update_with_component_with_modifiers(self):
        """Test update with component that has modifiers."""
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid
        from game.simulation.components.modifier_effects import ModifierEffect

        rect = pygame.Rect(10, 10, 400, 300)
        grid = ModifierImpactGrid(self.manager, self.container, rect)

        # Create mock modifier effects
        effect1 = ModifierEffect(
            stat_key='mass_mult',
            value=2.0,
            operation='multiply',
            target_ability=None,
            source_modifier_id='simple_size_mount',
            source_modifier_name='Size Mount',
            formula_str='param',
            param_value=2.0
        )
        effect2 = ModifierEffect(
            stat_key='hp_mult',
            value=2.0,
            operation='multiply',
            target_ability=None,
            source_modifier_id='simple_size_mount',
            source_modifier_name='Size Mount',
            formula_str='param',
            param_value=2.0
        )

        mock_component = MagicMock()
        mock_mod = MagicMock()
        mock_mod.definition.id = 'simple_size_mount'
        mock_mod.definition.name = 'Size Mount'
        mock_mod.value = 2.0
        mock_component.modifiers = [mock_mod]
        mock_component.get_all_modifier_effects.return_value = [effect1, effect2]
        mock_component.get_modifier_stat_summary.return_value = {
            'mass_mult': {'net_value': 2.0, 'operation': 'multiply', 'contributors': []},
            'hp_mult': {'net_value': 2.0, 'operation': 'multiply', 'contributors': []}
        }

        grid.update(mock_component)

        assert grid.current_component == mock_component
        # Grid should have identified stats to display
        assert len(grid.stat_columns) > 0

    def test_get_affected_stats(self):
        """Test that get_affected_stats returns only modified stats."""
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid

        rect = pygame.Rect(10, 10, 400, 300)
        grid = ModifierImpactGrid(self.manager, self.container, rect)

        summary = {
            'mass_mult': {'net_value': 2.0, 'operation': 'multiply', 'contributors': []},
            'hp_mult': {'net_value': 1.0, 'operation': 'multiply', 'contributors': []},  # No change
            'damage_mult': {'net_value': 1.5, 'operation': 'multiply', 'contributors': []},
            'arc_add': {'net_value': 0.0, 'operation': 'add', 'contributors': []},  # No change
        }

        affected = grid._get_affected_stats(summary)

        # Should only return stats that differ from default
        assert 'mass_mult' in affected
        assert 'damage_mult' in affected
        assert 'hp_mult' not in affected  # 1.0 is default for multiply
        assert 'arc_add' not in affected  # 0.0 is default for add

    def test_format_stat_name(self):
        """Test stat name formatting for display."""
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid

        rect = pygame.Rect(10, 10, 400, 300)
        grid = ModifierImpactGrid(self.manager, self.container, rect)

        assert grid._format_stat_name('mass_mult') == 'Mass'
        assert grid._format_stat_name('hp_mult') == 'HP'
        assert grid._format_stat_name('damage_mult') == 'Damage'
        assert grid._format_stat_name('arc_add') == 'Arc'

    def test_format_value_multiply(self):
        """Test value formatting for multiply operations."""
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid

        rect = pygame.Rect(10, 10, 400, 300)
        grid = ModifierImpactGrid(self.manager, self.container, rect)

        assert grid._format_value(2.0, 'multiply') == 'x2.000'
        assert grid._format_value(0.5, 'multiply') == 'x0.500'
        # 4 significant digits tests
        assert grid._format_value(73.73, 'multiply') == 'x73.73'  # 2 decimals for 10-99
        assert grid._format_value(1000.73, 'multiply') == 'x1001'  # No decimals for >=1000
        assert grid._format_value(350.76, 'multiply') == 'x350.8'  # 1 decimal for 100-999

    def test_format_value_add(self):
        """Test value formatting for add operations."""
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid

        rect = pygame.Rect(10, 10, 400, 300)
        grid = ModifierImpactGrid(self.manager, self.container, rect)

        assert grid._format_value(90.0, 'add') == '+90.00'
        assert grid._format_value(-10.0, 'add') == '-10.00'

    def test_kill_cleans_up_elements(self):
        """Test that kill() properly cleans up UI elements."""
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid

        rect = pygame.Rect(10, 10, 400, 300)
        grid = ModifierImpactGrid(self.manager, self.container, rect)

        # Create some mock component to generate UI elements
        mock_component = MagicMock()
        mock_component.modifiers = []
        mock_component.get_all_modifier_effects.return_value = []
        mock_component.get_modifier_stat_summary.return_value = {}
        grid.update(mock_component)

        # Kill should not raise
        grid.kill()

        # Panel should be killed
        assert not grid.panel.alive()
