# Phase 3: Typed `StatAccumulator` dataclass (10 scalar + 4 map fields = 14 total)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-367 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace `acc: Dict[str, Any]` with a `StatAccumulator` dataclass of **10 scalar fields + 4 named map fields = 14 total**. Misspelled scalar/map field access becomes `AttributeError` at runtime instead of silent zeros. Dynamic resource keys (`max_<resource>`, `gen_<resource>`) live inside `resource_storage` / `resource_generation` map fields. Golden snapshot bit-identical. Update `docs/02_PATTERNS.md` § 35 to describe the unified extension surface. Backfill PROJ-360 cross-link.

---

## Pre-flight

- [ ] Phase 2 complete and committed
- [ ] Sharded suite green at end of Phase 2
- [ ] **Field-set survey:** `grep -rn 'acc\[' game/simulation/entities/stat_contributors/ game/simulation/entities/ship_stats.py` — capture every key written or read. Confirm against the 12 keys at `ship_stats.py:235-243` plus the dynamic resource pattern at `:285-295`. Map to the 14 dataclass fields below.

---

## Authoritative field set (14 total)

```python
@dataclass
class StatAccumulator:
    # Scalar fields (10)
    thrust: float = 0.0
    strategic_movement: int = 0
    turn_speed: float = 0.0
    maneuver_points: float = 0.0
    max_shields: float = 0.0
    shield_regen: float = 0.0
    shield_cost: float = 0.0
    warp_max_tonnage: float = 0.0
    warp_energy_cost: float = 0.0
    pod_storage_mass: float = 0.0

    # Named map fields (4)
    warp_resource_costs: Dict[str, float] = field(default_factory=dict)
    cargo_storage: Dict[str, float] = field(default_factory=dict)
    resource_storage: Dict[str, float] = field(default_factory=dict)       # was acc["max_<resource>"]
    resource_generation: Dict[str, float] = field(default_factory=dict)    # was acc["gen_<resource>"]
```

---

## Tasks

### Task 3.1: Field-count and misspelled-field tests (TDD-first) [Simple]
**File:** `tests/unit/simulation/entities/stat_contributors/test_stat_accumulator.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/stat_contributors/test_stat_accumulator.py -v`

