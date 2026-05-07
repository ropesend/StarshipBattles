# Phase 6: Combat Lab fallback + docs + lint

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-354B 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire Combat Lab fallback builder; lint verifier dependency direction; update docs.

See `plan.md` Phase 6 for full task details.

---

## Tasks

### Task 6.1: Combat Lab fallback wiring [Medium]
**File:** `game/strategy/services/replay_verification_coordinator.py`
**Tests:** `tests/integration/replay/test_combat_lab_verification.py` (NEW)

- [ ] In `_verify_one`, pass `fallback_builder=self._fallback_ship_builder` to `build_replay_ship_builder`
- [ ] Composition root passes `combat_lab.design_loader.load_combat_lab_design` as the fallback
- [ ] DO NOT silent-fall-back to global registry lookup
- [ ] Test: Combat Lab record (synthetic, `instance_snapshot=None`) → coordinator runs with fallback → passes
- [ ] Test: no fallback wired AND no snapshots → ERROR sidecar with specific message
- [ ] Verify: both tests pass

**Notes:**

### Task 6.2: Verifier dependency direction lint [Simple]
**File:** `tests/unit/simulation/replay/test_replay_verifier_imports.py` (NEW)

- [ ] AST parse `replay_verifier.py`; assert no imports from `game.strategy.*`, `game.ui.*`, `game.ai.*`
- [ ] Verify: passes

**Notes:**

### Task 6.3: Update `docs/systems/combat_simulation.md` [Medium]
**File:** `docs/systems/combat_simulation.md` § 11

- [ ] Add "Background Verification" subsection: post-persist trigger, sidecar schema/path, settings, materialization requirements, no-recursion guarantee
- [ ] Update `> **Last verified:**` blockquote
- [ ] Verify: doc matches implementation

**Notes:**

### Task 6.4: Update `docs/systems/strategy_layer.md` [Medium]
**File:** `docs/systems/strategy_layer.md`

- [ ] In Replay Persistence section, add: sidecar schema/lifecycle, `add_on_record_persisted_listener` API, `verification_status` field on `ReplayLookup`
- [ ] Update `> **Last verified:**` blockquote
- [ ] Verify: doc matches implementation

**Notes:**

### Task 6.5: Update `docs/01_ARCHITECTURE.md` [Simple]
**File:** `docs/01_ARCHITECTURE.md`

- [ ] In Strategy services table (around line 175), add `ReplayVerificationCoordinator` row
- [ ] Update `> **Last verified:**` blockquote
- [ ] Verify: table reflects new service

**Notes:**

### Task 6.6: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite; compare to baseline + PROJ-354A new tests + PROJ-354B new tests
- [ ] Acceptance: all tests pass; zero regressions
- [ ] Verify: investigate any failures

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete and ready for verification
