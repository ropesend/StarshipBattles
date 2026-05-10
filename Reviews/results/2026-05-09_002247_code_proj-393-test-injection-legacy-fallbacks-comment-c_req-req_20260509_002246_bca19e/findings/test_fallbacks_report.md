# PROJ-393 Review: Phase 2 Test-Fallback Deletions & IScene Migration

**Reviewer:** OpenCode  
**Date:** 2026-05-09  
**Scope:** LEG-03-004/005/006/007 + LEG-02-002  
**Files audited:** 9 production files, 6 test files, 1 protocol file, 1 fixture file

---

## Focus Area 1: Phase 2 test-fallback deletions — test-side audit thoroughness

### LEG-03-006: BuildQueueDragHandler on_remove_from_queue fallback

**Verdict: Clean deletion, all tests pass the required callback.**

| Check | Status | Evidence |
|---|---|---|
| Fallback branch deleted | CONFIRMED | `game/ui/panels/build_queue_drag_handler.py:208` calls `self._on_remove_from_queue(idx)` without any `if None: return` guard |
| `_on_remove_from_queue` is required | CONFIRMED | `build_queue_drag_handler.py:53` — `on_remove_from_queue: 'RemoveFromQueueCallback'` with no default |
| All tests pass `on_remove_from_queue=` | CONFIRMED — 3/3 | See below |

**Test instantiation audit:**

| Test file | Line | Passes `on_remove_from_queue=`? |
|---|---|---|
| `tests/unit/ui/panels/test_build_queue_drag_handler.py` | 90-96 | Yes — `on_remove_from_queue=on_remove` (MagicMock) |
| `tests/integration/ui/build_queue_screen/test_drag_handler_multi_queue.py` | 27-34 | Yes — `on_remove_from_queue=MagicMock()` |
| `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` | 394-401 | Yes — `on_remove_from_queue=MagicMock()` |

**No tests instantiate BuildQueueDragHandler without `on_remove_from_queue`.**

**No tests trigger the deleted fallback path** (which would now be a `TypeError`-on-missing-arg since the parameter is required). The deleted tests (`test_drag_from_queue_falls_back_to_direct_pop_without_callback`, `test_motion_above_threshold_legacy_pops_directly_when_no_callback`) were properly removed alongside the production code.

---

#### MINOR: Vestigial `with_remove_callback` kwarg in `_make_handler` helper

**File:** `tests/unit/ui/panels/test_build_queue_drag_handler.py:69`  
**Severity:** MINOR  
**Finding:** The `_make_handler` helper accepts `with_remove_callback: bool = True` but its only purpose per the docstring is "ABI parity with existing call sites that pass True." The function unconditionally creates and passes `on_remove=MagicMock()` at line 88 and passes it at line 96 regardless of the kwarg value. The kwarg has no effect on behavior — when `False`, the callback mock is still created and passed (line 88 still runs).

**Evidence:** Lines 69-97 — `with_remove_callback` is read nowhere in the function body; the `on_remove` callback is always created and always passed.

**Why it matters:** Dead API surface in test helpers. The docstring claims "PROJ-393 made `on_remove_from_queue` a required arg; the `with_remove_callback=False` flavor that legacy tests used to exercise the construction-queue direct-pop fallback is gone." The kwarg should be removed since it serves no purpose and could mislead future readers into thinking there's still a no-callback path.

---

### LEG-03-007: EmpireBuildQueueWindow facade fallback

**Verdict: Clean deletion, but test suite never exercises the real constructor.**

| Check | Status | Evidence |
|---|---|---|
| `facade` is required | CONFIRMED | `game/ui/screens/empire_build_queue_window.py:163` — `facade: Any` is keyword-only with no default |
| Fallback branch deleted | CONFIRMED | `empire_build_queue_window.py:402-404` — comment explicitly states "PROJ-393 deletes the legacy 'no facade injected' fallback that mutated `source.construction_queue` in-place." Only path is `self._facade.handle_command(cmd)` at line 420 |
| Static guard verifies `session=` not accepted | CONFIRMED | `tests/static_guards/test_facade_bypass_guard.py:38` — `GUARDED_CONSTRUCTORS = {"BuildQueueScreen", "EmpireBuildQueueWindow"}` |

**Test instantiation audit:**

No test instantiates `EmpireBuildQueueWindow` through its real `__init__`. All tests either:
1. Bypass `__init__` via `patch.object(EmpireBuildQueueWindow, '__init__', lambda self, *a, **kw: None)` + `__new__` (`test_empire_build_queue_window.py:63-65`)
2. Patch the class entirely with MagicMock (`test_build_queue_windows.py:74`)

