# Phase 1: Shared Role schema + RoleRegistry machinery

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-278 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the shared `Role` dataclass and `RoleRegistry` class in [game/core/roles.py](../../../game/core/roles.py). No callers wired yet — pure infrastructure with full test coverage.

---

## Tasks

### Task 1.1: Write tests for Role dataclass [Simple]
**File:** `tests/unit/core/test_role.py` (NEW)
**Tests:** `pytest tests/unit/core/test_role.py`

- [x] Test: `Role(id, display_name, description)` constructs cleanly with empty `vehicle_type_filter`
- [x] Test: `Role(...)` is frozen — assigning to a field raises
- [x] Test: Two roles with same id but different fields compare unequal (frozen + dataclass equality)
- [x] Test: `Role.id` is required positional / keyword

**Notes:** Wrote 9 tests total (added: explicit vehicle_type_filter, equality-when-equal, display_name/description required, tuple-not-list, import path). Confirmed tests fail with `ModuleNotFoundError: No module named 'game.core.roles'` — TDD red phase verified.

### Task 1.2: Implement Role dataclass [Simple]
**File:** `game/core/roles.py` (NEW)
**Tests:** `pytest tests/unit/core/test_role.py` — all pass

- [x] Add module docstring stating purpose
- [x] `@dataclass(frozen=True) class Role:` with fields per [design.md](design.md)
- [x] `__all__` exports `Role`
- [x] Verify all tests from 1.1 pass

**Notes:** Used `@dataclass(frozen=True, slots=True)` matching the convention from `combat_types.py::DamageContext`. All 10 tests pass.

### Task 1.3: Write tests for RoleRegistry — basic operations [Medium]
**File:** `tests/unit/core/test_role_registry.py` (NEW)
**Tests:** `pytest tests/unit/core/test_role_registry.py`

- [x] Test: empty registry — `all()` returns `[]`, `get("missing")` raises `KeyError`
- [x] Test: `load_from_file(tmp_json_with_2_roles, "base")` populates 2 roles, retrievable by id
- [x] Test: `load_from_file` with same id twice (different source_tag) — later source wins (precedence)
- [x] Test: `load_from_file` with malformed JSON raises clear error: chose `json.JSONDecodeError` (use `load_json_required` from `game.core.json_utils`)

**Notes:** Combined Tasks 1.3 + 1.4 into one comprehensive test file (`test_role_registry.py`). Added: contains-membership, vehicle_type_filter loading + default-empty, missing-file raises FileNotFoundError, `_`-prefixed JSON keys skipped (per project convention), `all()` returns sorted-by-id (deterministic). File format chosen: `{"roles": [{...}, ...]}` — list of dicts. Phase 2 will migrate the existing `data/design_roles.json` (which uses `{"roles": {id: {...}}}` dict-keyed shape) into this new format.

### Task 1.4: Write tests for RoleRegistry — runtime add + invalidation [Medium]
**File:** `tests/unit/core/test_role_registry.py`
**Tests:** `pytest tests/unit/core/test_role_registry.py`

- [x] Test: `RoleRegistry(allow_runtime_add=True).add_user_role(role)` succeeds, role retrievable
- [x] Test: `RoleRegistry(allow_runtime_add=False).add_user_role(role)` raises `RoleRegistryReadOnlyError`
- [x] Test: `register_invalidation_callback(cb)` then `add_user_role` — callback fires exactly once
- [x] Test: multiple callbacks fire on add
- [x] Test: callback exceptions don't prevent the add — DECIDED: callbacks that raise are swallowed (logged), the add succeeds, subsequent callbacks still fire. Rationale: a misbehaving subscriber should not block correct registration. This matches the "graceful degradation" pattern from event_logging.py.

**Notes:** Tests confirmed failing with `ImportError: cannot import name 'RoleRegistry'` — TDD red phase verified. Added bonus tests: load_from_file does NOT fire invalidation (only runtime add does), runtime add overrides loaded role (highest precedence), callbacks fire once per add not once total.

### Task 1.5: Implement RoleRegistry [Medium]
**File:** `game/core/roles.py`
**Tests:** `pytest tests/unit/core/test_role_registry.py` — all pass

- [x] Define `RoleRegistryReadOnlyError(Exception)` with helpful message
- [x] `class RoleRegistry` per [design.md](design.md) signature
- [x] `load_from_file(path, source_tag)` — uses `game.core.json_utils.load_json_required` for loading
- [x] `get(id) -> Role` raising `KeyError` on miss (chose plain `KeyError` over domain-specific — consistent with dict-like API)
- [x] `all() -> List[Role]` — sorted by id for determinism
- [x] `add_user_role(role)` — checks flag, inserts, fires callbacks
- [x] `register_invalidation_callback(cb)` — appends to list
- [x] Update `__all__` to export `RoleRegistry`, `RoleRegistryReadOnlyError`
- [x] Verify: all 30 tests pass (10 Role + 20 RoleRegistry)

**Notes:** Added `__contains__` for natural `"id" in registry` membership testing. Used keyword-only `allow_runtime_add` so caller intent is explicit at construction sites. JSON loading uses `load_json_required` (not `load_json`) so missing/malformed files raise loudly — these are critical config files. Underscore-prefixed keys in role dicts are skipped (per project memory: same convention as components.json formula parsing).

### Task 1.6: Update game.core public API [Simple]
**File:** `game/core/__init__.py`
**Tests:** `pytest tests/unit/core/`

- [x] Add to `__all__`: `Role`, `RoleRegistry`, `RoleRegistryReadOnlyError`
- [x] Add re-exports from `game.core.roles`
- [x] Update `docs/01_ARCHITECTURE.md` "game.core" exports section with the new entries
- [x] Update `docs/01_ARCHITECTURE.md` package directory map with `roles.py` row
- [x] Update export count: 42 → 45

**Notes:** Also added a docstring section in `game/core/__init__.py` documenting the new exports (matching the style of other Public API sections). Full `tests/unit/core/` suite (990 tests) passes — no regressions.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/core/` passes (990 tests, all green)
- [x] No callers of the new module exist yet — grep `game.core.roles` returns only `game/core/__init__.py` (re-export) and the two test files
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
