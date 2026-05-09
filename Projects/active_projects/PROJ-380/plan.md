# PROJ-380: Audit-shrink cleanup 2026-05-07

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-380` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-380 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Dead imports | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Dead functions (deprecated statics) | Complete (superseded) | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Duplication consolidation | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 3 — Not Started (Phases 1 & 2 done)
**Last Action:** Phase 2 marked superseded by PROJ-384 (commit 6398bb1da deleted all 6 *_static ModifierManager methods)
**Next Action:** Execute Phase 3 tasks in order (3.1 → 3.9)
**Blockers:** None

## Overview
Created from the audit-shrink review at `Reviews/results/2026-05-07_220215_audit_shrink/` after a skeptical re-verification pass. The audit flagged 13 verified-safe items (1 dead import + 12 CRITICAL/MAJOR duplications). Independent verification confirmed 11 (1 dead import, 1 dead-function block, 9 duplications), reduced scope on 2 (DUP-X-05 preserves the still-used `remove_modifier_inplace` helper; DUP-X-10 is fleet_ops-scoped only), rejected 1 (DUP-X-04 hit-effect rendering — specialized variations, not parameterizable), and parked 1 as uncertain (DUP-X-03 ability `__init__` boilerplate — only 2 of 5 abilities are true twins). Audit-claimed reclaimable LOC for the verified-only set: ≈ **310 LOC**.

## Goals
- **Phase 1:** Remove 1 verified dead import + fix one stale string annotation.
- **Phase 2:** Delete 5 deprecated `ModifierManager` static methods (~95 LOC) while preserving `remove_modifier_inplace` (still used internally).
- **Phase 3:** Consolidate 9 verified CRITICAL/MAJOR duplications across superweapon handlers, factories, cargo aggregation, click dispatch, event log, fleet ops, BattleEndCondition serialization, and ability source providers.

## Scope
**In:**
- Tier 4 dead imports verified by independent re-grep against tests/docs/data/JSON-driven dispatch.
- CRITICAL + MAJOR duplication clusters from the audit's Section 4 with concrete extraction targets that survived independent verification.
- Scope-reduced variants of DUP-X-05 (preserve internal helper) and DUP-X-10 (fleet_ops sites only).

**Out:**
- Anything the audit tagged `PRODUCT_DECISION`, `UNCERTAIN`, or `false_positive` (see [findings/verification_report.md](findings/verification_report.md)). This includes `ShipPickerStub`, `create_brick`/`create_interceptor`, `allocate_crew_and_life_support`, `has_superweapons`, and the four `__exit__` / TYPE_CHECKING false positives.
- Complexity hotspots from Section 5 of the source audit (47 functions with CC ≥ 20).
- MINOR / INFO duplications (DUP-X-13 through DUP-X-22).
- DUP-X-04 (hit effect rendering) — REJECTED in verification: three functions have specialized rendering, not parameterizable.
- DUP-X-03 (ability `__init__` boilerplate) — UNCERTAIN: needs human judgement on partial vs full consolidation given diverging field schemas across 5 ability classes.

## Key Files
| Component | File Path |
|-----------|-----------|
| AI controller | `game/ai/controller.py` |
| Modifier manager | `game/simulation/components/modifier_manager.py` |
| Superweapon command handlers | `game/strategy/engine/superweapon_command_handlers.py` |
| LLM provider factory | `game/services/llm/factory.py` |
| Image provider factory | `game/ui/services/image/factory.py` |
| Fleet cargo aggregator | `game/strategy/data/fleet_consumable_aggregator.py` |
| Strategy click dispatcher | `game/ui/screens/strategy_click_dispatcher.py` |
| Strategy superweapons UI | `game/ui/screens/strategy_superweapons.py` |
| Event log data source | `game/ui/screens/event_log_data_source.py` |
| Strategy fleet ops UI | `game/ui/screens/strategy_fleet_ops.py` |
| BattleEndCondition hierarchy | `game/simulation/systems/battle_end_conditions.py` |
| Ability iterator | `game/strategy/services/ability_iterator.py` |

## Related Documents
- [design.md](design.md) - Source-audit summary and verification metrics
- [decisions.md](decisions.md) - Full decisions log
- [findings/verification_report.md](findings/verification_report.md) - Verified / Rejected / Uncertain breakdown
- [findings/source_audit.md](findings/source_audit.md) - Pointer to the originating audit-shrink review

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
