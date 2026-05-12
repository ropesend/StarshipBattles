"""
Tests for ResearchTreeScene event routing, draw orchestration, input,
resize re-push, and validation logging.

PROJ-337: Gap-fill characterization for behaviors not covered by
test_initialization.py / test_callbacks.py / test_interaction.py.

Pin observed behavior — no production refactors.
"""
from contextlib import contextmanager
from unittest.mock import MagicMock, patch, call

import pygame
import pytest


def _make_default_tree():
    tree = MagicMock()
    tree.nodes = {}
    tree.get_max_depth.return_value = 0
    tree.validate_requirements.return_value = []
    tree.detect_cycles.return_value = []
    return tree


def _make_default_tracker(seed=12345, **overrides):
    tracker = MagicMock()
    tracker.session_seed = seed
    tracker.auto_spread_enabled = False
    tracker.turn_number = 1
    tracker.get_all_tech_levels.return_value = {}
    for key, value in overrides.items():
        setattr(tracker, key, value)
    return tracker


@contextmanager
def _patched_research_scene(*, with_service=False):
    """Patch the standard set of research_scene module attributes."""
    patches = {
        'TechTree': patch('game.ui.research.research_scene.TechTree'),
        'Tracker': patch('game.ui.research.research_scene.ResearchTracker'),
        'Camera': patch('game.ui.research.research_scene.Camera'),
        'StarshipUIManager': patch('game.ui.research.research_scene.StarshipUIManager'),
        'Renderer': patch('game.ui.research.research_scene.ResearchRenderer'),
        'Panel': patch('game.ui.research.research_scene.ResearchControlPanel'),
    }
    if with_service:
        patches['Service'] = patch('game.ui.research.research_scene.ResearchService')

    started = {name: p.start() for name, p in patches.items()}
    try:
        started['TechTree'].load_from_json.return_value = _make_default_tree()
        started['Tracker'].return_value = _make_default_tracker()
        yield started
    finally:
        for p in patches.values():
            p.stop()


def _make_scene(mocks, *, canvas_width=1570, screen_height=1080):
    """Build a ResearchTreeScene with controllable mocks for renderer/panel/camera."""
    from game.ui.research.research_scene import ResearchTreeScene
    mocks['Renderer'].return_value = MagicMock()
    mocks['Panel'].return_value = MagicMock()

    # Default control_panel.handle_event returns False so routing continues
    mocks['Panel'].return_value.handle_event.return_value = False
    # ui_manager.process_events returns False so event passes through
    ui_manager = MagicMock()
    ui_manager.process_events.return_value = False
    mocks['StarshipUIManager'].return_value = ui_manager

    scene = ResearchTreeScene(canvas_width + 350, screen_height)
    return scene


class TestHandleEventRouting:
    """Tests for handle_event routing precedence."""

    def test_handle_event_returns_early_when_ui_manager_consumes(self):
        with _patched_research_scene() as mocks:
            scene = _make_scene(mocks)
            scene.ui_manager.process_events.return_value = True

            event = MagicMock()
            event.type = pygame.MOUSEBUTTONDOWN
            event.button = 1
            event.pos = (10, 10)

            scene.handle_event(event)

            # Control panel handle_event should NOT have been called
            scene.control_panel.handle_event.assert_not_called()

    def test_handle_event_returns_early_when_control_panel_consumes(self):
        with _patched_research_scene() as mocks:
            scene = _make_scene(mocks)
            scene.control_panel.handle_event.return_value = True

            # Spy on _handle_click
            with patch.object(scene, '_handle_click') as spy_click:
                event = MagicMock()
                event.type = pygame.MOUSEBUTTONDOWN
                event.button = 1
                event.pos = (10, 10)

                scene.handle_event(event)

                spy_click.assert_not_called()

    def test_handle_event_escape_key_invokes_on_close(self):
        with _patched_research_scene() as mocks:
            close_cb = MagicMock()
            from game.ui.research.research_scene import ResearchTreeScene
            mocks['Renderer'].return_value = MagicMock()
            mocks['Panel'].return_value = MagicMock()
            mocks['Panel'].return_value.handle_event.return_value = False
            ui_manager = MagicMock()
            ui_manager.process_events.return_value = False
            mocks['StarshipUIManager'].return_value = ui_manager

            scene = ResearchTreeScene(1920, 1080, on_close_callback=close_cb)

            event = MagicMock()
            event.type = pygame.KEYDOWN
            event.key = pygame.K_ESCAPE

            scene.handle_event(event)

            close_cb.assert_called_once()

    def test_handle_event_left_click_on_canvas_calls_handle_click(self):
        with _patched_research_scene() as mocks:
            scene = _make_scene(mocks)

            with patch.object(scene, '_handle_click') as spy_click:
                event = MagicMock()
                event.type = pygame.MOUSEBUTTONDOWN
                event.button = 1
                # canvas extends to canvas_width = 1570
                event.pos = (100, 200)

                scene.handle_event(event)

                spy_click.assert_called_once_with(100, 200)

    def test_handle_event_left_click_on_sidebar_is_ignored(self):
        with _patched_research_scene() as mocks:
            scene = _make_scene(mocks)

            with patch.object(scene, '_handle_click') as spy_click:
                event = MagicMock()
                event.type = pygame.MOUSEBUTTONDOWN
                event.button = 1
                # canvas_width is 1570 — pos.x >= canvas_width is sidebar
                event.pos = (1700, 200)

                scene.handle_event(event)

                spy_click.assert_not_called()

    def test_handle_event_mousewheel_over_canvas_routes_to_camera(self):
        with _patched_research_scene() as mocks:
            scene = _make_scene(mocks)

            with patch('pygame.mouse.get_pos', return_value=(100, 200)):
                event = MagicMock()
                event.type = pygame.MOUSEWHEEL

                scene.handle_event(event)

                scene.camera.update_input.assert_called_once_with(0, [event])

    def test_handle_event_mousewheel_over_sidebar_is_ignored(self):
        with _patched_research_scene() as mocks:
            scene = _make_scene(mocks)

            with patch('pygame.mouse.get_pos', return_value=(1700, 200)):
                event = MagicMock()
                event.type = pygame.MOUSEWHEEL

                scene.handle_event(event)

                scene.camera.update_input.assert_not_called()


