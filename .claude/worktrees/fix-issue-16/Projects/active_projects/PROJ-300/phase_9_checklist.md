# Phase 9: Documentation sync

**Status:** Complete (2026-04-27)
**Objective:** Update `docs/` to describe the new universal ability-source framework. Per CLAUDE.md Rule 2, docs and code stay in sync — this phase makes the new architecture authoritative.

---

## Tasks

### Task 9.1: Update `docs/02_PATTERNS.md` — add `IAbilitySource` pattern [Medium]
**File:** `docs/02_PATTERNS.md`

- [ ] Read existing pattern entries to match the documented style.
- [ ] Add a new pattern entry: **"Universal Ability Source"** (or similar name).
  - Describe `IAbilitySource` protocol + adapter package + iterator + collector pipeline.
  - File references: `game/core/protocols.py`, `game/strategy/services/ability_sources/`, `game/strategy/services/ability_iterator.py`, `game/strategy/services/system_effects_collector.py`.
  - Note the adapter-extension mechanism (`register_source_provider`) future projects use.
  - Reference PROJ-300 as the introducing project; PROJ-301..305 as extending it.
- [ ] Update the patterns count in `docs/README.md` (currently "25 design patterns") if the count changes.

**Notes:**

### Task 9.2: Update `docs/systems/strategy_layer.md` — storm/sector-effects section [Medium]
**File:** `docs/systems/strategy_layer.md`

- [ ] Search for current storm-related content.
- [ ] Replace any references to:
  - `AreaEffectManager` → `system_effects_collector.collect_sector_effects`
  - `EnvironmentalEffects` → effect dict list
  - `StormEffect` → `Storm.abilities`
  - `_entries_from_environmental_effects` → `_entries_from_sector_effects`
- [ ] Add a section describing how storms and facilities both contribute to sector effects via the unified pipeline.
- [ ] Add a diagram or text trace of: hex query → iterator → adapters → collector → aggregated effect dict list → consumer.
- [ ] Document the storm `data/storm_types.json` v2.0 schema.

**Notes:**

### Task 9.3: Update `docs/systems/ability_reference.md` — new abilities [Medium]
**File:** `docs/systems/ability_reference.md`

- [ ] Add entries for the four new abilities:
  - **`ThrustModifier`** — multiplier-style; stat key `thrust_mult`. Combat consumption deferred (registered for stat flow only).
  - **`StrategicSpeedModifier`** — multiplier-style. Consumed by `fleet_movement_engine`.
  - **`EnvironmentalDamage`** — rate-style. `damage_type` parameter for grouping. Consumed by `environmental_hazard_engine` (`/100` per tick).
  - **`FuelDrain`** — rate-style. Consumed by `environmental_hazard_engine`.
- [ ] Add a new section "Rate-style abilities vs multiplier-style abilities" explaining the `kind` discriminator and the two aggregators.
- [ ] Reference the registries: `SYSTEM_EFFECT_ABILITIES` and `ABILITY_STAT_REGISTRY`.

**Notes:**

### Task 9.4: Update `docs/01_ARCHITECTURE.md` if needed [Simple]
**File:** `docs/01_ARCHITECTURE.md`

- [ ] Search for `IStorm`, `AreaEffectManager`, `EnvironmentalEffects`, `StormEffect`.
- [ ] Update `IStorm` protocol description to reflect `abilities` instead of `effects`.
- [ ] Add `IAbilitySource` to the protocols table.
- [ ] Remove `AreaEffectManager` from any service catalog.

**Notes:**

### Task 9.5: Update `docs/guides/adding_abilities.md` [Simple]
**File:** `docs/guides/adding_abilities.md`

- [ ] Add a section "Sector-scope and system-scope abilities":
  - How a component declares `scope: "sector"`.
  - How the collector picks it up.
  - Brief mention that any `IAbilitySource` (storms, future planets/stars/etc.) can declare the same abilities.

**Notes:**

### Task 9.6: Audit any other docs referencing the old systems [Simple]
**File:** N/A (verification)

- [ ] `grep -r "AreaEffectManager\|EnvironmentalEffects\|StormEffect" docs/`
- [ ] For each hit, update or delete the reference.

**Notes:** Docs in `docs/refactoring/` describe historical refactors and are reference-only — leave them alone unless explicitly mis-stating current architecture.

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] All `docs/` references to the old systems are gone
- [ ] `docs/02_PATTERNS.md` has a new "Universal Ability Source" pattern entry
- [ ] `docs/systems/ability_reference.md` documents the four new abilities and the rate-style aggregator
- [ ] Update status to `Complete`
- [ ] Update plan.md — move the project to "Awaiting Verification"
- [ ] Run final full-suite test: `python Tools/test_sharded/test_sharded.py`
- [ ] Run final grep guard for the eradicated names
- [ ] Notify user: project ready for verification
