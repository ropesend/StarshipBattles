# PROJ-293: Habitability Factor Display Refactor (UI Label Overflow)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-293` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-293 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add display fields to HabitabilityFactor | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Refactor format_value to data-driven | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Resize labels & verify zero warnings | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-26 06:30
**Active Phase:** Planning Complete — awaiting user approval
**Last Action:** Plan drafted; research findings written to findings/research.md
**Next Action:** User reviews plan; on approval, implement Phase 1
**Blockers:** None
**Context for Next Agent:** This is a 3-phase refactor that closes a gap in the FACTOR_REGISTRY pattern (PROJ-283). Each factor will declare its own display unit + precision instead of UI code branching on `unit` strings. Test coverage is good in [tests/unit/ui/widgets/test_preference_row.py](../../../tests/unit/ui/widgets/test_preference_row.py); extend it to lock in the new contract.

## Overview

The race habitability editor's `PreferenceRow` widget produces 7 `pygame_gui.UserWarning: Label Rect is too small for text` warnings at runtime ([game/ui/widgets/preference_row.py](../../../game/ui/widgets/preference_row.py)). Two coupled root causes:

1. **Label widths are too tight** — `_SETPOINT_LABEL_WIDTH = _TOLERANCE_LABEL_WIDTH = 60px` ([preference_row.py:45-46](../../../game/ui/widgets/preference_row.py#L45-L46)). Even `"101.3 kPa"` overflows by 3px.
2. **Display formatting violates FACTOR_REGISTRY single-source-of-truth (PROJ-283)** — `format_value()` ([preference_row.py:73-98](../../../game/ui/widgets/preference_row.py#L73-L98)) hardcodes unit handling for `Pa`/`K`/`m/s^2`/`fraction`/`earth_equiv` and falls through to `f"{scaled:.2f} {unit}"` for the rest, producing `"0.30 fraction"` and `"±50.00 shielding"`.

**Fix:** Make display formatting a property of each `HabitabilityFactor` (declarative `display_unit` + `display_precision` fields). Collapse `format_value()` to one data-driven line. Bump label widths so even short units have breathing room.

## Goals

- Eliminate all 7 `Label Rect is too small` warnings at runtime (zero pygame_gui label warnings on game launch).
- Restore the FACTOR_REGISTRY contract: adding a new factor should be a single registry edit with no UI-side branching to update.
- No regression in habitability scoring, race-point budget, or the race editor UX.

## Scope

**In:**
- Add two new fields (`display_unit: str`, `display_precision: int`) to `HabitabilityFactor` ([game/strategy/data/habitability_factors.py](../../../game/strategy/data/habitability_factors.py))
- Populate the new fields on all 7 scalar factors and the gas-factor builder
- Refactor `PreferenceRow.format_value()` to use the new fields
- Bump `_SETPOINT_LABEL_WIDTH` and `_TOLERANCE_LABEL_WIDTH` from 60 → 90px (room for "±50.00 shld")
- Extend test coverage in [tests/unit/ui/widgets/test_preference_row.py](../../../tests/unit/ui/widgets/test_preference_row.py) to lock in the new contract
- Extend test coverage in [tests/unit/strategy/data/test_habitability_factors.py](../../../tests/unit/strategy/data/test_habitability_factors.py) to assert every factor has `display_unit` set and `display_precision >= 0`

**Out:**
- Changes to habitability scoring (the `extractor`/`scorer` callables are untouched)
- Changes to point budget math (`calculate_factor_cost` is untouched)
- Refactoring `unit` (storage unit) — keep as-is; it's still the canonical storage label
- Layout reflow of `PreferenceRow` beyond the two label-width constants
- Any work on the atmosphere target editor ([game/ui/screens/atmosphere_target_editor.py](../../../game/ui/screens/atmosphere_target_editor.py)) — it doesn't use `format_value()` per research

## Key Files

| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Factor registry (data) | [game/strategy/data/habitability_factors.py](../../../game/strategy/data/habitability_factors.py) | `HabitabilityFactor`, `FACTOR_REGISTRY` |
| UI row widget | [game/ui/widgets/preference_row.py](../../../game/ui/widgets/preference_row.py) | `PreferenceRow.format_value`, `_SETPOINT_LABEL_WIDTH`, `_TOLERANCE_LABEL_WIDTH` |
| UI row tests | [tests/unit/ui/widgets/test_preference_row.py](../../../tests/unit/ui/widgets/test_preference_row.py) | `TestDisplayScaling` |
| Registry tests | [tests/unit/strategy/data/test_habitability_factors.py](../../../tests/unit/strategy/data/test_habitability_factors.py) | `TestRegistryShape`, `TestGasFactorWeights` |

## Related Documents

- [design.md](design.md) - Architecture, swarm findings, key patterns
- [decisions.md](decisions.md) - Decision log (defaults, naming, label width chosen)
- [findings/research.md](findings/research.md) - Call sites, factor inventory, test coverage map

## Verification

- [ ] All phase checklists complete
- [ ] `pytest tests/unit/ui/widgets/test_preference_row.py tests/unit/strategy/data/test_habitability_factors.py` — all green
- [ ] `python Tools/test_sharded/test_sharded.py` — full suite green (15109+ tests)
- [ ] Manual smoke: launch game, open race editor, scroll all habitability rows — zero `Label Rect is too small` warnings in stderr
- [ ] User verified
