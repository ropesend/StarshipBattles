# Phase 5: Documentation Update

**Objective:** Update architecture docs to reflect the new caching patterns and dirty-flag conventions.

---

## Checklist

### Documentation Updates
- [ ] Update `docs/02_PATTERNS.md` — add "Dirty-Flag Stat Invalidation" pattern with Ship as the canonical example
- [ ] Update `docs/02_PATTERNS.md` — strengthen "Two-Phase Ability Aggregation" section to note FleetAuraManager now uses the shared aggregator
- [ ] Update `docs/01_ARCHITECTURE.md` — note that ShipCombatManager separates transient updates from conditional stat rebuilds
- [ ] Update `docs/strategy_layer.md` — document PlanetEnergyCache and its invalidation triggers
- [ ] Add note to `docs/03_CONVENTIONS.md` about cache invalidation convention: "mutation events invalidate caches; never poll for changes"

### Verification
- [ ] Run full test suite — confirm no regressions (docs-only phase)
