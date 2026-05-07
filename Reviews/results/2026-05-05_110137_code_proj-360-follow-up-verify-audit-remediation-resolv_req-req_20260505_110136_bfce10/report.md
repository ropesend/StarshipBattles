# Review Report: PROJ-360 Follow-up — Verify Audit Remediation Resolved Findings

**Review Type:** code (follow-up verification)
**Request ID:** req_20260505_110136_bfce10
**Parent Request:** req_20260505_073251_b48e74
**Scope:** `game/simulation/entities/stat_contributors/registry.py`, `defense.py`, `weapons.py`, `game/simulation/entities/ship_stats.py`, `tests/unit/simulation/entities/test_ship_stats_golden.py` + snapshot, `conftest.py`, `Projects/active_projects/PROJ-360/decisions.md`
**Review Mode:** follow-up (per-finding pass/fail verification, no full re-review)
**Limitations:** None. All scope files read in full. Relevant tests executed (35 passed / 0 failed).
**Date:** 2026-05-05

---

## Verification Matrix

| Parent Finding | Status | Evidence |
|---|---|---|
| EXT-01 (CRIT) | **resolved** | `STAT_CONTRIBUTOR_REGISTRY` is now `Dict[str, StatContributorEntry]` (`registry.py:195`). `register_stat_contributor` raises on duplicate ability name regardless of `domain` tag (`registry.py:214-219`). Dedup key is per-ability, not per-domain. Old permissive test deleted. |
| EXT-12 (CRIT) | **resolved** | `apply_registered_contributors` receives `(ship, comp, acc)` (`registry.py:252`). Call site in `ship_stats.py:270` passes the same `acc` dict built-ins mutate. `test_registered_contributor_receives_acc_dict` pins the contract: contributor sees a real `dict` with built-in keys (`thrust`, `max_shields`). |
| EXT-02 (MAJ) | **resolved** | `BUILTIN_HANDLED_ABILITIES` frozenset (`registry.py:156-169`) enumerates 9 built-in abilities. `is_builtin_suppressed_for()` queries both the frozenset and registry dict (`registry.py:238-249`). All four built-in domain handlers consult it: `movement.py:46,51,56,65`, `defense.py:57,67`, `command.py:56`, `launch.py:40`. `test_registering_shield_projection_does_not_double_count` pin: registers a 7x contributor, asserts `max_shields == 7 × baseline` (not 8×). `TestBuiltinSuppression` (4 tests, `test_registry.py:135-171`) covers the API at unit scope. |
| EXT-05 (MAJ) | **resolved** | Shield energy cost extraction now uses `comp.get_abilities("ResourceConsumption")` filtered on `resource_type == "energy"` (`defense.py:77-80`). Legacy "first match wins" + `has_ability("ShieldRegeneration")` gate preserved. `test_shield_energy_cost_filters_by_resource_type` (`test_defense.py:156`) added. |
| FM-01 (MAJ) | **resolved** | `aggregate_targeting_scores` annotated `-> float` (`weapons.py:36`). `float(ecm_score)` cast on return (`weapons.py:56`). |
| A1 (MAJ) | **resolved** | Root `conftest.py` imports and calls `reset_stat_contributor_registry()` pre-test (`conftest.py:47`) and post-test in the `finally` block (`conftest.py:123`). `reset_stat_contributor_registry` helper (`registry.py:272-280`) does `STAT_CONTRIBUTOR_REGISTRY.clear()`. |
| C1 (MAJ) | **resolved** | `STAT_CONTRIBUTOR_REGISTRY` is `Dict[str, StatContributorEntry]` (`registry.py:195`). Registration, lookup, and suppression queries are O(1). |
| FIND-002 (MAJ) | **resolved** | All 12 combat-endurance fields (`fuel_consumption`, `ammo_consumption`, `energy_consumption`, `potential_fuel_consumption`, `potential_ammo_consumption`, `potential_energy_consumption`, `fuel_endurance`, `ammo_endurance`, `energy_endurance`, `energy_recharge`, `energy_net`, `cached_summary`) captured by `_capture_stats` (`test_ship_stats_golden.py:172-183`). `float('inf')` normalized to `"inf"` sentinel via `_normalize_infinity`. Snapshot regenerated; all 7 designs pass verified by grep (84 matches across 7 designs). |
| EXT-07 (MAJ) | **deferred** (sound) | Five abilities (`Armor`, `MultiplexTracking`, `VehicleLaunch`, `VehicleStorage`, `PodStorage`) bypass typed `get_abilities()` because they lack typed `Ability` subclasses. Creating them is a multi-touch refactor across `data/components.json`, the ability registry, and consumers. The EXT-02 suppression hook works by ability name, not class instance — it functions regardless. Deferring as a standalone Project is architecturally correct; the cost/benefit isn't justified for an audit pass. |
| EXT-11 (MAJ) | **deferred** (sound) | Two-tier model (built-in + registered) is intentional. The EXT-02 fix lets a registered contributor fully replace a built-in handler without code edits — the practical extension story is delivered. Merging built-ins into `STAT_CONTRIBUTOR_REGISTRY` itself would require reworking `_phase_stats_aggregation`'s call order guarantees (some contributors mutate `acc`, others mutate `ship` directly across two phases). The current separation is deliberate and sound. |

---

## Regression Check

No regressions found. Specific verification:

- **Test suite:** 35 targeted tests pass (golden snapshot × 7 designs + 2 entry-check tests + 5 extension tests + 10 registry tests + 11 defense tests).
- **Built-in correctness:** `is_builtin_suppressed_for` returns `False` when no contributor is registered → all built-ins fire exactly as before. The `AND` logic (`ability in BUILTIN_HANDLED_ABILITIES AND ability in STAT_CONTRIBUTOR_REGISTRY`) prevents false suppression.
- **Golden snapshot:** All 7 designs pass `test_ship_stats_match_golden` — the combat-endurance fields were added without disturbing existing fields.
- **Conftest reset:** `reset_stat_contributor_registry()` in both pre-test and post-test paths is purely additive — no existing fixture behavior altered.
- **Shield energy cost path:** `get_abilities("ResourceConsumption")` replaces `ability_instances` scan under the same `has_ability("ShieldRegeneration")` gate — "first match wins" semantics preserved.

---

## Derivation Report: Critical Regression Test

`test_registering_shield_projection_does_not_double_count` (`test_stat_contributor_extension.py:172-246`) correctly pins the EXT-01+EXT-02 contract:

1. **Baseline pass:** `baseline_ship.recalculate_stats()` → `baseline_max_shields` computed by built-in defense handler alone.
2. **Registration pass:** A 7× multiplier contributor is registered. `replaced_ship.recalculate_stats()` suppresses the built-in and runs only the registered contributor.
3. **Assertion 1:** Contributor was actually invoked (`assert invocations`).
4. **Assertion 2:** `replaced_ship.max_shields == baseline_max_shields * 7` (not `* 8`). Uses `math.isclose(rel_tol=1e-9)`.

This directly validates both halves: hook fires AND built-in is suppressed. Without the EXT-02 fix, shields would be 8× baseline.

---

## Summary

| Severity | Count |
|----------|-------|
| CRIT — resolved | 2 |
| MAJ — resolved | 7 |
| MAJ — deferred (rationale sound) | 2 |
| Regressions | 0 |

All 9 findings the request asked to verify are either resolved (7) or deferred with sound rationale (2). No regressions introduced by commit `79e79d9e5`.
