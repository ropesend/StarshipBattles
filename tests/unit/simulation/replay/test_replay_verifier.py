"""PROJ-354B Phase 1.2 — Unit tests for the pure replay verifier.

Tests in this module exercise ``verify_replay_outcome`` and
``compute_outcome_diff`` from ``game.simulation.replay.replay_verifier``.

The verifier compares the persisted ``record.outcome.data`` (a dict
captured at battle end) against the dict shape of the replayed
``BattleOutcome`` (via ``battle_outcome_to_dict``). Equality is strict
and structural; the diff is capped at ``max_diffs`` entries with a
``diff_truncated`` flag and a ``total_diff_count`` field for the count
of every detected difference.
"""
from __future__ import annotations

import copy
from typing import Any, Dict

import pytest

from game.simulation.replay import REPLAY_SCHEMA_VERSION, ReplayOutcome, ReplayRecord, ReplaySpec
from game.simulation.replay.replay_outcome_serde import battle_outcome_to_dict
from game.simulation.replay.replay_verifier import (
    Difference,
    ReplayVerificationResult,
    compute_outcome_diff,
    verify_replay_outcome,
)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _make_record() -> ReplayRecord:
    """Reuse the existing test helper from test_serialization."""
    from tests.unit.simulation.replay.test_serialization import (
        _make_minimal_battle_spec,
        _make_minimal_outcome,
    )
    spec = _make_minimal_battle_spec()
    outcome = _make_minimal_outcome()
    return ReplayRecord(
        schema_version=REPLAY_SCHEMA_VERSION,
        replay_id="r-verifier",
        captured_at="2026-05-04T00:00:00Z",
        sector_name="test",
        sector_coords=(0, 0),
        turn_number=1,
        participating_empires=("A", "B"),
        components_registry_hash="sha256:test",
        spec=ReplaySpec.from_battle_spec(spec),
        outcome=ReplayOutcome.from_battle_outcome(outcome),
    )


# ---------------------------------------------------------------------------
# compute_outcome_diff (lower-level walker)
# ---------------------------------------------------------------------------


