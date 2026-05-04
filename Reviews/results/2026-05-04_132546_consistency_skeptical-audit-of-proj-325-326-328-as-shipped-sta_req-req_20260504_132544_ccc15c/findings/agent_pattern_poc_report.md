# Agent Pattern PoC Report — Focus Areas 2, 3, 8

**Reviewer:** OpenCode (skeptical audit)
**Request:** `req_20260504_132544_ccc15c`
**Date:** 2026-05-04

---

## Focus Area 2: Pattern Bend Audit

### PoC Finding 1 — `self.rect` descriptor handling: **PASS**

Verified every production file — NO bypass branch assigns `self.rect`.

| File | Bypass-branch `self.rect` assignment? | Evidence |
|------|--------------------------------------|----------|
| `game/ui/screens/race_setup/screen.py` | NO | Line 211: `del rect` + docstring: "not assignable on a bypassed UIWindow" |
| `game/ui/screens/strategy_modal_window.py` | NO | Lines 101-105: docstring explicitly documents non-assignment |
| `game/ui/screens/build_queue_list_window.py` | NO | Inherent from `super().__init__()` → `StrategyModalWindow` bypass (no assignment) |
| `game/ui/screens/orders_window.py` | NO | Inherent from `StrategyModalWindow` bypass; `rect` stored as `self._initial_rect` (not the descriptor) |
| `game/ui/screens/fleet_report_window.py` | NO | Inherent from `StrategyModalWindow` bypass |
| `game/ui/screens/new_game_setup_screen.py` | NO | Line 184: `# NOTE: do not assign self.rect.` directly in bypass |
| `game/ui/screens/transfer_dialog.py` | NO | Inherent from `StrategyModalWindow` bypass |

**Verdict:** All 7 production files avoid the `self.rect` descriptor write in the bypass branch. No drift. ✓

### PoC Finding 2 — Bypass branch invokes `ui_builder.build(self)`: **PASS**

Verified every bypass branch calls `ui_builder.build(self)` when `ui_builder` is explicitly supplied.

| File | Calls `ui_builder.build(self)`? | Lines |
|------|-------------------------------|-------|
| `race_setup/screen.py` | YES | 161-162 |
| `strategy_modal_window.py` | N/A (base class, no builder parameter) | — |
| `build_queue_list_window.py` | YES | 177-179 |
| `orders_window.py` | YES | 350-352 |
| `fleet_report_window.py` | YES | 201-203 |
| `new_game_setup_screen.py` | YES | 189-190 |
| `transfer_dialog.py` | YES | 158-160 |

**Note:** `StrategyModalWindow` is a base class without a `ui_builder` parameter — it correctly does NOT attempt to call a builder in its bypass branch. All 6 concrete subclasses that accept a `ui_builder` seam invoke it correctly under bypass. ✓

### PoC Finding 3 — Delegate refs mirrored to legacy attribute names: **PASS**

| Class | Delegate mirror assignments | Evidence |
|-------|----------------------------|----------|
| `RaceSetupScreen` | `self._view_model`, `self._renderer`, `self._controller`, `self._input_handler`, `self._llm_service` mirrored from `self._delegates` (factory-built) | `screen.py:139-143` |
| `NewGameSetupScreen` | `self._view_model`, `self._controller` assigned directly from constructor params | `new_game_setup_screen.py:163-170` |
| `TransferDialog` | `self._renderer`, `self.view_model` (public), `self._controller` assigned directly from constructor params | `transfer_dialog.py:131-135` |

**Verdict:** All three classes mirror delegates to the legacy attribute names. The mirroring style differs (factory-mediated vs. direct parameter assignment), but the attribute availability is consistent. ✓

### PoC Finding 4 — Renderer-internal widget reach-throughs: **PASS with note**

**RaceSetup pairing:** `tests/fixtures/race_setup_ui_builders.py:87-99` reproduces 11 renderer-internal widget refs on `screen._renderer`:
- `save_update_dialog`, `btn_overwrite`, `btn_save_new`, `btn_save_cancel`
- `llm_dialog_window`, `llm_dialog_btn_keep`, `llm_dialog_btn_stop`, `llm_dialog_field`
- `llm_error_popup`, `llm_error_popup_btn_ok`, `_ship_preview`

