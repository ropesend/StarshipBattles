# Phase 5: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-284 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Document the demographics loop, the configurable food resource, and the new engines. Ensure PROJ-285 and future work can build on solid docs.

---

## Tasks

### Task 5.1: Document the demographics loop [Medium]
**File:** `docs/systems/strategy_layer.md`

- [ ] Add a major section "Colony Demographics (PROJ-284)" covering:
  - Turn-phase order: `[100-tick loop] -> OrganicsConsumptionEngine -> HappinessEngine -> PopulationEngine`.
  - `ColonySpeciesConfig` (per-colony per-species) and `last_food_ratio` (transient).
  - Happiness formula and bounds.
  - Reproduction formula and decline term.
  - Data-driven food resource via `data/economy.json`.
  - `FoodAllocationEditor` UI entry point.
- [ ] Cross-reference PROJ-283 docs for the habitability formula.

### Task 5.2: Update services catalog [Simple]
**File:** `docs/04_SERVICES.md`

- [ ] Add entries for:
  - `OrganicsConsumptionEngine` (`game/strategy/engine/organics_consumption_engine.py`)
  - `HappinessEngine` (`game/strategy/engine/happiness_engine.py`)
  - `EconomyConfig` (`game/strategy/config/economy_config.py`)
  - `ColonySpeciesConfig` (`game/strategy/data/colony_species_config.py`)

### Task 5.3: Add "swap the food resource" recipe [Simple]
**File:** `docs/systems/strategy_layer.md`

- [ ] Short subsection: "Swapping the population food resource"
- [ ] Steps: (1) edit `data/economy.json` `population_food_resource` to any `resources.json` ID. (2) Ensure the resource is `has_quality: true` and harvestable somewhere in the game. (3) Restart game (or call `set_default_economy_config`).
- [ ] UI relabels automatically; no code edits.

### Task 5.4: Update CLAUDE.md if needed [Simple]
**File:** `CLAUDE.md`

- [ ] If the `get_default_* / set_default_*` pattern needs reinforcement or a new callout, add it. Otherwise no-op.

### Task 5.5: Orphan sweep [Simple]

- [ ] `grep -rn "pop.happiness\s*=" game/` — confirm only `HappinessEngine.process_happiness` writes to it.
- [ ] `grep -rn "happiness=[0-9]" tests/` — flag any legacy static-happiness seeding; update test to seed via engine or switch to asserting post-engine happiness.
- [ ] `grep -rn "base_reproduction_rate\|base_happiness" .` — confirm consumers are only the engines this project adds + PROJ-283 race_config + UI race_environment_panel + docs.

### Task 5.6: Final verification [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green.
- [ ] Manual end-to-end from plan.md Verification section.
- [ ] PROJ-284 plan.md Current State updated to "Complete, ready to close."

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
