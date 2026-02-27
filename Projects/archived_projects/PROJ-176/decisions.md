# PROJ-176: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Project created from review findings | 7-agent review identified 3,564 pattern instances across 11 clusters; 6 clusters selected for remediation |
| 2026-02-23 | 3-phase logical ordering (not severity-based) | Phases ordered by dependency: Cluster 5 first (foundation), then Cluster 6 (depends on factory methods), then Cluster 4 (highest risk, last) |
| 2026-02-23 | ValidationResult: Static factory methods, NOT class methods | Factory methods are simplest mechanism — no inheritance, no state, purely additive to existing dataclass |
| 2026-02-23 | Validator primitives: Composable pure functions, NOT base class | Per DESIGN agent recommendation — validators have too little structural commonality for inheritance. Pure functions with `Optional[ValidationResult]` return are more flexible |
| 2026-02-23 | BaseCommandHandler: Mixin class with static helpers | Resolution helpers are stateless — `_resolve_fleet()` / `_resolve_planet()` return (entity, error) tuples. ICommandHandler protocol stays unchanged |
| 2026-02-23 | SimpleMultiplierAbility: Class-attribute-driven base class | 7 classes follow identical pattern with only 5 varying values. Template method with class attributes eliminates all 4 boilerplate methods |
| 2026-02-23 | SimpleMultiplierAbility: Add `__init_subclass__` validation | getattr/setattr means typos in class attribute strings fail silently — must validate at class definition time |
| 2026-02-23 | SuperweaponMarker: Separate from SimpleMultiplierAbility | Superweapons have no recalculate/stat logic — just markers with a name. Different base class, simpler design |
| 2026-02-23 | Exclude Clusters 1, 2, 7, 8, 9, 11 | UITheme partially resolved; DrawingUtils questionable ROI; JSON Loaders working fine; Serialization high risk + saves disposable; Event Handling inherently screen-specific; Test Fixtures intentional locality |
| 2026-02-23 | ALL-AT-ONCE migration per abstraction | Per CLAUDE.md migration policy — no backward compatibility layers. When an abstraction is introduced, ALL consumers migrate in the same phase |
| 2026-02-23 | STAT_BINDINGS auto-generation deferred | ABS-SIM-003 recommended auto-generating STAT_BINDINGS from class attributes. Defer until SimpleMultiplierAbility is proven stable — keep explicit STAT_BINDINGS initially |
