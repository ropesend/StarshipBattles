# Decomposition Design: test_run_details.py

**Current size:** 960 lines (one class, `TestRunDetailsPanel`)
**Target post-split:** every resulting module <500 lines
**Sibling-aware:** `game/ui/screens/test_lab/renderer.py` (1195 lines) is being decomposed in parallel — we should not modify it but should mirror its idioms (read state, do not mutate; per-section draw methods; rect outputs stored on the panel for input handler use).

> **Last verified:** 2026-04-27 — Design walkthrough against the live file at `game/ui/screens/test_lab/test_run_details.py`.

---

## Current responsibilities

The file is a single 960-line `TestRunDetailsPanel` class. Internally it has very clear, separable concerns. Line ranges below are accurate against the read of the file.

- **L19–58 — Construction / theming / font cache / scroll & callback wiring.** Holds `selected_run`, `ScrollState`, three button-rect slots, three callback hooks (`on_view_states`, `on_use_seed`, `on_copy_results`).
- **L60–69 — Run binding / clear.** `set_run`, `clear`.
- **L71–91 — Scroll height calculation.** `_calculate_scroll` — content height depends on phase header count, metric count, validation result count.
- **L93–126 — Event routing.** `handle_event` — three button hit-tests + mousewheel scroll inside the panel rect. **Public contract.**
- **L128–177 — Top-level `draw()` orchestrator.** Frames, clipping, scroll offset arithmetic, dispatch to nine `_draw_*` helpers. **Public contract.**
- **L179–198 — `_draw_header_and_status`.** Run number, timestamp, big PASSED/FAILED badge.
- **L200–218 — `_draw_metadata`.** Seed + Ticks small line.
- **L220–310 — `_draw_action_buttons`.** Three action buttons (View States / Use Seed / Copy Results), with hover state and visibility-clipping logic. Stores the three `*_button_rect` slots that `handle_event` consumes.
- **L312–335 — `_draw_metrics`.** Generic key/value list of `run_record.metrics` (excluding nested keys).
- **L337–395 — `_draw_validation_results`.** Phase-grouped check list (DATA / PRECONDITION / OUTCOME) with phase headers. **CRITICAL UI CONTRACT** — this is where green/red-flag, expected-vs-actual results live (per `feedback_combat_lab_ui.md`).
- **L397–488 — `_draw_single_validation`.** Per-check renderer: V/X/! glyph, name (color-coded), Expected / Actual / Difference / p-value / Detail rows, separator. **CRITICAL UI CONTRACT.**
- **L490–533 — `_draw_numeric_difference`.** Difference/percentage row with EXACT MATCH detection and pass/fail coloring.
- **L535–543 — Test-type predicates.** `_is_propulsion_test` / `_is_resource_test` (keyed off `test_id` prefix).
- **L545–584 — `_draw_resource_outcomes` dispatch.** RESOURCE-001..003 → fuel; RESOURCE-004..005a → energy; else (006..008) → ammo. Section header + separator.
- **L586–649 — `_draw_fuel_outcomes`.** Initial / Final / Consumed / Expected / tolerance check / Final Velocity. Pass/fail color on tolerance.
- **L651–710 — `_draw_energy_outcomes`.** Initial / Final / Consumed / Shots Fired / Damage Dealt / Energy-per-Damage. "Depleted" warning state.
- **L712–777 — `_draw_ammo_outcomes`.** Initial / Final / Consumed / Shots-or-Launches (RESOURCE-008 seekers branch) / Damage Dealt. "Depleted" warning state.
- **L779–818 — `_draw_propulsion_outcomes` dispatch.** Section header, decides turn-test vs motion-test vs stationary based on metrics.
- **L820–863 — `_draw_motion_outcomes`.** Velocity / Position / Distance.
- **L865–925 — `_draw_turn_outcomes`.** Angle / Expected / Actual (color-coded by error) / Error / Turn Speed.
- **L927–948 — `_draw_stationary_outcomes`.** Velocity 0 / Distance 0.
- **L950–960 — `_draw_scrollbar`.** Right-edge scroll thumb.

Two clusters dominate by LOC:

| Cluster | Approximate LOC | Notes |
|---------|-----------------|-------|
| Resource outcomes (`_is_resource_test` + `_draw_resource_outcomes` + 3 sub-renderers) | ~240 | RESOURCE-### specific |
| Propulsion outcomes (`_is_propulsion_test` + `_draw_propulsion_outcomes` + 3 sub-renderers) | ~170 | PROP-### specific |
| Validation results (header + per-check + numeric diff) | ~200 | UI contract zone |
| Buttons + scrollbar + frame | ~190 | Generic chrome |
| Header / metadata / metrics | ~80 | Top of card |

