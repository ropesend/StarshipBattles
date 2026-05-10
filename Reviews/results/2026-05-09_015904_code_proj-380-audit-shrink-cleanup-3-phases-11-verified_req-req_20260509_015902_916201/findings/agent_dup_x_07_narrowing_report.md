# DUP-X-07 Narrowing Claim Verification

**Reviewer:** OpenCode  
**Review item:** DUP-X-07 narrowing — `_cancel_input_mode` helper extraction  
**Source file:** `game/ui/screens/strategy_click_dispatcher.py` (605 lines)  
**Date:** 2026-05-08

---

## Q1: All Click-Handler Entry Points (dispatch table handlers)

The dispatch table at `strategy_click_dispatcher.py:35-50` registers 14 mode→handler pairs.

| # | Mode Key | Handler Method | Line |
|---|----------|---------------|------|
| 1 | `MOVE` | `_handle_move_mode_click` | 118 |
| 2 | `JOIN` | `_handle_join_mode_click` | 159 |
| 3 | `COLONIZE_TARGET` | `_handle_colonize_mode_click` | 188 |
| 4 | `TRANSFER` | `_handle_transfer_mode_click` | 228 |
| 5 | `DROP_CARGO` | `_handle_drop_cargo_mode_click` | 255 |
| 6 | `LOAD_CARGO` | `_handle_load_cargo_mode_click` | 267 |
| 7 | `WARP_TARGET` | `_handle_warp_target_click` | 279 |
| 8 | `IMPLODE_PLANET_TARGET` | `_handle_implode_planet_click` → delegates to `_handle_superweapon_click` | 317 |
| 9 | `STELLERATE_STAR_TARGET` | `_handle_stellerate_star_click` → delegates to `_handle_superweapon_click` | 321 |
| 10 | `OPEN_WARP_TARGET` | `_handle_open_warp_click` → delegates to `_handle_superweapon_click` | 325 |
| 11 | `CLOSE_WARP_TARGET` | `_handle_close_warp_click` → delegates to `_handle_superweapon_click` | 329 |
| 12 | `DYSON_SPHERE_TARGET` | `_handle_dyson_sphere_click` → delegates to `_handle_superweapon_click` | 333 |
| 13 | `EDIT_MOVE` | `_handle_edit_move_click` | 240 |
| 14 | `SELECT` | `_handle_select_mode_click` | 337 |

The 5 superweapon handlers (modes 8–12) are all thin delegates to `_handle_superweapon_click` (line 299). The `SELECT` handler (mode 14) has a fundamentally different right-click behavior (quick-move, not cancel). This leaves 9 distinct right-click-cancel sites:

1. `_handle_move_mode_click` (line 154–155)
2. `_handle_join_mode_click` (line 183–184)
3. `_handle_colonize_mode_click` (line 223–224)
4. `_handle_transfer_mode_click` (line 236–237)
5. `_handle_drop_cargo_mode_click` (line 263–264)
6. `_handle_load_cargo_mode_click` (line 275–276)
7. `_handle_warp_target_click` (line 295–296)
8. `_handle_superweapon_click` (line 313–314) — serves 5 superweapon modes
9. `_handle_edit_move_click` (line 252) — uses `on_cancel` callback variant

The count of "9 handlers" in the agent's claim is correct.

---

## Q2: Left-Click vs Right-Click per Handler

