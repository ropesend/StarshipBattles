# Apply Doc Audit — Summary

**Source audit:** `Reviews/results/2026-05-04_090303_docs-audit/`
**Applied at (UTC):** 2026-05-04
**Working tree at start:** dirty (1 unrelated telemetry file — see `preflight.md`)

## Counts

| Verdict | Count |
|---------|-------|
| CONFIRMED (applied) | 14 |
| ALREADY-FIXED | 1 |
| DISPUTED | 2 |
| STALE | 0 |
| INCONCLUSIVE | 3 |
| DEFERRED | 7 |
| **Total work items** | **27** |

CONFIRMED breakdown by tier:
- Tier 0: T0-01, T0-02 (2 items)
- Tier 1: T1-04, T1-05, T1-06, T1-07, T1-08, T1-09, T1-10, T1-11, T1-12 (9 items)
- Tier 2: T2-15, T2-16, T2-19, T2-21 (3 doc edits + 1 protocol-template edit)

ALREADY-FIXED: T1-13 (`AgentCoordination/Scratchpad/` directory exists with all documented subdirectories).

DISPUTED: T0-03 (Python version — `pyproject.toml` says `requires-python = ">=3.13"` so CLAUDE.md and 03_CONVENTIONS.md are correct; AGENTS.md is the disagreeing doc but is not the audit's fix target). T2-22 (Last verified for AGENTS.md / CLAUDE.md / CODEX.md — protocol scope explicitly excludes these from the convention).

INCONCLUSIVE: T2-14 (layer-diagram Assets placement — subjective layout choice). T2-17 (delegate Quick Reference primary file — subjective "primary" choice; cited file exists). T2-20 (retired-protocol visual markers — rename/move out of scope; banners already exist).

DEFERRED: T2-18 (replay system in architecture doc — Tier 3-style new content) plus all six Tier 3 missing-docs items (T3-23 … T3-28).

## Dead-reference scan (deterministic re-check)

| Metric | Before | After |
|--------|--------|-------|
| Total file refs scanned | 715 | 722 |
| Dead refs total | 13 | 2 |
| Dead refs resolved by this run | — | 11 |

The 11 resolved dead refs match the CONFIRMED dead-reference edits applied: T1-04 (10 × `game/core/protocols.py`) + T1-08 (1 × test_lab handler filename). Sanity check passes — no discrepancy.

The 2 remaining dead refs are **intentional false positives** that the audit itself flagged as "no action needed":
1. `docs/03_CONVENTIONS.md:80` → `game/core/input_handler.py` — this is a "DON'T reference this nonexistent file" warning (DOC-G1-008).
2. `docs/02_PATTERNS.md:139` → `game/core/singleton.py` — this is historical removal documentation: "SingletonMeta and game/core/singleton.py were removed by PROJ-297" (DOC-G1-002).

Zero new dead refs introduced by the fix pass.

## Top changes

1. **T1-04** — `game/core/protocols.py` → `game/core/protocols/` across 12 sites in 4 docs (with sub-module-specific paths for ISerializable, IFleet, IRaceRegistry, IOrderable, IRegistryProvider).
2. **T1-07** — README pattern count corrected in 3 sites (Last verified note "31", reading-order table "30", directory-structure listing "30") → all "33"; superseded "Registrar Close-Callback" callout replaced with current Pattern #32/#33 names.
3. **T1-09** — `combat_simulation.md:867` planetary.py ability list expanded from 3 (with 2 stale class names) to 18 current classes.
4. **T2-15** — 4 missing core modules added to architecture table (`ship_classes.py`, `component_state.py`, `state_machine.py`, `return_destination.py`).
5. **T2-19** — 4 PROJ-300..305 strategic abilities added to ability_reference quick-reference table (`EnvironmentalDamage`, `FuelDrain`, `StrategicSpeedModifier`, `ThrustModifier`).

Full per-edit before/after snippets in [changes.md](changes.md). Per-finding verdicts and evidence in [verification_log.md](verification_log.md).

## DEFERRED items (recommended follow-up)

| ID | Topic | Suggested action |
|----|-------|------------------|
| T2-18 | Battle Replay System in architecture doc | Roll into T3-23 |
| T3-23 | Battle Replay System (PROJ-312) | `claude-proj-start "Documentation Coverage Backfill — Replay, Facade Slices, Save Service, Retreat Manager, Ship Component Manager"` (single project covering all six gaps) |
| T3-24 | Strategy Session Facade Slice Architecture | (same project) |
| T3-25 | Save/Load Service (`save_game_service.py`, 519 LOC) | (same project) |
| T3-26 | Retreat Manager (`retreat_manager.py`, 280 LOC) | (same project) |
| T3-27 | Ship Component Manager (`ship_component_manager.py`, 293 LOC) | (same project) |
| T3-28 | Replay System guide | (same project — guide phase) |

A single coordinated project is recommended over six separate ones because the replay subsystem touches both simulation and strategy layers (T3-23, T3-24, T3-25 overlap), and the simulation managers (T3-26, T3-27) share the same combat_simulation.md target doc.

## Notable skips (DISPUTED / INCONCLUSIVE highlights)

- **T0-03 (Python version)**: pyproject.toml is the canonical source of the supported baseline (`requires-python = ">=3.13"` per PROJ-295). CLAUDE.md and 03_CONVENTIONS.md ("3.13+") match pyproject.toml; AGENTS.md ("Python 3.14") is the divergent doc. The audit's chosen fix targets contradict ground truth — no edits applied. If the team wants AGENTS.md aligned with the other docs, that is a separate one-line edit out of this audit's scope.
- **T2-14 (layer-diagram Assets placement)**: ASCII-art diagram redraw or explanatory prose-authoring is subjective; the dependency rules table on the same page is correct.
- **T2-22 (Last verified on root agent docs)**: Protocol 11 §Phase 3 step 4 explicitly excludes AGENTS.md / CLAUDE.md / CODEX.md from the convention, in agreement with the audit's own G3 / G4 scope notes.

## Artifacts

- [verification_log.md](verification_log.md) — per-finding verdict + evidence (27 work items)
- [changes.md](changes.md) — per-CONFIRMED-fix before/after snippets (14 applied)
- [preflight.md](preflight.md) — pre-existing dirty-state record
- [postcheck/raw/doc_file_refs.json](postcheck/raw/doc_file_refs.json) — post-fix dead-ref scan output

## Next steps for the user

1. Review `git diff --stat` — you should see edits to `docs/` and `Projects/protocols/WORKER_TEMPLATE.md` only. **No `game/`, `tests/`, or `Projects/projects_index.md` changes.**
2. Consider committing in a single doc-audit-apply commit, or grouped by tier (T0 / T1 / T2).
3. Optional: run `claude-proj-start` for the deferred Tier 3 documentation backfill (suggested wording above).
4. Optional out-of-audit-scope cleanup: if you want AGENTS.md to align with the other docs on Python version, change `Python 3.14` (line 52) to `Python 3.13+` to match `pyproject.toml`.