The file is essentially **a generic results frame + two test-family-specific outcome renderers + a validation-check renderer**. Splitting along those seams gives a clean MVVM-style breakdown.

---

## Proposed sub-modules

All under a new subpackage `game/ui/screens/test_lab/details/`. Subpackage rather than flat because there will be 5 closely-related files that only this panel uses (per §2.3 "3+ closely related files").

### 1. `details/panel.py` — `TestRunDetailsPanel` (the orchestrator)

- **Path:** `game/ui/screens/test_lab/details/panel.py`
- **Responsibility:** Public class. Owns state (`selected_run`, `scroll`, button rects, callbacks). Implements `set_run`, `clear`, `handle_event`, `draw`. The `draw` method delegates each section to a helper module — it is the only thing that knows the section ordering and y-cursor flow.
- **Symbols:** `TestRunDetailsPanel` (only).
- **Estimated LOC:** ~180 (constructor + set_run/clear + calc_scroll + handle_event + draw + scrollbar).
- **Depends on:** `details.chrome`, `details.validation`, `details.resource_outcomes`, `details.propulsion_outcomes`, `pygame`, `game.ui.fonts`, `game.ui.colors`, `theme`, `ScrollState`.

### 2. `details/chrome.py` — Generic frame (header/metadata/buttons/metrics/scrollbar)

- **Path:** `game/ui/screens/test_lab/details/chrome.py`
- **Responsibility:** Test-family-agnostic chrome — header & PASSED/FAILED badge, seed+ticks metadata line, three action buttons (with hit-rect output), generic metrics list, scrollbar. These are all things every test type shows.
- **Symbols (free functions, all take `ctx` — see "Shared draw context" below):**
  - `draw_header_and_status(ctx, run_record, run_number, y_offset) -> int`
  - `draw_metadata(ctx, run_record, y_offset) -> int`
  - `draw_action_buttons(ctx, run_record, y_offset) -> ActionButtonRects` (returns the three rects so the panel can store them on `self`)
  - `draw_metrics(ctx, run_record, y_offset) -> int`
  - `draw_scrollbar(ctx) -> None`
  - `@dataclass ActionButtonRects: view_states, use_seed, copy_results`
- **Estimated LOC:** ~210 (button block dominates at ~90).
- **Depends on:** `theme`, `pygame`, `game.core.string_utils.display_name`.

### 3. `details/validation.py` — Validation results (UI-contract zone)

- **Path:** `game/ui/screens/test_lab/details/validation.py`
- **Responsibility:** Phase grouping (DATA/PRECONDITION/OUTCOME), per-check renderer, numeric-difference renderer. **This is the green/red flag, expected-vs-actual contract from `feedback_combat_lab_ui.md` — do not change behavior, only relocate.**
- **Symbols:**
  - `draw_validation_results(ctx, run_record, y_offset) -> int`
  - `draw_single_validation(ctx, vr, y_offset) -> int` (kept module-private behind the public `draw_validation_results`, but exported for unit-test reach)
  - `draw_numeric_difference(ctx, expected, actual, status, y_offset, indent, label_width) -> int`
  - `_PHASE_ORDER`, `_PHASE_LABELS`, `_PHASE_COLORS` (module constants — currently inline in the method).
- **Estimated LOC:** ~210.
- **Depends on:** `theme`, `pygame`, `formatting_utils.format_value`, `game.ui.colors.TEST_PASS/TEST_FAIL`.

### 4. `details/resource_outcomes.py` — RESOURCE-### family

- **Path:** `game/ui/screens/test_lab/details/resource_outcomes.py`
- **Responsibility:** Resource consumption section. Test-id dispatch + three sub-renderers (fuel / energy / ammo).
- **Symbols:**
  - `is_resource_test(run_record) -> bool`
  - `draw_resource_outcomes(ctx, run_record, y_offset) -> int`
  - `_draw_fuel_outcomes(ctx, metrics, y_offset, palette) -> int`
  - `_draw_energy_outcomes(ctx, metrics, y_offset, palette) -> int`
  - `_draw_ammo_outcomes(ctx, metrics, y_offset, palette, test_id) -> int`
- **Estimated LOC:** ~250.
- **Depends on:** `theme`, `pygame`.

### 5. `details/propulsion_outcomes.py` — PROP-### family

