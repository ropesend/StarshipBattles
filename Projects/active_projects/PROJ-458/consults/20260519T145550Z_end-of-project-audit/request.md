---
protocol: consult/v1
from: claude
to: codex
mode: pre-final-check
allow_tests: false
created_at_utc: 2026-05-19T14:55:50Z
repo_root: C:/Developer/StarshipBattles
consult_leaf: C:/Developer/StarshipBattles/Projects/active_projects/PROJ-458/consults/20260519T145550Z_end-of-project-audit
complete: true
---

# PROJ-458 end-of-project audit (Group C, position 3 of 4)

## Background

PROJ-458 ("UIWindow retrofit completion") closes the F-C-017 finding
across 5 `UIWindow` subclasses + closes F-C-016 (docs touch). Each
window receives the Pattern #33 two-stage `bypass_init` shape: Stage 1
pure-Python state + `ui_builder` seam above the bypass guard, Stage 2
`super().__init__` + heavy widget tree below.

All 5 phases are complete and pushed to `origin/group-c`. This consult
audits the project before the end-of-project merge to `main`.

## Commits to audit on `group-c`

```
16fed8a10  PROJ-458 Phase 1: SettingsWindow Pattern #33 retrofit + F-C-016 closure
3caec637a  PROJ-458 Phase 2: AtmosphereTargetEditor Pattern #33 retrofit
e37f800da  PROJ-458 Phase 3: GravityTargetEditor Pattern #33 retrofit
dfcb38a8e  PROJ-458 Phase 4: WaterTargetEditor Pattern #33 retrofit
f49b873be  PROJ-458 Phase 5: RadiationShieldEditor Pattern #33 retrofit (flake retry note)
```

## Phase summary

- **Phase 1 (SettingsWindow, 109 LOC, F-C-017 + F-C-016)**: Add
  `SettingsWindowUiBuilder` Protocol + `DefaultSettingsWindowUiBuilder`
  (full widget tree builder). Restructure `__init__` to two-stage. F-C-016
  closure: delete the stale-doc warning paragraph at
  `docs/known-issues.md:37` and add SettingsWindow to the "already on
  two-stage recipe" list. 10 characterization tests at
  `tests/unit/ui/screens/test_settings_window.py`.
