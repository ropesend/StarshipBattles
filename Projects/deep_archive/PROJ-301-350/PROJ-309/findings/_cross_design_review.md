# PROJ-309 Phase 2.11 Cross-Design Review

**Reviewed:** 2026-04-27
**Reviewer:** Cross-design review pass over 10 sibling design docs.
**Docs reviewed:**

1. `race_setup_screen_decomposition.md` (current 1598 LOC)
2. `strategy_renderer_decomposition.md` (current 1208 LOC)
3. `test_lab_renderer_decomposition.md` (current 1195 LOC)
4. `core_protocols_decomposition.md` (current 1087 LOC)
5. `command_handlers_decomposition.md` (current 1076 LOC)
6. `test_run_details_decomposition.md` (current 960 LOC)
7. `strategy_session_facade_decomposition.md` (current 928 LOC)
8. `workshop_viewmodel_decomposition.md` (current 873 LOC)
9. `app_decomposition.md` (current 855 LOC)
10. `strategy_window_manager_decomposition.md` (current 817 LOC)

---

## Summary

- **Overall verdict: APPROVE WITH FIXES.** All 10 designs are template-complete, the Option A/B reasoning is justified in every case, and the LOC budget is respected almost everywhere. Two pre-Phase-3 fixes are required (LOC pre-decision on `core/protocols/strategy.py`; cross-renderer convention alignment) and a handful of open questions need a single-vote answer before Phase 3 starts.
- Design docs missing template sections: **0**
- LOC budget violations or borderlines: **1** (`core/protocols/strategy.py` self-flagged at ~520 LOC)
- Cross-design conflicts found: **2** (renderer subpackage naming convention; potential test-lab `_draw_helpers` duplication)
- Escalation-worthy open questions: **8** (compiled below)

---

## Per-doc compliance

Legend: ✓ = section present and useful; ~ = present but thin; ✗ = missing.

| Doc | Template complete? | LOC budget OK? | Option A/B justified? | Risks covered? |
|---|---|---|---|---|
| race_setup_screen | ✓ all 7 sections; line ranges given for all 18 concerns | ✓ all sub-modules ≤450; controller 420 documented as concentrated mutation per §2.4 | ✓ Option A — also splits into Option A (RaceSetupScreen) + Option B (leaked RaceBrowserDialog import) with specific reasoning | ✓ test-patch breakage flagged, ownership rules enumerated, import-cycle DAG traced, no missing categories |
| strategy_renderer | ✓ all 7; line ranges throughout | ✓ every module ≤230 LOC | ✓ Option A "composer-style" — explains why this is *not* a graveyard shim | ✓ flags `screen_diameter` latent bug at L846/854; flags `_temp_screen_pos`/`_temp_draw_r` smell on domain models; polar-angle duplication with click_dispatcher |
| test_lab_renderer | ✓ all 7; line ranges throughout | ✓ all modules ≤210 (largest metadata_panel ~160) | ✓ Option A — also explains the test-compat shim for class-level `_format_check_pair`/`_is_condition_verified` access | ✓ flags hidden viewmodel rect contract; documents y-cursor flow coupling; documents test-compat shim as known debt |
| core_protocols | ✓ all 7; line ranges per-symbol in a table | **~ borderline:** `strategy.py` self-flagged at ~520 LOC with a fallback split (`strategy_entities.py` + `strategy_domain.py`) but no upfront decision | ✓ Option A justified by 132 imports / 80 files | ✓ flags `_has_attrs` private-public ambiguity; flags `ILocatable`/`INamed`/`IOwnable` dead-mixin question; flags TypeGuard/Protocol pairing rule |
| command_handlers | ✓ all 7; line ranges per-handler | ✓ all modules ≤230 LOC | ✓ Option A justified by ~30 import sites; explains hybrid (Option B for sibling handlers internal to package) | ✓ flags `planet_command_handlers.py` deferred-import pattern as cleanup opportunity; documents zero cross-handler dependencies |
| test_run_details | ✓ all 7; line ranges throughout | ✓ all modules ≤250 | ✓ Option A justified by package-internal callers + prose references in README | ✓ y-cursor flow risk; button-rect attr contract; UI-contract preservation per `feedback_combat_lab_ui.md` |
| strategy_session_facade | ✓ all 7; methods enumerated by line range | ✓ all slices ≤280 LOC composer included | ✓ Option A justified by 53-method public surface + tests asserting on private cache attrs | ✓ slice-to-slice coupling enumerated with specific cases; cache-invalidation contract documented |
| workshop_viewmodel | ✓ all 7; line ranges throughout | ✓ all modules ≤310 (core slimmed to 310) | ✓ Option A justified — viewmodel IS the MVVM seam; rejects splitting public surface | ✓ selection state ownership rules; modifier-sync circular concern; PROJ-282 §1.6 contract preserved |
| app | ✓ all 7; line ranges throughout, plus an "Execution sequencing notes" annex (bonus) | ✓ all modules ≤340 | ✓ **Option B** justified: only 5 import sites in tree, none need to change — *real* clean-API not a shim | ✓ HIGH-risk bootstrap order documented; flags `ResourceCatalog.from_json()` called twice; overlay-flag ownership question raised; profiler shutdown order flagged |
| strategy_window_manager | ✓ all 7; line ranges per banner-section | ✓ all modules ≤180 (composition root largest) | ✓ Option A justified — composition root is real first-class object, not graveyard | ✓ flags `planet_abilities_window` missing None-init / has_modal_open omission; deferred-import pattern preservation; closure-capture regression risk |