class TestComputeOutcomeDiff:
    def test_identical_dicts_yield_no_diff(self):
        a = {"x": 1, "y": [1, 2, {"z": "ok"}]}
        b = copy.deepcopy(a)
        diff, truncated, total = compute_outcome_diff(a, b)
        assert diff == ()
        assert truncated is False
        assert total == 0

    def test_single_leaf_mismatch(self):
        a = {"teams": [{"ships": [{"current_hp": 10}]}]}
        b = {"teams": [{"ships": [{"current_hp": 7}]}]}
        diff, truncated, total = compute_outcome_diff(a, b)
        assert truncated is False
        assert total == 1
        assert len(diff) == 1
        assert diff[0].path == ("teams", 0, "ships", 0, "current_hp")
        assert diff[0].expected == 10
        assert diff[0].actual == 7

    def test_multi_leaf_mismatch(self):
        a = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
        b = {"a": 9, "b": 8, "c": 7, "d": 6, "e": 5}
        diff, truncated, total = compute_outcome_diff(a, b)
        assert total == 4
        assert truncated is False
        assert len(diff) == 4

    def test_diff_capped_at_max(self):
        # 30 leaves differ; default cap is 25.
        a = {f"k{i}": i for i in range(30)}
        b = {f"k{i}": i + 1 for i in range(30)}
        diff, truncated, total = compute_outcome_diff(a, b, max_diffs=25)
        assert truncated is True
        assert total == 30
        assert len(diff) == 25

    def test_list_length_mismatch_emits_diff(self):
        a = {"xs": [1, 2, 3]}
        b = {"xs": [1, 2]}
        diff, truncated, total = compute_outcome_diff(a, b)
        assert total >= 1
        # The path should reflect the structural mismatch
        paths = [d.path for d in diff]
        assert any(p[0] == "xs" for p in paths)

    def test_dict_key_mismatch_emits_diff(self):
        a = {"a": 1, "b": 2}
        b = {"a": 1, "c": 2}
        diff, truncated, total = compute_outcome_diff(a, b)
        assert total >= 1

    # ----- PROJ-354B audit remediation tests ------------------------------

    def test_missing_key_emits_expected_value_actual_none(self):
        """TC-C01: key in expected but missing from actual."""
        a = {"a": 1, "b": 99}
        b = {"a": 1}
        diff, _, total = compute_outcome_diff(a, b)
        assert total == 1
        assert len(diff) == 1
        assert diff[0].path == ("b",)
        assert diff[0].expected == 99
        assert diff[0].actual is None

    def test_extra_key_emits_expected_none_actual_value(self):
        """TC-C01: key in actual but missing from expected."""
        a = {"a": 1}
        b = {"a": 1, "c": 7}
        diff, _, total = compute_outcome_diff(a, b)
        assert total == 1
        assert len(diff) == 1
        assert diff[0].path == ("c",)
        assert diff[0].expected is None
        assert diff[0].actual == 7

    def test_type_mismatch_emits_diff(self):
        """TC-C02: same key but value types differ."""
        a = {"x": 1}
        b = {"x": [1]}
        diff, _, total = compute_outcome_diff(a, b)
        assert total == 1
        assert diff[0].path == ("x",)
        assert diff[0].expected == 1
        assert diff[0].actual == [1]

    def test_int_float_scalar_not_diffed(self):
        """0 and 0.0 are JSON-equivalent and should not flag as a diff."""
        diff, _, total = compute_outcome_diff({"x": 0}, {"x": 0.0})
        assert total == 0
        assert diff == ()

    def test_tuple_path_walks_like_list(self):
        """TC-C03: tuples must be walked structurally identically to lists."""
        # Tuple equal to list: no diff (CJ-01 normalization).
        diff, _, total = compute_outcome_diff({"xs": (1, 2, 3)}, {"xs": [1, 2, 3]})
        assert total == 0
        assert diff == ()

    def test_tuple_index_diff(self):
        """TC-C03: tuple element mismatch surfaces with index path."""
        a = {"xs": (1, 2, 3)}
        b = {"xs": [1, 9, 3]}
        diff, _, total = compute_outcome_diff(a, b)
        assert total == 1
        assert diff[0].path == ("xs", 1)
        assert diff[0].expected == 2
        assert diff[0].actual == 9

    def test_tuple_length_mismatch(self):
        """TC-C03: tuple-vs-list length difference produces synthetic diff."""
        a = {"xs": (1, 2, 3)}
        b = {"xs": [1, 2]}
        diff, _, total = compute_outcome_diff(a, b)
        assert total >= 1
        # The length-mismatch diff uses synthetic ``__len__`` payload (CJ-03).
        len_diffs = [d for d in diff if d.path == ("xs",)]
        assert len(len_diffs) == 1
        assert len_diffs[0].expected == {"__len__": 3}
        assert len_diffs[0].actual == {"__len__": 2}

    def test_float_drift_within_tolerance_passes(self):
        """CJ-02: sub-ULP float drift must not flag as a diff."""
        a = {"hp": 100.0}
        b = {"hp": 100.0 + 1e-12}  # well below the 1e-9 tolerance
        diff, _, total = compute_outcome_diff(a, b)
        assert total == 0
        assert diff == ()

    def test_float_drift_outside_tolerance_fails(self):
        """CJ-02: drift larger than tolerance still produces a diff."""
        a = {"hp": 100.0}
        b = {"hp": 100.5}
        diff, _, total = compute_outcome_diff(a, b)
        assert total == 1
        assert diff[0].path == ("hp",)

    def test_exactly_at_cap_diff_count(self):
        """TC-M01: 25 diffs at cap=25 must NOT trigger truncation."""
        a = {f"k{i}": i for i in range(25)}
        b = {f"k{i}": i + 1 for i in range(25)}
        diff, truncated, total = compute_outcome_diff(a, b, max_diffs=25)
        assert truncated is False
        assert total == 25
        assert len(diff) == 25

    def test_length_mismatch_does_not_carry_full_lists(self):
        """CJ-03: length-mismatch diff must use synthetic payload, not raw blobs."""
        a = {"xs": list(range(1000))}
        b = {"xs": list(range(500))}
        diff, _, total = compute_outcome_diff(a, b)
        assert total >= 1
        # The path-level diff should be the synthetic length payload,
        # not the full 1000-element list.
        len_diffs = [d for d in diff if d.path == ("xs",)]
        assert len(len_diffs) == 1
        assert len_diffs[0].expected == {"__len__": 1000}
        assert len_diffs[0].actual == {"__len__": 500}


