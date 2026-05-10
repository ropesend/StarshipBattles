# PROJ-250 Phase 1: Document and Clean Up

> **BEFORE MARKING THIS PHASE COMPLETE:**
> Run: `pytest tests/unit/simulation/ -x`

## Objective
Document retreat priority logic, remove dead BattleConfig.isolated field.

## Status: Not Started

---

### Task 1.1: Document _retreat_allowed() Priority [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** N/A (documentation only)

- [ ] Lines 393-401: Expand docstring to explicitly state:
  ```
  Priority: Mode handler provides the default per battle mode.
  BattleConfig.allow_retreat=True can OVERRIDE to enable retreat
  in modes that normally deny it (e.g., manual battles).
  Config cannot DISABLE retreat when mode handler allows it.
  ```
- [ ] Check if `_reinforcements_allowed()` has the same OR pattern — apply same documentation

### Task 1.2: Document BattleConfig.allow_retreat [Simple]
**File:** `game/simulation/battle_config.py`
**Tests:** N/A (documentation only)

- [ ] Line 65: Add docstring to `allow_retreat` explaining override semantics:
  ```python
  allow_retreat: bool = False  # Override: enables retreat even in modes that deny it by default
  ```
- [ ] Same for `allow_reinforcements` if it exists

### Task 1.3: Remove Dead isolated Field [Simple]
**File:** `game/simulation/battle_config.py`
**Tests:** `pytest tests/unit/simulation/ -x`

- [ ] Line 75: Remove `isolated: bool = True` and its comment
- [ ] Search for `config.isolated` or `.isolated` in tests — remove any stale references
- [ ] Also check if `should_clone_ships()` on mode handlers is called anywhere — if not, document it as dead code too
- [ ] Run tests: `pytest tests/unit/simulation/ -x`

**Notes:**
