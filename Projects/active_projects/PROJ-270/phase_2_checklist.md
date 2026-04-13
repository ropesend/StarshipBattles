# Phase 2: Combat Lab Outcome Adoption

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Risk:** MEDIUM
**Depends On:** Phase 1
**Objective:** Rewrite the Combat Lab `_run_validation(engine)` contract to consume `BattleOutcome` instead of the live `BattleEngine` captured through a closure trick. Once this lands, the `engine_ref["engine"] = engine` pattern is dead plumbing and every Combat Lab scenario is exercising the same outcome-consumption path that strategy already uses. Phase 2 must land before Phase 4 because visual-mode adoption depends on having a proven outcome-consumption reference.

---

## Tasks

### Task 2.1: Validator-to-outcome field inventory [Simple — but produces design]
**File:** `design.md` (append to "Validator-to-Outcome Field Mapping" section)
**Tests:** Design-only task — no automated tests

- [ ] Enumerate every `engine.*` read in the 162 Combat Lab scenarios. Start with the 5 templates:
  - StaticTargetScenario validators — grep `self.attacker.` and `self.target.` reads
  - DuelScenario validators
  - PropulsionScenario validators
  - ResourceScenario validators
  - ComparisonScenario validators (both baseline and variant paths)
- [ ] Enumerate `engine.*` reads in the 5 custom non-template scenarios (PROP-002, PROP-005, TOHIT-ATK-FLEET-002/003/004)
- [ ] For each read, determine the corresponding `BattleOutcome` / `ShipOutcome` / `WeaponSummary` / `ShipStats` field
- [ ] Identify GAPS — engine fields with no existing outcome equivalent (known: in-flight projectile counts; per-tick position tracks)
- [ ] Document gaps + chosen resolution in [design.md](design.md) Validator-to-Outcome section. Decision already locked: Option B — Combat-Lab-specific `CombatLabTelemetry` bundle, NOT extension of simulation-layer `BattleOutcome`
- [ ] Update [design.md](design.md) with the final mapping table

**Notes:** [Filled during implementation — the mapping IS the deliverable for this task]

---

### Task 2.2: New `_run_validation(outcome)` contract on `TestScenario` base [Medium]
**File:** `combat_lab/scenarios/base.py`
**Tests:** `pytest tests/unit/combat_lab/test_outcome_validation.py --tb=short`

- [ ] Write failing test in [tests/unit/combat_lab/test_outcome_validation.py](../../../tests/unit/combat_lab/test_outcome_validation.py) (new file) asserting:
  - `TestScenario._run_validation` accepts a `BattleOutcome` parameter (and optionally a `CombatLabTelemetry` bundle)
  - When given a passing outcome, the validator returns `report.passed = True`
  - When given a failing outcome, the validator returns `report.passed = False`
- [ ] Run test — confirm it fails (signature is still `_run_validation(engine)`)
- [ ] Change signature on `TestScenario._run_validation` in [combat_lab/scenarios/base.py](../../../combat_lab/scenarios/base.py):
  ```python
  def _run_validation(self, outcome: BattleOutcome, telemetry: Optional[CombatLabTelemetry] = None) -> ValidationReport:
  ```
- [ ] Update base-class default implementation to delegate to `validate(outcome, telemetry)` (new signature) on the subclass
- [ ] Run test — confirm it passes
- [ ] Leave template subclasses broken temporarily (Task 2.3 fixes them one by one)

**Notes:** [Filled during implementation]

---

### Task 2.3: Migrate each template validator one-at-a-time [Complex]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** Per-template: `python -m combat_lab.run_tests --fast --no-history` (asserts the N scenarios using that template still pass)

Migrate templates in this order (simplest first):

- [ ] **StaticTargetScenario** (line 1406): rewrite `_run_validation` to consume outcome. Verify the ~40 scenarios using StaticTargetScenario still pass
- [ ] **DuelScenario**: rewrite `_run_validation`. Verify duel scenarios still pass
- [ ] **PropulsionScenario**: rewrite `_run_validation`. Note: some PROP scenarios rely on per-tick position tracks — use the `CombatLabTelemetry` bundle from Task 2.1. Verify PROP scenarios pass
- [ ] **ResourceScenario**: rewrite `_run_validation`. Uses `ShipOutcome.components` + resource readouts. Verify RESOURCE scenarios pass
- [ ] **ComparisonScenario**: rewrite both baseline + variant validators. Most complex because it runs two battles. Verify comparison scenarios pass

After each template migration: run `python -m combat_lab.run_tests --fast --no-history` — must stay 162/162 green before proceeding to the next template.

**Notes:** [Filled during implementation]

---

### Task 2.4: Migrate the 5 custom non-template scenarios [Medium]
**File:** `combat_lab/scenarios/propulsion_scenarios.py`, `combat_lab/scenarios/tohit_attack_fleet_scenarios.py`
**Tests:** `python -m combat_lab.run_tests --fast --no-history`

