"""
Unit tests for PlanetListWindow and related components.

Tests window initialization, planet list population, column sorting,
filter application, and preset system.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import pygame


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_galaxy():
    """Create mock galaxy with planets."""
    galaxy = Mock()

    # Create planets
    planet1 = Mock()
    planet1.name = "Terra Prime"
    planet1.planet_type = Mock()
    planet1.planet_type.name = "Continental"
    planet1.mass = 5.97e24
    planet1.surface_gravity = 9.81
    planet1.surface_temperature = 288
    planet1.surface_water = 0.71
    planet1.total_pressure_atm = 1.0
    planet1.owner_id = 1
    planet1.resources = {}

    planet2 = Mock()
    planet2.name = "Frost World"
    planet2.planet_type = Mock()
    planet2.planet_type.name = "Cryoplanet"
    planet2.mass = 2.5e24
    planet2.surface_gravity = 5.0
    planet2.surface_temperature = 150
    planet2.surface_water = 0.95
    planet2.total_pressure_atm = 0.5
    planet2.owner_id = None
    planet2.resources = {}

    planet3 = Mock()
    planet3.name = "Desert Prime"
    planet3.planet_type = Mock()
    planet3.planet_type.name = "Arid"
    planet3.mass = 4.0e24
    planet3.surface_gravity = 7.0
    planet3.surface_temperature = 350
    planet3.surface_water = 0.05
    planet3.total_pressure_atm = 0.8
    planet3.owner_id = 2
    planet3.resources = {}

    system = Mock()
    system.name = "Sol"
    system.planets = [planet1, planet2, planet3]

    galaxy.systems = {"Sol": system}
    # PROJ-477 Phase 4: gather_planets takes the scene.world seam; wire
    # iter_systems to yield the same systems this fixture builds.
    galaxy.iter_systems.side_effect = lambda: iter(galaxy.systems.values())
    galaxy.get_empire = Mock(return_value=Mock(name="Enemy Empire"))

    return galaxy


@pytest.fixture
def mock_empire():
    """Create mock empire."""
    empire = Mock()
    empire.id = 1
    empire.name = "Player Empire"
    return empire


# =============================================================================
# PresetManager Tests
# =============================================================================

class TestPresetManager:
    """Tests for PresetManager class."""

    def test_init_loads_from_disk(self):
        """Test initialization loads presets from disk."""
        from game.ui.screens.planet_list_presets import PresetManager

        with patch('game.ui.screens.planet_list_presets.load_json') as mock_load:
            mock_load.return_value = {"TestPreset": {"filters": {}}}

            manager = PresetManager()

            mock_load.assert_called_once()
            assert manager.presets == {"TestPreset": {"filters": {}}}

    def test_get_preset_names_includes_default(self):
        """Test get_preset_names includes Default."""
        from game.ui.screens.planet_list_presets import PresetManager

        with patch('game.ui.screens.planet_list_presets.load_json') as mock_load:
            mock_load.return_value = {"Custom1": {}, "Custom2": {}}

            manager = PresetManager()
            names = manager.get_preset_names()

            assert "Default" in names
            assert "Custom1" in names
            assert "Custom2" in names

    def test_save_preset(self):
        """Test save_preset saves and persists."""
        from game.ui.screens.planet_list_presets import PresetManager

        with patch('game.ui.screens.planet_list_presets.load_json') as mock_load:
            with patch('game.ui.screens.planet_list_presets.save_json') as mock_save:
                mock_load.return_value = {}

                manager = PresetManager()
                manager.save_preset("NewPreset", {"filters": {"name": "test"}})

                assert "NewPreset" in manager.presets
                mock_save.assert_called_once()

    def test_get_preset_returns_preset(self):
        """Test get_preset returns preset by name."""
        from game.ui.screens.planet_list_presets import PresetManager

        with patch('game.ui.screens.planet_list_presets.load_json') as mock_load:
            mock_load.return_value = {"MyPreset": {"data": "value"}}

            manager = PresetManager()
            result = manager.get_preset("MyPreset")

            assert result == {"data": "value"}

    def test_get_preset_returns_none_for_missing(self):
        """Test get_preset returns None for missing preset."""
        from game.ui.screens.planet_list_presets import PresetManager

        with patch('game.ui.screens.planet_list_presets.load_json') as mock_load:
            mock_load.return_value = {}

            manager = PresetManager()
            result = manager.get_preset("NonExistent")

            assert result is None

    def test_has_preset(self):
        """Test has_preset checks existence."""
        from game.ui.screens.planet_list_presets import PresetManager

        with patch('game.ui.screens.planet_list_presets.load_json') as mock_load:
            mock_load.return_value = {"Exists": {}}

            manager = PresetManager()

            assert manager.has_preset("Exists") is True
            assert manager.has_preset("NotExists") is False

    def test_delete_preset(self):
        """Test delete_preset removes preset."""
        from game.ui.screens.planet_list_presets import PresetManager

        with patch('game.ui.screens.planet_list_presets.load_json') as mock_load:
            with patch('game.ui.screens.planet_list_presets.save_json') as mock_save:
                mock_load.return_value = {"ToDelete": {}}

                manager = PresetManager()
                result = manager.delete_preset("ToDelete")

                assert result is True
                assert "ToDelete" not in manager.presets
                mock_save.assert_called()

    def test_delete_preset_nonexistent(self):
        """Test delete_preset returns False for missing preset."""
        from game.ui.screens.planet_list_presets import PresetManager

        with patch('game.ui.screens.planet_list_presets.load_json') as mock_load:
            mock_load.return_value = {}

            manager = PresetManager()
            result = manager.delete_preset("NonExistent")

            assert result is False


# =============================================================================
# capture_planet_list_state Tests
# =============================================================================

class TestCapturePlanetListState:
    """Tests for capture_planet_list_state function."""

    def test_captures_columns(self):
        """Test captures column visibility state."""
        from game.ui.screens.planet_list_presets import capture_planet_list_state

        columns = [
            {'id': 'name', 'visible': True, 'title': 'Name'},
            {'id': 'type', 'visible': False, 'title': 'Type'},
        ]
        txt_name_filter = Mock()
        txt_name_filter.get_text = Mock(return_value="")
        filter_types = {'Continental': True}
        filter_owner = {'Player': True}
        ui_filters = {
            'gravity': {'min': Mock(get_current_value=Mock(return_value=0)), 'max': Mock(get_current_value=Mock(return_value=10))},
            'temp': {'min': Mock(get_current_value=Mock(return_value=0)), 'max': Mock(get_current_value=Mock(return_value=500))},
            'mass': {'min': Mock(get_current_value=Mock(return_value=0)), 'max': Mock(get_current_value=Mock(return_value=100))},
        }

        result = capture_planet_list_state(columns, txt_name_filter, filter_types, filter_owner, ui_filters)

        assert 'columns' in result
        assert len(result['columns']) == 2
        assert result['columns'][0] == {'id': 'name', 'visible': True}
        assert result['columns'][1] == {'id': 'type', 'visible': False}

    def test_captures_filters(self):
        """Test captures filter state."""
        from game.ui.screens.planet_list_presets import capture_planet_list_state

        columns = []
        txt_name_filter = Mock()
        txt_name_filter.get_text = Mock(return_value="terra")
        filter_types = {'Continental': True, 'Arid': False}
        filter_owner = {'Player': True, 'Enemy': False}
        ui_filters = {
            'gravity': {'min': Mock(get_current_value=Mock(return_value=0.5)), 'max': Mock(get_current_value=Mock(return_value=2.0))},
            'temp': {'min': Mock(get_current_value=Mock(return_value=200)), 'max': Mock(get_current_value=Mock(return_value=400))},
            'mass': {'min': Mock(get_current_value=Mock(return_value=0.1)), 'max': Mock(get_current_value=Mock(return_value=5.0))},
        }

        result = capture_planet_list_state(columns, txt_name_filter, filter_types, filter_owner, ui_filters)

        assert result['filters']['name'] == "terra"
        assert result['filters']['types'] == {'Continental': True, 'Arid': False}
        assert result['filters']['owner'] == {'Player': True, 'Enemy': False}
        assert result['filters']['ranges']['gravity'] == [0.5, 2.0]


# =============================================================================
# apply_planet_list_state Tests
# =============================================================================

class TestApplyPlanetListState:
    """Tests for apply_planet_list_state function."""

    def test_applies_column_visibility(self):
        """Test applies column visibility from state."""
        from game.ui.screens.planet_list_presets import apply_planet_list_state

        state = {
            'columns': [
                {'id': 'name', 'visible': False},
                {'id': 'type', 'visible': True},
            ]
        }
        columns = [
            {'id': 'name', 'visible': True, 'title': 'Name'},
            {'id': 'type', 'visible': False, 'title': 'Type'},
        ]
        txt_name_filter = Mock()
        filter_types = {}
        ui_filters = {'columns': {}}

        result = apply_planet_list_state(state, columns, txt_name_filter, filter_types, ui_filters)

        assert result[0]['visible'] is False  # name changed to False
        assert result[1]['visible'] is True   # type changed to True

    def test_applies_name_filter(self):
        """Test applies name filter from state."""
        from game.ui.screens.planet_list_presets import apply_planet_list_state

        state = {
            'filters': {
                'name': 'terra'
            }
        }
        columns = []
        txt_name_filter = Mock()
        filter_types = {}
        ui_filters = {}

        apply_planet_list_state(state, columns, txt_name_filter, filter_types, ui_filters)

        txt_name_filter.set_text.assert_called_with('terra')

    def test_applies_type_filters(self):
        """Test applies type filters from state."""
        from game.ui.screens.planet_list_presets import apply_planet_list_state

        state = {
            'filters': {
                'types': {'Continental': False, 'Arid': True}
            }
        }
        columns = []
        txt_name_filter = Mock()
        filter_types = {'Continental': True, 'Arid': False}
        ui_filters = {'types': {}}

        apply_planet_list_state(state, columns, txt_name_filter, filter_types, ui_filters)

        assert filter_types == {'Continental': False, 'Arid': True}

    def test_applies_owner_filters(self):
        """Test applies owner filters from state (PROJ-220 bug fix)."""
        from game.ui.screens.planet_list_presets import apply_planet_list_state

        state = {
            'filters': {
                'owner': {'Player': True, 'Enemy': False, 'Unowned': True}
            }
        }
        columns = []
        txt_name_filter = Mock()
        filter_types = {}
        filter_owner = {'Player': True, 'Enemy': True, 'Unowned': True}
        ui_filters = {'owners': {}}

        apply_planet_list_state(
            state, columns, txt_name_filter, filter_types, ui_filters,
            filter_owner=filter_owner,
        )

        assert filter_owner == {'Player': True, 'Enemy': False, 'Unowned': True}

    def test_applies_owner_filters_updates_buttons(self):
        """Test applies owner filters updates UI buttons (PROJ-220 bug fix).

        PROJ-323 Task 5.24: kept mock-call assertions. The buttons are
        pygame_gui UI widgets with no public observable state for
        select/unselect/set_text — the only way to verify these side effects
        is via mock call inspection. This test pattern is acceptable here
        because the mocks ARE the integration boundary.
        """
        from game.ui.screens.planet_list_presets import apply_planet_list_state

        state = {
            'filters': {
                'owner': {'Player': False, 'Enemy': True, 'Unowned': False}
            }
        }
        columns = []
        txt_name_filter = Mock()
        filter_types = {}
        filter_owner = {'Player': True, 'Enemy': True, 'Unowned': True}
        btn_player = Mock()
        btn_enemy = Mock()
        btn_unowned = Mock()
        ui_filters = {
            'owners': {
                'Player': btn_player,
                'Enemy': btn_enemy,
                'Unowned': btn_unowned,
            }
        }

        apply_planet_list_state(
            state, columns, txt_name_filter, filter_types, ui_filters,
            filter_owner=filter_owner,
        )

        btn_player.unselect.assert_called_once()
        btn_player.set_text.assert_called_with("Player")
        btn_enemy.select.assert_called_once()
        btn_enemy.set_text.assert_called_with("[Enemy]")
        btn_unowned.unselect.assert_called_once()
        btn_unowned.set_text.assert_called_with("Unowned")

    def test_missing_owner_key_defaults_to_all_true(self):
        """Old presets without owner key should leave filter_owner unchanged."""
        from game.ui.screens.planet_list_presets import apply_planet_list_state

        state = {
            'filters': {
                'types': {'Continental': True}
                # Note: no 'owner' key
            }
        }
        columns = []
        txt_name_filter = Mock()
        filter_types = {'Continental': False}
        filter_owner = {'Player': True, 'Enemy': True, 'Unowned': True}
        ui_filters = {'types': {}}

        apply_planet_list_state(
            state, columns, txt_name_filter, filter_types, ui_filters,
            filter_owner=filter_owner,
        )

        # Owner filter should remain unchanged (all True)
        assert filter_owner == {'Player': True, 'Enemy': True, 'Unowned': True}


# =============================================================================
# filter_planets Tests (extending existing)
# =============================================================================

class TestFilterPlanets:
    """Tests for filter_planets function."""

    def test_filter_with_no_matching_planets(self):
        """Test filter returns empty list when no planets match."""
        from game.ui.screens.planet_list_filters import filter_planets

        planet = Mock()
        planet._cached_type_category = "Jovian"
        planet._cached_name_lower = "jupiter"
        planet._cached_gravity_g = 2.5
        planet.surface_temperature = 125
        planet._cached_mass_earth = 318.0
        planet.owner_id = None

        # Disable Jovian type
        filter_types = {'Continental': True, 'Jovian': False}

        result = filter_planets(
            [planet], "", filter_types, 0, 100, 0, 1000, 0, 1000,
            {'Player': True, 'Unowned': True}, Mock(id=1)
        )

        assert len(result) == 0

    def test_filter_with_all_matching(self):
        """Test filter returns all planets when all match."""
        from game.ui.screens.planet_list_filters import filter_planets

        planets = []
        for i in range(5):
            p = Mock()
            p._cached_type_category = "Continental"
            p._cached_name_lower = f"planet{i}"
            p._cached_gravity_g = 1.0
            p.surface_temperature = 288
            p._cached_mass_earth = 1.0
            p.owner_id = 1
            planets.append(p)

        filter_types = {'Continental': True}

        result = filter_planets(
            planets, "", filter_types, 0, 10, 0, 1000, 0, 100,
            {'Player': True}, Mock(id=1)
        )

        assert len(result) == 5

    def test_filter_by_name(self):
        """Test filter by name substring."""
        from game.ui.screens.planet_list_filters import filter_planets

        p1 = Mock()
        p1._cached_type_category = "Continental"
        p1._cached_name_lower = "terra prime"
        p1._cached_gravity_g = 1.0
        p1.surface_temperature = 288
        p1._cached_mass_earth = 1.0
        p1.owner_id = 1

        p2 = Mock()
        p2._cached_type_category = "Continental"
        p2._cached_name_lower = "mars colony"
        p2._cached_gravity_g = 0.4
        p2.surface_temperature = 220
        p2._cached_mass_earth = 0.1
        p2.owner_id = 1

        filter_types = {'Continental': True}

        result = filter_planets(
            [p1, p2], "terra", filter_types, 0, 10, 0, 1000, 0, 100,
            {'Player': True}, Mock(id=1)
        )

        assert len(result) == 1
        assert result[0] == p1

    def test_filter_reset_clears_filters(self):
        """Test filter with empty/full ranges shows all."""
        from game.ui.screens.planet_list_filters import filter_planets

        p1 = Mock()
        p1._cached_type_category = "Continental"
        p1._cached_name_lower = "planet1"
        p1._cached_gravity_g = 0.1
        p1.surface_temperature = 50
        p1._cached_mass_earth = 0.01
        p1.owner_id = 1

        p2 = Mock()
        p2._cached_type_category = "Continental"
        p2._cached_name_lower = "planet2"
        p2._cached_gravity_g = 10.0
        p2.surface_temperature = 1000
        p2._cached_mass_earth = 100.0
        p2.owner_id = 1

        filter_types = {'Continental': True}

        # Wide ranges that include all
        result = filter_planets(
            [p1, p2], "", filter_types, 0, 100, 0, 2000, 0, 500,
            {'Player': True}, Mock(id=1)
        )

        assert len(result) == 2


# =============================================================================
# sort_planets Tests
# =============================================================================

class TestSortPlanets:
    """Tests for sort_planets function."""

    def test_sort_by_name_ascending(self):
        """Test sort by name ascending."""
        from game.ui.screens.planet_list_filters import sort_planets

        p1 = Mock()
        p1.name = "Zeta"
        p1._cached_name_lower = "zeta"
        p2 = Mock()
        p2.name = "Alpha"
        p2._cached_name_lower = "alpha"
        p3 = Mock()
        p3.name = "Beta"
        p3._cached_name_lower = "beta"

        planets = [p1, p2, p3]
        columns = [{'id': 'name', 'attr': 'name', 'visible': True, 'width': 100, 'title': 'Name'}]

        # sort_planets(planets, sort_column_id, sort_descending, columns)
        result = sort_planets(planets, 'name', False, columns)  # False = ascending

        assert result[0]._cached_name_lower == "alpha"
        assert result[1]._cached_name_lower == "beta"
        assert result[2]._cached_name_lower == "zeta"

    def test_sort_by_name_descending(self):
        """Test sort by name descending."""
        from game.ui.screens.planet_list_filters import sort_planets

        p1 = Mock()
        p1.name = "Zeta"
        p1._cached_name_lower = "zeta"
        p2 = Mock()
        p2.name = "Alpha"
        p2._cached_name_lower = "alpha"

        planets = [p1, p2]
        columns = [{'id': 'name', 'attr': 'name', 'visible': True, 'width': 100, 'title': 'Name'}]

        result = sort_planets(planets, 'name', True, columns)  # True = descending

        assert result[0]._cached_name_lower == "zeta"
        assert result[1]._cached_name_lower == "alpha"

    def test_sort_by_numeric_attribute(self):
        """Test sort by numeric attribute."""
        from game.ui.screens.planet_list_filters import sort_planets

        p1 = Mock()
        p1.surface_temperature = 500
        p2 = Mock()
        p2.surface_temperature = 100
        p3 = Mock()
        p3.surface_temperature = 300

        planets = [p1, p2, p3]
        columns = [{'id': 'temp', 'attr': 'surface_temperature', 'visible': True, 'width': 100, 'title': 'Temp'}]

        result = sort_planets(planets, 'temp', False, columns)  # False = ascending

        assert result[0].surface_temperature == 100
        assert result[1].surface_temperature == 300
        assert result[2].surface_temperature == 500


# =============================================================================
# gather_planets Tests
# =============================================================================

class TestGatherPlanets:
    """Tests for gather_planets function."""

    def test_gathers_from_all_systems(self, mock_galaxy, mock_empire):
        """Test gathers planets from all systems."""
        from game.ui.screens.planet_list_filters import gather_planets

        result = gather_planets(mock_galaxy, mock_empire)

        assert len(result) == 3

    def test_caches_type_category(self, mock_galaxy, mock_empire):
        """Test caches _cached_type_category on planets."""
        from game.ui.screens.planet_list_filters import gather_planets

        result = gather_planets(mock_galaxy, mock_empire)

        for planet in result:
            assert hasattr(planet, '_cached_type_category')

    def test_caches_name_lower(self, mock_galaxy, mock_empire):
        """Test caches _cached_name_lower on planets."""
        from game.ui.screens.planet_list_filters import gather_planets

        result = gather_planets(mock_galaxy, mock_empire)

        for planet in result:
            assert hasattr(planet, '_cached_name_lower')
            assert planet._cached_name_lower == planet.name.lower()

    def test_caches_gravity_g(self, mock_galaxy, mock_empire):
        """Test caches _cached_gravity_g on planets."""
        from game.ui.screens.planet_list_filters import gather_planets

        result = gather_planets(mock_galaxy, mock_empire)

        for planet in result:
            assert hasattr(planet, '_cached_gravity_g')


# =============================================================================
# compute_planet_ranges Tests
# =============================================================================

class TestComputePlanetRanges:
    """Tests for compute_planet_ranges function."""

    def test_computes_gravity_range(self):
        """Test computes gravity range from planets."""
        from game.ui.screens.planet_list_filters import compute_planet_ranges

        p1 = Mock()
        p1.surface_gravity = 4.9  # ~0.5g
        p1.surface_temperature = 200
        p1.mass = 3.0e24  # ~0.5 Earth mass

        p2 = Mock()
        p2.surface_gravity = 19.6  # ~2.0g
        p2.surface_temperature = 400
        p2.mass = 3.0e25  # ~5.0 Earth mass

        result = compute_planet_ranges([p1, p2])

        # Check gravity range is computed (min <= max)
        assert result['gravity'][0] <= result['gravity'][1]

    def test_computes_temp_range(self):
        """Test computes temperature range from planets."""
        from game.ui.screens.planet_list_filters import compute_planet_ranges

        p1 = Mock()
        p1.surface_gravity = 9.81
        p1.surface_temperature = 100
        p1.mass = 5.97e24

        p2 = Mock()
        p2.surface_gravity = 9.81
        p2.surface_temperature = 500
        p2.mass = 5.97e24

        result = compute_planet_ranges([p1, p2])

        # Check temp range is computed (min <= max)
        assert result['temp'][0] <= result['temp'][1]
        # Min should be at most 100, max at least 500
        assert result['temp'][0] <= 100
        assert result['temp'][1] >= 500

    def test_empty_planets_returns_defaults(self):
        """Test empty planet list returns default ranges."""
        from game.ui.screens.planet_list_filters import compute_planet_ranges

        result = compute_planet_ranges([])

        assert 'gravity' in result
        assert 'temp' in result
        assert 'mass' in result


# =============================================================================
# PlanetListWindow Detail Panel Geometry Tests (BUG-80)
# =============================================================================

class TestDetailPanelGeometry:
    """Tests for _detail_panel_geometry and dynamic panel sizing."""

    def _make_window_stub(self, width=1600, height=900):
        """Create a minimal stub + event-router wrapping it. PROJ-457 Phase 2
        moved `_detail_panel_geometry` from PlanetListWindow to
        PlanetListEventRouter; the stub exposes the same callable shape by
        attaching the router-bound method."""
        from game.ui.screens.planet_list_event_router import PlanetListEventRouter
        stub = Mock()
        stub.rect = pygame.Rect(0, 0, width, height)
        stub.detail_panel_width = 580
        router = PlanetListEventRouter(stub)
        stub._detail_panel_geometry = router._detail_panel_geometry
        return stub

    def test_panel_x_is_right_aligned(self):
        """Panel X should be window_width - detail_panel_width - 10."""
        stub = self._make_window_stub(width=1600)
        x, y, h = stub._detail_panel_geometry()
        assert x == 1600 - 580 - 10

    def test_panel_y_is_below_title(self):
        """Panel Y should be 60 (below title bar)."""
        stub = self._make_window_stub()
        x, y, h = stub._detail_panel_geometry()
        assert y == 60

    def test_panel_height_fills_window(self):
        """Panel height should fill available space dynamically."""
        stub = self._make_window_stub(height=900)
        x, y, h = stub._detail_panel_geometry()
        # height = max(450, 900 - 60 - 80) = max(450, 760) = 760
        assert h == 760

    def test_panel_height_minimum_450(self):
        """Panel height should never be less than 450 (PlanetReportPanel minimum)."""
        stub = self._make_window_stub(height=400)  # Very small window
        x, y, h = stub._detail_panel_geometry()
        assert h >= 450

    def test_taller_window_gives_taller_panel(self):
        """A taller window should produce a taller detail panel."""
        small = self._make_window_stub(height=700)
        large = self._make_window_stub(height=1200)
        _, _, h_small = small._detail_panel_geometry()
        _, _, h_large = large._detail_panel_geometry()
        assert h_large > h_small

    def test_wider_window_shifts_panel_right(self):
        """A wider window should move the panel further right."""
        narrow = self._make_window_stub(width=1200)
        wide = self._make_window_stub(width=2000)
        x_narrow, _, _ = narrow._detail_panel_geometry()
        x_wide, _, _ = wide._detail_panel_geometry()
        assert x_wide > x_narrow


# =============================================================================
# PlanetListWindow Column Swap Tests (BUG-100)
# =============================================================================

class TestPlanetListColumnSwap:
    """PlanetListWindow should call column_manager.swap_column() when header returns swap event."""

    def _make_update_stub(self):
        """Create a minimal stub wired for testing the update() swap path."""
        from game.ui.screens.planet_list_window import PlanetListWindow
        stub = Mock(spec=PlanetListWindow)
        stub.virtual_table = Mock()
        stub.virtual_table.scroll_bar.check_has_moved_recently.return_value = False
        stub.column_manager = Mock()
        stub.ui_filters = {}
        stub.refresh_list = Mock()
        stub.dd_presets = Mock()
        stub.dd_presets.selected_option = "Default"
        stub.last_preset_selection = "Default"
        stub.preset_manager = Mock()
        return stub

    def _run_update_with_swap(self, stub, col_dict, direction):
        """Run the shared update template on the stub with a swap_column header result.

        PROJ-375 Task 3.2: `PlanetListWindow.update` now delegates the
        swap/sort/scroll/preset polling to `DataListWindowMixin._run_update_template`.
        Test the production path by invoking that method directly on the
        stub (the swap dispatch lives there now, not in `PlanetListWindow.update`).
        """
        from game.ui.screens.data_list_window_mixin import DataListWindowMixin
        stub.virtual_table.check_header_presses.return_value = {
            'swap_column': (col_dict, direction), 'sort_column': None
        }
        DataListWindowMixin._run_update_template(stub, [])

    def test_swap_column_calls_column_manager(self):
        """When header returns swap_column, column_manager.swap_column() must be called."""
        stub = self._make_update_stub()
        col_dict = {"id": "mass", "title": "Mass", "width": 100, "visible": True}
        self._run_update_with_swap(stub, col_dict, 1)
        stub.column_manager.swap_column.assert_called_once_with("mass", 1)

    def test_swap_column_rebuilds_headers_and_rows(self):
        """After swap, rebuild_headers() and rebuild_row_pool() must be called."""
        stub = self._make_update_stub()
        col_dict = {"id": "gravity", "title": "Gravity", "width": 80, "visible": True}
        self._run_update_with_swap(stub, col_dict, -1)
        stub.virtual_table.rebuild_headers.assert_called_once()
        stub.virtual_table.rebuild_row_pool.assert_called_once()

    def test_swap_column_refreshes_list(self):
        """After swap, refresh_list() must be called."""
        stub = self._make_update_stub()
        col_dict = {"id": "mass", "title": "Mass", "width": 100, "visible": True}
        self._run_update_with_swap(stub, col_dict, 1)
        stub.refresh_list.assert_called_once()


# =============================================================================
# FEAT-16: Effects sidebar section.
#
# `build_sidebar` accepts an `effect_keys` parameter. When non-empty, an
# Effects filter group is rendered (one chip per group-key, plus All/None
# buttons) and the toggle buttons are exposed via ui_filters['effects'].
# When empty, the entire Effects section is omitted (label not even
# rendered) and `ui_filters['effects']` is `{}`.
# =============================================================================


class TestSidebarEffectsSection:
    """Verify sidebar conditionally renders the Effects filter group based
    on `effect_keys`. Patches pygame_gui widget classes to keep the test
    Pygame-free."""

    def _patch_widgets(self):
        """Patch every pygame_gui widget the sidebar instantiates.
        Returns the mock-patcher context manager list (use enter/exit).

        PROJ-319 DUP-X-07: range slider widgets moved to
        `game.ui.widgets.range_slider_builder`; patch BOTH the sidebar module
        (for non-range widgets it still uses) and the builder module.
        """
        return [
            patch('game.ui.screens.planet_list_sidebar.UIScrollingContainer'),
            patch('game.ui.screens.planet_list_sidebar.UILabel'),
            patch('game.ui.screens.planet_list_sidebar.UIButton'),
            patch('game.ui.screens.planet_list_sidebar.UITextEntryLine'),
            patch('game.ui.screens.planet_list_sidebar.UIDropDownMenu'),
            # FEAT-25: Effects section now uses TriStateFilterWidget
            patch('game.ui.screens.planet_list_sidebar.TriStateFilterWidget'),
            # PROJ-319 DUP-X-07: range-slider widgets moved to shared builder.
            patch('game.ui.widgets.range_slider_builder.UILabel'),
            patch('game.ui.widgets.range_slider_builder.UIHorizontalSlider'),
            patch('game.ui.widgets.range_slider_builder.UITextEntryLine'),
        ]

    def _call_build_sidebar(self, effect_keys):
        """Invoke build_sidebar with mocked widgets and the given effect_keys."""
        from game.ui.screens.planet_list_sidebar import build_sidebar
        from game.ui.screens.planet_list_presets import PresetManager

        manager = MagicMock()
        sidebar_panel = MagicMock()
        planet_ranges = {
            'gravity': (0.0, 10.0),
            'temp': (0, 2000),
            'mass': (0.0, 500.0),
        }
        columns = [{'id': 'name', 'title': 'Name', 'visible': True}]

        with patch.object(PresetManager, '_load_from_disk', return_value={}):
            preset_manager = PresetManager()

        patches = self._patch_widgets()
        for p in patches:
            p.start()
        try:
            return build_sidebar(
                manager=manager,
                sidebar_panel=sidebar_panel,
                sidebar_width=300,
                rect_height=800,
                planet_ranges=planet_ranges,
                columns=columns,
                preset_manager=preset_manager,
                effect_keys=effect_keys,
            )
        finally:
            for p in patches:
                p.stop()

    def test_no_effects_section_when_empty_galaxy(self):
        """effect_keys=[] → ui_filters['effects'] is empty (or absent)."""
        widgets = self._call_build_sidebar(effect_keys=[])
        ui_filters = widgets['ui_filters']
        # Either key missing or empty dict — both signal no chips rendered
        effects = ui_filters.get('effects', {})
        assert effects == {}

    def test_effects_section_chips_match_keys(self):
        """Each group-key gets one toggle button entry in ui_filters['effects']."""
        widgets = self._call_build_sidebar(
            effect_keys=['ThrustModifier', 'EnvironmentalDamage:thermal', 'FuelDrain']
        )
        ui_filters = widgets['ui_filters']
        assert set(ui_filters['effects'].keys()) == {
            'ThrustModifier',
            'EnvironmentalDamage:thermal',
            'FuelDrain',
        }
        # All/None buttons exposed for the effects category
        assert 'btn_all_effects' in widgets
        assert 'btn_none_effects' in widgets
