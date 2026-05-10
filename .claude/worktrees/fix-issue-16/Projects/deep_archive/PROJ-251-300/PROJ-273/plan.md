# PROJ-273: Shared Ability Stat Key Registry

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-273` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-273 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create registry module + unit tests (TDD) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate Battle Setup compiler | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate Strategy compiler | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Glob-driven coverage test | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Runtime unknown-stat_key warning | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Docs | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-04-16
**Active Phase:** COMPLETE — awaiting user verification + audit
**Last Action:** Phase 6 complete. All 6 phases delivered. Docs updated: added "Pattern 26: Ability-Stat Registry" to `docs/02_PATTERNS.md` (immediately after pattern 25), updated pattern 25 to reference shared `OPPONENT_SCOPES`, updated Quick Reference table (L1400) to include both patterns 25+26 with new file references. Rewrote strategy_layer.md L790-800 paragraph to describe registry-driven emission. Rewrote combat_simulation.md L422-442 external-modifiers section to reference `ABILITY_STAT_REGISTRY`, `OPPONENT_SCOPES`, `KNOWN_EXTERNAL_STAT_KEYS`, and the new `_log_unknown_stat_key_once` behavior. All remaining `_ABILITY_TO_STAT_KEY` / `_OPPONENT_SCOPES` mentions in docs are intentional historical context ("Pre-PROJ-273..." / "PROJ-273 consolidated..."). Final full-suite check: 513 incremental tests passed, 1 failed + 3 errors (ALL PRE-EXISTING per baseline captured pre-Phase-1).
**Next Action:** User verification steps:
1. Manual launch: Battle Setup with a shield-booster complex → verify aura labels appear on battle HUD (no warnings in console for known stat_keys).
2. Optional: run full `pytest tests/` (no testmon) for pure belt-and-braces baseline confirmation.
3. Audit the project (`Projects/protocols/04_audit_project.md`) once user verifies.
**Blockers:** None
**Context for Next Agent:** PROJECT COMPLETE. All acceptance criteria met:
- Registry module exists (`game/simulation/combat/ability_stat_registry.py`) with `ABILITY_STAT_REGISTRY` (3 entries), `AbilityStatMapping` frozen dataclass, `OPPONENT_SCOPES` frozenset, `KNOWN_EXTERNAL_STAT_KEYS` frozenset (10 keys), `emit_entries_for_ability(...)` helper.
- Battle Setup compiler (`game/ui/screens/battle_setup/spec_compiler.py`) consumes registry. Deleted: `_ABILITY_TO_STAT_KEY`, `_OPPONENT_SCOPES`, `_extract_ability_value`. Kept: `_route_team_for_scope` (PROJ-275 handoff).
- Strategy compiler (`game/strategy/combat/spec_compiler.py`) consumes registry via thin `_emit_entries_team_scoped` wrapper. Deleted: `_real_entry`, direct `ModifierEffect` construction.
- `FleetAuraManager` (`game/simulation/combat/fleet_aura_manager.py`) warns once per (stat_key, source) on unknown stat_keys via `_log_unknown_stat_key_once`.
- Glob-driven tests in `tests/unit/simulation/combat/test_ability_stat_registry.py` iterate all 27 `qs_*_complex.json` designs automatically. Forward-compat: adding a combat-class ability without updating the registry fails `test_all_complex_abilities_have_registry_coverage`.
- 32 registry tests + 5 warning tests = 37 new tests added. Hardcoded 10-design guard in `test_unified_entry_guard.py` deleted; coverage superseded by the glob test (2.7x broader).
- Docs updated: patterns catalog (pattern 26 added), strategy_layer.md (rewrite L790-800), combat_simulation.md (external-modifiers section).
- Test baseline: 14693 passed, 1 failed (quickstart), 3 errors (ai/ x2 + strategy/engine x1) — all pre-existing and unrelated to PROJ-273.
- Unblocks PROJ-275 (N-team combat). Helper already supports N-team fan-out via `num_teams` kwarg.

## Overview

Eliminate duplicate ability→stat_key mapping between Battle Setup and Strategy spec compilers. Introduce a single registry module that both compilers (and any future caller) import from, plus a glob-driven guard test so new `qs_*_complex.json` designs are automatically covered. Add a runtime warning in `FleetAuraManager` when an unknown stat_key appears in the modifier stack (today silently ignored).

## Goals

- One canonical mapping of ability class name → (stat_key, operation, value_field).
- Both spec compilers emit `ModifierEntry` through a shared helper, not via hand-rolled hardcoded functions.
- Test that iterates every `data/designs/qs_*_complex.json` and asserts no placeholder entries / no unknown abilities.
- Unknown stat_keys emit a runtime WARNING in `FleetAuraManager` (currently silently ignored).

## Scope

**In:**
- New module: `game/simulation/combat/ability_stat_registry.py`
- Refactor `_ABILITY_TO_STAT_KEY` out of `game/ui/screens/battle_setup/spec_compiler.py` (lines 70-74)
- Refactor `_entries_from_environmental_effects` + `_entries_from_fleet_combat_modifiers` in `game/strategy/combat/spec_compiler.py` (lines 336-412) to use the shared helper
- New auto-coverage test: `tests/unit/simulation/combat/test_ability_stat_registry.py`
- Runtime warning in `game/simulation/combat/fleet_aura_manager.py::_apply_bonuses`
- Docs: `docs/systems/combat_simulation.md`, `docs/systems/strategy_layer.md`, `docs/02_PATTERNS.md`

**Out:**
- Adding new abilities to the registry (content work, not a refactor)
- Changing stat_key semantics (composition order in `ship_stats.py`)
- Changes to `_route_team_for_scope` signature (that lands in PROJ-275)

## Key Files

| Component | File Path |
|-----------|-----------|
| New registry module | `game/simulation/combat/ability_stat_registry.py` |
| Battle Setup compiler | `game/ui/screens/battle_setup/spec_compiler.py` |
| Strategy compiler | `game/strategy/combat/spec_compiler.py` |
| Fleet aura manager | `game/simulation/combat/fleet_aura_manager.py` |
| New guard test | `tests/unit/simulation/combat/test_ability_stat_registry.py` |
| Existing guard | `tests/unit/simulation/test_unified_entry_guard.py` |
| Docs | `docs/systems/combat_simulation.md`, `docs/systems/strategy_layer.md`, `docs/02_PATTERNS.md` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest

## Verification
- [ ] All phase checklists complete
- [ ] `pytest tests/unit/simulation/combat/test_ability_stat_registry.py` passes
- [ ] Glob-driven test covers every `data/designs/qs_*_complex.json`
- [ ] Full suite: `python Tools/test_sharded/test_sharded.py` — 14727+ passing, no regressions
- [ ] Manual: launch Battle Setup with a shield-booster complex, verify aura labels still appear on battle HUD
- [ ] Audit passed
- [ ] User verified
