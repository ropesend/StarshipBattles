# Phase 1: Extract stats-calculation logic before changing storage

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-425 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_0
**Review Mode:** standard
**Files (planned):**
- `game/strategy/data/ship_instance.py` (slim — stats logic moves out)
- `game/strategy/data/ship_stats_cache.py` (optional new — only if no natural existing home)
- `tests/unit/strategy/ship_instance/test_registries_di.py` (extend)
- `tests/unit/strategy/ship_instance/test_ship_stats_cache.py` (optional new — only if helper file is created)

**Objective:** Move stats-calculation + cache-invalidation behavior into a helper / service. **Keep `_cached_stats` on the entity for this phase** (TD-06 Weak-LLM Guardrail #2: move logic first, storage second). Required behavior preserved: missing-registry failures still surface the same way; cache invalidation after relevant state changes still works; callers do not need to change.

---

## Pre-flight (TDD baseline)

- [ ] Re-read Phase 0 findings on stats-cache behavior in `findings_ledger.md`.
- [ ] Re-read the stats-related sections of `ship_instance.py` (calculation entry point, invalidation hooks, `_cached_stats` reads/writes).
- [ ] Decide: extend an existing stats path / service, or add the optional `game/strategy/data/ship_stats_cache.py`. **Prefer extension** unless no natural home exists. Record the decision in `decisions.md`.

---

## Tasks

### Task 1.1: TDD anchor — add or tighten the stats-cache behavior tests [Medium]
**File:** `tests/unit/strategy/ship_instance/test_registries_di.py` (extend) — and/or `test_ship_stats_cache.py` (new, only if a new helper is being introduced)
**Tests:** the chosen file(s)

- [ ] Cover: cache hit returns equal stats; missing-registry path raises the same error type/message it did in Phase 0; mutation hook (component toggle / repair) invalidates and the next read recomputes.
- [ ] Tests target the **new** entry point (helper / service method) once the implementation lands — they fail today until Task 1.2 moves the logic.
- [ ] **Verify:** tests fail for the right reason (new entry point not yet present).

**Notes:**

### Task 1.2: Move calculation + invalidation behavior into the helper [Medium]
**File:** `ship_stats_cache.py` (new) — or extension of an existing stats module per Pre-flight decision
**Tests:** Task 1.1 tests

- [ ] Cut (do not duplicate) the calculation body out of `ShipInstance`. Update `ShipInstance` to call the helper.
- [ ] Leave `_cached_stats` storage on the entity for this phase.
- [ ] Preserve the failure mode for missing registries (same exception type + message).
- [ ] **Verify:** Task 1.1 tests pass; Phase 0 stats-cache regression tests still pass.

**Notes:**

### Task 1.3: Focused regression sweep [Simple]
**Tests:** as below.

- [ ] `pytest tests/unit/strategy/ship_instance/ -x`
- [ ] `pytest tests/unit/strategy/services/test_ship_instance_write_service.py -x`
- [ ] `pytest tests/unit/strategy/fleets/test_ship_instance_roundtrip.py tests/unit/strategy/fleets/test_ship_instance_components.py -x`
- [ ] No new failures vs. the Phase 0 baseline.
- [ ] **Verify:** record pass count in `findings_ledger.md`.

**Notes:**

### Task 1.4: Sharded suite + phase complete [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Sharded suite green.
- [ ] `git status --short` confirms only Phase 1 files are dirty.
- [ ] Record post-phase `wc -l game/strategy/data/ship_instance.py` in `findings_ledger.md`.
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-425 phase_1` per 03c protocol.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Stats-calculation logic no longer lives inline in `ShipInstance`
- [ ] `_cached_stats` storage **still on the entity** (deliberate — Guardrail #2)
- [ ] Missing-registry failure mode unchanged
- [ ] Cache invalidation after state changes still works
- [ ] Focused + sharded suites green
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after review
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
