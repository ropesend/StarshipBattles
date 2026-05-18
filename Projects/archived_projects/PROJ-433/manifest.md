# PROJ-433 File Manifest

> Generated during project init from the PROJ-425 Codex consult finding.
> Used by `/proj-parallel` for conflict detection.
> Update if implementation discovers additional files.

## Files

### Production — modified (Phase 1)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/services/component_inspector.py` | Production (rewrite or delete) | Currently 537 LOC. Phase 1: extract Surface A (ability iteration helpers + `has_warp_capability`) → `component_abilities.py`. Extract Surface B (layer-view helpers added by PROJ-425 Phase 2) → `component_layers.py`. End state: either a thin re-export shim (Option A) or deleted (Option B). Decision locked in Phase 0. |

### Production — created (Phase 1)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/services/component_abilities.py` | Production (new) | Ability iteration surface: `get_component_abilities`, `extract_abilities_from_component`, `get_component_type`, `get_component_threshold`, `iterate_design_components`, `iter_facility_ability_entries`, `ship_has_ability`, `find_ship_with_ability`, `count_ability`, `list_ship_abilities`, `get_ability_list`, `has_warp_capability`. Plus the private `_get_component_registry`. Estimated ~440-450 LOC. |
| `game/strategy/services/component_layers.py` | Production (new) | Layer-view surface: `iter_components_by_layer`, `damaged_components_by_layer`, `count_damaged_components`. Plus `lookup_design_max_hp` if Phase 0 grep shows no non-layer consumer. Estimated ~140-160 LOC. |

### Tests — modified (Phase 0 + Phase 1)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/services/test_component_inspector.py` | Test (extend) | Phase 0: pin Surface A public surface (snapshot `__all__` set as a test fixture). Phase 1: update imports if Option B is chosen. |
| `tests/unit/strategy/services/test_component_inspector_layers.py` | Test (extend) | Phase 0 + Phase 1; Surface B coverage from PROJ-425 Phase 2. |
| Possibly other `tests/unit/strategy/services/test_component_inspector*.py` files | Test | Discovered by Phase 0 grep. |

### Caller migration scope (discovered by grep in Phase 0)

Caller files migrated if Option B is chosen. Will be filled in during Phase 0:

- Phase 0 grep: `rg -n "from game.strategy.services.component_inspector|import.*component_inspector" game tests`.
- Likely consumers: `game/strategy/data/ship_instance.py` (entity delegates), strategy validators (`game/strategy/services/colonize_validator.py`, `superweapon_validator.py` etc. per the PROJ-108 Phase 3 docstring), UI panels that consume layer views.

### Docs — modified (Phase 2)

| File | Type | Notes |
|------|------|-------|
| `docs/architecture/*.md` or `docs/refactoring/*.md` | Doc | Phase 2: update any doc that references `component_inspector.py` by name. Phase 0 grep will identify these. |
| `Projects/active_projects/PROJ-425/decisions.md` + `findings_ledger.md` | Doc | Phase 2: back-link noting the split landed. |
