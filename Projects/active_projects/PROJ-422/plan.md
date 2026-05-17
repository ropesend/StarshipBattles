# PROJ-422: Split engine interface monolith (TD-09)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-422` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-422 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Docs read + structural TDD anchor test | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Introduce the engines package | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Align top-level interfaces aggregator | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Validate consumers (regression sweep) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Docs sync | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Clean review | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-16
**Active Phase:** All phases complete; ready for user verification
**Last Action:** Phase 5 complete — diff-shape audit, leaf inspection, surface checks. Diff vs `07eddbe93` (the user's pre-existing branch commit): 1 deletion (engines.py, -778), 10 additions (engines/ leaves + __init__.py), 1 rewrite (interfaces/__init__.py), 1 new test, plus project scaffold + test_baseline receipts. Zero concrete engine edits. `engines.__all__` has exactly 18 names; all TYPE_CHECKING imports are referenced.
**Next Action:** User verification + archive via `/claude-proj-archive` when ready.
**Blockers:** None

## Overview
Convert `game/strategy/interfaces/engines.py` (778 LOC, 18 ABCs spanning 9 unrelated domains) into a `game/strategy/interfaces/engines/` package with one leaf module per domain, re-exporting every ABC through `engines/__init__.py` so the 30 existing consumers (production engines, TurnEngine, tests, mocks) keep working with zero churn. The split is symbol-preserving and mechanical; no interface contracts change, no concrete engine logic changes.

## Goals
- Replace the 778-LOC monolith with 9 domain-scoped leaf modules, each well under 200 LOC and comfortably under the project's 500-LOC ceiling.
- Preserve every existing `from game.strategy.interfaces.engines import I<Name>` import path via an explicit package `__init__.py` re-export (the stable seam — not a "fallback shim" in the AGENTS.md sense).
- Close pre-existing drift: `engines.__all__` currently misses `IComponentActivationEngine`, and `game/strategy/interfaces/__init__.py` re-exports only 13 of 18 ABCs. The split adds the missing 5 and asserts the contract with a layout test.
- Establish a structural regression test (`tests/unit/strategy/interfaces/test_engines_package_layout.py`) that enforces the package layout + symmetric re-export between `engines.__all__` and `game.strategy.interfaces.__all__` going forward.
- Make the monolith deletion a root-cause fix per AGENTS.md (no parallel "old + new" path; `engines.py` is removed in Phase 1).

## Scope
**In:** package conversion of `game/strategy/interfaces/engines.py`; one new layout regression test; rewrite of `game/strategy/interfaces/__init__.py` to re-export all 18 ABCs; minor docs sync for any page that calls out `engines.py` as a single file.

**Out:** renaming ABCs (e.g. the PROJ-286 `IOrganicsConsumptionEngine` deferred rename); merging or reducing the ABC count; concrete engine refactors (TD-04, TD-05); changes to `TurnEngineConfig` or `turn_phase_registry.py`; touching `interfaces/battle_resolver.py` (already separate).

## Dependencies
Hard predecessors: none. Soft predecessors: none. This project should run first because it is the lowest-risk mechanical change in the strategy tech-debt arc — symbol-preserving, no consumer churn — and it removes noise from later imports without changing behavior. See [EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) §"Recommended Linear Order #1".

This project unblocks (soft-preference only): **PROJ-428 (TD-04 phase registry hooks)** — TD-04's new phase classes can import narrower domain contracts from the split package rather than from a 778-LOC pile.

## Key Files
| Component | File Path | Type |
|-----------|-----------|------|
| Current monolith (to delete) | `game/strategy/interfaces/engines.py` | Production |
| New package entry (re-export) | `game/strategy/interfaces/engines/__init__.py` | Production (new) |
| Fleet movement domain | `game/strategy/interfaces/engines/movement.py` | Production (new) |
| Orders domain | `game/strategy/interfaces/engines/orders.py` | Production (new) |
| Combat / hazards domain | `game/strategy/interfaces/engines/combat.py` | Production (new) |
| Production domain | `game/strategy/interfaces/engines/production.py` | Production (new) |
| Resource / logistics domain | `game/strategy/interfaces/engines/logistics.py` | Production (new) |
| Colony / population domain | `game/strategy/interfaces/engines/population.py` | Production (new) |
| Planet operations domain | `game/strategy/interfaces/engines/planet_ops.py` | Production (new) |
| Terraforming domain | `game/strategy/interfaces/engines/terraforming.py` | Production (new) |
| Component lifecycle domain | `game/strategy/interfaces/engines/components.py` | Production (new) |
| Top-level interfaces aggregator | `game/strategy/interfaces/__init__.py` | Production (rewrite) |
| Layout regression test | `tests/unit/strategy/interfaces/test_engines_package_layout.py` | Test (new) |

Full enumeration of touched files (production + tests + docs) lives in [manifest.md](manifest.md).

## Phases

### Phase 0: Docs read + structural TDD anchor test
Read the foundation docs (`docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`) and grep for any `engines.py` mention to queue Phase 4 doc updates. Author `tests/unit/strategy/interfaces/test_engines_package_layout.py` with ~6 small tests covering: package-hood (`__path__` exists), each leaf module loads, each ABC importable from the package root, leaf `__all__` matches the layout table verbatim, `engines.__all__` symmetric with `game.strategy.interfaces.__all__`, and no leftover `engines.py` module file. Run the test, confirm it fails for the right reason (`engines` is still a module, not a package).

### Phase 1: Introduce the engines package
Create `game/strategy/interfaces/engines/`. For each of the 18 ABCs, cut (do not duplicate) the class plus its TYPE_CHECKING imports verbatim into the appropriate leaf module (`movement.py`, `orders.py`, `combat.py`, `production.py`, `logistics.py`, `population.py`, `planet_ops.py`, `terraforming.py`, `components.py`). Each leaf gets `from __future__ import annotations`, a minimal TYPE_CHECKING block, and an `__all__` listing its ABCs. Author `engines/__init__.py` with explicit per-leaf imports and a sorted-by-domain `__all__` of all 18 names. **Delete** `game/strategy/interfaces/engines.py` — no parallel old path per AGENTS.md root-cause rule. Phase-0 test must be green.

### Phase 2: Align top-level interfaces aggregator
Rewrite `game/strategy/interfaces/__init__.py` to import every ABC the engines package exposes (currently misses 5: `IOrganicsConsumptionEngine`, `IHappinessEngine`, `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine`) and update its `__all__`. The layout test's symmetric-re-export assertion enforces this contract from here on.

### Phase 3: Validate consumers (no code changes expected)
Run the focused strategy-engine test surface (`tests/unit/strategy/turn_engine`, `tests/integration/strategy`, `tests/unit/strategy/interfaces`), the AST-guard test `test_no_function_local_engine_imports_in_TurnEngine_methods`, and the full sharded baseline `python Tools/test_sharded/test_sharded.py`. Zero consumer source files should require edits; if any do, stop and prove with a failing test that package-root re-exports are insufficient.

### Phase 4: Docs sync
Update any doc that refers to `interfaces/engines.py` as a single file. Likely candidates: `docs/systems/strategy_layer.md` and any `docs/architecture/*.md` page that lists the engine interface count. Skip `docs/_ignore/` per AGENTS.md.

### Phase 5: Clean review
`git status --short` to confirm the only deletion is `engines.py` and the only additions are the 9 leaf modules + `__init__.py` + the new test. Inspect each leaf module for copy/paste duplicates, orphan TYPE_CHECKING imports, and docstring fidelity. Confirm `engines/__init__.py` re-exports exactly 18 names and matches `__all__`.

## Related Documents
- [TD-09 source plan](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-09_engine_interface_split.md) — canonical specification (verification findings, file touch plan, per-phase success criteria)
- [Strategy tech-debt EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) — why TD-09 runs first in the 10-plan arc
- [design.md](design.md) — distilled architecture analysis and risk register
- [decisions.md](decisions.md) — full decisions log
- [manifest.md](manifest.md) — enumerated file touch list

## Verification
Acceptance criteria from the TD-09 plan:
- [x] `game/strategy/interfaces/engines.py` has been replaced by a package layout without changing the public symbols available to production callers.
- [x] Package-root imports continue to work for all existing consumers (30 import sites confirmed pre-split).
- [x] No concrete engine modules required logic changes just to accommodate the split.
- [x] The new structural layout test (`tests/unit/strategy/interfaces/test_engines_package_layout.py`) is present and passes.
- [x] Focused interface/import regression coverage is green before the sharded run.
- [x] `python Tools/test_sharded/test_sharded.py` is green. (20857/20857 in Phase 3.)
- [x] Docs no longer describe `engines.py` as a monolithic single file. (They never did; Phase 4 confirmed no-op.)