`test_race_setup_screen.py:661-745` exercises `screen._renderer.save_update_dialog` across 5+ tests, confirming the reach-through. ✓

**Transfer pairing:** `tests/fixtures/transfer_ui_builder.py` reproduces dialog-level widget slots (`drop_source`, `drop_target`, `btn_*`, `grid_container`) but does NOT populate renderer-internal widget refs (e.g., `_renderer.some_internal_widget`). The characterization tests at `test_transfer_dialog_characterization.py` assert delegate existence (`dialog._renderer is not None` at line 561) but do NOT reach into renderer-internal widgets. This is a **correct omission** — the TransferDialog characterization tests exercise pure data/math/command logic, not widget layout. The mock builder faithfully mirrors only what the tests need. ✓

---

## Focus Area 3: PROJ-325 PoC Quality

### AC-1: RaceSetupScreen.__init__ two-stage pattern: **PASS**

`screen.py:79-175` implements the two-stage pattern cleanly:
- **Stage 1** (lines 125-143): cheap state (`_init_state`) + widget-ref placeholders (`_init_widget_refs`) + delegate factory construction (`_delegates`) + legacy attribute mirroring. Always runs (before the guard).
- **Stage 2** (lines 151-163): `bypass_init` guard — sets `ui_manager`, `_window_init_bypassed`, optionally invokes test-supplied `ui_builder`, returns early.
- **Stage 3** (lines 165-175): production-only — `super().__init__()` (UIWindow shell) + widget tree via `(ui_builder or RaceSetupUiBuilder()).build(self)`.

