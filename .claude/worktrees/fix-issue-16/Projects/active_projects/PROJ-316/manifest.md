# PROJ-316 File Manifest

> Generated during project setup. Used by /claude-proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

### Phase 1 — paperwork sweep (no production code)

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-313/phase_1_checklist.md` | Tracking | Status → Complete; check off boxes |
| `Projects/active_projects/PROJ-313/phase_2_checklist.md` | Tracking | Status → Complete; check off boxes |
| `Projects/active_projects/PROJ-313/phase_3_checklist.md` | Tracking | Status → Complete; check off boxes |
| `Projects/active_projects/PROJ-313/phase_4_checklist.md` | Tracking | Status → Complete; check off boxes |
| `Projects/active_projects/PROJ-313/phase_5_checklist.md` | Tracking | Status → Complete; check off boxes |
| `Projects/active_projects/PROJ-313/phase_6_checklist.md` | Tracking | Status → Complete; check off boxes |
| `Projects/active_projects/PROJ-313/phase_7_checklist.md` | Tracking | Status → Complete; check off boxes; note Phase 3 of PROJ-316 rewrites the regression test |
| `Projects/active_projects/PROJ-313/phase_8_checklist.md` | Tracking | Add `Deferred:` notes; add Scope Deviation section |
| `Projects/active_projects/PROJ-313/plan.md` | Tracking | Mark deferred goals; correct blockers/index readiness context |
| `docs/02_PATTERNS.md` | Documentation | Pattern #31: 21→20 adopters; rewrite "one-liner" claim; rewrite contract-test claim. Pattern #30: clarify SUPERSEDED banner |

### Phase 2 — tighten `window_manager` to required

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/strategy_modal_window.py` | Production | Base already required `window_manager`; update docstring to reflect retained slot cleanup test |
| `game/ui/screens/planet_list_window.py` | Production | Remove `= None` default |
| `game/ui/screens/star_list_window.py` | Production | Remove `= None` default |
| `game/ui/screens/build_queue_list_window.py` | Production | Remove `= None` default |
| `game/ui/screens/empire_build_queue_window.py` | Production | Remove `= None` default |
| `game/ui/screens/event_log_window.py` | Production | Remove `= None` default |
| `game/ui/screens/empire_panel_window.py` | Production | Remove `= None` default |
| `game/ui/screens/fleet_report_window.py` | Production | Remove `= None` default |
| `game/ui/screens/planet_abilities_window.py` | Production | Remove `= None` default |
| `game/ui/screens/strategy_windows/move_choice_dialog.py` | Production | **NO CHANGE** — `MoveChoiceWindow` inherits the already-required base constructor |
| `game/ui/screens/food_allocation_editor.py` | Production | Remove `= None` default |
| `game/ui/screens/atmosphere_target_editor.py` | Production | Remove `= None` default |
| `game/ui/screens/gravity_target_editor.py` | Production | Remove `= None` default |
| `game/ui/screens/water_target_editor.py` | Production | Remove `= None` default |
| `game/ui/screens/radiation_shield_editor.py` | Production | Remove `= None` default |
| `game/ui/screens/planet_selection_window.py` | Production | **NO CHANGE** — cross-screen window; callers pass either real manager or explicit `None` |
| `docs/06_UI_STYLE_GUIDE.md` | Documentation | Window Management section: example shows required `window_manager`; add cross-screen reuse subsection |
| `tests/unit/ui/screens/test_strategy_modal_window.py` | Test | Add signature guard for strategy-only windows |
| `tests/unit/ui/screens/test_build_queue_list_window.py` | Test | Add explicit `window_manager=None` for non-modal-tracking test construction |
| `tests/unit/ui/screens/test_fleet_report_window_multi_select.py` | Test | Add explicit `window_manager=None` for non-modal-tracking test construction |
| `tests/unit/ui/screens/test_food_allocation_editor.py` | Test | Add explicit `window_manager=None` for non-modal-tracking test construction |

### Phase 3 — replace Phase 7 regression test

| File | Type | Notes |
|------|------|-------|
| `tests/integration/ui/test_editor_click_blocking.py` | Test | Major rewrite: import the 5 editor classes; add subclass test, registration-on-construct test, spawn-site assertion test; rename or remove the existing MagicMock-only test |

### Phase 4 — verification (no production changes)

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-316/plan.md` | Tracking | Mark all 4 phases Complete; bump `Last verified:` |
| `Projects/projects_index.md` | Tracking | Update PROJ-316 status |
| `Projects/active_projects/PROJ-316/decisions.md` | Tracking | Document kickoff baseline, inventory, explicit-None test policy, and mutation verification |

## Files NOT touched
- `game/ui/screens/strategy_event_router.py` — `_handle_window_close` and the slot scans are explicitly NOT removed (R3a vs R3b decision; see `decisions.md`).
- `game/ui/screens/strategy_window_manager.py` — slot fields are explicitly NOT removed for the same reason.
- `tests/unit/ui/screens/test_strategy_window_manager_public_api.py` `TestModalSlotCleanupContract` — explicitly NOT removed; remains a regression for the still-active slot-cleanup pathway.
