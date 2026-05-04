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

    def test_init_constructs_panel_with_passed_rect_and_container(self):
        """Pin that __init__ forwards `rect` and `container` to the
        UIPanel constructor and exposes them as instance attributes used
        by draw() / handle_event() (rect for hit-testing, panel for
        get_abs_rect()). Replaces a tautology (`grid.rect == rect`,
        `grid.panel is not None`) with a real plumbing check."""
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid

        rect = pygame.Rect(10, 10, 400, 300)
        with patch('game.ui.panels.modifier_impact_grid.UIPanel') as mock_panel_cls:
            ModifierImpactGrid(self.manager, self.container, rect)
        # UIPanel was called once with the passed rect, manager, container,
        # and the production-stable object_id used for theming.
        kwargs = mock_panel_cls.call_args.kwargs
        assert kwargs['relative_rect'] is rect
        assert kwargs['manager'] is self.manager
        assert kwargs['container'] is self.container
        assert kwargs['object_id'] == '#modifier_impact_grid'

    def test_update_with_no_component_does_not_call_summary_methods(self):
        """`update(None)` must short-circuit BEFORE calling
        `get_modifier_stat_summary` or `get_all_modifier_effects` —
        guarding against the pre-condition that those methods don't
        exist on a None component. Pins the production guard at
        modifier_impact_grid.py:112 (`if not component: return`)."""
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid

        rect = pygame.Rect(10, 10, 400, 300)
        grid = ModifierImpactGrid(self.manager, self.container, rect)
        # Seed state that update() would otherwise overwrite.
        grid.stat_columns = ['old_stat']
        grid.modifier_rows = [{'id': 'old', 'name': 'old', 'stats': {}}]

        grid.update(None)

        # The early-return clears state to empty rather than leaving stale.
        assert grid.current_component is None
        assert grid.stat_columns == []
        assert grid.modifier_rows == []

    def test_update_with_no_affected_stats_renders_empty_message_label(self):
        """When the component has zero affected stats (empty summary),
        `_build_ui` renders a 'No modifier effects to display' message
        label. Pin that branch directly via _ui_elements rather than
        merely checking `current_component == mock`."""
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid

        rect = pygame.Rect(10, 10, 400, 300)
        grid = ModifierImpactGrid(self.manager, self.container, rect)

        mock_component = MagicMock()
        mock_component.ability_instances = []
        mock_component.get_all_modifier_effects.return_value = []
        mock_component.get_modifier_stat_summary.return_value = {}

        with patch('game.ui.panels.modifier_impact_grid.UILabel') as mock_label:
            grid.update(mock_component)

        # _build_ui took the empty-message branch (one UILabel call with
        # the no-effects text).
        mock_label.assert_called_once()
        assert mock_label.call_args.kwargs['text'] == "No modifier effects to display"
        assert grid.stat_columns == []  # confirms the empty-affected branch

    def test_update_with_modifiers_groups_effects_by_source_modifier_id(self):
        """When a component returns multiple ModifierEffects from the
        same source modifier, `update` must coalesce them into a SINGLE
        modifier_rows entry (keyed by source_modifier_id) whose 'stats'
        dict carries one entry per stat_key. Pin the grouping logic at
        modifier_impact_grid.py:130-148 instead of the trivial
        `current_component == mock_component` check."""
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid
        from game.simulation.components.modifier_effects import ModifierEffect

        rect = pygame.Rect(10, 10, 400, 300)
        grid = ModifierImpactGrid(self.manager, self.container, rect)

        eff_mass = ModifierEffect(
            stat_key='mass_mult', value=2.0, operation='multiply',
            target_ability=None, source_modifier_id='size_mount',
            source_modifier_name='Size Mount', formula_str='param',
            param_value=2.0,
        )
        eff_hp = ModifierEffect(
            stat_key='hp_mult', value=2.0, operation='multiply',
            target_ability=None, source_modifier_id='size_mount',
            source_modifier_name='Size Mount', formula_str='param',
            param_value=2.0,
        )

        mock_component = MagicMock()
        mock_component.ability_instances = []
        mock_component.get_all_modifier_effects.return_value = [eff_mass, eff_hp]
        mock_component.get_modifier_stat_summary.return_value = {
            'mass_mult': {'net_value': 2.0, 'operation': 'multiply', 'contributors': []},
            'hp_mult': {'net_value': 2.0, 'operation': 'multiply', 'contributors': []},
        }

        grid.update(mock_component)

        # Both effects came from the same source → exactly one row.
        assert len(grid.modifier_rows) == 1
        row = grid.modifier_rows[0]
        assert row['id'] == 'size_mount'
        assert row['name'] == 'Size Mount'
        # Both stat_keys present in the merged stats dict.
        assert set(row['stats'].keys()) == {'mass_mult', 'hp_mult'}
        # Both stats are surfaced in the column set.
        assert set(grid.stat_columns) == {'mass_mult', 'hp_mult'}

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


