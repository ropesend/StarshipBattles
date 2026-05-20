# Phase 3: Strict-mode migration (research/services/assets/engine/core)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-462 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate the foundation layers to `mypy --strict` in dependency order (cleanest first). Per-layer error counts below are the audit's estimates; the audit's by-path attribution cannot be exactly reproduced with `mypy <path>` (mypy follows imports), so confirm the real count per layer at the start of each task before estimating effort.

---

## Tasks

### Task 3.1: Adopt strict for the research layer [Simple]
**File:** `game/research/` (mypy config)
**Tests:** `mypy --strict game/research/` then `pytest tests/ --testmon`

- [ ] Confirm current strict error count for research (audit estimate: 0)
- [ ] Resolve any residual errors
- [ ] Add `--strict` (or per-module strict config) for the research layer's mypy config
- [ ] Verify: pytest passes; `mypy --strict game/research/` shows no errors

### Task 3.2: Adopt strict for the services layer [Simple]
**File:** `game/services/` (mypy config)
**Tests:** `mypy --strict game/services/` then `pytest tests/ --testmon`

- [ ] Resolve the 1 `import-untyped` error (audit estimate: install/declare stub, e.g. `types-requests`)
- [ ] Add `--strict` to the services layer's mypy config
- [ ] Verify: pytest passes; `mypy --strict game/services/` shows no errors

### Task 3.3: Adopt strict for the assets layer [Medium]
**File:** `game/assets/` (mypy config)
**Tests:** `mypy --strict game/assets/` then `pytest tests/ --testmon`

- [ ] Resolve ~10 errors (audit: mostly `no-any-return`, `var-annotated` — annotate `AssetManager.assets/manifest/star_metadata: dict[str, ...]` in `asset_manager.py` lines 31-35; add `-> Surface`/`-> str` return types)
- [ ] Add `--strict` to the assets layer's mypy config
- [ ] Verify: pytest passes; `mypy --strict game/assets/` shows no errors

### Task 3.4: Adopt strict for the engine layer [Medium]
**File:** `game/engine/` (mypy config)
**Tests:** `mypy --strict game/engine/` then `pytest tests/ --testmon`

- [ ] Resolve ~11 errors (audit: 4 `has-type` Vector2/PhysicsBody — should be largely cleared by Phase 1.1; 4 `union-attr`; 2 `no-any-return`; 1 `assignment`)
- [ ] Add `--strict` to the engine layer's mypy config
- [ ] Verify: pytest passes; `mypy --strict game/engine/` shows no errors

### Task 3.5: Adopt strict for the core layer [Medium]
**File:** `game/core/` (mypy config)
**Tests:** `mypy --strict game/core/` then `pytest tests/ --testmon`

- [ ] Resolve the ~50 `has-type` Vector2 errors (cleared by Phase 1.1) and ~16 `no-any-return` (largely Phase 1/2 tasks above)
- [ ] Resolve remaining ~8 `assignment` (implicit Optional) errors in core
- [ ] Add `--strict` to the core layer's mypy config (foundation — benefits ALL higher layers)
- [ ] Verify: pytest passes; `mypy --strict game/core/` shows no errors

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-19_223900_type-audit/`. See `findings/source_audit.md` for the link._
