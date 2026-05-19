# PROJ-454 Phase 3: Unwind `OrderProcessor.process_*` facade reshape (F-B-017)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-454 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Close F-B-017 by migrating **68 test caller sites across 12 test files** (corrected by codex audit 2026-05-19 from the original `~15 sites / 7 files` undercount) of `OrderProcessor.process_join_fleet` / `process_colonize` / `process_transfer` to read `OrderExecutionResult` directly via `processor.get_handler(...).execute_action_order(...)`, then deleting the three legacy facade methods + the three legacy typed result dataclasses (`JoinFleetResult` / `ColonizeResult` / `TransferResult`).

**Live caller inventory (re-run 2026-05-19 via `python -c "..."` walking each file with regex `\.process_(join_fleet|colonize|transfer)\(`):**

- **68 test call sites across 12 test files** (strict call-site count, excluding docstring/comment narration):
  - `tests/integration/colonization/test_explicit_orders.py` — **3 call sites** (lines 65, 91, 105)
  - `tests/integration/colonization/test_planet_specific_colonization.py` — **7 call sites** (lines 286, 380, 390, 473, 484, 520, 550)
  - `tests/integration/strategy/test_fleet_registration_lifecycle.py` — **1 call site** (line 212)
  - `tests/unit/strategy/engine/test_colonize_population.py` — **6 call sites** (lines 180, 211, 245, 280, 310, 341)
  - `tests/unit/strategy/engine/test_fleet_order_transfer.py` — **3 call sites** (lines 97, 106, 115)
  - `tests/unit/strategy/engine/test_order_processor_colonize.py` — **7 call sites** (lines 105, 124, 157, 181, 213, 245, 283)
  - `tests/unit/strategy/engine/test_order_processor_instant.py` — **2 call sites** (lines 247, 268)
  - `tests/unit/strategy/engine/test_order_processor_transfer.py` — **10 call sites** (lines 74, 112, 131, 169, 201, 231, 268, 302, 332, 369)
  - `tests/unit/strategy/engine/test_process_colonize_validation.py` — **6 call sites** (lines 201, 234, 271, 307, 386, 420)
  - `tests/unit/strategy/engine/test_transfer_order.py` — **7 call sites** (lines 196, 230, 262, 293, 327, 372, 414)
  - `tests/unit/strategy/test_engine_event_emission.py` — **5 call sites** (lines 496, 528, 592, 991, 1047)
  - `tests/unit/strategy/test_fleet_order_processor.py` — **11 call sites** (lines 82, 102, 116, 129, 196, 224, 245, 269, 520, 549, 577)

Additional non-call references (docstring, comment, internal narration — no migration needed but must drop with the deleted block):
- `game/strategy/engine/order_processor.py` — 4 references (lines 18 docstring, 97 method def, 108 method def, 123 method def — all deleted in Task 3.10)
- `game/strategy/engine/handlers/base.py:423` — single docstring reference (drops naturally when Phase 3 lands)
- `game/strategy/engine/order_handlers/{transfer,join_fleet,colonize}.py` — narration in module docstrings (update or drop in Task 3.10)
- `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py` — file-level narration; Task 3.9 decides delete-vs-rewrite

**Cross-bucket file-ownership rule:** This phase touches `game/strategy/engine/order_processor.py` (delete sections) and ~7 test files. PROJ-453 Task 1.2 annotates the same file's `__init__`; the sites are disjoint. If PROJ-453 lands first (preferred), no conflict; if PROJ-454 Phase 3 lands first, PROJ-453 rebases trivially.

**Source-of-truth findings:** [`findings/PROJ-454_findings.md`](findings/PROJ-454_findings.md) — read F-B-017's full text and the "F-B-017 caller list" subsection.

---

## Tasks

### Task 3.1: Re-run the canonical caller-list discovery commands [Simple]

- [x] Run the canonical discovery commands:
  ```bash
  git grep -nE "process_join_fleet|process_colonize|process_transfer\b" game/ tests/
  git grep -nE "JoinFleetResult|ColonizeResult|TransferResult" game/ tests/
  ```
