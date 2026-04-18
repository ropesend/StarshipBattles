# Phase 1: Shared Role schema + RoleRegistry machinery

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-278 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the shared `Role` dataclass and `RoleRegistry` class in [game/core/roles.py](../../../game/core/roles.py). No callers wired yet — pure infrastructure with full test coverage.

---

## Tasks

### Task 1.1: Write tests for Role dataclass [Simple]
**File:** `tests/unit/core/test_role.py` (NEW)
**Tests:** `pytest tests/unit/core/test_role.py`

- [ ] Test: `Role(id, display_name, description)` constructs cleanly with empty `vehicle_type_filter`
- [ ] Test: `Role(...)` is frozen — assigning to a field raises
- [ ] Test: Two roles with same id but different fields compare unequal (frozen + dataclass equality)
- [ ] Test: `Role.id` is required positional / keyword

**Notes:**

### Task 1.2: Implement Role dataclass [Simple]
**File:** `game/core/roles.py` (NEW)
**Tests:** `pytest tests/unit/core/test_role.py` — all pass

- [ ] Add module docstring stating purpose
- [ ] `@dataclass(frozen=True) class Role:` with fields per [design.md](design.md)
- [ ] `__all__` exports `Role`
- [ ] Verify all tests from 1.1 pass

**Notes:**

### Task 1.3: Write tests for RoleRegistry — basic operations [Medium]
**File:** `tests/unit/core/test_role_registry.py` (NEW)
**Tests:** `pytest tests/unit/core/test_role_registry.py`

- [ ] Test: empty registry — `all()` returns `[]`, `get("missing")` raises `KeyError`
- [ ] Test: `load_from_file(tmp_json_with_2_roles, "base")` populates 2 roles, retrievable by id
- [ ] Test: `load_from_file` with same id twice (different source_tag) — later source wins (precedence)
- [ ] Test: `load_from_file` with malformed JSON raises clear error (which exception type? decide)

**Notes:**

### Task 1.4: Write tests for RoleRegistry — runtime add + invalidation [Medium]
**File:** `tests/unit/core/test_role_registry.py`
**Tests:** `pytest tests/unit/core/test_role_registry.py`

- [ ] Test: `RoleRegistry(allow_runtime_add=True).add_user_role(role)` succeeds, role retrievable
- [ ] Test: `RoleRegistry(allow_runtime_add=False).add_user_role(role)` raises `RoleRegistryReadOnlyError`
- [ ] Test: `register_invalidation_callback(cb)` then `add_user_role` — callback fires exactly once
- [ ] Test: multiple callbacks fire on add
- [ ] Test: callback exceptions don't prevent the add (or DO — decide)

**Notes:**

### Task 1.5: Implement RoleRegistry [Medium]
**File:** `game/core/roles.py`
**Tests:** `pytest tests/unit/core/test_role_registry.py` — all pass

- [ ] Define `RoleRegistryReadOnlyError(Exception)` with helpful message
- [ ] `class RoleRegistry` per [design.md](design.md) signature
- [ ] `load_from_file(path, source_tag)` — uses `game.core.json_utils` for loading
- [ ] `get(id) -> Role` raising `KeyError` (or domain-specific) on miss
- [ ] `all() -> List[Role]` — sorted by id for determinism
- [ ] `add_user_role(role)` — checks flag, inserts, fires callbacks
- [ ] `register_invalidation_callback(cb)` — appends to list
- [ ] Update `__all__` to export `RoleRegistry`, `RoleRegistryReadOnlyError`

**Notes:**

### Task 1.6: Update game.core public API [Simple]
**File:** `game/core/__init__.py`
**Tests:** `pytest tests/unit/core/`

- [ ] Add to `__all__`: `Role`, `RoleRegistry`, `RoleRegistryReadOnlyError`
- [ ] Add re-exports from `game.core.roles`
- [ ] Update `docs/01_ARCHITECTURE.md` "game.core" exports section with the new entries

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/core/` passes
- [ ] No callers of the new module exist yet (verify via grep — Phase 2 wires `design_role`)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
