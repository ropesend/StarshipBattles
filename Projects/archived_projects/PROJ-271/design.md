# PROJ-271: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Context

PROJ-269 Phase 5.5 introduced the "placeholder stat_key silently skipped" decision that made several strategic modifiers no-op at battle time. PROJ-270 Phase 6 (Track A) restored the 1:1 multiplier-to-existing-stat_key sources (`shield_capacity_mult`, `damage_mult`). Track B — this project — covers the modifiers that require new architectural wiring:

1. **`flat_shield_bonus`**: additive, not multiplicative. Needs a new `SHIELD_BONUS_ADD` stat_key with `operation=ADD`.
2. **Suppressor effects**: route to opposing team in `ModifierStack.per_team`, not the source team.

## Architecture

### Existing Infrastructure (PROJ-270 inherited)

- **`StatKey` enum** at `game/simulation/components/abilities/stat_keys.py`. Each entry carries `operation` (MULT or ADD), `target_attribute`, `base_attribute`. Pre-existing ADD-operation precedent: `ACCURACY_ADD`.
- **`AbilityStatBinding`** at `game/modifiers/ability_stat_binding.py`. Maps a `StatKey` onto a concrete ability/component attribute so `FleetAuraManager` can apply the modifier to ship stats.
- **`ModifierStack`** at `game/simulation/combat/modifier_stack.py`. Structure: `per_team: Dict[int, List[ModifierEntry]]` + `global_entries: List[ModifierEntry]`. Per-team application already works (Track A uses it).
- **`FleetAuraManager`** at `game/simulation/combat/fleet_aura_manager.py`. `initialize(ships, modifier_stack=...)` applies entries via `_append_external_from_entry`. Logs a placeholder warning once per source when `stat_key == "placeholder"`.
- **Strategy compiler** at `game/strategy/combat/spec_compiler.py`. PROJ-270 Phase 6.1/6.2 added the `_real_entry()` helper which emits real stat_keys; `_entries_from_fleet_combat_modifiers` is where `flat_shield_bonus` lives.

### Key Patterns to Reuse

- **`_real_entry` helper** at `game/strategy/combat/spec_compiler.py:440-466` — the sanctioned path for emitting a `ModifierEntry` with a real stat_key. Reuse for `flat_shield_bonus`.
- **`ACCURACY_ADD` precedent** — the existing ADD-operation stat_key + its binding + its pipeline wiring is the template for `SHIELD_BONUS_ADD`. Do not invent new architecture — copy the shape.
- **`ModifierStack.per_team[team_id]` routing** — Track A already uses this for friendly-team mods. Suppressors use the same structure, just target the opponent's team_id.

### Dependencies & Risks

1. **`FleetAuraManager` additive pipeline** may not compose correctly with multiplicative entries for the same stat_key (e.g., `shield_bonus_add=50` + `shield_capacity_mult=2.0` — does the base-100 ship end up at (100+50)*2=300 or at 100*2+50=250?). Phase 1.3 has a test for this — if the pipeline orders wrong, fix `FleetAuraManager._append_external_from_entry` or equivalent BEFORE completing Phase 1.
2. **Data-model gap for suppressors**: `FleetCombatModifiers` may not have an explicit "target=opponent" discriminator. Phase 3.1 audit task identifies which field(s) are suppressors. If the data model needs extending, surface that to the user before implementing Phase 3.2.
3. **Combat Lab modifier wiring**: not in scope. Combat Lab tests use per-scenario `ModifierStack` construction, not planet-driven compiler paths. If Phase 1's `SHIELD_BONUS_ADD` changes break a Combat Lab scenario, that's a regression to fix, not a scope expansion.

### Opportunities Discovered

- The `_real_entry` helper (added in PROJ-270 Phase 6.1) already takes `operation` as a kwarg. No helper changes needed for Track B — just pass `operation="add"` for `flat_shield_bonus`.
- Regression guard (`tests/unit/simulation/test_unified_entry_guard.py::TestNoPlaceholderStatKeyInStrategyCompiler`) already has the pattern established by Track A; adding two more assertions (one per Track B modifier source) extends the guard without adding new test classes.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
