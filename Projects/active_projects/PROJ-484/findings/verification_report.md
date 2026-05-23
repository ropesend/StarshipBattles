# PROJ-484: Verification Report

**Source audit:** `Reviews/results/2026-05-20_210635_legacy-audit/`
**Run date:** 2026-05-22
**Bundle counts:** 4 verified / 0 rejected / 0 uncertain / 0 INFO / 0 out-of-scope (this bundle)
**Run-wide totals across all 7 sibling projects:** 17 verified / 3 rejected / 0 uncertain / 0 INFO / 12 out-of-scope (audit-self-retracted)

## Verified

| ID | File | Symbol | Replaces | Call sites | Recommendation | Severity | Policy |
|----|------|--------|----------|------------|----------------|----------|--------|
| LEG-A-01 | `game/simulation/entities/ship.py:23` | `CombatConstants` re-export | `game.core.constants.CombatConstants` | 0 | delete | CRITICAL | none |
| LEG-04-MINOR-01 | `game/ui/services/image/__init__.py:37` | `_null_provider` side-effect import | explicit `register_image_provider("null", NullImageProvider)` at line 42 | 0 | delete | MINOR | none |
| LEG-01-008 | `game/simulation/combat/combat_events.py:62` | `DamageContext` re-export | `game.core.combat_types.DamageContext` | 1 (test) | migrate_callers_then_delete | CRITICAL | none |
| LEG-A-02 | `game/simulation/entities/ship.py:22` | `DEFAULT_MAX_MASS` re-export | `game.simulation.physics_constants.DEFAULT_MAX_MASS` | 1 (test) | migrate_callers_then_delete | MAJOR | none |

## Rejected

(None in this bundle. Run-wide rejections recorded in sibling projects' `verification_report.md`.)

## Uncertain (resolved)

(None — no UNCERTAIN verdicts in this bundle.)

## INFO (resolved)

(None — no INFO items were surfaced for this cluster.)

## Out of Scope

(None directly tied to this cluster. Run-wide out-of-scope items recorded in sibling projects' `verification_report.md` where they thematically belong.)

## Notes

- The `_null_provider` import is unusual because the verifier confirmed `null_provider.py` has **no** `register_image_provider` call of its own — unlike `openai_provider.py:418` which does have a side-effect registration. Therefore the explicit registration at line 42 is the sole binding source, and the side-effect import is genuinely a no-op.
- `ship.py:21` carries the header comment "Re-export for backward compatibility and convenient access" that applies to both lines 22 and 23. Remove it once both lines are gone.
