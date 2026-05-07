# Phase 1: Golden-save fixture (closes PROJ-372 review MAJ-001)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-377 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** none
**Review Mode:** lightweight
**Objective:** Add a checked-in JSON golden-save fixture (two variants: baseline + populated) to `tests/fixtures/saves/` and a deterministic capture script. Extend `tests/integration/strategy/test_save_round_trip.py` with two assertions that load each fixture and verify byte-identical round-trip via `Galaxy.from_dict(fixture).to_dict() == fixture`. Closes PROJ-372 review MAJ-001 — protects the cumulative serialization path across PROJ-368 → PROJ-372 (and forward).

**Files (planned):** see manifest.md "Phase 1" row group.
**Test target:** `pytest tests/integration/strategy/test_save_round_trip.py -v`
**Sharded suite:** must remain green; pass count grows by 2.

---

## Reading

- [x] `tests/integration/strategy/test_save_round_trip.py` — full file (99 LOC); shape of synthetic round-trip
- [x] `game/strategy/data/galaxy.py:287-350` — `to_dict` / `from_dict`
- [x] `game/strategy/data/planet_serde.py:30-185` — Planet to_dict / from_dict_kwargs (47-field surface)
- [x] `game/strategy/data/star_system.py` — `StarSystem.to_dict / from_dict`
- [x] PROJ-377 [design.md](design.md) §"Golden-fixture format" — JSON, two fixtures, capture script convention
- [x] PROJ-377 [decisions.md](decisions.md) — confirm fixture format choice and seed values

---

## Tasks

### Task 1.1: Add the two golden-fixture round-trip tests (TDD — must FAIL first) [Simple]
**File:** `tests/integration/strategy/test_save_round_trip.py` (modify)
**Tests:** `pytest tests/integration/strategy/test_save_round_trip.py -v`

- [x] At the top of the file, add `import json` and `from pathlib import Path` if not present.
- [x] Add `_FIXTURE_DIR = Path(__file__).parent.parent.parent / "fixtures" / "saves"` (or use `Paths` if the project has a fixtures path).
- [x] Add a new test function `test_round_trip_golden_baseline_fixture()`:
  - Load the JSON: `fixture = json.loads((_FIXTURE_DIR / "galaxy_proj372_baseline.json").read_text())`. (`read_text()` reads the file; `json.loads` parses the resulting string. `json.loads` does NOT accept `Path` objects.)
  - `galaxy = Galaxy.from_dict(fixture)`
  - `assert galaxy.to_dict() == fixture`
- [x] Add `test_round_trip_golden_populated_fixture()` mirror of the above with `galaxy_proj372_populated.json`.
- [x] Run pytest: `pytest tests/integration/strategy/test_save_round_trip.py -v`.
- [x] **Verify:** both new tests FAIL because the fixture files do not yet exist (expected error: `FileNotFoundError` / `OSError` citing the missing JSON paths). The 5 pre-existing synthetic tests must still pass.

**Notes:**

### Task 1.2: Write the capture script [Medium]
**File:** `tests/fixtures/saves/_capture_baseline.py` (NEW)
**Tests:** Manual `python tests/fixtures/saves/_capture_baseline.py`

- [x] Confirm `tests/fixtures/` exists (it does — see `tests/fixtures/captions/`, `tests/fixtures/test_components.json`).
- [x] Confirm no pre-existing `tests/fixtures/saves/` directory; create it: `mkdir tests/fixtures/saves`.
- [x] Module docstring: explain the script's purpose (deterministic JSON capture for golden-fixture round-trip), why leading underscore (pytest-no-discovery), and how to re-run.
- [x] Reuse the synthetic test's structure: `random.seed(2)`, `Galaxy(radius=30)`, `generate_systems(5, min_dist=5)`, `_strip_storms(galaxy)`, `generate_warp_lanes()`. Call this `capture_baseline()`.
- [x] Write a `capture_populated()` function: `random.seed(100)`, `Galaxy(radius=50)`, `generate_systems(10, min_dist=5)`, strip storms, generate planets where possible (try/except per `test_round_trip_10_systems_with_planets`), generate warp lanes, then construct one explicitly-owned planet with non-default fields (atmosphere, owned_id, populations, stockpile, intrinsic_abilities) and register it. The goal: every Planet field in `planet_serde.planet_to_dict` is populated with non-default content for at least one planet in the fixture.
- [x] Write a `main()` that calls both, opens `tests/fixtures/saves/galaxy_proj372_baseline.json` and `..._populated.json` for write, dumps via `json.dump(d, f, indent=2, sort_keys=True)`.

**Notes:**

### Task 1.3: Run the capture script and check in the two JSON fixtures [Simple]
**File:** `tests/fixtures/saves/galaxy_proj372_baseline.json` (NEW), `tests/fixtures/saves/galaxy_proj372_populated.json` (NEW)
**Tests:** Manual

- [x] Run the script: `python tests/fixtures/saves/_capture_baseline.py`.
- [x] **Verify:** both files exist; sizes are reasonable (baseline ~10-50 KB, populated ~100-500 KB).
- [x] **Verify:** re-running the script produces byte-identical files (idempotent).
- [x] `git add tests/fixtures/saves/galaxy_proj372_baseline.json tests/fixtures/saves/galaxy_proj372_populated.json` (commit deferred to Task 1.7).

**Notes:**

### Task 1.4: Re-run the round-trip tests; confirm they now pass [Simple]
**File:** `tests/integration/strategy/test_save_round_trip.py`
**Tests:** `pytest tests/integration/strategy/test_save_round_trip.py::test_round_trip_golden_baseline_fixture tests/integration/strategy/test_save_round_trip.py::test_round_trip_golden_populated_fixture -v`

- [x] Run focused.
- [x] **Verify:** both tests pass (closes the TDD red→green loop established in Task 1.1).

**Notes:**

### Task 1.5: Run the full integration test file [Simple]
**File:** `tests/integration/strategy/test_save_round_trip.py`
**Tests:** `pytest tests/integration/strategy/test_save_round_trip.py -v`

- [x] Confirm all 7 functions pass (5 synthetic + 2 new golden-fixture).
- [x] **Verify:** sharded suite pass count grew by 2.

**Notes:**

### Task 1.6: Run sharded suite [Medium]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run the full sharded suite.
- [x] **Verify:** pass count = baseline + 2; zero new failures.
- [x] Pin the new pass count in `plan.md` Current State.

**Notes:**

### Task 1.7: Commit Phase 1 [Simple]
**File:** N/A

- [x] `git add tests/fixtures/saves/galaxy_proj372_baseline.json tests/fixtures/saves/galaxy_proj372_populated.json tests/fixtures/saves/_capture_baseline.py tests/integration/strategy/test_save_round_trip.py`
- [x] Commit message: `PROJ-377 phase 1: golden-save JSON fixtures + round-trip identity tests (closes PROJ-372 review MAJ-001)`
- [x] **Verify:** `git status` clean; `git log -1 --stat` shows the expected files.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Both fixtures committed
- [x] Both new round-trip tests passing
- [x] Sharded suite green; pass count = baseline + 2
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
