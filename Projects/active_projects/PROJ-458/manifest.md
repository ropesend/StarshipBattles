# PROJ-458 File Manifest

> Generated during charter creation 2026-05-19 from Codex r4 audit redesign (job 10) + F-C-017 finding.
> Updated during implementation as per-phase retrofits surface additional files (e.g. `PlanetTargetEditor` base class changes in Phase 2-5 if required).

## Files

### Phase 1 — SettingsWindow retrofit + F-C-016 docs touch

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/settings_window.py` | Production | Apply two-stage `__init__` per Pattern #33. Stage 1 (above guard): `on_close_callback`, `_settings` (GameSettings instance). Stage 2 (below guard): `super().__init__(...)`, widget construction via UI builder. Add optional `ui_builder=None` constructor kwarg with `DefaultSettingsWindowUiBuilder()` default. |
| `tests/unit/ui/screens/test_settings_window.py` | Test (new) | Dedicated characterization tests. Cover construction (bypass-init + production paths), slider state transitions, Reset button behavior, Close button + on_close_callback emission. Use `make_ui_widget(SettingsWindow, ...)` with `bypass_init(SettingsWindow)` context manager. |
| `tests/fixtures/settings_window_ui_builder.py` | Test fixture (new — optional) | `NullSettingsWindowUiBuilder` (no-op for tests that don't care about widgets) + `MockSettingsWindowUiBuilder` (MagicMock-populated slots for tests asserting UI builder calls). Mirrors `tests/fixtures/race_setup_ui_builder.py` pattern. |
| `docs/known-issues.md` | Docs | F-C-016 close (codex r5 audit 2026-05-19): delete the stale-doc warning at `docs/known-issues.md:37` — the README it warns about (`tests/fixtures/README.md:22,310-336`) was already updated at HEAD. Verify the README state before deleting the warning, then remove the warning paragraph (and the `#uiwindow-super-init-chain-blocker` anchor section if it still exists). |
| `Projects/active_projects/PROJ-458/findings/PROJ-458_findings.md` | Project | Update F-C-016 + F-C-017 (SettingsWindow row) to `Status: resolved`. |

### Phase 2 — AtmosphereTargetEditor retrofit

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/atmosphere_target_editor.py` | Production | Apply two-stage `__init__` per Pattern #33. Note: this class inherits from `PlanetTargetEditor` (`game/ui/screens/planet_target_editor_base.py`). If the base-class `__init__` needs adjustment to support the bypass-init flow (e.g. the base's `super().__init__(...)` to `StrategyModalWindow` must also honor the bypass guard), audit and adjust the base class too — record the decision in `decisions.md`. |
| `game/ui/screens/planet_target_editor_base.py` | Production (conditional) | If Phase 2 audit determines the base class needs to participate in the two-stage flow, add bypass-init support here so all 4 subclasses share the same plumbing. Otherwise leave unchanged. |
| `tests/unit/ui/screens/test_atmosphere_target_editor.py` | Test (new) | Dedicated characterization tests for the 10-gas slider grid + species-ideal preset wiring + Apply/Cancel callbacks. |
| `tests/fixtures/atmosphere_target_editor_ui_builder.py` | Test fixture (new — optional) | Null + Mock builders for the AtmosphereTargetEditor. |
| `Projects/active_projects/PROJ-458/findings/PROJ-458_findings.md` | Project | Update F-C-017 AtmosphereTargetEditor row to `Status: resolved`. |

### Phase 3 — GravityTargetEditor retrofit

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/gravity_target_editor.py` | Production | Apply two-stage `__init__` per Pattern #33. Inherits from `PlanetTargetEditor` (already adjusted in Phase 2 if needed). |
| `tests/unit/ui/screens/test_gravity_target_editor.py` | Test (new) | Dedicated characterization tests. |
| `tests/fixtures/gravity_target_editor_ui_builder.py` | Test fixture (new — optional) | Null + Mock builders. |
| `Projects/active_projects/PROJ-458/findings/PROJ-458_findings.md` | Project | Update F-C-017 GravityTargetEditor row to `Status: resolved`. |

### Phase 4 — WaterTargetEditor retrofit

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/water_target_editor.py` | Production | Apply two-stage `__init__` per Pattern #33. Inherits from `PlanetTargetEditor`. |
| `tests/unit/ui/screens/test_water_target_editor.py` | Test (new) | Dedicated characterization tests. |
| `tests/fixtures/water_target_editor_ui_builder.py` | Test fixture (new — optional) | Null + Mock builders. |
| `Projects/active_projects/PROJ-458/findings/PROJ-458_findings.md` | Project | Update F-C-017 WaterTargetEditor row to `Status: resolved`. |

### Phase 5 — RadiationShieldEditor retrofit

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/radiation_shield_editor.py` | Production | Apply two-stage `__init__` per Pattern #33. Inherits from `PlanetTargetEditor`. |
| `tests/unit/ui/screens/test_radiation_shield_editor.py` | Test (new) | Dedicated characterization tests. |
| `tests/fixtures/radiation_shield_editor_ui_builder.py` | Test fixture (new — optional) | Null + Mock builders. |
| `Projects/active_projects/PROJ-458/findings/PROJ-458_findings.md` | Project | Update F-C-017 RadiationShieldEditor row to `Status: resolved`. PROJ-458 complete after this phase. |

### Cross-cutting (every phase)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/ui/screens/test_strategy_modal_window.py` | Test | The parametrized test at lines 367-398 (`test_strategy_only_windows_require_explicit_window_manager`) parametrizes over the 4 PlanetTargetEditor subclasses + FoodAllocationEditor. After each PROJ-458 phase, re-run this test to confirm the retrofit didn't accidentally regress the window-manager-required contract. |
| `tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py` | Test | The SettingsRegistrar test at lines 100-127 exercises SettingsWindow indirectly. After Phase 1, re-run to confirm no regression. |
| `Projects/active_projects/PROJ-458/decisions.md` | Project | Record per-phase decisions: which template was followed for each retrofit; whether the PlanetTargetEditor base class needed adjustment in Phase 2; any retrofit-recipe deviations and their rationale. |
| `Projects/active_projects/PROJ-458/plan.md` | Project | Update Quick Status table + Current State after each phase. |

### Pattern + docs reference

| File | Type | Notes |
|------|------|-------|
| `docs/02_PATTERNS.md` §33 | Docs | Primary reference — do not edit (already documented). Read before each phase. |
| `docs/02_PATTERNS.md` §32 (Compositional Construction) | Docs | Read if a phase's retrofit surfaces 3+ stable heavy collaborators (likely for `AtmosphereTargetEditor`). |

### Findings + tracking updates

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-458/findings/PROJ-458_findings.md` | Project | Update after each phase. F-C-017 has 5 sub-rows (one per window); each closes as its phase completes. F-C-016 closes in Phase 1. |
| `Projects/projects_index.md` | Project | Update PROJ-458 row to `Complete` after Phase 5. |

### Optional Codex consult deliverable (end-of-project)

| File | Type | Notes |
|------|------|-------|
| `AgentCoordination/Scratchpad/Consult/<timestamp>_proj458-final/response.md` | Scratch | Codex pre-final-check consult response. Standard end-of-project workflow per PROJ-443/PROJ-444 precedent. |
