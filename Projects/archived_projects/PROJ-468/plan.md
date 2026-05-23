# PROJ-468: Docs cleanup — reference: systems + guides docs (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-468` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-468 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical content-accuracy errors | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major dead refs + missing docs | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Codex-audit verified additional dead refs | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-20
**Active Phase:** Complete (3 phases, all validate_phase PASSED)
**Last Action:** Phase 3 complete — fixed 5 residual dead refs the Codex advisory audit surfaced in 2 in-scope files (adding_abilities.md, strategy_layer.md): residual `planetary.py`, `EFFECT_ABILITY_METADATA`, `SYSTEM_EFFECT_ABILITIES`. All 5 VERIFIED before fixing. Codex confirmed 0 wrong replacement paths/symbols introduced by Phases 1-2.
**Next Action:** Orchestrator commits. (User applies `verified` after review.)
**Blockers:** None

## Overview
Created from the docs-audit at `Reviews/results/2026-05-20_073330_docs-audit/` after an independent third-pass re-verification. This is the reference bundle: systems docs (`docs/systems/*`) and guide docs (`docs/guides/*`), plus two missing-documentation additions. It carries the **bulk of the audit's CRITICAL content-accuracy errors**: docs across `ability_reference.md`, `strategy_layer.md`, `04_SERVICES.md`, `adding_abilities.md`, `component_system.md`, and `qs_complex_design.md` still teach `component_inspector.py` and `effect_ability_metadata.py` as canonical import paths and even claim a re-export shim "remains importable" — but both files were fully deleted (PROJ-433/429/454). Every example `import` from those paths fails at runtime. 18 verified items total.

## Goals
- Phase 1: Correct 7 CRITICAL content-accuracy errors — replace deleted `component_inspector.py` references with `component_abilities.py` + `component_layers.py`, and deleted `effect_ability_metadata.py` references with `ability_metadata.py`, across 6 docs; remove the false "remains importable" / "thin re-export shim" claims.
- Phase 2: Fix 9 MAJOR dead refs (split-package `planetary/`, `planet_context_menu.py` split, `data/spectrum.py`, `research/ui/`, dead test paths, `test_damage.py` command), add `Last verified:` to `pre_commit_hooks.md`, and add documentation coverage for 2 undocumented architectural-surface modules (`superweapon_order_processor.py`, `game_initializer.py`).

## Scope
**In:** `dead_ref`, `content_error`, and `missing_docs` findings localized to `docs/systems/*`, `docs/guides/*`, and the coordinated `docs/04_SERVICES.md` component-inspector content error (same fix family).
**Out:** Root agent / architecture / protocol docs (see sibling [PROJ-467](../PROJ-467/plan.md)); cross-doc/terminology findings spanning multiple files (see sibling [PROJ-469](../PROJ-469/plan.md)); REJECTED and OUT_OF_SCOPE items (see `findings/verification_report.md`).

## Key Files
| Doc File | Items |
|----------|-------|
| `docs/systems/ability_reference.md` | 5 |
| `docs/guides/adding_abilities.md` | 3 |
| `docs/guides/qs_complex_design.md` | 3 |
| `docs/systems/strategy_layer.md` | 2 |
| `docs/guides/component_system.md` | 2 |
| `docs/guides/testing_infrastructure.md` | 1 |
| `docs/04_SERVICES.md` | 1 |
| `docs/systems/fighters.md` | 1 |
| `docs/systems/minefields.md` | 1 |
| `docs/systems/research_system.md` | 1 |
| `docs/guides/pre_commit_hooks.md` | 1 |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/verification_report.md](findings/verification_report.md) - Independent re-verification of audit claims
- [findings/source_audit.md](findings/source_audit.md) - Pointer to the source audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) - Interactive bundling record

## Verification
- [x] All phase checklists complete
- [x] All tests passing (docs-only change; no code touched — no test impact. Deterministic dead-ref scan clean across 12 touched docs.)
- [ ] Audit passed (Codex audit round pending — orchestrator step 5)
- [ ] User verified
