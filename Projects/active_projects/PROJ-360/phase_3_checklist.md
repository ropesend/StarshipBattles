# Phase 3: Replace Hardcoded Ability-Name Checks with Registered Contributors

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-360 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):** game/simulation/entities/stat_contributors/*.py, game/simulation/combat/ability_stat_registry.py, tests/unit/simulation/entities/test_stat_contributor_extension.py
**Objective:** Replace remaining hardcoded ability-class string checks (still inside the contributors after Phase 2) with registered metadata. Lock the extension point with an executable acceptance test.

---

## Tasks

### Task 3.1: Inventory remaining string checks [Simple]
**File:** Read-only audit
**Tests:** None

- [ ] Grep `has_ability('` and `has_ability("` inside `stat_contributors/`
- [ ] List every match in [decisions.md](decisions.md). For each: which contributor, which ability class name, what stat it affects

**Notes:**

---

### Task 3.2: Extend `ABILITY_STAT_REGISTRY` (or sibling) for stat-domain bindings [Medium]
**File:** `game/simulation/combat/ability_stat_registry.py` (extend) OR new sibling registry
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py tests/unit/simulation/entities/ -v`

- [ ] Decide: extend the existing registry OR create a sibling one for stat-domain contributors. Document the choice in [decisions.md](decisions.md). Default: extend, since the data shape overlaps
- [ ] Each ability class that contributes a hardcoded stat gets a registry entry with: ability class name, target stat, contributor domain, value field, operation (add/multiply)
- [ ] Existing registry tests still pass

**Notes:**

---

### Task 3.3: Replace string checks in each contributor [Medium]
**File:** `game/simulation/entities/stat_contributors/*.py`
**Tests:** `pytest tests/unit/simulation/entities/ -v`

- [ ] Movement: replace ability-class lookups with registry consultation
- [ ] Defense: same
- [ ] Weapons: same
- [ ] Command: same
- [ ] Launch: same
- [ ] Golden tests STILL PASS bit-for-bit at each step

**Notes:**

---

### Task 3.4: Acceptance test — fake contributor extension [Medium]
**File:** `tests/unit/simulation/entities/test_stat_contributor_extension.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/test_stat_contributor_extension.py -v`

- [ ] Define a `FakeStatDomain` contributor in the test
- [ ] Register it; add a fake ability class to the registry
- [ ] Build a Ship with a component carrying that fake ability
- [ ] Assert `calculate()` produces the contributor's expected stat WITHOUT editing any other contributor or `ship_stats.py`
- [ ] This is the extensibility goal — codified

**Notes:**

---

### Task 3.5: Document the pattern [Simple]
**File:** `docs/02_PATTERNS.md`, `docs/systems/combat_simulation.md` (or `docs/systems/ship_stats.md` if a dedicated doc fits)
**Tests:** None

- [ ] Add the "Stat Contributor Registry" pattern entry mirroring the Ability-Stat Registry entry
- [ ] Document how to add a new stat contributor (one ADR-style step list)
- [ ] Per AGENTS.md, docs update lands in the same change

**Notes:**

---

### Task 3.6: Final sharded sweep [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite passes
- [ ] Pass count >= Phase 1 baseline + all new tests across Phases 2-3
- [ ] `ship_stats.py` confirmed under 500 LOC
- [ ] Document final state in [decisions.md](decisions.md)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to closure / awaiting user verification
- [ ] Update [manifest.md](manifest.md) with the final file set touched
