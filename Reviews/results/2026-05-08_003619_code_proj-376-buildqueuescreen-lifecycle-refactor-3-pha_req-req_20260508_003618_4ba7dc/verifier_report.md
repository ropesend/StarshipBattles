# PROJ-376 Verifier Report — Independent Review of OpenCode's Findings

**Verifier:** Claude (Opus 4.7, 1M ctx)
**Date:** 2026-05-08
**Source review:** `report.md` in this directory (OpenCode, 6 findings)
**Branch:** `feat/03c-phase-aware-execution`
**Commits in scope:** 56bbe4c54, a93330bb9, 4ef34e87b

---

## Verdicts Table

| ID      | Severity | Verdict     | Confidence |
|---------|----------|-------------|------------|
| LOC-01  | MAJ      | CONFIRM     | High       |
| LS-01   | MIN      | CONFIRM     | High       |
| LS-02   | MIN      | CONFIRM     | High       |
| LS-03   | MIN      | CONFIRM (no-action) | High |
| LS-04   | INFO     | CONFIRM     | High       |
| DOC-01  | INFO     | CONFIRM     | High       |

**Summary:** All 6 findings independently verified. Zero rejections. No new findings discovered during the independent sweep.

---

## Per-finding Detail

### LOC-01 — CONFIRM

