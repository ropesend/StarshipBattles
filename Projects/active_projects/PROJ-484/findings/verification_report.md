# PROJ-484: Verification Report

**Source audit:** `Reviews/results/2026-05-20_210635_legacy-audit/`
**Run date:** 2026-05-22 (corrected during execution after Codex audit found two false positives)
**Bundle counts:** 2 verified / 2 rejected / 0 uncertain / 0 INFO / 0 out-of-scope (this bundle)
**Run-wide totals across all 7 sibling projects:** 15 verified / 5 rejected / 0 uncertain / 0 INFO / 12 out-of-scope (audit-self-retracted)

## Verified

| ID | File | Symbol | Replaces | Call sites | Recommendation | Severity | Policy |
|----|------|--------|----------|------------|----------------|----------|--------|
| LEG-04-MINOR-01 | `game/ui/services/image/__init__.py:37` | `_null_provider` side-effect import | explicit `register_image_provider("null", NullImageProvider)` at line 42 | 0 | delete | MINOR | none |
| LEG-01-008 | `game/simulation/combat/combat_events.py:62` | `DamageContext` re-export | `game.core.combat_types.DamageContext` | 1 (test) | migrate_callers_then_delete | CRITICAL | none |

## Rejected

| ID | File | Symbol | Original verdict | Rejection rationale (verified 2026-05-22) |
|----|------|--------|-------------------|-------------------------------------------|
| LEG-A-01 | `game/simulation/entities/ship.py:23` | `CombatConstants` re-export | 0 call sites; delete | Audit miscounted call sites — symbol is used internally in same module (`ship.py:190`: `self.max_targets = CombatConstants.DEFAULT_MAX_TARGETS`). Line 23 is the only `CombatConstants` import in the file. Not a re-export; line must remain. |
| LEG-A-02 | `game/simulation/entities/ship.py:22` | `DEFAULT_MAX_MASS` re-export | 1 (test); migrate + delete | Audit miscounted call sites — symbol is used internally in same module (`ship.py:116`: `self.max_mass_budget = class_def.get('max_mass', DEFAULT_MAX_MASS)`). Line 22 is the only `DEFAULT_MAX_MASS` import in the file. Not a re-export; line must remain. The test caller (`tests/unit/entities/test_ship.py:472`) was still migrated to the canonical `game.simulation.physics_constants` path, since that is independently beneficial. |

## Uncertain (resolved)

(None — no UNCERTAIN verdicts in this bundle.)

## INFO (resolved)

(None — no INFO items were surfaced for this cluster.)

## Out of Scope

(None directly tied to this cluster. Run-wide out-of-scope items recorded in sibling projects' `verification_report.md` where they thematically belong.)

## Notes

- The `_null_provider` import is unusual because the verifier confirmed `null_provider.py` has **no** `register_image_provider` call of its own — unlike `openai_provider.py:418` which does have a side-effect registration. Therefore the explicit registration at line 42 is the sole binding source, and the side-effect import is genuinely a no-op.
- `ship.py:21` carries the header comment "Re-export for backward compatibility and convenient access" that originally applied to both lines 22 and 23. After this audit correction, both lines 22 and 23 remain in place (live internal imports), so the comment is misleading but harmless. Correcting it is out of PROJ-484's corrected scope; defer to a future audit-fix project if desired.
- **Lesson learned for future legacy audits:** when auditing "re-exports", a `# Re-export for backward compatibility` comment is NOT sufficient to classify a normal `import` line as a re-export. The audit must also grep the same module for internal uses of the imported symbol. Both rejected items in this bundle would have been caught earlier by that check.
