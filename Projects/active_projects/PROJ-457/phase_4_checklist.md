# PROJ-457 Phase 4: F-C-028 — Split `game/core/exceptions.py` (411 LOC at HEAD; PENDING USER DECISION on scope) by domain with re-export shim

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-457 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** None (Phases 1-3 not hard prerequisites — write scope is `game/core/`, fully disjoint from `game/ui/`).
**Review Mode:** standard
**Objective:** Split `game/core/exceptions.py` (411 LOC at HEAD, 31 classes — re-measured 2026-05-19) by domain into 5 submodules; `exceptions.py` becomes a re-export aggregator (~60-80 LOC with explicit per-name imports per convention) so all 250+ existing callers keep working unchanged. **Note: the file is ALREADY UNDER the 500-LOC ceiling at HEAD; the original "544 LOC over ceiling" framing is stale. Rationale shifted from ceiling enforcement to architectural cleanup (31 classes split by domain for clarity / import locality). PHASE 4 PENDING USER DECISION on whether to proceed.**

**Source-of-truth finding:** F-C-028 in [`findings/PROJ-457_findings.md`](findings/PROJ-457_findings.md).

**Pattern reference:** `docs/02_PATTERNS.md` §36 (Re-Export Shim) — allowed convention when "many callers exist" (re-verified 2026-05-19: 250+ caller files).

**Verified domain split (by reading `exceptions.py` class headers 2026-05-19):**

| Submodule | Class count | Est. LOC | Class names |
|-----------|-----------:|---------:|-------------|
| `exceptions_base.py` | 7 | ~110 | `GameException`, `StateException`, `FrozenStateException`, `ValidationException`, `ResourceException`, `MissingResourceException`, `PersistenceException` |
| `exceptions_strategy.py` | 5 | ~95 | `StrategyException`, `SessionInitializationError`, `EnginePhaseError`, `TurnFailedError`, `BattleResolutionError` |
| `exceptions_simulation.py` | 3 | ~30 | `SimulationException`, `ComponentException`, `FormulaException` |
| `exceptions_llm.py` | 8 | ~85 | `LLMException`, `LLMConfigError`, `LLMNetworkError`, `LLMResponseError`, `LLMRateLimited`, `LLMTimeoutError`, `LLMCancelled`, `LLMUnexpectedError` |
| `exceptions_image.py` | 8 | ~80 | `ImageException`, `ImageConfigError`, `ImageNetworkError`, `ImageResponseError`, `ImageRateLimited`, `ImageTimeoutError`, `ImageCancelled`, `ImageUnexpectedError` |

Total: 31 classes (count includes 4 additional names beyond the 27 in `01_ARCHITECTURE.md` — verified 2026-05-19 against `grep -cE "^class\s+\w+Exception|^class\s+\w+Error" exceptions.py`).

---

## Tasks

> **TDD ordering (codex r5 audit 2026-05-19):** The structure tests come FIRST and must be RED before the implementation tasks land. The repo's fail-first rule (`AGENTS.md` §"Strict TDD") requires the failing test be written before the production code that satisfies it.

### Task 4.1: Add new structure tests for the planned submodules + the re-export shim contract (RED) [Simple]
**File:** `tests/unit/core/test_exceptions.py` (existing — append new tests; existing tests stay untouched).
**Tests:** `pytest tests/unit/core/test_exceptions.py -q`

- [ ] Read `tests/unit/core/test_exceptions.py`. Existing tests assert on exception class behavior; they continue to work through the re-export aggregator once Tasks 4.2-4.3 land.
- [ ] **RED**: Add the following tests at the bottom of the file. They MUST fail/error initially because the submodules don't exist yet:
  - **Re-export shim contract**: one test per submodule asserting an exception class is importable from BOTH `game.core.exceptions` AND its new domain submodule, and that the two import paths return the same object identity. Five tests total (one per submodule); each picks a representative class:
    ```python
    def test_strategy_exception_importable_from_both_paths():
        from game.core.exceptions import StrategyException as via_aggregator
        from game.core.exceptions_strategy import StrategyException as via_submodule
        assert via_aggregator is via_submodule
    ```
    Repeat for `GameException` (exceptions_base), `SimulationException` (exceptions_simulation), `LLMException` (exceptions_llm), `ImageException` (exceptions_image).
  - **`__all__` structural-drift guard**: one test per submodule asserting each domain submodule's `__all__` matches the actual class definitions in that submodule (catches drift from adding a class without exporting it). Implementation hint: use `inspect.getmembers(submodule, inspect.isclass)` filtered to classes defined in that submodule, then assert that the set of names equals `set(submodule.__all__)`.
