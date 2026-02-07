# PROJ-54: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
<<<<<<< HEAD
| 2026-02-05 | Project initialized | Starting point for Combat Lab Quality Cleanup and Expansion |
| 2026-02-05 | Phase 0 (quality cleanup) before expansion | User explicitly requested code quality focus before adding new features |
| 2026-02-05 | All 5 priorities in scope | User chose all: _resolve_path dedup, extraction generalization, verify dedup, defense tests, modifier tests |
| 2026-02-05 | Add defense stats to extraction | User chose to include defense stats (total_defense_score, emissive_armor, max_shields, current_shields) |
| 2026-02-05 | Test modifiers are single-effect only | User specified: "test modifiers should only modify a single variable" - isolates the variable being tested |
| 2026-02-05 | Test modifiers have no restrictions | Unlike game modifiers which have `allow_abilities`/`deny_abilities`, test modifiers are unrestricted for flexibility |
| 2026-02-05 | Maintain backward compat for `data['weapon']` | Existing beam scenarios use `attacker.weapon.damage` paths - these must continue working after extraction generalization |
| 2026-02-05 | 6-phase structure (3 cleanup + 3 expansion) | Phases 1-3 clean foundation, Phases 4-6 add new features. Run full test suite after each phase. |
=======
| 2026-02-01 | Project initialized: Universal Planet Report Component | Consolidate duplicate planet display implementations across 4 UI contexts |
| 2026-02-01 | Use Strategy layer bottom-right panel as "golden" template | User confirmed this is the most complete implementation and will be extended in future |
| 2026-02-01 | Each planet has specific image file assigned during generation | User confirmed planets get specific `image_id` assigned (not procedural) - need to fix loading bug |
| 2026-02-01 | Build Queue link button should only appear in Strategy viewport and Planet List | Build Queue and Colonize windows shouldn't link to themselves (avoid circular navigation) |
| 2026-02-01 | Replace Strategy UI inline implementation with PlanetReportPanel | User chose consolidation over keeping duplicate code (consistency > minimal risk) |
| 2026-02-01 | Position Build Queue button BELOW the planet report panel | User chose vertical layout - cleaner, easier to implement than integrated or side-by-side |
| 2026-02-01 | Upgrade Colonize window to use full PlanetReportPanel | User chose richer display over simple text-only (more information helps colonization decisions) |
| 2026-02-01 | Fix planet image bug FIRST, then consolidate panels | User chose two-phase approach - fixes bug for all contexts immediately, consolidation builds on working foundation |
| 2026-02-01 | Enhance PlanetReportPanel with backward-compatible parameters | Add `portrait_surface` to __init__, `show_complexes` parameter - enables reuse without breaking existing code |
| 2026-02-01 | Keep action buttons external to panel (not embedded) | Follows single-responsibility principle - panel is display-only, screens manage interactions |
| 2026-02-01 | Delete duplicate `format_planet_info()` from strategy_ui.py | Eliminate code duplication - use single source in `strategy_detail_fmt.py` |
| 2026-02-01 | 6-phase implementation strategy | Sequential phases allow independent testing, image fix first prevents building on broken foundation |

>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08
