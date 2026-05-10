# PROJ-325 Phase 2 + Phase 3 Review Report

**Review date:** 2026-05-04
**Scope:** Phase 3 (RaceSetupScreen two-stage UIWindow construction PoC) + Phase 2 (PROJ-323 Task 3.34 fleet_not_found parametrize + Task 3.37 cargo parametrize)

---

## Executive Summary

**Phase 3 (two-stage construction PoC):** The pattern is correctly applied per Pattern 33 documentation and the consensus refactor plan. All 4 PoC findings from `poc_findings.md` are respected. The `DefaultRaceSetupDelegateFactory` produces real, exercise-able delegates. The `MockRaceSetupUiBuilder` populates every widget slot the 62 pre-existing tests need. 63/63 tests pass.

**Phase 2 (parametrize):** Task 3.34 correctly splits 11 fleet_not_found handler tests into two groups (9 fleet_id-handlers + 2 entity_id-handlers), preserving the legitimate command-shape boundary. Task 3.37 correctly parametrizes 4 zero/negative cargo tests (load/unload zero/negative). Both are clean, not over-consolidated.

**Key concerns:** (1) 30+ pre-existing tests mock the method under test — vacuous surface independent of PROJ-325, (2) 2 tests still use the legacy `__new__` bypass, (3) the `_make_race_setup_screen` helper overrides `_controller` internal state post-construction, defeating the delegate-factory seam for some tests.

---

## Findings: Phase 3 (RaceSetupScreen two-stage construction)

### FND-01: Two-stage pattern correctly applied; all 4 PoC refinements respected
**Severity:** NONE (confirmation)
**File:** `game/ui/screens/race_setup/screen.py`
**Line:** 79-176
**Description:** Stage 1 (cheap state `_init_state` + `_init_widget_refs` + delegate factory) runs lines 125-143 BEFORE the `bypass_init` guard at line 151. Stage 2 (`super().__init__` + builder) runs lines 165-175 after the guard. All 4 PoC refinements from `poc_findings.md` are applied: (1) no `self.rect = rect` in bypass branch, (2) bypass branch invokes `ui_builder.build(self)` when explicitly supplied, (3) delegate refs mirrored to legacy attribute names, (4) `MockRaceSetupUiBuilder` handles renderer-internal reach-throughs. No action required.

### FND-02: Delegate factory produces real, exercise-able delegates
**Severity:** NONE (confirmation)
**File:** `game/ui/screens/race_setup/delegate_factory.py`
**Line:** 60-84
**Description:** `DefaultRaceSetupDelegateFactory.build(screen)` creates real instances of `RaceSetupViewModel`, `RaceSetupRenderer`, `RaceSetupController`, `LLMDialogService`, and `RaceSetupInputHandler` — all plain-Python classes that do not touch `pygame_gui` in their constructors. Tests exercise them: e.g., `test_on_race_selected_updates_panel_race_configs` (test_race_setup_screen.py:602) calls `screen._controller.on_race_selected(new_config)` and asserts real behavior (updating panel `race_config` refs, calling `set_from_config` on 7 panels). No action required.

### FND-03: Mock builder populates every widget slot; Null builder is under-used
**Severity:** MAJOR
**File:** `tests/fixtures/race_setup_ui_builders.py`
**Line:** 42-112
**Description:** `MockRaceSetupUiBuilder.build()` populates 8 panel refs, 7 step_panels, 7 tab_buttons (with `tab_index`), 5 bottom-bar buttons, 3 misc widget refs, and 11 renderer-internal widget refs — matching the legacy 118-LOC helper (phase_3_checklist.md Task 3.5 notes document the full set). Every existing test uses this builder through `_make_race_setup_screen()`.

However, `NullRaceSetupUiBuilder` (line 34-39) is consumed by exactly **one** test (`TestPROJ325TwoStageConstruction.test_bypass_init_with_null_builder_yields_useful_instance` at line 104) plus its own smoke test. No pre-existing test migrated to the null builder. The fixture's documented purpose — "use when a test only exercises cheap state + delegate behaviour" — has no consumer beyond the PoC verification test.
**Recommendation:** Either (a) migrate a few existing tests to use `NullRaceSetupUiBuilder` where they only exercise delegates and don't touch widget slots (proves the null-path is real), or (b) add a comment noting the fixture exists for PROJ-328 sibling refactors and is not dead code. A fixture with one consumer is a cleanup candidate.

