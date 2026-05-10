"""
Unit tests for StrategyDetailFormatter class.

Tests initialization, show_detail dispatch, planet report panel management,
and production computation.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import pygame


class TestStrategyDetailFormatterInit:
    """Tests for StrategyDetailFormatter initialization."""

    def test_init_stores_references(self):
        """Test initialization stores all references correctly."""
        from game.ui.screens.strategy_detail_formatter import StrategyDetailFormatter

        scene = Mock()
        manager = Mock()
        detail_panel = Mock()
        widgets = MagicMock()
        graph_rect = pygame.Rect(10, 170, 150, 100)
        screen_size = (1920, 1080)

        formatter = StrategyDetailFormatter(
            scene, manager, detail_panel, widgets, graph_rect, screen_size
        )

        assert formatter.scene is scene
        assert formatter.manager is manager
        assert formatter.detail_panel is detail_panel
        assert formatter._widgets is widgets
        assert formatter.graph_rect == graph_rect
        assert formatter._screen_width == 1920
        assert formatter._screen_height == 1080

    def test_init_sets_default_state(self):
        """Test initialization sets default state values."""
        from game.ui.screens.strategy_detail_formatter import StrategyDetailFormatter

        formatter = StrategyDetailFormatter(
            Mock(), Mock(), Mock(), MagicMock(),
            pygame.Rect(0, 0, 100, 100), (800, 600)
        )

        assert formatter.current_selection is None
        assert formatter.current_raw_data == ""
        assert formatter.planet_report_panel is None


class TestShowDetailedReport:
    """Tests for show_detailed_report() dispatch."""

    @pytest.fixture
    def formatter(self):
        """Create formatter with full mock setup."""
        from game.ui.screens.strategy_detail_formatter import StrategyDetailFormatter

        scene = Mock()
        scene.current_empire = Mock()
        scene.current_empire.id = 1

        widgets = MagicMock()
        widgets.spectrum_graph.render = Mock(return_value=pygame.Surface((100, 100)))

        return StrategyDetailFormatter(
            scene, Mock(), Mock(), widgets,
            pygame.Rect(0, 0, 100, 100), (800, 600)
        )

    def test_show_detail_with_none_clears_panel(self, formatter):
        """Test show_detail with None clears detail panel."""
        formatter.show_detailed_report(None)

        assert formatter.detail_text.set_text.called or formatter.detail_text.rebuild.called

    def test_show_detail_hides_buttons_initially(self, formatter):
        """Test show_detail hides all context buttons."""
        formatter.show_detailed_report(None)

        formatter.btn_raw_data.hide.assert_called()
        formatter.btn_colonize.hide.assert_called()
        formatter.btn_build_yard.hide.assert_called()
        formatter.btn_orders.hide.assert_called()
        formatter.btn_fleet_report.hide.assert_called()
        formatter.btn_build_fleet.hide.assert_called()

    def test_show_detail_with_star_system(self, formatter):
        """Test show_detail with star system updates display."""
        system = Mock()
        system.name = "Sol System"
        system.primary_star = Mock()
        system.primary_star.name = "Sol"
        system.primary_star.star_type = Mock()
        system.primary_star.star_type.name = "G2V"
        system.primary_star.mass = 1.0
        system.primary_star.temperature = 5778
        system.stars = [system.primary_star]

        # Mock spectrum for format_spectrum_html
        system.primary_star.spectrum = Mock()
        system.primary_star.spectrum.gamma_ray = 1e-10
        system.primary_star.spectrum.xray = 1e-8
        system.primary_star.spectrum.ultraviolet = 1e-5
        system.primary_star.spectrum.blue = 1e-3
        system.primary_star.spectrum.green = 1e-3
        system.primary_star.spectrum.red = 1e-3
        system.primary_star.spectrum.infrared = 1e-4
        system.primary_star.spectrum.microwave = 1e-6
        system.primary_star.spectrum.radio = 1e-9

        with patch('game.ui.screens.strategy_detail_formatter.is_star_system', return_value=True):
            with patch('game.ui.screens.strategy_detail_formatter.is_star', return_value=False):
                with patch('game.ui.screens.strategy_detail_formatter.is_planet', return_value=False):
                    with patch('game.ui.screens.strategy_detail_formatter.is_fleet', return_value=False):
                        with patch('game.ui.screens.strategy_detail_formatter.is_warp_point', return_value=False):
                            with patch('game.ui.screens.strategy_detail_formatter.is_sector_environment', return_value=False):
                                formatter.show_detailed_report(system)

        assert formatter.current_selection is system
        formatter.graph_image.show.assert_called()
        formatter.btn_raw_data.show.assert_called()

    def test_show_detail_with_fleet_shows_fleet_buttons(self, formatter):
        """Test show_detail with owned fleet shows fleet buttons."""
        fleet = Mock()
        fleet.id = "F-001"
        fleet.owner_id = 1  # Same as current empire
        fleet.location = (10, 20)
        fleet.speed = 5
        fleet.fuel_endurance = Mock(return_value=25)
        fleet.orders = []
        fleet.ships = []
        fleet.has_space_shipyard = False

        with patch('game.ui.screens.strategy_detail_formatter.is_star_system', return_value=False):
            with patch('game.ui.screens.strategy_detail_formatter.is_star', return_value=False):
                with patch('game.ui.screens.strategy_detail_formatter.is_planet', return_value=False):
                    with patch('game.ui.screens.strategy_detail_formatter.is_fleet', return_value=True):
                        with patch('game.ui.screens.strategy_detail_formatter.is_warp_point', return_value=False):
                            with patch('game.ui.screens.strategy_detail_formatter.is_sector_environment', return_value=False):
                                formatter.show_detailed_report(fleet)

        formatter.btn_orders.show.assert_called()
        formatter.btn_fleet_report.show.assert_called()

    def test_show_detail_with_fleet_having_shipyard(self, formatter):
        """Test show_detail with fleet having space shipyard shows Build button."""
        fleet = Mock()
        fleet.id = "F-001"
        fleet.owner_id = 1
        fleet.location = (10, 20)
        fleet.speed = 5
        fleet.fuel_endurance = Mock(return_value=25)
        fleet.orders = []
        fleet.ships = []
        fleet.has_space_shipyard = True

        with patch('game.ui.screens.strategy_detail_formatter.is_star_system', return_value=False):
            with patch('game.ui.screens.strategy_detail_formatter.is_star', return_value=False):
                with patch('game.ui.screens.strategy_detail_formatter.is_planet', return_value=False):
                    with patch('game.ui.screens.strategy_detail_formatter.is_fleet', return_value=True):
                        with patch('game.ui.screens.strategy_detail_formatter.is_warp_point', return_value=False):
                            with patch('game.ui.screens.strategy_detail_formatter.is_sector_environment', return_value=False):
                                formatter.show_detailed_report(fleet)

        formatter.btn_build_fleet.show.assert_called()

    def test_show_detail_stores_current_selection(self, formatter):
        """Test show_detail stores current selection."""
        obj = Mock()

        with patch('game.ui.screens.strategy_detail_formatter.is_star_system', return_value=False):
            with patch('game.ui.screens.strategy_detail_formatter.is_star', return_value=False):
                with patch('game.ui.screens.strategy_detail_formatter.is_planet', return_value=False):
                    with patch('game.ui.screens.strategy_detail_formatter.is_fleet', return_value=False):
                        with patch('game.ui.screens.strategy_detail_formatter.is_warp_point', return_value=False):
                            with patch('game.ui.screens.strategy_detail_formatter.is_sector_environment', return_value=False):
                                with patch('game.ui.screens.strategy_detail_formatter.is_storm', return_value=False):
                                    formatter.show_detailed_report(obj)

        assert formatter.current_selection is obj


class TestComputePlanetProduction:
    """Tests for compute_planet_production()."""

    @pytest.fixture
    def formatter(self):
        """Create formatter for production tests."""
        from game.ui.screens.strategy_detail_formatter import StrategyDetailFormatter

        return StrategyDetailFormatter(
            Mock(), Mock(), Mock(), MagicMock(),
            pygame.Rect(0, 0, 100, 100), (800, 600)
        )

    def test_unowned_planet_returns_empty(self, formatter):
        """Test unowned planet returns empty dict."""
        planet = Mock()
        planet.owner_id = None

        result = formatter.compute_planet_production(planet)

        assert result == {}

    def test_planet_with_no_facilities_returns_empty(self, formatter):
        """Test planet with no facilities returns empty dict."""
        planet = Mock()
        planet.owner_id = 1
        planet.facilities = []

        result = formatter.compute_planet_production(planet)

        assert result == {}

    def test_planet_with_harvester_computes_rate(self, formatter):
        """Test planet with harvester facility computes rate."""
        planet = Mock()
        planet.owner_id = 1
        planet.deposits = {'metal': {'quality': 0.8}}

        facility = Mock()
        facility.is_operational = True
        facility.design_data = {
            'layers': {
                'core': [
                    {
                        'id': 'harvester_01',
                        'abilities': {
                            'ResourceHarvester': {
                                'resource_type': 'metal',
                                'base_harvest_rate': 10.0
                            }
                        }
                    }
                ]
            }
        }
        planet.facilities = [facility]

        # PROJ-174: Mock registry provider (DI pattern)
        mock_provider = Mock()
        mock_provider.get_components.return_value = {}
        mock_provider.get_modifiers.return_value = {}
        mock_provider.get_vehicle_classes.return_value = {}
        mock_provider.get_resources.return_value = {}

        with patch('game.core.registry.get_default_registry_provider', return_value=mock_provider):
            result = formatter.compute_planet_production(planet)

        assert 'metal' in result
        assert result['metal'] == 8.0  # 10.0 * 0.8 quality

    def test_non_operational_facility_skipped(self, formatter):
        """Test non-operational facility is skipped."""
        planet = Mock()
        planet.owner_id = 1
        planet.deposits = {'metal': {'quality': 0.8}}

        facility = Mock()
        facility.is_operational = False
        facility.design_data = {
            'layers': {
                'core': [
                    {
                        'id': 'harvester_01',
                        'abilities': {
                            'ResourceHarvester': {
                                'resource_type': 'metal',
                                'base_harvest_rate': 10.0
                            }
                        }
                    }
                ]
            }
        }
        planet.facilities = [facility]

        # PROJ-174: Mock registry provider (DI pattern)
        mock_provider = Mock()
        mock_provider.get_components.return_value = {}
        mock_provider.get_modifiers.return_value = {}
        mock_provider.get_vehicle_classes.return_value = {}
        mock_provider.get_resources.return_value = {}

        with patch('game.core.registry.get_default_registry_provider', return_value=mock_provider):
            result = formatter.compute_planet_production(planet)

        assert result == {}


class TestShowRawDataPopup:
    """Tests for show_raw_data_popup()."""

    @pytest.fixture
    def formatter(self):
        """Create formatter for popup tests."""
        from game.ui.screens.strategy_detail_formatter import StrategyDetailFormatter

        return StrategyDetailFormatter(
            Mock(), Mock(), Mock(), MagicMock(),
            pygame.Rect(0, 0, 100, 100),
            (800, 600)
        )

    @patch('game.ui.screens.strategy_detail_formatter.pygame_gui.windows.UIMessageWindow')
    def test_shows_popup_when_data_available(self, mock_window, formatter):
        """Test popup shown when raw data available."""
        formatter.current_raw_data = "<b>Test Data</b>"

        formatter.show_raw_data_popup()

        mock_window.assert_called_once()
        call_kwargs = mock_window.call_args[1]
        assert call_kwargs['html_message'] == "<b>Test Data</b>"
        assert call_kwargs['window_title'] == "Raw Data Analysis"

    @patch('game.ui.screens.strategy_detail_formatter.pygame_gui.windows.UIMessageWindow')
    def test_no_popup_when_no_data(self, mock_window, formatter):
        """Test no popup when no raw data."""
        formatter.current_raw_data = ""

        formatter.show_raw_data_popup()

        mock_window.assert_not_called()


class TestGetHarvesterInfo:
    """Tests for _get_harvester_info shared utility (moved to planet_report_panel)."""

    def test_inline_abilities(self):
        """Test extracts harvester from inline abilities."""
        from game.strategy.services.planet_economy_projector import _get_harvester_info

        comp = {
            'id': 'harvester_01',
            'abilities': {
                'ResourceHarvester': {
                    'resource_type': 'metal',
                    'base_harvest_rate': 10.0
                }
            }
        }

        result = _get_harvester_info(comp, None)

        assert result is not None
        assert result['resource_type'] == 'metal'
        assert result['base_harvest_rate'] == 10.0

    def test_no_harvester_ability(self):
        """Test returns None when no harvester ability."""
        from game.strategy.services.planet_economy_projector import _get_harvester_info

        comp = {
            'id': 'weapon_01',
            'abilities': {
                'Weapon': {'damage': 50}
            }
        }

        result = _get_harvester_info(comp, None)

        assert result is None

    def test_registry_fallback(self):
        """Test falls back to registry lookup."""
        from game.strategy.services.planet_economy_projector import _get_harvester_info

        comp = {'id': 'harvester_01'}

        comp_def = Mock()
        comp_def.abilities = {
            'ResourceHarvester': {
                'resource_type': 'energy',
                'base_harvest_rate': 5.0
            }
        }

        registries = Mock()
        registries.components.get = Mock(return_value=comp_def)

        result = _get_harvester_info(comp, registries)

        assert result is not None
        assert result['resource_type'] == 'energy'

    def test_non_dict_returns_none(self):
        """Test returns None for non-dict input."""
        from game.strategy.services.planet_economy_projector import _get_harvester_info

        result = _get_harvester_info("not a dict", None)

        assert result is None
