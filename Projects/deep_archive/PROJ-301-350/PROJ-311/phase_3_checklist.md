# Phase 3: Backfill annotations (per layer)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-311 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Annotate every unannotated function/method in `game/`, in waves by subsystem. After each wave, re-audit and report.

**Prerequisites:** Phase 2 complete — audit script and CSV exist.

---

## Per-wave methodology

For each wave (subsystem):
1. Filter the CSV to functions in that subsystem
2. For each file in the subsystem, read the file and add return annotations
3. **Modern syntax only:** `T | None`, `list[T]`, etc.
4. If a function has no `return` statement, annotate `-> None`
5. If forward references are needed, add `from __future__ import annotations` at the top
6. If the actual return type is `Any` or genuinely unclear, annotate `Any` honestly — don't lie
7. Run targeted tests for the subsystem
8. Re-run the audit script — confirm the count for this subsystem dropped to (near) zero
9. Commit the wave

---

## Sub-phases

### Sub-phase 3.1: Wave A — Core (`game/core/`) [Simple]
- [ ] Annotate all unannotated non-dunder functions in `game/core/`
- [ ] `from __future__ import annotations` added to files that need it
- [ ] `pytest tests/unit/core/` passes
- [ ] Re-audit `game/core/` — coverage ≥ 95%
- [ ] Commit

**Notes:**

---

### Sub-phase 3.2: Wave B — Simulation (`game/simulation/`) [Medium]
- [ ] Annotate all unannotated non-dunder functions in `game/simulation/`
- [ ] `pytest tests/unit/simulation/ tests/integration/simulation/` passes (subset of full suite for fast iteration)
- [ ] Re-audit `game/simulation/` — coverage ≥ 95%
- [ ] Commit

**Notes:** Watch for `Ship`, `BattleSpec`, `BattleOutcome` types — heavily reused. Use the existing concrete types or relevant `IShip*` protocols.

---

### Sub-phase 3.3: Wave C — Strategy (`game/strategy/`) [Medium]
- [ ] Annotate all unannotated non-dunder functions in `game/strategy/`
- [ ] `pytest tests/unit/strategy/ tests/integration/strategy/` passes
- [ ] Re-audit `game/strategy/` — coverage ≥ 95%
- [ ] Commit

**Notes:** Largest layer in absolute count. Consider sub-waves if too big for one commit (e.g., strategy/data → strategy/engine → strategy/facade → strategy/services → strategy/validation).

---

### Sub-phase 3.4: Wave D — AI (`game/ai/`) [Simple]
- [ ] Annotate all unannotated non-dunder functions in `game/ai/`
- [ ] `pytest tests/unit/ai/` passes
- [ ] Re-audit `game/ai/` — coverage ≥ 95%
- [ ] Commit

**Notes:**

---

### Sub-phase 3.5: Wave E — UI (`game/ui/`) [Medium]
- [ ] Annotate all unannotated non-dunder functions in `game/ui/`
- [ ] `pytest tests/unit/ui/` passes
- [ ] Re-audit `game/ui/` — coverage ≥ 95%
- [ ] Commit

**Notes:** Largest absolute volume. Many UI callbacks return `-> None`. Consider sub-waves: `ui/screens/`, `ui/panels/`, `ui/widgets/`, `ui/services/`.

---

### Sub-phase 3.6: Anything else [Simple]
- [ ] Run audit on the whole of `game/`
- [ ] If anything is missed (top-level scripts, miscellaneous modules), annotate
- [ ] Re-audit overall — coverage ≥ 95%

**Notes:**

---

### Sub-phase 3.7: Smoke test [Medium]
- [ ] Full sharded suite (`python Tools/test_sharded/test_sharded.py`)
- [ ] Confirm 15389+ baseline
- [ ] Investigate any new failures (likely a wrong annotation causing `inspect.signature` or pydantic to choke)

**Notes:**

---

## Phase Completion Checklist
- [ ] All waves complete
- [ ] Overall return-annotation coverage in `game/` ≥ 95%
- [ ] Full sharded suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 4)
