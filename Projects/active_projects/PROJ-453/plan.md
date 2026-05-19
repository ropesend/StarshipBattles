# PROJ-453: Engine + Services Surface Polish

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-453` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-453 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** legacy serial-on-main (matches PROJ-443/444 standing preference; no worktrees).

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Mechanical polish sweep (10 findings, all <30 LOC each) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-19
**Active Phase:** Planning
**Last Action:** Cross-group collision resolution applied 2026-05-19; Group B is ready for execution. Serial order confirmed: PROJ-453 → PROJ-454 → PROJ-456 → PROJ-457. PROJ-453 is the first project in Group B's series; no upstream gate. Prior fixes retained: (a) Group 3 pre-execution review (`AgentCoordination/Scratchpad/Consult/20260519T024637Z_group3-pre-execution-review/`) — F-B-011 findings file synced to 6 mutator accessors; 4 Unix-style shell snippets in `phase_1_checklist.md` mechanically swept to `rg -n …`; (b) codex Bucket-B audit fixes — F-B-016 file path corrected `data/` → `services/`; four non-existent test paths replaced with actual paths in phase_1_checklist.md; F-B-011 scope expanded from 4 to 6 accessors (added `environmental_hazard_engine.py:65` and `superweapon_order_processor.py:70`).
**Next Action:** Run agent picks up PROJ-453 Phase 1 first (Group B's entry point).
**Blockers:** None.

## Overview

Mechanical polish job for the `game/strategy/engine/` + `game/strategy/services/` layer. The 10 findings closed here are all individual <30-LOC touches that were aggregated together by the post-PROJ-447 redesign because (a) they share a file-set with PROJ-454's larger retirements, (b) landing them first reduces noise when the larger sweeps run, and (c) they are independent of every other open project in the engine/services cluster (no shared write surfaces with PROJ-452 / PROJ-454 / PROJ-455).

All 10 findings come from `Projects/archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md`. None of them touch behaviour: 6 are missing return annotations on public engine accessors, 1 is a `# type: ignore` mask over a missing annotation, 2 are dead `try / except ImportError` guards in a test file, and 2 are stale docstrings referencing retired surfaces (`_cargo_contents` and the deleted PROJ-300 Phase-7 path).

## Goals

- Close the residual annotation gaps on the public engine + services surface so the layer matches the `docs/03_CONVENTIONS.md` "Public functions and methods require return-type annotations" rule end-to-end.
- Delete the two dead `pytest.skip` guards in `test_superweapon_registry_contract.py` that silently mask any future `command_registry` import breakage.
- Refresh the two stale docstrings in `production_engine.py` and `conflict_modifier_collection.py` that point at code paths PROJ-436 and PROJ-300 retired.
- Reduce the engine/services finding count to zero before PROJ-454 starts the larger retirement sweeps (so the diff against the retirement PRs is purely structural, not polish-mixed-with-structural).

## Scope

