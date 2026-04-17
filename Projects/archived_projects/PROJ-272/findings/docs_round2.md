# PROJ-272 Round-2 Documentation Verification

Scope: verify Round-1's additions (patterns 24-26, two new sections, README header rewrite, modifier data-flow diagram) are internally consistent, and surface anything Round-1 missed. Executed against `c:/Dev/Starship Battles/docs/` on 2026-04-13.

---

## Severity: HIGH (must fix)

### H1. Pattern 13 and Pattern 26 are duplicates

`docs/02_PATTERNS.md` now contains TWO patterns covering the same concept:

- **Pattern 13** (`## 13. Spec Compiler + run_battle (replaces "Battle Mode Strategy")`, lines 959-1030) — substantial treatment with diagram, a full comparison table ("Old mode trait | New BattleSpec field"), a "When to Use" list.
- **Pattern 26** (`## 26. Spec Compiler → run_battle (PROJ-269)`, lines 1334-1346) — short summary of the same mechanism, cites the acceptance guard test.

Both appear in the TOC (entries 13 and 26) and both appear in the Quick Reference table (lines 1371 and 1383). There is no cross-reference between them — an LLM reading the doc sequentially will treat them as separate patterns.

**Fix:** Delete Pattern 26 and merge its unique value (reference to `tests/unit/simulation/test_unified_entry_guard.py` and the "every battle is spec → engine → outcome" enforcement quote) into Pattern 13. Then:
- TOC line 35: remove `26. [Spec Compiler → run_battle]`.
- Quick Reference: remove line 1383 (keep line 1371, which already covers it).
- Header claim `26 patterns` in `02_PATTERNS.md:3` and `README.md:4 / README.md:17 / README.md:66` → `25 patterns`.
- README Step 1 table line 17: `26 design patterns` → `25 design patterns`.
- README directory listing line 66: `26 design patterns` → `25 design patterns`.

---

## Severity: MEDIUM

### M1. Shield formula worded three different ways across three docs

The PROJ-271 semantic fix `(base + flat) × capacity_mult × shield_capacity_mult` is authoritative in `combat_simulation.md:579`, but the other two references give abbreviated forms that could be read as contradictions:

| Doc | Line | Text |
|-----|------|------|
| `combat_simulation.md` | 579 | `(base_shield_capacity + shield_bonus_add) × capacity_mult × shield_capacity_mult` (correct, shows both mults) |
| `combat_simulation.md` | 441 | `Pipeline ordering (base + flat) × mult is locked in ship_stats.py::_apply_aggregated_stats` (hides the two-mult detail) |
| `ability_reference.md` | 1546 | `Pipeline ordering (base + flat) × mult` (same abbreviation) |
| `adding_abilities.md` | 275 | No formula given; prose only |

**Fix options** — either:
- (a) Make `combat_simulation.md:574-587` the single source of truth and reduce the other two to `See "Shield Stat Pipeline Ordering" in combat_simulation.md`, OR
- (b) Update `ability_reference.md:1546` and `combat_simulation.md:441` to spell out `× capacity_mult × shield_capacity_mult` explicitly so all three agree verbatim.

Recommend (a) — keep one canonical formula.

### M2. Phase 8 UI additions are undocumented

Two Phase 8 production UI features ship in code but do not appear in `docs/`:

- `BattleScreen.get_active_modifier_labels` + HUD panel (code at `game/ui/screens/battle_screen.py`).
- `BattleResultsScreen` shields row (code at `game/ui/screens/battle_results_screen.py:253-259`).

Neither term matches anywhere in `docs/` (searched `BattleResultsScreen`, `active_modifier_labels`, `shields row`, `HUD.*modifier`, `modifier labels`). Phase 10 checklist in `Projects/archived_projects/PROJ-271/phase_10_checklist.md` has no entries covering these files — docs sync genuinely missed them.

**Fix:** Add a short "Modifier Visibility" or "Battle HUD Surfacing" subsection to `combat_simulation.md` (naturally fits near the existing `FleetAuraManager` section around line 418) that says:
- Active per-team modifiers are surfaced via `BattleScreen.get_active_modifier_labels() -> List[str]` (consumed by the in-battle HUD panel).
- `BattleResultsScreen` renders a `Shields: current/max` row per surviving ship alongside hull bars.
- Both are read-only views over `ship.external_stats` / `BattleOutcome`; neither mutates state.

### M3. Pattern 24 / 25 structure drift from siblings

Patterns 24-26 use the inline-bold format (`**Where:** ...`) that matches 19-23 — consistent. However:
- Pattern 24 has a `**Don't:**` list.
- Patterns 25 and 26 do not.
- Pattern 13 (the older duplicate) uses the `### Where / ### How It Works` block-heading format.

Not a correctness issue but a readability inconsistency for automated agents parsing patterns. Low priority; flag only if Pattern 26 is kept (see H1).

---

## Severity: LOW

### L1. Quick Reference row 1381 cosmetic oddity