**Verdict: every doc is template-complete and risk-aware.** No doc needs to be re-sent. Two need explicit decisions before Phase 3 (see "Recommended fixes" below).

---

## LOC budget concerns

### `core/protocols/strategy.py` ~520 LOC — must decide upfront

The `core_protocols_decomposition.md` doc estimates **~520 LOC** for `strategy.py` (the merged strategy.entities + strategy.domain bucket). It declines to commit and says:

> "Borderline. May exceed the 500 cap. … if the actual split lands above 500, fall back to the two-file plan: `strategy_entities.py` (IStarSystem, IStar, IPlanet, IOrderable, IZoneOccupant, IFleet, IWarpPoint, ISectorEnvironment, IStorm + their guards, ~340 LOC) and `strategy_domain.py` (IEmpire, IFacility, IRaceRegistry, IShipInstance + their guards, ~180 LOC)."

This "decide later" stance is wrong for a Phase-2 design doc. Phase 3 should not have to discover a budget violation in-flight. The natural seam is already identified (entities vs domain). The pre-split layout (`strategy_entities.py` + `strategy_domain.py`) costs nothing extra — both files are well under 500, both have a clean cohesive boundary (PROJ-238 entity protocols vs PROJ-193 domain protocols), and the package-level `__init__.py` shim re-exports both transparently.

**Recommendation: pre-split.** Land the package as 9 files (rather than 8) from the start: `common.py`, `registry.py`, `strategy_entities.py`, `strategy_domain.py`, `combat.py`, `boundary.py`, `ui.py`, `persistence.py`, `__init__.py`. Phase 3 gains zero risk; design clarity gains a lot.

### Other budget notes (acceptable, no action needed)

- `race_setup_screen` controller at ~420 LOC: justified per `docs/03_CONVENTIONS.md` §2.4 (controllers with 15+ mutation methods can legitimately exceed 300 within ≤500). Documented honestly. No action.
- `strategy_session_facade` composer at ~280 LOC: 53 public-method forwarders are unavoidable; the doc considered `__getattr__` auto-forwarding and rejected it for valid reasons (IDE autocomplete + type hints). No action.
- `app_decomposition` `screen_router.py` at ~340 LOC: doc explicitly flags a fallback (extract `_handle_*_action` methods to `screen_router_actions.py`) if it overshoots in implementation. Acceptable Phase-3 contingency.
- `command_handlers` `construction_queue.py` at ~225 LOC: comfortably under budget despite housing the largest single handler.

---

## Cross-design overlaps and conflicts

### Conflict 1: Renderer subpackage naming convention diverges between siblings

Two parallel renderer splits chose different layouts:

- **`strategy_renderer.py`** → new package `game/ui/screens/strategy_render/` (singular `_render`), original file rewritten as the composer.
- **`test_lab/renderer.py`** → new package `game/ui/screens/test_lab/renderer/` (sibling subdir of the original file), with the original file becoming a 5-line shim.

