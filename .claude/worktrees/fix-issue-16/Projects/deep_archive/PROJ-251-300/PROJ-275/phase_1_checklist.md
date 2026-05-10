# Phase 1: Audit Phase (Read-Only)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 1`
> 2. Only proceed if output shows PASSED

**Status:** Complete
**Objective:** Catalog every 2-team assumption in the codebase. Produce a comprehensive findings report before writing any code.

---

## Tasks

### Task 1.1: Grep for 2-team assumptions [Simple]
**File:** Multiple — read-only sweep
**Tests:** N/A

- [x] Run `grep -rn "_NUM_TEAMS" game/ tests/` — catalog all occurrences
- [x] Run `grep -rn "team_id == 0\|team_id == 1" game/` — catalog hardcoded checks
- [x] Run `grep -rn "team_modifiers\[0\]\|team_modifiers\[1\]" game/` — catalog indexed accesses
- [x] Run `grep -rn "side_0\|side_1" game/` — catalog Battle Setup state references
- [x] Run `grep -rn "fleet1.*fleet2\|fleet_1.*fleet_2" game/ tests/` — catalog 2-fleet signatures
- [x] Run `grep -rn "(_NUM_TEAMS - 1)\|(1 - owner)\|(1 - team)" game/` — catalog arithmetic 2-team tricks
- [x] Write findings to `findings/audit_2team_assumptions.md`

**Notes:** All greps executed. Full table in `findings/audit_2team_assumptions.md`. Key sites: `_NUM_TEAMS` + its usage in `battle_setup/spec_compiler.py` (7 sites in one file), `team_modifiers[0]/[1]` hardcode at `simulation_adapter.py:187-189`, `side_0/side_1` spread across `battle_setup_state.py` (7), `battle_setup_screen.py` (~10), `battle_setup/spec_compiler.py` (3), and `fleet1/fleet2` in `simulation_adapter.py` + `interfaces/battle_resolver.py`.

### Task 1.2: Classify findings — load-bearing vs. cosmetic [Medium]
**File:** `findings/audit_2team_assumptions.md`
**Tests:** N/A

- [x] For each occurrence tagged Load-bearing / Cosmetic / UI / Test-only
- [x] Produce a count summary table
- [x] For each load-bearing finding, note the blast radius

**Notes:** Summary table at top of findings doc. Load-bearing surfaces: `_NUM_TEAMS` + routing (Phase 3+4), `team_modifiers[0/1]` (Phase 7), `side_0/side_1` state+UI+compiler (Phase 4+5), `fleet1/fleet2` adapter+interface (Phase 7), sequential 2-fleet decomposition loop (Phase 7 — flagged critical). Cosmetic items: a `# today (_NUM_TEAMS = 2)` comment in tests and one log string. The `team_id == 0/1` pattern yielded zero in-scope hits — no hardcoded conditional branches on team 0 vs 1 in production. The `(1 - owner)` arithmetic trick appears only inside the same `_route_team_for_scope` function (Phase 3 touches it).

### Task 1.3: Audit Battle Setup UI layout [Complex]
**File:** `game/ui/screens/battle_setup/panels/`
**Tests:** N/A

- [x] List all files in `game/ui/screens/battle_setup/` — only `spec_compiler.py` + `__init__.py`; no `panels/` subdirectory
- [x] The UI layer is `game/ui/screens/battle_setup_screen.py` (single file); all "panels" are inline within the screen
- [x] Screen reads `state.side_0` / `state.side_1` in ~10 sites — mechanical migration in Phase 5
- [x] Overall layout: horizontally-stacked columns for the 2 sides
- [x] Proposed layout for N sides: keep columnar layout for 2-4 sides; flag 5+ sides as "functional only" per plan's out-of-scope decision
- [x] Flagged UI complexity — Phase 5 is the largest surface but mechanical

