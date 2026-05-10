"""Tests for build_queue_list_window module - UI for showing all build queues.

PROJ-328 Phase A Task A.2: Migrated from the legacy ``__new__`` /
``patch.object(...,_build_list)`` bypass pattern to the two-stage
construction pattern. Tests now exercise the real ``__init__`` under
``bypass_init`` and pass an explicit ``MockBuildQueueListUiBuilder`` so
``screen.row_labels`` is populated honestly via the production
``BuildQueueRowCollector``.

PROJ-322 Tasks 5.29 + 3.19 closed by this migration.
"""

from unittest.mock import MagicMock
import pygame

from game.ui.screens.build_queue_list_window import (
    BuildQueueListWindow,
    BuildQueueRowCollector,
)
from tests.fixtures.build_queue_list_ui_builder import (
    MockBuildQueueListUiBuilder,
    NullBuildQueueListUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init


def _make_window(empire, *, ui_builder=None, on_close_callback=None,
                 input_mapper=None):
    """Construct a real ``BuildQueueListWindow`` under ``bypass_init``.

    The two-stage constructor runs Stage 1 (cheap state) and Stage 2
    (bypass shell), then invokes ``ui_builder.build(self)`` if one is
    supplied (PROJ-325 PoC finding 2). Default builder is the Mock
    variant — most tests want populated ``row_labels``.
    """
    if ui_builder is None:
        ui_builder = MockBuildQueueListUiBuilder()
    with bypass_init(BuildQueueListWindow):
        return BuildQueueListWindow(
            pygame.Rect(0, 0, 400, 300),
            MagicMock(name="ui_manager"),
            empire,
            window_manager=None,
            on_close_callback=on_close_callback,
            input_mapper=input_mapper,
            ui_builder=ui_builder,
        )


class TestBuildQueueListWindowInit:
    """Stage-1 cheap state survives bypass_init."""

    def test_stores_empire_reference(self):
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        window = _make_window(empire)
        assert window.empire is empire

    def test_stores_callback(self):
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        callback = MagicMock()
        window = _make_window(empire, on_close_callback=callback)
        assert window.on_close_callback is callback

    def test_stores_input_mapper(self):
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        mapper = MagicMock()
        window = _make_window(empire, input_mapper=mapper)
        assert window._mapper is mapper

    def test_default_row_collector_is_real(self):
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        window = _make_window(empire)
        assert isinstance(window._row_collector, BuildQueueRowCollector)

    def test_window_init_bypassed_flag_set(self):
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        window = _make_window(empire)
        assert window._window_init_bypassed is True

    def test_null_builder_leaves_row_labels_empty(self):
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        window = _make_window(empire, ui_builder=NullBuildQueueListUiBuilder())
        assert window.row_labels == []


class TestBuildQueueRowCollector:
    """The pure-data row collector — no bypass / no widgets needed."""

    def test_collects_colony_queue_items(self):
        planet = MagicMock()
        planet.name = "Earth"
        planet.construction_queue = [
            {'design_id': 'Frigate', 'turns_remaining': 3, 'type': 'ship'}
        ]
        empire = MagicMock()
        empire.colonies = [planet]
        empire.fleets = []

        rows = BuildQueueRowCollector().collect(empire)
        assert len(rows) == 1
        assert rows[0].location == "Earth"
        assert rows[0].design_id == "Frigate"
        assert "Earth" in rows[0].text
        assert "Frigate" in rows[0].text

    def test_collects_fleet_queue_items(self):
        fleet = MagicMock()
        fleet.name = "First Fleet"
        fleet.construction_queue = [
            {'design_id': 'Cruiser', 'turns_remaining': 5, 'type': 'ship'}
        ]
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = [fleet]

        rows = BuildQueueRowCollector().collect(empire)
        assert len(rows) == 1
        assert rows[0].location == "First Fleet"
        assert "Cruiser" in rows[0].text

    def test_skips_fleets_without_queue(self):
        fleet_with_queue = MagicMock()
        fleet_with_queue.name = "Has Queue"
        fleet_with_queue.construction_queue = [
            {'design_id': 'Ship', 'turns_remaining': 1}
        ]

        fleet_without = MagicMock()
        fleet_without.name = "No Queue"
        fleet_without.construction_queue = []

        empire = MagicMock()
        empire.colonies = []
        empire.fleets = [fleet_with_queue, fleet_without]

        rows = BuildQueueRowCollector().collect(empire)
        assert len(rows) == 1
        assert rows[0].location == "Has Queue"

    def test_handles_missing_fields(self):
        planet = MagicMock()
        planet.name = "Mars"
        planet.construction_queue = [{}]  # missing every field
        empire = MagicMock()
        empire.colonies = [planet]
        empire.fleets = []

        rows = BuildQueueRowCollector().collect(empire)
        assert len(rows) == 1
        assert rows[0].design_id == "?"
        assert rows[0].turns_remaining == "?"
        assert rows[0].item_type == "ship"

    def test_empty_empire_yields_no_rows(self):
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        rows = BuildQueueRowCollector().collect(empire)
        assert rows == []


class TestMockBuilderRowPopulation:
    """The MockBuildQueueListUiBuilder routes through the real
    BuildQueueRowCollector, so seeding the empire produces the right
    number of mock labels."""

    def test_colony_queue_populates_row_labels(self):
        planet = MagicMock()
        planet.name = "Earth"
        planet.construction_queue = [
            {'design_id': 'Frigate', 'turns_remaining': 3, 'type': 'ship'}
        ]
        empire = MagicMock()
        empire.colonies = [planet]
        empire.fleets = []

        window = _make_window(empire)
        # 1 header + 1 row label
        assert len(window.row_labels) == 2

    def test_empty_empire_emits_header_plus_empty_label(self):
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        window = _make_window(empire)
        # 1 header + 1 empty-state label
        assert len(window.row_labels) == 2


class TestKeyboardHandling:
    def test_handle_keydown_without_mapper_returns_false(self):
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        window = _make_window(empire, input_mapper=None)
        event = MagicMock()
        assert window._handle_keydown(event) is False

    def test_close_action_kills_window(self):
        from game.core.input_actions import InputAction

        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        mapper = MagicMock()
        mapper.resolve.return_value = InputAction.BUILD_QUEUE_CLOSE

        window = _make_window(empire, input_mapper=mapper)
        window.row_labels = []  # avoid touching pygame in kill()
        window.kill = MagicMock()  # spy

        event = MagicMock()
        result = window._handle_keydown(event)

        assert result is True
        window.kill.assert_called_once()

    def test_unhandled_action_returns_false(self):
        from game.core.input_actions import InputAction

        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        mapper = MagicMock()
        mapper.resolve.return_value = InputAction.GLOBAL_EXIT

        window = _make_window(empire, input_mapper=mapper)
        event = MagicMock()
        result = window._handle_keydown(event)

        assert result is False


class TestKill:
    def test_kills_all_labels(self):
        planet = MagicMock()
        planet.name = "Earth"
        planet.construction_queue = [
            {'design_id': 'Frigate', 'turns_remaining': 3, 'type': 'ship'}
        ]
        empire = MagicMock()
        empire.colonies = [planet]
        empire.fleets = []

        window = _make_window(empire)
        labels_before = list(window.row_labels)
        assert labels_before  # sanity: at least the header

        # Stub out the base UIWindow.kill (we're under bypass_init so
        # super().kill() would still try to interact with pygame state).
        from unittest.mock import patch
        with patch('pygame_gui.elements.UIWindow.kill'):
            window.kill()

        for lbl in labels_before:
            lbl.kill.assert_called()
        assert window.row_labels == []

    def test_calls_close_callback(self):
        empire = MagicMock()
        empire.colonies = []
        empire.fleets = []
        callback = MagicMock()
        window = _make_window(empire, on_close_callback=callback)

        from unittest.mock import patch
        with patch('pygame_gui.elements.UIWindow.kill'):
            window.kill()

        callback.assert_called_once()
