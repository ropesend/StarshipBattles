# PROJ-404: Tier 1 B-05 — Eradicate save-format compatibility (Rule 3 follow-on)

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Delete remaining save-format fallbacks + add negative tests | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-09
**Active Phase:** Phase 1
**Last Action:** Project skeleton created from REMEDIATION_PLAN B-05
**Next Action:** Delete two surviving save-format compat surfaces; route raw `KeyError` through `require_keys()`; add negative tests.
**Blockers:** None

## Overview
PROJ-386 deleted the four named save-migration targets, but the same touched files still tolerate other legacy save shapes. Per CLAUDE.md Rule 3 ("old saves are disposable; never write compatibility shims for old save formats"), these must go too. The same review also flagged that `ShipInstanceSerializer.from_dict()` raises raw `KeyError` on missing `components` instead of the documented `PersistenceException`. This project deletes both fallbacks, normalizes the error type, and adds negative tests asserting old shapes are rejected.

## Goals
- Delete the `resource_levels` rename fallback in `ship_instance_serializer.py:106`.
- Delete the missing-`*_complex_toggles` tolerance in `BattleSetupSide.from_dict()` (`battle_setup_state.py:117-130`) including the docstring framing it as legacy compat.
- Route missing `components` through `require_keys()` so the canonical `PersistenceException` is raised (not raw `KeyError`).
- Tests that exercised the legacy paths must be deleted (they encode the bug).
- Add positive-shape regression confirming new format round-trips.
- Add negative tests asserting legacy shapes raise (C-05 from Tier 4 — folded in here per the brief).

## Scope
**In:**
- `game/strategy/data/ship_instance_serializer.py` — delete `resource_levels` fallback; route `components` through `require_keys()`.
- `game/ui/screens/battle_setup_state.py` — delete `*_complex_toggles` tolerance; remove "legacy save" docstring framing.
- Corresponding tests in `tests/unit/...` — delete legacy-path tests; add positive + negative regression tests.

**Out:**
- A repo-wide hunt for other save-format tolerance — that's beyond the specific B-05 finding.
- PROJ-386 manifest/checklist drift — covered by Tier 2 PROJ-406.

## Key Files
| Component | File Path |
|-----------|-----------|
| Serializer | `game/strategy/data/ship_instance_serializer.py` |
| `BattleSetupSide` | `game/ui/screens/battle_setup_state.py` |
| `require_keys` (read-only) | `game/strategy/data/persistence.py` (or wherever `require_keys` lives — confirm) |
| `PersistenceException` (read-only) | likely `game/core/exceptions.py` |
| Serializer tests | `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` |
| Battle-setup tests | `tests/unit/ui/screens/test_battle_setup_state.py` |

## Source Evidence (REMEDIATION_PLAN B-05)
- `game/strategy/data/ship_instance_serializer.py:106` — `consumable_levels=data.get('consumable_levels', data.get('resource_levels', {}))`.
- `game/ui/screens/battle_setup_state.py:117-130` — `BattleSetupSide.from_dict` tolerates legacy missing `*_complex_toggles`.
- `tests/unit/ui/screens/test_battle_setup_state.py:223-235` — legacy-path test that should be deleted.
- `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py:66-69` — assertion is too weak; doesn't reject legacy input.
- PROJ-386 review (`Reviews/results/2026-05-09_proj-380-399-implementation-review/PROJ-386_report.md`).
- CLAUDE.md Rule 3 (no save-migration code).

## Verification
- [ ] Phase 1 checklist complete
- [ ] `pytest tests/unit/strategy/ship_instance/test_ship_instance_serializer.py tests/unit/ui/screens/test_battle_setup_state.py -v` — passes including new positive + negative tests
- [ ] `pytest tests/integration/save_load/test_roundtrip_ships.py -v` — round-trip still passes
- [ ] `pytest tests/integration/ui/test_battle_setup_three_sides.py -v` — passes
- [ ] `python Projects/scripts/validate_audit_ready.py PROJ-404` passes
- [ ] User verified
