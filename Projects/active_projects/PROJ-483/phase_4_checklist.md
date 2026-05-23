# Phase 4: Strict-mode adoption — clean & near-clean layers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-483 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Adopt mypy `--strict` for the 6 bounded layers — research (0 errors → config-only), engine (14), ai (60), core (116), services (1), assets (15). Heavy layers (simulation 622, strategy 1070, ui 2571) are explicitly **deferred** to a future dedicated project.

> **Verifier baseline (2026-05-22):** these counts were measured with `python -m mypy --strict --follow-imports=silent <layer_path>` on current source. If the counts differ when you re-run, the layer has changed since this project was filed — investigate before proceeding.

---

## Tasks

### Task 4.1: research — config-only enable [Simple]
**File:** `mypy.ini` (or `pyproject.toml` `[tool.mypy]`) — currently no strict overrides exist per verifier

- [ ] Re-run `python -m mypy --strict game/research/` to confirm 0 errors
- [ ] Create `mypy.ini` (or add `[tool.mypy]` to `pyproject.toml`) with a per-module override:
  ```ini
  [mypy-game.research.*]
  strict = True
  ```
- [ ] Verify: `python -m mypy game/research/` (no `--strict` flag) shows 0 errors
- [ ] Verify: full test suite still passes (`python Tools/test_sharded/test_sharded.py`)

### Task 4.2: services — investigate the 1 error then enable [Simple]
**Files:** `mypy.ini` (or `pyproject.toml`), `game/services/llm/deepseek.py` (likely)

- [ ] Re-run `python -m mypy --strict game/services/` — verifier reported 1 `import-untyped` error (likely `requests` stub missing)
- [ ] Either install stubs (`pip install types-requests`) or add `[mypy-requests.*]` ignore in config
- [ ] Confirm 0 errors after the fix
- [ ] Add `[mypy-game.services.*]` strict override
- [ ] Verify: tests still pass

### Task 4.3: assets — resolve the 15 errors then enable [Medium]
**File:** `mypy.ini`, plus per-file fixes in `game/assets/`

- [ ] Re-run `python -m mypy --strict game/assets/` — verifier reported 15 errors (type-arg×5, no-any-return×3, assignment×1, ...)
- [ ] Fix each error category — most are missing `list[T]` parameterizations or untyped returns
- [ ] Confirm 0 errors
- [ ] Add `[mypy-game.assets.*]` strict override
- [ ] Verify: tests still pass

### Task 4.4: engine — resolve the 14 errors then enable [Medium]
**File:** `mypy.ini`, plus per-file fixes in `game/engine/`

- [ ] Re-run `python -m mypy --strict game/engine/` — verifier reported 14 errors (union-attr×4, has-type×4, no-untyped-def×3, no-any-return×2, ...)
- [ ] Fix per category: add missing return types (no-untyped-def), narrow union returns (union-attr), explicit annotations for circular references (has-type)
- [ ] Confirm 0 errors
- [ ] Add `[mypy-game.engine.*]` strict override
- [ ] Verify: tests still pass

### Task 4.5: ai — resolve the 60 errors then enable [Medium]
**File:** `mypy.ini`, plus per-file fixes in `game/ai/`

- [ ] Re-run `python -m mypy --strict game/ai/` — verifier reported 60 errors (no-any-return×22, no-untyped-def×19, assignment×6, has-type×4, ...)
- [ ] Note: Phase 3 Task 3.1 already narrowed 5 AI protocol items — many `no-any-return` should drop after that lands. Re-run mypy after Phase 3 completes
- [ ] Fix remaining per category
- [ ] Confirm 0 errors
- [ ] Add `[mypy-game.ai.*]` strict override
- [ ] Verify: tests still pass

### Task 4.6: core — resolve the 116 errors then enable [Complex]
**File:** `mypy.ini`, plus per-file fixes in `game/core/`

- [ ] Re-run `python -m mypy --strict game/core/` — verifier reported 116 errors (has-type×52, type-arg×25, no-any-return×14, no-untyped-def×13, ...)
- [ ] Note: Phase 3 Tasks 3.2-3.5 already narrowed many `core/protocols/*` items — re-run after Phase 3 lands; `has-type` and `no-any-return` counts should drop substantially
- [ ] Fix remaining per category. `type-arg×25` is most likely missing `list[T]` / `dict[K,V]` parameterizations on collection annotations
- [ ] Confirm 0 errors
- [ ] Add `[mypy-game.core.*]` strict override
- [ ] Verify: tests still pass

### Task 4.7: Coordination + final verification [Simple]
- [ ] Re-confirm `mypy.ini` (or `pyproject.toml`) has strict overrides for all 6 layers: research, services, assets, engine, ai, core
- [ ] Run `python Tools/test_sharded/test_sharded.py` — must pass with 0 regressions
- [ ] Run `python -m mypy game/` (no `--strict` flag) — confirm 0 errors across covered layers (per-module strict applies)
- [ ] Update `docs/03_CONVENTIONS.md` (if appropriate) to note: research/services/assets/engine/ai/core are now under `mypy --strict`; simulation/strategy/ui remain non-strict pending follow-up

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_210540_type-audit/`. See `findings/source_audit.md` for the link._
