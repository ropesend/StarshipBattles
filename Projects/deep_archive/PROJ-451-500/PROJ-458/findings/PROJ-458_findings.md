# PROJ-458 Findings — UIWindow retrofit completion (5 windows)

> Consolidated from `Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md` (2026-05-18 scan).
> The original scan flagged 30 findings across UI + Core + Tests. This file extracts the 1 entry
> that PROJ-458 owns (plus F-C-016, carried over for the documentary touch). File:line refs re-verified
> against repo HEAD on 2026-05-19.

## Owned Findings

### F-C-017 — Deferred UIWindow retrofit: `SettingsWindow` + 4 `PlanetTargetEditor` subclasses lack DEDICATED behavior-locking retrofit tests

- **Severity**: low (downgraded from medium by Codex r1 audit 2026-05-18 — see Codex verification note below)
- **Category**: missing-functionality (no DEDICATED retrofit/behavior-locking tests; some incidental coverage exists)
- **Files** (re-verified 2026-05-19 against repo HEAD):
  - `game/ui/screens/settings_window.py` (109 LOC) — smallest, simplest
  - `game/ui/screens/atmosphere_target_editor.py` (273 LOC)
  - `game/ui/screens/gravity_target_editor.py` (220 LOC)
  - `game/ui/screens/water_target_editor.py` (227 LOC)
  - `game/ui/screens/radiation_shield_editor.py` (231 LOC)
- **Symbol**: `SettingsWindow`, `AtmosphereTargetEditor`, `GravityTargetEditor`, `WaterTargetEditor`, `RadiationShieldEditor`
- **Source refactor**: PROJ-329A decisions D-003 / D-009
- **What survived**: PROJ-329A deferred the **dedicated retrofit + characterization test pass** for these 5 UIWindow subclasses until they gained coverage.