**Notes:** The project plan assumed a `panels/` subdirectory that doesn't exist. Consolidated UI lives in `battle_setup_screen.py` — simpler than expected. Phase 5's task list in `phase_5_checklist.md` references "for each panel" but the actual work is "for each `side_0`/`side_1` reference in the screen" (~10 sites). Findings logged in `audit_2team_assumptions.md` → "Battle Setup UI Complexity Estimate". Max-8-sides cap (per plan decisions) makes columnar layout feasible for all allowed counts.

### Task 1.4: Audit strategy conflict resolution flow [Medium]
**File:** `game/strategy/engine/conflict_resolution_engine.py`, `game/strategy/adapters/simulation_adapter.py`
**Tests:** N/A

- [x] Read `conflict_resolution_engine.py` end-to-end — path is `game/strategy/engine/` (plan said `turn_engine/` — minor path correction)
- [x] Identified the sequential 2-fleet decomposition: `_resolve_combat_at_hex` L215-256 — while-loop calling `_resolve_combat(f1, f2)` pairwise until one empire left
- [x] Inputs: `occupants: List[(Empire, Fleet)]`. Iteration: `self._rng.sample(emp_ids, 2)` picks 2 random empires. Output: side-effects on `fleets_by_emp`, `_combats_resolved`, `_fleets_destroyed`.
- [x] Determinism concern: order DOES depend on `self._rng.sample(...)` seeded at engine init; N-team replacement must either preserve seeding or accept that 3+-empire hexes get a different (deterministic) outcome
- [x] Documented `SimulationBattleResolver.resolve_battle`: signature `(fleet1, fleet2, *, seed, registries, environmental_effects, team0_modifiers, team1_modifiers)`. `team0_modifiers`/`team1_modifiers` come from `collect_combat_modifiers(f1, f2, ...)` / `collect_combat_modifiers(f2, f1, ...)` respectively.
- [x] Findings in `audit_2team_assumptions.md` (sections 2 and 4)

**Notes:** Delegated the standalone `audit_strategy_conflict_flow.md` content into the composite `audit_2team_assumptions.md` to keep findings in one place. Path correction for Phase 7: checklist will update module path from `game/strategy/turn_engine/conflict_resolution_engine.py` to `game/strategy/engine/conflict_resolution_engine.py`.

### Task 1.5: Audit apply_outcome_to_fleets [Simple]
**File:** `game/strategy/combat/post_battle_hook.py`
**Tests:** N/A

- [x] Read `apply_outcome_to_fleets` end-to-end
- [x] Identified: NO hardcoded 2-team assumptions
- [x] Confirmed: iterates `outcome.teams` and looks up fleets via `fleets_by_team_id.get(team.team_id, [])` — already N-team friendly
- [x] Findings added to `audit_2team_assumptions.md` section "apply_outcome_to_fleets Post-Battle Hook Check"

**Notes:** Significant positive finding — Phase 6 doesn't need to touch this file. The hook already takes `fleets_by_team_id: Mapping[int, List[Fleet]]` and iterates. Strategy compiler (Phase 6) just needs to build that mapping for N teams.

### Task 1.6: Audit report review [Simple]
**File:** `findings/audit_2team_assumptions.md` (composite)
**Tests:** N/A

- [x] Composed master summary (top of findings doc)
- [x] Counts: ~25 load-bearing production sites across 6 files; ~10 UI reads (battle_setup_screen.py); no test-only assumptions outside one comment
- [x] Proposed Phase 5 scope: mechanical migration of `state.side_0`/`side_1` references in `battle_setup_screen.py` + `battle_setup_state.py`; columnar UI layout preserved for 2-8 sides
- [x] No surprises or scope-renegotiation flags — findings match plan expectations

**Notes:** No scope renegotiation needed. Proceeding to Phase 2.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
- [x] Run `python Projects/scripts/validate_phase.py PROJ-275 1`

_User acknowledgment of audit findings: no scope renegotiation required — plan remains accurate. Deferred to project-level verification._
