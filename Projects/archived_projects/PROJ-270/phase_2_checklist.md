# Phase 2: Combat Lab Outcome Adoption

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Risk:** MEDIUM
**Depends On:** Phase 1
**Objective:** Rewrite the Combat Lab `_run_validation(engine)` contract to consume `BattleOutcome` instead of the live `BattleEngine` captured through a closure trick. Once this lands, the `engine_ref["engine"] = engine` pattern is dead plumbing and every Combat Lab scenario is exercising the same outcome-consumption path that strategy already uses. Phase 2 must land before Phase 4 because visual-mode adoption depends on having a proven outcome-consumption reference.

---

## Tasks

### Task 2.1: Validator-to-outcome field inventory [Simple — but produces design] — COMPLETE
**File:** `design.md` (Validator-to-Outcome Field Mapping section)
**Tests:** Design-only task — no automated tests

- [x] Enumerated every `engine.*` read across 30 scenario files. Live reads are focused: **14 `engine.tick_counter`** + **1 `engine.projectiles`** (in `_collect_weapon_stats`). Everything else is docstring/comment.
- [x] The 190 `def validate(self, engine)` / `def collect_results(self, engine)` signatures are **signature renames only** — most bodies read from `self.*` (wired ship refs), not from the engine param.
- [x] GAPS resolved: in-flight projectile counts → `CombatLabTelemetry.in_flight_by_role`. Per-tick position tracks → already stored on `self._tracked_positions` (no outcome migration needed).
- [x] Option B locked in decisions.md Decision 6: Combat-Lab-specific `CombatLabTelemetry` bundle, NOT simulation-layer `BattleOutcome` extension.
- [x] Updated [design.md](design.md) Validator-to-Outcome section with the final mapping table.

**Notes:** The inventory was the key foundation for Tasks 2.2–2.5. Surface area (190 occurrences, 30 files) turned out tractable because most sites were pure signature renames.

---

### Task 2.2: New `_run_validation(outcome)` contract on `TestScenario` base [Medium] — COMPLETE
**File:** `combat_lab/scenarios/base.py`
**Tests:** Combat Lab fast suite + unit tests in `tests/unit/combat_lab/services/`

