# Phase 3: Documentation + Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-257 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update architecture documentation to reflect the changes made in Phases 1-2. Run final verification to ensure all layer violations are resolved and no regressions exist.

---

## Tasks

### Task 3.1: Update `docs/01_ARCHITECTURE.md` - Core package table [Simple]
**File:** `docs/01_ARCHITECTURE.md`
**Tests:** N/A (documentation)

- [ ] Add `combat_types.py` to the `game/core/` module table (after `config.py`):
  `| combat_types.py | DamageContext frozen dataclass (attacker identity DTO) |`
- [ ] Add `formula_evaluator.py` to the `game/core/` module table (after `event_logging.py`):
  `| formula_evaluator.py | FormulaEvaluator, FormulaContext, AST-based formula evaluation |`
- [ ] Update the `game/core` Public API section to add:
  - `FormulaEvaluator`, `FormulaContext` under a new **Formula Evaluation** heading
  - `DamageContext` under a new **Combat Types** heading
- [ ] Verify the Forbidden Dependencies table still accurate: "Engine must not import Simulation, Strategy, AI, or UI" -- this was violated before and is now fixed

**Notes:**

---

### Task 3.2: Update `docs/01_ARCHITECTURE.md` - Engine package description [Simple]
**File:** `docs/01_ARCHITECTURE.md`
**Tests:** N/A (documentation)

- [ ] Update the `game/engine/` module table entry for `physics.py`:
  Change description to: `PhysicsBody base class (position, velocity, rotation, forward_vector). Property container -- subclasses implement their own physics update.`
- [ ] Add a note under the Engine section explaining:
  - PhysicsBody is a property container, not a physics simulator
  - Ship uses ShipPhysicsMixin for arcade-style physics
  - Projectile uses direct velocity integration

**Notes:**

---

### Task 3.3: Update `docs/01_ARCHITECTURE.md` - Simulation package description [Simple]
**File:** `docs/01_ARCHITECTURE.md`
**Tests:** N/A (documentation)

- [ ] In the `game/simulation/` root modules table, update `FormulaSystem` entry:
  Change to: `FormulaSystem (re-export shim -- canonical location: game.core.formula_evaluator)`
- [ ] Verify the combat_events entry still lists CombatEvent, CombatEventBus, etc. (DamageContext removed from here, lives in core)

**Notes:**

---

### Task 3.4: Update `docs/02_PATTERNS.md` if needed [Simple]
**File:** `docs/02_PATTERNS.md`
**Tests:** N/A (documentation)

- [ ] Check if any pattern references `game.simulation.formula_system` -- if so, update to `game.core.formula_evaluator`
- [ ] Check if any pattern references `DamageContext` import from simulation -- if so, update to core
- [ ] If no references exist, no changes needed (check the box and note "no changes needed")

**Notes:**

---

### Task 3.5: Final grep verification - layer violations [Simple]
**Tests:** Manual verification

- [ ] `grep -rn "from game\.simulation" game/engine/` -- must return zero results (Engine imports no Simulation code)
- [ ] `grep -rn "import game\.simulation" game/engine/` -- must return zero results
- [ ] `grep -rn "eval(" game/core/formula_evaluator.py` -- must return zero results (no eval() in formula evaluation)
- [ ] `grep -rn "from game\.simulation\.formula_system import" game/simulation/ game/strategy/` -- must return zero results in production code
- [ ] `grep -rn "from game\.simulation\.combat\.combat_events import DamageContext" game/engine/` -- must return zero results
- [ ] Verify `from game.core.combat_types import DamageContext` works in Python REPL
- [ ] Verify `from game.core.formula_evaluator import FormulaEvaluator` works in Python REPL
- [ ] Verify backward compat: `from game.simulation.formula_system import FormulaEvaluator` works in Python REPL
- [ ] Verify backward compat: `from game.simulation.combat.combat_events import DamageContext` works in Python REPL

**Notes:**

---

### Task 3.6: Full test suite run [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the full sharded test suite: `python Tools/test_sharded/test_sharded.py`
- [ ] Verify all tests pass (baseline: 14783 tests, 0 skipped)
- [ ] If any failures, investigate and fix
- [ ] Record final test count in notes below

**Notes:**

---

### Task 3.7: Run simulation test suite [Simple]
**Tests:** `python -m combat_lab.run_tests --fast`

- [ ] Run Combat Lab simulation tests: `python -m combat_lab.run_tests --fast`
- [ ] Verify all tests pass
- [ ] Record result in notes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `docs/01_ARCHITECTURE.md` accurately reflects new file locations
- [ ] All grep verifications pass (no layer violations)
- [ ] Full test suite passes (14783+ tests)
- [ ] Simulation tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete, ready for audit
