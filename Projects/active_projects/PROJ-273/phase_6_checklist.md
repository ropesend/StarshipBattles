# Phase 6: Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-273 6`
> 2. Only proceed if output shows PASSED

**Status:** Not Started
**Objective:** Update documentation to reference the shared registry as the authoritative source of truth. Add a pattern-catalog entry.

---

## Tasks

### Task 6.1: Add Pattern 26 to patterns catalog [Medium]
**File:** `docs/02_PATTERNS.md`
**Tests:** Manual review

- [ ] Add a new entry: "Pattern 26: Ability-Stat Registry"
- [ ] Include: problem (duplicate ability→stat_key mapping across compilers), solution (single registry + shared helper), file reference (`game/simulation/combat/ability_stat_registry.py`), example of using `emit_entries_for_ability`
- [ ] Note that adding a new ability is a one-line registry edit, and the glob test gives coverage for free
- [ ] Link to both caller sites (battle_setup compiler, strategy compiler)

**Notes:**

### Task 6.2: Update strategy_layer.md guidance [Simple]
**File:** `docs/systems/strategy_layer.md`
**Tests:** Manual review

- [ ] Find the paragraph referencing `_ABILITY_TO_STAT_KEY` (line ~798)
- [ ] Rewrite: "Adding a new complex ability type that should influence combat requires extending `ABILITY_STAT_REGISTRY` in `game/simulation/combat/ability_stat_registry.py`. The glob-driven test in `tests/unit/simulation/combat/test_ability_stat_registry.py` will automatically pick up any new `qs_*_complex.json` design and validate it."
- [ ] Update any other references to the old dict name (`_ABILITY_TO_STAT_KEY`) across the file

**Notes:**

### Task 6.3: Update combat_simulation.md composition paragraph [Simple]
**File:** `docs/systems/combat_simulation.md`
**Tests:** Manual review

- [ ] Find the external-modifier composition discussion (around "External modifiers (PROJ-270...)")
- [ ] Add mention of the registry: "All compiler-emitted modifier stack entries use stat_keys from `ABILITY_STAT_REGISTRY`. `FleetAuraManager` warns once per (stat_key, source) if an unknown stat_key appears."

**Notes:**

### Task 6.4: Sanity check — no stale references [Simple]
**File:** Multiple — grep across `docs/`
**Tests:** Manual grep

- [ ] `grep -rn "_ABILITY_TO_STAT_KEY" docs/` — zero results expected
- [ ] `grep -rn "extending.*_ABILITY_TO_STAT_KEY" docs/` — zero results
- [ ] If any references remain, update them to point at the new module

**Notes:**

### Task 6.5: Full suite final check [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full pytest suite passes
- [ ] Baseline maintained (14727+)
- [ ] Combat Lab suite: `python -m combat_lab.run_tests` — all passing

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State — mark project COMPLETE
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-273 6`
- [ ] User verification: manually launch Battle Setup with a shield-booster complex — aura labels still appear on HUD
