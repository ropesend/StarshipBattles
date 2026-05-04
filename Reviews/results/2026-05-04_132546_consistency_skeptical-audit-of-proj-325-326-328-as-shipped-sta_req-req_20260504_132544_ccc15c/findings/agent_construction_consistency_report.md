# Two-Stage Construction Consistency Audit

**Auditor:** OpenCode  
**Date:** 2026-05-04  
**Scope:** 7 production classes across PROJ-325 and PROJ-328  
**Method:** Line-by-line comparison of `__init__` against the canonical PoC
(RaceSetupScreen) and the 4 refined PoC findings.

## Summary

| Finding | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 0 |
| MINOR | 7 |
| INFO (positive confirmations) | 4 |

No bugs found. All 7 classes correctly implement the two-stage pattern.
Divergences are architectural (different inheritance hierarchies) or
stylistic, not semantic.

---

## Positive Confirmations (PoC Findings 1-4 Verified)

### F1: `self.rect` NOT assigned in bypass branch — ALL CLASSES PASS

`pygame_gui`'s `GUISprite` base class makes `rect` a descriptor that mutates
`self.blit_data` on write, and `blit_data` is initialized only by the
`pygame.sprite.Sprite.__init__` chain that `bypass_init` skips. Every
class correctly avoids the assignment:

- **RaceSetupScreen** (`screen.py:211`): `_init_state` receives `rect` but
  explicitly `del rect` — "not assignable on a bypassed UIWindow."
- **StrategyModalWindow** (`strategy_modal_window.py:101-105`): Docstring
  explicitly warns against it; bypass branch never writes `self.rect`.
- **NewGameSetupScreen** (`new_game_setup_screen.py:184-188`): Comment
  notes "do not assign `self.rect`" with full rationale.
- **OrdersWindow** (`orders_window.py:324`): Stores `rect` as
  `self._initial_rect` (different attribute name), used only by builder
  in Stage 3. Does NOT write `self.rect`.
- **BuildQueueListWindow, FleetReportWindow, TransferDialog**: Neither
  store `rect` separately nor write `self.rect` — pass it straight to
  `super().__init__()`.

### F2: Bypass branch invokes `ui_builder.build(self)` when explicitly supplied — ALL CLASSES PASS

Every concrete class gates the builder call on `ui_builder is not None`:

- **RaceSetupScreen** (`screen.py:161-162`): `if ui_builder is not None: ui_builder.build(self)`
- **BuildQueueListWindow** (`build_queue_list_window.py:178-179`): Same.
- **OrdersWindow** (`orders_window.py:351-352`): Same.
- **FleetReportWindow** (`fleet_report_window.py:202-203`): Same.
- **NewGameSetupScreen** (`new_game_setup_screen.py:189-190`): Same.
- **TransferDialog** (`transfer_dialog.py:159-160`): Same.

When no builder is supplied under bypass, widget slots remain at their
placeholder values (None / empty lists), keeping bypassed instances
honest: cheap delegates present, widget tree absent.

### F3: Delegate refs mirrored to legacy attribute names — VERIFIED WHERE APPLICABLE

- **RaceSetupScreen** (`screen.py:138-143`): Explicit 5-line mirroring
  (`self._view_model = self._delegates.view_model` etc.)
- **NewGameSetupScreen** (`new_game_setup_screen.py:263-309`): 8 property
  shims onto `self._view_model`.
- **TransferDialog** (`transfer_dialog.py:195-257`): 12 property shims
  onto `self.view_model`.
- **BuildQueueListWindow, OrdersWindow, FleetReportWindow**: No legacy
  attribute names to mirror. These classes did not undergo an attribute
  renaming during the refactor — the attribute names `self.view_model`,
  `self.column_manager`, etc. were always the canonical names.

### F4: Renderer-internal widget reach-throughs — EXTENSIVE BUT SYSTEMATIC

Delegates (controller, renderer, input handler) access the screen's
private widget refs (`self._screen._identity_panel`, etc.). The screen
is the composition root and single owner of all widget refs. The delegates
take a `screen` back-reference at construction time and reach through
it to access widgets.

- **RaceSetupController** (`controller.py`): accesses `_identity_panel`,
  `_flag_gallery`, `_portrait_gallery`, `_theme_gallery`,
  `_environment_panel`, `_aptitudes_panel`, `_description_panel`,
  `_summary_panel`, `btn_save`, `btn_load`, `race_config`, `is_editing`,
  and `kill()`. ~15 unique private attribute accesses.
- **RaceSetupInputHandler** (`input_handler.py`): accesses
  `_controller`, `_renderer`, `_description_panel`, `_flag_gallery`,
  `_portrait_gallery`, `_theme_gallery`, `_identity_panel`,
  `_environment_panel`, `_aptitudes_panel`, and calls `_show_step()`.
- **RaceSetupRenderer** (`renderer.py`): accesses `ui_manager`,
  `get_container()`, and constructs modals on the screen's manager.
  Lighter than the controller.