**Codex verification 2026-05-18** (preserved verbatim from the source-of-truth finding):
> Incidental coverage exists: the 4 PlanetTargetEditor subclasses are exercised through the explicit-window-manager contract suite at `tests/unit/ui/screens/test_strategy_modal_window.py:367-398`, and `SettingsWindow` creation/slot handling is exercised via `SettingsRegistrar` in `tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py:100-127`. No DEDICATED test file exists for any of the 5 windows; no behavior-locking characterization pass has been run; the bypass-init shell retrofit recipe (Pattern #33) was never applied.

**Verified 2026-05-19**:
- Re-confirmed: no `tests/unit/ui/screens/test_settings_window.py`, `test_atmosphere_target_editor.py`, `test_gravity_target_editor.py`, `test_water_target_editor.py`, or `test_radiation_shield_editor.py` exists.
- Re-confirmed: none of the 5 windows have the `if getattr(type(self), 'bypass_init', False): return` guard — they remain unretrofitted (single-stage `__init__`).
- The 4 PlanetTargetEditor subclasses are referenced from `test_strategy_modal_window.py` lines 367-398 (parametrized test asserting `window_manager` is a required keyword-only parameter — verified at lines 360-401 in the actual file).

- **Why it's a problem**: The 5 windows are exercised structurally (do they instantiate? do their slots wire?) but not behaviorally (do their state transitions, validation rules, and ok/cancel paths preserve invariants?). Refactoring them without a characterization pass first means any future migration breaks invisibly until a user reports it. PROJ-329A's "refactoring untested code adds risk without locking behavior" framing still applies — just less acutely than the original "zero coverage" framing suggested.
- **Suggested action**: Pick the smallest one (`SettingsWindow`, 109 LOC) and write a characterization-test pass through the bypass-init shell, then apply the standard two-stage retrofit recipe. Use the existing 6 retrofitted windows (`RaceSetupScreen`, `NewGameSetupScreen`, `race_browser_dialog`, `design_selector_window`, plus 2 others in `strategy_modal_window.py` and `strategy_window_manager.py` framework files) as templates.
- **Effort**: medium (per window) — ~1 sub-PR per window internally, 5 sub-PRs total for the project.

**Status as of 2026-05-19: open.**

**PROJ-458 disposition (per Codex r4 redesign):**

Codex r4: "Finish the dedicated behavior-locking retrofit pass for `SettingsWindow` plus the 4 planet-target editors. This is one coherent retrofit program even if it becomes multiple PRs internally. Closes `F-C-017`. Parallel-safe with `9` if write scopes stay separate." → PROJ-458 phases the work smallest-first to match Codex's "if review load matters, job 10 can be split into SettingsWindow first and PlanetTargetEditors second without changing any other dependency."

**Phase plan** (smallest-first, 5 sub-PRs internally):
- **Phase 1**: `SettingsWindow` (109 LOC) — smallest, simplest, no inheritance from `PlanetTargetEditor` (it inherits directly from `UIWindow` — verified 2026-05-19).
- **Phase 2**: `AtmosphereTargetEditor` (273 LOC) — largest of the 4 planet-target editors; tackles the most complex case first so the remaining 3 are smaller-as-similar.
- **Phase 3**: `GravityTargetEditor` (220 LOC).
- **Phase 4**: `WaterTargetEditor` (227 LOC).
- **Phase 5**: `RadiationShieldEditor` (231 LOC).

Per phase: read the 5 already-retrofitted UIWindow subclasses (`race_setup/screen.py`, `new_game_setup_screen.py`, `race_browser_dialog.py`, `design_selector_window.py`, `strategy_modal_window.py` itself) as templates, write characterization tests against the bypass-init shell, apply the two-stage retrofit recipe.

---

## Carried-Over Findings (Documentary Touch Only)

### F-C-016 — `docs/known-issues.md:37` carries a stale "tests/fixtures/README.md is out of date" warning

- **Severity**: low
- **Category**: test-inconsistency
- **File**: `docs/known-issues.md:37`
- **Symbol**: "Stale-doc warning: `tests/fixtures/README.md` still describes `ui_widget_factory.py` as 'non-UIWindow only' and points at the old blocker. The current authoritative guidance is the factory docstring plus `docs/02_PATTERNS.md` section 33."
- **Source refactor**: PROJ-329A retrofits + Compositional Construction (PROJ-322 onward)
- **What survived (verified 2026-05-19, codex r5 audit re-verification):** Only `docs/known-issues.md:37` still carries the stale warning. The README ITSELF has already been updated:
  - `tests/fixtures/README.md:22` now reads `ui_widget_factory.py    # pygame_gui widget factory + UIWindow bypass_init helper` (the "Non-UIWindow widget factory" framing is gone).
  - `tests/fixtures/README.md:310-336` already documents the current two-stage Pattern #33 approach and points at `docs/02_PATTERNS.md` §33 and the factory docstring as authoritative.
- **Why it's a problem (remaining):** `docs/known-issues.md:37` advertises that the README is stale, but the README is no longer stale. New contributors who read known-issues will mistakenly believe the README is wrong and route around it. The remaining fix is a single-line removal in `docs/known-issues.md`.
- **Suggested action**: Delete the stale-doc warning paragraph at `docs/known-issues.md:37` (and any associated `#uiwindow-super-init-chain-blocker` anchor section if it still exists). Do NOT re-edit `tests/fixtures/README.md` — it's already correct.
- **Effort**: tiny (1 line removal in 1 docs file)

**Status as of 2026-05-19: open (scope narrowed — README half already resolved).**

**PROJ-458 disposition:** Phase 1 sub-task. Reduced to a single-line removal in `docs/known-issues.md`. The README half of the original finding (rewriting the "Non-UIWindow only" / "Limitation — UIWindow super-init chain" sections) is already done as of HEAD 2026-05-19 — verify with a quick read of `tests/fixtures/README.md:22,310-336` before touching `docs/known-issues.md`.

---

## Cross-References

- **Codex r4 audit redesign**: `AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md` (Job 10 = PROJ-458).
- **Original bucket scan (2026-05-18)**: `Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md`.
- **Pattern #33 reference**: `docs/02_PATTERNS.md` §33 — UI Widget Test Factory + two-stage `UIWindow` bypass-init recipe (the central pattern for this project).
- **Existing retrofitted templates** (verified 2026-05-19 — files containing `if getattr(type(self), 'bypass_init', False)`):
  - `game/ui/screens/strategy_modal_window.py` — the base class with the guard at the framework level
  - `game/ui/screens/race_setup/screen.py` — example UIWindow subclass retrofit (line 149)
  - `game/ui/screens/race_browser_dialog.py`
  - `game/ui/screens/new_game_setup_screen.py`
  - `game/ui/screens/design_selector_window.py`
- **Codex r4 dependency note**: "Parallel-safe with `9` if write scopes stay separate." → PROJ-458 touches `settings_window.py`, `atmosphere_target_editor.py`, `gravity_target_editor.py`, `water_target_editor.py`, `radiation_shield_editor.py`. PROJ-457 touches `build_queue_screen.py`, `planet_list_window.py`, `test_lab/screen.py`, `game/core/exceptions.py`. Zero overlap → parallel-safe confirmed.

## Not Owned (Out of Scope)

- F-C-001..F-C-012, F-C-029 — UI back-compat shim clusters. Owned by PROJ-456.
- F-C-013, F-C-014 — protocol-layer residue. Owned by PROJ-449.
- F-C-015 — `stat_rows_dynamic.py` `LABEL_ABBREV`. Owned by PROJ-453.
- F-C-018, F-C-019 — static guards. Landed Stages 1+2.
- F-C-020 — `tests/fixtures/strategy_entities.py` legacy kwargs. Owned by PROJ-449.
- F-C-021..F-C-026 — test-skip wallpaper findings. Out of PROJ-458 scope.
- F-C-027, F-C-028 — file-LOC overflow + exceptions split. Owned by PROJ-457.
- F-C-030 — protocol `Dict[]` / `List[]` annotations. Owned by PROJ-454.
- DI-2026-05-18-002 — `transfer_dialog.py` LOC overflow. Owned by PROJ-456.
- DI-2026-05-18-004 — `LABEL_ABBREV` IDs side. Owned by PROJ-453.
