# Phase 5: Documentation Update

**Objective:** Update architecture docs to reflect the new spatial API, identity mapping, and indexing patterns.

---

## Checklist

### Documentation Updates
- [ ] Update `docs/01_ARCHITECTURE.md` — note `query_radius_exact()` as the preferred spatial query for combat
- [ ] Update `docs/02_PATTERNS.md` — document the identity mapping rule: use `instance_id`, never `name`, for ship matching
- [ ] Update `docs/04_SERVICES.md` — update `calculate_design_stats()` docs: no fallback, single path, raises on error
- [ ] Update `docs/strategy_layer.md` — document Galaxy indices and facade cache patterns
- [ ] Update `docs/04_SERVICES.md` — update `FleetBattleAdapter` docs to reference `instance_id` matching

### Verification
- [ ] Run full test suite — confirm no regressions (docs-only phase)
