# Phase 7: Documentation Closeout [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-296 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update the documentation to match the new architecture. Run the full sharded suite. Confirm everything is green.

---

## Tasks

### Task 7.1: Add `services/` layer to `docs/01_ARCHITECTURE.md` [Medium]
**File:** `docs/01_ARCHITECTURE.md`
**Tests:** N/A (docs)

- [ ] Add `Services Layer` row to the Layer Structure ASCII diagram between Engine and Core (per design.md hierarchy)
- [ ] Update the Dependency Rules table:
  - Add new row: `Services` → `Allowed Dependencies: Core only`
  - For UI / AI / Strategy / Research / Simulation / Engine, append `Services` to their allowed-deps list
- [ ] Add a new section after "Forbidden Dependencies":
  ```markdown
  ### What belongs in `game/services/`?

  Every service must satisfy ALL three:

  1. **Depends only on `game/core/`** (and stdlib + third-party). Never imports from a domain layer.
  2. **Used by 2+ other layers** (or has clear roadmap to be). Otherwise it belongs in the consuming layer's own `services/` subpackage.
  3. **Has a documented protocol + at least one testable implementation.**

  Current services:
  - `game/services/llm/` — LLM provider abstraction (PROJ-296)
  ```
- [ ] Add `game/services/` entry to the "Package Directory Map" table after `game/core/`
- [ ] Update the "Last verified" header date

**Notes:**

### Task 7.2: Add Pattern #28 "Background Service Call" to `docs/02_PATTERNS.md` [Medium]
**File:** `docs/02_PATTERNS.md`
**Tests:** N/A (docs)

- [ ] Add Pattern #28 entry to the Table of Contents
- [ ] Bump pattern count in document header (currently 27)
- [ ] Add the section at the end before "Quick Reference":
  ```markdown
  ## 28. Background Service Call (PROJ-296)

  **Where:** `game/services/llm/background.py` — `LLMBackgroundCall`

  **How It Works:**
  Wraps a synchronous service call (LLM `complete()`) in a worker thread.
  Caller polls `.status` / `.result` / `.error` / `.elapsed_seconds` from the
  pygame `update()` loop. Cancellation via `.cancel()` sets a `threading.Event`
  that the underlying provider checks between retries; in-flight HTTP work
  completes in the background and is discarded. A module-level counter enforces
  `LLMConfig.MAX_CONCURRENT_CALLS`. A shutdown hook in `game/app.py` joins all
  workers with a 5s timeout before `pygame.quit()`.

  **When to Use:**
  - Any service call with unbounded latency (network I/O) that must not block
    the pygame main loop.
  - Future LLM consumers (race description, diplomacy turn-end, ad-hoc summaries).
  - Future non-LLM services with the same shape (cloud sync, telemetry uploads).

  **Don't:**
  - Use for fast operations (file I/O, in-memory work) — overhead isn't worth it.
  - Skip the concurrent-call limit — buggy consumers can otherwise spam expensive
    requests.
  ```
- [ ] Add Pattern 28 row to the Quick Reference table

**Notes:**

### Task 7.3: Add LLM Service entry to `docs/04_SERVICES.md` [Simple]
**File:** `docs/04_SERVICES.md`
**Tests:** N/A (docs)

- [ ] Read existing structure of 04_SERVICES.md
- [ ] Add a section for the LLM Service following the existing format:
  - Location: `game/services/llm/`
  - Public API: `LLMProvider` Protocol, `LLMProviderFactory`, `LLMBackgroundCall`, `get_default_llm_provider()`
  - Configuration: `DEEPSEEK_API_KEY` env var, `LLMConfig` constants in `game/core/config.py`
  - Status: Foundation only — no consumers wired yet (PROJ-296)

**Notes:**

### Task 7.4: Add LLM exception branch to `docs/05_ERROR_HANDLING.md` [Simple]
**File:** `docs/05_ERROR_HANDLING.md`
**Tests:** N/A (docs)

- [ ] Add `LLMException` branch to the exception hierarchy diagram
- [ ] Add LLM exception classes to the "When to Use Each Exception Type" table
- [ ] Add `L001`-`L006` codes to the Error Codes section
- [ ] Update the "Last Updated" footer

**Notes:**

### Task 7.5: Verify the new `services/` layer rule is enforced [Simple]
**File:** Tests only
**Tests:** New regression test

- [ ] Add `tests/regression/test_services_layer_rule.py` that scans `game/services/llm/*.py` and asserts none of them import from `game.simulation`, `game.strategy`, `game.ai`, `game.ui`, `game.research`, `game.engine`. Only `game.core` (and stdlib / third-party) is allowed.
- [ ] Run the test, confirm it passes

**Notes:**

### Task 7.6: Final full-suite verification [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run `python Tools/test_sharded/test_sharded.py`
- [ ] Confirm: baseline 15167 + ~60 new = ~15227+ passing, 0 failures
- [ ] Confirm wall time is roughly +1s over baseline (50.3s → ~51s)
- [ ] Document final test count in plan.md Current State

**Notes:**

### Task 7.7: Manual smoke (optional but recommended) [Simple]
**File:** N/A
**Tests:** Manual

- [ ] With `DEEPSEEK_API_KEY` UNSET: launch the game, confirm no crash. `get_default_llm_provider()` returns None silently.
- [ ] With `DEEPSEEK_API_KEY` SET to a fake/expired key: launch the game, confirm no crash at startup. (No consumer yet exercises the provider.)
- [ ] With `DEEPSEEK_API_KEY` SET to a real key: from a Python shell with the venv active:
  ```python
  from game.services.llm import get_default_llm_provider, Message, Role
  from game.context import ApplicationContext
  ctx = ApplicationContext.create_production()
  p = get_default_llm_provider()
  assert p is not None
  result = p.complete([Message(role=Role.USER, content='Say hi.')])
  print(result.text)
  print(result.usage)
  ```
- [ ] If smoke succeeds, document in plan.md that v1 is functional end-to-end.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] All docs updated and consistent
- [ ] Layer-rule regression test added and passing
- [ ] Full sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table — all phases `Complete`
- [ ] Update `plan.md` Current State — implementation done, awaiting user verification