# =============================================================================
# PROJ-339: Characterization tests
# =============================================================================


class TestPROJ339Characterization:
    """PROJ-339: pin observable behavior of `update`, formatters, and
    scroll gating in ModifierImpactGrid."""

    def setup_method(self):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        self.manager = pygame_gui.UIManager((800, 600))
        self.container = pygame_gui.elements.UIPanel(
            pygame.Rect(0, 0, 500, 400), manager=self.manager,
        )

    def teardown_method(self):
        pass

    def _grid(self):
        from game.ui.panels.modifier_impact_grid import ModifierImpactGrid

        return ModifierImpactGrid(
            self.manager, self.container, pygame.Rect(10, 10, 400, 300),
        )

    # -- Top 3 ---------------------------------------------------------

    def test_update_filters_columns_to_consumed_stats(self):
        """A bridge-like component (no weapon abilities) should NOT
        surface weapon-binding stats like 'damage_mult' in stat_columns,
        even though the modifier summary contains them. Universal stats
        (mass/hp/cost) always pass through the filter."""
        grid = self._grid()

        # Mock a bridge-like component: no abilities -> only universal
        # stats are in the consumed-stats set.
        mock_component = MagicMock()
        mock_component.ability_instances = []
        mock_component.get_all_modifier_effects.return_value = []
        mock_component.get_modifier_stat_summary.return_value = {
            'mass_mult': {'net_value': 1.5, 'operation': 'multiply', 'contributors': []},
            'damage_mult': {'net_value': 2.0, 'operation': 'multiply', 'contributors': []},
        }

        grid.update(mock_component)

        # mass_mult is universal, damage_mult is weapon-binding.
        assert 'mass_mult' in grid.stat_columns
        assert 'damage_mult' not in grid.stat_columns

    def test_format_value_prefixes_per_operation(self):
        """`_format_value` prefix-rule pinning across operations."""
        grid = self._grid()
        # multiply uses 'x' prefix
        assert grid._format_value(1.5, 'multiply') == "x1.500"
        # add with positive value uses '+' prefix
        assert grid._format_value(50, 'add') == "+50.00"
        # add with negative value emits the raw sign (no '+')
        assert grid._format_value(-1, 'add') == "-1.000"
        # set uses '=' prefix
        assert grid._format_value(7, 'set') == "=7.000"

    def test_format_sig_digits_precision_tiers_for_positive_values(self):
        """Positive-value precision tier boundaries."""
        grid = self._grid()
        # Zero special-cases to "0"
        assert grid._format_sig_digits(0) == "0"
        # >= 1000 -> no decimals (int round)
        assert grid._format_sig_digits(1000) == "1000"
        assert grid._format_sig_digits(1500) == "1500"
        # 100..999 -> 1 dp
        assert grid._format_sig_digits(100) == "100.0"
        assert grid._format_sig_digits(999) == "999.0"
        # 10..99 -> 2 dp
        assert grid._format_sig_digits(10) == "10.00"
        assert grid._format_sig_digits(99) == "99.00"
        # 0 < v < 10 -> 3 dp
        assert grid._format_sig_digits(5) == "5.000"
        assert grid._format_sig_digits(0.5) == "0.500"

    def test_format_sig_digits_negative_values_use_same_tier_boundaries(self):
        """MIN-004: pin observed precision-tier behavior on negative
        values. Production uses `abs(value)` for the tier check, so
        negatives match positive tier widths.

        Pinned cases:
            -1000 -> '-1000'   (no decimals, >= 1000 tier)
            -500  -> '-500.0'  (1 dp, 100-999 tier)
            -5    -> '-5.000'  (3 dp, < 10 tier)
            -0.001 -> '-0.001' (3 dp, < 10 tier)
        """
        grid = self._grid()
        assert grid._format_sig_digits(-1000) == "-1000"
        assert grid._format_sig_digits(-500) == "-500.0"
        assert grid._format_sig_digits(-5) == "-5.000"
        assert grid._format_sig_digits(-0.001) == "-0.001"

    # -- Gap-fillers ---------------------------------------------------

    def test_update_with_none_clears_columns_and_rows(self):
        """`update(None)` clears stat_columns and modifier_rows so the
        grid renders empty on the next draw."""
        grid = self._grid()
        # Seed some state to ensure clearing actually empties the lists.
        grid.stat_columns = ['mass_mult', 'damage_mult']
        grid.modifier_rows = [{'id': 'x', 'name': 'X', 'stats': {}}]

        grid.update(None)

        assert grid.stat_columns == []
        assert grid.modifier_rows == []
        assert grid.current_component is None

    def test_get_value_color_neutral_for_default_multiply(self):
        """`_get_value_color(1.0, 'multiply')` is the neutral color
        (NOT buff or debuff). The `_get_affected_stats` filter excludes
        any stat whose net_value is exactly 1.0 within 0.001 tolerance."""
        grid = self._grid()
        # 1.0 multiply is neutral by color
        assert grid._get_value_color(1.0, 'multiply') == grid.COLOR_NEUTRAL
        # Filter excludes net_value == 1.0 (multiply default)
        summary = {
            'mass_mult': {'net_value': 1.0, 'operation': 'multiply'},
            'hp_mult': {'net_value': 1.0005, 'operation': 'multiply'},
        }
        affected = grid._get_affected_stats(summary)
        assert 'mass_mult' not in affected
        # Tolerance is 0.001 — 1.0005 is within tolerance, also excluded
        assert 'hp_mult' not in affected

    def test_handle_event_scroll_only_when_mouse_inside_panel_rect(self):
        """A `MOUSEWHEEL` event is consumed only when the mouse is
        inside the grid's panel abs_rect AND the scroll-state actually
        scrolled. Outside the rect → not consumed (no scroll-state
        mutation either)."""
        grid = self._grid()
        # Seed many scrollable rows so the viewport overflows and the
        # scroll-state has somewhere to go.
        grid.modifier_rows = [
            {'id': f'r{i}', 'name': f'r{i}', 'stats': {}} for i in range(40)
        ]

        # Stub the panel's absolute rect so we can position the mouse.
        panel_rect = pygame.Rect(100, 100, 200, 150)
        grid.panel = MagicMock()
        grid.panel.get_abs_rect.return_value = panel_rect

        wheel_event = MagicMock(type=pygame.MOUSEWHEEL, y=-1)

        # Outside rect → not consumed AND scroll-state offset stays at 0.
        with patch('pygame.mouse.get_pos', return_value=(0, 0)):
            consumed = grid.handle_event(wheel_event)
        assert consumed is False
        assert grid.scroll.offset == 0

        # Inside rect → scroll-state offset advances (content overflows
        # viewport) and the event is consumed.
        with patch('pygame.mouse.get_pos', return_value=(150, 150)):
            consumed = grid.handle_event(wheel_event)
        assert consumed is True
        assert grid.scroll.offset > 0

    # -- Missing-coverage gap-fillers (review-4 follow-up) --------------

    def test_set_position_updates_panel_origin(self):
        """`set_position(pos)` mutates `self.rect.topleft` AND calls
        `panel.set_position(pos)` so subsequent draw() calls render at
        the new origin. Pin both side effects of the public mutator
        at modifier_impact_grid.py:511-514."""
        grid = self._grid()
        grid.panel = MagicMock()  # capture set_position call

        grid.set_position((250, 175))

        assert grid.rect.topleft == (250, 175)
        grid.panel.set_position.assert_called_once_with((250, 175))

    def test_handle_event_returns_false_for_non_mousewheel_event(self):
        """`handle_event` only consumes MOUSEWHEEL; everything else
        returns False without touching scroll state. Pin the event-type
        guard at modifier_impact_grid.py:485 so a refactor that drops
        the `if event.type == pygame.MOUSEWHEEL:` check fails the test."""
        grid = self._grid()
        # Seed offset so we can prove non-mousewheel path leaves it alone.
        grid.scroll.offset = 7

        non_wheel = MagicMock(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10))
        consumed = grid.handle_event(non_wheel)

        assert consumed is False
        assert grid.scroll.offset == 7  # unchanged

    def test_format_value_returns_unknown_op_fallback_for_unrecognized_operation(self):
        """`_format_value` returns `str(value)` for any operation outside
        {'multiply', 'add', 'set'} — the fallthrough at
        modifier_impact_grid.py:271. Pins behavior so a future
        operation rename doesn't silently break display."""
        grid = self._grid()
        # Unknown op falls through the if/elif chain to `return str(value)`.
        assert grid._format_value(42, 'unknown_op') == '42'
        assert grid._format_value(3.5, 'fancy_new_op') == '3.5'
