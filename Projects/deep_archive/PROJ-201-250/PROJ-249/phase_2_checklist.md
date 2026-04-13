# PROJ-249 Phase 2: Update Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> Run: `pytest tests/unit/simulation/combat/test_targeting_system.py -x`

## Objective
Verify existing behavior preserved and custom targets work.

## Status: Not Started

---

### Task 2.1: Verify Existing PDC Tests Pass [Simple]
**File:** `tests/unit/simulation/combat/test_targeting_system.py`
**Tests:** `pytest tests/unit/simulation/combat/test_targeting_system.py -x`

- [ ] Run `TestPDCFighterDetection` class (lines 864-956) — all existing tests pass unchanged
- [ ] Verify SEEKER-PD-001 and SEEKER-PD-002 simulation tests still pass

### Task 2.2: Add Custom Target Tests [Simple]
**File:** `tests/unit/simulation/combat/test_targeting_system.py`
**Tests:** `pytest tests/unit/simulation/combat/test_targeting_system.py -x`

- [ ] Add test: PDC with `pdc_valid_targets=["MISSILE", "FIGHTER", "DRONE"]` targets drone entities
- [ ] Add test: PDC with `pdc_valid_targets=["MISSILE"]` does NOT target fighters (only missiles)
- [ ] Add test: PDC with default (no pdc_valid_targets in JSON) behaves identically to current
