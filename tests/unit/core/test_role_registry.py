"""Tests for game.core.roles.RoleRegistry — generic role registry (PROJ-278).

Two registry instances exist in the running app (`design_role_registry` for
gameplay archetypes; `combat_lab_role_registry` for Combat Lab scenario
wiring). This module tests the shared machinery in isolation — no callers
wired yet, no I/O layer dependencies.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pytest

from game.core.roles import (
    Role,
    RoleRegistry,
    RoleRegistryReadOnlyError,
)


def _write_roles_json(tmp_path: Path, roles: List[dict], filename: str = "roles.json") -> Path:
    """Helper: write a {"roles": [...]} JSON file in tmp_path and return path."""
    p = tmp_path / filename
    p.write_text(json.dumps({"roles": roles}), encoding="utf-8")
    return p


class TestRoleRegistryEmpty:
    """Behavior of an empty registry."""

    def test_empty_registry_all_returns_empty_list(self):
        reg = RoleRegistry(allow_runtime_add=True)
        assert reg.all() == []

    def test_empty_registry_get_raises_keyerror(self):
        reg = RoleRegistry(allow_runtime_add=True)
        with pytest.raises(KeyError):
            reg.get("missing")

    def test_empty_registry_contains_returns_false(self):
        reg = RoleRegistry(allow_runtime_add=True)
        assert "missing" not in reg


class TestRoleRegistryLoading:
    """Loading roles from JSON files."""

    def test_load_from_file_populates_roles(self, tmp_path):
        path = _write_roles_json(tmp_path, [
            {"id": "carrier", "display_name": "Carrier", "description": "Hangar."},
            {"id": "interceptor", "display_name": "Interceptor", "description": "Fast."},
        ])
        reg = RoleRegistry(allow_runtime_add=True)
        reg.load_from_file(path, source_tag="base")

        assert len(reg.all()) == 2
        assert reg.get("carrier").display_name == "Carrier"
        assert reg.get("interceptor").description == "Fast."

    def test_load_from_file_reads_vehicle_type_filter(self, tmp_path):
        path = _write_roles_json(tmp_path, [
            {
                "id": "carrier",
                "display_name": "Carrier",
                "description": "...",
                "vehicle_type_filter": ["Battleship", "Cruiser"],
            },
        ])
        reg = RoleRegistry(allow_runtime_add=True)
        reg.load_from_file(path, source_tag="base")

        assert reg.get("carrier").vehicle_type_filter == ("Battleship", "Cruiser")

    def test_load_from_file_defaults_vehicle_type_filter_to_empty_tuple(self, tmp_path):
        path = _write_roles_json(tmp_path, [
            {"id": "x", "display_name": "X", "description": "x"},
        ])
        reg = RoleRegistry(allow_runtime_add=True)
        reg.load_from_file(path, source_tag="base")

        assert reg.get("x").vehicle_type_filter == ()

    def test_later_source_overrides_earlier_source(self, tmp_path):
        """Precedence: later load_from_file calls override earlier ones for same id."""
        base = _write_roles_json(tmp_path, [
            {"id": "carrier", "display_name": "Carrier (base)", "description": "base"},
        ], filename="base.json")
        overlay = _write_roles_json(tmp_path, [
            {"id": "carrier", "display_name": "Carrier (overlay)", "description": "overlay"},
        ], filename="overlay.json")

        reg = RoleRegistry(allow_runtime_add=True)
        reg.load_from_file(base, source_tag="base")
        reg.load_from_file(overlay, source_tag="user")

        carrier = reg.get("carrier")
        assert carrier.display_name == "Carrier (overlay)"
        assert carrier.description == "overlay"

    def test_load_from_missing_file_raises(self, tmp_path):
        """Critical config — a missing file is a loud failure, not a silent skip."""
        reg = RoleRegistry(allow_runtime_add=True)
        with pytest.raises(FileNotFoundError):
            reg.load_from_file(tmp_path / "does_not_exist.json", source_tag="base")

    def test_load_from_malformed_json_raises(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json", encoding="utf-8")
        reg = RoleRegistry(allow_runtime_add=True)
        with pytest.raises(json.JSONDecodeError):
            reg.load_from_file(bad, source_tag="base")

    def test_load_skips_underscore_prefixed_keys_in_role_dict(self, tmp_path):
        """Per project memory: `_`-prefixed JSON keys are comments/section headers."""
        path = _write_roles_json(tmp_path, [
            {"id": "x", "display_name": "X", "description": "x", "_comment": "ignore me"},
        ])
        reg = RoleRegistry(allow_runtime_add=True)
        reg.load_from_file(path, source_tag="base")

        assert reg.get("x").id == "x"  # loaded successfully despite extra key

    def test_all_returns_roles_sorted_by_id(self, tmp_path):
        """Deterministic iteration order — sorted by id."""
        path = _write_roles_json(tmp_path, [
            {"id": "z", "display_name": "Z", "description": "z"},
            {"id": "a", "display_name": "A", "description": "a"},
            {"id": "m", "display_name": "M", "description": "m"},
        ])
        reg = RoleRegistry(allow_runtime_add=True)
        reg.load_from_file(path, source_tag="base")

        ids = [r.id for r in reg.all()]
        assert ids == ["a", "m", "z"]


class TestRoleRegistryLoadOptional:
    """`load_from_file_optional` tolerates a missing file (returns silently)
    but still raises on malformed JSON. Used for the user-overlay path
    that won't exist on first run."""

    def test_load_from_file_optional_with_missing_file_is_noop(self, tmp_path):
        reg = RoleRegistry(allow_runtime_add=True)
        reg.load_from_file_optional(tmp_path / "missing.json", source_tag="user")
        assert reg.all() == []

    def test_load_from_file_optional_with_existing_file_loads_roles(self, tmp_path):
        path = _write_roles_json(tmp_path, [
            {"id": "x", "display_name": "X", "description": "x"},
        ])
        reg = RoleRegistry(allow_runtime_add=True)
        reg.load_from_file_optional(path, source_tag="user")
        assert reg.get("x").id == "x"

    def test_load_from_file_optional_with_malformed_json_still_raises(self, tmp_path):
        """Existence-tolerant; corruption-intolerant."""
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json", encoding="utf-8")
        reg = RoleRegistry(allow_runtime_add=True)
        with pytest.raises(json.JSONDecodeError):
            reg.load_from_file_optional(bad, source_tag="user")

    def test_load_from_file_optional_does_not_fire_invalidation(self, tmp_path):
        """Like `load_from_file`, this is initialization, not mutation."""
        path = _write_roles_json(tmp_path, [
            {"id": "x", "display_name": "X", "description": "x"},
        ])
        reg = RoleRegistry(allow_runtime_add=True)
        calls: List[int] = []
        reg.register_invalidation_callback(lambda: calls.append(1))

        reg.load_from_file_optional(path, source_tag="user")

        assert calls == []


