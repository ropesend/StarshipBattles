# Phase 0: Pre-flight survey + baseline-drift census

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-499 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Confirm scope assumptions before committing to the bulk re-baseline. Specifically: prove (not infer) how many of the 65 baselines are stale, and confirm no other harnesses share the gap.

---

## Tasks

### Task 0.1: Confirm baseline-drift scope [Simple]
**File:** `tests/regression/snapshots/*.json`
**Tests:** none (read-only census)

Walk every JSON in `tests/regression/snapshots/` and capture a full structural census (not just `component.stats`). Audit F4 from the mid-project-review consult (`AgentCoordination/Scratchpad/Consult/20260523T131241Z_audit-PROJ-499/response.md:19`) flagged that a stats-only census would miss top-level, `component`-subkey, and ability-level drift; the expanded scope below catches all four.

- [ ] For each baseline, record: (a) top-level key set, (b) `component` subkey set, (c) `component.stats` key set, (d) `abilities` length and class-name sequence, (e) per-ability emitted key set (keyed by ability `class_name`).
- [ ] Compare (c) against live `StatKey` enum values in `game/simulation/components/abilities/stat_keys.py:24-70`.
- [ ] Compare (a), (b), (d), (e) across baselines — if there's MORE than one variant of any of them across the 65 files, that's drift the harness has been hiding.
- [ ] Record per-baseline census in `findings/source_review.md` as a table.
- [ ] Verify: at minimum, every unchanged baseline (i.e. anything other than the 7 PROJ-489 reshots) is missing `launch_rate_mult`, `recovery_rate_mult`, `bay_capacity_mult`, `shield_bonus_add` from `component.stats`.
- [ ] If ANY baseline shows drift beyond those four `stats` keys (e.g. top-level shape variant, new ability-class key not in `snapshot_ability_stats()` projection), escalate — Phase 3 needs a wider spot-check, and the contract phrasing in decisions.md may need updating.

Codex's read-only census on 2026-05-23 reported exactly two `component.stats` variants (7-with vs. 58-without the four new keys), one top-level shape, one `component` subshape, and one ability-key-set variant per ability class. Phase 0 re-verifies this from a clean read at execution time.

**Notes:** [Filled during execution]

### Task 0.2: Confirm no other harness shares the gap [Simple]
**File:** repo-wide
**Tests:** none (read-only survey)

- [ ] Re-verify Codex's harness survey (response.md:13-15) by independently grepping for snapshot-comparison patterns: `json.load`, `compare_snapshots`, golden-fixture compare patterns.
- [ ] Confirm `tests/infrastructure/deep_compare.py:77-106` unions key sets (symmetric).
- [ ] Confirm `tests/integration/strategy/test_save_round_trip.py:222-231`, `test_galaxy_reproducibility.py:40-45`, `test_ship_stats_golden.py:261-275,315-325`, `test_golden_fixture_field_coverage.py:65-86` use strict equality.
- [ ] Record results in `findings/harness_survey.md`.
- [ ] If a NEW asymmetric comparator is found, STOP and escalate — Phase 5 would need to widen its scope or a sibling project may be needed.

**Notes:** [Filled during execution]

### Task 0.3: Capture baseline sharded-suite green state [Simple]
**File:** none
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Record the current working-tree state (`git status --short`) before running. Do NOT revert unrelated dirty state per AGENTS.md — work around it. Audit F4 (consult response.md:19) softened this from "clean main" because the consult request itself was made with ambient `AgentCoordination/generated/*` dirt.
- [ ] Run full sharded suite. Confirm GREEN.
- [ ] Record pass count + the captured `git status --short` snapshot in plan.md "Last Action" line — this is the pre-change baseline. If any tests fail in a way related to the modifier-snapshot harness or `compare_snapshots()`, STOP and triage before continuing. Unrelated pre-existing failures are noted but not blocking.

**Notes:** [Filled during execution]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `findings/source_review.md` and `findings/harness_survey.md` written
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 1