`wc -l game/ui/screens/build_queue_screen.py` reports **822 lines**, matching the report exactly. The pre-PROJ-376 baseline of 659 LOC is consistent with prior reviews (PROJ-373's findings reference that ballpark). Growth of 163 lines is genuine and the file does exceed `docs/03_CONVENTIONS.md` §2.3's 500 LOC soft target by 322 lines.

OpenCode's recommendation (acknowledge as acceptable for PROJ-376; defer extraction of event-handling block lines 550-746 or command-dispatch lines 383-509 to future work) is reasonable. The added lifecycle methods (`hide`, `show`, `is_visible`, `open_for_yard`, `_construct_collaborators`, `_rebuild_panels`, `_validate_params`) are cohesive with the screen's responsibilities; an immediate split would be premature.

### LS-01 — CONFIRM (redundant rebind is real)

Read `build_queue_screen.py:288-292`. After `_construct_collaborators` (lines 205-217) builds the controller with `galaxy=self.galaxy, empire=self.empire`, the `open_for_yard` method then assigns `self.controller.galaxy = self.galaxy` and `self.controller.empire = self.empire`.

I checked **every** mutation of `self.galaxy` / `self.empire` on the screen — only the `__init__` writes (lines 98-99) exist. They are never reassigned. So even after `_construct_collaborators` (whether on first open OR cross-type rebuild), `controller.galaxy / controller.empire` are guaranteed equal to `self.galaxy / self.empire`. Hot-reload of registries does not affect this — galaxy/empire are session-stable references on the screen.

OpenCode's framing is correct: the writes are a no-op in the common path and create the false impression that the controller might hold a different galaxy/empire on reuse. Recommendation: remove or comment as defense-in-depth — either is acceptable.

### LS-02 — CONFIRM

`_validate_params` lines 135-171: when `build_context is None`, line 155-157 returns early, so no `hex_coord` consistency check is performed. A caller passing `(initial_yard=None, build_context=<planet>, hex_coord=None)` would not trip `_validate_params` because `effective_initial_yard = initial_yard or build_context` is `<planet>` (non-None), so `_validate_params` is invoked with `build_context=<planet>` and `hex_coord=None` — that path raises the explicit "requires hex_coord" exception at line 158. So the documented bug shape is slightly different than reported.

However, the underlying point still holds: there's a **second** ambiguous path — `(initial_yard=None, build_context=None, hex_coord=<set>)` — where validation skips out at line 157 even though hex_coord was supplied without a context. This combination is currently unused and would silently no-op, which is the asymmetry OpenCode flagged.

Either guard (raise on `build_context is None and hex_coord is not None`) or accept the asymmetry. Trivial. Not blocking.

### LS-03 — CONFIRM (no-action; theoretical-only)

`grep` for `add_listener|register_callback|on_kill` against the BuildQueueScreen controller / renderer / drag_handler returned **zero matches** in `game/`. No pygame_gui kill-completion callbacks are registered against any of these collaborators. The orphan-instance risk OpenCode describes is purely theoretical — there is no current pygame_gui callback wiring through these objects.

Verdict: confirm the description, but it correctly carries an "Effort: None / no action required" tag in the report. This is documentation noise, kept for awareness if future work adds such callbacks.

### LS-04 — CONFIRM

`open_for_yard` at line 281 sets `self.planet_selection_window = None` unconditionally. By contrast, `hide()` at lines 329-331 explicitly kills the window first:

```python
if self.planet_selection_window is not None:
    self.planet_selection_window.kill()
    self.planet_selection_window = None
```

If `open_for_yard` is reached without `hide()` having been called first AND a `PlanetSelectionWindow` is currently open (mid-selection from a previous yard), the slot is cleared while the underlying `UIPanel` tree remains alive in the pygame_gui manager — a true leak. As OpenCode notes, the manager's current flow always routes through `hide()` (via `_request_close` → `on_close` callback → manager flow) before the next `open_for_yard`, so the leak is not currently triggered. But mirroring `hide()`'s kill-first pattern is cheap defense-in-depth and removes a latent footgun. Trivial fix; not urgent.

### DOC-01 — CONFIRM

- `Projects/active_projects/PROJ-376/plan.md:26` does say "Task 3.1 user-side re-profile deferred" and is documented as a user-side smoke gate.
- Line 27 confirms: "Task 3.1 re-profile is a user-side smoke; not blocking the code-side closeout."
- `phase_3_checklist.md:8` reads "Status: Complete (Task 3.1 user-side re-profile deferred)" — exactly as the report states.
- The repro instructions at `phase_3_checklist.md:33-39` cleanly mirror PROJ-373's original repro.

Documentation is faithful. INFO-only.

---

## Independent Sweep — Additional Checks

### New / flaky-looking tests in scope

- `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` — 583 lines. Spot-checked `test_close_method_is_removed` (lines 545-550) and the `test_open_for_yard_initial_yard_kwarg_matches_post_open_state` (lines 252-299) tests cited by OpenCode. Both make non-trivial assertions (10+ attribute comparisons, identity checks, alive-state checks). No `pass`-ing skeletons or trivial-true assertions found. No skipif/xfail markers. No flakiness signals.
- `test_request_close_can_be_re_opened` (line 553+) and `test_close_callback_does_not_null_screen_slot` are integration-flavored but observable. Acceptable.

### Manager call paths bypassing rebind logic

`grep` for `open_for_yard|hide()|show()` in `strategy_build_queue_manager.py`:

- All three click handlers (`on_build_yard_click`, `on_fleet_build_click`, `on_navigate_to_hex_build`) route through `_open_build_queue` (line 154 reference confirmed). No direct `open_for_yard` / `hide` calls bypass the helper.
- `_on_build_queue_close` correctly does NOT null `self._screen.build_queue_screen`. The cached instance is reused (lines 185-186).

### Production callers stuck on old `_close()` pattern

`grep -rn "_close()" game/ | grep build_queue` returns **only** docstring/comment references inside `build_queue_screen.py` and a logger message in `strategy_build_queue_manager.py:172`. No production caller invokes `_close()`. Migration to `_request_close()` is complete.

### Comment / docstring drift

`build_queue_screen.py:801` comment says "PROJ-376 Phase 2: replaces ``_close()`` (which destroyed the panel...". This is documentation, not a callable name reference. No drift.

---

## Recommended Actions for Claude

**Fix now (cheap, defensible):**

1. **LS-04** — In `open_for_yard` around line 281, replace `self.planet_selection_window = None` with the kill-first pattern that `hide()` already uses. ~3 lines, removes a latent leak. (Trivial.)

**Optional / stylistic (defer or skip):**

2. **LS-01** — Either delete lines 291-292 (rely on `_construct_collaborators` initial values, which I confirmed are guaranteed identical) **OR** leave them with a 1-line comment "idempotent — defense-in-depth" so future readers don't infer a non-existent contract. Either is fine. Trivial.
3. **LS-02** — Add a 2-line guard to `_validate_params` for `build_context is None and hex_coord is not None`. Optional — no current caller triggers it.

**Defer (not for this PR):**

4. **LOC-01** — File extraction (event-handling block lines 550-746 and/or command-dispatch lines 383-509). Acknowledge in PROJ-376 closeout that the 500-LOC ceiling is exceeded; track as future cleanup.
5. **LS-03** — No action required (theoretical only).
6. **DOC-01** — User-side re-profile (Task 3.1) is the only outstanding gate; it is correctly documented as user-deferred.

**Verifier sign-off:** OpenCode's review is accurate, calibrated, and complete. No counter-findings. The PR is safe to merge after (optionally) addressing LS-04.