# ---------------------------------------------------------------------------
# verify_replay_outcome (high-level)
# ---------------------------------------------------------------------------


class TestVerifyReplayOutcome:
    def test_round_trip_identity_passes(self):
        record = _make_record()
        replayed = record.outcome.to_battle_outcome()
        result = verify_replay_outcome(record, replayed)
        assert isinstance(result, ReplayVerificationResult)
        assert result.replay_id == "r-verifier"
        assert result.passed is True
        assert result.diff == ()
        assert result.diff_truncated is False
        assert result.total_diff_count == 0

    def test_single_field_divergence_fails(self):
        record = _make_record()
        replayed = record.outcome.to_battle_outcome()
        # Mutate the record's expected dict to diverge by exactly one leaf.
        # We can't mutate the frozen dataclass field directly; copy + replace.
        bad_data = copy.deepcopy(record.outcome.data)
        # Walk into a known leaf — duration_ticks is a top-level int.
        bad_data["duration_ticks"] = bad_data["duration_ticks"] + 1
        from dataclasses import replace
        bad_outcome = ReplayOutcome(
            schema_version=record.outcome.schema_version, data=bad_data
        )
        bad_record = replace(record, outcome=bad_outcome)
        result = verify_replay_outcome(bad_record, replayed)
        assert result.passed is False
        assert result.total_diff_count == 1
        assert len(result.diff) == 1
        assert result.diff[0].path == ("duration_ticks",)
        # Expected = what the record says; actual = what we replayed.
        assert result.diff[0].expected == bad_data["duration_ticks"]
        assert result.diff[0].actual == battle_outcome_to_dict(replayed)["duration_ticks"]

    def test_capped_diff_round_trip(self):
        # Force a record whose expected dict differs from the replayed
        # outcome on more than 25 leaves. We mutate the spec's seed here
        # is too coarse; instead we build a synthetic outcome dict and
        # bypass via compute_outcome_diff (already tested) and assert the
        # high-level call carries the cap through.
        record = _make_record()
        # Real round-trip yields zero diff. Construct a contrived bad
        # record by replacing every team's `ships` entry with mismatched
        # data — we'll use a record whose `outcome.data` is a deep-mutated
        # copy that diverges from the live replay on 30+ keys via direct
        # dict replacement.
        replayed = record.outcome.to_battle_outcome()
        replayed_dict = battle_outcome_to_dict(replayed)
        bad_data: Dict[str, Any] = copy.deepcopy(replayed_dict)
        # Inject 30 synthetic top-level mismatches under a new 'fake' key
        # tree that the real dict won't have at all — prepend so they're
        # all detected.
        for i in range(30):
            bad_data[f"_fake_diff_{i}"] = {"v": i}
        from dataclasses import replace
        bad_outcome = ReplayOutcome(
            schema_version=record.outcome.schema_version, data=bad_data
        )
        bad_record = replace(record, outcome=bad_outcome)
        result = verify_replay_outcome(bad_record, replayed)
        assert result.passed is False
        assert result.total_diff_count >= 30
        assert result.diff_truncated is True
        assert len(result.diff) == 25

    def test_difference_dataclass_is_frozen(self):
        d = Difference(path=("a",), expected=1, actual=2)
        with pytest.raises((AttributeError, Exception)):
            d.path = ("b",)  # type: ignore[misc]

    def test_replay_verification_result_is_frozen(self):
        """TC-M02: ReplayVerificationResult is also @dataclass(frozen=True)."""
        r = ReplayVerificationResult(
            replay_id="r1",
            passed=True,
            diff=(),
            diff_truncated=False,
            total_diff_count=0,
        )
        with pytest.raises((AttributeError, Exception)):
            r.passed = False  # type: ignore[misc]