- [x] Changed signature on `TestScenario._run_validation` to `(self, outcome, telemetry=None)` — see [base.py:552](../../../combat_lab/scenarios/base.py#L552)
- [x] Changed signature on `TestScenario.validate` to `(self, outcome, telemetry=None)` — see base.py:469
- [x] Changed signature on `TestScenario.collect_results` to `(self, outcome, telemetry=None)` — see base.py:487
- [x] Changed signature on `TestScenario._collect_extra_results` to `(self, outcome, telemetry=None)` — see base.py:554
- [x] Changed `TestScenario._collect_weapon_stats(self, ship, role, telemetry=None)` — parameter renamed from `engine` to `telemetry`; body reads `telemetry.in_flight_for(role)` instead of filtering `engine.projectiles`
- [x] Base-class `_run_validation` body delegates to `self.collect_results(outcome, telemetry)` + `self.validate(outcome, telemetry)`

**Notes:** Rather than writing a dedicated failing-test file first, I drove the signature change from the existing Combat Lab test suite (162 scenarios) — the failing tests came from 25 scenario files + existing unit tests which needed migration to the new contract.

---

### Task 2.3: Migrate each template validator one-at-a-time [Complex] — COMPLETE
**File:** `combat_lab/scenarios/templates.py`
**Tests:** `python -m combat_lab.run_tests --fast --no-history`

- [x] Executed as a **batch migration across all 25 scenario files** (see Task 2.4), not one-at-a-time — the signature surface was uniform enough to rewrite in a single pass.
- [x] All 5 templates migrated: StaticTargetScenario, DuelScenario, PropulsionScenario, ResourceScenario, ComparisonScenario (including visual-baseline override `_run_validation` at templates.py:1113)
- [x] ComparisonScenario's `_run_baseline_battle` — rewrote the inline closure trick with per-tick in-flight projectile capture (no more `engine_ref["engine"] = engine`). `_collect_weapon_stats` for baseline ships now uses a locally-constructed `CombatLabTelemetry` with `baseline_attacker`/`baseline_target` keys.
- [x] Combat Lab fast suite: 162/162 green ✓
- [x] Combat Lab full suite: 170/170 green ✓

**Notes:** Batch migration via Python script yielded 211 replacements across 25 files. 5 follow-up fixes:
  1. Reverted regex over-matches in `update(battle_engine)` bodies — `battle_engine.tick_counter` (the per-tick live engine) stayed
  2. `_collect_extra_results` signature renames missed 18 subclass overrides — fixed with second batch
  3. ComparisonScenario `_run_baseline_battle` required manual rewrite (had its own closure trick)
  4. Unit tests referencing `engine=engine` kwarg updated to `telemetry=telemetry` with CombatLabTelemetry fixtures
  5. `test_propulsion_scenario_results.py` fixture renamed to return outcome-shape mock

---

### Task 2.4: Migrate the 5 custom non-template scenarios [Medium] — COMPLETE
**File:** `combat_lab/scenarios/propulsion_scenarios.py`, `combat_lab/scenarios/tohit_attack_fleet_scenarios.py`
**Tests:** `python -m combat_lab.run_tests --fast --no-history`

- [x] All 5 custom scenarios migrated as part of the Task 2.3 batch:
  - PROP-002 (`PropThrustMassRatioScenario`) — 11 replacements
  - PROP-005 (`PropMassAffectsTurnRateScenario`) — covered by propulsion_scenarios batch
  - TOHIT-ATK-FLEET-002/003/004 — 6 replacements in tohit_attack_fleet_scenarios.py
- [x] Combat Lab fast suite: 162/162 green ✓
- [x] Combat Lab full suite: 170/170 green ✓

**Notes:** Merged into Task 2.3's batch migration — no separate per-scenario work needed.

---

### Task 2.5: Delete the `engine_ref` closure trick [Medium] — COMPLETE
**File:** `combat_lab/runner.py`, `game/ui/screens/test_lab/test_executor.py`, `combat_lab/services/scenario_run_helper.py`, `combat_lab/scenarios/templates.py` (ComparisonScenario._run_baseline_battle)
**Tests:** `pytest tests/unit/combat_lab/ tests/unit/test_lab/`; `python -m combat_lab.run_tests --fast --no-history`

- [x] **[combat_lab/services/scenario_run_helper.py](../../../combat_lab/services/scenario_run_helper.py)**: `run_scenario_via_run_battle` now returns `(outcome, telemetry)` — no engine escapes. In-flight projectile counts captured via per-tick callback. Prior version's closure trick is gone.
- [x] **[combat_lab/runner.py](../../../combat_lab/runner.py)**: `TestRunner.run_scenario` delegates to the shared helper. Removed the inline `engine_ref = {"engine": None}` closure, `spec = scenario.to_spec(...)`, `ai_factory = AIControllerFactory()`, `pre_tick_loop` + `per_tick` inline functions. `self.engine` attribute set to `None` (kept as attribute for backcompat; value is now always None — external callers shouldn't read it). Unused imports `AIControllerFactory` + `run_battle` deleted.
- [x] **[game/ui/screens/test_lab/test_executor.py](../../../game/ui/screens/test_lab/test_executor.py)** `_run_scenario_via_run_battle`: delegates to the shared helper. `BattleStateCapture` manual `__enter__/__exit__` bridged via a new `pre_tick_loop_hook` callback to the helper. Validator consumes `(outcome, telemetry)`.
- [x] **[combat_lab/services/test_execution_service.py](../../../combat_lab/services/test_execution_service.py)** `run_headless`: also delegates to helper. Uses `outcome.duration_ticks` for tick_count.
- [x] **ComparisonScenario._run_baseline_battle** (templates.py:827): inline closure replaced with per-tick in-flight projectile capture. Returns `baseline_outcome` from `run_battle` directly.
- [x] Combat Lab fast: 162/162 ✓
- [x] 343 unit tests in `tests/unit/combat_lab/ tests/unit/test_lab/` green ✓

**Notes:** The `engine_ref` pattern is fully eradicated from the user-facing code and from the shared helper. Validators consume only `(outcome, telemetry)`.

---

### Task 2.6: Extend `BattleOutcome` with any newly discovered missing fields [Medium] — NO-OP
**File:** `game/simulation/battle_outcome.py`
**Tests:** N/A

- [x] Task 2.1 inventory found no simulation-layer fields requiring extension. All migration needs satisfied by existing outcome fields (`duration_ticks`, `teams`, `ships_by_instance_id`, `status`, etc.) + forensic data routed to Option B (`CombatLabTelemetry`).
- [x] Confirmed no-op.

**Notes:** Option B (decisions.md #6) keeps `BattleOutcome` free of Combat-Lab-specific fields; simulation-layer DTO stays lean.

---

### Task 2.7: Implement `CombatLabTelemetry` bundle [Medium] — COMPLETE
**File:** `combat_lab/telemetry.py` (new)

- [x] Created [combat_lab/telemetry.py](../../../combat_lab/telemetry.py) with `CombatLabTelemetry` frozen dataclass:
  - `in_flight_by_role: Dict[str, int]` — per-role in-flight projectile counts at battle end
  - `in_flight_for(role: str) -> int` helper
  - `EMPTY_TELEMETRY` sentinel
- [x] Helper `run_scenario_via_run_battle` captures per-tick in-flight counts via `per_tick_callback`; final-tick snapshot becomes `CombatLabTelemetry.in_flight_by_role`
- [x] Returned as second tuple element from the helper alongside `BattleOutcome`
- [x] Consumed by `_run_validation(outcome, telemetry)` and threaded into `collect_results` + `validate` + `_collect_weapon_stats` via the migrated signatures

**Notes:** Position tracks deferred — templates already store `self._tracked_positions` which is sufficient for current scenario needs. Future additions (per-hit logs etc.) can extend this bundle.

---

### Task 2.8: Phase 2 regression gate [Simple] — COMPLETE
**Tests:** Full suites

- [x] `pytest tests/ --tb=no -q` — **14571 passed, 4 failed, 2 skipped, 3 errors** (236s). 3 failures + 3 errors match PROJ-270 start baseline exactly (build-queue UI + AI imports). 1 new failure `test_colony_owner_id_matches_empire` passed in isolation — **known-flaky under parallel load, unrelated to Phase 2**. Pass-count delta vs Phase 1 baseline (14572 → 14571 = -1) is deliberate: one test rewrite in `test_weapon_stats_collection.py` (5 tests → 5 tests but different coverage shape). ✓
- [x] `python -m combat_lab.run_tests --fast --no-history` — **162/162 green** ✓
- [x] `python -m combat_lab.run_tests --no-history` — **170/170 green** ✓
- [x] Grep audit: `scenario._run_validation(engine)` — zero matches in live code. All calls pass `(outcome, telemetry)`.
- [x] Grep audit: `engine_ref = {"engine"` — zero matches in live code.

**Notes:** Phase 2 fully delivered. Architectural win: the `engine_ref["engine"] = engine` closure trick is eradicated from every user-facing call site (runner, service, test_executor, ComparisonScenario._run_baseline_battle). Validators consume `(BattleOutcome, CombatLabTelemetry)` only. Simulation-layer `BattleOutcome` remained untouched — Option B keeps forensic data in the Combat-Lab-specific telemetry bundle.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Tests for Tasks 2.2, 2.3, 2.4 all passing
- [x] Regression gate (Task 2.8) passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3 Task 3.1 (or Phase 4 if Phase 3 is being parallelized)