---

#### MAJOR: No test ever calls `EmpireBuildQueueWindow(...)` through the real constructor

**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py:63-65`  
**Severity:** MAJOR  
**Finding:** The entire test suite bypasses `EmpireBuildQueueWindow.__init__`. If someone inadvertently reverts `facade` from a required parameter to optional (e.g., adds `= None` default), no test would catch it via a constructor-invocation error. The static guard (`test_facade_bypass_guard.py`) only checks for `session=` text references in the source file, not for the `facade` parameter's optionality.

**Evidence:**
- `_make_window()` at line 63-65: `with patch.object(EmpireBuildQueueWindow, '__init__', lambda self, *a, **kw: None): win = EmpireBuildQueueWindow.__new__(EmpireBuildQueueWindow)` — completely bypasses parameter validation.
- All other test files patch `EmpireBuildQueueWindow` with `MagicMock()` instead of instantiating it.

**Why it matters:** The constructor signature is not validated by any test. A regression that makes `facade` optional would go undetected, which is exactly the pattern PROJ-393 aimed to eliminate.

**Recommendation:** Add at least one constructor-validation test that calls `EmpireBuildQueueWindow(...)` with all required args (even if the window is immediately killed), or add a `test_constructor_requires_facade` test that asserts `TypeError` is raised when `facade` is omitted.

---

#### MINOR: Test fake-facade is an inline mock that reimplements command handler logic

**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py:110-132`  
**Severity:** MINOR  
**Finding:** The `_fake_handle_command` closure at lines 110-130 reimplements `AddToConstructionQueueCommand` handler logic — it knows about `cmd.queue_id`, `cmd.entity_id`, `cmd.category`, and mutates `src.construction_queue` in-place. This is an inline mock, not a clean fixture. While it does respect the facade contract (calls `handle_command`, returns mock with `is_valid`), it tightly couples the test to `AddToConstructionQueueCommand` internals.

**Why it matters:** If the command handler's dispatch logic changes, this mock silently diverges. However, this is standard unit-test mock practice and the behavior tested (item ends up in `source.construction_queue`) would still be verified by integration tests. Severity is MINOR rather than MAJOR because the mock correctly verifies the window constructs and dispatches the right command.

---

### LEG-03-004/005: PlanetOrderValidator component_key fallbacks

**Verdict: Clean deletion, no caller can pass None.**

| Check | Status | Evidence |
|---|---|---|
| `component_key` is keyword-only `str` | CONFIRMED | `planet_order_validator.py:31` — `component_key: str` (not Optional); same at line 75 |
| Fallback branches deleted | CONFIRMED | No `if component_key is None:` guards in the validator |
| Handler guards against None | CONFIRMED | `planet_command_handlers.py:74-75` — `if not cmd.component_key: return ValidationResult.error(...)` before calling validator |
| Fleet command router guards against None | CONFIRMED | `strategy_fleet_command_router.py:277` — `if not target_facility_id or not target_component_key: return` |

**Indirect call-path analysis:**

All call paths to `validate_activate_ability` / `validate_deactivate_ability`:

| Caller | File:Line | Guards `component_key=None`? |
|---|---|---|
| `IssuePlanetOrderCommandHandler.execute()` | `planet_command_handlers.py:76-78` | Yes — line 74-75 returns error before call |
| `IssuePlanetOrderCommandHandler.execute()` | `planet_command_handlers.py:85-87` | Yes — line 83-84 returns error before call |

The `IssuePlanetOrderCommand.component_key` field is `Optional[str] = None` (`commands/__init__.py:421`), which means `None` **can** enter the command handler. The handler's guard catches it. No caller bypasses the handler to call the validator directly.

---

#### MINOR: Type contract mismatch between command dataclass and validator

**File:** `game/strategy/engine/commands/__init__.py:421` vs `game/strategy/validation/planet_order_validator.py:31`  
**Severity:** MINOR  
**Finding:** `IssuePlanetOrderCommand.component_key` is typed `Optional[str] = None`, but `PlanetOrderValidator.validate_activate_ability(component_key: str)` requires non-optional `str`. The command handler guards (lines 74-75, 83-84 of `planet_command_handlers.py`) prevent this from causing a runtime type error, but a direct call to the validator without the handler guard would fail mypy strict-mode check.

