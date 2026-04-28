# PROJ-315 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/core/component_state.py` | Production | Add `ComponentInstanceView` frozen dataclass next to `ComponentState`. Additive only. |
| `game/strategy/data/ship_instance.py` | Production | Add `iter_all_components_by_layer()` method. Additive — does not modify existing `get_components_by_layer()` or `get_damaged_components_by_layer()`. |
| `game/ui/panels/ship_detail_panel.py` | Production | Replace `_build_damage_section` → `_build_component_section`; remove `if damage_count > 0` gate; add module-level `InstanceDamage` / `ComponentGroup` / `group_components_by_id`; add `_apply_strikethrough` helper; rename section header to `COMPONENT STATUS`. |
| `game/ui/colors.py` | Production | Add `MUTED_GREY` colour constant for manually-disabled components. |
| `tests/unit/core/test_component_state.py` | Test | New tests for `ComponentInstanceView` (construction, frozen, equality). |
| `tests/unit/strategy/test_ship_instance_damage.py` | Test | New `TestIterAllComponentsByLayer` test class — pristine, partial damage, HULL filter, parser-bug regression, empty design, instance_index numbering. |
| `tests/unit/ui/panels/test_ship_detail_panel.py` | Test | New `TestGroupComponentsById` (pure function) and `TestComponentStatusSection` (widget) classes. ~15 new tests. |
| `docs/06_UI_STYLE_GUIDE.md` | Documentation | New "Read-only component grouping (PROJ-315)" section + bumped `Last verified:` timestamp. |
| `Projects/active_projects/PROJ-315/plan.md` | Tracking | Updated Current State + Work Log on completion. |
| `Projects/projects_index.md` | Tracking | Status flip to "Awaiting User Verification" on completion. |

## Maybe-touched (decide during implementation)

| File | Type | Notes |
|------|------|-------|
| `tests/integration/ui/conftest.py` | Test | Already provides `ui_manager` fixture. No changes expected; consult during widget tests. |
| `tests/conftest.py` | Test | Already provides `ship_factory`. No changes expected. |
| `docs/02_PATTERNS.md` | Documentation | One-line cross-reference if a "module-level pure-function colocation" pattern needs an explicit entry. Optional per Phase 3 Task 3.1. |