| # | Handler | Left-Click (button==1) | Right-Click (button==3) |
|---|---------|----------------------|------------------------|
| 1 | `_handle_move_mode_click` | Move/intercept designation. On `choice` result: prompt move-vs-intercept dialog. On `success`: finish move action. On failure: exit mode. (~35 lines) | Cancel to SELECT via `_cancel_input_mode()` |
| 2 | `_handle_join_mode_click` | Join designation. On `choice`: prompt fleet-selection dialog. On `success`: select joined fleet, exit mode. (~20 lines) | Cancel to SELECT via `_cancel_input_mode()` |
| 3 | `_handle_colonize_mode_click` | Colonize designation. On `prompt`: show planet selection, queue colonize mission, open transfer dialog. On `success`: re-select fleet. Always resets to SELECT. (~30 lines) | Cancel to SELECT via `_cancel_input_mode()` |
| 4 | `_handle_transfer_mode_click` | Resolve target hex → open transfer dialog → reset to SELECT. (4 lines) | Cancel to SELECT via `_cancel_input_mode()` |
| 5 | `_handle_drop_cargo_mode_click` | Resolve target hex → open cargo quick dialog (unload) → reset to SELECT. (4 lines) | Cancel to SELECT via `_cancel_input_mode()` |
| 6 | `_handle_load_cargo_mode_click` | Resolve target hex → open cargo quick dialog (load) → reset to SELECT. (4 lines) | Cancel to SELECT via `_cancel_input_mode()` |
| 7 | `_handle_warp_target_click` | Resolve target hex → issue `IssueWarpCommand` → handle result/error. (~10 lines) | Cancel to SELECT via `_cancel_input_mode()` |
| 8 | `_handle_superweapon_click` | Invoke `self.scene._superweapons.<method>(mx, my, fleet)`, reset mode on success. (5 modes via delegation) | Cancel to SELECT via `_cancel_input_mode()` |
| 9 | `_handle_edit_move_click` | Resolve target hex → `self.scene.complete_edit_move(new_hex)`. (3 lines) | Cancel via `_cancel_input_mode(on_cancel=_clear_edit_state)` — clears ghost state first |

---

## Q3: Left-Click Divergence Assessment

The agent claimed: *"left-click bodies diverge significantly (move/intercept prompt, colonize mission queue, transfer dialog, cargo operations, warp targeting, superweapon targeting)."*

**This is partially incorrect.** The three simple-dialog handlers are near-identical:

- `_handle_transfer_mode_click` (lines 230–235)
- `_handle_drop_cargo_mode_click` (lines 257–262)
- `_handle_load_cargo_mode_click` (lines 269–274)

All three follow the exact same skeleton:

```
target_hex = self._resolve_click_target(mx, my)
fleet = self.scene.selected_fleet
self.scene.ui.<dialog_method>(fleet, target_hex, ...)
self.input_mode = 'SELECT'
return True
```

`DROP_CARGO` and `LOAD_CARGO` differ by a single string literal (`'unload'` vs `'load'`). `TRANSFER` differs only in the dialog method name (`open_transfer_dialog` vs `open_cargo_quick_dialog` + operation string).

The remaining 6 handlers (MOVE, JOIN, COLONIZE, WARP_TARGET, superweapon, EDIT_MOVE) do have meaningfully divergent left-click logic that resists trivial consolidation.

---

## Q4: Near-Identical Left-Click Handler Pairs

### FND-031 — MAJOR: DROP_CARGO / LOAD_CARGO are identical except for a string literal

**File:** `game/ui/screens/strategy_click_dispatcher.py`  
**Lines:** 255–277

`_handle_drop_cargo_mode_click` (line 255) and `_handle_load_cargo_mode_click` (line 267) are byte-for-byte identical except:

| Location | DROP_CARGO | LOAD_CARGO |
|----------|-----------|------------|
| Dialog call (line 260 / 272) | `open_cargo_quick_dialog(fleet, target_hex, 'unload')` | `open_cargo_quick_dialog(fleet, target_hex, 'load')` |

Everything else — hex resolution, fleet fetch, mode reset, right-click cancel, `return False` — is identical. Consolidation into a single `_handle_cargo_quick_click(self, mx, my, button, operation: str)` was warranted but was missed.

### FND-032 — MAJOR: TRANSFER shares the same skeleton as DROP/LOAD_CARGO

**File:** `game/ui/screens/strategy_click_dispatcher.py`  
**Lines:** 228–238

`_handle_transfer_mode_click` (line 228) uses the identical 4-line left-click skeleton as DROP_CARGO and LOAD_CARGO. The only difference is `open_transfer_dialog(fleet, target_hex)` vs `open_cargo_quick_dialog(fleet, target_hex, operation_string)`. A broader consolidation into a `_handle_dialog_mode_click(..., dialog_method: Callable, *args)` or similar parameterized handler would cover all three modes. The agent's claim that "left-click bodies diverge significantly" is wrong for these three — they are structurally identical.

