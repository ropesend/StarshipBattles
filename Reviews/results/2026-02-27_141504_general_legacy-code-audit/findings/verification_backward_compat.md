# Verification Report: Backward Compatibility Violations

**Reviewer:** Skeptical Verification Agent
**Date:** 2026-02-27
**Scope:** Three findings related to legacy code paths and backward compatibility

---

### Finding ID: STR-002
**Original Claim:** `game/strategy/engine/fleet_order_processor.py:242-278` has dual code paths -- modern (remove colony ship only) vs legacy (remove entire fleet when `component_registry is None`).

**Verification Result:** CONFIRMED

**Evidence:**

The dual code path is real and exists in two places within `process_colonize()`:

1. **Planet selection (lines 225-244):** When `component_registry is not None`, the code iterates candidates to find one matching an available colony pod. When `None`, it falls back to `valid_candidates[0]` (legacy behavior).

2. **Ship/fleet removal (lines 268-278):** When `component_registry is not None`, only the specific colony ship is removed from the fleet. When `None`, the entire fleet is removed via `empire.remove_fleet(fleet)`.

**Production callers never pass None.** The real production call chain is:
- `TurnEngine._process_tick()` (line 402-405) calls `self.action_engine.process_action_ticks()` with `component_registry=self._registries.components`
- `ActionExecutionEngine` passes it through to `FleetOrderProcessor.process_end_turn_orders()`
- `process_end_turn_orders()` passes it to `process_colonize()`

`self._registries` is always initialized -- either from an injected `GameRegistries` or by calling `get_default_registry_provider()` (lines 160-170 of `turn_engine.py`). The `.components` attribute is a required field of `GameRegistries`.

**However, several tests call `process_end_turn_orders()` without `component_registry`**, defaulting to `None` and exercising the legacy path:
- `tests/integration/strategy/test_colonize_logic.py` (5 test functions) -- all call without registry
- `tests/unit/strategy/test_fleet_order_processor.py::TestEndTurnOrderProcessing::test_process_end_turn_orders_colonize` -- calls without registry

These tests rely on the legacy "remove entire fleet" behavior (e.g., `assert len(empire.fleets) == 0`).

**Risk of Fix:** Removing the legacy path would break at least 6 existing tests. The tests would need to be updated to either:
- Pass a component registry and add proper colony pod components to test ships, OR
- Mock the `ColonizeValidator.find_ship_with_colony_pod` return value

No production runtime risk -- the legacy path is never reached in production.

**Recommendation:** FIX

**Reasoning:** This is textbook dead code in production, kept alive only by tests that take shortcuts. The legacy path produces incorrect game behavior (destroying the entire fleet instead of just the colony ship), so any test exercising it is testing the wrong behavior. The fix should:
1. Remove the `component_registry is None` fallback paths
2. Make `component_registry` a required parameter (not Optional)
3. Update the ~6 affected tests to provide a component registry

---

### Finding ID: UIS-001
**Original Claim:** `game/ui/screens/empire_build_queue_window.py:153-155` has `self.scroll_bar` and `self.column_mgr` aliases solely for test compatibility.

**Verification Result:** PARTIALLY CONFIRMED

**Evidence:**

The comment at line 153 says "Store references for backward compatibility with tests," but the actual usage tells a different story for each attribute:

**`self.scroll_bar` (line 154) -- NOT just a test alias:**
The production code itself uses `self.scroll_bar` in 4 places:
- Line 427: `current_pct = self.scroll_bar.start_percentage`
- Line 429: `new_pct = max(0.0, min(1.0 - self.scroll_bar.visible_percentage, new_pct))`
- Line 430: `self.scroll_bar.set_scroll_from_start_percentage(new_pct)`
- Line 451: `if self.scroll_bar.check_has_moved_recently():`

This is a convenience reference to `self._virtual_table.scroll_bar`. It is actively used in production code for scroll handling. Removing it would break the production code. The comment is misleading -- this is a functional shortcut, not a backward-compat alias.

Test usage: `tests/unit/ui/screens/test_empire_build_queue_window.py` lines 94-96 mock `win.scroll_bar`.

**`self.column_mgr` (line 155) -- IS just a test alias:**
In production code, `self.column_mgr` is only assigned at line 155 and never referenced elsewhere in the file. The production code uses `self._column_manager` directly (e.g., line 447: `self._column_manager.set_sort(sort_col)`).