The `test_lab_renderer` doc (Open Question §1) explicitly flags this and asks for cross-alignment. `strategy_renderer` does not directly address the test-lab convention.

**Recommendation: align on `<screen>/renderer/` subpackage naming.** Specifically, prefer the `test_lab/renderer/` style. Apply the same to `strategy_renderer.py`: new package `game/ui/screens/strategy/renderer/` with the original `strategy_renderer.py` becoming a composer (or a shim importing from `strategy/renderer/composer.py`). Reasoning:

1. **Parallel structure across screens** is a stronger signal than the subtle hint in `_render` (singular implies "render layer subdirectories"). Future maintainers should see `<screen>/renderer/<concern>.py` everywhere.
2. The strategy-screen path already has a sibling `strategy_window_manager.py` going to `strategy_windows/`. So strategy-screen-related packages are: `strategy_render/` (renderer) and `strategy_windows/` (window manager). If we rename to `strategy/renderer/` we'd also want `strategy/windows/`. That's a bigger move than the current designs scope, so:

**Pragmatic compromise: keep both as proposed** (`strategy_render/` and `test_lab/renderer/`), but **document the convention** in `docs/03_CONVENTIONS.md` so future renderer splits don't proliferate yet a third style. Either choice is fine; what matters is that subsequent renderer splits choose the same one. Flag this for the user as a one-vote decision.

### Conflict 2: `test_lab/renderer/` and `test_lab/test_run_details/` both want a `_draw_helpers.py`

`test_lab_renderer_decomposition.md` proposes `renderer/_draw_helpers.py` (section/wrap/bullet primitives + validation flag).
`test_run_details_decomposition.md` does NOT propose a `_draw_helpers.py`, but its `details/validation.py` and `details/chrome.py` reimplement section text rendering.

The `test_lab_renderer` doc (Open Question §2) flags this:
> "After both splits land, `test_lab/renderer/` and `test_lab/test_run_details/` will both be subpackages. Consider whether `test_run_details` panel components could share `_draw_helpers.py` (section/wrap/bullet primitives). This is a follow-up consolidation — not a blocker for either split."

The `test_run_details` doc (Risk §3) also flags it:
> "If `renderer.py` introduces a `DrawContext` dataclass, we should consider unifying it with `DetailsDrawContext` in a follow-up — but **not in this commit.**"

**Recommendation: defer consolidation, but bake in the future seam now.** During Phase 3, the renderer split should land first. Once `renderer/_draw_helpers.py` exists at `game/ui/screens/test_lab/renderer/_draw_helpers.py`, the `test_run_details` split should import its section/bullet/wrap helpers from there rather than re-implementing them. This costs nothing extra, prevents code duplication from the moment of landing, and gives the user one fewer follow-up cleanup to track. The `DetailsDrawContext` and any renderer `RenderContext` can stay separate for now (different shapes — panel-level vs section-level). Update the `test_run_details` design before its sub-phase to import helpers from `renderer/_draw_helpers.py`.

### Other observed alignments (no conflict)

- **`race_setup_screen` MVVM deviation from sketch.** The doc explicitly refutes the design.md sketch (`genome_panel.py / traits_panel.py / ...`) and applies the PROJ-282 MVVM split (`screen.py + controller.py + view_model.py + input_handler.py + renderer.py`) — same shape as `battle_setup/`. **This is internally consistent with PROJ-282 and is the right call.** No other UI-screen split currently chooses a MVVM-style decomposition (the others split by panel or render-layer), but those screens are not god-screens of the same shape. The deviation is well-justified by the doc's "panels are already extracted" finding. Approve.

- **`strategy_window_manager.py` (`strategy_windows/`) and `strategy_renderer.py` (`strategy_render/`).** Both target sibling files in `game/ui/screens/`. They share no code. Risk only for `strategy_ui.py`, which both projects' shim layer touches indirectly — coordinate merge order during Phase 3 (see "Phase 3 sequencing recommendation" below). The `strategy_window_manager` doc calls this out (Risk §6).

- **`app.py` (Option B)** — only file using Option B. Doc justifies: only 5 import sites in source tree; `Game` and `main` stay as public symbols at `game/app.py`; the Option B is "no caller migration needed because the public symbols don't move." This is sound — it's not really Option B in the same sense the other docs use it (no "callers updated"); it's "internal restructure with zero external API change." Consistent with the project goal.

