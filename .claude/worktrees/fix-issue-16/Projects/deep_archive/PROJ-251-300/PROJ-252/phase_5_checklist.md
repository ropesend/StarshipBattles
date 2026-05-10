# Phase 5: Documentation Update

**Objective:** Update architecture and pattern docs to reflect the new DI, RNG, and event patterns.

---

## Checklist

### Documentation Updates
- [ ] Update `docs/02_PATTERNS.md` — add "Per-Battle RNG" pattern: `random.Random(seed)` instances, never global `random.seed()`
- [ ] Update `docs/02_PATTERNS.md` — strengthen DI section with note that `get_default_registry_provider()` must not be called from `game/simulation/`
- [ ] Update `docs/01_ARCHITECTURE.md` — note that BattleEngine uses injected RNG for determinism
- [ ] Update `docs/04_SERVICES.md` — update BattleEngine/BattleService API docs to mention `rng` parameter
- [ ] Update `docs/04_SERVICES.md` — document EventBus as session-scoped, not global
- [ ] Review `docs/05_ERROR_HANDLING.md` — ensure event logging section reflects EventBus pattern

### Verification
- [ ] All doc references to `random.seed()` in simulation context are removed or updated
- [ ] No docs reference `set_event_handler()` as the primary pattern
- [ ] Run full test suite — confirm no regressions (docs-only phase, but verify)
