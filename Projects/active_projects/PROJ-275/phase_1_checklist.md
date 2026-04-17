# Phase 1: Audit Phase (Read-Only)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-275 1`
> 2. Only proceed if output shows PASSED

**Status:** Not Started
**Objective:** Catalog every 2-team assumption in the codebase. Produce a comprehensive findings report before writing any code.

---

## Tasks

### Task 1.1: Grep for 2-team assumptions [Simple]
**File:** Multiple — read-only sweep
**Tests:** N/A

- [ ] Run `grep -rn "_NUM_TEAMS" game/ tests/` — catalog all occurrences
- [ ] Run `grep -rn "team_id == 0\|team_id == 1" game/` — catalog hardcoded checks
- [ ] Run `grep -rn "team_modifiers\[0\]\|team_modifiers\[1\]" game/` — catalog indexed accesses
- [ ] Run `grep -rn "side_0\|side_1" game/` — catalog Battle Setup state references
- [ ] Run `grep -rn "fleet1.*fleet2\|fleet_1.*fleet_2" game/ tests/` — catalog 2-fleet signatures
- [ ] Run `grep -rn "(_NUM_TEAMS - 1)\|(1 - owner)\|(1 - team)" game/` — catalog arithmetic 2-team tricks
- [ ] Write findings to `findings/audit_2team_assumptions.md`

**Notes:**

### Task 1.2: Classify findings — load-bearing vs. cosmetic [Medium]
**File:** `findings/audit_2team_assumptions.md`
**Tests:** N/A

- [ ] For each occurrence, tag as:
  - **Load-bearing:** the logic breaks for N≠2 (e.g. `(_NUM_TEAMS - 1) - owner` in `_route_team_for_scope`)
  - **Cosmetic:** a variable name or comment that happens to say "2-team" but the code generalizes (e.g. loop over teams list)
  - **UI:** User-facing layout — Battle Setup panels hardcoded to "Side 0" / "Side 1"
  - **Test-only:** Test fixtures that set up 2 teams specifically
- [ ] Produce a count summary table: N load-bearing / N cosmetic / N UI / N test-only
- [ ] For each load-bearing finding, note the blast radius (how many callers depend on it)

**Notes:**

### Task 1.3: Audit Battle Setup UI layout [Complex]
**File:** `game/ui/screens/battle_setup/panels/`
**Tests:** N/A

- [ ] List all files in `game/ui/screens/battle_setup/panels/`
- [ ] For each panel: identify if it references `side_0` / `side_1` directly or via state lookup
- [ ] Identify panels that parameterize on "side index" vs those hardcoded to left/right layout
- [ ] Identify the overall layout strategy (two columns, grid, tabs?)
- [ ] Write findings to `findings/audit_battle_setup_ui.md` with:
  - Panel file list
  - Which panels need refactor (hardcoded)
  - Which already parameterize
  - Proposed layout for N sides (tab-based? Scrollable column?)
- [ ] Flag this as "UI complexity" — may expand the project's scope

**Notes:**

### Task 1.4: Audit strategy conflict resolution flow [Medium]
**File:** `game/strategy/turn_engine/conflict_resolution_engine.py`, `game/strategy/adapters/simulation_adapter.py`
**Tests:** N/A

- [ ] Read `conflict_resolution_engine.py` end-to-end
- [ ] Identify the specific function that decomposes 3+ empires into sequential 2-fleet battles
- [ ] Document inputs → what gets iterated → outputs
- [ ] Identify: does the current resolver respect fleet ORDER when sequencing? (Determinism concern.)
- [ ] Document `SimulationBattleResolver.resolve_battle` — what args it takes, where `team_modifiers` comes from
- [ ] Write to `findings/audit_strategy_conflict_flow.md`

**Notes:**

### Task 1.5: Audit apply_outcome_to_fleets [Simple]
**File:** `game/strategy/combat/post_battle_hook.py`
**Tests:** N/A

- [ ] Read `apply_outcome_to_fleets` end-to-end
- [ ] Identify any hardcoded 2-team assumptions
- [ ] Check if it iterates `outcome.team_outcomes.items()` or indexes `[0]` / `[1]`
- [ ] Add findings to the audit report

**Notes:**

### Task 1.6: Audit report review [Simple]
**File:** `findings/audit_2team_assumptions.md` (composite)
**Tests:** N/A

- [ ] Compose a master audit summary with all findings
- [ ] Present count: load-bearing N sites, UI N files, test N sites
- [ ] Propose Phase 5 (UI) scope based on findings
- [ ] Flag any surprises or unknown blast-radius items for user discussion BEFORE proceeding to Phase 2

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-275 1`
- [ ] User acknowledges audit findings (may trigger scope renegotiation)
