"""PROJ-499 — Comparator strictness pinning.

The legacy ``compare_snapshots()`` (``conftest.py:139-173``) walked
``for key in expected_val`` only and silently ignored any extra key
present in ``actual``. That asymmetry let PROJ-489's re-shot baselines
add 4 new ``StatKey`` enum members while 58 sibling baselines stayed
GREEN despite lacking those keys. PROJ-499 tightens
``compare_snapshots()`` to walk the union of key sets and report
"unexpected key in actual" diffs.

These tests pin the symmetric contract:

* ``test_extra_top_level_key_in_actual_is_reported`` — flat case.
* ``test_extra_nested_dict_key_in_actual_is_reported`` — mirrors the
  real ``component.stats`` shape that the regression exploited.
* ``test_extra_key_in_abilities_list_element_is_reported`` — nested
  list-of-dicts case (the ``abilities`` array in
  ``snapshot_full_component``).
* ``test_strictness_negative_guard`` — Phase 4 add-on; loads a real
  baseline file, injects a canary, asserts the diff fires.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from tests.regression.modifier_ability_snapshots.conftest import (
    compare_snapshots,
    get_snapshots_dir,
)


def _join_diffs(diffs: list[str]) -> str:
    """Join diff list for inclusion in assertion messages."""
    return "\n  ".join(diffs) if diffs else "<no diffs>"


def test_extra_top_level_key_in_actual_is_reported() -> None:
    """Flat case: extra key in ``actual`` must be reported as a diff."""
    actual = {"a": 1, "b": 2}
    expected = {"a": 1}

    diffs = compare_snapshots(actual, expected)

    assert diffs, (
        "compare_snapshots returned no diffs for actual with an extra key. "
        "It silently ignored the extra `b` -- symmetric contract broken."
    )
    joined = " ".join(diffs)
    assert "b" in joined, (
        f"Expected diff to mention key 'b'. Got:\n  {_join_diffs(diffs)}"
    )


def test_extra_nested_dict_key_in_actual_is_reported() -> None:
    """Nested case: extra key inside ``component.stats`` must be reported.

    Mirrors the exact shape that the PROJ-499 bug exploited. The legacy
    comparator iterates ``for key in expected_val``, never reaches
    ``launch_rate_mult`` because ``expected`` does not contain it, and
    returns no diff.
    """
    actual = {"component": {"stats": {"mass_mult": 1.0, "launch_rate_mult": 1.0}}}
    expected = {"component": {"stats": {"mass_mult": 1.0}}}

    diffs = compare_snapshots(actual, expected)

    assert diffs, (
        "compare_snapshots returned no diffs for an extra nested key. "
        "This is the exact PROJ-489 schema-drift escape hatch."
    )
    joined = " ".join(diffs)
    assert "launch_rate_mult" in joined, (
        f"Expected diff to mention 'launch_rate_mult'. Got:\n  "
        f"{_join_diffs(diffs)}"
    )


def test_extra_key_in_abilities_list_element_is_reported() -> None:
    """List-of-dicts case: extra key in an ``abilities[i]`` element must
    be reported. ``snapshot_full_component`` emits a list of ability
    dicts; the comparator must remain strict inside list elements too.
    """
    actual = {"abilities": [{"damage": 1, "new_field": 2}]}
    expected = {"abilities": [{"damage": 1}]}

    diffs = compare_snapshots(actual, expected)

    assert diffs, (
        "compare_snapshots returned no diffs for an extra key inside a "
        "list element. The list-branch recursion inherited the same gap."
    )
    joined = " ".join(diffs)
    assert "new_field" in joined, (
        f"Expected diff to mention 'new_field'. Got:\n  {_join_diffs(diffs)}"
    )


def test_strictness_negative_guard() -> None:
    """Negative guard: load a real baseline, inject a canary key into a
    deep-copy of the loaded data, and assert ``compare_snapshots`` flags it
    as an unexpected key.

    If this test fails, someone weakened ``compare_snapshots()`` back to
    asymmetric iteration. Revert that change. The whole point of PROJ-499
    is that schema drift between live and baseline is loud, not silent.

    Verifies BOTH directions of strictness:
      1. extra key in ``actual`` (regression direction PROJ-489 exploited)
      2. extra key in ``expected`` (a stale baseline carrying a removed key)
    """
    baseline_path = get_snapshots_dir() / "railgun_no_modifiers.json"
    with open(baseline_path, "r", encoding="utf-8") as f:
        baseline = json.load(f)

    # Direction 1: actual has an extra key that baseline does not.
    actual_with_extra = copy.deepcopy(baseline)
    actual_with_extra["component"]["stats"]["__strictness_canary__"] = "should fail"

    diffs_extra_in_actual = compare_snapshots(actual_with_extra, baseline)
    assert diffs_extra_in_actual, (
        "PROJ-499 STRICTNESS REGRESSION: compare_snapshots did not flag an "
        "extra key in `actual` that the baseline lacked. The asymmetric gap "
        "is back. Revert the conftest.py change."
    )
    joined_1 = " ".join(diffs_extra_in_actual)
    assert "__strictness_canary__" in joined_1, (
        f"PROJ-499 STRICTNESS REGRESSION: extra-key diff present but does not "
        f"name the canary key. Got:\n  {_join_diffs(diffs_extra_in_actual)}"
    )

    # Direction 2: baseline (expected) has an extra key that actual does not.
    # Pre-PROJ-499 comparator already handled this direction (it iterates
    # ``for key in expected``), so this assertion is the regression-floor.
    # We pin it explicitly so a future "optimization" cannot silently drop
    # the missing-in-actual branch.
    expected_with_extra = copy.deepcopy(baseline)
    expected_with_extra["component"]["stats"]["__missing_canary__"] = "removed"

    diffs_missing_in_actual = compare_snapshots(baseline, expected_with_extra)
    assert diffs_missing_in_actual, (
        "PROJ-499 STRICTNESS REGRESSION: compare_snapshots did not flag a "
        "key present in baseline (expected) but missing from actual. The "
        "missing-in-actual branch was silently dropped."
    )
    joined_2 = " ".join(diffs_missing_in_actual)
    assert "__missing_canary__" in joined_2, (
        f"PROJ-499 STRICTNESS REGRESSION: missing-key diff present but does "
        f"not name the canary key. Got:\n  {_join_diffs(diffs_missing_in_actual)}"
    )
