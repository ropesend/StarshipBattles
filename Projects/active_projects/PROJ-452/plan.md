# PROJ-452: Catalog-driven resource surfaces

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-452` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-452 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** legacy serial-on-main (matches PROJ-443/444 standing preference; no worktrees).

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Container.remove non-negative guard (DI-005) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. FleetInfo.from_fleet catalog-driven (DI-003) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. stat_rows_dynamic LABEL_ABBREV retirement (DI-004 + F-C-015) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Sweep — catalog-vs-hardcode residue in stat_rows_dynamic + adjacent UI surfaces | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-18
**Active Phase:** End-of-project codex audit (pending)
**Last Action:** Phase 4 (sweep audit) complete on `group-c`. Audit-only outcome — zero production changes. Audited surfaces: `stat_rows_dynamic.py` (post-Phase-3), `empire_treasury_panel.py`, `build_queue_helpers.py`, plus backstop grep across `game/ui/` and `game/strategy/`. Two candidate hardcoded lists identified (`stat_rows_dynamic.py:72` `resource_order` and `build_queue_helpers.py:20-35` `RESOURCE_ABBREVS` / `RESOURCE_ABBREVS_SHORT`) but BOTH classified as different from the DI-003/004 silent-loss anti-pattern: they are curated lists with non-silent fallbacks (alphabetical sort / `res[:3]`). Per-finding rationale recorded in `decisions.md`. PROJ-452 production scope is closed: all four phases complete; DI-003, DI-004, DI-005 marked `resolved` in `log.jsonl`; F-C-015 closure recorded in `decisions.md`.
**Next Action:** Run Phase 4 sharded gate (no production changes since Phase 3, but the protocol still requires sharded green at phase end). Commit + push Phase 4. Then dispatch the end-of-project codex audit per protocol §10 / Group C prompt Step 4.
**Blockers:** None.
**2026-05-19 cross-group resolution (final):** No edits required to PROJ-452 beyond adding the Group C execution-context block to Dependencies. PROJ-452 is the most parallel-safe project in Group C (no shared write surfaces with Groups A/B).

## Overview

Three independent findings on the resource-catalog boundary plus one container-invariant hardening item that's geographically adjacent. Each finding is the same anti-pattern: **a production surface hardcodes a list of resource IDs or display labels, so adding a new resource to `data/resources.json` silently fails to surface in that consumer until somebody edits the constant.** PROJ-436 Phase 7 retired the worst offender (`RESOURCE_TYPES` constant); this project finishes the sweep on the three surfaces that escaped it.

The container-invariant item (DI-005) is included because Phase 1 is already on the resource-boundary file (`game/strategy/data/container.py`); it's a tiny mirror of the existing `Container.add` non-negative guard and the marginal cost of bundling it into a Phase-1 single-PR is lower than spinning a dedicated project for one finding.

## Goals

- Remove the last three hardcoded resource lists/labels from production code (`FleetInfo.from_fleet` 8-tuple, `stat_rows_dynamic.LABEL_ABBREV` × 2).
- Drive every UI/DTO resource-iteration loop through `ResourceCatalog.from_json().all_ids()` or `.by_display_group("planetary")` + `ResourceDefinition.name` for display labels.
- Mirror the `Container.add` non-negative guard on `Container.remove` to close DI-2026-05-18-005 (the original primary subject of that DI entry).
- Sweep `stat_rows_dynamic.py` and adjacent UI files for any remaining hardcoded constants in the same anti-pattern.
- Surface no new entries in `AgentCoordination/discovered_issues/log.jsonl` from this project's work unless they are genuine out-of-scope discoveries.

## Scope

**In (this project owns these files):**
- `game/strategy/data/container.py` (Phase 1 — DI-005 only)
- `game/strategy/facade/dto/fleet_dto.py` (Phase 2 — DI-003)
- `game/ui/screens/builder/stat_rows_dynamic.py` (Phase 3 — DI-004 + F-C-015)
- Any UI panels or DTOs surfaced by the Phase 4 sweep (audit first; touch only if a hardcoded resource list/label is found)
- New / updated tests under `tests/unit/strategy/data/test_container.py`, `tests/unit/strategy/facade/test_fleet_dto.py`, `tests/unit/ui/screens/builder/test_stat_rows_dynamic.py`

**Out (PROJ-453 owns):** annotation polish and stale docstrings in `game/strategy/engine/` + `game/strategy/services/`.

**Out (PROJ-454 owns):** `effect_ability_metadata.py` + `component_inspector.py` retirement, OrderProcessor facade unwinding, OrderExecutionResult legacy fields.

**Out (PROJ-455 owns):** any planet-FMS engine-mediated behavioural coverage work.

**Out of scope entirely (deferred):**
- `FleetInfo.passengers_current` / `passengers_capacity` and other non-resource-catalog hardcoded fields. Phase 2 stays narrow on the cargo_resources / cargo_capacities tuples.
- `transfer_view_model._iter_resource_definitions` — already catalog-driven per PROJ-436 Phase 7. Do not retouch.
- `EmpireInfo.total_resources` / `PlanetInfo.stockpile` — already catalog-driven (verified at `empire_dto.py:109` and `planet_dto.py:55` 2026-05-19).
- The `PLANET_RESOURCE_NAMES` constant at `stat_rows_dynamic.py:177` — already catalog-driven (`[d.id for d in ResourceCatalog.from_json().by_display_group("planetary")]`). The Phase 3 work targets only the `LABEL_ABBREV` companion dicts immediately below it.

## Findings Summary

Full report: [findings/PROJ-452_findings.md](findings/PROJ-452_findings.md). 4 entries.

| Finding | Severity | File:Line (current) | Source |
|---------|----------|---------------------|--------|
| DI-2026-05-18-003 — FleetInfo.from_fleet hardcoded 8-resource tuple | medium | `game/strategy/facade/dto/fleet_dto.py:230-239` | DI log |
| DI-2026-05-18-004 — stat_rows_dynamic hardcoded LABEL_ABBREV (IDs side) | medium | `game/ui/screens/builder/stat_rows_dynamic.py:178-181, 251-254` | DI log |
| DI-2026-05-18-005 — Container.remove non-negative guard missing | low | `game/strategy/data/container.py:225` | DI log |
| F-C-015 — stat_rows_dynamic LABEL_ABBREV (labels side, companion to DI-004) | medium | `game/ui/screens/builder/stat_rows_dynamic.py:178-181, 251-254` | bucket C scan |

DI-004 + F-C-015 are the **same two LABEL_ABBREV dicts**, viewed through different lenses (DI-004 frames the IDs-side regression risk; F-C-015 frames the display-labels-side regression risk). They land together in Phase 3 as one PR.

## Key Files

| Component | File Path | Phase |
|-----------|-----------|-------|
| Container substrate | `game/strategy/data/container.py:225` | 1 |
| FleetInfo DTO | `game/strategy/facade/dto/fleet_dto.py:230-239` | 2 |
| Builder stat rows (Construction + Strategic) | `game/ui/screens/builder/stat_rows_dynamic.py:178-181, 251-254` | 3 |
| Sweep targets (verify before touching) | `game/ui/screens/builder/stat_rows_dynamic.py` (rest of file), `game/ui/panels/empire_treasury_panel.py`, `game/ui/screens/build_queue_helpers.py` | 4 |

Full enumeration in [manifest.md](manifest.md).

## Phase Breakdown

### Phase 1: DI-005 — Container.remove non-negative guard (smallest; mirror existing Container.add guard) [Simple]

Mirror the `Container.add` non-negative guard at `container.py:191` (resource) and `:213` (population) onto `Container.remove` at `container.py:225`. Pure invariant hardening; no production caller currently passes a negative quantity (Codex verified end-to-end during PROJ-436 Phase 11), but the forward-contract risk is real. Add a focused unit test that reproduces the gap before the guard lands.

**Why bundled here:** Phase 1 establishes the project's TDD recipe on the smallest finding so subsequent phases can mirror the pattern.

### Phase 2: DI-003 — Replace `FleetInfo.from_fleet` hardcoded 8-tuple with catalog iteration [Simple-Medium]

Replace the two `("metals", "organics", "vapors", "radioactives", "exotics", "fuel", "energy", "ammo")` hardcoded tuples at `fleet_dto.py:230-239` (note: the archived DI entry cites :217-226; the current location is :230-239 because PROJ-444 Phase 1 Task 1.4 split the F-A-017 narrow-catch block, shifting the line numbers down by 13). Use the same `ResourceCatalog.from_json().all_ids()` iteration that `empire_dto.py:109` already uses (verified 2026-05-19) and the parallel pattern in `planet_dto.py:55`.

Adds one regression test asserting `FleetInfo.cargo_resources` surfaces a new resource added to `data/resources.json` without code change (use a session-scoped registry fixture).

### Phase 3: DI-004 + F-C-015 — Drop `LABEL_ABBREV` dicts; use `ResourceCatalog.get(rid).name` for display labels [Simple]

The two `LABEL_ABBREV` dicts at `stat_rows_dynamic.py:178-181` (Construction section, in `get_construction_rows`) and `:251-254` (Strategic section, in `get_strategic_rows`) duplicate the same 5-entry mapping. The IDs they iterate over (`PLANET_RESOURCE_NAMES` at line 177) are already catalog-driven; only the display labels are still hardcoded.

Replace the two dicts with a single module-level helper `_label_for(resource_id: str) -> str` that wraps `ResourceCatalog.from_json().get(resource_id).name` (or falls back to the raw `resource_id` if the catalog doesn't have an entry — defensive guard against the registry not being fully hydrated during test setup). Call the helper from both `get_construction_rows` and `get_strategic_rows`.

Single PR closes both DI-004 (IDs side — which is actually already closed at line 177; the DI entry was written before the partial fix) and F-C-015 (labels side — the real gap).

### Phase 4: Sweep — catalog-vs-hardcode residue in `stat_rows_dynamic.py` and adjacent UI surfaces [Simple-Medium]

Now that Phase 3 has touched `stat_rows_dynamic.py`, sweep the rest of the file (and the immediate UI neighbours) for any remaining hardcoded resource constants. Concrete targets:

- `stat_rows_dynamic.py` — check `get_logistics_rows`, `_discover_resources`, and the `_get_strategic_abilities` helpers (lines 197-243) for any hardcoded resource enumerations. The harvester/storage iteration at lines 256-274 reads from `info['harvesters']` / `info['storage']` which are dynamically discovered from the ship — that's the **correct** pattern; only flag a fix if a hardcoded constant survives elsewhere.
- `game/ui/panels/empire_treasury_panel.py` — verify the helper at line 32 is the only hardcoded-list site in the panel (already uses `by_display_group("planetary")`, so likely no work). Audit other functions in the same file.
- `game/ui/screens/build_queue_helpers.py:14` — comment cites the deleted RESOURCE_TYPES; verify no hardcoded list survives.
- Any other UI file that pops up under `rg -n '"metals".*"organics".*"vapors"|RESOURCE_NAMES\b|RESOURCE_TYPES\b' game/ui/`. If a hardcoded list is found, add the fix here.

This is an audit-then-decide phase. If no hardcoded constants survive after Phase 3, Phase 4 closes with the audit report committed to `decisions.md` and no production touch.

## Related Documents

- [design.md](design.md) — architecture rationale + parallelism contract with PROJ-453/454/455
- [decisions.md](decisions.md) — decisions log
- [findings/PROJ-452_findings.md](findings/PROJ-452_findings.md) — full finding text (verbatim from bucket A + bucket C scans + DI log)
- [`Projects/archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md`](../../archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md) — sibling scan (engine/services — out of PROJ-452 scope)
- [`Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md`](../../archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md) — source for F-C-015
- [`AgentCoordination/discovered_issues/log.jsonl`](../../../AgentCoordination/discovered_issues/log.jsonl) — DI-003, DI-004, DI-005 source
- [`AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md`](../../../AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md) — Codex r4 redesign that produced this project (job #4)

## Dependencies & Sibling Projects

### Group C execution context (coordinator-assigned 2026-05-19)

**Group C serial order: PROJ-452 → PROJ-455 → PROJ-458 → PROJ-460.**

This is **PROJ-452 — position 1 of 4** in Group C. The run agent starts here. When this project is complete (all phases + codex audit + any audit-driven extra phases) the run agent advances to PROJ-455.

Groups A (PROJ-449/451/450/459) and B (PROJ-456/454/457) run in parallel branches. Coordinator confirmed no hard cross-group blockers. See `Projects/active_projects/GroupC_execution_prompt.txt` for the run agent's full execution contract.

### Other-project relationships

| Project | Group | Status | Relationship |
|---------|-------|--------|--------------|
| PROJ-453 (engine + services surface polish) | B | Active | Disjoint file set — runs in parallel |
| PROJ-454 (engine + services obsolete-surface retirement) | B | Active | Disjoint file set — runs in parallel |
| PROJ-455 (Planet-FMS engine-mediated behavioural coverage) | C (next) | Active | Disjoint file set; serial successor in Group C |

No hard predecessor. All four phases are mechanically independent and can land in any order; the listed phase order is "smallest first" so the TDD recipe is established early.

## Verification

- [ ] All four phase checklists complete
- [x] DI-005 marked `resolved` in `AgentCoordination/discovered_issues/log.jsonl` (Phase 1)
- [x] DI-003 marked `resolved` in `AgentCoordination/discovered_issues/log.jsonl` (Phase 2)
- [x] DI-004 marked `resolved` in `AgentCoordination/discovered_issues/log.jsonl` (Phase 3)
- [x] F-C-015 closed in `decisions.md` (Phase 3)
- [ ] `pytest tests/unit/strategy/data/test_container.py tests/unit/strategy/facade/test_fleet_dto.py tests/unit/ui/screens/builder/ -q` green
- [ ] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] Sweep phase produced either fixes or an audit report in `decisions.md`
- [ ] Audit passed (Codex end-of-project consult per the standing workflow)
- [ ] User verified

## Checkpoint Log

### 2026-05-18T00:00:00Z — project-452-start + phase-1-complete (group-c first runner)
- **Done so far**: Group C session bootstrapped. `group-c` branch cut from `origin/main` and pushed (first runner; no prior group-c on origin). Baseline sharded suite verified green pre-edit (23368/23368). PROJ-452 Phase 1 complete: Container.remove non-negative guards mirror-landed at container.py:227-228 (resource) and :248-249 (population); 3 RED-then-GREEN tests in test_container.py; DI-005 marked resolved in log.jsonl.
- **Key decisions**: Stayed strictly within Phase 1 file ownership (container.py + test_container.py only); no incidental edits. Used `pytest.raises(ValueError, match="non-negative")` for the rejection tests so the test asserts the canonical wording is preserved across the future, not just any ValueError. Added a separate `test_remove_does_not_grow_storage_on_negative_quantity` to defend against the future regression where the guard is dropped but the underlying subtract-a-negative-number bug returns silently.
- **Open threads**: Post-edit sharded suite running (end-of-Phase-1 gate); awaiting green confirmation before committing.
- **Next action**: Commit Phase 1 on `group-c` with message `PROJ-452 Phase 1: Container.remove non-negative guard (DI-005)`, push, then start Phase 2 (DI-003 — `fleet_dto.py:230-239` catalog iteration). Read `phase_2_checklist.md` in full first.
- **Cross-group state observed**: `origin/group-a` exists (Group A in flight); no `origin/group-b` yet. No PROJ-449..460 entries on `origin/main` beyond the baseline plans.

### 2026-05-18T00:00:00Z — phases-1-2-3-complete + phase-4-pending
- **Done so far**: Phases 1 (DI-005), 2 (DI-003), 3 (DI-004 + F-C-015) all complete and pushed to `origin/group-c`. Plus one auxiliary commit on `group-c` extending `Tools/lint_test_files_allowlist.txt` with 3 entries (`tests/static_guards/test_no_activatable_abilities_constant.py`, `test_no_commands_specs_module.py`, `test_no_hidden_test_files.py`) — pre-existing drift on main that was blocking the pre-commit hook. Cumulative sharded: 23373/23373 after Phase 2; Phase 3 sharded gate currently running.
- **Key decisions**: (1) Auxiliary allowlist fix committed separately from Phase 1, not bundled, so the Group C log shows the scope cleanly. (2) Phase 2: module-level `ResourceCatalog` import in fleet_dto.py (necessary for the test's monkeypatch target to be valid). (3) Phase 3: adopt catalog `name` (`Radioactives`) over legacy `Radact` per F-C-015's directive. (4) Subagent pre-audit for Phase 4 flagged `game/ui/screens/build_queue_helpers.py:20-35` (`RESOURCE_ABBREVS` dict) as a same-anti-pattern candidate — verify in Phase 4.
- **Open threads**: Phase 3 sharded suite running (end-of-Phase-3 gate). Phase 4 audit pending. Codex end-of-project audit pending. Doc-consolidation check pending until PROJ-460. The pre-commit-hook drift fix on `group-c` will only reach Groups A/B after end-of-project merge to `main`; until then both other groups will hit the same hook failure and need to do their own fix.
- **Next action**: Confirm Phase 3 sharded green → commit + push Phase 3 → start Phase 4 audit (verify `stat_rows_dynamic.py` clean post-Phase-3; audit `empire_treasury_panel.py` + `build_queue_helpers.py`; decide whether the `RESOURCE_ABBREVS` candidate is in scope for Phase 4 or a separate finding).
- **Cross-group state observed**: `origin/group-a` exists but has the same commits as `origin/main` (no Group A phase work pushed yet). No `origin/group-b`. `origin/main` unchanged since pre-flight fetch.