- [ ] Write a test asserting `len(dataclasses.fields(StatAccumulator)) == 14`
- [ ] Write a test enumerating the 10 scalar field names + 4 map field names; assert they match the authoritative list
- [ ] Write a test that constructs a `StatAccumulator()` and asserts `setattr(acc, "shield_regen_typo", 1.0)` raises `AttributeError` if `__slots__` is used; otherwise assert `getattr(acc, "shield_regen_typo")` raises `AttributeError`
- [ ] Test that valid scalar fields default to 0/0.0; map fields default to empty dict
- [ ] Run the tests; **confirm they fail** (the class doesn't exist yet)

**Notes:** If runtime safety on misspelled-attribute writes is desired (not just reads), use `@dataclass(slots=True)` (Python 3.10+) which makes the dataclass `__slots__`-backed. The project baseline is Python 3.13+ per CLAUDE.md, so `slots=True` is safe.

### Task 3.2: Define `StatAccumulator` dataclass [Medium]
**File:** `game/simulation/entities/stat_contributors/registry.py` OR sibling `accumulator.py` if registry.py would push the 500 LOC ceiling
**Tests:** Task 3.1's tests

- [ ] Define `@dataclass(slots=True) class StatAccumulator` with exactly the 14 fields listed above
- [ ] Default each scalar field to its zero value (0.0 for floats, 0 for ints)
- [ ] Default each map field via `field(default_factory=dict)`
- [ ] Add a docstring listing what each field represents and which contributor writes it
- [ ] Decide registry.py vs accumulator.py based on actual LOC count after Phase 2 lands; document the choice in decisions.md
- [ ] Export from `stat_contributors/__init__.py` so contributors can type-annotate
- [ ] **Verify:** Task 3.1's tests pass

**Notes:**

### Task 3.3: Migrate Phase-3 built-in `contribute_*` functions to typed accumulator [Medium]
**Files:** `game/simulation/entities/stat_contributors/{movement,defense,launch,command}.py`
**Tests:** focused unit tests + golden snapshot

- [ ] In each `contribute_X` function, change parameter type annotation from `acc: Dict[str, Any]` to `acc: StatAccumulator`
- [ ] Replace every `acc["thrust"]` etc. with `acc.thrust` (attribute access)
- [ ] Replace every `acc.get("X", 0)` with `acc.X` (no fallback needed — dataclass defaults cover it)
- [ ] Replace `acc["warp_resource_costs"]` reads/writes with `acc.warp_resource_costs` (still dict access at the value level)
- [ ] Replace `acc["cargo_storage"]` reads/writes with `acc.cargo_storage` (still dict access at the value level)
- [ ] **DO NOT touch `weapons.py`** — out-of-scope (Phase 5)
- [ ] **Verify:** focused tests pass; golden snapshot bit-identical

**Notes:**

### Task 3.4: Migrate `ship_stats.py` accumulator construction and consumption [Medium]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** golden snapshot + endurance round-trip

- [ ] Replace `acc: Dict[str, Any] = {...defaults...}` (lines 235-243) with `acc = StatAccumulator()`
- [ ] In `_aggregate_resource_abilities` (lines 274-295):
  - Replace `acc[f"max_{ability.resource_type}"] = acc.get(...) + ability.max_amount` with `acc.resource_storage[ability.resource_type] = acc.resource_storage.get(ability.resource_type, 0.0) + ability.max_amount`
  - Replace `acc[f"gen_{ability.resource_type}"] = ...` with `acc.resource_generation[...]`
  - Replace `acc["warp_resource_costs"][rt] = ...` with `acc.warp_resource_costs[rt] = ...`
- [ ] In `_aggregate_cargo_and_pod_abilities` (lines 298-319):
  - Replace `acc["cargo_storage"][cargo_type] = ...` with `acc.cargo_storage[cargo_type] = ...`
  - Replace `acc["pod_storage_mass"] += ...` with `acc.pod_storage_mass += ...`
- [ ] In `_apply_aggregated_stats` (lines 318-358):
  - Replace `acc.items()` discovery loop for resource keys with `acc.resource_storage.items()` + `acc.resource_generation.items()`
  - Replace all `acc["X"]` with `acc.X`
- [ ] **Verify:** golden snapshot bit-identical; combat endurance fields all match (verified via `calculate_combat_endurance` reading `ship.resources` after `_apply_aggregated_stats`)

**Notes:**

### Task 3.5: Update modder contributor contract documentation [Simple]
**File:** `game/simulation/entities/stat_contributors/__init__.py` and `registry.py` docstrings
**Tests:** Manual review

- [ ] Update the public-API docstring on `register_stat_contributor` to specify the new signature `(ship, comp, accumulator: StatAccumulator) -> None`
- [ ] List every accumulator field in a comment block (or link to the dataclass docstring)
- [ ] Note the runtime safety guarantee: misspelled scalar/map field names raise `AttributeError` at the modder's first test (because of `slots=True`)
- [ ] Note that resource-type strings inside `resource_storage` / `resource_generation` maps still flow through dicts; misspelled types produce zero (same as today, but the surface area is much smaller)
- [ ] **Verify:** documentation matches code

**Notes:**

### Task 3.6: Update `docs/02_PATTERNS.md` § 35 [Simple]
**File:** `docs/02_PATTERNS.md`
**Tests:** Manual review

- [ ] Section 35 currently describes the PROJ-360 registry-with-suppression pattern. Update to describe:
  - One unified registry (built-ins seeded as defaults; modders register the same way)
  - Replacement-by-default with `RegistrationConflictPolicy` for explicit alternatives
  - `RegistrationHandle` for unambiguous cleanup
  - Typed `StatAccumulator` (10 + 4 = 14 fields) as the mutation surface
  - Phase-ordering via `phase_order` field (built-ins 10–50, modder default 99)
  - Phase 5 helpers (`weapons.py`, `apply_armor_and_repair_scores`, `init_armor_pool`) remain imperative — note this as a known boundary for future work
- [ ] Update the `> **Last verified:**` blockquote to today's date
- [ ] **Verify:** doc matches code; no references to deleted `BUILTIN_HANDLED_ABILITIES`

**Notes:**

### Task 3.7: Backfill PROJ-360 cross-link [Simple]
**File:** `Projects/active_projects/PROJ-360/decisions.md`
**Tests:** Manual review

- [ ] In the Audit Remediation table, mark EXT-07, EXT-11, EXT-13 as **resolved by PROJ-367 commit `<sha>`**
- [ ] **Verify:** PROJ-360 decisions.md still parses cleanly

**Notes:**

### Task 3.8: Full sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; pass count grows with new tests; zero regressions
- [ ] **Acceptance:** golden snapshot bit-identical; misspelled-field test passes; combat endurance fields all match; PROJ-360 cross-link renders correctly

**Notes:**

### Task 3.9: Commit Phase 3 [Simple]

- [ ] `git add` only files in this phase's scope
- [ ] Commit message: `refactor(PROJ-367): Phase 3 — typed StatAccumulator dataclass + unified extension surface`
- [ ] Sign-off: `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`
- [ ] Do NOT push
- [ ] **Verify:** working tree only contains in-scope files

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Zero `acc[...]` (dict-syntax) reads in `stat_contributors/` and `ship_stats.py:_phase_stats_aggregation`/`_aggregate_*` paths
- [ ] `StatAccumulator` is a dataclass with exactly 14 fields (verified via `dataclasses.fields()`)
- [ ] Misspelled-field test passes (proves runtime safety via `slots=True`)
- [ ] Dynamic resource keys live inside `resource_storage` / `resource_generation` maps (no `max_<R>` / `gen_<R>` synthetic keys at the top level)
- [ ] Combat endurance verified via `ship.resources` round-trip
- [ ] Golden snapshot bit-identical
- [ ] `docs/02_PATTERNS.md` § 35 reflects unified extension surface
- [ ] PROJ-360 cross-link backfilled (EXT-07/EXT-11/EXT-13 marked resolved)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate ready for audit
