# Shard 12 — Skeptical Verification Report

**Verifier**: Skeptical Verification Agent (OpenCode)  
**Date**: 2026-05-04  
**Phase 2 Report**: `SHARD_12.md` (Discovery Agent — OpenCode)  
**Verification scope**: All CRITICAL (1) and MAJOR (2) claims. MINOR/ADVISORY claims not re-verified (only upgrade candidates considered; none found).

---

## Summary

| Original Severity | File | Verdict | Corrected Severity |
|---|---|---|---|
| CRITICAL | `game/core/protocols/persistence.py` | **DISPUTED** | MINOR |
| MAJOR | `game/ui/screens/radiation_shield_editor.py` | **DISPUTED** | MINOR |
| MAJOR | `game/ui/screens/strategy_windows/empire_panel_ctrl.py` | **CONFIRMED (nuance)** | MAJOR |

2 of 3 CRITICAL/MAJOR claims were overstated due to discovery agent search failures. 1 MAJOR claim is confirmed. No MINOR/ADVISORY claims warranted upgrade.

---

## CONFIRMED Gaps

### MAJOR: `game/ui/screens/strategy_windows/empire_panel_ctrl.py` (82 LOC)

**Original claim**: Tier 0 — NO tests exist. 0/8 symbols: `EmpirePanelRegistrar`, `SettingsRegistrar`, and all their methods.  
**Verification**: **CONFIRMED (with nuance)**

**What was verified**:
- `EmpirePanelRegistrar` has **indirect** coverage through `tests/unit/ui/screens/test_strategy_window_manager.py` (lines 368–396):
  - `test_open_empire_panel_creates_window` (line 372): calls `window_manager.open_empire_panel()` → `self._empire_panel.open()` → `EmpirePanelRegistrar.open()`. Patches `EmpirePanelWindow` but the registrar's kill-check, rect-compute, and constructor-invoke logic all execute. Verifies the window reference is set.
  - `test_open_empire_panel_kills_existing` (line 380): sets `window_manager.empire_panel_window = existing`, calls `open_empire_panel()`, verifies `existing.kill()` was called. Exercises the `if c.empire_panel_window: c.empire_panel_window.kill()` branch in the registrar.
  - `test_on_empire_panel_closed_clears_reference` (line 389): sets a window, calls `_on_empire_panel_closed()` → `self._empire_panel._on_closed()` → `self._composer.empire_panel_window = None`. Verifies the reference clears.
- `SettingsRegistrar` has **zero** coverage — no direct or indirect tests in any file. A grep of the entire `tests/` directory for `open_settings`, `_settings`, or `SettingsRegistrar` returned no matches.
- The Phase 2 discovery agent did NOT search for indirect coverage through the `StrategyWindowManager` delegation chain, missing that `EmpirePanelRegistrar` is exercised by the manager tests.

**Untested registrar behaviors**:
- `EmpirePanelRegistrar.open()` — race_registry resolution via facade (lines 37–40) not verified
- `EmpirePanelRegistrar.open()` — registries DI passing to `EmpirePanelWindow` constructor (line 48) not verified  
- `EmpirePanelRegistrar.open()` — rect dimensions (90% of manager width/height) not explicitly verified
- `SettingsRegistrar.open()` — entirely untested (no tests touch the settings path)
- `SettingsRegistrar.open()` — kill-existing, rect computation, deferred `SettingsWindow` import

**Verdict**: MAJOR stands. 2 non-trivial classes (82 LOC combined) with only indirect coverage for one class and zero coverage for the other. The Phase 2 report was correct that no dedicated tests exist, but the "0 tests" claim is softened: `EmpirePanelRegistrar` has 3 indirect tests through the window manager.

---

## DISPUTED Claims

### ~~CRITICAL~~ → MINOR: `game/core/protocols/persistence.py` (27 LOC)

**Original claim**: Tier 0 — NO tests exist. 0/3 symbols untested. "Zero test coverage means there is no lock against accidental Protocol signature drift."  
**Verification**: **DISPUTED** — Dedicated tests exist.

**Evidence**:
- `tests/unit/core/test_serializable_protocol.py` (65 lines, 4 tests) directly imports and tests `ISerializable`:

| Test | What it verifies |
|---|---|
| `test_isinstance_check_passes` (line 36) | Conforming class passes `isinstance(obj, ISerializable)` |
| `test_isinstance_check_fails_missing_from_dict` (line 40) | Class missing `from_dict` fails `isinstance` check |
| `test_isinstance_check_fails_missing_to_dict` (line 44) | Class missing `to_dict` fails `isinstance` check |
| `test_battle_state_dataclasses_satisfy_protocol` (line 48) | All 5 battle state dataclasses (`ComponentState`, `ShipState`, `ProjectileState`, `BattleState`, `BattleResults`) have `to_dict`/`from_dict` |

- `tests/unit/core/test_protocols_public_api.py` (line 74): `ISerializable` is listed in the `PUBLIC_PROTOCOL_SYMBOLS` golden set with a parametrized test verifying it's importable from `game.core.protocols`.

