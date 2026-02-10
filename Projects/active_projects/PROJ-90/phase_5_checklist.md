# Phase 5: Documentation & Audit

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-90 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update ARCHITECTURE.md to reflect the cleaned state. Run final audit to verify all goals achieved.

---

## Tasks

### Task 5.1: Update ARCHITECTURE.md [Simple]
**File:** `docs/architecture/ARCHITECTURE.md`
**Tests:** N/A (documentation only)

- [ ] Update "Intentional Late Imports" section (lines 119-168):
  - Remove entries 1-3 under "Ship Module" (WeaponAbility, ModifierService, ShipSerializer — no longer late imports)
  - Update Ship Module description to note PROJ-90 cleaned up unnecessary late imports
  - Keep entries for Fleet and ShipInstance late imports (those remain intentional cross-layer)
- [ ] Add new section about `IPostBattleShip` protocol as the formal strategy-simulation boundary:
  - Explain the protocol's purpose
  - Reference `game/core/protocols.py`
  - Note which methods use it (`update_from_ship`, `update_from_battle_results`)
- [ ] Note the BattleConfig/BattleMode extraction to `game/simulation/battle_config.py`
- [ ] Note the registry loader extraction to `game/simulation/services/registry_loader.py`

**Notes:**

---

### Task 5.2: Final audit verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] `pytest tests/ -n 12` — all 7353+ tests pass
- [ ] Verify `game/core/registry.py` has no imports from `game.simulation`:
  `python -c "import ast; tree=ast.parse(open('game/core/registry.py').read()); print([n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module and 'simulation' in n.module])"`
  - Should print `[]`
- [ ] Verify `game/simulation/entities/ship.py` has no late imports:
  - No `import` statements inside method bodies (except stdlib like `copy` if any)
- [ ] Verify `game/simulation/managers/battle_state_manager.py` has no late imports
- [ ] Verify `game/strategy/data/ship_instance.py` no longer TYPE_CHECKING imports Ship
- [ ] Verify `game/strategy/data/fleet.py` no longer TYPE_CHECKING imports Ship

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] ARCHITECTURE.md is current and accurate
- [ ] All verification checks pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project is complete
- [ ] Update plan.md Verification section — check all boxes
