# PROJ-220: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-14 | Project initialized | Starting point for Tri-State Filter Widget & Filter Unification |
| 2026-03-14 | Tri-state interaction: 3 separate radio buttons per attribute (Yes/No/Ignore) | User preference — more explicit than click-to-cycle, uses more space but clearer |
| 2026-03-14 | Full state unification: create shared FilterStateManager + TriStateFilterWidget | User wants unified infrastructure, not just a widget drop-in. Eliminates 3 divergent patterns |
| 2026-03-14 | All tri-state filters default to Ignore (show all) | Matches current behavior where both Yes/No are enabled by default |
| 2026-03-14 | Fleet Report status filter (4-state: damaged/undamaged/derelict/destroyed) excluded from tri-state | Not binary — 4 independent statuses cannot map to tri-state semantics |
| 2026-03-14 | Planet List excluded from tri-state widget retrofit (no current binary filters) | Its filters are multi-select (11 types, 3 owners) and ranges — not binary. But must adopt FilterStateManager infrastructure so future binary filters use tri-state automatically |
| 2026-03-14 | New infrastructure location: `game/ui/filters/` for enum+state manager, `game/ui/components/filters/` for widget | Follows existing pattern: `game/ui/components/table/` for reusable components. State manager has no pygame deps (testable). Widget is pygame component |
| 2026-03-14 | Follow Build Queue's architecture as template (cleanest current pattern) | BuildQueueFilterManager + ViewModel + EventBus is the best-separated current implementation |
| 2026-03-14 | Preset migration: old bool presets auto-convert (True→INCLUDE, False→EXCLUDE) | Planet List has serialized presets in `ui_presets.json`. Save files are disposable but presets should survive |
| 2026-03-14 | Special capability filters: refactor filter logic to structured state before UI swap | Dynamic string key generation (`can_` → `no_`) is fragile. Move to structured Dict[str, FilterState] |
