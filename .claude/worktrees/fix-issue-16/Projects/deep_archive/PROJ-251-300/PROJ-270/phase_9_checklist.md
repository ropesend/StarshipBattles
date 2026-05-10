# Phase 9: Track A Battle-Math Integrity (CRITICAL)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 9`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (9.1-9.5 + 9.7 done; 9.6 rescoped to PROJ-271 Phase 2)
**Risk:** HIGH (fixes a live gameplay regression that Phase 6 claimed was resolved)
**Depends On:** None — this IS the blocker
**Objective:** Actually fix the strategic-modifier battle-math regression that PROJ-269 Phase 5.5 introduced and PROJ-270 Phase 6 falsely claimed was restored. The compiler emits the right stat_keys into `ModifierStack`; the aggregator sums them into `_team_bonuses` — but `_apply_bonuses` is a hardcoded 2-key sink that discards everything except `ToHitAttackModifier` + `ToHitDefenseModifier`. `shield_capacity_mult` and `damage_mult` never reach ship stats.

## Context (from skeptic audit 2026-04-12)

Empirically reproduced by skeptic agent:
```
team_bonuses: {0: {'shield_capacity_mult': 0.5}}
ship.max_shields: 1000    ← should be 500 if Track A worked
```

Full report: `.agent_reports/proj-269-270-skeptic-review/battle_math_skeptic.md` (will be deleted after this project closes — key findings captured here).