- [x] Diff against the 2026-05-19 caller list in `findings/PROJ-454_findings.md`. Note any new callers since the audit.
- [x] **Verify**: there should be **zero production callers** of the three legacy facade methods (per the 2026-05-19 audit). If any production caller surfaces, surface for user decision — that changes the project's risk profile.

**Notes:**

---

### Task 3.2: Read the unified result contract on `OrderExecutionResult` [Simple]
**File:** Read-only — `game/strategy/engine/order_handlers/base.py:36-56`

- [x] Confirm `OrderExecutionResult` carries all the fields the test callers will need after migration:
  - `success: bool` (line 47)
  - `fleet_consumed: bool = False` (line 48)
  - `message: str = ""` (line 49)
  - `merged: bool = False` (line 51 — formerly `JoinFleetResult.merged`)
  - `cancelled: bool = False` (line 52 — formerly `JoinFleetResult.cancelled`)
  - `colonized: bool = False` (line 53 — formerly `ColonizeResult.colonized`)
  - `planet_name: Optional[str] = None` (line 54 — formerly `ColonizeResult.planet_name`)
  - `amount_transferred: int = 0` (line 55 — formerly `TransferResult.amount_transferred`)
- [x] The migration is field-by-field equivalent — every property that the legacy result types carried is already on `OrderExecutionResult`. Phase 3 is a thin remapping, not a behaviour change.

**Notes:**

---

### Task 3.3: Migrate `tests/integration/colonization/test_planet_specific_colonization.py` (7 sites) [Medium]
**File:** `tests/integration/colonization/test_planet_specific_colonization.py:286, 380, 390, 473, 484, 520, 550`
**Tests:** `pytest tests/integration/colonization/test_planet_specific_colonization.py -v`

- [x] For each `processor.process_colonize(...)` call, replace with the handler-direct path. Recipe:
  ```python
  # Before (line 286-ish):
  result = processor.process_colonize(fleet, empire, galaxy, component_registry)
  
  # After:
  handler = processor.get_handler(OrderType.COLONIZE)
  result = handler.execute_action_order(
      fleet, empire, galaxy,
      component_registry=component_registry,
  )
  ```
- [x] Update any assertion that reads `result.colonized` / `result.planet_name` — these attributes already exist on `OrderExecutionResult`, so the assertion text doesn't change.
- [x] Run targeted tests; confirm green.
- [x] **Verify**: `git grep -n "process_colonize" tests/integration/colonization/test_planet_specific_colonization.py` returns zero matches after this task.

**Notes:**

---

### Task 3.4: Migrate `tests/integration/colonization/test_explicit_orders.py` (3 sites) [Simple]
**File:** `tests/integration/colonization/test_explicit_orders.py:65, 91, 105`
**Tests:** `pytest tests/integration/colonization/test_explicit_orders.py -v`

- [x] For each `processor.process_transfer(...)` call (3 sites), replace with the handler-direct path:
  ```python
  handler = processor.get_handler(OrderType.TRANSFER)
  result = handler.execute_action_order(fleet, empire, galaxy)
  # result.success, result.amount_transferred, result.message all already on OrderExecutionResult
  ```
- [x] Run targeted tests; confirm green.

**Notes:**

---

### Task 3.5: Migrate `tests/integration/strategy/test_fleet_registration_lifecycle.py` (1 site) [Simple]
**File:** `tests/integration/strategy/test_fleet_registration_lifecycle.py:212`
**Tests:** `pytest tests/integration/strategy/test_fleet_registration_lifecycle.py -v`

- [x] Replace the single `processor.process_join_fleet(...)` call with:
  ```python
  handler = processor.get_handler(OrderType.JOIN_FLEET)
  result = handler.execute_action_order(source_fleet, emp1, galaxy)
  # result.merged, result.cancelled already on OrderExecutionResult
  ```
- [x] Run targeted tests; confirm green.

**Notes:**

---

### Task 3.6: Migrate `tests/unit/strategy/engine/test_colonize_population.py` (6 sites + 1 import) [Simple]
**File:** `tests/unit/strategy/engine/test_colonize_population.py:22 (import), 180, 211, 245, 280, 310, 341`
**Tests:** `pytest tests/unit/strategy/engine/test_colonize_population.py -v`

