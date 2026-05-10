# PROJ-317 File Manifest

> Generated during /claude-proj-start. Used by /claude-proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production | R1: lift `per_id_index` out of the layer loop in `iter_all_components_by_layer`. R4: registry-derived `max_hp` fallback + new `_lookup_design_max_hp` helper; skip instance on dual-miss. |
| `game/ui/panels/ship_detail_panel.py` | Production | R2: apply chosen damage-tier colour to the rendered label via `UILabel.text_colour` + `rebuild()`; tint strike overlay to match. R3: fix `_resolve_threshold_lookup` import path (`game.core.registry`) and method (`get_components()`); keep justified broad-catch for UI-only registry startup failures. |
| `Projects/active_projects/PROJ-315/plan.md` | Tracking | R5: edit lines 25 (`Blockers:` field), 241, 248, 254 (`## Phases` section bodies). |
| `tests/unit/strategy/test_ship_instance_damage.py` | Test | R1 regression test (cross-layer iterator key set equals `_build_full_hp_components_from_design`). R4 regression tests (registry-derived fallback; dual-miss skip). |
| `tests/unit/ui/panels/test_ship_detail_panel.py` | Test | R2 regression (damage-tier colour visible in rendered output, NOT via `_proj315_color`). R3 regression (threshold lookup uses registry). R6: trim two trailing CRLF blank lines at EOF. Phase 3 only: retire `_proj315_color` / `_proj315_strike` reads. |
| `Projects/active_projects/PROJ-317/plan.md` | Tracking | Updated Current State + Work Log on completion. |
| `Projects/active_projects/PROJ-317/phase_1_checklist.md` | Tracking | Phase 1 task completion and verification notes. |
| `Projects/active_projects/PROJ-317/phase_2_checklist.md` | Tracking | Phase 2 task completion and verification notes. |
| `Projects/active_projects/PROJ-317/phase_3_checklist.md` | Tracking | Phase 3 deferral record. |
| `Projects/active_projects/PROJ-317/decisions.md` | Tracking | Actual R2 implementation decision and Phase 3 deferral. |
| `Projects/projects_index.md` | Tracking | Status flip to "Awaiting User Verification" on completion. |

## Maybe-touched (decide during implementation)

| File | Type | Notes |
|------|------|-------|
| `game/ui/colors.py` | Production | No expected change; existing `HP_*` constants suffice. Touched only if a tinted strike line needs a new constant. |
| `tests/conftest.py` | Test | Already provides `ship_factory`. No changes expected. |
| `tests/integration/ui/conftest.py` | Test | Already provides `ui_manager` fixture. No changes expected. |

## Out-of-scope

- **R8 (LOC ceiling).** `ship_detail_panel.py` is at 681 LOC. Deferred
  to a future PROJ-309 sweep per existing PROJ-315 `decisions.md` row 32.
- **Facade DTO + slice query.** Already declared out of scope in
  PROJ-315 design.
- **Visual layout / chevron / column-order changes.**

## Notes

- No new files. No new dataclasses. No new module-level functions
  outside the panel and the iterator. Keeps the diff small and
  reviewable.
- Cross-checked against PROJ-313, PROJ-314, PROJ-316 manifests on
  2026-04-28: zero file-overlap. Safe to run in parallel.
