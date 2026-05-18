# PROJ-446 Phase 2: Static-guard backfill + protocol surface narrowing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-446 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** Phase 1 complete (recommended; not strictly required — Phase 2 is independent)
**Objective:** Backfill two missing static guards that previous retirement projects (PROJ-434 / PROJ-435) didn't include in their guard set. Narrow `IShipInstance.cargo_contents` and document `IFacility.consumable_levels` as intentional-inconsistency. Mechanical sweep of pre-PEP-604 annotation syntax across the 7 protocol modules.

**Cross-bucket file-ownership rule:** Edit `tests/static_guards/`, `game/core/protocols/`, and UI/test files. **Do NOT touch the concrete `ShipInstance` setter at `game/strategy/data/ship_instance.py`** — that's PROJ-444's territory; the protocol annotation narrowing here is a no-op until PROJ-444 Phase 3 retires the concrete setter.

**Source-of-truth findings:** [`findings/bucket_c_ui_core_tests_scan.md`](findings/bucket_c_ui_core_tests_scan.md) — F-C-013, F-C-014, F-C-018, F-C-019, F-C-030.

---

## Tasks

### Task 2.1: F-C-018 — DesignLibrary re-emergence static guard [Simple]
**File (new):** `tests/static_guards/test_no_design_library_class.py`
**Tests:** `pytest tests/static_guards/test_no_design_library_class.py -v`

- [ ] Read existing guard pattern in `tests/static_guards/test_no_carried_items_proxy.py` (or another existing guard — match the AST-scan or attribute-check pattern)
- [ ] **GREEN**: Create the new guard. Two assertions:
  - `assert not hasattr(game.strategy.systems.design_catalog, "DesignLibrary")` — runtime attribute check
  - AST scan of `game/strategy/systems/` (and possibly `game/simulation/services/`) for `class DesignLibrary` definitions; assert zero hits
- [ ] **RED-check**: Temporarily add a stub `class DesignLibrary: pass` somewhere in `game/strategy/systems/`; confirm the guard fails. Revert.
- [ ] Run the guard; it passes (the class is truly gone).

### Task 2.2: F-C-019 — _ACTIVATABLE_ABILITIES re-emergence static guard [Simple]
**File (new):** `tests/static_guards/test_no_activatable_abilities_constant.py`
**Tests:** `pytest tests/static_guards/test_no_activatable_abilities_constant.py -v`

- [ ] Read existing guard `tests/static_guards/test_no_resource_types_constant.py` for the canonical AST-scan pattern
- [ ] **GREEN**: Create the new guard. AST-scan `game/ui/screens/builder/stat_rows_dynamic.py` (and the broader `game/ui/screens/builder/` package for safety) for any `_ACTIVATABLE_ABILITIES = ...` assignment node. Assert zero hits.
- [ ] **RED-check**: Temporarily add `_ACTIVATABLE_ABILITIES = []` to stat_rows_dynamic.py; confirm the guard fails. Revert.
- [ ] Run the guard; it passes.

### Task 2.3: F-C-014 — Narrow IShipInstance.cargo_contents to Mapping [Simple]
**File:** `game/core/protocols/strategy_domain.py:188`
**Tests:** `pytest tests/static_guards/ tests/unit/core/ -v`

- [ ] Read the existing protocol member declaration at strategy_domain.py:188 — currently `cargo_contents: Dict[str, int]` with the "**not** read-only in absolute terms" caveat in the docstring
- [ ] **GREEN**: Change the annotation to `Mapping[str, int]`. Add the `Mapping` import from `typing` (or just `collections.abc.Mapping` if PEP-604 modern is preferred).
- [ ] **DO NOT delete the docstring caveat in this phase** — the concrete-class setter at `game/strategy/data/ship_instance.py` still exists (it's part of the `_ship_instance_init_with_legacy_kwargs` wrapper). PROJ-444 Phase 3 retires that wrapper; after that lands, PROJ-444's Phase 3 Task 3.5 will update this docstring to drop the caveat.
- [ ] Run the static guard suite to confirm no breakage.
- [ ] Run `pytest tests/static_guards/test_no_legacy_protocol_names.py` — should still pass (the existing guard pins the surface).

### Task 2.4: F-C-013 — Document IFacility.consumable_levels intentional-inconsistency [Simple]
**File:** `game/core/protocols/strategy_domain.py:144`
**Tests:** Same static-guard suite.

- [ ] Read the existing `IFacility.consumable_levels` protocol member at strategy_domain.py:144
- [ ] Read the existing static guard `test_ifacility_still_declares_consumable_levels` (in `tests/static_guards/test_no_legacy_protocol_names.py` or similar) — confirms this is a deliberate "stay-as-is" decision
- [ ] **GREEN — docstring update**: Add a docstring on the `consumable_levels` protocol member declaring the intentional inconsistency. Cite the PROJ-436 Phase 0 D1 decision (deferred fold-in until a transfer-UI use case emerges). Mention the existing static guard.
- [ ] No code structural change — this is a documentation-only edit on the protocol surface.

### Task 2.5: F-C-030 — Modern type syntax sweep across protocol modules [Medium]
**Files:** `game/core/protocols/strategy_domain.py:8`, `strategy_entities.py:8`, `boundary.py:7`, `combat.py:3`, `persistence.py:3`, `common.py:14`, `registry.py:3` (7 modules total)
**Tests:** `pytest tests/static_guards/ tests/unit/core/protocols/ -v`

- [ ] For each protocol module, mechanically rewrite:
  - `from typing import Dict, List, Optional, FrozenSet, Tuple` → drop these imports (keep only `Protocol`, `runtime_checkable`, etc. that are still needed)
  - `Dict[K, V]` → `dict[K, V]`
  - `List[X]` → `list[X]`
  - `Optional[X]` → `X | None`
  - `FrozenSet[X]` → `frozenset[X]`
  - `Tuple[A, B]` → `tuple[A, B]`
  - `Set[X]` → `set[X]`
- [ ] Add `from __future__ import annotations` at the top of each file if not already present (Python 3.13 baseline allows PEP-604 without it, but `from __future__` keeps forward references string-compatible)
- [ ] Run the protocol test suite + static guards after each file to catch import breakages.
- [ ] Coordinate with PROJ-447 Phase 3 (the parallel sweep across `research/`, `assets/`, `engine/`, `simulation/` loaders). Same recipe; different files. Sequence either-first.

---

## Phase Completion Checklist

- [ ] DesignLibrary + `_ACTIVATABLE_ABILITIES` static guards in place and green
- [ ] `IShipInstance.cargo_contents` narrowed to `Mapping[str, int]`
- [ ] `IFacility.consumable_levels` intentional-inconsistency documented in protocol docstring
- [ ] All 7 protocol modules use modern PEP-604 type syntax
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-446 2` — PASSED
- [ ] Update status to `Complete`; plan.md phase table + Current State → Phase 3
- [ ] No new entries in `discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries

## Coordination Touchpoints

- **PROJ-444 Phase 3 (wrapper retirement)**: Task 2.3's docstring caveat retirement is sequenced into PROJ-444 Phase 3 Task 3.5. Don't try to delete it here — the concrete-class setter still exists.
- **PROJ-447 Phase 3 (annotation sweep)**: Same recipe as Task 2.5 but on different files. No conflict; either project can ship first.

## Notes

- Pure mechanical phase. No behavior changes. Static guards are AST-scan tests; protocol annotation changes are type-only (no runtime effect).
- If the AST scan in Task 2.1 or Task 2.2 needs a helper utility, write it as a module-level test util that other static guards can reuse.