- **Path:** `game/ui/screens/test_lab/details/propulsion_outcomes.py`
- **Responsibility:** Propulsion outcomes section. Heuristic dispatch (turn / motion / stationary) + three sub-renderers.
- **Symbols:**
  - `is_propulsion_test(run_record) -> bool`
  - `draw_propulsion_outcomes(ctx, run_record, y_offset) -> int`
  - `_draw_motion_outcomes(ctx, metrics, y_offset, palette) -> int`
  - `_draw_turn_outcomes(ctx, metrics, y_offset, palette) -> int`
  - `_draw_stationary_outcomes(ctx, metrics, y_offset, palette) -> int`
- **Estimated LOC:** ~180.
- **Depends on:** `theme`, `pygame`.

### 6. `details/draw_context.py` — Shared draw context dataclass

- **Path:** `game/ui/screens/test_lab/details/draw_context.py`
- **Responsibility:** Frozen dataclass passed to every helper. Carries `surface`, `panel` (for `x`, `y`, `width`, `height`, `scroll`), and the four font handles + the standard color palette. Avoids 8-positional-arg helper signatures and keeps helpers stateless.
- **Symbols:**
  - `@dataclass(frozen=True) DetailsDrawContext`: `surface`, `x`, `y`, `width`, `height`, `title_font`, `header_font`, `body_font`, `small_font`, `pass_color`, `fail_color`, `header_color`, `text_color`, `button_color`, `button_hover_color`.
  - `@dataclass(frozen=True) OutcomePalette`: `label_color`, `value_color`, `highlight_color`, `indent`, `label_width` — the bag of constants currently passed positionally to fuel/energy/ammo helpers.
- **Estimated LOC:** ~50.
- **Depends on:** stdlib only.

### 7. `details/__init__.py` — Subpackage entry

- **Path:** `game/ui/screens/test_lab/details/__init__.py`
- **Responsibility:** Re-exports `TestRunDetailsPanel` (Option A — see below) so existing import sites keep working.
- **Symbols:** `TestRunDetailsPanel`.
- **Estimated LOC:** ~5.

### Total estimated LOC

| Module | LOC |
|---|---:|
| `details/panel.py` | 180 |
| `details/chrome.py` | 210 |
| `details/validation.py` | 210 |
| `details/resource_outcomes.py` | 250 |
| `details/propulsion_outcomes.py` | 180 |
| `details/draw_context.py` | 50 |
| `details/__init__.py` | 5 |
| **Total** | **~1085** |

Each module is **comfortably below 500 LOC** and has a single reason to change. The total is slightly above the original 960 because of the dataclasses, the per-file imports, and the public-helper docstrings — the standard cost of a clean MVVM-style split.

---

## Public API surface

**Single externally-visible symbol:** `TestRunDetailsPanel`.

**Callers (full grep result):**

| File | Lines | What it does |
|---|---|---|
| `game/ui/screens/test_lab/panel_manager.py` | L14 import; L193 instantiation | Constructs the panel and wires the three callbacks (`on_view_states`, `on_use_seed`, `on_copy_results`). |
| `game/ui/screens/test_lab/results_panel.py` | L37, L57 | Holds a reference and calls `details_panel.clear()` / (elsewhere) `set_run(...)`. |
| `game/ui/screens/test_lab/__init__.py` | L15 | Documentation comment only — no import. |

That's it — **two real call sites**, both inside the same package. No code outside `game/ui/screens/test_lab/` constructs or types `TestRunDetailsPanel`.

The public method surface that callers depend on:
- Constructor `(x, y, width, height)`
- `set_run(run_record, run_number)`
- `clear()`
- `handle_event(event) -> bool`
- `draw(surface)`
- Attributes `on_view_states`, `on_use_seed`, `on_copy_results` (set by `panel_manager`)

This surface must be preserved exactly.

---

## Caller-update strategy

**Choice:** **Option A — re-export shim.**

**Justification:**

1. The current import is `from .test_run_details import TestRunDetailsPanel` in `panel_manager.py`. After the split, the canonical location becomes `game.ui.screens.test_lab.details` (the subpackage). A 4-line shim file at the original path —

   ```python
   # game/ui/screens/test_lab/test_run_details.py
   from game.ui.screens.test_lab.details import TestRunDetailsPanel
   __all__ = ["TestRunDetailsPanel"]
   ```

   keeps the existing import working with zero churn at the call site.

2. Although there are only two real callers, the module name `test_run_details` is referenced in seven non-code locations (README, manifest, conventions doc, the `__init__.py` doc string, etc.). Keeping the shim means we don't have to revisit any of that prose in this commit, and PROJ-309 itself can decide later whether to delete the shim.

