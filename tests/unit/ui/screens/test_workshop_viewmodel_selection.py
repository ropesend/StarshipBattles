from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from game.core.constants import LayerType
from game.ui.screens import workshop_viewmodel_selection as selection


class _Component:
    def __init__(self, component_id: str) -> None:
        self.id = component_id


def _ship_with_layers(*components: _Component) -> SimpleNamespace:
    return SimpleNamespace(
        layers={
            LayerType.CORE: SimpleNamespace(components=list(components[:1])),
            LayerType.INNER: SimpleNamespace(components=list(components[1:])),
        }
    )


def test_normalize_selection_passes_existing_tuples_through() -> None:
    component = _Component("laser")
    item = (LayerType.CORE, 0, component)

    assert selection.normalize_selection([item], ship=None) == [item]


def test_normalize_selection_finds_component_coordinates_on_ship() -> None:
    first = _Component("armor")
    target = _Component("shield")
    ship = _ship_with_layers(first, target)

    normalized = selection.normalize_selection([target], ship)

    assert normalized == [(LayerType.INNER, 0, target)]


def test_normalize_selection_marks_template_components_without_ship_location() -> None:
    template = _Component("template")

    normalized = selection.normalize_selection([template], ship=None)

    assert normalized == [(None, -1, template)]


def test_append_selection_replaces_when_component_types_differ() -> None:
    current_component = _Component("laser")
    incoming_component = _Component("shield")
    current = [(LayerType.CORE, 0, current_component)]
    incoming = [(LayerType.INNER, 0, incoming_component)]

    result = selection.apply_append_selection(current, incoming, toggle=False)

    assert result == incoming


def test_append_selection_toggles_existing_object_off_without_readding_duplicate() -> None:
    component = _Component("laser")
    sibling = _Component("laser")
    current = [
        (LayerType.CORE, 0, component),
        (LayerType.INNER, 0, sibling),
    ]
    incoming = [
        (LayerType.CORE, 0, component),
        (LayerType.CORE, 0, component),
    ]

    result = selection.apply_append_selection(current, incoming, toggle=True)

    assert result == [(LayerType.INNER, 0, sibling)]


def test_append_selection_keeps_current_when_incoming_empty() -> None:
    component = _Component("laser")
    current = [(LayerType.CORE, 0, component)]

    result = selection.apply_append_selection(current, [], toggle=True)

    assert result == current
    assert result is not current


def test_sync_modifiers_to_selection_skips_primary_component(
    monkeypatch,
) -> None:
    primary = _Component("laser")
    sibling = _Component("laser")
    copy_modifiers = MagicMock()
    monkeypatch.setattr(
        "game.ui.screens.builder.modifier_utils.copy_modifiers",
        copy_modifiers,
    )

    selection.sync_modifiers_to_selection(
        primary,
        [
            (LayerType.CORE, 0, primary),
            (LayerType.INNER, 0, sibling),
        ],
    )

    copy_modifiers.assert_called_once_with(primary, sibling)
