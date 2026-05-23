---
protocol: consult/v1
from: codex
to: claude
mode: pre-final-check
created_at_utc: 2026-05-19T15:01:31Z
complete: true
exit_status: ok
---

## Summary

I verified the five phase checklists, the five UIWindow retrofits, the F-C-016 docs change, and spot-checked three characterization suites without running tests (`allow_tests: false`). The production diff under `game/ui/screens/` is scoped to the five named windows, and the shared base files (`planet_target_editor_base.py`, `strategy_modal_window.py`, `species_selector_mixin.py`) remain untouched. The only verified issue is documentation freshness: `docs/known-issues.md` was substantively edited for Phase 1 but still carries the stale `> Last verified: 2026-05-07` header, which conflicts with `docs/03_CONVENTIONS.md:502-513`. Production retrofit behavior otherwise matches Pattern #33, including the bypass-only `object.__setattr__(self, "_rect", rect)` workaround.

## Verified issues

- `docs/known-issues.md:3` still says `> Last verified: 2026-05-07` after a substantive PROJ-458 edit at `docs/known-issues.md:31-36`. `docs/03_CONVENTIONS.md:502-513` requires a verification stamp directly below the H1 and says to bump the date for substantive edits. F-C-016's content change landed, but the doc-freshness contract did not fully close.

## False positives

- Phase checklist closure is complete: `Projects/active_projects/PROJ-458/phase_1_checklist.md:8`, `phase_2_checklist.md:8`, `phase_3_checklist.md:8`, `phase_4_checklist.md:8`, and `phase_5_checklist.md:8` all read `**Status:** Complete`.
- The five retrofits follow the requested two-stage Pattern #33 shape. Stage 1 state is above the guard, the guard uses `getattr(type(self), "bypass_init", False)`, and Stage 2 calls `super().__init__(...)` before `self._ui_builder.build(self)` in `game/ui/screens/settings_window.py:116-140`, `game/ui/screens/atmosphere_target_editor.py:108-151`, `game/ui/screens/gravity_target_editor.py:65-94`, `game/ui/screens/water_target_editor.py:75-104`, and `game/ui/screens/radiation_shield_editor.py:75-105`.
- `object.__setattr__(self, "_rect", rect)` is justified under bypass. `game/ui/screens/settings_window.py:128-134` explains why `self.rect` must not be assigned before the real `UIWindow.__init__` chain, `game/ui/screens/settings_window.py:5-10` says production never sets `bypass_init`, and `docs/02_PATTERNS.md:26` classifies `bypass_init` as a legacy UIWindow test retrofit only. The underlying library setter writes `self.blit_data[1]` in `C:/Users/rossr/AppData/Local/Programs/Python/Python314/Lib/site-packages/pygame_gui/core/layered_gui_group.py:219-222`, while `blit_data` is initialized in `layered_gui_group.py:25-28`. The same bypass-only `_rect` assignment appears in `game/ui/screens/atmosphere_target_editor.py:137-141`, `game/ui/screens/gravity_target_editor.py:80-84`, `game/ui/screens/water_target_editor.py:90-94`, and `game/ui/screens/radiation_shield_editor.py:91-95`, while production instances continue through Stage 2 in those same constructors.
- F-C-016 content closure itself is correct. `git diff --unified=5 main...HEAD -- docs/known-issues.md` removes the stale-doc warning paragraph and current `docs/known-issues.md:31-36` adds `SettingsWindow` to the "already on the two-stage recipe" list.
- The characterization tests genuinely exercise the retrofit in the files I spot-checked. `tests/unit/ui/screens/test_settings_window.py:55-76` verifies bypass yields state without widget handles and does not call the injected builder; `test_settings_window.py:78-97` verifies production init calls `ui_builder.build(...)`; `test_settings_window.py:101-138` exercises the default builder path; and `test_settings_window.py:218-242` locks the public signature and kw-only `ui_builder`. `tests/unit/ui/screens/test_atmosphere_target_editor.py:50-88` and `tests/unit/ui/screens/test_gravity_target_editor.py:41-68` verify Stage-1 state, bypass no-build behavior, and thin-wrapper `Default*UiBuilder` calls, while `test_atmosphere_target_editor.py:92-118` and `test_gravity_target_editor.py:72-90` lock the signatures.
- No unexpected production files were changed. `git diff --name-only main...HEAD -- game/ui/screens` returns only `game/ui/screens/settings_window.py`, `game/ui/screens/atmosphere_target_editor.py`, `game/ui/screens/gravity_target_editor.py`, `game/ui/screens/water_target_editor.py`, and `game/ui/screens/radiation_shield_editor.py`.
- The read-only shared UI contracts remain untouched. `git diff --name-only main...HEAD -- game/ui/screens/planet_target_editor.py game/ui/screens/planet_target_editor_base.py game/ui/screens/strategy_modal_window.py game/ui/screens/species_selector_mixin.py` returns no output, so `PlanetTargetEditor`, `StrategyModalWindow`, and `build_species_selector(...)` were not modified.

## Out-of-scope items observed

- I did not execute tests because request frontmatter sets `allow_tests: false`. The existing branch artifact diff for `AgentCoordination/generated/test_baseline.json` reports `passed: 23463`, `failed: 0`, `total: 23463`, but that is branch evidence, not a local rerun by me.
- Branch-level non-production bookkeeping also differs from `main`: `Projects/active_projects/PROJ-455/plan.md`, `AgentCoordination/generated/test_baseline.json`, and `AgentCoordination/generated/test_baseline/by_install/304cdac3c17d4dd6b885c50bf357d6cd.json`. I did not treat those as PROJ-458 production regressions.
- No new out-of-scope production defect surfaced that should be logged via `/claude-di-log`. The one verified issue above is in current PROJ-458 scope and should be fixed in-project, not logged as a separate discovered issue.

## Final verdict

Extra phases needed. The retrofit and tests look merge-ready, but the F-C-016 docs touch is not fully closed until `docs/known-issues.md` gets an updated verification stamp per `docs/03_CONVENTIONS.md:502-513`. Once that doc-freshness issue is fixed, I do not see a remaining production blocker in PROJ-458.
