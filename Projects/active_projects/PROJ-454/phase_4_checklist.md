# PROJ-454 Phase 4: Refresh `OrderExecutionResult` legacy-field framing (F-B-018)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-454 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Close F-B-018 by refreshing the framing of the 5 "legacy fields" on `OrderExecutionResult`. With Phase 3 done, these fields are no longer legacy — they're the live unified-result surface. Drop the "legacy field" inline comments and the docstring narration about typed-result reshaping. Optionally shrink the dataclass if any field is now demonstrably unused.

**Cross-bucket file-ownership rule:** This phase touches only `game/strategy/engine/order_handlers/base.py` (the `OrderExecutionResult` dataclass). Do NOT touch any file PROJ-452 / PROJ-453 / PROJ-455 owns.

**Source-of-truth findings:** [`findings/PROJ-454_findings.md`](findings/PROJ-454_findings.md) — read F-B-018's full text.

---

## Tasks

### Task 4.1: Audit field usage post-Phase-3 [Simple]
**File:** Read-only

- [ ] After Phase 3 deletes the facade reshape, audit which of the 5 "legacy fields" are still set + read:
  ```bash
  for field in merged cancelled colonized planet_name amount_transferred; do
    echo "=== $field ==="
    git grep -n "OrderExecutionResult.*$field\|\.${field}\b" game/strategy/engine/order_handlers/ tests/
  done
  ```
- [ ] For each field, record:
  - Where the field is SET (which handler's `execute_action_order` populates it).
  - Where the field is READ (which test or production caller reads `result.<field>`).
- [ ] Identify any field that's set-but-never-read or read-but-never-set. Those are deletion candidates.

**Notes:**

---

### Task 4.2: Drop the "legacy field" inline comments [Simple]
**File:** `game/strategy/engine/order_handlers/base.py:50-55`

- [ ] Read the current dataclass at lines 36-56. Field declarations look like:
  ```python
  merged: bool = False              # JoinFleet legacy field
  cancelled: bool = False           # JoinFleet legacy field
  colonized: bool = False           # Colonize legacy field
  planet_name: Optional[str] = None  # Colonize legacy field
  amount_transferred: int = 0       # Transfer legacy field
  ```
- [ ] **GREEN**: Drop the `# JoinFleet legacy field` / `# Colonize legacy field` / `# Transfer legacy field` inline comments. The fields stay; only the trailing comments go.
- [ ] No test changes required — this is a comment-only edit.

**Notes:**

---

### Task 4.3: Refresh the class docstring at lines 36-45 [Simple]
**File:** `game/strategy/engine/order_handlers/base.py:36-45`

- [ ] Current docstring text references the deleted legacy result types:
  > "Internal handlers work with this single type; the `OrderProcessor` facade reshapes it back into the legacy typed result dataclasses (`JoinFleetResult`, `ColonizeResult`, `TransferResult`, `SuperweaponResult`) for backward compatibility with existing characterization tests."
- [ ] **GREEN**: Rewrite the docstring to describe the current unified contract:
  ```python
  """Unified result type for `IOrderHandler.execute_action_order`.
  
  All concrete handlers populate the fields they care about; readers
  consume the unified result directly. The class carries per-handler
  fields side by side because the runtime overhead is negligible and
  per-handler payload subclasses would complicate caller ergonomics.
  
  SuperweaponResult is still produced by SuperweaponOrderProcessor
  (separate facade) and is NOT this type.
  """
  ```
- [ ] Update any imports affected (none expected).

**Notes:**

---

### Task 4.4: Decide on field shrinkage [Simple]

- [ ] From the Task 4.1 audit, identify any field that's set-but-never-read or read-but-never-set after Phase 3.
- [ ] **Decision**:
  - **Keep all 5 fields** if every field has a real setter + real reader. Document in `decisions.md`: `2026-XX-XX | F-B-018 fields retained | All 5 unified-result fields have live producers and consumers post-Phase-3. Flat unified result preferred over per-handler subclasses per Codex r4 redesign. | PROJ-454 Phase 4.`
  - **Drop unused fields** if any are demonstrably dead. Update the dataclass, run targeted tests + sharded.
- [ ] Apply the decision.

**Notes:** Per Codex r4 redesign, the recommendation is **keep flat**. The 5-field overhead is small; per-handler subclasses would force every caller to know which subclass it's reading.

---

### Task 4.5: Verify F-B-018 closure [Simple]

- [ ] `git grep -n "legacy field" game/strategy/engine/order_handlers/base.py` returns zero matches.
- [ ] `OrderExecutionResult`'s docstring no longer mentions `JoinFleetResult` / `ColonizeResult` / `TransferResult`.
- [ ] If fields were dropped, the deletion landed cleanly across all callers.
- [ ] Document closure in `decisions.md` (Task 4.4 already wrote the row; verify it's there).

**Notes:**

---

## Phase Completion Checklist

When all tasks above are checked off:

- [ ] F-B-018 closed (documented in `decisions.md`)
- [ ] "Legacy field" inline comments removed
- [ ] `OrderExecutionResult` docstring refreshed
- [ ] Field shrinkage decision documented (and applied if any field was dropped)
- [ ] `pytest tests/unit/strategy/engine/ -q` green
- [ ] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-454 4` — PASSED
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project complete; awaiting end-of-project Codex consult per the standing workflow"

## Notes / Deferrals

- **`SuperweaponResult`** — out of PROJ-454 scope. The unified-result narrative doesn't touch it; SuperweaponOrderProcessor uses a separate facade.
- **Per-handler payload subclasses** — explicitly out of scope per Codex r4 redesign. If a future maintainer wants subclasses, it's a fresh project.
- **No new tests in Phase 4** — this is a documentation + decision phase. The Phase 3 tests already verify the dataclass behaviour end-to-end.