`02_PATTERNS.md:1381`:
```
| External-Stats Bridge | game/simulation/entities/ship.py + fleet_aura_manager.py | ship.external_stats, FleetAuraManager._apply_bonuses |
```

The pattern body (line 1293) cites FOUR files (`ship.py`, `fleet_aura_manager.py`, `abilities/base.py`, `ship_stats.py`); the Quick Reference shows two. Consistent-enough for a summary table, but an agent relying on the Quick Reference alone won't find `get_effective_stat` composition or the ship-level `_apply_aggregated_stats` consumer. Consider amending to:

```
| External-Stats Bridge | ship.py + fleet_aura_manager.py + abilities/base.py | ship.external_stats, FleetAuraManager._apply_bonuses, Ability.get_effective_stat |
```

### L2. README header claim about "stack_group respect" is accurate but untestable from docs

`README.md:4` asserts `FleetAuraManager respects stack_group (intra-group MAX, inter-group SUM) on external entries`. Verified against `combat_simulation.md:427` ("stack_group is respected via two-phase MAX/SUM aggregation"). The pointer chain works but neither doc points at the test lock. Consider adding `locked by tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py` to `combat_simulation.md:427-428`.

### L3. `adding_abilities.md` Step 5 numbering inconsistency

Step 5 calls itself a "4-tier lookup" via structure (section titled "Understand get_effective_stat()") but the numbered list at lines 245-254 contains FOUR items labelled 1/2/3/4. One of those items (item 3, "Composition") is logically a consequence of 1+2, not a separate lookup tier. Not incorrect but slightly confusing. Optional rename: `1. Local`, `2. External`, `3. Composition rule`, `4. Default`. No flow issue with Steps 4 and 6.

---

## Areas Clean

- **Modifier data-flow diagram** (`modifier_system.md:18-36`) — markdown renders fine (fenced code block with plain ASCII, no backticks in path), both paths terminate in the correct consumers, cross-references to patterns 24/25 present at lines 41-42. No broken references to a prior single-path model elsewhere in the file.
- **`adding_abilities.md` Step 5 tier list** — 4-tier lookup is factually correct (matches `Ability.get_effective_stat` at `abilities/base.py:227` and `external_stats` read at line 277-282). No contradicting 3-tier description anywhere in the file.
- **Strategy layer "Complex-Toggle Compilation" subsection** (`strategy_layer.md:771-783`) — internally consistent, ability→stat_key table matches `_ABILITY_TO_STAT_KEY` implementation intent, `_OPPONENT_SCOPES` value matches code (`{"enemy_sector", "enemy_system"}` at `spec_compiler.py:78`), `_NUM_TEAMS = 2` matches code (line 92). Correctly contrasts with the strategy-path pre-routing via `CombatModifierCollector`.
- **Combat sim "Shield Stat Pipeline Ordering" subsection** (`combat_simulation.md:574-587`) — formula is correct, test lock cited, no contradiction with §3 component caching above it.
- **Stale-reference sweep** — no `PROJ-269/270/271 in flight` or `pending PROJ-271` remaining anywhere in `docs/`. `AIPolicy`, `TaskForceOutcome`, `BattleController.run_headless`, `BattleConfig.test_scenario`, `BattleConfig.map_bounds`, `BattleState.mode`, `battle_factories`, `battle_mode_handler` appear ONLY in historical `_ignore/` prompts and in explicit "deleted in PROJ-XX" markers. Clean.
- **Deleted-method sweep** (`_entries_from_modifier_source`, `_noop_hook`, `_placeholder_entry`) — only referenced in historical markers (`combat_simulation.md:83, 430`; `strategy_layer.md:762`). No live "we use X" claims.
- **File-reference accuracy for new patterns 24/25/26** — all referenced files exist: `fleet_aura_manager.py`, `ship_stats.py`, `battle_setup/spec_compiler.py`, `combat_modifier_collector.py`, `strategy/combat/spec_compiler.py`, `combat_lab/scenarios/base.py`, `battle_runner.py`, `tests/unit/simulation/test_unified_entry_guard.py`.
- **README header "Last verified" claims** — all spot-checked claims hold: `ReturnDestination` at `game/core/return_destination.py` (confirmed), `StatKey.SHIELD_BONUS_ADD / SHIELD_CAPACITY_MULT / DAMAGE_MULT` exist in `stat_keys.py`, `BattleConfig` is visual-mode-only per `combat_simulation.md:346-350`.
- **Phantom `run_battle(spec, headless=...)` kwarg** — no remaining uses anywhere in `docs/`.
- **HitRecord contradiction at `combat_simulation.md:125-130`** — now resolved cleanly; single authoritative description.

---

## Summary

One HIGH-severity fix (duplicate Pattern 13/26 plus cascading count corrections), two MEDIUM fixes (shield formula wording variance, undocumented Phase 8 UI), plus three minor cosmetic items. All Round-1 fixes landed cleanly — no regressions from the edits.
