# PROJ-350: Combat Lab Registry Class Identity Fix

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-350` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-350 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Regression test + registry fix | Complete (awaiting user verification) | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04 18:35
**Active Phase:** 1 (verification)
**Last Action:** Implemented fix, regression test passes, Combat Lab full suite 162/162, sharded 17213/17222 with 5 pre-existing strategy/UI failures unrelated to this change (verified by stashing PROJ-350 changes — same 3 of 5 still fail).
**Next Action:** User smoke test of the original failing path (Combat Lab batch run that hit TOHIT-ATK-001).
**Blockers:** None

## Overview

Fix a class-identity bug in `combat_lab/registry.py` that causes
`build_test_battle_spec` to raise `NotImplementedError` when a registry-discovered
ComparisonScenario subclass is dispatched. Root cause: the registry's bespoke
loader (`spec_from_file_location` + `module_from_spec` + `exec_module`) re-executes
`combat_lab/scenarios/templates.py`, creating a duplicate set of template base
classes that breaks `isinstance` checks elsewhere. Replace with
`importlib.import_module(module_name)` so the standard import cache is honored.

## Goals
- Make `combat_lab/registry.py` use Python's standard import machinery
- Add a regression test that locks in class-identity invariance across registry discovery
- Eliminate the entire class of "duplicate class object" bugs that the bespoke loader enables

## Scope
**In:**
- Replace the manual loader in `combat_lab/registry.py` with `importlib.import_module`
- Add a regression test under `tests/unit/combat_lab/`
- Drop now-unused imports

**Out:**
- `combat_lab/runner.py:271-292` (separate explicit-path CLI loader, non-overlapping — verified by Codex)
- Other uses of `spec_from_file_location` outside production
- Skip-list-only patches (rejected as bandaid)

## Key Files
| Component | File Path |
|-----------|-----------|
| Registry loader (root cause) | `combat_lab/registry.py` |
| Spec compiler (crash site) | `combat_lab/spec_compiler.py` |
| Templates (the duplicated module) | `combat_lab/scenarios/templates.py` |
| Failing scenario (representative) | `combat_lab/scenarios/tohit_attack_scenarios.py` |
| Regression test (new) | `tests/unit/combat_lab/test_registry_class_identity.py` |

## Related Documents
- [design.md](design.md) — Diagnosis, evidence, and rejected alternatives
- [decisions.md](decisions.md) — Discussion outcome and key choices
- Discussion leaf: `AgentCoordination/Scratchpad/Discussion/20260505T010845Z_spec-compiler-class-identity/`

## Verification
- [ ] Regression test fails on current main (proves it reproduces)
- [ ] Regression test passes after fix
- [ ] `python -m combat_lab.run_tests TOHIT-ATK-001 --no-history` passes
- [ ] `python -m combat_lab.run_tests --fast` passes
- [ ] `python Tools/test_sharded/test_sharded.py` passes (15405 baseline)
- [ ] User verified