The guard is NOT the first executable statement (contrary to Pattern #33's "MUST be first" rule in `02_PATTERNS.md:1831`). This is intentional per the PoC design — cheap state + delegates MUST run before the guard to make bypassed instances useful. Pattern #33's documentation (lines 1791-1808) itself describes and endorses this refinement. **No drift detected** — the docs and code are consistent. ✓

### AC-2: bypass_init + MockRaceSetupUiBuilder produces useful instance: **PASS**

`test_race_setup_screen.py:104-115` constructs a `RaceSetupScreen` under `with bypass_init(RaceSetupScreen): make_ui_widget(...)` with `MockRaceSetupUiBuilder()`. The test asserts:
- `screen.race_config is not None`
- `screen.is_editing is False`
- `screen.race_library is not None`

All delegates (`_view_model`, `_controller`, `_renderer`, `_input_handler`, `_llm_service`) are populated via the `DefaultRaceSetupDelegateFactory().build(self)` call in Stage 1. Widget slots are populated with `MagicMock` instances via `MockRaceSetupUiBuilder.build(self)` in Stage 2 (the bypass `ui_builder.build(self)` invocation). The legacy `_make_race_setup_screen` helper (lines 37-87) uses this exact construction pattern and returns a fully functional instance. ✓

### AC-3: `_make_race_setup_screen` LOC delta: **PASS (minor variance)**

**Measured:** The helper at `test_race_setup_screen.py:37-94` spans **58 lines** (including `def` line, docstring, and blank lines). Non-blank non-comment lines: **42**.

**Claimed:** 118 → 53 LOC delta (i.e., ~53 lines now vs ~118 previously).

**Analysis:** The measured 58 lines vs claimed 53 is a 5-line (~9%) difference — within defensible counting variation (exclude docstring = ~53, exclude blank lines = ~50). The pre-PROJ-325 version lived inline at the top of the test file (lines 31-148 per `race_setup_ui_builders.py:47`), spanning ~118 lines. The current version is 58 lines — a **60-line reduction (~51%)**. The claim is approximately verified. **Minor note:** the helper still does manual override wiring at lines 67-70 (`screen.race_config = race_config`, `screen._controller.race_config = race_config`, etc.), suggesting some integration friction between MockRaceSetupUiBuilder defaults and existing test expectations. Not a bug; a future clean-up opportunity. ✓

### AC-5: Test suite run: **PASS**

```
$ python -m pytest tests/unit/ui/screens/test_race_setup_screen.py -q
63 passed in 2.19s
```

All 63 tests pass, including:
- `TestPROJ325TwoStageConstruction.test_bypass_init_with_null_builder_yields_useful_instance`
- `TestPROJ325TwoStageConstruction.test_mock_builder_populates_widget_slots`
- All legacy tab-navigation, data-flow, validation, and panel tests

✓

---

## Focus Area 8: Cross-Reference Integrity

### Section 32 → 33 cross-reference: **PASS**

`docs/02_PATTERNS.md` section 32 (Compositional Construction) references section 33 in two places:
- Line 1719: "`bypass_init` (Pattern from PROJ-325 / PROJ-328)" — names the pattern family
- Line 1720: "...pair Compositional Construction with `bypass_init` or a two-stage `__init__` (cheap state then heavy shell — see `RaceSetupScreen`)."

Section 32 does NOT include an explicit "see Section 33" hyperlink, but it describes the relationship accurately (Compositional Construction is canonical for new code; `bypass_init` is the retrofit pattern). ✓

### Section 33 → 32 cross-reference: **PASS**

`docs/02_PATTERNS.md` section 33 (UI Widget Test Factory) cross-references section 32 explicitly and prominently:
- Line 1737: **bold** callout box: "**Relationship to Pattern #32 (Compositional Construction).** Compositional Construction is the **preferred** pattern for **new** classes... **This pattern (#33) is the retrofit pattern for legacy UIWindow subclasses**"
- Line 1815: "For NEW UI classes: prefer Pattern #32 (Compositional Construction) up front."

The cross-reference is accurate, well-placed, and repeated in the "When to Use" section. ✓

### PROJ-328 design.md: **FAIL — Unfilled template**

`Projects/active_projects/PROJ-328/design.md` (26 lines) is a **template with every section unfilled**:

| Section | Content |
|---------|---------|
| Initial Analysis | `[Findings from Phase A code review - what was discovered about the codebase]` |
| Architecture | `[Key architecture points relevant to implementation]` |
| Key Patterns to Reuse | `- **[Pattern Name]**: file:lines - description` |
| Dependencies & Risks | `1. **[Risk/Dependency]** - mitigation approach` |
| Opportunities Discovered | `- [Opportunity 1]` |

All bracketed placeholders are unexpanded. The header states "THIS IS A REFERENCE DOCUMENT — Do not modify during implementation" but there is nothing to reference. The `manifest.md` lists this file as a deliverable; it was delivered as a stub. **PROJ-328 shipped with an unfilled design document.** ✗

---

## Summary

| Focus Area | Claim | Verdict |
|------------|-------|---------|
| 2: PoC finding 1 | `self.rect` not assigned in bypass (7 files) | **PASS** ✓ |
| 2: PoC finding 2 | `ui_builder.build(self)` called in bypass (6/7) | **PASS** ✓ |
| 2: PoC finding 3 | Delegate refs mirrored (3 classes) | **PASS** ✓ |
| 2: PoC finding 4 | Renderer reach-throughs reproduced in mock builders | **PASS** ✓ |
| 3: AC-1 | Two-stage `__init__` pattern followed | **PASS** ✓ |
| 3: AC-2 | `bypass_init` + Mock builder = useful instance | **PASS** ✓ |
| 3: AC-3 | LOC delta ~118→53 | **PASS** (58 lines, minor variance) ✓ |
| 3: AC-5 | `pytest test_race_setup_screen.py` passes | **PASS** (63 passed) ✓ |
| 8: §32→§33 | Cross-reference from Compositional to Test Factory | **PASS** ✓ |
| 8: §33→§32 | Cross-reference from Test Factory to Compositional | **PASS** ✓ |
| 8: PROJ-328 design.md | Filled-in template? | **FAIL** — stub ✗ |

**Overall:** 10/11 claims verified as correct or approximately correct. The single failure is PROJ-328's design.md being an unfilled template — a documentation gap in an otherwise clean-shipping project bundle.
