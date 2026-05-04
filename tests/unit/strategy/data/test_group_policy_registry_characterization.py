"""Characterization tests for game/strategy/data/group_policy_registry.py.

PROJ-335 Phase 1. Pins:

- Fresh-registry state: ``_loaded`` is False; all axes empty; all
  ``is_valid_*`` return False.
- ``load(file_path)`` real I/O via tmp_path (D-005); populates the three
  axes from top-level keys ``targeting`` / ``movement`` / ``retreat``.
- Missing-file fallback: ``load`` does not raise (load_json default={}),
  sets ``_loaded`` True with empty axes.
- ``validate_policy`` per-axis behavior: None means inherit (skipped, no
  error); invalid id produces an exact-format error string; multi-axis
  errors emit in axis order (targeting, movement, retreat).

Mode: characterization-only — pin the literal ``"Invalid {axis} policy:
'{id}'"`` format string per D-007.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from game.strategy.data.fleet_hierarchy import CombatPolicy
from game.strategy.data.group_policy_registry import GroupPolicyRegistry


# ---------------------------------------------------------------------------
# Fresh-registry state
# ---------------------------------------------------------------------------

class TestFreshRegistry:
    """Pin the pre-load state."""

    def test_fresh_registry_is_not_loaded(self):
        reg = GroupPolicyRegistry()
        assert reg._loaded is False

    def test_fresh_registry_axes_are_empty(self):
        reg = GroupPolicyRegistry()
        assert reg.targeting_policies == {}
        assert reg.movement_policies == {}
        assert reg.retreat_policies == {}

    def test_fresh_registry_is_valid_returns_false_for_any_id(self):
        reg = GroupPolicyRegistry()
        assert reg.is_valid_targeting("anything") is False
        assert reg.is_valid_movement("anything") is False
        assert reg.is_valid_retreat("anything") is False

    def test_fresh_registry_get_returns_none(self):
        reg = GroupPolicyRegistry()
        assert reg.get_targeting("anything") is None
        assert reg.get_movement("anything") is None
        assert reg.get_retreat("anything") is None


# ---------------------------------------------------------------------------
# load (real I/O via tmp_path)
# ---------------------------------------------------------------------------

class TestLoadFromFile:
    """D-005: real I/O via tmp_path so the JSON file format is part of the
    pinned contract."""

    def _write_policies(self, tmp_path: Path) -> Path:
        path = tmp_path / "policies.json"
        path.write_text(json.dumps({
            "targeting": {
                "aggressive": {"priority": "highest_threat"},
                "defensive": {"priority": "self_preservation"},
            },
            "movement": {
                "stay": {"behavior": "hold_position"},
            },
            "retreat": {
                "never": {"threshold": 0},
            },
        }))
        return path

    def test_load_populates_all_three_axes(self, tmp_path):
        reg = GroupPolicyRegistry()
        reg.load(str(self._write_policies(tmp_path)))

        assert reg._loaded is True
        assert set(reg.targeting_policies.keys()) == {"aggressive", "defensive"}
        assert set(reg.movement_policies.keys()) == {"stay"}
        assert set(reg.retreat_policies.keys()) == {"never"}

    def test_is_valid_after_load(self, tmp_path):
        reg = GroupPolicyRegistry()
        reg.load(str(self._write_policies(tmp_path)))

        assert reg.is_valid_targeting("aggressive") is True
        assert reg.is_valid_targeting("unknown") is False
        assert reg.is_valid_movement("stay") is True
        assert reg.is_valid_retreat("never") is True

    def test_get_after_load_returns_definition_dict(self, tmp_path):
        reg = GroupPolicyRegistry()
        reg.load(str(self._write_policies(tmp_path)))

        assert reg.get_targeting("aggressive") == {"priority": "highest_threat"}
        assert reg.get_targeting("unknown") is None
        assert reg.get_movement("stay") == {"behavior": "hold_position"}


class TestLoadMissingFile:
    """Missing file falls through ``load_json(default={})`` — no exception,
    empty axes, ``_loaded`` True."""

    def test_missing_file_does_not_raise(self, tmp_path):
        reg = GroupPolicyRegistry()
        missing = tmp_path / "definitely_not_here.json"

        # No exception expected.
        reg.load(str(missing))

    def test_missing_file_leaves_axes_empty_and_marks_loaded(self, tmp_path):
        reg = GroupPolicyRegistry()
        missing = tmp_path / "definitely_not_here.json"
        reg.load(str(missing))

        assert reg._loaded is True
        assert reg.targeting_policies == {}
        assert reg.movement_policies == {}
        assert reg.retreat_policies == {}


# ---------------------------------------------------------------------------
# validate_policy
# ---------------------------------------------------------------------------

class TestValidatePolicyAllNone:
    """None on an axis means inherit, not invalid."""

    def test_empty_policy_returns_no_errors(self):
        reg = GroupPolicyRegistry()  # empty registry
        errors = reg.validate_policy(CombatPolicy())

        assert errors == []


class TestValidatePolicyInvalidIds:
    """Pin the literal error string format and multi-error ordering."""

    @pytest.fixture
    def loaded_registry(self, tmp_path) -> GroupPolicyRegistry:
        path = tmp_path / "policies.json"
        path.write_text(json.dumps({
            "targeting": {"aggressive": {}},
            "movement": {"stay": {}},
            "retreat": {"never": {}},
        }))
        reg = GroupPolicyRegistry()
        reg.load(str(path))
        return reg

    def test_single_invalid_targeting_format(self, loaded_registry):
        errors = loaded_registry.validate_policy(
            CombatPolicy(targeting="bogus")
        )

        assert errors == ["Invalid targeting policy: 'bogus'"]

    def test_single_invalid_movement_format(self, loaded_registry):
        errors = loaded_registry.validate_policy(
            CombatPolicy(movement="not_a_thing")
        )

        assert errors == ["Invalid movement policy: 'not_a_thing'"]

    def test_single_invalid_retreat_format(self, loaded_registry):
        errors = loaded_registry.validate_policy(
            CombatPolicy(retreat="??")
        )

        assert errors == ["Invalid retreat policy: '??'"]

    def test_valid_id_produces_no_error(self, loaded_registry):
        errors = loaded_registry.validate_policy(
            CombatPolicy(
                targeting="aggressive",
                movement="stay",
                retreat="never",
            )
        )

        assert errors == []

    def test_multi_axis_errors_emitted_in_axis_order(self, loaded_registry):
        """Order: targeting, movement, retreat."""
        errors = loaded_registry.validate_policy(
            CombatPolicy(
                targeting="bogus_t",
                movement="bogus_m",
                retreat="bogus_r",
            )
        )

        assert errors == [
            "Invalid targeting policy: 'bogus_t'",
            "Invalid movement policy: 'bogus_m'",
            "Invalid retreat policy: 'bogus_r'",
        ]

    def test_partial_invalid_only_flags_bad_axes(self, loaded_registry):
        errors = loaded_registry.validate_policy(
            CombatPolicy(
                targeting="aggressive",  # valid
                movement="bogus_m",      # invalid
                retreat=None,            # inherit
            )
        )

        assert errors == ["Invalid movement policy: 'bogus_m'"]