class TestRoleRegistryQueryByVehicleType:
    """`get_roles_for_vehicle_type` returns roles whose `vehicle_type_filter`
    accepts the given vehicle type. Empty filter = matches any."""

    def test_empty_filter_matches_any_vehicle_type(self):
        reg = RoleRegistry(allow_runtime_add=True)
        reg.add_user_role(Role(id="generic", display_name="Generic", description="g"))

        assert reg.get_roles_for_vehicle_type("Ship") == [reg.get("generic")]
        assert reg.get_roles_for_vehicle_type("Fighter") == [reg.get("generic")]

    def test_non_empty_filter_matches_only_listed_types(self):
        reg = RoleRegistry(allow_runtime_add=True)
        reg.add_user_role(Role(
            id="carrier", display_name="Carrier", description="c",
            vehicle_type_filter=("Battleship", "Cruiser"),
        ))

        assert reg.get_roles_for_vehicle_type("Battleship") == [reg.get("carrier")]
        assert reg.get_roles_for_vehicle_type("Fighter") == []

    def test_result_sorted_by_display_name(self):
        reg = RoleRegistry(allow_runtime_add=True)
        reg.add_user_role(Role(id="c", display_name="Charlie", description="c"))
        reg.add_user_role(Role(id="a", display_name="Alpha", description="a"))
        reg.add_user_role(Role(id="b", display_name="Bravo", description="b"))

        names = [r.display_name for r in reg.get_roles_for_vehicle_type("Ship")]
        assert names == ["Alpha", "Bravo", "Charlie"]

    def test_returns_empty_list_when_no_roles_match(self):
        reg = RoleRegistry(allow_runtime_add=True)
        reg.add_user_role(Role(
            id="x", display_name="X", description="x",
            vehicle_type_filter=("Battleship",),
        ))

        assert reg.get_roles_for_vehicle_type("Fighter") == []

    def test_mix_of_filtered_and_unfiltered_roles(self):
        reg = RoleRegistry(allow_runtime_add=True)
        reg.add_user_role(Role(id="generic", display_name="Generic", description="g"))
        reg.add_user_role(Role(
            id="carrier", display_name="Carrier", description="c",
            vehicle_type_filter=("Battleship",),
        ))

        result = reg.get_roles_for_vehicle_type("Battleship")
        assert {r.id for r in result} == {"generic", "carrier"}


