"""Tests for the shared ListDataSource base class."""
from dataclasses import dataclass

from game.ui.screens.list_data_source_base import ListDataSource


@dataclass
class _Location:
    x: float
    y: float


@dataclass
class _Entity:
    name: str
    mass: float
    location: _Location


class _IconDataSource(ListDataSource):
    def __init__(self) -> None:
        super().__init__(
            [
                {"id": "icon", "type": "image"},
                {"id": "name", "attr": "name"},
                {"id": "mass", "attr": "mass", "fmt": "{:.1f}"},
                {"id": "x", "attr": "location.x", "fmt": "{:.0f}"},
                {"id": "computed", "func": lambda entity: entity.mass * 2},
                {"id": "missing", "attr": "missing.value"},
            ]
        )
        self.rendered_entities = []

    def _render_icon(self, entity):
        self.rendered_entities.append(entity)
        return f"icon:{entity.name}"


def test_update_data_controls_row_count() -> None:
    source = _IconDataSource()

    assert source.get_row_count() == 0

    source.update_data([_Entity("Scout", 12.5, _Location(3.2, 4.0))])

    assert source.get_row_count() == 1


def test_get_columns_returns_configured_columns() -> None:
    source = _IconDataSource()

    column_ids = [column["id"] for column in source.get_columns()]

    assert column_ids == ["icon", "name", "mass", "x", "computed", "missing"]


def test_get_cell_value_supports_func_attr_nested_attr_and_format() -> None:
    source = _IconDataSource()
    source.update_data([_Entity("Frigate", 42.25, _Location(7.8, 1.0))])

    assert source.get_cell_value(0, "computed") == "84.5"
    assert source.get_cell_value(0, "name") == "Frigate"
    assert source.get_cell_value(0, "mass") == "42.2"
    assert source.get_cell_value(0, "x") == "8"


def test_get_cell_value_returns_empty_or_question_mark_for_missing_data() -> None:
    source = _IconDataSource()
    source.update_data([_Entity("Frigate", 42.25, _Location(7.8, 1.0))])

    assert source.get_cell_value(99, "name") == ""
    assert source.get_cell_value(0, "unknown") == ""
    assert source.get_cell_value(0, "missing") == "?"


def test_get_cell_image_only_renders_valid_image_columns() -> None:
    source = _IconDataSource()
    entity = _Entity("Frigate", 42.25, _Location(7.8, 1.0))
    source.update_data([entity])

    assert source.get_cell_image(0, "icon") == "icon:Frigate"
    assert source.rendered_entities == [entity]
    assert source.get_cell_image(0, "name") is None
    assert source.get_cell_image(99, "icon") is None
    assert source.get_cell_image(0, "unknown") is None

