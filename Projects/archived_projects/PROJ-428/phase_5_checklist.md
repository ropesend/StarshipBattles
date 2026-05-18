# Phase 5: Validate and document

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-428 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_4
**Review Mode:** standard
**Files (planned):**
- `docs/systems/strategy_layer.md` (only if hook placement / registry ownership is described there)

**Objective:** Run the targeted regression gate, then the full sharded
suite, then update documentation only where it describes the prior hook
placement.

---

## Tasks

### Task 6.1: Focused regression gate [Simple]
**Tests:**

```bash
pytest tests/unit/strategy/turn_engine/ -x
pytest tests/unit/strategy/engine/test_turn_engine_config.py tests/unit/strategy/engine/test_no_lazy_fallback_init.py -x
pytest tests/integration/test_fms_b_e2e.py tests/integration/test_fms_b_statistical_balance.py -x
```

- [ ] All three focused commands are green.
- [ ] Record commit SHA and any tolerance-band observations.

**Notes:**

### Task 6.2: Full sharded suite [Complex]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite is green.
- [ ] If any flake recurs, capture stdout/stderr in `findings/` and treat
      the flake as a separate ticket (do not silently retry-until-green).

**Notes:**

### Task 6.3: Documentation update [Simple]
**File:** `docs/systems/strategy_layer.md`

- [ ] Grep `docs/systems/strategy_layer.md` for references to the deleted
      registry helpers and any "registry owns X" wording.
- [ ] Update only the sections that describe hook placement or registry
      ownership.
- [ ] If the file does not mention any of this, skip the update and note
      the skip in `findings/`.

**Notes:**

### Task 6.4: Final acceptance check [Simple]

- [ ] Verify every plan.md verification checkbox can be ticked.
- [ ] Verify `turn_phase_registry.py` has zero module-level functions and
      zero gameplay engine imports (sanity check via the Phase 4 guard).
- [ ] Run `phase_complete.py PROJ-428 phase_5` so the final cumulative
      review covers all six phases.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full sharded suite is green
- [ ] Update status at top of this file to `Complete (Committed)`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Awaiting final audit"