**Why it matters:** This is a latent type-safety gap. If someone adds a new call site to the validator that doesn't replicate the handler guard, they'll get a clean mypy pass (the command's `Optional[str]` is compatible with `str` at the handler call site) but the runtime behavior would be undefined if `component_key` happens to be None. The guard in the handler is the right place to handle this, but the type system doesn't enforce the guard.

---

## Focus Area 5: run_loop.py IScene migration (LEG-02-002)

**Verdict: Clean migration, no event types lost.**

| Check | Status | Evidence |
|---|---|---|
| Legacy `handle_input()` branch deleted | CONFIRMED | `run_loop.py:122-125` — comment: "Removed legacy MOUSEBUTTONDOWN/MOUSEWHEEL dispatch." No per-state branch for RESEARCH_TREE/GALAXY_TEST |
| Unified dispatch | CONFIRMED | `run_loop.py:146-163` — `_forward_event_to_scene` calls `self._router.active_scene.handle_event(event)` |
| `ResearchTreeScene.handle_event()` exists | CONFIRMED | `research_scene.py:216-248` — handles pygame_gui events, ESC, mouse clicks, scroll |
| `GalaxyTestScreen.handle_event()` exists | CONFIRMED | `galaxy_test/screen.py:181-213` — handles pygame_gui events, ESC, scroll, clicks |

**Event dispatch equivalence:**

Old code pattern (before migration):
```
elif scene_type in ('RESEARCH_TREE', 'GALAXY_TEST'):
    scene.handle_input(event)  # inline event handling
```

New code pattern:
```
self._router.active_scene.handle_event(event)  # unified IScene dispatch
```

The `handle_event` methods in both scenes now handle:
- **pygame_gui events** (`UI_BUTTON_PRESSED`, etc.) — processed via `self.ui_manager.process_events(event)` at `research_scene.py:224` and `galaxy_test/screen.py:184`
- **KEYDOWN** (ESC) — handled at `research_scene.py:232-235` and `galaxy_test/screen.py:192-198`
- **MOUSEBUTTONDOWN** (left click) — handled at `research_scene.py:238-242` and `galaxy_test/screen.py:209-213`
- **MOUSEWHEEL** — handled at `research_scene.py:245-248` and `galaxy_test/screen.py:203-206`
- **QUIT**, **KEYDOWN** (global hotkeys), **VIDEORESIZE** — handled in `_handle_normal_events` before forwarding

No event types are silently dropped. The per-frame `update_input()` call at `run_loop.py:208` handles continuous keyboard polling (camera pan via arrow keys), which is separate from event dispatch and remains functional.

---

#### INFO: `update_input` is NOT part of the IScene protocol

**File:** `game/core/protocols/ui.py:9-31` vs `game/run_loop.py:203-208`  
**Severity:** INFO  
**Finding:** `IScene` mandates `handle_event`, `update`, `draw`, `handle_resize` — but `run_loop.py:208` calls `router.active_scene.update_input(frame_time, events)` which is not in the protocol. The run_loop comment at line 203 acknowledges this: "Scenes that need per-frame keyboard polling expose update_input(dt, events); IScene only mandates handle_event/update/draw/handle_resize."

**Why it matters:** This is a deliberate design choice documented in code, not a bug. Both `ResearchTreeScene` and `GalaxyTestScreen` implement `update_input`. If a new scene that implements IScene but not `update_input` is used in these states, it would crash with `AttributeError`. The comment correctly warns about this implicit contract.

---

## Summary

| ID | Severity | Finding |
|---|---|---|
| LEG-03-006 | **No issues** | Fallback deleted, all 3 tests pass required callback |
| LEG-03-006 | MINOR | Vestigial `with_remove_callback` kwarg in test helper (no effect) |
| LEG-03-007 | **MAJOR** | No test calls `EmpireBuildQueueWindow()` through real constructor — constructor parameter validation unverified |
| LEG-03-007 | MINOR | Inline `_fake_handle_command` mock reimplements command handler logic |
| LEG-03-004/005 | **No issues** | No caller can reach validator with `component_key=None`; handler guards exist |
| LEG-03-004/005 | MINOR | Type mismatch: command field is `Optional[str]` but validator requires `str` (guarded by handler) |
| LEG-02-002 | **No issues** | IScene migration correct; no event types dropped |
| LEG-02-002 | INFO | `update_input` is not in IScene protocol (documented design choice) |

**Overall assessment:** The Phase 2 legacy fallback deletions are correctly implemented. The test-side audit is thorough for BuildQueueDragHandler and PlanetOrderValidator. The main gap is that EmpireBuildQueueWindow's constructor signature is never validated by a real instantiation — all tests bypass `__init__`, leaving the `facade`-as-required contract unenforced at the test level.
