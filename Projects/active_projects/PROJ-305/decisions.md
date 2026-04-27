# PROJ-305: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | Starting point for Fleet Strategic-Layer Ability Sources |
| 2026-04-26 | **Fleet abilities project at the strategic layer**, NOT combat-only | User explicitly chose: "Strategic-layer hex effects from fleets (e.g. flagship aura buffs allies in same hex on the strategy map)" over the combat-only option. The unification adds a new capability; existing `FleetAuraManager` combat behavior is unchanged. |
| 2026-04-26 | **Scope dichotomy enforces clean separation**: combat-only scopes (self/fleet/team) stay in `FleetAuraManager`; strategic scopes (sector/system/etc.) flow through `FleetAbilitySource` | One ability data model, two consumption paths gated by scope. No overlap; no leak in either direction. |
| 2026-04-26 | **Fleet `owner_id` honored** (NOT ownerless like storms/stars) | Fleets have empire ownership. `allied_sector` / `enemy_sector` scopes filter properly through PROJ-300's `_aggregate` owner-aware filtering. |
| 2026-04-26 | **`source_label` prefers flagship name** if available, else fleet name + empire | Fleets often have generic names; flagships have lore. Format: `"Flagship 'Indomitable' (Player 1)"` or `"Fleet 'Strike Group Alpha' (Player 1)"`. |
| 2026-04-26 | **Component-level audit, not blanket scope expansion** | Each ability's `allowed_scopes` change is a design choice. Adding `scope: sector` to `WeaponAbility` (for example) makes no design sense. Phase 1 audits and proposes per-ability changes. |
| 2026-04-26 | **Fleet abilities are treated as always-active in PROJ-305** | Per-component activation state aggregation across many ships in a fleet is complex. PROJ-305 ships flat "operational ship contributes; non-operational doesn't"; activation state of individual abilities is a follow-up. Documented as a known limitation. |
| 2026-04-26 | **Performance: cache per-turn if needed** | A fleet's `get_abilities()` is `O(N*M)` (ships × components). If profiling shows regression, cache `(hex, empire_id, turn)` → effects in the collector and invalidate at turn start. Defer until measured. |
| 2026-04-26 | **Stealth/cloak interaction deferred** | Whether a cloaked fleet's abilities still project is a per-ability-type concern. Punt to a future stealth-design project; document as a TODO in the implementation. |
| 2026-04-26 | **No new combat consumption** in PROJ-305 | If a strategic-scope ability also makes design sense in combat (e.g. `ShieldModifier scope: allied_sector` from a flagship affecting battle), the existing PROJ-300 spec compiler picks it up via the universal sector-effects path. No new combat wiring needed. |
