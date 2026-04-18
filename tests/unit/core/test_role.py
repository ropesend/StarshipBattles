"""Tests for game.core.roles.Role — frozen dataclass for role definitions.

Role is the shared schema used by both the gameplay design_role registry and
the Combat Lab scenario_role registry (PROJ-278).
"""
import dataclasses

import pytest

from game.core.roles import Role


class TestRole:
    """Role is a frozen DTO describing one role with optional vehicle_type filtering."""

    def test_create_with_required_fields_defaults_empty_filter(self):
        role = Role(
            id="carrier",
            display_name="Carrier",
            description="Hangar-bay focused capital ship.",
        )
        assert role.id == "carrier"
        assert role.display_name == "Carrier"
        assert role.description == "Hangar-bay focused capital ship."
        assert role.vehicle_type_filter == ()

    def test_create_with_explicit_vehicle_type_filter(self):
        role = Role(
            id="interceptor",
            display_name="Interceptor",
            description="Fast intercept role.",
            vehicle_type_filter=("Fighter", "Frigate"),
        )
        assert role.vehicle_type_filter == ("Fighter", "Frigate")

    def test_frozen_immutability(self):
        role = Role(id="x", display_name="X", description="x")
        with pytest.raises(dataclasses.FrozenInstanceError):
            role.id = "y"
        with pytest.raises(dataclasses.FrozenInstanceError):
            role.display_name = "Y"
        with pytest.raises(dataclasses.FrozenInstanceError):
            role.vehicle_type_filter = ("Frigate",)

    def test_equality_same_fields_are_equal(self):
        a = Role(id="x", display_name="X", description="x")
        b = Role(id="x", display_name="X", description="x")
        assert a == b
        assert hash(a) == hash(b)

    def test_equality_same_id_different_other_fields_are_unequal(self):
        a = Role(id="x", display_name="X", description="x")
        b = Role(id="x", display_name="X-renamed", description="x")
        assert a != b

    def test_id_is_required(self):
        with pytest.raises(TypeError):
            Role(display_name="X", description="x")  # type: ignore[call-arg]

    def test_display_name_is_required(self):
        with pytest.raises(TypeError):
            Role(id="x", description="x")  # type: ignore[call-arg]

    def test_description_is_required(self):
        with pytest.raises(TypeError):
            Role(id="x", display_name="X")  # type: ignore[call-arg]

    def test_vehicle_type_filter_is_tuple_not_list(self):
        """Tuple typing matters for hashability + frozen-dataclass equality."""
        role = Role(
            id="x",
            display_name="X",
            description="x",
            vehicle_type_filter=("Frigate",),
        )
        assert isinstance(role.vehicle_type_filter, tuple)

    def test_import_path(self):
        from game.core.roles import Role as R
        assert R is Role