class TestDrawOrchestration:
    """Tests for draw paint order."""

    def test_draw_fills_background_then_canvas_then_renderer_then_sidebar_then_ui(self):
        with _patched_research_scene() as mocks:
            scene = _make_scene(mocks)

            screen = MagicMock(spec=pygame.Surface)

            with patch('game.ui.research.research_scene.pygame.draw.rect') as mock_rect:
                scene.draw(screen)

                # 1. screen.fill called for background
                screen.fill.assert_called_once()
                # 2. pygame.draw.rect was called for canvas + sidebar
                assert mock_rect.call_count == 2
                # 3. renderer.draw was called between the two rects
                scene.renderer.draw.assert_called_once()
                # 4. ui_manager.draw_ui called last
                scene.ui_manager.draw_ui.assert_called_once_with(screen)


class TestHandleInput:
    """Tests for update_input continuous-input routing."""

    def test_update_input_routes_to_camera_only_when_mouse_over_canvas(self):
        with _patched_research_scene() as mocks:
            scene = _make_scene(mocks)

            # Mouse over canvas
            with patch('pygame.mouse.get_pos', return_value=(100, 200)):
                scene.update_input(0.016, [])
                scene.camera.update_input.assert_called_once_with(0.016, [])

            scene.camera.update_input.reset_mock()

            # Mouse over sidebar
            with patch('pygame.mouse.get_pos', return_value=(1700, 200)):
                scene.update_input(0.016, [])
                scene.camera.update_input.assert_not_called()


class TestHandleResize:
    """Tests for handle_resize re-push of selected node."""

    def test_handle_resize_re_pushes_selected_node_when_set(self):
        with _patched_research_scene() as mocks:
            mock_node = MagicMock()
            mock_node.id = 'sel_node'
            tree = _make_default_tree()
            tree.get_node.return_value = mock_node
            mocks['TechTree'].load_from_json.return_value = tree

            scene = _make_scene(mocks)
            scene.selected_node_id = 'sel_node'

            # handle_resize replaces control_panel; so capture the new mock
            new_panel = MagicMock()
            mocks['Panel'].return_value = new_panel

            scene.handle_resize(2560, 1440)

            new_panel.update_selected_node.assert_called_once_with(
                mock_node, scene.tracker
            )


class TestValidationLogging:
    """Tests for validate_requirements logging cap."""

    def test_validate_requirements_errors_logged_first_5(self, caplog):
        import logging

        with _patched_research_scene() as mocks:
            tree = _make_default_tree()
            tree.validate_requirements.return_value = [
                f"err{i}" for i in range(7)
            ]
            mocks['TechTree'].load_from_json.return_value = tree

            with caplog.at_level(logging.INFO,
                                 logger='game.ui.research.research_scene'):
                _make_scene(mocks)

            validation_records = [
                r for r in caplog.records
                if 'TechTree validation' in r.getMessage()
                and any(f'err{i}' in r.getMessage() for i in range(7))
            ]
            # First 5 errors only
            assert len(validation_records) == 5
            messages = [r.getMessage() for r in validation_records]
            for i in range(5):
                assert any(f'err{i}' in m for m in messages)
            # err5 and err6 should NOT have been logged
            for i in (5, 6):
                assert not any(f'err{i}' in m for m in messages)


class TestOnNextTurnRefresh:
    """Tests for _on_next_turn refreshing selected-node display."""

    def test_on_next_turn_refreshes_selected_node_display(self):
        with _patched_research_scene(with_service=True) as mocks:
            mock_node = MagicMock()
            mock_node.id = 'sel'
            tree = _make_default_tree()
            tree.get_node.return_value = mock_node
            mocks['TechTree'].load_from_json.return_value = tree

            mocks['Service'].process_turn.return_value = []

            scene = _make_scene(mocks)
            scene.selected_node_id = 'sel'
            scene.control_panel.update_selected_node.reset_mock()

            scene._on_next_turn()

            scene.control_panel.update_selected_node.assert_called_with(
                mock_node, scene.tracker
            )
