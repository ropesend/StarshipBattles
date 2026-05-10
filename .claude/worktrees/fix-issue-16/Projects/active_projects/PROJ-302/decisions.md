# PROJ-302: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | Starting point for Star Intrinsic Ability Sources |
| 2026-04-26 | **Stars project mostly system-scope abilities** (radiation field, stellar heat, gravitational lensing) | A star physically affects its entire system, not just the central hex. The framework's `system` scope is the right fit. Sector-scope is reserved for star-hex-only effects (e.g. a future "coronal flare" hot spot). |
| 2026-04-26 | **Stars are ownerless (`owner_id=None`)** | Same rationale as planet intrinsic abilities: the radiation damages friend and foe equally. |
| 2026-04-26 | **`source_label` format: `"<star.name> (<star_type>)"`** e.g. `"Sol (G-class)"` | Matches PROJ-301 planet pattern. |
| 2026-04-26 | **Pulsar `ShieldModifier scope: system`** affects all combat in pulsar systems with stacking reduction | Intentional balance lever — pulsar systems are dangerous to fight in. Combat aggregation through `_entries_from_sector_effects` (PROJ-300 Phase 6c) already handles system-scope provider entries; no new wiring needed. |
| 2026-04-26 | **Reuse PROJ-301's `roll_intrinsic_abilities` helper** rather than reimplement *(SUPERSEDED 2026-04-27 — see D6)* | (Original) Promote to a shared module is appropriate now that two projects use it. If PROJ-301 hasn't landed, ship it here. |
| 2026-04-27 | **D6 — Helper now ships in PROJ-300 (D15 in PROJ-300)** | Per the PROJ-300..305 review, `roll_intrinsic_abilities` and `format_intrinsic_source_label` ship in PROJ-300 framework. PROJ-302 imports both — see `game/strategy/services/ability_sources/intrinsic_roll.py` and `.../labels.py`. PROJ-302 does NOT reimplement either. |
| 2026-04-27 | **D7 — Hostile star systems are intentional design, NO balance cap** | User decision in review: pulsar / red giant / neutron star system-scope effects stack uncapped with facilities, storms, and other modifiers. Some star systems are deliberately combat-hostile and the player is expected to recognize and route around them. No floor multiplier on `ShieldModifier scope: system` from a star, and no rate cap on `EnvironmentalDamage scope: system`. |
| 2026-04-27 | **D8 — System panel shows a clear hazard hint when a system has hostile star intrinsics** | Counterpart to D7: if the design is "the player should avoid this system," the player must be able to *see* the hazard from the strategic map without entering combat first. Phase 4 UI verification adds a system-panel callout (e.g. red bordered "Hazard: Pulsar — system-wide shield interference" line) for any system whose star projects a `ShieldModifier scope: system` < 1.0 OR `EnvironmentalDamage scope: system`. Implementation: extend `system_tree_panel._add_system_effects` to flag system-scope hazards visually; reuse the existing Sector Effects rendering. |
