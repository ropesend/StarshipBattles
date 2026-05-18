# PROJ-447 Phase 4: Test-wallpaper + static-guard backfill

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-447 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** None (independent of other phases)
**Objective:** Close 3 test/test-infra residue sites: rewrite a misleading assertion message pointing at deleted `commands/specs.py`; drop a try/except wallpaper that hides a missing `data/techtree.json` (also corrects PROJ-446 F-C-021's filename mistake); backfill the missing static guard against `commands/specs.py` re-emergence.

**Cross-bucket file-ownership rule:** Edit test files. The F-D-025 guard sits in `tests/static_guards/` which is nominally PROJ-446's home; this project's plan explicitly takes ownership of the paired companion fix to F-D-003 (both stem from PROJ-371's `commands/specs.py` retirement).

**Source-of-truth findings:** [`findings/bucket_d_simulation_ai_research_engine_docs_scan.md`](findings/bucket_d_simulation_ai_research_engine_docs_scan.md) — F-D-003 (codex seed), F-D-020, F-D-025.

---

## Tasks

### Task 4.1: F-D-003 — Rewrite test_command_specs_contract assertion message (codex seed) [Simple]
**File:** `tests/unit/strategy/engine/test_command_specs_contract.py:85-87`
**Tests:** `pytest tests/unit/strategy/engine/test_command_specs_contract.py -v`

- [ ] Read the existing assertion message: "Add an entry in game/strategy/engine/commands/specs.py."
- [ ] Confirm `commands/specs.py` is truly gone: `ls game/strategy/engine/commands/specs.py` should fail. The guard test `tests/unit/strategy/engine/test_no_specs_tuple_literal.py:3-7` confirms re-introduction is forbidden.
- [ ] Read the canonical extension path at `docs/systems/orders_system.md:130-137` and `:418-422` — uses `@command_spec(...)` decorator + per-module `register(registry)` calls
- [ ] **GREEN**: Rewrite the assertion message: "Add a `@command_spec(...)` decorator on the Command DTO and a `register(registry)` call in the owning handler module (see `docs/systems/orders_system.md`)."
- [ ] Verify the test still passes (the message change doesn't affect the assertion logic).

### Task 4.2: F-D-020 — Drop tech_tree wallpaper (corrects PROJ-446 F-C-021) [Simple]
**File:** `tests/integration/research_workflow/test_workflow.py:188-192`
**Tests:** `pytest tests/integration/research_workflow/test_workflow.py -v`

- [ ] Read the existing try/except wallpaper:
  ```python
  try:
      tree = TechTree.load_from_json()
  except FileNotFoundError:
      pytest.skip("Tech tree JSON not found")
  ```
- [ ] Note: PROJ-446 F-C-021 originally cited this finding but used the wrong filename (`tech_tree.json` doesn't exist; the real file is `data/techtree.json`). F-D-020 closes the actual finding.
- [ ] Confirm `data/techtree.json` exists: `ls data/techtree.json`
- [ ] **GREEN**: Drop the try/except. Let `FileNotFoundError` propagate naturally — if the production data file is genuinely missing, the test should fail loudly.
- [ ] Run targeted test; should pass (the file exists, so no exception is raised).

### Task 4.3: F-D-025 — commands/specs.py re-emergence static guard [Simple]
**File (new):** `tests/static_guards/test_no_commands_specs_module.py`
**Tests:** `pytest tests/static_guards/test_no_commands_specs_module.py -v`

- [ ] Read existing static guards for the canonical pattern. Codex r3 verified paths (the original phase-4 references were wrong — both files live elsewhere):
  - **Sibling guard**: `tests/unit/strategy/engine/test_no_specs_tuple_literal.py:3-7` (guards against the tuple-literal anti-pattern from the same PROJ-371 retirement). Note this lives under `tests/unit/strategy/engine/`, NOT `tests/static_guards/`.
  - **AST-scan template**: look for any existing file-existence guard in `tests/static_guards/`. If none exists yet, this guard establishes the pattern; structure it with a clear comment header naming the retirement (PROJ-371 Phase 2).
- [ ] **GREEN**: Create the new guard. Use a runtime `Path.exists()` check rather than an AST scan (the asserted invariant is "the file does not exist"):
  ```python
  from pathlib import Path
  def test_specs_module_must_not_re_emerge():
      assert not Path("game/strategy/engine/commands/specs.py").exists(), (
          "commands/specs.py was retired in PROJ-371 Phase 2. "
          "If a new commands config module is needed, choose a different name."
      )
  ```
- [ ] **RED-check**: Temporarily create an empty `game/strategy/engine/commands/specs.py`; confirm the guard fails. Delete the temp file; the guard now passes.
- [ ] Add a module docstring explaining the pairing: this guard + `tests/unit/strategy/engine/test_no_specs_tuple_literal.py` together prevent both ways of re-introducing the deleted module (file existence + tuple-literal anti-pattern).

---

## Phase Completion Checklist

- [ ] All 3 tasks complete
- [ ] Test assertion message at `test_command_specs_contract.py:85-87` updated
- [ ] Wallpaper at `test_workflow.py:188-192` removed
- [ ] Static guard `test_no_commands_specs_module.py` in place and green
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-447 4` — PASSED
- [ ] Update status to `Complete`; plan.md phase table + Current State → Phase 5

## Notes

- Small phase; 3 tasks all tiny.
- Coordination touchpoint: PROJ-446 F-C-021 is the older Bucket C finding that gave the wrong filename. **PROJ-446 owns the bookkeeping of marking F-C-021 superseded** — see `PROJ-446/phase_1_checklist.md` Task 1.7. This phase does NOT track PROJ-446's bookkeeping completion (codex r3 corrected the cross-project criterion overlap).
