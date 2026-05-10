# Phase 2: New game/ui/services/image/ service

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-314 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the new image-generation service mirroring `game/services/llm/`.

---

## Tasks

### Task 2.1: Add image-provider service modules [Medium]
**Files:** `game/ui/services/image/`
**Tests:** `pytest tests/unit/ui/services/image/`

- [x] Create `provider.py` protocol.
- [x] Create `types.py` result DTOs.
- [x] Create `openai_provider.py` concrete provider.
- [x] Create `null_provider.py` unavailable-provider implementation.
- [x] Create `factory.py` provider factory.
- [x] Create `defaults.py` module-level default accessors.
- [x] Create `background.py` background-call wrapper.

**Notes:** Shipped via commit 62a7c05af (PROJ-314 Phase 2).

### Task 2.2: Add image-service unit tests [Medium]
**Files:** `tests/unit/ui/services/image/`
**Tests:** `pytest tests/unit/ui/services/image/`

- [x] Add provider contract tests.
- [x] Add OpenAI provider request/response tests.
- [x] Add null provider tests.
- [x] Add factory/default access tests.
- [x] Add background-call lifecycle tests.

**Notes:** Shipped via commit 62a7c05af (PROJ-314 Phase 2).

### Task 2.3: Wire image provider into ApplicationContext [Simple]
**File:** `game/context.py`
**Tests:** `pytest tests/unit/test_application_context.py`

- [x] Add `image_provider` constructor slot.
- [x] Create production provider via `ImageProviderFactory`.
- [x] Install `NullImageProvider` when image generation is unavailable.
- [x] Support `image_provider` override in `create_test()`.

**Notes:** Shipped via commit 62a7c05af (PROJ-314 Phase 2).

### Task 2.4: Reset image-provider defaults in tests [Simple]
**File:** `tests/conftest.py`
**Tests:** `pytest tests/unit/ui/services/image/`

- [x] Add default-provider reset coverage to the test fixture stack.
- [x] Confirm image-service state is isolated between tests.

**Notes:** Shipped via commit 62a7c05af (PROJ-314 Phase 2).

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Image-service modules exist
- [x] Image-service tests exist and pass
- [x] ApplicationContext wiring exists
- [x] Commit: `feat(PROJ-314 Phase 2): game/ui/services/image/ service + DI wiring`
