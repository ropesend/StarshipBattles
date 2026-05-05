# Phase 3: Decompose `_aggregate`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-362 3`
> 2. Only proceed if PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Split `_aggregate` (~150 LOC, CC 47) into four named functions: `collect_providers`, `aggregate_status`, `aggregate_value`, `format_rows`. Behavior identical; functions are unit-testable in isolation.

---

## Tasks

### Task 3.1: Extract `collect_providers` [Medium]
**File:** `game/strategy/services/system_effects_collector.py`
**Tests:** `pytest tests/unit/strategy/services/test_system_effects_collector*.py -v`

- [x] Create new internal function `_collect_providers(sources, allowed_scopes, empire_id, hex_coord, registries) -> dict[str, dict]`:
  - Walks every source.
  - Applies owner filter, hex filter, get_abilities() error tolerance, scope filter, ownership-aware-scope rejection.
  - Builds `raw_providers[group_key] = {'ability_name', 'display_name', 'resource_type', 'damage_type', 'kind', 'providers': [...]}`.
  - Returns `raw_providers`.
- [x] In `_aggregate`, call `_collect_providers` and use the returned dict to drive the rest.
- [x] Run all tests (Phase 1 characterization + existing). Green.

**Notes:** _(filled during implementation)_

### Task 3.2: Extract `aggregate_status` [Simple]
**File:** Same

- [x] Pull the status-rollup logic (lines 400-416) into `_aggregate_status(providers: list[dict]) -> str` returning one of "Active", "Activating (N)", "Deactivating", "Inactive".
- [x] Call from `_aggregate` per group.
- [x] Add direct unit tests:
  - all-active → "Active"
  - mixed active/activating/deactivating → "Active"
  - only-activating → first "Activating (N)" string
  - only-deactivating → "Deactivating"
  - all-inactive → "Inactive"
- [x] All tests green.

**Notes:** _(filled during implementation)_

### Task 3.3: Extract `aggregate_value` [Medium]
**File:** Same

- [x] Pull value-aggregation logic (currently mixed-kind validation + active/inactive entries selection + kind-specific aggregation) into `_aggregate_value(providers: list[dict], kind: str, group_key: str) -> float`.
- [x] Keep the PROJ-300 D16 mixed-kind validation logging inside this function.
- [x] Add direct unit tests for: rate aggregation (sum), multiplier aggregation (intra-group MAX, inter-group MULTIPLY), inactive-only fallback to would-be value, mixed-kind warning + entry skip.
- [x] All tests green.

**Notes:** _(filled during implementation)_

### Task 3.4: Extract `format_rows` [Simple]
**File:** Same

- [x] Pull final-row construction into `_format_rows(raw_providers: dict, status_per_group: dict, value_per_group: dict) -> list[dict]` producing the public return shape (preserving `_legacy_provider_fields` keys for now — Phase 4 retires those).
- [x] Call from `_aggregate`.

**Notes:** _(filled during implementation)_

### Task 3.5: Verify `_aggregate` is now a 5-line orchestrator [Simple]
**File:** Same

- [x] `_aggregate` body should now be:
  ```python
  raw_providers = _collect_providers(sources, allowed_scopes, empire_id, hex_coord, registries)
  status_per_group = {k: _aggregate_status(v['providers']) for k, v in raw_providers.items()}
  value_per_group = {k: _aggregate_value(v['providers'], v['kind'], k) for k, v in raw_providers.items()}
  return _format_rows(raw_providers, status_per_group, value_per_group)
  ```
- [x] Run `python -m radon cc game/strategy/services/system_effects_collector.py -s` — `_aggregate` CC should drop from 47 to <10.
- [x] Run full focused suite: green.
- [x] UI smoke test: open System Tree panel and Planet List; effect rows render identically.

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
- [x] All tasks checked
- [x] `_aggregate` now < 20 LOC, CC < 10
- [x] Each helper function has direct unit tests
- [x] All Phase 1 characterization tests still green
- [x] UI rendering visually unchanged
- [x] Update plan.md phase table to `Complete`
- [x] Update Current State: PROJ-362 ready for user verification (Phase 4 deferred)