- [ ] Run the test file. Expect every new test to FAIL with `ModuleNotFoundError` (the submodules don't exist yet). Confirm the failure mode matches expectations — this is the RED step.
- [ ] Do NOT proceed to Task 4.2 until the new tests are committed (or staged) and confirmed RED.

### Task 4.2: Create the 5 new submodules (GREEN for submodule existence; reusable-class tests still RED) [Medium]
**Files:** `game/core/exceptions_base.py`, `exceptions_strategy.py`, `exceptions_simulation.py`, `exceptions_llm.py`, `exceptions_image.py` (all new).
**Tests:** `pytest tests/unit/core/test_exceptions.py -q` — the new structural-drift tests should pass for the freshly-created submodules; the re-export shim contract tests still RED because the aggregator isn't built yet.

- [ ] For each domain submodule, create a new file with:
  - Module docstring describing the domain (one sentence each — these are sibling files, not deep documentation).
  - Imports from `__future__` and standard library.
  - The class definitions in the same order they appear in the original `exceptions.py`.
  - An `__all__` declaration listing every class name in the submodule.
- [ ] Copy the class definitions verbatim from `exceptions.py`. Do NOT refactor the class hierarchy in this phase — that is a separate decision.
- [ ] If a class inherits from a class in another submodule (e.g. `StrategyException(GameException)`), import the parent from its new submodule (`from game.core.exceptions_base import GameException`).
- [ ] Verify each new submodule's LOC (PowerShell-safe): for each file, run `(Get-Content game/core/exceptions_base.py | Measure-Object -Line).Lines` (etc.) — each must be under 200 LOC (well under the 500 ceiling).
- [ ] Run the new structural-drift tests; they should pass now that the submodules + `__all__` lists exist.

### Task 4.3: Convert `exceptions.py` to the re-export aggregator (GREEN for shim contract tests) [Medium]
**File:** `game/core/exceptions.py`
**Tests:** `pytest tests/unit/core/test_exceptions.py -q` — all new tests, plus all pre-existing tests, should now pass.

- [ ] Replace the entire content of `exceptions.py` with the re-export aggregator. Sketch:
  ```python
  """Exception hierarchy re-exports.
  
  This module is a thin aggregator over the domain-split exception modules
  introduced by PROJ-457 Phase 4. All 31 exception classes are still
  importable from `game.core.exceptions` for back-compat with the 250+
  caller files in the repo.
  
  Direct imports from the domain submodules are also supported and recommended
  for new code.
  
  Submodules:
  - exceptions_base: base hierarchy (GameException, StateException, ValidationException, ResourceException, PersistenceException, ...)
  - exceptions_strategy: strategy-layer errors (StrategyException, SessionInitializationError, EnginePhaseError, TurnFailedError, BattleResolutionError)
  - exceptions_simulation: simulation-layer errors (SimulationException, ComponentException, FormulaException)
  - exceptions_llm: LLM service errors (LLMException + 7 subclasses)
  - exceptions_image: image service errors (ImageException + 7 subclasses)
  """
  from game.core.exceptions_base import (
      GameException,
      StateException,
      FrozenStateException,
      ValidationException,
      ResourceException,
      MissingResourceException,
      PersistenceException,
  )
  from game.core.exceptions_strategy import (
      StrategyException,
      SessionInitializationError,
      EnginePhaseError,
      TurnFailedError,
      BattleResolutionError,
  )
  from game.core.exceptions_simulation import (
      SimulationException,
      ComponentException,
      FormulaException,
  )
  from game.core.exceptions_llm import (
      LLMException,
      LLMConfigError,
      LLMNetworkError,
      LLMResponseError,
      LLMRateLimited,
      LLMTimeoutError,
      LLMCancelled,
      LLMUnexpectedError,
  )
  from game.core.exceptions_image import (
      ImageException,
      ImageConfigError,
      ImageNetworkError,
      ImageResponseError,
      ImageRateLimited,
      ImageTimeoutError,
      ImageCancelled,
      ImageUnexpectedError,
  )
  
  __all__ = [
      # base
      "GameException", "StateException", "FrozenStateException",
      "ValidationException", "ResourceException", "MissingResourceException",
      "PersistenceException",
      # strategy
      "StrategyException", "SessionInitializationError", "EnginePhaseError",
      "TurnFailedError", "BattleResolutionError",
      # simulation
      "SimulationException", "ComponentException", "FormulaException",
      # llm
      "LLMException", "LLMConfigError", "LLMNetworkError", "LLMResponseError",
      "LLMRateLimited", "LLMTimeoutError", "LLMCancelled", "LLMUnexpectedError",
      # image
      "ImageException", "ImageConfigError", "ImageNetworkError", "ImageResponseError",
      "ImageRateLimited", "ImageTimeoutError", "ImageCancelled", "ImageUnexpectedError",
  ]
  ```
- [ ] Prefer explicit `from ... import X, Y, Z` over `from ... import *` — explicit imports are clearer and survive better in code-review.
- [ ] Verify (PowerShell-safe): `(Get-Content game/core/exceptions.py | Measure-Object -Line).Lines` should now return < 80 LOC.
- [ ] Re-run `pytest tests/unit/core/test_exceptions.py -q`. The re-export shim contract tests added in Task 4.1 should now all pass. The structural-drift tests should remain green.

### Task 4.4: Run the sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run the full sharded suite. Expect green at the same count as before Phase 4 — the re-export aggregator preserves the public API end-to-end.
- [ ] If any test fails with `ImportError` or `AttributeError` on an exception class, the aggregator is missing a name. Audit the original `exceptions.py` for any classes not yet split (e.g. private helpers, type aliases) and decide: move them to the appropriate submodule or keep them in the aggregator.

### Task 4.5: Update docs [Simple]
**Files:** `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md` §36.

- [ ] `docs/01_ARCHITECTURE.md`: Update the `game/core/` package map entry for `exceptions.py`. Current text: "`exceptions.py`: 27 exception classes, including strategy, LLM, and image-service hierarchies." Replace with: "`exceptions.py`: re-export aggregator over 5 domain submodules (`exceptions_base`, `exceptions_strategy`, `exceptions_simulation`, `exceptions_llm`, `exceptions_image`) — 31 classes total". **Cross-group collision: this file is also touched by PROJ-459 + PROJ-460 — check the coordinator's serialization decision in plan.md's Dependencies section before editing.**
- [ ] `docs/02_PATTERNS.md` §36 (Re-Export Shim): Add `game/core/exceptions.py` to the documented shim sites if it isn't already there.
- [ ] Bump the "Last verified" date on both docs to today's date.

---

## Phase Completion Checklist

When all 5 tasks are checked off:
- [ ] F-C-028 flipped to `Status: resolved` in `findings/PROJ-457_findings.md`.
- [ ] PowerShell-safe LOC check: `(Get-Content game/core/exceptions.py | Measure-Object -Line).Lines` returns < 80.
- [ ] PowerShell-safe LOC check: every new `game/core/exceptions_*.py` submodule under 200 LOC (per-file measurement using the same pattern).
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green at the same count.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-457 4` — PASSED.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to point to Phase 5.
- [ ] Commit message: `PROJ-457 Phase 4: split game/core/exceptions.py by domain with re-export shim (411 -> <NEW> LOC + 5 submodules; 31 classes split; F-C-028 closed as architectural cleanup — file was already under 500 ceiling)`.
- [ ] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.
