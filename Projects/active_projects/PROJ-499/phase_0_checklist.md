# Phase 0: Pre-flight survey + baseline-drift census

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-499 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Confirm scope assumptions before committing to the bulk re-baseline. Specifically: prove (not infer) how many of the 65 baselines are stale, and confirm no other harnesses share the gap.

---

## Tasks

### Task 0.1: Confirm baseline-drift scope [Simple]
**File:** `tests/regression/snapshots/*.json`
**Tests:** none (read-only census)

Walk every JSON in `tests/regression/snapshots/` and capture a full structural census (not just `component.stats`). Audit F4 from the mid-project-review consult (`AgentCoordination/Scratchpad/Consult/20260523T131241Z_audit-PROJ-499/response.md:19`) flagged that a stats-only census would miss top-level, `component`-subkey, and ability-level drift; the expanded scope below catches all four.

- [x] For each baseline, record: (a) top-level key set, (b) `component` subkey set, (c) `component.stats` key set, (d) `abilities` length and class-name sequence, (e) per-ability emitted key set (keyed by ability `class_name`).
- [x] Compare (c) against live `StatKey` enum values in `game/simulation/components/abilities/stat_keys.py:24-70`.
- [x] Compare (a), (b), (d), (e) across baselines — if there's MORE than one variant of any of them across the 65 files, that's drift the harness has been hiding.
- [x] Record per-baseline census in `findings/source_review.md` as a table.
- [x] Verify: at minimum, every unchanged baseline (i.e. anything other than the 7 PROJ-489 reshots) is missing `launch_rate_mult`, `recovery_rate_mult`, `bay_capacity_mult`, `shield_bonus_add` from `component.stats`.
- [x] If ANY baseline shows drift beyond those four `stats` keys (e.g. top-level shape variant, new ability-class key not in `snapshot_ability_stats()` projection), escalate — Phase 3 needs a wider spot-check, and the contract phrasing in decisions.md may need updating.

Codex's read-only census on 2026-05-23 reported exactly two `component.stats` variants (7-with vs. 58-without the four new keys), one top-level shape, one `component` subshape, and one ability-key-set variant per ability class. Phase 0 re-verifies this from a clean read at execution time.

**Notes:**
- Census driver: `c:/tmp/proj499_census.py` (one-shot read-only, not committed).
- Verified count: **65 baselines, 58 stale (missing the 4 new StatKeys), 7 fresh** — exactly the Codex prediction.
- Stats key-set variants: 2 (25-key stale, 29-key fresh; delta is exactly `launch_rate_mult, recovery_rate_mult, bay_capacity_mult, shield_bonus_add`).
- Top-level: 1 variant (`{abilities, component}`); component subkey: 1 variant (10 keys); ability class-name sequences: 7 variants (one per component family — capital_missile/laser_cannon/railgun/crew_quarters_automation/generator_efficiency/standard_engine/thruster).
- Per-ability key sets: 1 variant per ability class. No within-class drift.
- No baseline references `mini_capital_missile` (re-verified via grep; PROJ-497 retype data edit is invisible to Phase 3 re-shoot).
- No baseline depends on the deleted `efficient_engines` modifier (all engine baselines use `standard_engine_no_modifiers` or `standard_engine_size_N`).
- See `findings/source_review.md` §3 for full census tables.

### Task 0.2: Confirm no other harness shares the gap [Simple]
**File:** repo-wide
**Tests:** none (read-only survey)

- [x] Re-verify Codex's harness survey (response.md:13-15) by independently grepping for snapshot-comparison patterns: `json.load`, `compare_snapshots`, golden-fixture compare patterns.
- [x] Confirm `tests/infrastructure/deep_compare.py:77-106` unions key sets (symmetric).
- [x] Confirm `tests/integration/strategy/test_save_round_trip.py:222-231`, `test_galaxy_reproducibility.py:40-45`, `test_ship_stats_golden.py:261-275,315-325`, `test_golden_fixture_field_coverage.py:65-86` use strict equality.
- [x] Record results in `findings/harness_survey.md`.
- [x] If a NEW asymmetric comparator is found, STOP and escalate — Phase 5 would need to widen its scope or a sibling project may be needed.

**Notes:**
- `Grep compare_snapshots|deep_compare`: 8 files. New file `test_allowance_matrix.py` (PROJ-498) is a boolean pair-allowance harness, NOT a snapshot comparator. Documented in harness_survey.md.
- `tests/infrastructure/deep_compare.py:87` confirmed symmetric: `set(expected.keys()) | set(actual.keys())`.
- No new asymmetric comparator found. Perf benches at `tests/performance/bench_*.py` use numeric-ratio thresholds, not dict walks. `galaxy_repro_baseline.py` only loads JSON; comparison happens in the (already-strict) reproducibility tests.
- harness_survey.md updated with the four post-planning additions (PROJ-498 allowance matrix + two perf benches + galaxy_repro_baseline).

### Task 0.3: Capture baseline sharded-suite green state [Simple]
**File:** none
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Record the current working-tree state (`git status --short`) before running. Do NOT revert unrelated dirty state per AGENTS.md — work around it. Audit F4 (consult response.md:19) softened this from "clean main" because the consult request itself was made with ambient `AgentCoordination/generated/*` dirt.
- [x] Run full sharded suite. Confirm GREEN.
- [x] Record pass count + the captured `git status --short` snapshot in plan.md "Last Action" line — this is the pre-change baseline. If any tests fail in a way related to the modifier-snapshot harness or `compare_snapshots()`, STOP and triage before continuing. Unrelated pre-existing failures are noted but not blocking.

**Notes:**
- Pre-existing dirty state (NOT reverted): PROJ-497/498 plan + checklist edits, data/modifiers.json + data/components.json (PROJ-497 deletions/retypes), modifier_service.py + modifier_save_restore.py (new PROJ-498 production), test_allowance_matrix.py (PROJ-498 test), several docs (modifier_system.md, adding_modifiers.md, etc.), three AgentCoordination/generated/* test-baseline files (advisory only), discovered_issues/log.jsonl.
- Sharded suite GREEN: **26870 tests | 26869 passed | 0 failed | 0 errors | 1 skipped** in 153.6s across 12 shards.
- No modifier-snapshot harness failure. Baseline locked.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `findings/source_review.md` and `findings/harness_survey.md` written
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 1
