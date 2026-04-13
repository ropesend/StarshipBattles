# Unified Entry/Exit + Visual Mode — Round 2 Verification

## Verdict

**Scope-trims mostly defensible, with 2 material gaps that warrant new PROJ-270 phases.** The Phase 9 bridge, Phase 10 routing migration, and Phase 11 guard-tightening are real and verifiable: all 3 production visual call sites now route through `start_from_spec` → `start_engine_from_spec`, which in turn calls `engine.start_teams()` → `FleetAuraManager.initialize(modifier_stack=...)`. Track A battle-math therefore works in visual mode too (same code path). The 3 integration tests are green; 26 guard tests are green. However, two items currently marked "deferred" are neither PROJ-271 scope nor cosmetic follow-ups — they should become Phase 13 / Phase 14 of PROJ-270 before archival.

## Findings

### Finding 1: Contributor-facing Combat Lab how-to section still teaches the deleted API
**Severity:** High
**Applies to:** PROJ-270 new phase
**Location:** `combat_lab/COMBAT_LAB_DOCUMENTATION.md:668-700` (§8 "Creating New Tests" Step 4 "Write Test Scenario Class")
**What's wrong:** Phase 11.9 updated the base-class section (line 283) to show the current `to_spec/wire_ships/custom_setup/validate(outcome, telemetry)` API and added a top banner. But §8 — the step-by-step how-to a new contributor follows when creating a test — still shows `def setup(self, battle_engine):`, `battle_engine.start([attacker], [target], seed=...)`, and `def validate(self, engine) -> list`. A contributor doing what the top banner redirects them to do ("see §1 for architecture") but then following the numbered steps in §8 will write legacy code that would fail `TestNoLegacyScenarioSetup` (AST). Phase 11 banner is in §1; §8 Step-4 example is authoritative to a skim-reader.
**Evidence:** `grep -n "def setup\|def update\|def validate(self, engine)"` → 3 hits at lines 668/686/689 + live call `battle_engine.start([self.attacker], [self.target], seed=self.metadata.seed)` at line 676. `docs/guides/simulation_testing.md:185-195` shows the exact same legacy block; 707 lines of body content after a 17-line banner makes the banner cosmetic.
**Recommended fix (new PROJ-270 Phase 13, Task 13.1):** Rewrite §8 Step-4 and `simulation_testing.md` §~185 code blocks to use `to_spec()/wire_ships()/custom_setup()/validate(outcome, telemetry)`. Delete legacy examples rather than retaining them "for historical reference" (CLAUDE.md System Migration Policy: eradicate). Update `check_exact('Damage', ..., actual=weapon.damage)` surrounding example to read from outcome/telemetry.

### Finding 2: `_build_fallback_outcome` synthesizes false `seed`, `end_reason`, telemetry
**Severity:** Medium-High
**Applies to:** PROJ-270 new phase
**Location:** `game/ui/screens/battle_screen.py:582-588`
**What's wrong:** Hardcodes `seed=0`, `end_reason=EndReason.TEAM_ELIMINATED`, `telemetry_level=TelemetryLevel.NORMAL` with empty `stats=zero_stats`/`hits_taken=()`. None of these reflect reality. Today no test asserts on these fields (verified via grep `end_reason|_build_fallback_outcome|get_outcome` on `tests/unit/ui/test_battle_screen*.py` → no hits), so the synthesizer doesn't actively hide bugs — but: (a) `telemetry_level=NORMAL` is a LIE because no aggregator ran, so downstream consumers reading `outcome.telemetry_level` and expecting populated `stats`/`hits_taken` will silently get zeros; (b) if any future test or UI feature asserts `outcome.seed == controller.config.seed`, it'll false-pass at seed=0. The "scope-trim" is documented as "deferred until 71 callers migrated," but the synthesizer itself is a Rule-3 violation independent of the caller migration.
**Evidence:** `battle_screen.py:582-588` hardcoded fields; `_on_battle_ended` calls `extract_battle_results(outcome, ...)` which only reads display fields today — but `BattleResultsScreen` already reads `outcome.end_reason` and `outcome.seed` (trace through `extract_battle_results`). The trimming leaves a ticking DoS against the outcome contract's truthfulness.
**Recommended fix (new PROJ-270 Phase 13, Task 13.2):** Change fallback synthesizer to report `telemetry_level=TelemetryLevel.MINIMAL` (the level that matches "empty aggregator data") and derive `end_reason` from `engine.end_condition` via the existing `_END_REASON_BY_CLASS` map in battle_runner.py. Pull `seed` from `engine.rng` / `controller.config.seed` if available, else use `None` (ShipOutcome.seed is Optional). Small diff, removes 3 lies.