- [x] Line 22: drop the `ColonizeResult` import. The import line currently reads `from game.strategy.engine.order_processor import OrderProcessor, ColonizeResult`. Change to `from game.strategy.engine.order_processor import OrderProcessor`.
- [x] Lines 180, 211, 245, 280, 310, 341 (6 call sites — corrected count from codex audit 2026-05-19; original cited 2 sites): migrate each `processor.process_colonize(...)` call per the Task 3.3 recipe.
- [x] Run targeted tests; confirm green.

**Notes:**

---

### Task 3.7: Migrate `tests/unit/strategy/engine/test_transfer_order.py` (7 sites + 1 import) [Simple]
**File:** `tests/unit/strategy/engine/test_transfer_order.py:15 (import), 196, 230, 262, 293, 327, 372, 414`
**Tests:** `pytest tests/unit/strategy/engine/test_transfer_order.py -v`

- [x] Line 15: drop the `TransferResult` import.
- [x] Strict call-site count (2026-05-19 audit): **7 `processor.process_transfer(...)` call sites** at lines 196, 230, 262, 293, 327, 372, 414. Line 103 docstring is narration only — update or drop. Migrate every call per the Task 3.4 recipe.
- [x] Run targeted tests; confirm green.

**Notes:**

---

### Task 3.8: Migrate `tests/unit/strategy/engine/test_order_processor_colonize.py` (7 sites) [Simple]
**File:** `tests/unit/strategy/engine/test_order_processor_colonize.py:105, 124, 157, 181, 213, 245, 283 (+ docstring at 102, 304)`
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_colonize.py -v`

- [x] Line 102 (docstring): mentions `ColonizeResult(colonized=False)`. Update the docstring to reflect `OrderExecutionResult(colonized=False)` (or whatever the test actually asserts after migration).
- [x] Migrate all 7 `proc.process_colonize(...)` calls in the file body (lines 105, 124, 157, 181, 213, 245, 283 — codex audit 2026-05-19 confirmed via live grep) per the Task 3.3 recipe.
- [x] Line 304: comment references "the legacy process_colonize delegate" — drop or update.
- [x] Run targeted tests; confirm green.

**Notes:** This test file's name (`test_order_processor_colonize`) targets the facade; consider whether to rename to `test_colonize_handler` post-migration since the testing is now of the handler, not the facade. Decision in `decisions.md`.

---

### Task 3.8a: Migrate `tests/unit/strategy/engine/test_fleet_order_transfer.py` (3 sites) [Simple]
**File:** `tests/unit/strategy/engine/test_fleet_order_transfer.py:97, 106, 115`
**Tests:** `pytest tests/unit/strategy/engine/test_fleet_order_transfer.py -v`

- [x] Added by codex audit 2026-05-19 — file was MISSING from the original Phase 3 inventory.
- [x] Strict call-site count (2026-05-19 audit): 3 `processor.process_transfer(...)` sites at lines 97, 106, 115. (Line 91 docstring is narration only.)
- [x] Migrate each call per the Task 3.4 recipe (use `processor.get_handler(OrderType.TRANSFER).execute_action_order(...)`).
- [x] Run targeted tests; confirm green.

**Notes:**

---

### Task 3.8b: Migrate `tests/unit/strategy/engine/test_order_processor_instant.py` (2 sites) [Simple]
**File:** `tests/unit/strategy/engine/test_order_processor_instant.py:247, 268 (+ docstring at 8, 234, 238, 254)`
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_instant.py -v`

- [x] Added by codex audit 2026-05-19 — file was MISSING from the original Phase 3 inventory.
- [x] Migrate both `proc.process_join_fleet(...)` calls (lines 247, 268) per the Task 3.5 recipe (use `processor.get_handler(OrderType.JOIN_FLEET).execute_action_order(...)`).
- [x] Update the file docstring (lines 8, 234) and test-name narration referring to `process_join_fleet` — switch to the unified handler vocabulary.
- [x] Run targeted tests; confirm green.

**Notes:**

---

