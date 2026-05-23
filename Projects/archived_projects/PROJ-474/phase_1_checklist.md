# Phase 1: Codify the UI-safe surface as machine-checkable data

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-474 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the comment-only `UISAFE` category in
`tests/static_guards/test_facade_read_path_imports_guard.py` with a
machine-checkable `_UISAFE_SYMBOLS` data structure; add a doc↔guard parity test
and a no-misfile invariant; reconcile the three known drifts; promote the 12
detached value/config/enum/static-metadata symbols out of `TAIL`; delete the
annotation-only `EmpireEconomySnapshot` runtime import. STOP before any
live-reader or tooling migration (PROJ-475/476).

**TDD note:** every code task writes/identifies the failing test FIRST, runs it
red, then implements. Targeted run:
`pytest tests/static_guards/test_facade_read_path_imports_guard.py -q`.

---

## Tasks

### Task 1.1: Add the no-misfile invariant test (RED first) [Medium]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py -k no_misfile -q`

- [x] Add `_UISAFE_SYMBOLS: frozenset[tuple[str, str]]` (empty/stub at first) so the test can reference it.
- [x] Write `test_uisafe_symbols_not_also_in_transitional_allowlist`: asserts no `(module, member)` in `_UISAFE_SYMBOLS` appears as the `(module, member)` PROJECTION of **any** triple in `_IMPORT_ALLOWLIST` (the whole file-scoped transitional set, not just the TAIL section — so a symbol cannot be simultaneously UISAFE and transitional anywhere). Per post-flesh review §5.4.
- [x] Verify: test exists and is referenced; run to confirm it executes (it passes vacuously while `_UISAFE_SYMBOLS` is empty — the meaningful RED is exercised in Task 1.4).

**Notes:**

---

### Task 1.2: Add `_UISAFE_SYMBOLS` data + matcher branch + reconcile drift [Medium]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py -q`

- [x] Populate `_UISAFE_SYMBOLS` with the existing UISAFE-block symbols (de-duplicated to `(module, member)`): `game_config` scalars (`DEFAULT_SYSTEM_COUNT`, `GameConfig`, `PlayerConfig`, `THEME_DEFAULTS`, `MAX_SYSTEM_COUNT`, `MIN_SYSTEM_COUNT`, `VALID_GALAXY_TYPES`); `EnvironmentalPreference`; `habitability_factors.iter_gas_factors`/`iter_scalar_factors`; `homeworld_presets.*` (4 loaders); `RacePointBudget`; `race_config` label tuples (`GOVERNMENT_ORGANIZATIONS`/`GOVERNMENT_TYPES`/`LEADER_TITLES`/`PHYSICAL_TYPES`/`SOCIETY_TYPES`); `ContainableKind`; `ActivationPhase`; `ComponentActivationState`.
- [x] Add matcher branch in `_violations_in_file` (and the bare-`import` path): allow when `(module, member) ∈ _UISAFE_SYMBOLS`, before falling through to the exact triple check (`...imports_guard.py:285`,`:308-309`).
- [x] Remove the now-redundant UISAFE-block triples from `_IMPORT_ALLOWLIST` (`:67-105`) — they are covered by `_UISAFE_SYMBOLS`. Keep the section comment pointing to `_UISAFE_SYMBOLS`.
- [x] Reconcile `ComponentActivationState`: it is now in `_UISAFE_SYMBOLS` (was a TAIL-adjacent UISAFE-block entry); confirm it is no longer a triple.
- [x] Verify: `test_no_unallowlisted_strategy_imports_in_ui` still green for every UI file; `test_import_classifier_positive_controls` + `test_matcher_*` still green.

**Notes:**

---

### Task 1.3: Add the doc↔guard parity test + Pattern #5 token block (RED first) [Medium]
**Files:** `tests/static_guards/test_facade_read_path_imports_guard.py`, `docs/02_PATTERNS.md`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py -k parity -q`

- [x] Write `test_uisafe_symbols_match_pattern5_token_list`: parse a fenced canonical block in `docs/02_PATTERNS.md` (one `module.member` token per line, a dedicated fenced section under Pattern #5 read-path policy) and assert the parsed set equals `_UISAFE_SYMBOLS`. Run RED first (block absent).
- [x] Add the fenced canonical token block to Pattern #5 listing every `_UISAFE_SYMBOLS` entry as `module.member`, with a one-line note that this block is the parity source of truth.
- [x] Update the Pattern #5 prose UI-safe list to add `ComponentActivationState` (was missing) so prose + token block agree.
- [x] Verify: parity test green; `docs/` and code agree (CLAUDE.md "keep code and docs consistent").

**Notes:**

---

### Task 1.4: Promote the 12 misfiled TAIL symbols [Medium]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py -q`

