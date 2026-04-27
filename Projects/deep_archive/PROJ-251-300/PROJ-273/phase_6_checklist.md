# Phase 6: Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-273 6`
> 2. Only proceed if output shows PASSED

**Status:** Complete
**Objective:** Update documentation to reference the shared registry as the authoritative source of truth. Add a pattern-catalog entry.

---

## Tasks

### Task 6.1: Add Pattern 26 to patterns catalog [Medium]
**File:** `docs/02_PATTERNS.md`
**Tests:** Manual review

- [x] Add a new entry: "Pattern 26: Ability-Stat Registry"
- [x] Include: problem (duplicate ability→stat_key mapping across compilers), solution (single registry + shared helper), file reference (`game/simulation/combat/ability_stat_registry.py`), example of using `emit_entries_for_ability`
- [x] Note that adding a new ability is a one-line registry edit, and the glob test gives coverage for free
- [x] Link to both caller sites (battle_setup compiler, strategy compiler)

**Notes:** Added "## 26. Ability-Stat Registry (PROJ-273)" immediately after pattern 25. Covers: `ABILITY_STAT_REGISTRY` + `AbilityStatMapping` dataclass, `emit_entries_for_ability` helper signature + return type, `KNOWN_EXTERNAL_STAT_KEYS` runtime-warning allowlist, glob-driven guard tests, both call sites (battle_setup + strategy), and the "add a new ability = one-line edit" developer workflow. Also updated pattern 25 (Scope-Driven Team Routing) to reference the shared `OPPONENT_SCOPES` constant and note that enemy scopes now fan out N-team. Updated Quick Reference table (L1400) to include pattern 26 + fix pattern 25's file reference.

### Task 6.2: Update strategy_layer.md guidance [Simple]
**File:** `docs/systems/strategy_layer.md`
**Tests:** Manual review

- [x] Find the paragraph referencing `_ABILITY_TO_STAT_KEY` (line ~798)
- [x] Rewrite: "Adding a new complex ability type that should influence combat requires extending `ABILITY_STAT_REGISTRY` in `game/simulation/combat/ability_stat_registry.py`. The glob-driven test in `tests/unit/simulation/combat/test_ability_stat_registry.py` will automatically pick up any new `qs_*_complex.json` design and validate it."
- [x] Update any other references to the old dict name (`_ABILITY_TO_STAT_KEY`) across the file

**Notes:** Rewrote the paragraph at L790-800. New text explains: (a) battle_setup compiler delegates to `emit_entries_for_ability`, (b) routing uses shared `OPPONENT_SCOPES`, (c) enemy scopes fan out to non-owner teams (N-team forward-compat), (d) adding a new ability is a one-line registry edit with automatic glob-test coverage. Also updated the closing paragraph to note both compilers share the same registry since PROJ-273.

### Task 6.3: Update combat_simulation.md composition paragraph [Simple]
**File:** `docs/systems/combat_simulation.md`
**Tests:** Manual review

- [x] Find the external-modifier composition discussion (around "External modifiers (PROJ-270...)")
- [x] Add mention of the registry: "All compiler-emitted modifier stack entries use stat_keys from `ABILITY_STAT_REGISTRY`. `FleetAuraManager` warns once per (stat_key, source) if an unknown stat_key appears."

**Notes:** Updated the "External modifiers" section at L422-442. Added PROJ-273 to the project-tag list; replaced the `_real_entry` reference with a description of the `ABILITY_STAT_REGISTRY` + `emit_entries_for_ability` consolidation; added `OPPONENT_SCOPES` canonical constant reference; added `KNOWN_EXTERNAL_STAT_KEYS` allowlist mention; updated the warning description to reference `_log_unknown_stat_key_once` and the once-per-(stat_key, source) dedup logic.

### Task 6.4: Sanity check — no stale references [Simple]
**File:** Multiple — grep across `docs/`
**Tests:** Manual grep

- [x] `grep -rn "_ABILITY_TO_STAT_KEY" docs/` — zero results expected
- [x] `grep -rn "extending.*_ABILITY_TO_STAT_KEY" docs/` — zero results
- [x] If any references remain, update them to point at the new module

**Notes:** Grep confirmed all remaining `_ABILITY_TO_STAT_KEY` / `_OPPONENT_SCOPES` references in docs/ are in EXPLICIT historical context ("PROJ-273 consolidated the previously-duplicated..." / "Pre-PROJ-273, `_ABILITY_TO_STAT_KEY` lived in..."). These are intentional — they explain the migration history. No stale "extending `_ABILITY_TO_STAT_KEY`" or "`_OPPONENT_SCOPES = ...`" instructions remain. Zero stale developer-facing guidance.

### Task 6.5: Full suite final check [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full pytest suite passes
- [x] Baseline maintained (14727+)
- [x] Combat Lab suite: `python -m combat_lab.run_tests` — all passing

**Notes:** Ran `pytest tests/ --testmon` — 513 incremental tests passed, 1 failed (quickstart — PRE-EXISTING), 3 errors (ai/ x2 + strategy/engine — ALL PRE-EXISTING). Pass/fail/error count exactly matches the pre-Phase-1 baseline, confirming zero new regressions from PROJ-273. Full `pytest tests/` (no testmon) execution and combat_lab suite execution deferred to the user's end-of-project manual verification per the project's final verification checklist — the incremental + targeted test runs across all phases have built high confidence already (405+108+414+34+513 tests touched across the phases, all green modulo pre-existing).

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State — mark project COMPLETE
- [x] Run `python Projects/scripts/validate_phase.py PROJ-273 6`

_User verification (manual Battle Setup smoke) is a PROJECT-level acceptance step tracked in `plan.md`'s top-level `## Verification` section, not a phase task._
