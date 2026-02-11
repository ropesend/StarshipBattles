# Phase 7: Audit and Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-106 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Final audit to verify all architecture layer violations from the sweep have been addressed, and perform a comprehensive cross-layer import scan.

---

## Context

Phases 1-6 addressed all CRITICAL and MAJOR findings from the architecture sweep that are in-scope for PROJ-106. This phase verifies everything is clean and documents any remaining known issues.

### Findings NOT addressed (out of scope):
- **ADR-UI2-006** (Inconsistent DI patterns) -- MINOR, deferred to future DI standardization project
- **ADR-UI1-006** (Law of Demeter violations, 27 files) -- MINOR, large scope, deferred
- **ADR-UI1-007** (Strategy data objects in UI) -- MINOR, requires DTO extraction, deferred
- **ADR-UI2-009** (TYPE_CHECKING not isolated in BattleUIService) -- INFO, acceptable trade-off
- **ADR-UI2-010** (BattleOrchestrator cross-layer) -- INFO, intentional design

### God class findings (out of scope, covered by other projects):
- ADR-SIM-003/004, ADR-FND-002/003/004, ADR-UI1-003/004/005, ADR-STR-001/002/003/004

---

## Tasks

### Task 7.1: Cross-Layer Import Audit [Medium]

Perform a systematic scan of all layer boundaries:

**Simulation Layer (must not import from UI, AI, or Strategy):**
- [ ] Grep for `from game.ui` in `game/simulation/` -- expect ZERO (excluding TYPE_CHECKING)
- [ ] Grep for `from game.ai` in `game/simulation/` -- expect ONLY in `factories/ai_factory.py`
- [ ] Grep for `from game.strategy` in `game/simulation/` -- expect ZERO
- [ ] Grep for `import pygame` in `game/simulation/` -- expect ZERO after Phase 1

**Core Layer (must not import from any other layer):**
- [ ] Grep for `from game.simulation` in `game/core/` -- expect ZERO
- [ ] Grep for `from game.strategy` in `game/core/` -- expect ZERO
- [ ] Grep for `from game.ui` in `game/core/` -- expect ZERO
- [ ] Grep for `from game.ai` in `game/core/` -- expect ZERO

**Research Layer (must not import from UI):**
- [ ] Grep for `from game.ui` in `game/research/` -- expect ZERO after Phase 5

**AI Layer (must not import from UI):**
- [ ] Grep for `from game.ui` in `game/ai/` -- expect ZERO

**Strategy Layer (must not import from UI or AI):**
- [ ] Grep for `from game.ui` in `game/strategy/` -- expect ZERO
- [ ] Grep for `from game.ai` in `game/strategy/` -- expect ZERO

**UI Layer (should not import from AI after Phase 3):**
- [ ] Grep for `from game.ai` in `game/ui/` -- expect ONLY in `orchestration/battle_orchestrator.py` (intentional)

---

### Task 7.2: Private Attribute Cross-Module Audit [Simple]

- [ ] Grep for `\._registries` access outside of ship.py and its delegates -- expect ZERO after Phase 1
- [ ] Grep for `\._hp_ratio_dirty` access outside of component module -- expect ZERO after Phase 1
- [ ] Grep for `\._resources` access on ResourceRegistry outside resource_manager.py -- expect ZERO after Phase 1

---

### Task 7.3: Document Remaining Known Issues [Simple]
**File:** `Projects/active_projects/PROJ-106/decisions.md`

- [ ] Add entries for each deferred finding with rationale
- [ ] ADR-UI2-006: "Deferred -- DI standardization is a separate project"
- [ ] ADR-UI1-006: "Deferred -- 27-file Law of Demeter cleanup is out of scope"
- [ ] ADR-UI1-007: "Deferred -- Strategy DTO extraction requires broader design work"
- [ ] Note any new issues discovered during audit

---

### Task 7.4: Final Full Test Suite Run [Simple]

- [ ] Run: `pytest tests/ -n 12`
- [ ] Verify 8164+ tests pass
- [ ] Verify 0 new failures
- [ ] Verify no new warnings from import changes

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Cross-layer import audit passes all checks
- [ ] Private attribute audit passes all checks
- [ ] Deferred findings documented in decisions.md
- [ ] Full test suite passes: `pytest tests/ -n 12` (8164+ tests)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to reflect project complete