3. The cost of Option A is one ~5-line file. The benefit is that the docstring in `test_lab/__init__.py` (L15) and `README.md` (L24, L44) keep referring to a file that still exists.

4. **Migration plan to ultimately remove the shim** (out of scope for this design, listed for completeness): update the two call sites in `panel_manager.py` and `results_panel.py` plus the prose in `README.md` and `__init__.py`, then delete the shim. Trivial follow-up.

---

## Test plan

### Existing tests affected

A grep of `tests/` for `TestRunDetailsPanel` and `test_run_details` returns **zero matches** in the tests tree (the only matches are documentation and project files). This panel currently has no direct unit tests — its behavior is covered indirectly by Combat Lab smoke runs.

That means:
- No tests need to be edited to land the split.
- The split is the right opportunity to **add** the small set of contract tests below.

### New contract tests

Add `tests/unit/ui/screens/test_lab/details/` with:

1. `test_validation_render_contract.py` — instantiate a `TestRunDetailsPanel`, build a `run_record` stub with one PASS check and one FAIL check carrying `expected`/`actual`, render to an off-screen surface, and assert (via pixel sampling or — preferably — by capturing draw calls through a `pygame.Surface` mock):
   - PASS row text color matches `TEST_PASS`.
   - FAIL row text color matches `TEST_FAIL`.
   - Both "Expected:" and "Actual:" labels are blitted.
   - The "Difference:" row is blitted when both values are numeric.
   This is the protection for the `feedback_combat_lab_ui.md` UI contract.

2. `test_outcome_dispatch.py` — assert that `is_resource_test` returns True for `RESOURCE-001` and False for `PROP-001`/`BEAMWEAPON-001`; symmetric for `is_propulsion_test`. This pins the prefix-based dispatch.

3. `test_resource_outcomes_branches.py` — drive `draw_resource_outcomes` with synthetic metrics for each of the three sub-branches (fuel / energy / ammo seeker / ammo non-seeker) and assert each branch reaches the expected sub-renderer (mock the sub-renderers at module level).

4. `test_propulsion_outcomes_branches.py` — same shape for the turn / motion / stationary trichotomy.

5. `test_action_button_callbacks.py` — set `on_view_states` / `on_use_seed` / `on_copy_results` to mock callables, render once to populate the button rects, post a synthetic `MOUSEBUTTONDOWN` at each rect, and assert each callback fires exactly once with the expected payload.

6. `test_panel_module_size.py` (small static guard) — `assert each module under details/ is < 500 LOC` so the file budget stays enforced.

These are TDD-correct: write each test before relocating the corresponding code, watch it pass against the original `test_run_details.py` (since the new modules just relocate behavior), then move the code and watch it still pass. No new behavior is introduced.

### Manual smoke checklist

In the Combat Lab UI, after the split:

- [ ] Run BEAMWEAPON-001 once. Click the run in the history list. **Detailed Test Results panel** must show:
  - [ ] "DETAILED TEST RESULTS" panel title.
  - [ ] "Run #1 - <timestamp>" header.
  - [ ] Big "PASSED" or "FAILED" status badge in correct color.
  - [ ] "Seed: ###" and "Ticks: ###" metadata line.
  - [ ] **View States**, **Use Seed**, **Copy Results** buttons all present, hover-highlight, and fire the right action.
  - [ ] "Test Metrics" section listing every key in `run_record.metrics`.
  - [ ] "VALIDATION RESULTS" header with phase sub-headers (DATA / PRECONDITION / OUTCOME) in the right colors.
  - [ ] Each check shows V or X glyph in the right color, name color-coded, "Expected:" / "Actual:" / "Difference:" rows, "p-value:" when statistical, "Detail:" when present.
  - [ ] "EXACT MATCH" rendered for diff < 1e-9.
  - [ ] Subtle separator between check items.
