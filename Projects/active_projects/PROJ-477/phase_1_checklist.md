# Phase 1: Guard #3 scaffold (ratchet from day one) + session-guard dynamic-`getattr` hardening

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-477 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Stand up the third static guard (property-read surface) GREEN with a full current
allowlist so it blocks net-new `scene.galaxy`/`empires`/`systems` bypasses during the migration,
and harden the session guard for the dynamic `getattr(obj,"session")` hole. No production behavior
changes this phase.

> **PRE-REQ:** PROJ-475 has landed; consumer inventory re-scanned against post-475 live code.

---

## Tasks

### Task 1.1: Property-read static guard scaffold [Complex]
**File:** `tests/static_guards/test_facade_read_path_property_guard.py` (NEW)
**Tests:** `pytest tests/static_guards/test_facade_read_path_property_guard.py`

- [ ] Mirror `test_facade_read_path_session_guard.py` structure: `_ui_python_files()`, `if TYPE_CHECKING:` skip, parametrized per-file scan, `pytest.fail` with a fix-pointer message.
- [ ] Matcher `_matched_property_read(node)` recognizing **Load-context** `<expr>.scene.{galaxy,empires,systems}`, `<expr>._screen.{...}`, `r.{...}`, `screen.{...}` (only in `strategy_screen_*` modules), and `self.galaxy` only in `strategy_screen.py`. Returns the matched attr-path tail.
- [ ] Explicitly DO NOT match generic `self.galaxy`/`self.empires`/`self.systems` (false-positives on injected locals — see design.md). Confirm `ast.Store` context is excluded.
- [ ] `_PROPERTY_READ_ALLOWLIST: frozenset[tuple[str, str]]` seeded with EVERY current live consumer (Key Files table) so the directory scan is GREEN at introduction. Each entry carries a `# PROJ-477 PhaseN migration target` reason.
- [ ] Positive-control test `test_property_read_matcher_recognises_scoped_forms`: pins that `scene.galaxy`, the NESTED `c.scene.galaxy` / `self.scene.galaxy` shapes (POST-FLESH B4 — most live matches are nested), `r.empires`, `_screen.systems` match and that `self.galaxy` in `build_queue_controller`-style code and a `.galaxy =` store do NOT.
- [ ] Verify: `pytest tests/static_guards/test_facade_read_path_property_guard.py` GREEN (allowlist absorbs all current reads).

**Notes:**

---

### Task 1.2: Harden session guard for dynamic `getattr(..., "session")` [Medium]
**File:** `tests/static_guards/test_facade_read_path_session_guard.py`
**Tests:** `pytest tests/static_guards/test_facade_read_path_session_guard.py`

- [ ] Extend `_matched_session_read` (or add a sibling matcher) to flag `getattr(<expr>, "session")` / `getattr(<expr>, '_session')` calls — the form `system_tree_panel.py:418-425` uses.
- [ ] Add an allowlist-with-reason entry for `system_tree_panel.py` (`getattr.session` → PROJ-477 Phase 3 migration target) so the guard stays GREEN now.
- [ ] Add a positive-control test asserting the new matcher catches `getattr(scene, "session")` and that PROJ-475's existing forms still match.
- [ ] Verify: `pytest tests/static_guards/test_facade_read_path_session_guard.py` GREEN.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Both guard test files GREEN; full sharded suite unaffected
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