### Finding 3: AIPolicy + TaskForceOutcome are genuinely dead — YAGNI
**Severity:** Low (cosmetic correctness) / High (as Rule-3 violation signal)
**Applies to:** PROJ-270 new phase (consolidated scaffolding-purge)
**Location:** `game/simulation/battle_spec.py:67-79` (AIPolicy — `pass` body); `game/simulation/battle_outcome.py` (TaskForceOutcome)
**What's wrong:** Confirmed: `grep "ai_policy\." game/` returns ZERO production attribute accesses. `grep "fleet_hierarchy\.[a-zA-Z_]" game/` returns ZERO attribute reads of `TaskForceOutcome`. Both are constructed-but-never-read. Phase 12 deferred with rationale "43/51 call sites is session-sized" — but (a) 43/51 refs are mostly tests, (b) the fixes are mechanical (delete `ai_policy=AIPolicy()` + field + class), (c) sunset-date marker on `FORBIDDEN_FIELDS` doesn't apply here. CLAUDE.md Rule 3 prohibits "maintaining parallel systems that do the same thing" — AIPolicy is worse: a zero-body dataclass that costs lines of code everywhere and delivers nothing.
**Evidence:** 4 construction sites, 0 attribute reads. `TaskForceOutcome(task_force_id=task_force.task_force_id)` on `battle_runner.py:323` — compare to `fleet_hierarchy=tuple(task_force_outcomes)` on line 341 — the object shape flows through extract_outcome but nothing reads fields off it.
**Recommended fix (new PROJ-270 Phase 13, Task 13.3):** Bite the bullet — delete `AIPolicy` class, `ai_policy` field on `TeamSpec`, `ai_policy=AIPolicy()` at all 4 call sites. Delete `TaskForceOutcome` class, `fleet_hierarchy` field on `TeamOutcome`, the `task_force_outcomes` loop in `battle_runner.py:320-323`, `fleet_hierarchy=tuple(...)` on line 341. Single session; 43+51 refs are 90% tests that can migrate via a 15-minute mechanical sweep. Keeping dead types "for future work" is exactly what Rule 3 calls out.

### Finding 4: Skeptic-report preservation hygiene not handled
**Severity:** Low
**Applies to:** Archive checklist
**Location:** `.agent_reports/proj-269-270-skeptic-review/` vs. `Projects/active_projects/PROJ-270/findings/`
**What's wrong:** 4 skeptic reports live only at `.agent_reports/proj-269-270-skeptic-review/{unified_entry_exit,battle_math,test_docs,clean_sheet}_skeptic.md`. `.agent_reports/` is ephemeral per CLAUDE.md Subagent Reports policy ("contents are disposable"). `PROJ-270/findings/` has only `acceptance_audit.md` — the source findings that drove Phases 9-12 are unlinked.
**Evidence:** `ls findings/` → just `acceptance_audit.md`. Archival wipes the reasoning trail unless copied.
**Recommended fix:** Either copy the 4 reports into `PROJ-270/findings/` before archival, or explicitly cite the verification doc as authoritative and note in `plan.md` that the skeptic reports were consumed and summarized. Trivial task.

### Finding 5: `_run_single_tick` raise-path is reachable under legacy `.start()` — dead code check
**Severity:** Low (verified reachable only via unconfigured screens — not a bug, just noise)
**Applies to:** Acceptable deferral
**Location:** `game/ui/screens/battle_screen.py:411-417`
**What's wrong:** Phase 10 replaced `self.engine.update()` with `raise StateException(...)` when `self._controller is None`. Reality check: `BattleScreen.start(team0, team1)` on line 227 builds a controller internally (line 256) and calls `self.start_battle(controller)` (line 261) — so production and all tests following that path set `self._controller`. The raise-path can only fire if someone instantiates BattleScreen and calls `_run_single_tick` without any start. That's effectively impossible in production or tests. The raise is fine as a safety net; nothing to fix.