**Severity justification:** The DUP-X-07 narrowing was over-conservative. Three handlers with near-identical left-click bodies remain unconsolidated. This is not just a missed opportunity — it contradicts the agent's own divergence claim used to justify limiting the consolidation scope.

---

## Q5: `_cancel_input_mode` Helper Correctness

### FND-033 — INFO: `_cancel_input_mode` correctly replicates all 9 right-click cancel branches

**File:** `game/ui/screens/strategy_click_dispatcher.py`, lines 83–112

The `_cancel_input_mode` helper at line 83 performs:

1. Optionally calls `on_cancel()` if provided (line 108–109)
2. Sets `self.input_mode = 'SELECT'` (line 110)
3. Logs `"Input Mode: SELECT"` (line 111)
4. Returns `True` (line 112)

This matches the original 3-line block that was present in all 9 right-click branches:

```python
self.input_mode = 'SELECT'
logger.debug("Input Mode: SELECT")
return True
```

All 9 call sites verified:
- Line 155: `_handle_move_mode_click` → `self._cancel_input_mode()` ✓
- Line 184: `_handle_join_mode_click` → `self._cancel_input_mode()` ✓
- Line 224: `_handle_colonize_mode_click` → `self._cancel_input_mode()` ✓
- Line 237: `_handle_transfer_mode_click` → `self._cancel_input_mode()` ✓
- Line 264: `_handle_drop_cargo_mode_click` → `self._cancel_input_mode()` ✓
- Line 276: `_handle_load_cargo_mode_click` → `self._cancel_input_mode()` ✓
- Line 296: `_handle_warp_target_click` → `self._cancel_input_mode()` ✓
- Line 314: `_handle_superweapon_click` → `self._cancel_input_mode()` ✓ (covers 5 superweapon modes)
- Line 252: `_handle_edit_move_click` → `self._cancel_input_mode(on_cancel=_clear_edit_state)` ✓

All calls are correct.

---

## Q6: `_handle_edit_move_click` `on_cancel` Wiring

### FND-034 — INFO: EDIT_MOVE `on_cancel` callback is correctly wired

**File:** `game/ui/screens/strategy_click_dispatcher.py`, lines 240–253

The handler defines a local `_clear_edit_state` closure that clears three edit-move-specific attributes:

```python
def _clear_edit_state() -> None:
    self.scene._edit_move_ghost_hex = None
    self.scene._edit_move_order_index = None
    self.scene._edit_move_fleet = None
```

This is passed to `_cancel_input_mode(on_cancel=_clear_edit_state)` at line 252.

The helper runs `on_cancel()` **before** `self.input_mode = 'SELECT'` (lines 108–110). This ordering is correct: the edit-move state cleanup happens while the mode is still nominally `EDIT_MOVE`, then the mode flips to `SELECT`. Callers that observe state after `_cancel_input_mode` returns will see a clean slate (no ghost hex, no order index, no fleet) in SELECT mode.

---

## Summary

| ID | Severity | Summary |
|----|----------|---------|
| FND-033 | INFO | `_cancel_input_mode` correctly consolidates all 9 right-click cancel branches |
| FND-034 | INFO | `_handle_edit_move_click` `on_cancel` callback correctly wired; cleanup runs before mode flip |
| FND-031 | **MAJOR** | DROP_CARGO / LOAD_CARGO left-click bodies are identical except for `'unload'`/`'load'` string — missed consolidation opportunity |
| FND-032 | **MAJOR** | TRANSFER left-click body is structurally identical to DROP/LOAD_CARGO — all three share `resolve → get fleet → open dialog → reset to SELECT` skeleton |

**Overall verdict:** The right-click consolidation (`_cancel_input_mode`) is correct and well-implemented. However, the agent's claim that left-click bodies diverge significantly was wrong for TRANSFER, DROP_CARGO, and LOAD_CARGO — these three are structurally identical and should have been consolidated. The DUP-X-07 narrowing was **over-conservative**.
