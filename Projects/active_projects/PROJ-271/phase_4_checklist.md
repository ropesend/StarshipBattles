# Phase 4: End-to-end integration tests + manual smoke

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Risk:** LOW (tests over working code)
**Depends On:** Phases 1 + 2 + 3
**Objective:** Integration-tier coverage for Track A + Track B modifier battle-math end-to-end (real ships, real battles). Includes the `test_storm_shield_interference.py` test deferred from PROJ-270 Task 6.5.

---

## Tasks

### Task 4.1: Storm shield interference integration test [Medium] — PROJ-270 Task 6.5 DEFERRED
**File:** `tests/integration/strategy/combat/test_storm_shield_interference.py` (new)
**Tests:** `pytest tests/integration/strategy/combat/test_storm_shield_interference.py --tb=short`

- [ ] Write test (real ships, real battles, NOT mocks): same two-ship battle in storm hex vs non-storm hex. Storm ship should take more hull damage (because `shield_capacity_mult=0.5` reduces effective shields)
- [ ] Same-shape test for fleet `shield_mult`: fleet with `shield_mult=2.0` survives a battle that the baseline fleet loses
- [ ] Same-shape test for fleet `damage_mult`: fleet with `damage_mult=2.0` destroys enemies faster
- [ ] Run — passes (Track A is already live from PROJ-270 Phase 6.1/6.2)

**Notes:** PROJ-270 Phase 6.5 deferred this specifically to land here so Track A + Track B integration tests live together in one file/folder.

---

### Task 4.2: Flat shield bonus integration test [Medium]
**File:** `tests/integration/strategy/combat/test_flat_shield_bonus.py` (new)

- [ ] Same-shape test as 4.1 but for `flat_shield_bonus`: fleet buffed by a planet aura with `flat_shield_bonus=50` takes less hull damage than the baseline fleet in the same battle

**Notes:** [Filled during implementation]

---

### Task 4.3: Suppressor integration test [Medium]
**File:** `tests/integration/strategy/combat/test_suppressor_effects.py` (new)

- [ ] Same-shape test for opponent-team-routed suppressor: enemy fleet in a hex with a suppressor planet has (for example) `damage_mult=0.8` applied; they deal less damage
- [ ] Verify: the friendly fleet on the suppressor-owning team is NOT affected (routing is correct)

**Notes:** [Filled during implementation]

---

### Task 4.4: Regression gate + manual launcher smoke [Simple]
**Tests:** Full suites + interactive manual test

- [ ] `pytest tests/ --tb=no -q` — ≥ baseline + new integration tests
- [ ] `python -m combat_lab.run_tests --fast --no-history` — 162/162 green
- [ ] `python -m combat_lab.run_tests --no-history` — 170/170 green
- [ ] Grep audit: strategy compiler emits zero `stat_key="placeholder"` for any modifier source (all sources must now map to a real stat_key)
- [ ] Manual smoke (interactive): Strategy fleet battle in a storm hex + with a flat-bonus-aura planet + opposing a suppressor planet — verify effects are visible in battle (damage numbers differ from baseline)

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] 3 integration-tier tests green
- [ ] Full regression gate green
- [ ] Manual launcher smoke verified
- [ ] Grep audit: zero placeholder stat_keys
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] PROJ-271 ready for archival via protocol 05
