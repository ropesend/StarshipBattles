# Phase 2: Cross-process determinism (PYTHONHASHSEED + subprocess)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-379 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_1
**Review Mode:** lightweight
**Files (planned):**
- `tests/integration/strategy/test_save_round_trip.py` (modify — +2 cross-process determinism tests)

**Objective:** The Phase 1 byte-determinism tests run in a single process and a fixed `PYTHONHASHSEED`. Phase 2 adds tests that spawn fresh subprocesses with `PYTHONHASHSEED=random`, ensuring the builder's output is also byte-identical *across* processes — this is what G1 actually requires (`Projects/active_projects/PROJ-379/plan.md` G1). The Phase 1 in-process check would pass for a builder that accidentally iterates a `set`; the cross-process check would not.

---

## Reading

- [x] Phase 1 outcomes — confirm `_build_galaxy_fixture.py` is in place and the JSONs are regenerated.
- [x] PROJ-379 `decisions.md` row "PYTHONHASHSEED-immune build" — the standing rule the test enforces.

---

## Tasks

### Task 2.1: Add cross-process subprocess determinism tests [Medium]
**File:** `tests/integration/strategy/test_save_round_trip.py`
**Tests:** `pytest tests/integration/strategy/test_save_round_trip.py::test_baseline_byte_deterministic_across_processes tests/integration/strategy/test_save_round_trip.py::test_populated_byte_deterministic_across_processes --override-ini="addopts=" -v`

- [x] Add helper near the top of the test file:
  ```python
  import os
  import subprocess
  import sys


  def _run_builder_in_subprocess(builder_name: str, hash_seed: str) -> str:
      """Spawn a fresh Python process with PYTHONHASHSEED, return JSON string from the builder."""
      env = os.environ.copy()
      env["PYTHONHASHSEED"] = hash_seed
      result = subprocess.run(
          [
              sys.executable, "-c",
              "import json; "
              f"from tests.fixtures.saves._build_galaxy_fixture import {builder_name}; "
              f"print(json.dumps({builder_name}(), indent=2, sort_keys=True))",
          ],
          capture_output=True, text=True, env=env, check=True,
          cwd=str(Path(__file__).resolve().parent.parent.parent.parent),  # repo root
      )
      return result.stdout
  ```
- [x] Add `test_baseline_byte_deterministic_across_processes`:
  ```python
  def test_baseline_byte_deterministic_across_processes() -> None:
      """PROJ-379 G1: build_baseline() output is byte-identical across processes
      with random PYTHONHASHSEED. Catches set-iteration regressions that pass
      the in-process determinism test but fail under hash randomization.
      """
      a = _run_builder_in_subprocess("build_baseline", "0")
      b = _run_builder_in_subprocess("build_baseline", "12345")
      c = _run_builder_in_subprocess("build_baseline", "random")
      assert a == b == c
  ```
- [x] Add `test_populated_byte_deterministic_across_processes` — mirror with `build_populated`.
- [x] Run focused tests; verify both pass.

**Notes:** `cwd` to repo root ensures `tests.fixtures.saves._build_galaxy_fixture` resolves; pytest's import path is unavailable inside the bare `python -c` subprocess. Adjust the depth count if the test file moves.

### Task 2.2: Run sharded suite + commit Phase 2 [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Sharded green; pass count = Phase 1 close + 2.
- [x] `git status --short` confirms only `test_save_round_trip.py` dirty.
- [x] Commit message: `PROJ-379 phase 2: cross-process PYTHONHASHSEED determinism tests`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] Both subprocess determinism tests committed and passing.
- [x] Sharded suite green.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 3.
