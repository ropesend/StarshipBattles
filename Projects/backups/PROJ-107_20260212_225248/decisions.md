# PROJ-107: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-11 | Project initialized | Starting point for Consistency and API Standardization |
| 2026-02-11 | Use "A" prefix for AI error codes (A001-A099) | Follows existing X### convention (V, S, R, P, F, C). "AI" prefix from sweep finding doesn't follow the single-letter convention. |
| 2026-02-11 | Keep `_get_hp_percent` and `_is_in_pdc_arc` instance methods, delete only `_stat_*` static wrappers | The instance methods are used internally by AIController. The static wrappers add nothing - they just delegate to TargetEvaluator. |
| 2026-02-11 | Rename `BattleResult` to `BattleServiceResult` (not rename `BattleResults`) | BattleResults (plural) is the canonical battle outcome type used everywhere. BattleResult (singular) is a service operation result. Renaming the less-used one minimizes blast radius. |
| 2026-02-11 | BattleEngine.get_winner() stays `-> int`, BattleService.get_winner() stays `-> Optional[int]` | These are correct for their layers. BattleEngine always returns 0/1/-1. BattleService adds None for "no engine" case. Fix is documentation, not code. |
| 2026-02-11 | Standardize DI parameter name to `registry_provider`, keep strict-vs-optional per PROJ-50 | PROJ-50 intentionally made VehicleClassService strict. We respect that decision. Only standardize the naming. |
| 2026-02-11 | ShipIOAdapter return types stay different for save vs load | save returns `Tuple[bool, Optional[str]]`, load returns `Tuple[Optional[Any], Optional[str]]`. These represent genuinely different operations. Fix is documentation. |
| 2026-02-11 | ResourceRegistry already follows correct Optional/empty-collection convention | Single lookups return Optional, collection lookups return empty lists. Fix is documentation. |
| 2026-02-11 | Use `StateException` (not `ValueError`) for state violations in battle_controller | Aligns with PROJ-45 exception hierarchy. StateException is the correct semantic type for "wrong mode" errors. |
| 2026-02-11 | Defer 13 findings to other projects | event_handler rename (50 files), ability lifecycle (PROJ-88), lazy init (PROJ-86-89), Ship facade (PROJ-88), serialization, fleet_id naming (PROJ-87), error return values, from_dict signatures, ShipThemeManager (PROJ-86), Camera API (PROJ-89), BattleUIService errors, click handler returns (25+ files), click handler params |
| 2026-02-11 | Use `Dict[str, Any]` (typing module form) for to_dict() return types | Matches existing fleet.py and ship_instance.py pattern. Lowercase `dict[str, Any]` (Python 3.9+) is also valid but inconsistent with existing codebase convention. |
| 2026-02-11 | Phase ordering: Error codes first, type hints second, naming third | Error codes are isolated (no ripple effects). Type hints are additive-only. Naming changes touch call sites but are still low risk. Simulation API changes (Phase 5) are highest risk, so last before cleanup. |
| 2026-02-11 | `check_missiles` -> `include_missiles` | "check" is ambiguous (verify vs search). "include" clearly communicates the parameter's purpose: whether to include missiles in the enemy search results. |
