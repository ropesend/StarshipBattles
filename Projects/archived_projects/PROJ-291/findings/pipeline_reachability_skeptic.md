# Pipeline End-to-End Reachability — Skeptical Audit

## Verdict

ONE CRITICAL BUG FOUND. Pipeline B (Treasury Population Upkeep) fails end-to-end:
snapshot.total_population_upkeep is computed correctly but snapshot.total_expenses 
(lines 147–150) omits it. Treasury Total row shows Ships+Complexes+Tributes only,
missing population drain. Users see inconsistent math. Pipelines A, C, D work.

---

## Pipelines Traced

### Pipeline A: Multi-resource starvation to UI label

Status: WORKING END-TO-END

1. EconomyConfig.population_consumption loaded from data/economy.json
2. OrganicsConsumptionEngine.process_consumption() 
   - Clears last_consumption_ratios every turn (line 96)
   - Writes per-resource ratios (organics=0.8, metals=0.5)
3. ColonySpeciesConfig.last_food_ratio property
   - Returns min(ratios) = Liebig's Law minimum
4. HappinessEngine reads last_food_ratio
   - Computes raw = base_happiness * ratio * habitability
   - Writes pop.happiness = clamp(raw, 0, 3)
5. StrategySessionFacade.get_colony_demographic_view()
   - Reads pop.happiness (line 710)
   - Wraps in SpeciesDemographicView DTO
6. format_planet_info() calls _happiness_category()
   - Maps happiness to label: Content/Settled/Unhappy
   - Renders in UI

Conclusion: Multi-resource MIN correctly computed, read, persisted, wrapped,
rendered. NO DROP.

---

### Pipeline B: Treasury Population Upkeep in Total

Status: CRITICAL BUG - Data computed but excluded from Total

1. EmpireEconomyCalculator.calculate() line 142:
   - Calls _aggregate_population_upkeep(empire)
   - Sums per-resource upkeep across colonies
   - Writes to snapshot.total_population_upkeep correctly

2. BUG: Total Expenses Calculation (lines 147-150):
   MISSING: + snapshot.total_population_upkeep.get(r, 0.0)

3. EmpireTreasuryPanel renders:
   Tributes: 0
   Ships: 2
   Complexes: 3
   Population Upkeep: -10
   Total: 5    <- WRONG! Should be 15

Root Cause: Line 151 omits the fourth expense category from total aggregation.

Fix: Add + snapshot.total_population_upkeep.get(r, 0.0) to lines 147-150.

---

### Pipeline C: Projection grid math

Status: WORKING END-TO-END

1. PlanetEconomyProjector.project() computes:
   - harvest, upkeep, yard_drain separately
   - Line 104: net = harvest - upkeep - yard
   - Returns frozen ResourceProjection with all four values
   
2. StrategySessionFacade wraps in ColonyDemographicView DTO

3. _projection_grid_rows() renders:
   - harvest_cell, -upkeep_cell, -yard_cell, net_cell
   - Reads proj.net directly (never recomputed)

Verification: net computed once, frozen, read directly. No re-derivation.
Sign convention consistent. NO DROP.

---

### Pipeline D: Uncolonized habitability empire resolution

Status: WORKING CORRECTLY

1. StrategyWindowManager._open_planet_list_window() line 124:
   empire = self.scene.current_empire  <- HUMAN PLAYER's empire

2. Threads through to PlanetListWindow via PlanetReportPanel

3. format_planet_info() checks planet.owner_id is None
   - Calls format_uncolonized_habitability_for_empire()

4. format_uncolonized_habitability_for_empire() line 115:
   species_ids = sorted(empire.resident_species())
   - Reads VIEWING EMPIRE's resident species (count >= 1)

5. Empire.resident_species() (lines 252-270):
   - Iterates self.colonies, returns species with pop.count >= 1

6. Scores per species, renders 0-100 habitability

Conclusion: Empire reference is explicit self.scene.current_empire.
NO CONFUSION, NO DROP.

---

## Findings

### Finding 1: Treasury Total Excludes Population Upkeep Expense

Severity: Critical

Location: game/strategy/engine/empire_economy_calculator.py:147-150

What's wrong: total_expenses aggregation is missing the fourth expense category.
snapshot.total_population_upkeep is computed on line 142 and correctly inserted
as a display row by the treasury panel (lines 276-282), but the Total aggregation
on lines 147-150 does not include it. Result: Treasury Total shows only 3 of 4
expense categories. Users see mathematically inconsistent totals.

Example: Empire with tributes=0, ships=2, complexes=3, population_upkeep=10 shows:
Tributes: 0
Ships: 2
Complexes: 3
Population Upkeep: -10
Total: 5    <- WRONG! Should be 15 (0+2+3+10)

Evidence: Lines 144-151 of empire_economy_calculator.py show that 
snapshot.total_population_upkeep is computed but never added to total_expenses.

Recommended fix: Add + snapshot.total_population_upkeep.get(r, 0.0) to the
total_expenses summation on lines 147-150.

---

## False Positives

- last_food_ratio staleness: OrganicsConsumptionEngine clears the dict
  every turn (line 96). No stale entries. VERIFIED.

- Happiness missing multi-resource: Liebig's Law MIN correctly applied.
  Multi-resource ratios are reflected. VERIFIED.

- Projection grid math errors: Net computed once, frozen in DTO, read
  directly. No re-derivation or double-negation. VERIFIED.

- Net resources overstated: This is a CONSEQUENCE of Finding 1, not a
  separate bug. Fixing Finding 1 fixes net automatically. VERIFIED.

---

## Summary

Pipelines A, C, D all reach their final consumers correctly. Pipeline B
computes the correct data but loses it in the aggregation step, causing
a user-visible mismatch in the Treasury Total row. This is the PROJ-283-290
equivalent of the PROJ-269-270 bug: data computed but silently dropped from
a summary calculation.
