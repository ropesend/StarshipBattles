# Phase 3: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run targeted tests: `pytest tests/unit/simulation/combat/test_combat_events.py -x`
> 2. Confirm `python -c "from game.simulation.combat.combat_events import CombatEvent; from typing import get_type_hints; get_type_hints(CombatEvent); print('OK')"` prints `OK`.

**Status:** Complete
**Objective:** Restore the `DamageContext` annotation binding in `combat_events.py:78` that was orphaned by the Phase 2 deletion of the re-export at line 62. Use the file's existing `TYPE_CHECKING` pattern at lines 28-30 to avoid re-introducing a runtime import.

---

## Tasks

### Task 3.1: Restore `DamageContext` annotation binding
**File:** `game/simulation/combat/combat_events.py`
**Tests:** `pytest tests/unit/simulation/combat/test_combat_events.py -x`

- [x] Add `from game.core.combat_types import DamageContext` to the existing `if TYPE_CHECKING:` block at lines 28-30
- [x] Change `context: Optional[DamageContext] = None` at line 78 to `context: Optional["DamageContext"] = None` (forward-reference string, since the import is TYPE_CHECKING-only)
- [x] Verify `typing.get_type_hints(CombatEvent)` no longer raises `NameError`

### Phase Verification
- [x] `pytest tests/unit/simulation/combat/test_combat_events.py -x` passes
- [x] `typing.get_type_hints(CombatEvent)` smoke probe succeeds
- [x] No new runtime imports introduced (TYPE_CHECKING import only)

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table to include Phase 3 as Complete

_Source: Codex audit at `AgentCoordination/Scratchpad/Consult/20260523T053310Z_audit-PROJ-484/response.md`. Verification table at `findings/audit_verification.md`._