### Task 3.8c: Migrate `tests/unit/strategy/engine/test_order_processor_transfer.py` (10 sites) [Medium]
**File:** `tests/unit/strategy/engine/test_order_processor_transfer.py:74, 112, 131, 169, 201, 231, 268, 302, 332, 369 (+ comment at 63, 67)`
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_transfer.py -v`

- [x] Added by codex audit 2026-05-19 — file was MISSING from the original Phase 3 inventory. **Second-largest single-file migration in Phase 3.**
- [x] Walk every site; migrate each `proc.process_transfer(...)` to the handler-direct path per Task 3.4 recipe.
- [x] Drop / update the section-header comments at lines 63 ("`process_transfer`: invalid params") and any other narration referring to the facade method.
- [x] Run targeted tests; confirm green.

**Notes:**

---

### Task 3.8d: Migrate `tests/unit/strategy/engine/test_process_colonize_validation.py` (6 sites) [Medium]
**File:** `tests/unit/strategy/engine/test_process_colonize_validation.py:201, 234, 271, 307, 386, 420`
**Tests:** `pytest tests/unit/strategy/engine/test_process_colonize_validation.py -v`

- [x] Added by codex audit 2026-05-19 — file was MISSING from the original Phase 3 inventory.
- [x] Strict call-site count (2026-05-19 audit): 6 `processor.process_colonize(...)` sites at lines 201, 234, 271, 307, 386, 420. (Lines 2-6 and 176, 320 are docstring/comment narration referring to `process_colonize()`; not call sites.)
- [x] Migrate each call per the Task 3.3 recipe.
- [x] Update the file docstring (lines 2-6) and section-header docstrings at lines 176, 320 — they narrate `process_colonize()` as the unit under test; rewrite to reference the handler.
- [x] Run targeted tests; confirm green.

**Notes:** Consider renaming the test file post-migration: `test_colonize_handler_validation.py` reflects the new subject. Decision in `decisions.md`.

---

### Task 3.8e: Migrate `tests/unit/strategy/test_engine_event_emission.py` (5 sites) [Simple]
**File:** `tests/unit/strategy/test_engine_event_emission.py:496, 528, 592, 991, 1047`
**Tests:** `pytest tests/unit/strategy/test_engine_event_emission.py -v`

- [x] Added by codex audit 2026-05-19 — file was MISSING from the original Phase 3 inventory.
- [x] Strict call-site count (2026-05-19 audit): 5 `processor.process_colonize(...)` sites at lines 496, 528, 592, 991, 1047. (Line 478 docstring is narration only.)
- [x] Migrate each call per the Task 3.3 recipe.
- [x] Update test docstrings at lines 477-478 (and any other narration that references `process_colonize`) — switch to the unified-handler vocabulary.
- [x] Run targeted tests; confirm green.

**Notes:** This file is event-emission focused; the migration should not change which events are emitted, only how the call is dispatched.

---

### Task 3.8f: Migrate `tests/unit/strategy/test_fleet_order_processor.py` (11 sites) [Medium]
**File:** `tests/unit/strategy/test_fleet_order_processor.py:82, 102, 116, 129, 196, 224, 245, 269, 520, 549, 577`
**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py -v`

- [x] Added by codex audit 2026-05-19 — file was MISSING from the original Phase 3 inventory. **Largest single-file migration in Phase 3 (11 sites).**
- [x] The file mixes `process_join_fleet` (sites at 82, 102, 116, 129) and `process_colonize` (sites at 196, 224, 245, 269, 520, 549, 577). Migrate each to the matching handler:
  - `process_join_fleet` → `processor.get_handler(OrderType.JOIN_FLEET).execute_action_order(...)`
  - `process_colonize` → `processor.get_handler(OrderType.COLONIZE).execute_action_order(...)`
- [x] Update test docstrings (lines 68, 88, 107, 122-123, 177, 205, 232, 253, 501, 531, 558) referencing `process_join_fleet` / `process_colonize` as the unit under test.
- [x] Run targeted tests; confirm green.

**Notes:** This file's name suggests it was the primary OrderProcessor test before the handler migration. Consider renaming to `test_fleet_order_handlers.py` post-migration; decision in `decisions.md`.

---