These tests exactly match the Phase 2 report's own recommendation: "Structural Protocol conformance tests (verify a conforming class passes `isinstance`)", "Negative tests (a class missing `to_dict` or `from_dict` should fail `isinstance`)", and "Verify battle state dataclasses satisfy ISerializable".

**Corrected severity**: **MINOR** — The protocol has adequate structural tests. The Phase 2 report's signature-drift concern is addressed: the negative `isinstance` tests lock the protocol shape, and the dataclass attribute checks verify implementation conformance. No additional tests needed for this file.

---

### ~~MAJOR~~ → MINOR: `game/ui/screens/radiation_shield_editor.py` (231 LOC)

**Original claim**: Tier 0 — NO tests exist. 0/8 symbols: `RadiationShieldEditor`, `__init__`, `_build_ui`, `update`, `_button_handlers`, `_on_apply`, `_set_auto`, `_clear_target`.  
**Verification**: **DISPUTED** — Tests exist, but are structural/integration, not behavioral unit tests.

**Evidence — structural tests exist**:

| Test file | What it tests |
|---|---|
| `tests/integration/ui/test_editor_click_blocking.py` (231 lines) | 6 test functions reference `RadiationShieldEditor`: subclass check, modal register/deregister, spawn-site passes window_manager, click-blocking inside/outside/dead editor |
| `tests/unit/ui/screens/test_strategy_modal_window.py` (line 326–331) | Parametrized test verifies `RadiationShieldEditor.__init__` requires `window_manager` parameter (no default) |

The integration test file constructs `RadiationShieldEditor` via `cls.__new__` + `StrategyModalWindow.__init__`, then tests the modal registration/deregistration lifecycle and click-blocking integration. This exercises the class hierarchy and the window-manager interaction — but does NOT test the editor's domain logic.

**What remains genuinely untested**:
- `_set_auto()` — slider clamping `max(MIN_SHIELDING, min(MAX_SHIELDING, rad_pref.setpoint))` and preference lookup
- `_on_apply()` — callback fires with `(planet_id, shielding_value)` tuple
- `_clear_target()` — callback fires with `(planet_id, None)` 
- `update()` — slider-moved-recently label update
- `_build_ui()` — slider range `[0.0, 2.0]`, label text formatting

**Corrected severity**: **MINOR** — The "0 tests" claim in the Phase 2 report is factually wrong; structural integration tests exist. The behavioral gaps are real but lower severity: the editor inherits modal lifecycle from `StrategyModalWindow` (well-tested), and the domain logic (slider clamping, callbacks) is simple arithmetic/wiring that the structural tests could be extended to cover.

---

## Inconclusive / Disputed Table

| File | Original | New | Reason |
|---|---|---|---|
| `game/core/protocols/persistence.py` | CRITICAL | MINOR | `test_serializable_protocol.py` (4 tests) + `test_protocols_public_api.py` exist. Agent missed them. |
| `game/ui/screens/radiation_shield_editor.py` | MAJOR | MINOR | `test_editor_click_blocking.py` (6 test functions) + `test_strategy_modal_window.py` (1 parametrized) exist. Structural only; no behavioral unit tests for editor methods. |
| `game/ui/screens/strategy_windows/empire_panel_ctrl.py` | MAJOR | MAJOR | `EmpirePanelRegistrar` has 3 indirect tests through `test_strategy_window_manager.py`. `SettingsRegistrar` has zero coverage. Still warrants dedicated tests. |

---

## Discovery Agent Errors

The Phase 2 Discovery Agent made the following search errors in this shard:

| # | Error | Impact | Root Cause |
|---|---|---|---|
| 1 | **Missed `test_serializable_protocol.py`** — Claimed CRITICAL (0 tests) for `ISerializable` Protocol when a dedicated 65-line test file with 4 tests exists | False CRITICAL — Protocol is tested | Agent searched `tests/unit/core/protocols/test_persistence.py` (doesn't exist) but did not catch `tests/unit/core/test_serializable_protocol.py` |
| 2 | **Missed `test_editor_click_blocking.py`** — Claimed MAJOR (0 tests) for `RadiationShieldEditor` when an integration test file with 6 test functions exists | False MAJOR — Structural tests exist | Agent searched for `test_radiation_shield*` but missed the integration test that imports the class directly. Also missed `test_strategy_modal_window.py` parametrized test. |
| 3 | **Missed indirect coverage for `EmpirePanelRegistrar`** — Claimed 0 tests when `test_strategy_window_manager.py` exercises the registrar through the manager delegation chain | Overstated gap — 3 indirect tests exist for one registrar class | Agent only searched for `test_empire_panel*` and did not trace the `StrategyWindowManager.open_empire_panel()` → `EmpirePanelRegistrar.open()` delegation chain |
| 4 | **Missed `test_protocols_public_api.py`** relevance — The public API contract test includes `ISerializable` in its golden list | Understated coverage | Agent likely only looked for files matching `test_persistence*` |
| 5 | **3 false-negative files in coverage matrix** — `app_bootstrap`, `_condition_logic`, and partially `formula_evaluator` were listed with 0 tests in the matrix despite test files existing | Noise in the Coverage Matrix accuracy section | AST scanner limitation acknowledged in the report; Discovery Agent correctly identified these as false-negatives |