- **Phase 2 (AtmosphereTargetEditor, 273 LOC)**: Add
  `AtmosphereTargetEditorUiBuilder` Protocol +
  `DefaultAtmosphereTargetEditorUiBuilder` (thin wrapper around the
  editor's existing `_build_ui()` method). Restructure `__init__` to
  two-stage. 5 characterization tests.
- **Phase 3 (GravityTargetEditor, 220 LOC)**: Same recipe as Phase 2. 5
  characterization tests.
- **Phase 4 (WaterTargetEditor, 227 LOC)**: Same recipe. 5 characterization
  tests.
- **Phase 5 (RadiationShieldEditor, 231 LOC)**: Same recipe (3-button
  override; same Stage 1 / guard / Stage 2 split). 5 characterization
  tests. Final commit also rolls up the cumulative plan.md updates and
  the combined sharded baseline.

## Common retrofit shape (all 5 windows)

```python
def __init__(self, ..., *, ui_builder=None):
    # Stage 1 — pure-Python state + UI-builder seam (no pygame_gui widgets).
    self.X = ...
    self._ui_builder = ui_builder or DefaultXxxUiBuilder()
    # Bypass guard.
    if getattr(type(self), "bypass_init", False):
        self.ui_manager = manager
        self._window_init_bypassed = True
        object.__setattr__(self, "_rect", rect)  # avoid pygame_gui rect.setter
        return
    # Stage 2 — heavy widget tree.
    super().__init__(...)
    self._window_init_bypassed = False
    self._ui_builder.build(self)
```

The `object.__setattr__(self, "_rect", rect)` is to skirt `pygame_gui`'s
`UIWindow.rect.setter` which writes `self.blit_data[1]` — `blit_data` is
only populated by the real `UIWindow.__init__` chain.

## Verification checklist gates

- F-C-017 (5 windows) all on the two-stage recipe — `bypass_init` flag
  honored; Stage 1 state populated; Stage 2 widget construction routes
  through `ui_builder`.
- F-C-016 (docs touch) — `docs/known-issues.md:37` stale warning deleted;
  `SettingsWindow` added to the "already on two-stage recipe" list.
  `tests/fixtures/README.md` not touched (already current at HEAD per
  the project's pre-flight findings).
- 30 new characterization tests across 5 new test files at
  tests/unit/ui/screens/test_settings_window.py,
  test_atmosphere_target_editor.py, test_gravity_target_editor.py,
  test_water_target_editor.py, test_radiation_shield_editor.py.
- Public positional/keyword-able signatures preserved on all 5; kw-only
  `ui_builder` parameter added everywhere.
- Sharded: 23463/23463 (23443 from Phase 1 close + 20 new from Phases
  2-5) on retry. First sharded after the Phase 2-5 batch had 1 flake on
  `test_reset_button_resets_settings_to_defaults` which passed in
  isolation per §13.

## Audit requests

Please verify, citing `file:line`:

1. **Phase checklist closure** — each `phase_N_checklist.md` (N=1..5) has
   Status: Complete.
2. **Retrofit shape** — for each of the 5 windows, the `__init__` follows
   the two-stage Pattern #33 shape (Stage 1 state above guard; bypass
   guard correctly uses `getattr(type(self), "bypass_init", False)` per
   the pattern's "type(self) so subclass flags win" note; Stage 2 calls
   `super().__init__` then `self._ui_builder.build(self)`).
3. **`object.__setattr__` bypass workaround** — confirm the
   `object.__setattr__(self, "_rect", rect)` is needed (the
   `UIWindow.rect` setter writes `blit_data[1]`) and is not a layering
   violation in production. (It only runs under bypass; production
   instances go through the normal `super().__init__` rect-setter chain.)
4. **F-C-016 closure** — `docs/known-issues.md:37` stale warning was
   deleted; SettingsWindow added to the "already on two-stage recipe"
   list at the same anchor.
5. **Test fixture correctness** — the characterization tests genuinely
   exercise the retrofit (bypass yields state without widgets;
   ui_builder NOT called under bypass; signature checks; thin-wrapper
   tests for the Default*UiBuilder). Spot-check at least 2 of the 5
   test files.
6. **No production regression** — the production diff stays within the
   5 named window files + `docs/known-issues.md`. Other UI files
   (`planet_target_editor_base.py`, `strategy_modal_window.py`,
   `species_selector_mixin.py`) are not modified by this project.
7. **Read-only contracts** — confirm `PlanetTargetEditor`,
   `StrategyModalWindow`, `species_selector_mixin.build_species_selector`
   are not modified.
8. **Discovered-issue hygiene** — list any genuine new finding in the
   diff that should be logged via `/claude-di-log`.

## Out-of-scope clarifications

- Phase 5's flake retry note in the commit message is intentional per
  §13. The flake test is in `test_settings_window.py` (Phase 1 file);
  the flake itself does not point at a Phase 5 regression.
- Group A's PROJ-451 ratchet allowlist drift (`Tools/lint_test_files_allowlist.txt`
  extended in PROJ-452's merge prep) is non-production cleanup and
  already on `main`; not in PROJ-458's scope.

## Constraints` section.
Skills MUST NOT inline a separate copy.

Reference: `AgentCoordination/Scratchpad/Discussion/20260509T170814Z_consult-discuss-harmonize/plans/consult_harmonization_r002.md`
and the smoke-driven follow-up plan at `AgentCoordination/Scratchpad/Discussion/20260509T190300Z_smoke-findings-merge/plans/consult_v1_smoke_fixes_r001.md`.

## Constraints

- Strict TDD: identify failing tests first; don't propose code that bypasses this.
- Documentation first: reference `docs/` as source of truth; never read or cite `docs/_ignore/`.
- No backward-compat shims, monkey patches, fallback systems, or save-file migrations.
- Respect layer boundaries (per `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`).
- Do NOT revert unrelated user changes; work around existing dirty state.
- Evidence standard: cite `file:line`, command output, or transcript. Label unverified claims `[unverified]`.
- Final ownership: the initiator owns synthesis. You advise; you do NOT implement.
- Follow-up rule: the initiator may ask follow-ups. You stop when advice converges or repeats.
- Permission contract: read repo, run tests only when `allow_tests: true` AND the mode is `pre-final-check` or `deep-dive`, write only inside the directory named by `consult_leaf` in the request frontmatter. Do NOT edit production code, docs, tickets, projects, configs, commits, branches, or PRs.

## Output

Write `response.md` in this consult leaf. Body sections:
- Summary (≤200 words)
- Verified issues (with file:line evidence)
- False positives (with evidence)
- Out-of-scope items observed
- Final verdict (ready to merge / extra phases needed / blocked)