- [ ] PROP-002 — rewrite its custom `validate()` to consume outcome
- [ ] PROP-005 — rewrite its custom `validate()` to consume outcome
- [ ] TOHIT-ATK-FLEET-002 — rewrite
- [ ] TOHIT-ATK-FLEET-003 — rewrite
- [ ] TOHIT-ATK-FLEET-004 — rewrite
- [ ] Verify: `python -m combat_lab.run_tests --fast --no-history` 162/162 green
- [ ] Verify: `python -m combat_lab.run_tests --no-history` 170/170 green

**Notes:** [Filled during implementation]

---

### Task 2.5: Delete the `engine_ref` closure trick [Medium]
**File:** `combat_lab/runner.py`, `game/ui/screens/test_lab/test_executor.py`, `combat_lab/services/scenario_run_helper.py` (created in Task 1.1)
**Tests:** `pytest tests/unit/combat_lab/ tests/unit/test_lab/ --tb=short`; `python -m combat_lab.run_tests --fast --no-history`

- [ ] In [combat_lab/runner.py](../../../combat_lab/runner.py):
  - Delete `engine_ref = {"engine": None}` (line 175)
  - Delete `engine_ref["engine"] = engine` writes in `pre_tick_loop` (line 178) and `per_tick` (line 190)
  - Delete `engine = engine_ref["engine"]` read (line 217)
  - Change `scenario._run_validation(engine)` (line 228) to `scenario._run_validation(outcome, telemetry)` where telemetry is the Task 2.1 bundle
  - Keep `self.engine = engine` exposed? Audit — if no external caller reads `runner.engine`, delete the attribute
- [ ] In [game/ui/screens/test_lab/test_executor.py](../../../game/ui/screens/test_lab/test_executor.py):
  - Delete the `engine_ref` closure (lines 271, 274, 303)
  - Change `scenario._run_validation(engine)` (line 313) to outcome-consuming form
  - `BattleStateCapture` manual `__enter__/__exit__` pattern: audit whether it needs the engine or can be driven from outcome
- [ ] Same cleanup in the shared helper created in Task 1.1
- [ ] Run all affected test suites — green
- [ ] Run `python -m combat_lab.run_tests --fast --no-history` — 162/162

**Notes:** [Filled during implementation]

---

### Task 2.6: Extend `BattleOutcome` with any newly discovered missing fields [Medium]
**File:** `game/simulation/battle_outcome.py`
**Tests:** `pytest tests/unit/simulation/test_battle_outcome.py --tb=short`

- [ ] Only do this task if Task 2.1's inventory identified missing fields that belong on the simulation-layer DTO (NOT forensic Combat-Lab data — that's Option B / separate bundle)
- [ ] For each justified new field:
  - Write failing test asserting the field exists and is populated by `extract_outcome`
  - Add the field as a frozen dataclass attribute
  - Populate it in `extract_outcome` ([game/simulation/battle_runner.py:276](../../../game/simulation/battle_runner.py#L276))
  - Run test — passes
- [ ] If no simulation-layer fields need extension, this task is a no-op — document in Notes

**Notes:** [Filled during implementation — expected to be a no-op given Option B decision]

---

### Task 2.7: Implement `CombatLabTelemetry` bundle (if needed) [Medium]
**File:** `combat_lab/telemetry.py` (new file, if needed)
**Tests:** `pytest tests/unit/combat_lab/test_combat_lab_telemetry.py --tb=short`

- [ ] If Task 2.1 identified Combat-Lab-specific forensic data (in-flight projectiles, position tracks):
  - Write failing tests asserting the bundle is produced during the run and passed to the validator
  - Create `combat_lab/telemetry.py` with a `CombatLabTelemetry` dataclass
  - Populate it from per-tick callbacks in `runner.py` and the shared helper
  - Pass to `_run_validation` as second argument
- [ ] If not needed, document in Notes

**Notes:** [Filled during implementation]

---

### Task 2.8: Phase 2 regression gate [Simple]
**Tests:** Full suites

- [ ] `pytest tests/ --tb=no -q` — ≥ baseline
- [ ] `python -m combat_lab.run_tests --fast --no-history` — 162/162 green
- [ ] `python -m combat_lab.run_tests --no-history` — 170/170 green
- [ ] Grep audit confirms `scenario._run_validation(engine)` does not appear in live code (all calls now pass outcome)
- [ ] Grep audit confirms `engine_ref = {"engine"` does not appear in live code

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Tests for Tasks 2.2, 2.3, 2.4 all passing
- [ ] Regression gate (Task 2.8) passed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3 Task 3.1 (or Phase 4 if Phase 3 is being parallelized)
