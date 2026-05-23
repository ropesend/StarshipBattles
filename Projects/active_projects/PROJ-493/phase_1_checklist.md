# Phase 1: Add validator DI seam to SuperweaponOrderProcessor

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-493 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Introduce a `validator` constructor parameter to `SuperweaponOrderProcessor` following the existing lazy-default pattern. Route the existing static `SuperweaponValidator.find_ship_with_ability(...)` call through the injected/defaulted validator. TDD-driven.

---

## Tasks

### Task 1.0: Read production class and verify assumptions
**File:** `game/strategy/engine/superweapon_order_processor.py`, `game/strategy/validation/superweapon_validator.py`
**Tests:** none — read-only

- [ ] Read `SuperweaponOrderProcessor.__init__` and confirm the 3 existing deps and lazy-default helpers (`_get_empire_mutator`, `_get_nav_service`).
- [ ] Read `SuperweaponValidator.__init__` and confirm NO side effects (registers no handlers, opens no files). If side effects exist → use a module-level singleton instead of lazy default. Document the deviation in `decisions.md`.
- [ ] Confirm `find_ship_with_ability` is on `SuperweaponValidator` (not a subclass). If hierarchy exists, document.
- [ ] Confirm whether the method is `@staticmethod`, `@classmethod`, or instance method. Note in this checklist.

### Task 1.1: Write failing TDD test for constructor injection [Strict TDD]
**File:** `tests/unit/strategy/engine/test_superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py::test_validator_injection -xvs`

- [ ] Add a NEW test `test_validator_injection_is_consulted`:
  - Construct `SuperweaponOrderProcessor(validator=StubValidator())` where `StubValidator.find_ship_with_ability` records calls and returns a stub ship.
  - Invoke a method that hits the validator path (e.g. one of the 16 currently-patching tests' code paths).
  - Assert the stub recorded the call.
- [ ] Run the test — it MUST fail (validator kwarg doesn't exist yet). Record the failure mode.

### Task 1.2: Add validator constructor parameter and lazy default
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`

- [ ] Add `validator: Optional[Any] = None` to `__init__` parameter list.
- [ ] Add `self._validator = validator` in `__init__` body.
- [ ] Add `_get_validator()` method mirroring `_get_nav_service` / `_get_empire_mutator` pattern (import from `game.strategy.validation.superweapon_validator`).
- [ ] Update the static call sites at lines 280-282 (and any others found) to route through `self._get_validator()`.
- [ ] Verify Task 1.1's new test passes.
- [ ] Verify ALL other tests in the file still pass (no regression).

### Task 1.3: Document the seam
**File:** `docs/02_PATTERNS.md`
**Tests:** none — docs

- [ ] If the existing constructor-injection guidance is sufficient, add a `superweapon_order_processor.SuperweaponOrderProcessor.validator` reference to the canonical-DI-seam list.
- [ ] If the validator pattern needs its own guidance, add a short section pointing at `SuperweaponOrderProcessor` as the canonical example.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `SuperweaponOrderProcessor.__init__` accepts `validator=None`
- [ ] All existing tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2

_Source: PROJ-479 Phase 3 Task 3.14 + Codex consult. See [findings/source_review.md](findings/source_review.md)._