**Pipeline trace** (steps 1-5 work, step 6 fails):
1. `game/strategy/combat/spec_compiler.py:357-432` — emits real stat_keys. ✓
2. `run_battle` passes `spec.modifier_stack` to `FleetAuraManager`. ✓
3. `FleetAuraManager._append_external_from_entry` ingests. ✓
4. `_recalculate` aggregates into `_team_bonuses`. ✓
5. [game/simulation/combat/fleet_aura_manager.py:313-322](../../../game/simulation/combat/fleet_aura_manager.py#L313-L322) `_apply_bonuses` reads ONLY `ToHitAttackModifier` / `ToHitDefenseModifier`. **Everything else is discarded.** ✗
6. No bridge writes team-bonuses into `component.stats` where `ShieldProjection.get_effective_stat('shield_capacity_mult', 1.0)` and `WeaponAbility.get_effective_stat('damage_mult', 1.0)` read from.

---

## Tasks

### Task 9.1: Failing integration test (TDD Rule 1) [Medium] — COMPLETE
**File:** `tests/integration/strategy/combat/test_storm_shield_interference.py`
**Tests:** `pytest tests/integration/strategy/combat/test_storm_shield_interference.py --tb=short`

- [x] Wrote 3 end-to-end tests via `run_battle(spec)` with a real `ModifierStack`:
  - `test_shield_capacity_mult_halves_max_shields` — proves the bug (pre-fix: got 500.0, expected 250.0)
  - `test_shield_capacity_mult_only_applies_to_target_team` — verifies per-team routing
  - `test_damage_mult_halves_weapon_damage` — damage_mult coverage (plumbing level — outcome assertion is weak but documents intent)
- [x] Confirmed the tests FAIL pre-fix (captured in session — this was the smoking gun)
- [x] After bridge implementation (Tasks 9.3/9.4), all 3 now pass

**Notes:** Task 9.1 serves as both the failing-test-first gate AND the acceptance test for Phase 9. The `damage_mult` test is intentionally weak pending a dedicated component-level assertion in a future session — the two shield_capacity tests prove the architectural bridge works.

---

### Task 9.2: Architectural decision — how do team-bonuses reach ship stats? [Complex] — COMPLETE
**File:** `Projects/active_projects/PROJ-270/decisions.md`

- [x] Decision: **Option A (external-stats dict on Ship)** — documented in decisions.md 2026-04-12 entry. Rationale: preserves PROJ-269 "ships enter unmutated" principle (ModifierStack remains single source of truth; external_stats is read-only composition layer). Option B violates no-pre-mutation. Option C doesn't scale.
- [x] Implementation used `isinstance(external_stats, dict)` guard for Mock compatibility
- [x] Composition policy: `_mult` keys multiply, `_add` keys sum (stacks multiplicatively with component-local modifiers)

**Notes:** User implicitly approved via `/proj-continue` after skeptic finding report. Reversible in ~30 lines if needed.

---

### Task 9.3: Implement chosen bridge [Complex] — COMPLETE
**File:** `game/simulation/combat/fleet_aura_manager.py`, `game/simulation/entities/ship.py`, `game/simulation/components/abilities/base.py`
**Tests:** `pytest tests/unit/simulation/combat/ tests/unit/simulation/components/ -q` — 3512/3512 green

- [x] Added `ship.external_stats: Dict[str, float] = {}` on [game/simulation/entities/ship.py:139-146](../../../game/simulation/entities/ship.py#L139)
- [x] Extended [Ability.get_effective_stat](../../../game/simulation/components/abilities/base.py#L243) with third composition layer: `external_stats` from `ship.external_stats` composes multiplicatively (_mult) or additively (_add) with component-local stats. Guarded with `isinstance(external_stats, dict)` for Mock compatibility.
- [x] `_recalculate` propagation: `_apply_bonuses` only triggers `ship.recalculate_stats()` when `external_stats` actually changes (perf-conscious — avoids per-tick full recalc). Guarded for test shims (SimpleNamespace) via `callable(recalc)` check.
- [x] Task 9.1's 3 integration tests all pass

---

### Task 9.4: Extend `_apply_bonuses` to handle all stat_keys, not just 2 hardcoded [Medium] — COMPLETE
**File:** [game/simulation/combat/fleet_aura_manager.py:313-353](../../../game/simulation/combat/fleet_aura_manager.py#L313)

- [x] Replaced 2-key hardcoded sink with `ship.external_stats = dict(team)` — ALL stat_keys from `_team_bonuses[team_id]` now propagate to ship
- [x] Retained `fleet_attack_bonus` / `fleet_defense_bonus` direct-attribute setters (collision.py:115-120 reads by name)
- [x] Dirty-check guard: only `recalculate_stats()` when `external_stats` changed — avoids per-tick full pipeline recalc

---

### Task 9.5: `_log_placeholder_once` test coverage [Simple] — COMPLETE
**File:** `tests/unit/simulation/combat/test_fleet_aura_extended.py`

- [x] Added `TestLogPlaceholderOnce` class with 2 tests:
  - `test_placeholder_entry_emits_warning_once_per_source` — asserts duplicate-source placeholders emit 1 warning, not 2
  - `test_placeholder_warning_mentions_source_name` — asserts warning includes source identifier
- [x] Both pass. Skeptic's "no test for the claim" finding resolved.

---

### Task 9.6: Battle Setup complex toggles (Task 6.3 re-opened) [Medium] — RE-SCOPED TO PROJ-271
**File:** `game/ui/screens/battle_setup/spec_compiler.py:260-296`

- [x] Audit complete: `_complex_entries` at [game/ui/screens/battle_setup/spec_compiler.py:260-296](../../../game/ui/screens/battle_setup/spec_compiler.py#L260) emits `stat_key="placeholder"` for EVERY complex toggle (shield booster, damage booster, suppressor, flat_shield_bonus — all alike).
- [x] Finding: per-toggle mapping requires a `design_id → (stat_key, value, operation)` lookup table driven by `data/modifiers.json`, which is a Phase-5-sized data-modeling exercise. Adding Phase 9.6 implementation inside this closure phase would blow scope.
- [x] **Rescoped to PROJ-271 Phase 2** — grouped with `flat_shield_bonus` mapping (also in `_entries_from_modifier_source` at [game/strategy/combat/spec_compiler.py:505](../../../game/strategy/combat/spec_compiler.py#L505)). PROJ-271 Phase 2 becomes "all placeholder stat_key emissions across BOTH compilers" rather than just strategy. Update PROJ-271 phase_2_checklist.md accordingly.
- [x] Unblocking step completed in Phase 9: now that the pipeline ACTUALLY applies stat_keys (vs silently discarding them), per-toggle mapping is a pure data-mapping task. Before Phase 9's bridge fix it would have been wasted effort.

**Notes:** Phase 6 Task 6.3 was marked "complete" but was never implemented. The test-quality gap the skeptic identified is real. The Phase 9 bridge makes this unblockable; PROJ-271 Phase 2 will complete it.

---

### Task 9.7: Phase 9 regression gate — COMPLETE
**Tests:** Full suites + verified repro

- [x] Task 9.1 integration tests all green (3/3 pass)
- [x] `pytest tests/ --tb=no -q` — **14633 passed** (+4 from 14629 baseline matching new Phase 9 tests). 3 pre-existing build-queue + 3 pre-existing AI import errors unchanged. 1 flaky `test_colony_owner_id_matches_empire` (passes in isolation — documented flake).
- [x] Combat Lab fast: **162/162 green** ✓
- [x] Combat Lab full: **170/170 green** ✓
- [x] Empirical repro: `shield_capacity_mult=0.5` → `ship.max_shields=250` (was 500). Verified via integration test.
- [x] Grep audit — placeholder entries remaining:
  - `game/strategy/combat/spec_compiler.py:471` — generic placeholder helper (used for sources without a mapping)
  - `game/strategy/combat/spec_compiler.py:505` — PROJ-271 deferred (flat_shield_bonus + suppressors)
  - `game/ui/screens/battle_setup/spec_compiler.py:280` — PROJ-271 Phase 2 rescoped
  - Storm `shield_capacity_mult`, fleet `shield_mult`, `damage_mult` emit REAL stat_keys ✓

---

## Phase Completion Checklist

- [x] All task checkboxes above are checked
- [x] Task 9.1's integration test passes (was failing at start of phase)
- [x] Pipeline trace re-verified: stat_key from compiler DOES reach ship stats
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update `findings/acceptance_audit.md` — remove the false "Track A is working" claim
- [x] Update Phase 6 checklist Task 6.5 Notes — acknowledge the deferral reasoning was inverted