### Finding 6: Track A verified working via visual path
**Severity:** None (positive verification)
**Applies to:** Confirmation of existing claim
**Location:** `game/simulation/battle_controller.py:306-308` → `battle_runner.py:157-162` → `battle_engine.py:344`
**What's wrong:** Nothing. Trace: `BattleController.start_from_spec` calls `start_engine_from_spec(spec, ...)` which calls `engine.start_teams(...)` which calls `self.aura_manager.initialize(self.ships, modifier_stack=self.modifier_stack)`. `spec.boundary` and `spec.modifier_stack` are threaded into the engine BEFORE `start_teams` (lines 150-152 of battle_runner.py). Phase 9 bridge (`_apply_bonuses` → `external_stats` → `get_effective_stat`) operates off the ship's live state, not the spec — so it runs identically in visual and headless. Phase 9 integration test (`test_shield_capacity_mult_halves_max_shields`) uses `run_battle`, but the entire aura pipeline is shared. Visual mode inherits the fix transitively.

### Finding 7: `BattleService.adopt_started_engine` is a proper service method, not a hack
**Severity:** None (positive verification)
**Applies to:** Confirmation
**Location:** `game/simulation/services/battle_service.py:220-241`
**What's wrong:** Nothing material. It does populate `_engine`, `_team0_ships`, `_team1_ships`, `_is_started`, `_seed` consistently. `tick_counter` on the adopted engine is whatever `start_teams` left it at (0) — consistent with a just-started engine. The only minor oddity: `BattleService.start_battle` re-calls `self._engine.start(team0, team1, seed=...)` — so the service has two entry paths (`create_battle + start_battle` OR `adopt_started_engine`). Worth a docstring cross-reference but not a bug.

## Summary Table

| Item | Status | Resolution |
|------|--------|------------|
| Phase 9 Track A bridge (visual) | Works | Verified via code trace + green Phase 9 integration tests |
| 3 production call sites migrated to start_from_spec | Works | app.py:585, test_lab/screen.py:450, test_execution_service.py:92 all call `controller.start_from_spec(...)` |
| Hand-rolled `engine.boundary=`/`engine.modifier_stack=` plumbing | Eliminated | Only `start_engine_from_spec` (runner) and `start` (engine) own this |
| `self.engine.update()` bypass | Gone | Raise-path replaces else-branch; guard `TestNoDirectEngineTickLoop` is green |
| `BattleScreen.start(team0, team1)` shim + `_build_fallback_outcome` | Deferred (71 test callers) | **Tighten synthesis** per Finding 2 (Phase 13) before accepting deferral |
| Combat Lab / sim_testing doc how-to drift | Partial | Banner exists; Step-4 how-to body still shows legacy API (Finding 1 / Phase 13) |
| AIPolicy + TaskForceOutcome YAGNI | Deferred | **Should be Phase 14** not follow-up (Finding 3) |
| Skeptic report preservation | Not handled | Copy to findings/ before archival (Finding 4) |
| PROJ-269 completeness | Independent | Still carries own manual-smoke + archive TODO; Phase 9 didn't change its state |

## Recommended New PROJ-270 Phases

**Phase 13: Visual-mode outcome truthfulness + doc honesty**
- 13.1 Rewrite `COMBAT_LAB_DOCUMENTATION.md` §8 "Creating New Tests" Step 4 and `docs/guides/simulation_testing.md` lines ~185-200 to use `to_spec/wire_ships/custom_setup/validate(outcome, telemetry)` — delete legacy snippets rather than retaining as "historical".
- 13.2 Fix `_build_fallback_outcome` synthesizer: `telemetry_level=MINIMAL`, `end_reason` derived from `engine.end_condition`, `seed=config.seed` — stop lying.

**Phase 14: Eradicate AIPolicy + TaskForceOutcome scaffolding**
- 14.1 Delete `AIPolicy` class + `ai_policy` field on `TeamSpec` + 4 construction sites + all test references.
- 14.2 Delete `TaskForceOutcome` + `fleet_hierarchy` field on `TeamOutcome` + `battle_runner.py:320-323,341` + all test references.

**Archive checklist additions:**
- Copy `.agent_reports/proj-269-270-skeptic-review/*.md` to `Projects/active_projects/PROJ-270/findings/` before running protocol 05.

## Baseline Verified

- `tests/unit/simulation/test_unified_entry_guard.py` + `tests/unit/simulation/battle_controller/test_outcome_emission.py` → 26 passed
- `tests/integration/strategy/combat/test_storm_shield_interference.py` → 3 passed

Archival is close but not ready. Phase 13 (~1 session) + Phase 14 (~1 session) remain — both are genuinely PROJ-270 scope (unified entry/exit contract + clean-sheet per CLAUDE.md Rule 3), not PROJ-271.
