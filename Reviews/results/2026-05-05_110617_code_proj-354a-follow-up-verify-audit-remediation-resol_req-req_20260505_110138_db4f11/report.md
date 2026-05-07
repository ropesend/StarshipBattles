# PROJ-354A Follow-up: Verify Audit Remediation Resolved Findings

**Review Type:** code (follow-up)
**Review Mode:** follow-up verification (not a full re-review)
**Scope:** `game/strategy/combat/post_battle_hook.py`, `tests/unit/strategy/combat/test_post_battle_hook.py`, `Projects/active_projects/PROJ-354A/decisions.md`
**Parent Request:** req_20260505_055832_23a2f0
**Remediation Commit:** d956783e2
**Completed:** 2026-05-05T11:10:00Z

---

## Verification Matrix

| Parent Finding | Status | Notes |
|---|---|---|
| MAJ-001 (max_hp) | resolved | `_apply_survivor_outcome` line 166-171 reads `cs.max_hp` from outcome; defensive zero-fallback at line 168 |
| MAJ-001 (status) | deferred (sound) | `ComponentState` has no `status` field; adding one = save-format migration; engine reconciles on first tick; rationale is correct |
| MAJ-002 | resolved | Stale comment "ComponentStateSpec doesn't carry max_hp today" replaced with docstring at lines 142-153 documenting authoritative-from-outcome, zero-fallback, and intentional status drop |
| MAJ-003 | resolved | Same root cause as MAJ-001; `max_hp` at line 176 now uses resolved outcome value instead of `prior_max_hp` |

---

## Finding MAJ-001 (max_hp) — Resolved

**Original:** `_apply_survivor_outcome` sourced `max_hp` from `prior_max_hp` (pre-battle snapshot), ignoring the live extractor's `cs.max_hp` in the outcome.

**Fix (d956783e2):** Lines 166-171 now read `cs.max_hp` from each outcome `ComponentStateSpec`:
```python
outcome_max_hp = float(cs.max_hp)
max_hp = (
    outcome_max_hp
    if outcome_max_hp > 0.0
    else prior_max_hp.get(key, 0.0)
)
```
The outcome's authoritative `max_hp` is used when positive. The pre-battle snapshot is retained only as a defensive fallback when the outcome reports `max_hp <= 0.0` (treated as "missing"). This preserves modifier-reshaped caps across the write-back boundary.

**Test coverage:** `test_apply_survivor_outcome_uses_outcome_max_hp_over_pre_battle` (line 383) verifies the prefer-outcome path with a `reshaped_max = pre_max + 25.0` scenario. `test_apply_survivor_outcome_falls_back_to_prior_max_hp_when_outcome_zero` (line 451) verifies the zero-fallback path. Both pass. All 9 tests in `test_post_battle_hook.py` pass.

**Verdict: Resolved.**

---

## Finding MAJ-001 (status) — Deferred, Sound Rationale

**Original:** `cs.status` (`ComponentStatus.name` string) from PROJ-354A's extractor is ignored at the bridge — `_apply_survivor_outcome` never reads it.

**Deferral rationale (from decisions.md lines 27-28):** "`ComponentState` is a damage-only DTO with no status field, and adding one is a save-format migration that the original PROJ-354A scope explicitly excluded."

**Verification of rationale:**

1. `ComponentState` (`game/core/component_state.py:53-70`) has fields: `component_id`, `instance_index`, `current_hp`, `max_hp`, `is_active`. No `status` field exists.
2. Adding `status` would require: new field on the dataclass, `to_dict()` serialization, `from_dict()` deserialization, and potentially a save-format version bump. This is a separate migration scope.
3. The engine reconciles `ComponentStatus` from HP/active state on the next battle's first tick — no correctness loss from dropping `status` at the bridge.
4. Replay-side fidelity (`ReplayRecord.outcome.data`) preserves `status` independently — PROJ-354B's verifier compares `record.outcome.data` to `battle_outcome_to_dict(replayed_outcome)`, neither of which involves `ShipInstance.components`. The bridge fix (max_hp propagation) does not affect replay verification (confirmed at decisions.md line 37-38).

**Verdict: Deferral rationale is sound.** No action required at this time.

---

## Finding MAJ-002 — Resolved

**Original:** Comment "ComponentStateSpec doesn't carry max_hp today" was stale after PROJ-354A added `max_hp` to `ComponentStateSpec`.

**Fix:** Old comment (previously at lines 141-146) removed. New docstring (lines 142-153) documents:
- The authoritative-from-outcome behavior for `max_hp` (preferring live extractor value)
- The zero-fallback guard (defensive against missing values)
- The intentional `status` drop with architectural justification

**Verification:** No occurrences of "doesn't carry" or "does not carry" in `post_battle_hook.py`. The new docstring is accurate and complete.

**Verdict: Resolved.**

---

## Finding MAJ-003 — Resolved

**Original:** `_apply_survivor_outcome` line 157 constructed `ComponentState(max_hp=prior_max_hp.get(key, 0.0))`, ignoring `cs.max_hp` from the outcome `ComponentStateSpec`.

**Fix:** Same root cause and code location as MAJ-001. The `max_hp` parameter at line 176 now passes `max_hp=max_hp` (the resolved variable that prefers outcome `cs.max_hp`), replacing the old `max_hp=prior_max_hp.get(key, 0.0)`.

**Verdict: Resolved** (same fix as MAJ-001).

---

## Regression Scan

**Negative — no regressions found.**

1. **Existing tests unchanged (7 pre-remediation tests):** All pass. The `_make_ship_outcome` fixture had already been updated during the initial PROJ-354A commit (cd8ebf5e5) to include `max_hp=100.0` and `status="ACTIVE"` on `ComponentStateSpec` constructors. Since the factory creates ships with `max_hp=100.0` by default, the new outcome-based `max_hp` resolves identically for existing test scenarios — no behavioral change.

2. **Other hook functions untouched:** `_apply_single_outcome`, `_remove_ship`, `_prune_empty_fleets` were not modified.

3. **Defensive guards present:** The `outcome_max_hp > 0.0` check protects against zero, NaN (NaN > 0.0 is False), and negative values — all fall back to the pre-battle snapshot.

4. **No new imports, no new dependencies, no API surface changes.**

5. **No compat shims introduced.** Logic is a clean rewrite of the max_hp sourcing, not a layered patch.

6. **Full sharded suite:** Commit message reports 17,768 tests passed (verified by committer, not re-executed here as it was already confirmed pre-review-submission).

---

## Summary

All three MAJ findings from the parent review (req_20260505_055832_23a2f0) are resolved. The `max_hp` propagation is correct with an appropriate defensive fallback. The `status` deferral is well-reasoned — `ComponentState` lacks a status field and adding one is a separate save-format migration. The stale comment is replaced with an accurate, comprehensive docstring. No regressions detected.