---

## Inconsistencies in Option A/B reasoning

**Overall: consistent. All 10 docs justify their choice with caller counts, and the choices are coherent.**

Spot-check audit:

| Doc | Option | Caller count | Justification quality |
|---|---|---|---|
| race_setup_screen | A | 2 prod + 1 test | Could have been B; A chosen for shim-cost-zero. Honest. |
| strategy_renderer | A | 1 prod + 2 tests | Borderline-B; A chosen because composer-style A is "not a graveyard". Honest. |
| test_lab_renderer | A | 1 prod + 1 test | A required by class-level method shim for `_format_check_pair`. Sound. |
| core_protocols | A | 132 imports / 80 files | Mandatory A. Sound. |
| command_handlers | A | ~30 sites (1 prod, rest tests/siblings) | A chosen + explained as hybrid (B for siblings internal to package). Sound. |
| test_run_details | A | 2 prod (both same package) | Could have been B; A chosen for prose-reference preservation. Acceptable. |
| strategy_session_facade | A | 30 files; tests assert on private attrs | Mandatory A. Sound. |
| workshop_viewmodel | A | 5 prod + 23 tests | A is internal restructure — public class stays. Sound. |
| app | B | 5 sites | B because public symbols (`Game`, `main`) stay at `game/app.py`. Sound. |
| strategy_window_manager | A | 30+ sites across 5+ files | A chosen + composition root rationale. Sound. |