- [x] **TDD RED step for the no-misfile invariant (post-flesh review §4.2/§4.3):** add ONE known-duplicated symbol (e.g. `race_config.RaceConfig`) to `_UISAFE_SYMBOLS` WITHOUT yet removing its TAIL triple; run `pytest tests/static_guards/test_facade_read_path_imports_guard.py -k no_misfile -q` and confirm it goes RED. This proves the Task 1.1 invariant is not vacuous. Do this in the working tree before the deletion below — do NOT commit the RED intermediate state.
- [x] Add to `_UISAFE_SYMBOLS` (and the Pattern #5 token block + prose): `game_config.VALID_GALAXY_TYPES` (already added 1.2 — confirm the `galaxy_test` TAIL entry is now removed), `race_config.RaceConfig`, `race_point_budget.RacePointBudget` (confirm both TAIL sites removed), `order_types.OrderType`, `planet.PlanetType`, `fleet_hierarchy.BattleRole`, `fleet_hierarchy.CombatPolicy`, `economy_config.get_default_economy_config`, `race_description_llm_controller.FieldStatus`, `ability_metadata.StrategicKind`, `ability_metadata.abilities_with_kind_tag`, `superweapon_registry.SUPERWEAPONS`.
- [x] Delete the corresponding TAIL triples from `_IMPORT_ALLOWLIST` (the per-file entries for each symbol/site listed in design.md §"Promote to UISAFE"). Leave all OTHER imports from the same modules/files in TAIL (e.g. `RaceLibrary`, `RaceRandomizer`, `Galaxy`, `Planet`, `DesignCatalog`).
- [x] Verify no-misfile (1.1) goes back to GREEN after the triples are deleted, parity (1.3) stays green; full guard module green.

**Notes:**

---

### Task 1.5: Delete the annotation-only `EmpireEconomySnapshot` runtime import [Simple]
**File:** `game/ui/panels/empire_treasury_panel.py`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py -q` + `pytest tests/ -k treasury --testmon`

- [x] Confirm `EmpireEconomySnapshot` is used only in annotations (`:65`, `:301`, `:306`).
- [x] Ensure `from __future__ import annotations` is present (add if missing); move the import (`:33`) into an `if TYPE_CHECKING:` block.
- [x] Remove the `EmpireEconomySnapshot` triple from `_IMPORT_ALLOWLIST` (`...imports_guard.py:120`).
- [x] Verify: guard green (the import is now TYPE_CHECKING-only → ignored), treasury panel tests green, module still imports.

**Notes:**

---

### Task 1.6: Positive-control for the symbol-level matcher [Simple]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py -k positive -q`

- [x] Extend/author a positive control proving: a UISAFE `(module, member)` from a SYNTHETIC (not-allowlisted) file is allowed via `_UISAFE_SYMBOLS`, but a DIFFERENT (live) member of the SAME module is still flagged — pins that the structure is symbol-level, not module-level. Use `race_description_llm_controller`: `FieldStatus` allowed, `RaceDescriptionLLMController` flagged.
- [x] Verify: control green and would fail if `_UISAFE_SYMBOLS` were widened to a module prefix.

**Notes:**

---

### Task 1.7: Final validation [Simple]
**Tests:** sharded suite / targeted

- [x] `pytest tests/static_guards/ -q` green (all guards, all positive controls, parity + no-misfile).
- [x] `pytest tests/ -k "treasury or new_game_setup or race_setup or galaxy_test or builder or transfer or planet_abilities or orders_window or battle_setup" --testmon` green (affected UI imports resolve).
- [x] `python Tools/test_sharded/test_sharded.py` green (or note scope-limited run).
- [x] Confirm Pattern #5 prose + token block + `_UISAFE_SYMBOLS` are mutually consistent.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to user verification
