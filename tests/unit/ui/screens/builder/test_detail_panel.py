from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from game.ui.screens.builder.detail_panel import ComponentDetailPanel


class TestComponentDetailPanelSelectionDispatch:
    @pytest.mark.parametrize(
        ("selection_data", "expected"),
        [
            pytest.param(None, None, id="none"),
            pytest.param(("OUTER", 2, "component-from-tuple"), "component-from-tuple", id="tuple"),
            pytest.param(SimpleNamespace(id="laser"), "same-object", id="component-like"),
            pytest.param({"id": "dicts-do-not-dispatch"}, None, id="fallback"),
        ],
    )
    def test_worker_i_detail_panel_selection_dispatch(self, selection_data, expected) -> None:
        panel = ComponentDetailPanel.__new__(ComponentDetailPanel)
        panel.show_component = Mock()

        panel.on_selection_changed(selection_data)

        if expected == "same-object":
            panel.show_component.assert_called_once_with(selection_data)
        else:
            panel.show_component.assert_called_once_with(expected)