**Single mild concern:** `test_run_details_decomposition.md` Open Question §4 wavers ("happy to flip to Option B if the project prefers eradication-on-introduction"). Since the file has only 2 callers in the same package, **Option B would arguably better satisfy the System Migration Policy** (don't create a shim that has to be deleted later). But the chosen Option A is defensible. Recommend: leave Option A; commit to deleting the shim in a follow-up ticket created at the time of landing, so it doesn't drift.

---

## Latent bugs surfaced (for Phase 3 to triage)

Listed by source doc. Phase 3 must explicitly decide for each: preserve / fix / file follow-up.

1. **`strategy_renderer.py` L846, L854 — `screen_diameter` undefined name.** Source: `strategy_renderer_decomposition.md` Risks §"`screen_diameter` undefined name". Pre-existing latent bug in `_draw_dyson_spheres`. The owner-flag fallback path raises `NameError` if reached. Phase 3 recommendation: **file as a separate ticket** — fix outside this decomposition to avoid mixing semantic and structural changes.

2. **`strategy_renderer.py` `_temp_screen_pos` / `_temp_draw_r` painted onto domain objects (L740-741).** Source: `strategy_renderer_decomposition.md` Risks §"Shared mutable rendering state" and Open Question §3. Renderer attaches transient layout fields directly onto planet domain objects. Phase 3 recommendation: **fix in this decomposition** — confine to `systems.py` extraction, replace with a local `dict[planet_id, (pos, radius)]`. Doc author leans toward fixing per CLAUDE.md Rule 3.

3. **`strategy_window_manager.py` `planet_abilities_window` slot not None-initialized + missing from `has_modal_open()`.** Source: `strategy_window_manager_decomposition.md` Risks §4 + Open Question §4. Created on first `open_planet_abilities_window` call without an `__init__` declaration. The modal-detection chain ignores the slot. Phase 3 recommendation: **fix in this decomposition** — two lines, eliminates an inconsistency the new structure would otherwise inherit.

4. **`strategy_renderer.py` polar-angle duplication with `strategy_click_dispatcher.py:448`.** Source: `strategy_renderer_decomposition.md` Open Question §4. Comment in dispatcher says "must match strategy_renderer.py Rev 5 values." Phase 3 recommendation: **fix in this decomposition** — extract `compute_planet_group_angles(count)` into `strategy_render/planets.py` and have the click dispatcher import it. One-liner that closes a real correctness risk.

5. **`app.py` `ResourceCatalog.from_json()` called twice in bootstrap.** Source: `app_decomposition.md` Risks §1 + Open Question §6. Once at line 160 (registry hydration), once at line 182 (`GameRegistries`). Phase 3 recommendation: **fix in this decomposition** — call once, pass twice. Tracked by the bootstrap-result dataclass contract.

6. **`new_game_setup_screen.py:405` leaked `RaceBrowserDialog` import via `race_setup_screen`.** Source: `race_setup_screen_decomposition.md` Public API surface §. The import works today only because `race_setup_screen.py` has `from … import RaceBrowserDialog` at module-top. Phase 3 recommendation: **fix in this decomposition** — `new_game_setup_screen.py` updated to import from `game.ui.screens.race_browser_dialog` directly. One-line change.

7. **`planet_command_handlers.py` 7 deferred imports of `BaseCommandHandler`.** Source: `command_handlers_decomposition.md` Risks §4. Suggests historical circular-dep workaround. After split, target moves to leaf-level `handlers/base.py`. Phase 3 recommendation: **investigate during implementation; if cycle is gone, hoist to top-level** per CLAUDE.md Rule 3 ("don't preserve dead workarounds").

8. **`test_run_details.py` some `-> Any` return annotations should be `-> int`.** Source: `test_run_details_decomposition.md` Open Question §2. Cosmetic. Phase 3 recommendation: **fix during the move** — mechanical correction; PROJ-311 stipulates 100% return-type accuracy.

---

## Compiled open questions

Grouped by theme. Each entry: source doc(s) + question + reviewer recommendation.

### Theme A — Pre-split decisions for `core/protocols/`

**Q1 (HIGHEST PRIORITY).** Should `core/protocols/strategy.py` be pre-split into `strategy_entities.py` + `strategy_domain.py`?
- Source: `core_protocols_decomposition.md` Open Question §3.
- **Recommendation: YES — pre-split.** Land the package as 9 files. Detailed reasoning in "LOC budget concerns" above.

**Q2.** Should `_has_attrs` be renamed (drop the underscore)? Should it stay in `common.py` or move to `__init__.py`?
- Source: `core_protocols_decomposition.md` Open Question §2.
- **Recommendation:** keep underscored, place in `common.py`, re-export from `__init__.py` for back-compat. (As proposed by the doc.) Renaming would touch `simulation/interfaces/*` and `ai/protocols.py` — out of scope for size-driven decomposition.

**Q3.** Should `IRaceRegistry` live in `strategy.py` or `registry.py`?
- Source: `core_protocols_decomposition.md` Open Question §1.
- **Recommendation:** `strategy_domain.py` (per Q1 split). It groups with PROJ-193 domain protocols (`IEmpire`, `IFacility`, `IShipInstance`) and serves strategy-domain consumers.

### Theme B — Renderer / panel subpackage convention

**Q4.** What is the canonical naming convention for renderer subpackages?
- Source: `test_lab_renderer_decomposition.md` Open Question §1; `strategy_window_manager_decomposition.md` Open Question §3 indirectly.
- Choices: `<screen>_render/` (strategy doc proposal) vs `<screen>/renderer/` (test_lab doc proposal).
- **Recommendation:** keep both as proposed (different parents anyway: strategy is `game/ui/screens/strategy_render/` flat under `screens/`; test_lab is `game/ui/screens/test_lab/renderer/` nested under existing `test_lab/`). Document in `docs/03_CONVENTIONS.md` so the next renderer split picks one explicitly. No re-do of either design needed.

**Q5.** Should `test_lab/renderer/_draw_helpers.py` be shared with `test_lab/details/validation.py` and `test_lab/details/chrome.py`?
- Source: `test_lab_renderer_decomposition.md` Open Question §2; `test_run_details_decomposition.md` Risks §3 + Open Question §1.
- **Recommendation:** YES, but defer to **Phase 3 sub-phase ordering**: land renderer first; when test_run_details lands, import section/bullet/wrap helpers from `renderer/_draw_helpers.py` rather than re-implementing them. Costs nothing.

### Theme C — Renderer/details `RenderContext` / `DrawContext` unification

**Q6.** Should the eventual `DetailsDrawContext` (test_run_details), `RenderContext` (strategy_renderer), and any `RenderContext` from test_lab/renderer be unified?
- Source: `strategy_renderer_decomposition.md` (`context.py` proposal); `test_run_details_decomposition.md` Open Question §1; `test_lab_renderer_decomposition.md` Open Question §4.
- **Recommendation:** NO unification in PROJ-309. Different shapes serve different concerns (map render layer vs panel y-cursor vs panel-level theme). Sometimes a tactical `dataclass` per concern is the right answer. Document the three contexts in `docs/02_PATTERNS.md` if it becomes worth doing in a follow-up.

### Theme D — Shim deletion timeline

**Q7.** When should each Option-A shim be deleted?
- Source: `command_handlers_decomposition.md` Open Question §2; `test_run_details_decomposition.md` Open Question §4; `race_setup_screen_decomposition.md` Caller-update §; precedent (PROJ-297, PROJ-298).
- **Recommendation:** open a single follow-up project ticket "PROJ-3xx — PROJ-309 Shim Eradication" at the time the first sub-phase lands. Each shim's removal added to that ticket. Prevents drift.

### Theme E — In-decomposition cleanups vs follow-ups

**Q8.** For each latent bug surfaced (see "Latent bugs surfaced" above), fix during the decomposition or file as follow-up?
- Source: scattered across 5 docs.
- **Recommendation per item:**
  - `screen_diameter` (strategy_renderer): **follow-up ticket** — semantic vs structural separation.
  - `_temp_screen_pos` smell (strategy_renderer): **fix during decomposition** — confined to one extracted module.
  - `planet_abilities_window` None-init (strategy_window_manager): **fix during decomposition** — two lines.
  - polar-angle duplication (strategy_renderer ↔ click_dispatcher): **fix during decomposition** — one-line import.
  - `ResourceCatalog.from_json()` double-call (app): **fix during decomposition** — bootstrap is the natural place.
  - leaked `RaceBrowserDialog` import (race_setup_screen): **fix during decomposition** — one-line update.
  - deferred `BaseCommandHandler` imports (planet_command_handlers): **fix during decomposition if cycle no longer exists** — Rule 3.
  - `-> Any` annotations (test_run_details): **fix during decomposition** — mechanical PROJ-311 correction.

### Theme F — Smaller scope-line questions (no cross-design impact)

These can be decided by each sub-phase's implementer at execution time. Not blockers.

- `race_setup_screen`: extract `LLMDialogService`? Extract `ShipPreviewBuilder`? — both YES per author; Phase 3 confirm.
- `race_setup_screen`: move `race_validator.py` / `race_asset_loader.py` under `race_setup/`? — NO per author; defer.
- `app`: `_SCREEN_TRANSITIONS` location? — keep in `app.py` per author.
- `app`: move `main()` to `__main__.py`? — NO per author; keep in `app.py`.
- `app`: overlay-flag ownership (RunLoop vs ScreenRouter)? — defer to execution.
- `strategy_window_manager`: ShipPickerStub graduate to its own ticket? — YES, future ticket.
- `strategy_window_manager`: collapse `open_event_log` / `open_event_log_with_events`? — defer; out of scope for size split.
- `command_handlers`: move sibling handler files into `handlers/`? — NO per author; defer to a wider engine reorganization ticket.
- `strategy_session_facade`: should `_get_*_by_id` helpers live on `FacadeSessionState` or on slices? — author leans `FacadeSessionState`; reviewer agrees (eliminates slice-to-slice coupling). Phase 3 confirm.

---

## Recommended fixes before Phase 3 starts

Numbered, in priority order:

1. **`core_protocols_decomposition.md` — pre-split `strategy.py`.** Edit the doc to commit upfront to `strategy_entities.py` (~340 LOC) + `strategy_domain.py` (~180 LOC) instead of "fall back if measurement >500". Document `IRaceRegistry` in `strategy_domain.py`. Ensures Phase 3 has no in-flight budget surprises.

2. **Document the `<screen>_render/` vs `<screen>/renderer/` decision in `docs/03_CONVENTIONS.md` §2** (or wherever screen-package conventions live). Either pick one for future splits or formally declare both acceptable. Current design docs are self-consistent; the convention question is for the *next* renderer split, not these.

3. **Update `test_run_details_decomposition.md` to import section/bullet/wrap helpers from `test_lab/renderer/_draw_helpers.py`** when its sub-phase lands. Add a sentence to its design doc making this dependency explicit, plus a Phase 3 note that renderer must land first.

4. **Open the shim-eradication follow-up ticket placeholder** (`PROJ-3xx`) at the start of Phase 3 so each Option-A shim's deletion is tracked at landing, not after-the-fact.

5. **Confirm by user: latent-bug triage** per Theme E above. Eight items, each marked "fix in decomposition" or "follow-up". The user (or main agent) signs off, then Phase 3 proceeds with that triage in mind.

No design doc needs to be re-sent or fundamentally rewritten. Items 1–3 are minor edits. Items 4–5 are decisions, not document changes.

---

## Phase 3 sequencing recommendation

Ten sub-phases, one per file. Recommended landing order, lowest risk first:

1. **`core/protocols.py`** (sub-phase first). Mandatory Option A re-export shim. Pure type-definition file; no runtime behavior change. Lowest possible risk, broadest validation surface (every layer's tests exercise the imports). Confirms the Option-A shim infrastructure works before any harder split.

2. **`command_handlers.py`** (sub-phase second). Option A shim. ~17 handlers, each independently testable. Touched by recently-archived PROJ-298 (so the file is well-understood and stable). Strong test coverage in `tests/unit/strategy/test_command_handlers.py`. Independent of UI changes.

3. **`workshop_viewmodel.py`** (sub-phase third). Option A "internal restructure". No public API change. 23 test files exercise the public surface. Independent of all other splits.

4. **`strategy_session_facade.py`** (sub-phase fourth). Option A composer-pattern. Public surface preserved via forwarders. ~20 facade-specific test files. Independent of UI splits.

5. **`test_lab/renderer.py`** (sub-phase fifth). Option A composer + class-level test-compat shim. Lays down `renderer/_draw_helpers.py` for use by sub-phase 6.

6. **`test_lab/test_run_details.py`** (sub-phase sixth — depends on 5). Option A. Imports `_draw_helpers` from sub-phase 5. Could land in a single combined sub-phase with 5 if the user prefers fewer commits.

7. **`strategy_renderer.py`** (sub-phase seventh). Option A composer. Includes the `_temp_screen_pos` cleanup and polar-angle dedup with `strategy_click_dispatcher.py`. Independent of `strategy_window_manager.py` split — they share zero code.

8. **`strategy_window_manager.py`** (sub-phase eighth). Option A composition root. Includes the `planet_abilities_window` slot fix. Touches `strategy_ui.py` indirectly; coordinate with sub-phase 7's merge (also touches `strategy_ui.py` by way of the renderer integration). If both sub-phases happen to land within the same week, merge 7 first then rebase 8.

9. **`race_setup_screen.py`** (sub-phase ninth). Option A + small Option B for `RaceBrowserDialog`. PROJ-282 MVVM split. Most invasive single-file split (5+ new modules in a new package). Testing risk is real (~1221-line test file with ~17 patched private methods needs migration). Land late so the team is at maximum experience with PROJ-309 patterns.

10. **`app.py`** (sub-phase tenth — last). Option B. **Highest risk** because a faulty bootstrap = unlaunchable game. Mandatory full 15-step manual smoke per the design doc. Land last, when all tooling and patterns have been validated by the previous nine sub-phases.

**Rationale:**

- **Type-definition files (1, sub-phase 1) → pure logic (2, 3) → composer-pattern siblings (4) → renderer pair (5, 6) → strategy-screen pair (7, 8) → MVVM-heavy (9) → bootstrap (10).**
- Each sub-phase's full sharded suite must hold at 15405 passed / 2 skipped before the next sub-phase begins. If any sub-phase drops the suite, fix before continuing.
- Sub-phases 5+6 and 7+8 can be paired if the user prefers fewer commits (each pair is internally consistent and independent of other pairs).
- The order minimizes "in-flight cleanups blocking each other" — the latent-bug fixes from "Latent bugs surfaced" all land in their owning sub-phase with no cross-sub-phase dependency.

If timeline pressure dictates parallelism (separate developers per sub-phase), sub-phases 1+2+3+4 can land in parallel safely (zero shared files); sub-phases 5/6 must serialize; sub-phases 7/8 must coordinate via `strategy_ui.py`; sub-phases 9 and 10 should serialize against each other (both touch the menu/setup overlay flow).
