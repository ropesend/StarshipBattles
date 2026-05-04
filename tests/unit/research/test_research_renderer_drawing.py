"""
Drawing-orchestration characterization tests for ResearchRenderer.

PROJ-337 gap-fill: pins observed draw call sequence, dependency-line
color/dashed branches, dashed-line geometry, node fill/border colors,
RP-allocation indicator, zoom-conditional text, truncation, font min-size,
viewport culling.

Uses the same importlib-isolated `renderer_module` autouse fixture pattern
as test_research_renderer.py (loads renderer module from file path so
research_scene.py's pygame_gui import is bypassed).

Pygame.draw.line / pygame.draw.rect are monkeypatched per-test to capture
calls without needing a live surface.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pygame
import pytest


@pytest.fixture(autouse=True)
def renderer_module():
    """Load renderer module by file path, bypassing package __init__.py."""
    if not pygame.font.get_init():
        pygame.font.init()

    renderer_path = (
        Path(__file__).resolve().parents[3]
        / "game" / "ui" / "research" / "research_renderer.py"
    )
    spec = importlib.util.spec_from_file_location(
        "research_renderer_isolated_drawing", str(renderer_path)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    yield module


# ---- Helpers ----------------------------------------------------------------

def _make_renderer(renderer_module, *, node_positions=None, tech_levels=None,
                   states=None, zoom=1.0, camera_w=800, camera_h=600,
                   nodes=None):
    ResearchRenderer = renderer_module.ResearchRenderer

    tree = MagicMock()
    tree.nodes = nodes or {}

    tracker = MagicMock()
    tracker.get_all_tech_levels.return_value = tech_levels or {}

    if states is not None:
        def _get_state(node_id):
            return states.get(node_id, MagicMock(current_level=0,
                                                 current_chance=0.5,
                                                 rp_allocation=0))
        tracker.get_state.side_effect = _get_state

    camera = MagicMock()
    camera.zoom = zoom
    camera.width = camera_w
    camera.height = camera_h
    # Default world_to_screen returns input as-is (pretend identity)
    camera.world_to_screen.side_effect = lambda pos: (float(pos[0]), float(pos[1]))

    return ResearchRenderer(
        tech_tree=tree, tracker=tracker,
        node_positions=node_positions or {},
        camera=camera, node_width=100, node_height=60
    )


def _make_node(node_id, *, requirements=None, max_levels=5, name=None):
    node = MagicMock()
    node.id = node_id
    node.name = name or node_id
    node.requirements = requirements or []
    node.max_levels = max_levels
    node.base_decay = 0.01
    node.volatility = 0.1
    return node


def _make_req(node_id, level, *, negate=False):
    req = MagicMock()
    req.node_id = node_id
    req.get_required_level.return_value = level
    req.negate = negate
    return req


# ---- Section A: draw orchestration -----------------------------------------

class TestDrawOrchestration:

    def test_draw_sets_clip_to_canvas_rect_then_clears(self, renderer_module):
        renderer = _make_renderer(renderer_module)
        screen = MagicMock(spec=pygame.Surface)
        canvas_rect = pygame.Rect(0, 0, 800, 600)

        renderer.draw(screen, None, canvas_rect)

        # Two set_clip calls: one with rect, one with None
        assert screen.set_clip.call_args_list == [call(canvas_rect), call(None)]

    def test_draw_calls_dependency_lines_before_nodes(self, renderer_module):
        renderer = _make_renderer(renderer_module)
        screen = MagicMock(spec=pygame.Surface)

        order = []
        with patch.object(
            renderer, '_draw_dependency_lines',
            side_effect=lambda *a, **k: order.append('lines')
        ), patch.object(
            renderer, '_draw_nodes',
            side_effect=lambda *a, **k: order.append('nodes')
        ):
            renderer.draw(screen, None, pygame.Rect(0, 0, 800, 600))

        assert order == ['lines', 'nodes']


# ---- Section B: dependency lines -------------------------------------------

class TestDependencyLines:

    def test_dependency_lines_skip_nodes_missing_from_positions(
            self, renderer_module, monkeypatch):
        # Node "a" has prereq "missing" not in positions
        node_a = _make_node('a', requirements=[[_make_req('missing', 1)]])
        nodes = {'a': node_a}
        positions = {'a': (100, 100)}  # only a, no "missing"

        renderer = _make_renderer(
            renderer_module, node_positions=positions, nodes=nodes
        )

        line_calls = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'line',
            lambda *args, **kw: line_calls.append((args, kw))
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_dependency_lines(screen, {})

        # No line should have been drawn (prereq missing from positions)
        assert line_calls == []

    def test_dependency_lines_skip_off_screen_nodes(
            self, renderer_module, monkeypatch):
        node_a = _make_node('a', requirements=[[_make_req('b', 1)]])
        node_b = _make_node('b')
        nodes = {'a': node_a, 'b': node_b}
        # node 'a' is far off-screen; 'b' on-screen
        positions = {'a': (10000, 10000), 'b': (200, 200)}

        renderer = _make_renderer(
            renderer_module, node_positions=positions, nodes=nodes
        )

        line_calls = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'line',
            lambda *args, **kw: line_calls.append((args, kw))
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_dependency_lines(screen, {})

        assert line_calls == []

    def test_dependency_line_color_uses_met_when_prereq_meets_required_level(
            self, renderer_module, monkeypatch):
        node_a = _make_node('a', requirements=[[_make_req('b', 1)]])
        node_b = _make_node('b')
        positions = {'a': (300, 300), 'b': (100, 100)}

        renderer = _make_renderer(
            renderer_module,
            node_positions=positions, nodes={'a': node_a, 'b': node_b}
        )

        line_colors = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'line',
            lambda surf, color, start, end, width: line_colors.append(color)
        )

        screen = MagicMock(spec=pygame.Surface)
        # tech_levels: prereq 'b' at level 1 — meets requirement
        renderer._draw_dependency_lines(screen, {'b': 1})

        assert renderer.COLOR_LINE_MET in line_colors

    def test_dependency_line_color_uses_unmet_when_prereq_below_required(
            self, renderer_module, monkeypatch):
        node_a = _make_node('a', requirements=[[_make_req('b', 2)]])
        node_b = _make_node('b')
        positions = {'a': (300, 300), 'b': (100, 100)}

        renderer = _make_renderer(
            renderer_module,
            node_positions=positions, nodes={'a': node_a, 'b': node_b}
        )

        line_colors = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'line',
            lambda surf, color, start, end, width: line_colors.append(color)
        )

        screen = MagicMock(spec=pygame.Surface)
        # 'b' at level 0, required 2 — unmet
        renderer._draw_dependency_lines(screen, {'b': 0})

        assert renderer.COLOR_LINE in line_colors

    def test_negated_requirement_is_met_when_prereq_below_required(
            self, renderer_module, monkeypatch):
        node_a = _make_node(
            'a', requirements=[[_make_req('b', 2, negate=True)]]
        )
        node_b = _make_node('b')
        positions = {'a': (300, 300), 'b': (100, 100)}

        renderer = _make_renderer(
            renderer_module,
            node_positions=positions, nodes={'a': node_a, 'b': node_b}
        )

        # Capture _draw_dashed_line calls (negate path uses dashed)
        dashed_calls = []
        original = renderer._draw_dashed_line

        def _spy(screen, color, start, end, width=2, dash_length=8):
            dashed_calls.append(color)

        monkeypatch.setattr(renderer, '_draw_dashed_line', _spy)

        screen = MagicMock(spec=pygame.Surface)
        # 'b' at level 0, required 2 with negate — IS met
        renderer._draw_dependency_lines(screen, {'b': 0})

        assert renderer.COLOR_LINE_NEGATED_MET in dashed_calls

    def test_negated_requirement_uses_dashed_drawer(
            self, renderer_module, monkeypatch):
        node_a = _make_node(
            'a', requirements=[[_make_req('b', 1, negate=True)]]
        )
        node_b = _make_node('b')
        positions = {'a': (300, 300), 'b': (100, 100)}

        renderer = _make_renderer(
            renderer_module,
            node_positions=positions, nodes={'a': node_a, 'b': node_b}
        )

        line_calls = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'line',
            lambda *args, **kw: line_calls.append(args)
        )

        dashed_calls = []
        monkeypatch.setattr(
            renderer, '_draw_dashed_line',
            lambda *args, **kw: dashed_calls.append(args)
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_dependency_lines(screen, {'b': 5})

        assert len(dashed_calls) == 1
        # Negated path goes through _draw_dashed_line, NOT pygame.draw.line
        assert line_calls == []


# ---- Section C: dashed line geometry ---------------------------------------

class TestDashedLineGeometry:

    def test_dashed_line_zero_length_is_noop(self, renderer_module, monkeypatch):
        renderer = _make_renderer(renderer_module)

        line_calls = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'line',
            lambda *args, **kw: line_calls.append(args)
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_dashed_line(screen, (255, 0, 0), (10, 10), (10, 10))

        assert line_calls == []

    def test_dashed_line_clamps_final_dash_to_endpoint(
            self, renderer_module, monkeypatch):
        renderer = _make_renderer(renderer_module)

        # length not divisible by dash_length*2
        # length=20, dash_length=8 -> 8*2=16, num_dashes=int(20/16)=1
        # So loops i=0,1 and i=1 dash should clamp
        line_calls = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'line',
            lambda surf, color, start, end, width:
                line_calls.append((start, end))
        )

        screen = MagicMock(spec=pygame.Surface)
        end_point = (20, 0)
        renderer._draw_dashed_line(
            screen, (255, 0, 0), (0, 0), end_point, width=2, dash_length=8
        )

        # The last dash's endpoint should equal end_point exactly
        # due to the min() clamp
        assert line_calls, "Expected at least one dash drawn"
        last_end = line_calls[-1][1]
        # End point is clamped — at minimum x should be <= 20
        assert last_end[0] <= end_point[0]


# ---- Section D: node drawing -----------------------------------------------

class TestNodeDrawing:

    def _setup_single_node(self, renderer_module, *, status='available',
                           rp_allocation=0, current_level=0,
                           selected=False, zoom=1.0, name='Node'):
        node = _make_node('n1', max_levels=5, name=name)
        node.get_status.return_value = status

        state = MagicMock()
        state.current_level = current_level
        state.current_chance = 0.5
        state.rp_allocation = rp_allocation

        states = {'n1': state}
        positions = {'n1': (400, 300)}

        renderer = _make_renderer(
            renderer_module, node_positions=positions,
            nodes={'n1': node}, states=states, zoom=zoom
        )
        return renderer, node, state

    def test_node_color_completed_uses_research_completed(
            self, renderer_module, monkeypatch):
        renderer, _, _ = self._setup_single_node(
            renderer_module, status='completed', current_level=3
        )

        rect_calls = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'rect',
            lambda surf, color, rect, *a, **kw:
                rect_calls.append((color, a, kw))
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_nodes(screen, None, {})

        # First rect is the fill
        assert rect_calls[0][0] == renderer.COLOR_COMPLETED

    def test_node_color_available_uses_research_available(
            self, renderer_module, monkeypatch):
        renderer, _, _ = self._setup_single_node(
            renderer_module, status='available'
        )

        rect_calls = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'rect',
            lambda surf, color, rect, *a, **kw:
                rect_calls.append((color, a, kw))
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_nodes(screen, None, {})

        assert rect_calls[0][0] == renderer.COLOR_AVAILABLE

    def test_node_color_locked_fallback(self, renderer_module, monkeypatch):
        renderer, _, _ = self._setup_single_node(
            renderer_module, status='locked'
        )

        rect_calls = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'rect',
            lambda surf, color, rect, *a, **kw:
                rect_calls.append((color, a, kw))
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_nodes(screen, None, {})

        assert rect_calls[0][0] == renderer.COLOR_LOCKED

    def test_selected_node_drawn_with_selected_color_width_3(
            self, renderer_module, monkeypatch):
        renderer, _, _ = self._setup_single_node(
            renderer_module, status='available'
        )

        rect_calls = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'rect',
            lambda surf, color, rect, *a, **kw:
                rect_calls.append((color, a, kw))
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_nodes(screen, 'n1', {})

        # Second rect is the selected border with width=3
        # rect_calls items: (color, args_after_rect, kwargs)
        # signature: pygame.draw.rect(screen, color, rect, width, border_radius=...)
        border_call = rect_calls[1]
        assert border_call[0] == renderer.COLOR_SELECTED
        # args after rect: (3,) for width
        assert border_call[1][0] == 3

    def test_unselected_node_uses_lightened_border_width_1(
            self, renderer_module, monkeypatch):
        renderer, _, _ = self._setup_single_node(
            renderer_module, status='available'
        )

        rect_calls = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'rect',
            lambda surf, color, rect, *a, **kw:
                rect_calls.append((color, a, kw))
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_nodes(screen, None, {})

        border_call = rect_calls[1]
        # width=1 for unselected border
        assert border_call[1][0] == 1

    def test_rp_allocation_bar_drawn_only_when_allocation_positive(
            self, renderer_module, monkeypatch):
        # case 1: allocation > 0 -> 3 rect calls (fill, border, allocation bar)
        renderer, _, _ = self._setup_single_node(
            renderer_module, status='available', rp_allocation=10
        )

        rect_calls = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'rect',
            lambda *args, **kw: rect_calls.append(args)
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_nodes(screen, None, {})
        positive_count = len(rect_calls)

        # case 2: allocation == 0 -> only 2 rect calls
        renderer2, _, _ = self._setup_single_node(
            renderer_module, status='available', rp_allocation=0
        )
        rect_calls2 = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'rect',
            lambda *args, **kw: rect_calls2.append(args)
        )

        renderer2._draw_nodes(screen, None, {})
        zero_count = len(rect_calls2)

        assert positive_count > zero_count
        assert positive_count - zero_count == 1

    def test_node_text_drawn_only_when_zoom_above_quarter(
            self, renderer_module, monkeypatch):
        # zoom == 0.25 → no text
        renderer_low, _, _ = self._setup_single_node(
            renderer_module, status='available', zoom=0.25
        )
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'rect', lambda *a, **kw: None
        )
        screen = MagicMock(spec=pygame.Surface)
        renderer_low._draw_nodes(screen, None, {})

        low_blits = screen.blit.call_count

        # zoom > 0.25 → text rendered
        renderer_hi, _, _ = self._setup_single_node(
            renderer_module, status='available', zoom=1.0
        )
        screen2 = MagicMock(spec=pygame.Surface)
        renderer_hi._draw_nodes(screen2, None, {})
        hi_blits = screen2.blit.call_count

        assert low_blits == 0
        assert hi_blits > 0

    def test_node_off_screen_with_margin_is_culled(
            self, renderer_module, monkeypatch):
        node = _make_node('n1')
        node.get_status.return_value = 'available'
        state = MagicMock(current_level=0, current_chance=0.5, rp_allocation=0)
        positions = {'n1': (50000, 50000)}

        renderer = _make_renderer(
            renderer_module, node_positions=positions,
            nodes={'n1': node}, states={'n1': state}
        )

        rect_calls = []
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'rect',
            lambda *args, **kw: rect_calls.append(args)
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_nodes(screen, None, {})

        assert rect_calls == []


# ---- Section E: node text --------------------------------------------------

class TestNodeText:

    def test_long_name_truncated_with_ellipsis(self, renderer_module, monkeypatch):
        # Build a node with a very long name and zoom that yields a small rect
        node = _make_node('n1', name='A' * 200)
        node.get_status.return_value = 'available'
        state = MagicMock(current_level=0, current_chance=0.5, rp_allocation=0)
        positions = {'n1': (400, 300)}

        renderer = _make_renderer(
            renderer_module, node_positions=positions,
            nodes={'n1': node}, states={'n1': state}, zoom=1.0
        )

        rendered_strings = []

        # Patch get_font in the renderer module to return a fake font
        class _FakeFont:
            def size(self, text):
                return (len(text) * 20, 14)
            def render(self, text, antialias, color):
                rendered_strings.append(text)
                surf = MagicMock(spec=pygame.Surface)
                surf.get_height.return_value = 14
                surf.get_width.return_value = len(text) * 5
                return surf

        monkeypatch.setattr(renderer_module, 'get_font', lambda size: _FakeFont())
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'rect', lambda *a, **kw: None
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_nodes(screen, None, {})

        # The rendered name should end with "..."
        assert any(s.endswith('...') for s in rendered_strings)

    def test_chance_label_only_rendered_when_status_available(
            self, renderer_module, monkeypatch):
        # Status 'completed' should NOT render chance text
        node = _make_node('n1', name='X')
        node.get_status.return_value = 'completed'
        state = MagicMock(current_level=2, current_chance=0.5, rp_allocation=0)
        positions = {'n1': (400, 300)}

        renderer = _make_renderer(
            renderer_module, node_positions=positions,
            nodes={'n1': node}, states={'n1': state}, zoom=1.0
        )

        rendered = []

        class _FakeFont:
            def size(self, text):
                return (len(text) * 5, 14)
            def render(self, text, antialias, color):
                rendered.append(text)
                surf = MagicMock(spec=pygame.Surface)
                surf.get_height.return_value = 14
                surf.get_width.return_value = len(text) * 5
                return surf

        monkeypatch.setattr(renderer_module, 'get_font', lambda size: _FakeFont())
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'rect', lambda *a, **kw: None
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_nodes(screen, None, {})

        # No rendered string should contain a "%" (chance label format)
        assert not any('%' in s for s in rendered)

    def test_rp_color_text_muted_when_allocation_zero(
            self, renderer_module, monkeypatch):
        node = _make_node('n1', name='X')
        node.get_status.return_value = 'available'
        state = MagicMock(current_level=0, current_chance=0.5, rp_allocation=0)
        positions = {'n1': (400, 300)}

        renderer = _make_renderer(
            renderer_module, node_positions=positions,
            nodes={'n1': node}, states={'n1': state}, zoom=1.0
        )

        # Capture color args for "RP" string render
        rp_color_seen = []

        class _FakeFont:
            def size(self, text):
                return (len(text) * 5, 14)
            def render(self, text, antialias, color):
                if 'RP' in text:
                    rp_color_seen.append(color)
                surf = MagicMock(spec=pygame.Surface)
                surf.get_height.return_value = 14
                surf.get_width.return_value = len(text) * 5
                return surf

        monkeypatch.setattr(renderer_module, 'get_font', lambda size: _FakeFont())
        monkeypatch.setattr(
            renderer_module.pygame.draw, 'rect', lambda *a, **kw: None
        )

        screen = MagicMock(spec=pygame.Surface)
        renderer._draw_nodes(screen, None, {})

        assert renderer_module.TEXT_MUTED in rp_color_seen


# ---- Section F: misc -------------------------------------------------------

class TestMisc:

    def test_get_font_enforces_minimum_size_8(
            self, renderer_module, monkeypatch):
        renderer = _make_renderer(renderer_module)

        seen_sizes = []
        monkeypatch.setattr(
            renderer_module, 'get_font',
            lambda size: seen_sizes.append(size) or MagicMock()
        )

        renderer._get_font(2)
        renderer._get_font(0)
        renderer._get_font(-5)

        # All small sizes should be clamped to 8
        assert all(s == 8 for s in seen_sizes)
