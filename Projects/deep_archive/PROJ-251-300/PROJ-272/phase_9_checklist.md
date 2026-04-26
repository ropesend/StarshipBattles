# Phase 9: Documentation pass (HIGH — Docs-H1; MEDIUM — Docs-M1, M2; E2E H-1, H-4)

**Status:** Complete
**Risk:** LOW (docs-only)
**Depends On:** Phases 2 + 6 (updated code/semantics must precede doc formalization)
**Objective:** Multiple doc gaps surfaced by round-2 audit:
1. Pattern 13 and Pattern 26 in `02_PATTERNS.md` are DUPLICATES (both cover Spec Compiler + run_battle). Round-1 added 26 without noticing 13.
2. Shield formula worded 3 different ways across docs.
3. Phase 8 UI additions (shield row, HUD labels) undocumented.
4. 3+ team behavior undocumented (E2E H-1).
5. Mid-battle destruction semantic limits (external entries are static) undocumented (E2E H-4).

## Tasks

### Task 9.1: Delete duplicate Pattern 26 [Simple]
**File:** `docs/02_PATTERNS.md`

- [ ] Read Pattern 13 and Pattern 26 — confirm they cover the same material.
- [ ] Merge any Pattern 26 content not already in Pattern 13 INTO Pattern 13.
- [ ] Delete Pattern 26 section entirely.
- [ ] Update TOC (line ~32) — remove entry 26.
- [ ] Update header (line 3) — "26 patterns" → "25 patterns".
- [ ] Remove Pattern 26 row from Quick Reference table.

**Files also needing count update:**
- `docs/README.md` line 17 — "26 design patterns" → "25 design patterns"
- `docs/README.md` line 66 — same.

### Task 9.2: Canonicalize shield formula [Simple]
**Files:** `docs/systems/combat_simulation.md`, `docs/systems/ability_reference.md`, `docs/guides/adding_abilities.md`

- [ ] Pick ONE authoritative source for the shield formula (recommend `combat_simulation.md` "Shield Stat Pipeline Ordering" section).
- [ ] Other locations link to it with a one-line summary + backreference.
- [ ] After Phase 6 lands, the formula is `(base + flat) × shield_capacity_mult` — update all three locations consistently.

### Task 9.3: Document Phase 8 UI additions [Medium]
**File:** `docs/systems/combat_simulation.md` (or a new UI-modifier-visibility section)

- [ ] Document `BattleResultsScreen` "Shields: C/M" row (file + what it renders).
- [ ] Document `BattleScreen.get_active_modifier_labels()` + HUD panel (file + when it shows + format).
- [ ] Add cross-ref from `docs/README.md` Step 3 systems table.

### Task 9.4: Document 3+ team behavior [Simple]
**Files:** `docs/systems/combat_simulation.md`, `docs/systems/strategy_layer.md`

- [ ] Battle Setup compiler: document `_NUM_TEAMS = 2` assumption — if triggered with >2 teams, behavior is "NotImplementedError" (after Phase 10 lands).
- [ ] Strategy: document that `SimulationBattleResolver.resolve_battle` takes exactly 2 fleets. Multi-empire conflicts are resolved as sequential 2-fleet battles by `ConflictResolutionEngine`.

### Task 9.5: Document mid-battle destruction limits [Simple]
**File:** `docs/systems/strategy_layer.md` "Battle Setup Complex-Toggle Compilation" section

- [ ] Note: Battle Setup complexes enter the battle as STATIC ModifierStack entries, NOT as live ships. They cannot be destroyed mid-battle; their effects persist for the full battle regardless of what happens in-fight. If a design needs destructible aura providers, the source must be an actual ship-mounted ability on a combat-capable ship.

### Task 9.6: Fix LOW docs nits [Simple]
- [ ] Pattern 24 Quick Reference row: verify file paths are complete (2 of 4 missing per round-2 audit).
- [ ] README "stack_group respect" claim: add pointer to the locking test(s).
- [ ] `adding_abilities.md` Step 5 "4-tier" numbering: review wording (item 3 is a consequence, not a tier).

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] Pattern 26 deleted; count rolled back to 25 everywhere
- [ ] One canonical shield formula
- [ ] Phase 8 UI documented
- [ ] 3+ team + destruction limits documented
- [ ] Update plan.md
