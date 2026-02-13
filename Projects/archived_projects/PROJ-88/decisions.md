# PROJ-88: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-09 | Project initialized | Starting point for God Class Decomposition - Simulation Core Tier |
| 2026-02-09 | Delete ShipComponentManager entirely | Dead code -- extracted in PROJ-12 but never adopted. Ship still has all 11 methods inline. PROJ-49 added caching to Ship that permanently diverges from the extraction. Zero production imports. Per CLAUDE.md: "When a new system replaces an old one, ERADICATE the old system completely." |
| 2026-02-09 | Use Facade pattern for all new extractions | Ship has 136 importers, Component has 161 importers. Changing the public API would cascade across 100+ files. Instead, extract logic into helper classes and keep one-line delegation methods on Ship/Component. This matches the existing pattern used by ShipCombatEngine, AbilityManager, ModifierManager, and ComponentStatsCalculator. |
| 2026-02-09 | Defer Component extraction complexity -- keep conservative (18% target reduction) | Component's 161 importers make it the highest-risk target. Only extract clearly cohesive groups (resource/activation ~80 lines, health/damage ~40 lines). Leave ability access, modifier management, and stats calculation as-is since they already delegate to external managers. Target ~140 lines extracted from the 463-line Component class (not the loader functions). |
| 2026-02-09 | Complete IScene migration before extracting SceneDispatcher | PROJ-65 introduced IScene but left StrategyScreen using legacy callbacks. Must complete the migration first (fold handle_click/handle_scroll into handle_event) before evaluating whether a SceneDispatcher extraction is worthwhile. With only 4 importers, app.py has low blast radius and may not need heavy decomposition beyond cleanup. |
| 2026-02-09 | Name new Ship validator helper `ship_validator_helper.py` | `ship_validator.py` already exists at `game/simulation/validation/ship_validator.py` (the actual validation logic). The new file is a thin helper that delegates from Ship to the existing validator. Distinct naming avoids confusion. |
| 2026-02-09 | Phase 1 first (delete dead code) | Simplest phase with zero risk -- purely deleting unused code. Establishes momentum and validates the project's test baseline before touching live code. |
| 2026-02-09 | Leave component access helpers in Ship | get_all_components, iter_components, get_components_by_ability, etc. are thin (3-8 lines each) and already optimized with PROJ-49 caching. Extracting them would add indirection with no meaningful complexity reduction. |