class TestRoleRegistryRuntimeAdd:
    """Runtime add behavior — gated by allow_runtime_add flag."""

    def test_add_user_role_succeeds_when_allowed(self):
        reg = RoleRegistry(allow_runtime_add=True)
        role = Role(id="custom", display_name="Custom", description="Player-added.")
        reg.add_user_role(role)

        assert reg.get("custom") is role
        assert "custom" in reg

    def test_add_user_role_raises_when_not_allowed(self):
        reg = RoleRegistry(allow_runtime_add=False)
        role = Role(id="custom", display_name="Custom", description="...")
        with pytest.raises(RoleRegistryReadOnlyError):
            reg.add_user_role(role)

    def test_add_user_role_overrides_loaded_role(self, tmp_path):
        """Runtime add behaves like the highest-precedence overlay."""
        path = _write_roles_json(tmp_path, [
            {"id": "x", "display_name": "X (loaded)", "description": "loaded"},
        ])
        reg = RoleRegistry(allow_runtime_add=True)
        reg.load_from_file(path, source_tag="base")
        reg.add_user_role(Role(id="x", display_name="X (runtime)", description="runtime"))

        assert reg.get("x").display_name == "X (runtime)"


class TestRoleRegistryInvalidation:
    """Invalidation callbacks fire when roles are added at runtime."""

    def test_invalidation_callback_fires_on_add(self):
        reg = RoleRegistry(allow_runtime_add=True)
        calls: List[int] = []
        reg.register_invalidation_callback(lambda: calls.append(1))

        reg.add_user_role(Role(id="x", display_name="X", description="x"))

        assert calls == [1]

    def test_multiple_invalidation_callbacks_all_fire(self):
        reg = RoleRegistry(allow_runtime_add=True)
        calls: List[str] = []
        reg.register_invalidation_callback(lambda: calls.append("a"))
        reg.register_invalidation_callback(lambda: calls.append("b"))
        reg.register_invalidation_callback(lambda: calls.append("c"))

        reg.add_user_role(Role(id="x", display_name="X", description="x"))

        assert calls == ["a", "b", "c"]

    def test_invalidation_callbacks_do_not_fire_on_load_from_file(self, tmp_path):
        """Loading is initialization; only runtime add fires invalidation."""
        path = _write_roles_json(tmp_path, [
            {"id": "x", "display_name": "X", "description": "x"},
        ])
        reg = RoleRegistry(allow_runtime_add=True)
        calls: List[int] = []
        reg.register_invalidation_callback(lambda: calls.append(1))

        reg.load_from_file(path, source_tag="base")

        assert calls == []

    def test_invalidation_callbacks_fire_each_time_runtime_add_called(self):
        reg = RoleRegistry(allow_runtime_add=True)
        calls: List[int] = []
        reg.register_invalidation_callback(lambda: calls.append(1))

        reg.add_user_role(Role(id="x", display_name="X", description="x"))
        reg.add_user_role(Role(id="y", display_name="Y", description="y"))
        reg.add_user_role(Role(id="z", display_name="Z", description="z"))

        assert calls == [1, 1, 1]

    def test_callback_exception_does_not_prevent_add(self):
        """A misbehaving callback should not block role registration.
        The role IS added; the exception is logged (not re-raised)."""
        reg = RoleRegistry(allow_runtime_add=True)

        def boom():
            raise RuntimeError("callback failed")

        reg.register_invalidation_callback(boom)

        # Add still succeeds; callback exception swallowed (logged, not raised)
        reg.add_user_role(Role(id="x", display_name="X", description="x"))
        assert reg.get("x").id == "x"

    def test_subsequent_callbacks_fire_after_one_raises(self):
        """One bad callback doesn't prevent later callbacks from firing."""
        reg = RoleRegistry(allow_runtime_add=True)
        calls: List[str] = []

        def boom():
            raise RuntimeError("first one fails")

        reg.register_invalidation_callback(boom)
        reg.register_invalidation_callback(lambda: calls.append("b"))
        reg.register_invalidation_callback(lambda: calls.append("c"))

        reg.add_user_role(Role(id="x", display_name="X", description="x"))

        assert calls == ["b", "c"]