**In (this project owns these files):**
- `game/strategy/engine/superweapon_order_processor.py` (F-B-006, F-B-008)
- `game/strategy/engine/order_processor.py` (F-B-007 — `__init__` annotation only; the legacy facade methods are PROJ-454's territory)
- `game/strategy/engine/handlers/fms_shared.py` (F-B-009)
- `game/strategy/engine/turn_engine.py` (F-B-010)
- `game/strategy/engine/harvesting_engine.py`, `atmosphere_engine.py`, `planet_modifier_effect_engine.py`, `production_spawner.py` (F-B-011)
- `game/strategy/engine/production_engine.py` (F-B-015 — docstring only)
- `game/strategy/engine/conflict_modifier_collection.py` + `game/strategy/services/fleet_speed_calculator.py:175` (F-B-016 — docstring only; the `fleet_speed_calculator.py` touch is the parallel `EnvironmentalEffects` reference flagged in the same finding)
- `game/strategy/services/replay_store.py` (F-B-021)
- `tests/unit/strategy/services/test_superweapon_registry_contract.py` (F-B-012)

**Out (PROJ-454 owns these — do NOT touch):**
- `game/strategy/services/effect_ability_metadata.py` (F-B-004 retirement)
- `game/strategy/services/component_inspector.py` (F-B-005 retirement)
- `game/strategy/engine/order_processor.py` legacy result reshape (F-B-017 — touched here only for the `__init__` annotation, not for the facade unwinding)
- `game/strategy/engine/order_handlers/base.py` `OrderExecutionResult` legacy fields (F-B-018)

**Out (PROJ-452 owns):** any catalog-driven resource-surface work (`fleet_dto.py`, `stat_rows_dynamic.py`, `container.py`).

**Out (PROJ-455 owns):** any planet-FMS engine-mediated behavioural coverage work.

**Out of scope entirely (deferred):** legacy `Dict[]` / `List[]` / `Optional[]` PEP-604 rewrite across `game/core/protocols/*` (F-C-030 — that's a UI-bucket finding tracked by the UI sibling jobs).

## Findings Summary

Full report: [findings/PROJ-453_findings.md](findings/PROJ-453_findings.md) (10 findings, all extracted verbatim from `Projects/archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md` and re-verified 2026-05-19 against current code).

| Severity | Count |
|----------|-------|
| Low      | 10    |

| Category | Count |
|----------|-------|
| Polish (annotations + docstrings) | 8 |
| Test-inconsistency (dead skip guards) | 1 |
| Obsolete-code (stale docstrings) | 1 |

## Key Files

| Component | File Path | Finding |
|-----------|-----------|---------|
| SuperweaponOrderProcessor static helper | `game/strategy/engine/superweapon_order_processor.py:340` | F-B-006 (type: ignore + annotation gap) |
| OrderProcessor `__init__` | `game/strategy/engine/order_processor.py:64` | F-B-007 (event_bus param + return annotation) |
| SuperweaponOrderProcessor `__init__` | `game/strategy/engine/superweapon_order_processor.py:56` | F-B-008 (three untyped params + return) |
| `resolve_requested` module helper | `game/strategy/engine/handlers/fms_shared.py:94` | F-B-009 (return annotation + count param) |
| `TurnEngine.planet_modifier_effect_engine` property | `game/strategy/engine/turn_engine.py:521` | F-B-010 (return annotation) |
| 6 `_get_*_mutator` accessors | `game/strategy/engine/harvesting_engine.py:196` (+ `:205`), `atmosphere_engine.py:30`, `planet_modifier_effect_engine.py:34`, `production_spawner.py:101`, `environmental_hazard_engine.py:65`, `superweapon_order_processor.py:70` | F-B-011 (return annotations as `-> Any`) — codex audit 2026-05-19 added the two `environmental_hazard_engine` / `superweapon_order_processor` sites |
| Superweapon test dead skips | `tests/unit/strategy/services/test_superweapon_registry_contract.py:148-154, 172-178` | F-B-012 (delete two `try / except ImportError → pytest.skip` blocks) |
| `IProductionResourceSource` docstring | `game/strategy/engine/production_engine.py:80` | F-B-015 (`_cargo_contents` → `ShipCargoManager`) |
| `lookup_environmental_effects` docstring | `game/strategy/engine/conflict_modifier_collection.py:28-31` (and parallel `game/strategy/services/fleet_speed_calculator.py:175`) | F-B-016 (drop "Phase 7 deletes the legacy path" stale promise) |
| `ReplayStore._iter_replay_files` | `game/strategy/services/replay_store.py:434` | F-B-021 (return annotation) |

Full enumeration in [manifest.md](manifest.md).

## Phase Breakdown

### Phase 1 — Mechanical polish sweep (10 findings, all independent)

All 10 polish items as individual tasks. Order doesn't matter; check off as completed. Single phase because every item is mechanical, independent, and <30 LOC. RED-then-GREEN per item where a behaviour assertion is feasible; for pure annotation drops (no behaviour change) a `pytest tests/unit/strategy/engine/` smoke pass is sufficient verification.

Tasks (10 ordered by file proximity to minimise import re-resolution overhead):

- Task 1.1: F-B-006 — annotate `SuperweaponOrderProcessor._get_system_at_hex`; drop `# type: ignore`
- Task 1.2: F-B-007 — type `OrderProcessor.__init__(event_bus: Optional[Any] = None) -> None`
- Task 1.3: F-B-008 — type all three `SuperweaponOrderProcessor.__init__` params + return
- Task 1.4: F-B-009 — annotate `resolve_requested(count: Optional[int], count_available: int) -> int | ValidationResult`
- Task 1.5: F-B-010 — annotate `TurnEngine.planet_modifier_effect_engine` property
- Task 1.6: F-B-011 — annotate 6 `_get_*_mutator` accessors as `-> Any` (codex audit 2026-05-19: count corrected from 4 to 6; see phase_1_checklist.md Task 1.6)
- Task 1.7: F-B-012 — delete the two dead `try / except ImportError → pytest.skip` guards
- Task 1.8: F-B-015 — fix `_cargo_contents` → `ShipCargoManager` in `IProductionResourceSource.production_consume_resource` docstring
- Task 1.9: F-B-016 — drop "Phase 7 deletes the legacy path" promise; tidy companion reference in `fleet_speed_calculator.py:175`
- Task 1.10: F-B-021 — annotate `ReplayStore._iter_replay_files(rd: Path) -> Iterator[Path]`

## Related Documents

- [design.md](design.md) — architecture rationale + parallelism contract with PROJ-454
- [decisions.md](decisions.md) — decisions log
- [findings/PROJ-453_findings.md](findings/PROJ-453_findings.md) — full finding text (verbatim from bucket B scan)
- [`Projects/archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md`](../../archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md) — source scan
- [`AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md`](../../../AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md) — Codex r4 redesign that produced this project (job #5)

## Dependencies & Sibling Projects

**Group B serial order (coordinator-confirmed 2026-05-19): `PROJ-453 → PROJ-454 → PROJ-456 → PROJ-457`.** PROJ-453 is the FIRST project Group B's run agent executes. No upstream gate.

| Project | Status | Relationship |
|---------|--------|--------------|
| **PROJ-454** (engine + services obsolete-surface retirement) | Active — **Group B successor** | **Soft preference resolved as hard ordering in Group B serial.** Codex r4 redesign: "PROJ-454 depends on PROJ-453 (preferred — polish should land first to reduce noise during the retirement sweeps)." Group B's coordinator-confirmed order makes this preference operative: PROJ-453 lands first, then PROJ-454 deletes the `process_*` facade methods at `order_processor.py:97-143`. The `__init__` annotation (PROJ-453 Task 1.2) lands at `order_processor.py:64-82`; the two sites are line-disjoint. |
| **PROJ-456** (UI shim retirement) | Active — **Group B successor** | Runs third in Group B series. No file overlap with PROJ-453. |
| **PROJ-457** (UI structural debt extractions) | Active — **Group B successor** | Runs fourth (last) in Group B series. No file overlap with PROJ-453. |
| PROJ-452 (catalog-driven resource surfaces) | Active — **Group C** | Disjoint file set; runs in parallel from another agent's series. |
| PROJ-455 (Planet-FMS engine-mediated behavioural coverage) | Active — **Group A/C** | Disjoint test file set; runs in parallel from another agent's series. |

Phase 1 is one mechanical sweep; can land independently from non-Group-B projects in any order.

## Verification

- [ ] All Phase 1 tasks checked off
- [ ] `pytest tests/unit/strategy/engine/ tests/unit/strategy/services/ -q` green
- [ ] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] No new entries in `AgentCoordination/discovered_issues/log.jsonl` from this project's work
- [ ] Audit passed (Codex end-of-project consult per the standing workflow)
- [ ] User verified