### Task 3.9: Review `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py` [Simple]
**File:** `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py:33, 37, 53-54`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py -v`

- [x] Read the file end-to-end. Per the docstring at lines 33, 37, 53-54, this file specifically tests the **facade** — i.e., the surface PROJ-454 is deleting.
- [x] **Decision**: delete the file outright (the surface is gone) OR rewrite to test the unified `execute_action_order` contract (which is then duplicated coverage of the per-handler tests). Recommendation: **delete**, document in `decisions.md`.
- [x] If deleting: `git rm tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py`.

**Notes:**

---

### Task 3.10: Delete the three legacy facade methods + three result dataclasses [Medium]
**File:** `game/strategy/engine/order_processor.py:39-58, 97-143`
**Tests:** Full sharded suite

- [x] **Pre-delete sanity check**: `git grep -nE "\.process_(join_fleet|colonize|transfer)\(" game/ tests/` should return ZERO call sites outside `game/strategy/engine/order_processor.py` (the lines being deleted). The 68 call sites enumerated in the "Live caller inventory" block at the top of this checklist should all be migrated by Tasks 3.3 through 3.8f. If any test caller remains, identify the file and migrate before deleting.
- [x] Also run `git grep -nE "process_join_fleet|process_colonize|process_transfer" game/ tests/` (no word boundary, captures docstring/comment references). Expected survivors after migration:
  - `game/strategy/engine/order_processor.py` — the lines being deleted (docstring lines 18, method defs at 97/108/123, plus the dataclass block)
  - `game/strategy/engine/handlers/base.py:423` — docstring reference; drop in Task 3.10 inline edit
  - `game/strategy/engine/order_handlers/{transfer,join_fleet,colonize}.py` — module docstrings describing the "lift-and-shift from `process_X`" history; either keep as historical narration or refresh
  - Archived projects (`Projects/archived_projects/`) — historical narration, no action
- [x] Also `git grep -nE "JoinFleetResult|ColonizeResult|TransferResult" game/ tests/` should return only internal references + archived.
- [x] Delete `order_processor.py:39-58` (the three dataclasses) and `:97-143` (the three facade methods).
- [x] Update the module docstring at `order_processor.py:1-20` — drop the narration about "Public surface kept for backward compatibility" + the dataclass listing.
- [x] Update any internal references to the deleted symbols (e.g., docstrings in nearby methods).
- [x] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.

**Notes:**

---

### Task 3.11: Verify F-B-017 closure [Simple]

- [x] `git grep -nE "\b(process_join_fleet|process_colonize|process_transfer)\(" game/ tests/` returns zero matches (excluding archived projects). This is the call-site grep — the strict signal that every caller migrated.
- [x] `git grep -nE "JoinFleetResult|ColonizeResult|TransferResult" game/ tests/` returns zero matches (excluding archived projects).
- [x] `OrderProcessor` class no longer has `process_join_fleet` / `process_colonize` / `process_transfer` methods.
- [x] Document closure in `decisions.md`: `2026-XX-XX | F-B-017 closed | Migrated 68 test call sites across 12 test files (count corrected by codex audit 2026-05-19 from the original ~15 sites / 7 files) to processor.get_handler(...).execute_action_order(...). Deleted 3 legacy facade methods + 3 typed result dataclasses (~50 LOC). All readers now consume OrderExecutionResult directly. | PROJ-454 Phase 3.`

**Notes:**

---

## Phase Completion Checklist

When all tasks above are checked off:

- [x] F-B-017 closed (documented in `decisions.md`)
- [x] Three legacy facade methods deleted from `order_processor.py`
- [x] Three legacy result dataclasses deleted from `order_processor.py`
- [x] All 68 test call sites across 12 test files migrated to the unified result path (count corrected by codex audit 2026-05-19 from the original `~15 sites / 7 files`)
- [x] `pytest tests/integration/colonization/ tests/integration/strategy/ tests/unit/strategy/ tests/unit/strategy/engine/ -q` green
- [x] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [x] Run `python Projects/scripts/validate_phase.py PROJ-454 3` — PASSED
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4

## Notes / Deferrals

- **No production callers** — the F-B-017 audit confirmed all live callers are tests. If a production caller surfaces during Task 3.1's re-discovery, the project's risk profile changes and the migration recipe may need to expose a public test-helper.
- **`OrderExecutionResult` field renames** — Phase 4 considers whether the `merged` / `cancelled` / `colonized` / `planet_name` / `amount_transferred` fields keep their current names or get refactored. Phase 3 does NOT change the field names.