### FND-04: 30+ pre-existing tests mock the method under test — vacuous surface
**Severity:** MAJOR
**File:** `tests/unit/ui/screens/test_race_setup_screen.py`
**Line:** Throughout (examples: 302-312, 483-507, 562-592)
**Description:** Many tests replace production methods with mock clones and assert the mock was called, never exercising real production logic. Representative examples:
- `test_save_calls_race_library` (line 302): replaces `screen._save_race` with `mock_save_race` that calls `race_library.save()`, then asserts `.save.assert_called_once()`. Tests mock wiring, not real behavior.
- `test_complete_callback_invoked_on_save` (line 483): replaces `screen._on_save` with a wrapper, calls it, asserts the mock wrapper's effect. Tests nothing real.
- `test_save_button_visible_on_summary_tab` (line 562): replaces `screen._update_navigation_buttons` with a truncated clone, asserts the clone's loop. The real `_update_navigation_buttons` delegates to `_view_model.show_save_button_on()` — the mock clones ignore this entirely.
- `test_validate_for_save_checks_required_fields` (line 341): replaces `screen._validate_for_save` with a hand-rolled mock that does its own validation logic, then tests the mock.
- `test_aptitude_changes_update_race_config` (line 226): installs `mock_update_config` on `mocks['aptitudes_panel'].update_config`, calls it, asserts. Tests mock wiring.

These tests cannot detect regressions in the real code. The screen's real `_validate_for_save` could stop working and these tests would still pass. This is a pre-existing condition, not caused by PROJ-325 — the refactor preserved test behavior 1:1. However, the credibility of the 63-tests-pass metric is weakened.
**Recommendation:** Open a follow-up ticket (PROJ-33x) to audit and replace vacuous mock-the-method tests with tests that exercise real delegate behavior through the two-stage construction pattern. The Phase 3 PoC now provides the infrastructure to do this — tests can construct a screen with real delegates (`MockRaceSetupUiBuilder` for widget slots) and call `screen._controller.on_save()` etc. without mocking the method under test. Prioritize the validation and save-flow tests first (they guard the most important production behavior).

### FND-05: Old `__new__` bypass pattern persists in 2 kill-hook tests
**Severity:** MAJOR
**File:** `tests/unit/ui/screens/test_race_setup_screen.py`
**Line:** 1209-1210, 1229-1230
**Description:** `test_kill_cancels_description_controller` and `test_kill_when_no_controller_does_not_raise` use `RaceSetupScreen.__new__(RaceSetupScreen)` with `patch.object(RaceSetupScreen, '__init__', lambda self, *a, **k: None)`. This is the legacy `__new__` bypass pattern that Pattern 33 ("UI Widget Test Factory") says should be eradicated. These tests manually set `screen._controller` and call `screen.kill()` — they do not need a full screen instance, so `__new__` is functionally correct here, but the pattern persistence creates ambiguity about which bypass mechanism to use.
**Recommendation:** Either (a) add a comment at these 2 test sites explaining why `__new__` is used instead of the two-stage pattern ("tests only need a bare object with `_controller`; full construction would create unnecessary state"), or (b) migrate to the two-stage pattern with `NullRaceSetupUiBuilder` for consistency (accepts the overhead of unused state for pattern uniformity). Option (a) is preferred given the tests' scope.

### FND-06: `_make_race_setup_screen` overrides `_controller` internal state — leaky seam
**Severity:** MAJOR
**File:** `tests/unit/ui/screens/test_race_setup_screen.py`
**Line:** 67-69
**Description:** After constructing a real screen through the two-stage pattern (which builds real `RaceConfig()`/`RaceLibrary()` and wires them into the controller via `DefaultRaceSetupDelegateFactory`), the helper immediately overrides four attributes:
```python
screen.race_config = race_config        # mock
screen.race_library = race_library      # mock
screen._controller.race_config = race_config
screen._controller.race_library = race_library
```
The `_controller` overrides defeat the delegate-factory seam: the factory's wiring is discarded before any test runs. Tests that call `_controller.on_save()` or `_controller.on_race_selected()` exercise a controller whose `race_config`/`race_library` were set by the test helper, not by the factory. The factory's `RaceSetupController(...)` constructor call at delegate_factory.py:63-72 is dead weight for these tests.