- **FleetReportLayoutBuilder** (`fleet_report_window.py:49-114`): sets 9
  instance attributes on the screen (`sidebar_panel`, `sidebar`,
  `list_panel`, `data_source`, `virtual_table`, `detail_panel`,
  `ship_detail_panel`).

This coupling is a *pre-existing architectural choice* (screen as
composition root), not a regression introduced by the two-stage
refactor. No class crosses a delegate boundary it didn't already cross
before PROJ-325/328.

---

## Divergence Findings

### FND-CON-001: Bypass guard duplicated between two window hierarchies

**Severity:** MIN  
**File:** `game/ui/screens/new_game_setup_screen.py:177-191`  
**Observation:** NewGameSetupScreen (direct `UIWindow` subclass) and
RaceSetupScreen (direct `UIWindow` subclass) each contain an inline copy
of the bypass guard logic. StrategyModalWindow subclasses
(BuildQueueListWindow, OrdersWindow, FleetReportWindow, TransferDialog)
inherit the guard from the base class and only check
`self._window_init_bypassed`. The two direct-UIWindow screens each
duplicate:

```python
if getattr(type(self), 'bypass_init', False):
    self.ui_manager = manager
    self._window_init_bypassed = True
    # comment about self.rect...
    if ui_builder is not None:
        ui_builder.build(self)
    return
```

**Expected:** StrategyModalWindow's bypass guard was factored into the
base class to avoid duplication. The same could be done for non-modal
UIWindow subclasses via a `BypassableUIWindow` mixin or a
`_bypass_or_init(*args, manager, ui_builder, **kwargs)` helper function.
**Verdict:** JUSTIFIED (different hierarchies), but technical debt
worth tracking for future UIWindow refactors.

---

### FND-CON-002: StrategyModalWindow bypass guard runs before any subclass cheap state

**Severity:** MIN  
**File:** `game/ui/screens/strategy_modal_window.py:118-131`  
**Observation:** The bypass guard is the *first executable statement* in
`StrategyModalWindow.__init__`. There is no cheap state before it
because the base class owns no screen-specific state. Subclasses build
their cheap state *before* calling `super().__init__()`, and the base
class's bypass guard fires *during* that `super().__init__()` call.

**Expected:** The canonical headline pattern places cheap state → delegates
→ bypass guard in that order. The base class cannot do this because it
has no state to build. Subclasses achieve the pattern by building state
before `super().__init__()` and testing `_window_init_bypassed` after.
**Verdict:** JUSTIFIED (base class has no state; pattern is satisfied by
subclass composition order).

---

### FND-CON-003: StrategyModalWindow does not invoke a builder in bypass branch

**Severity:** MIN  
**File:** `game/ui/screens/strategy_modal_window.py:118-131`  
**Observation:** The base class bypass branch sets `_window_manager`,
`ui_manager`, and `_window_init_bypassed`, then returns. It does not
call any `ui_builder.build(self)`. The base class does not know about
subclass-specific builders.

**Expected:** Concrete screen classes handle the builder call in their
own Stage 3 (after `super().__init__()` returns), checking
`_window_init_bypassed`. All 4 StrategyModalWindow subclasses do this
correctly. **Verdict:** JUSTIFIED — base class cannot know subclass builder
type. Responsibility correctly delegated to subclasses.

---

### FND-CON-004: Inconsistent use of `_init_state` / `_init_widget_refs` helper methods

**Severity:** MIN  
**File:** Multiple (see below)  
**Observation:** Two classes extract cheap-state construction into named
helper methods; the other five set state inline in `__init__`:

| Class | `_init_state` | `_init_widget_refs` | Approach |
|-------|:---:|:---:|----------|
| RaceSetupScreen | Yes | Yes | Explicit helpers |
| NewGameSetupScreen | Yes | Yes | Explicit helpers |
| BuildQueueListWindow | No | No | Inline |
| OrdersWindow | No | No | Inline (partial: `_initial_rect`, `rows`, etc.) |
| FleetReportWindow | No | No | Inline (widget refs set as block of `= None`) |
| TransferDialog | No | Yes | Mixed: inline state + `_init_widget_refs()` helper |
| StrategyModalWindow | N/A | N/A | Base class, no state |

**Expected:** The two-stage pattern requires cheap state before the bypass
point; it does not mandate named helper methods. Both approaches satisfy
the pattern equally. **Verdict:** STYLISTIC — no pattern violation. The
`_init_state` + `_init_widget_refs` convention from the canonical PoC
is a readability choice, not a requirement.

---

### FND-CON-005: TransferDialog performs a side-effecting query in Stage 1

**Severity:** MIN  
**File:** `game/ui/screens/transfer_dialog.py:137-140`  
**Observation:** After building cheap state and delegates but before
`super().__init__`, TransferDialog calls
`self._controller.discover_pod_designs(scene)` to populate
`self.view_model.all_pod_names`. The docstring acknowledges this as a
"side-effecting query."