- [ ] Run a PROP-### test (e.g. PROP-001-MOTION). Confirm the **TEST OUTCOMES** section appears between metadata and metrics, with Velocity / Position / Distance lines.
- [ ] Run a turn-style propulsion test (e.g. PROP-002). Confirm the Angle / Expected / Actual / Error / Turn Speed block, with Actual color-coded by error.
- [ ] Run a stationary propulsion test. Confirm the "0.0 (stationary)" / "0 px" block.
- [ ] Run RESOURCE-001 (fuel). Confirm Initial / Final / Consumed / Expected / "Within tolerance" or "Difference: …" / Final Velocity.
- [ ] Run RESOURCE-004 (energy). Confirm Initial / Final / Consumed / Shots Fired / Damage Dealt / Energy/Damage. "0 (depleted)" warning when energy is exhausted.
- [ ] Run RESOURCE-006 (ammo, non-seeker). Confirm Shots Fired + Damage Dealt.
- [ ] Run RESOURCE-008 (ammo, seeker). Confirm "Launches:" + the "(Hits not tracked - seekers in flight)" note.
- [ ] Scroll the panel — scrollbar thumb visible on the right edge, mousewheel works only when the cursor is inside the panel.
- [ ] Click outside the panel — no crash, scroll doesn't change.

---

## Risks

### Sub-panel coupling via shared state

- **Y-cursor flow:** Today `draw()` is a single linear march of integer y-offsets. After the split, each helper still consumes & returns an `int` y-offset, so the flow stays identical — but the panel orchestrator `draw()` becomes the only place that knows the section order and the inter-section padding. **Mitigation:** the orchestrator stays in `panel.py` exactly as today; helpers stay pure of section-order knowledge.
- **Button rects mutated by render:** `_draw_action_buttons` writes to `self.view_states_button_rect` / `self.use_seed_button_rect` / `self.copy_results_button_rect`, which `handle_event` reads. After the split, the helper returns an `ActionButtonRects` dataclass and the panel stores it. **Mitigation:** the dataclass keeps the three names identical to the existing attributes, so `handle_event` can keep its three-rect hit-test exactly as written.
- **Scroll offset in button positioning:** `_draw_action_buttons` reads `self.scroll.offset` to compensate for the scroll position so buttons stay anchored relative to the panel. The helper will receive the panel via the draw context, not just `surface`. **Mitigation:** the `DetailsDrawContext` carries the panel rect & scroll state.

### Existing UI feature contract preserved

- `feedback_combat_lab_ui.md` is explicit: every check must show V/X with right color, every expected/actual must show, every difference must show. **All of that lives in `_draw_validation_results` / `_draw_single_validation` / `_draw_numeric_difference` and moves verbatim into `details/validation.py`.** No logic is rewritten — only relocated.
- The "PASSED"/"FAILED" big-text status, the green/red color split, the per-phase colors, the "EXACT MATCH" / "essentially exact" / `±%` formatting — all preserved character-for-character.
- The contract test list above explicitly pins these.

### Renderer split alignment (sibling concern)

- The sibling decomposition of `renderer.py` (the *outer* Combat Lab renderer, separate concern from this panel) may also extract per-section helpers. The two splits do not share files and do not share helper names, so there is no merge conflict risk. **Flag for cross-review:** if `renderer.py` introduces a `DrawContext` dataclass, we should consider unifying it with `DetailsDrawContext` in a follow-up — but **not in this commit.** Drop a note in the open questions below.

### Forward-compat for new test families

- Today the `_is_*` predicates and the resource/propulsion outcome modules are hard-coded to `RESOURCE-` / `PROP-`. After the split, adding (e.g.) a new `SHIELD-` outcome family is a new sibling module + one branch in `panel.py.draw`. No worse than today, slightly cleaner because the panel orchestrator's section-list is now the only place that knows.

---

## Open questions

1. **Cross-review with `renderer.py` split.** Should the eventual `DetailsDrawContext` (mine) and any `RenderContext` extracted from `renderer.py` be unified? Likely yes in a follow-up, but I am not coordinating live with that work — **flagging for the PROJ-309 lead to merge after both designs land.**
2. **Type annotations modernisation.** PROJ-311 mandates 100% return-type coverage, which the current file mostly satisfies but with some `Any` returns (e.g. `_draw_header_and_status -> Any`). I would correct these to `-> int` (the actual return) when relocating. Confirm that's in scope for PROJ-309 (I read it as yes — it's a mechanical improvement during a structural change).
3. **Should `formatting_utils.format_value` move into `details/`?** It's currently used only by `test_run_details.py` and `test_run_card.py`. Since `test_run_card.py` also uses it, I'm leaving it where it is. Flag in case the renderer split also touches it.
4. **Should we delete the shim at the same time as the split?** I've recommended Option A above. The two real callers can be migrated in the same commit without much extra cost — happy to flip to Option B if the project prefers eradication-on-introduction (per the project's "system migration policy"). My weak preference is shim now / migrate in a tiny follow-up, but it's a judgement call. **Flagging for the PROJ-309 lead.**
