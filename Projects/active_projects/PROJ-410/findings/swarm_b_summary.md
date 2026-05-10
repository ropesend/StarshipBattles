# PROJ-410 Phase B — Consolidated Swarm Summary

> Consolidated from 8 Phase B Explore agents. Four agents wrote standalone findings (`swarm_b_api.md`, `swarm_b_dependencies.md`, `swarm_b_performance.md`, `swarm_b_yard_selector.md`); four ran read-only and reported in chat only — their findings are preserved here.

## 1. Architecture Analyst (in-chat)

**Verdict: Proposed B+C+A is architecturally sound — with one re-evaluation needed on A.**

- `VirtualTable.invalidate_widget_caches()` belongs on `VirtualTable` itself. The cache fields (`_last_text`, `_last_img`, `_last_color`) are private to that class, and `virtual_table.py` is at 607 LOC — well below the 500-LOC ceiling for production files; even with the new method (~10–12 lines), it stays within budget. (Note: 607 LOC is over 500, but this is a pre-existing condition; PROJ-410 should not grow it materially.)
- **No existing pub/sub or callback subscription pattern on `StrategySessionFacade`.** Searched `game/strategy/facade/strategy_session_facade.py:80–150` and `slices/event_slice.py:1–97`. The only callback on the facade is `process_turn(progress_callback=...)` — a one-way per-turn progress hook. The facade exposes only read accessors (`get_active_empire`, `get_human_player_ids`, `get_turn_number`).
- **Recommendation that conflicts with user's Q3 answer (A — facade event):** the cleanest architectural fit is `StrategyBuildQueueManager` polls `facade.get_active_empire()` (or equivalent) on each `_open_build_queue()` and detects player change. This is fully Pattern #5 (Facade/Delegate) compliant — uses the existing read API, adds no new event/subscription surface. *See conflict in plan-level Open Question.*
- `on_active_player_changed()` should live on the manager (existing orchestration point), not on `BuildQueueScreen` (which should stay thin per Pattern #8 MVVM).
- PROJ-382 facade-bypass guard does NOT block A or B. Bypass = UI calling `session.handle_command()` directly. Adding a facade event/accessor doesn't bypass — it goes *through* the facade.
- Pattern #11 (Surface Caching) explicitly endorses `invalidate_cache()` methods on components owning local caches, so the new method follows precedent.

## 2. Dependency Mapper (file: `swarm_b_dependencies.md`)

- **Callers of `BuildQueueScreen.open_for_yard()`**: `StrategyBuildQueueManager._open_build_queue()` line 144 (modify), `BuildQueueScreen.__init__` line 147 (test against), 6 sites in `test_build_queue_screen_lifecycle.py` (test against).
- **Non-build-queue consumers of `VirtualTable`**: `EventLogWindow`, `EmpireBuildQueueWindow`, planet/fleet/star list windows. **Invalidation must be opt-in / data-source-aware** so we don't disturb other consumers.
- **`BuildQueueQueueDataSource.set_queue()`** has no version metadata; renderer hook needs another signal.
- **`drag_handler.selected_design` reset gap**: 1-line fix in `BuildQueueDragHandler.reset_state()` (line 88–100). **NOTE: Yard-Selector Investigator (below) reports `selected_design` IS already cleared by `reset_state()` indirectly — needs verification before declaring this a fix.**
- No LOC AST guards on `build_queue_*.py` or `virtual_table.py`. `tests/static_guards/test_facade_bypass_guard.py` is the active static guard; PROJ-410 won't trip it.

## 3. Test Impact Analyst (in-chat — could not write file)

**Existing perf-lock tests that must stay green:**
- `tests/unit/ui/components/table/test_virtual_table.py::TestRowPoolReuseGuard` (5 tests, ~lines 1097–1292) — assert widget `.kill()` call counts. **Hard constraint: invalidation must NOT call `.kill()` — only null cache fields.**
- `tests/unit/ui/screens/test_strategy_build_queue_manager.py::TestSecondClickReuse` (3 tests, ~lines 533–658) — assert `open_for_yard()` is called on second click, not constructor.
- `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py::test_request_close_*` (~lines 453–525) — panels survive close (`alive() == True`), instance identity preserved.
- `tests/static_guards/test_facade_bypass_guard.py` — ASTs every `game/ui/` file looking for `<expr>._session.handle_command(...)` and `BuildQueueScreen(..., session=...)` from outside `strategy_screen.py`.

**One existing test reportedly fails today** per Test Impact Analyst: `test_drag_handler_reset_state` for `selected_design` not being cleared. **CONFLICT** with Yard-Selector Investigator who reports `reset_state()` does clear it. **Action: verify by reading both `build_queue_drag_handler.py:88–101` and the existing test in Phase 1 before relying on this claim.**

**Test plan for the 5 user-approved regression scenarios:**
| # | Scenario | Test File | Test Name | Level |
|---|---|---|---|---|
| a | Yard switch, identical geometry | `test_build_queue_screen_lifecycle.py` (extend) | `test_same_context_type_yard_switch_invalidates_cache` | unit |
| b | Close + reopen on same yard | `test_build_queue_screen_lifecycle.py` (extend) | `test_close_and_reopen_invalidates_cache` | unit |
| c | End-of-turn → next-player open | `test_build_queue_screen_lifecycle.py` (extend) | `test_turn_boundary_invalidates_cross_player_cache` | unit |
| d | Ship-yard ↔ planetary-yard same planet | `test_build_queue_screen_lifecycle.py` (extend) | `test_same_planet_different_yard_type_invalidates` | unit |
| e | `+/-` click after switch fires on new row | `test_build_queue_screen_lifecycle.py` or new | `test_button_press_after_yard_switch_targets_new_row_index` | unit |

All five should fail today before fix, pass after fix (TDD).

**Coverage gap recommendations not in original plan:**
- New: `test_yard_selector_visible_on_second_player_planet` (integration) for the in-scope yard-selector symptom.
- New: `test_build_queue_screen_after_save_load` if save/load risk is real (see Risk Assessor).

## 4. Pattern Scout (in-chat — could not write file)

**Key findings:**
- **No prior precedent for cross-widget cache invalidation.** `VirtualTable` is the only widget with `_last_text` / `_last_img` / `_last_color` style caching. PROJ-410 sets a new pattern; document it in `docs/02_PATTERNS.md` Pattern #11 (Surface Caching) extension.
- **No facade callback pattern.** Reaffirms Architecture Analyst's view: polling `facade.get_active_empire()` from the manager is more consistent with what's there than introducing a callback API.
- **Closest precedent for context switch**: `BuildQueueScreen.open_for_yard()` already does explicit collaborator resets (controller, drag handler, selector) at lines 317–337. The missing piece is **VirtualTable cache invalidation** before the renderer's `_refresh_queue_display()` call at line 342.
- **Do not** add a `make_invalidator()` composition method (Pattern #32). Compositional Construction is for `__init__`-time slots, not post-construction lifecycle.
- **Anti-patterns search**: no `# HACK` / `# TODO` / `# XXX` comments near cache invalidation in `game/ui/`. The bug exists because the case wasn't anticipated, not because someone left a known issue.

## 5. Risk Assessor (in-chat — could not write file)

**Three risks that warrant additional plan tasks:**

### Risk A (MAJOR): Modal persists across player turns
- File: `build_queue_screen.py:823–838`, `strategy_build_queue_manager.py:178–217`
- This is the same symptom as triage's "cross-player merged display" but the *failure mode* is specifically: the modal is open when end-turn fires, and there's no hook to close/invalidate it. The proposed turn-boundary hook (Q3) addresses this; **action**: ensure the hook also calls `hide()` (not just invalidates), so the next player must explicitly reopen — clean state.

### Risk B (MAJOR — new finding not in original plan): Save/load breaks cached screen
- File: `save_game_service.py`, `strategy_screen.py:231–248`
- After loading a saved game mid-session, `BuildQueueScreen` instance survives with stale `Empire`/`Planet` references. Next `open_for_yard()` reads from old facade context.
- **Mitigation**: in `StrategyScreen.session` setter (around line 247) after rebinding the facade, hide and invalidate the cached `build_queue_screen`, or null it. Adds one task to the plan.

### Risk C (MAJOR — new finding not in original plan): Per-frame rebuild budget if flags aren't ephemeral
- File: `virtual_table.py:309–431`
- If `invalidate_widget_caches()` permanently disables the dirty-check early-return at lines 318–323, every frame after invalidation would re-render all visible rows — ~10–20% FPS drop during normal play.
- **Mitigation**: invalidation must be **ephemeral** — clear the data-identity dirty flag after the next `update_visible_rows()` runs once. Cache nulls naturally re-populate during that single re-render, restoring the early-return for subsequent frames. Adds an explicit subtask to the implementation phase.

**Other scenarios reviewed and resolved as non-issues**: drag-in-progress + yard switch (existing `reset_state()` covers it), scroll persistence (reset is expected UX), click-during-refresh (pygame_gui single-threaded input pump prevents race), N-player rotation (per-empire signal works), AI-only turns (unconditional hide is correct), close-during-invalidation (visibility gate prevents reentrancy).

## 6. Data Flow Tracer (in-chat — could not write file)

Traced 5 flows (first-open, yard-switch, add-to-queue, end-of-turn, close+reopen). Key insights:

- **Renderer hook B fires synchronously after every `facade.handle_command()`** via the `on_queue_changed` callback (`controller.add_to_queue` → callback → `_refresh_queue_display`). Not polling. **This means B-hook fires often** — must be cheap (~1–2 ms) and ideally guarded against redundant work via a `_data_identity_dirty` flag the data source sets when changed.
- **C-hook in `open_for_yard()` should run AFTER updating `build_context` (line 290) and BEFORE `_refresh_queue_display()` (line 342)** — that ordering ensures the data source carries new yard data when the table re-renders.
- **Flow 4 (turn boundary) is the only flow that mandates the A-hook.** The other four are covered by B+C alone. So the A-hook is solely about ensuring the next-player's first open invalidates correctly.
- **Already-handled by existing code**: `force_update()` (line 163) already resets `_last_scroll_pct` and `_last_row_count` to sentinels. Plan does NOT need to re-implement that — only add cache nulls.

## 7. Yard-Selector Investigator (file: `swarm_b_yard_selector.md`)

**Verdict: Separate bug — same surface, different cause.**

- The `BuildQueueSelector` does not use `VirtualTable`; it has its own UIButton creation in `refresh()`.
- `refresh()` correctly destroys and recreates yard buttons every call (lines 91–95, 113–123).
- `collect_build_queues_at_hex()` (called at line 294–297 of `build_queue_screen.py`) correctly filters by `self.empire`, which is updated each `open_for_yard()`.
- **Real bug**: container visibility lifecycle. When the first player closes the build queue, `hide()` recursively hides all child panels including the selector's `UIScrollingContainer`. When the second player opens, `refresh()` adds buttons but the container was never explicitly re-shown (line 369–373 of `build_queue_screen.py` only calls `show()` on the background panel, not children).
- **Fix**: small, explicit `show()` call on the selector's container, OR ensure pygame_gui auto-propagates visibility from the parent panel.
- **Implication**: yard-selector fix is a separate, small task (likely 2–5 LOC). Should still be in PROJ-410 per the user's Q1 answer.

**Discrepancy on `selected_design`**: this agent reports `reset_state()` *does* clear `selected_design` (citing line 327 of `build_queue_screen.py`). The Test Impact Analyst reported a failing test for this. **Both claims need verification by reading `build_queue_drag_handler.py:88–101` directly during Phase 1 TDD.**

## 8. Performance Analyst (file: `swarm_b_performance.md`)

**Verdict: PASS the `<0.5s` repeat-open budget with margin.**

- `invalidate_widget_caches()` cost: 1–2 ms (pool ~30–60 rows × ~16 widgets = ~900 attribute writes at ~1 µs each).
- Next `update_visible_rows()` re-render cost: 6–15 ms (font glyph rasterization ~0.5–1 ms per visible label × ~10–20 labels).
- Yard-switch overhead: ~7–17 ms total — well under 500 ms.
- Active-player change: ~20 ms — negligible.
- **TestRowPoolReuseGuard** stays green because invalidation does not call `.kill()`.
- **Concern**: B-hook fires on every `set_queue()`, which the renderer triggers after every queue mutation. Without a generation counter on `BuildQueueQueueDataSource`, the B-hook costs ~1–2 ms even when data didn't actually change identity (just contents). Acceptable for now; can be optimized later by adding a generation counter.
- **No standalone perf-verification phase needed**, but recommend a smoke timing check at the end of the project.

## 9. API/Interface Reviewer (file: `swarm_b_api.md`)

- `VirtualTable.invalidate_widget_caches() -> None` — naming approved, idempotent, observable via `_last_text is None` after call.
- Add private `_data_identity_dirty: bool = True` flag on `VirtualTable`; gate the early-return at lines 318–323 on it; clear it at the end of the next `update_visible_rows()` (ephemeral, per Risk C).
- `BuildQueueScreen.on_active_player_changed() -> None` — naming matches the existing `on_*_changed()` convention (`on_selection_changed`, `on_race_selected`).
- `BuildQueueController` and `BuildQueueDragHandler` — extend existing methods; no new public surface.
- **Recommends Phase B uses Option B (manager polling) for the A-hook**, with Option C (explicit facade callback) as a future upgrade. Aligns with Architecture Analyst and Pattern Scout.
- No exports change. No static guard violations.

---

## Cross-Cutting Conflicts to Resolve

1. **Turn-boundary mechanism (Q3)**: User answered **A (facade event)**. Architecture Analyst, Pattern Scout, and API Reviewer all converge on **B (manager polling)** as the more consistent fit — `StrategySessionFacade` has no callback pattern; polling `facade.get_active_empire()` on each open is Pattern #5 compliant and adds zero new surface. **Surface to user before finalizing the detailed plan.** *Default if no answer: switch to manager polling, document the rationale in `decisions.md`.*

2. **`drag_handler.selected_design` reset status**: Triage and Test Impact Analyst say it's NOT cleared; Yard-Selector Investigator says it IS cleared. **Verify in Phase 1 TDD by reading source directly and writing the failing test first.**

3. **New risks added to scope**: save/load cached-screen invalidation, ephemeral data-identity dirty flag. Both should be explicit tasks.