**Expected:** Stage 1 should only contain pure-Python object construction
(no queries, no I/O, no pygame_gui widgets). `discover_pod_designs`
walks the scene's pod design registry — it does not create pygame_gui
widgets, but it IS a read-side-effect (facade query). If the scene's
pod registry ever requires a pygame display context (unlikely but
possible), this would break under bypass_init.

**Verdict:** JUSTIFIED — the pod name list is needed before the builder
runs (it feeds `_build_pod_rows`). The query is cheap (in-memory
registry walk). But it's a divergence from the "pure construction only"
intent of Stage 1 and should be documented as such. The existing
docstring already covers this.

---

### FND-CON-006: FleetReportWindow mixes layout constants with delegate state in Stage 1

**Severity:** MIN  
**File:** `game/ui/screens/fleet_report_window.py:168-179`  
**Observation:** `__init__` Stage 1 sets layout constants
(`sidebar_width = 300`, `detail_width = 750`, `header_height`,
`row_height`) in the same block as delegate construction
(`view_model`, `column_manager`, `selection`) and widget ref
placeholders. The layout constants are pure integers — safe to set
before the bypass point. But they also represent a production layout
assumption baked into the constructor.

**Expected:** Layout constants belong in the builder (Stage 3), not in
the constructor. If a Mock builder doesn't use the standard layout, the
constants are misleading dead state on bypassed instances. **Verdict:**
MINOR — the constants don't break anything (they're pure ints), but
they violate the separation of concerns between state/delegates (Stage
1) and layout/widgets (Stage 3). Low-priority cleanup candidate.

---

### FND-CON-007: StrategyModalWindow subclass bypass check uses instance attr vs class attr

**Severity:** MIN  
**File:** `game/ui/screens/build_queue_list_window.py:177`,
`game/ui/screens/orders_window.py:350`,
`game/ui/screens/fleet_report_window.py:201`,
`game/ui/screens/transfer_dialog.py:158`  
**Observation:** All four StrategyModalWindow subclasses check the bypass
state via `getattr(self, '_window_init_bypassed', False)` (instance
attribute), while the two direct-UIWindow subclasses
(RaceSetupScreen, NewGameSetupScreen) check via
`getattr(type(self), 'bypass_init', False)` (class attribute).

**Expected:** This is the correct pattern for the StrategyModalWindow
hierarchy. The base class reads the class-level `type(self).bypass_init`
flag, acts on it (returning early or calling `super().__init__`), and
sets the instance-level `_window_init_bypassed` flag as a record of
what happened. Subclasses then read the instance flag to decide whether
to build widgets or short-circuit. Direct-UIWindow subclasses don't
have this indirection — they read the class flag directly because
there's no intervening base class to set the instance flag.

**Verdict:** NOT A DIVERGENCE — two correct patterns for two different
inheritance hierarchies. StrategyModalWindow's `_window_init_bypassed`
instance flag is part of its contract with subclasses.

---

## Cross-Class Pattern Trace

```
RaceSetupScreen (canonical PoC):
  _init_state → _init_widget_refs → delegates → bypass? → super() → builder

NewGameSetupScreen:
  _init_state → _init_widget_refs → delegates → bypass? → super() → builder
  (same structure, different inheritance)

StrategyModalWindow + BuildQueueListWindow:
  [subclass: cheap state → super().__init__()]
    └─ [base: bypass? → early-return | super().__init__ register_modal]
  [subclass: _window_init_bypassed? → builder? → return | builder]

StrategyModalWindow + OrdersWindow:
  [subclass: cheap state → super().__init__()]
    └─ [base: bypass? → early-return | super().__init__ register_modal]
  [subclass: _window_init_bypassed? → builder? → return | builder]

StrategyModalWindow + FleetReportWindow:
  [subclass: cheap state + delegates → super().__init__()]
    └─ [base: bypass? → early-return | super().__init__ register_modal]
  [subclass: _window_init_bypassed? → builder? → return | builder]

StrategyModalWindow + TransferDialog:
  [subclass: cheap state + delegates + query → super().__init__()]
    └─ [base: bypass? → early-return | super().__init__ register_modal]
  [subclass: _window_init_bypassed? → builder? → return | builder]
```

Two structural families visible:
1. **Direct UIWindow** (RaceSetupScreen, NewGameSetupScreen): inline bypass
   guard, `type(self).bypass_init` check.
2. **StrategyModalWindow subclasses** (4 classes): inherited bypass guard,
   `_window_init_bypassed` instance-flag check.

Both families satisfy all 4 PoC findings. The two-family split is a
consequence of the StrategyModalWindow base class being a *modal-tracking*
abstraction, not a general bypass-init abstraction. Refactoring the
bypass guard into a common `BypassableUIWindow` mixin would unify the
two families but is outside the scope of PROJ-325/328.

---

## Conclusion

The two-stage construction pattern is applied consistently and correctly
across all 7 audited classes. No CRITICAL or MAJOR findings. All 4 PoC
findings are verified against every class. The 7 MINOR findings are
either justified architectural choices or low-priority stylistic
inconsistencies.

No regressions, no pattern breaks, no missed implementations.
