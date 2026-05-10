# Phase 4: Combat Lab fallback + docs + verifier-import lint

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-366 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Test the Combat Lab fallback path end-to-end; lock in the verifier dependency direction with an AST lint test; update docs to describe the wired feature; update PROJ-354B's Quick Status to reflect that PROJ-366 has resolved its blocked phases.

See `plan.md` Phase 4 for context. Inherits PROJ-354B Phase 6 Tasks 6.1, 6.2, 6.3, 6.4, 6.5.

---

## Tasks

### Task 4.1: Combat Lab fallback test [Medium]
**File:** `tests/integration/replay/test_combat_lab_verification.py` (NEW)
**Tests:** Same file

- [ ] **Pass case:** construct a Combat Lab synthetic record (use `combat_lab/design_loader.py::load_combat_lab_design` or the existing test fixture) where every ship's `instance_snapshot` is `None`. Construct `ReplayVerificationCoordinator` with `fallback_ship_builder=<DesignOnlyMaterializer-wrapping closure>` (mirrors Phase 2's adapter shape from `app_bootstrap.py`). Trigger verification (call `coordinator._on_record_persisted(record, path)` directly OR persist via store + listener path). Use `coordinator.wait_for_idle(timeout=30)` THEN file-existence check. Assert `status=="PASSED"`.
- [ ] **Error case:** same record, but coordinator wired with `fallback_ship_builder=None`. Trigger verification. Assert sidecar `status=="ERROR"`. Assert error message contains a diagnostic substring like "no fallback builder" or "instance_snapshot" (verify the actual production message in `replay_ship_builder.py` and pin it).
- [ ] Cleanup: `coordinator.shutdown(timeout=5.0)`.
- [ ] **Verify:** both paths green.

**Notes:**

### Task 4.2: Verifier dependency direction lint test [Simple]
**File:** `tests/unit/simulation/replay/test_replay_verifier_imports.py` (NEW)
**Tests:** Same file

- [ ] Implement the AST-walk test from `design.md` § Phase 4 lint test:
  ```python
  import ast
  from pathlib import Path

  def test_verifier_has_no_upward_imports():
      src = Path("game/simulation/replay/replay_verifier.py").read_text()
      tree = ast.parse(src)
      forbidden_prefixes = ("game.strategy.", "game.ui.", "game.ai.")
      for node in ast.walk(tree):
          if isinstance(node, (ast.Import, ast.ImportFrom)):
              mod = node.module if isinstance(node, ast.ImportFrom) else None
              for alias in node.names:
                  target = mod or alias.name
                  assert not any(target.startswith(p) for p in forbidden_prefixes), \
                      f"replay_verifier.py imports forbidden module: {target}"
  ```
- [ ] **Verify:** test passes (PROJ-354B audit-remediation `27e297815` already moved `build_replay_ship_builder` out, so this should be green on first run; if it fails, a regression has snuck in).

**Notes:**

### Task 4.3: Update `docs/systems/combat_simulation.md` [Medium]
**File:** `docs/systems/combat_simulation.md`
**Tests:** Manual review

- [ ] In § 11 Replay Capture & Playback, add a new subsection "Background Verification":
  - Explain the post-persist trigger (listener fires after `ReplayStore.persist`).
  - Document the sidecar schema (`replay_<id>.verification.json`) and file path.
  - Document `verification_enabled` and `verification_queue_cap` settings.
  - Note `run_replay_headless` requires caller-supplied `ship_builder` and `registry_provider`; the coordinator handles this.
  - Document the no-recursion guarantee (`capture_context=None` in headless path).
  - Cross-link to `Projects/active_projects/PROJ-354B/` and `Projects/active_projects/PROJ-366/` for full design context.
- [ ] Update the `> **Last verified:**` blockquote at the top of the doc to today's date.
- [ ] **Verify:** documented behavior matches implementation.

**Notes:**

### Task 4.4: Update `docs/systems/strategy_layer.md` [Medium]
**File:** `docs/systems/strategy_layer.md`
**Tests:** Manual review

- [ ] In the Replay Persistence section, add:
  - Sidecar schema overview.
  - Sidecar lifecycle (delete + evict alongside replay record — already implemented in PROJ-354B Phase 2).
  - `ReplayStore.add_on_record_persisted_listener` / `remove_on_record_persisted_listener` API.
  - `ReplayResolver.resolve` returns a `verification_status` field on `ReplayLookup`.
  - Cross-link to PROJ-354B and PROJ-366.
- [ ] Update the `> **Last verified:**` blockquote.
- [ ] **Verify:** documented behavior matches implementation.

**Notes:**

### Task 4.5: Update `docs/01_ARCHITECTURE.md` [Simple]
**File:** `docs/01_ARCHITECTURE.md`
**Tests:** Manual review

- [ ] In the Strategy services table (around line 175), add a `ReplayVerificationCoordinator` row pointing to `game/strategy/services/replay_verification_coordinator.py`.
- [ ] Update the `> **Last verified:**` blockquote.
- [ ] **Verify:** table reflects the new service.

**Notes:**

### Task 4.6: Update PROJ-354B Quick Status [Simple]
**File:** `Projects/active_projects/PROJ-354B/plan.md`

- [ ] In the Quick Status table, change Phase 5 row to `Complete (via PROJ-366)` and Phase 6 row to `Complete (via PROJ-366)`.
- [ ] Update Current State:
  - **Last Updated:** today's date
  - **Active Phase:** Project complete (Phases 1-4 + audit-remediation in this project; Phases 5-6 delivered by PROJ-366)
  - **Last Action:** PROJ-366 wired the production sink + coordinator + shutdown + integration tests + docs
  - **Next Action:** Awaiting user verification + close-out
  - **Blockers:** None

**Notes:**

### Task 4.7: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite. Compare to baseline + Phase 1/2/3/4 new tests.
- [ ] Acceptance: all tests pass; zero regressions.
- [ ] **Verify:** investigate any failures.

**Notes:**

### Task 4.8: Update `Current State` in PROJ-366 plan.md [Simple]

- [ ] In `plan.md` Quick Status, mark Phase 4 as `Complete`.
- [ ] In `plan.md` Current State:
  - **Last Updated:** today's date
  - **Active Phase:** Awaiting verification
  - **Last Action:** Phase 4 complete; Combat Lab fallback tested; verifier-import lint added; docs updated; PROJ-354B Quick Status updated.
  - **Next Action:** Audit cycle + user verification.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete and ready for verification
