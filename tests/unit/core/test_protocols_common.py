"""Tests for shared protocol helper behavior."""

from game.core.protocols import _has_attrs


class DynamicThing:
    """Object with one real attribute and one dynamic property."""

    existing = "value"

    @property
    def dynamic_value(self) -> str:
        return "computed"


def test_has_attrs_empty_attr_list_returns_true() -> None:
    """No required attributes is vacuously true."""
    assert _has_attrs(object()) is True


def test_has_attrs_accepts_dynamic_properties() -> None:
    """Properties exposed through normal attribute lookup satisfy the helper."""
    assert _has_attrs(DynamicThing(), "existing", "dynamic_value") is True


def test_has_attrs_returns_false_for_missing_attribute() -> None:
    """Missing any required attribute makes the object fail the check."""
    assert _has_attrs(DynamicThing(), "existing", "missing") is False


def test_has_attrs_reexported_from_protocol_package() -> None:
    """The private helper remains available through the package re-export."""
    import game.core.protocols as protocols

    assert protocols._has_attrs is _has_attrs