Test usage: `tests/unit/ui/screens/test_empire_build_queue_window.py` references `win.column_mgr` at lines 111-113, 1592, 1597-1598, 1609-1610. These tests use the alias to set up mocks and make assertions.

**Risk of Fix:**
- Removing `self.scroll_bar`: Would break production code at 4 call sites. DO NOT REMOVE.
- Removing `self.column_mgr`: Would break ~6 test references. Tests would need to be updated to use `win._column_manager` instead. No production impact.

**Recommendation:** MODIFY APPROACH

**Reasoning:** The original claim lumps two attributes together but they have very different statuses:
- `self.scroll_bar`: Keep, but fix the misleading comment. This is a production convenience reference, not a test compatibility alias.
- `self.column_mgr`: Fix by either (a) removing the alias and updating tests to use `_column_manager`, or (b) keeping it as a clean public alias and having production code use it too. Option (a) is cleaner since `_column_manager` is the canonical name used throughout the production code.

---

### Finding ID: STR-001
**Original Claim:** `game/strategy/data/design_metadata.py:36-41` has a `sprite_preview` field that's serialized but never read.

**Verification Result:** CONFIRMED

**Evidence:**

The `sprite_preview` field:
- Declared at line 41: `sprite_preview: Optional[str] = None  # Reserved for future use`
- Serialized in `to_dict()` at line 58: `"sprite_preview": self.sprite_preview`
- Deserialized in `from_dict()` at line 85: `sprite_preview=data.get("sprite_preview")`
- Has a comment at lines 38-40 saying it's a placeholder for future use

**No code anywhere reads or writes a meaningful value to this field:**
- `from_design_file()` (lines 89-135) does NOT set `sprite_preview` -- it's left as `None`
- `from_ship()` (lines 138-165) does NOT set `sprite_preview` -- it's left as `None`
- No UI code accesses `.sprite_preview` on any `DesignMetadata` instance
- No save game code serializes `DesignMetadata` -- the save system (`save_game_service.py`) does not reference `DesignMetadata` at all
- `Empire.designed_ships` (the only place `DesignMetadata` objects live) is a runtime cache, never persisted

The field is only tested in `tests/unit/strategy/test_design_metadata.py`:
- `test_from_dict_sprite_preview_none` (line 245) -- tests None roundtrip
- `test_to_dict_sprite_preview_none` (line 511) -- tests None serialization
- Roundtrip test (line 541) -- includes `sprite_preview="path/to/preview.png"`

The comment says "the preview image should be stored in a separate UI cache, not in this strategy-layer metadata" and "This field exists as a placeholder for save file compatibility." But there is no save file compatibility concern since `DesignMetadata` is never persisted to save files.

**Risk of Fix:** Removing the field would break 3-4 test methods that explicitly test the `sprite_preview` serialization behavior. No production runtime impact. No save file compatibility impact (the field was never saved).

**Recommendation:** FIX

**Reasoning:** This is a YAGNI violation and a placeholder field that has been present across multiple project iterations without ever being implemented. Per the project's CLAUDE.md: "When a new system replaces an old one, ERADICATE the old system completely" and "Save files are disposable." The field adds serialization overhead to every `to_dict()` call, creates a false impression that sprite previews are supported, and the comment itself acknowledges this field should not live in the strategy layer. The fix should:
1. Remove the `sprite_preview` field from the dataclass
2. Remove it from `to_dict()` and `from_dict()`
3. Update or remove the 3-4 affected tests

---

## Summary

| Finding | Verdict | Production Risk | Test Impact | Recommendation |
|---------|---------|-----------------|-------------|----------------|
| STR-002 | CONFIRMED | None (legacy path unreachable in production) | ~6 tests break | FIX -- remove legacy path, update tests |
| UIS-001 | PARTIALLY CONFIRMED | `scroll_bar` is used in production; `column_mgr` is test-only | ~6 tests need update for `column_mgr` | MODIFY -- fix comment on `scroll_bar`, remove `column_mgr` alias |
| STR-001 | CONFIRMED | None (field always None, never persisted) | ~4 tests break | FIX -- remove placeholder field and tests |