This is a documented trade-off (phase_3_checklist.md Task 3.5 Notes: "The new helper sets `screen.race_config = race_config` ... AFTER the constructor runs because Stage 1 builds a real `RaceConfig`"). But it means the delegate_factory seam is leaky — tests cannot fully control what the controller receives without reaching into `_controller` internals.
**Recommendation:** Extend `DefaultRaceSetupDelegateFactory.build()` to accept an optional `race_config: RaceConfig | None = None` and `race_library: RaceLibrary | None = None` override. When supplied, the factory uses the override instead of reading from the screen. Tests would then pass a custom factory instead of post-construction overriding. Alternatively, note this as a PROJ-328 design consideration — the factory pattern should pass data IN, not just read from the screen.

### FND-07: Parametrize handler tests use `Mock(command_attr=value)` — fragile to handler interface changes
**Severity:** MAJOR
**File:** `tests/unit/strategy/test_command_handlers.py`
**Line:** 1852, 1903
**Description:** The parametrized fleet_not_found tests construct `Mock(fleet_id=999, **extra_cmd_kwargs)` which passes all extra fields as MagicMock attributes on a single Mock object. If any handler's `execute()` accesses a command attribute via `cmd.some_field` (rather than `getattr`), MagicMock silently auto-creates the attribute, making a missing command field invisible to the test. This is the standard Mock() behavior and the test's primary assertion (`"Fleet not found" in result.message`) only checks the fleet-lookup guard gate, not the full command shape, so the risk is low. But if a handler being parametrized later restructures its `fleet_id` field (e.g., to `source_fleet_id`), the test won't fail — `mock_cmd.fleet_id` will silently return a new MagicMock.
**Recommendation:** Low priority. Consider adding `spec=CommandClass` to the Mock or using a `side_effect` guard that rejects unknown attribute access. Not actionable in this review; file as a PROJ-327 test-hardening note.

---

## Findings: Phase 2 (parametrize)

### FND-08: fleet_not_found two-group parametrize is correct and preserves boundary
**Severity:** NONE (confirmation)
**File:** `tests/unit/strategy/test_command_handlers.py`
**Line:** 1820-1908
**Description:** Group A (9 handlers using `fleet_id=...`) and Group B (2 handlers using `entity_id=..., entity_type="fleet"`) are correctly split. Each handler's extra command kwargs are accurately documented. Tests assert `"Fleet not found" in result.message` — the canonical guard message. No over-consolidation: the `fleet_id` vs `entity_id` command-shape boundary is preserved. Original per-class docstrings updated with consolidation cross-references (e.g., line 93: "`test_fleet_not_found` consolidated"). ~75 LOC saved matches the design target.

### FND-09: zero/negative cargo parametrize is correct and not over-consolidated
**Severity:** NONE (confirmation)
**File:** `tests/unit/strategy/data/test_fleet_consumable_aggregator.py`
**Line:** 384-405
**Description:** 4 parametrize cases (zero_load, negative_load, zero_unload, negative_unload) collapsed into one test. Dynamic dispatch via `getattr(resource_aggregator, operation)` correctly routes to `load_cargo_to_fleet` / `unload_cargo_from_fleet`. Assertions verify short-circuit to 0 AND that per-ship method is NOT called. Clean 2 - 2 matrix with no over-consolidation. ~4 LOC saved (4 tests to 1 parametrize + 3 config lines).

---

## Summary

| Severity | Count | Actionable? |
|----------|-------|-------------|
| CRITICAL | 0 | — |
| MAJOR | 5 (FND-03, FND-04, FND-05, FND-06, FND-07) | 3 actionable (FND-04: follow-up ticket for vacuous tests; FND-05: comment or migrate; FND-06: extend factory or document for PROJ-328) |
| NONE (confirmation) | 4 (FND-01, FND-02, FND-08, FND-09) | — |

**Bottom line:** PROJ-325 Phase 3 successfully proves the two-stage UIWindow construction pattern. The production code is clean, the pattern is correctly applied, and the builder fixtures work. The key quality gap is the pre-existing vacuous test surface (FND-04) — the two-stage pattern now provides the infrastructure to fix it, but that remediation is a separate project. Phase 2 parametrizations are clean, correct, and well-scoped. PROJ-328 is unblocked.
