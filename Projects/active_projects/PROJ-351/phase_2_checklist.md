# Phase 2: T6.4 — PlanetAbilitiesController hardcoded list → registry scan

**Status:** Not Started
**Objective:** Replace hardcoded ability-name lists in `planet_abilities_controller.py:29-48` with a registry/data scan pattern per `docs/03_CONVENTIONS.md:500-512`.

---

## Tasks

### Task 2.1: Read hardcoded lists + identify the registry [Medium]
**File:** `game/ui/screens/planet_abilities_controller.py:29-48` (read-only)
**Reference:** `docs/03_CONVENTIONS.md:500-512`

- [ ] Read lines 29-48 to enumerate the hardcoded lists. Document what each list categorizes (offensive vs. defensive abilities, displayable vs. internal, etc.).
- [ ] Read the convention doc at `docs/03_CONVENTIONS.md:500-512` for the canonical registry-scan idiom.
- [ ] Find the right registry: `git grep -n "ability_registry\|AbilityRegistry\|abilities/__init__" game/`. Most ability metadata lives at `game/simulation/components/abilities/`.
- [ ] Determine how to filter abilities into the categories the hardcoded lists encode. The metadata likely supports this via `category`, `tags`, or `scope` attributes.
- [ ] If the metadata DOES NOT carry the category info: extending the registry is in scope; document the addition in [decisions.md](decisions.md).

**Notes:**

### Task 2.2: Find tests pinning the hardcoded lists [Simple]
**File:** locate via grep

- [ ] `git grep -nE "test_.*planet_abilities|planet_abilities_controller" tests/`
- [ ] Read each test that asserts a specific ability name appears in a category.
- [ ] Decide for each: rewrite to assert "registry-driven category yields these abilities" or delete with rationale.

**Notes:**

### Task 2.3: Refactor controller to registry scan [Medium]
**File:** `game/ui/screens/planet_abilities_controller.py:29-48`
**Tests:** `pytest tests/unit/ui/screens/test_planet_abilities_controller* -x`

- [ ] Replace each hardcoded list with a `registry.iter_abilities()` (or equivalent) call filtered by the category attribute.
- [ ] Preserve presentation labels via metadata where available; if metadata doesn't carry display labels, use a small presentation-only mapping (kept minimal and clearly labeled as presentation-only).
- [ ] Run targeted tests.

**Notes:**

### Task 2.4: Targeted slice + commit [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_planet_abilities_controller* -x -q`

- [ ] All pass.
- [ ] Commit: `refactor(planet-abilities-controller): replace hardcoded ability lists with registry scan (PROJ-351 T6.4)`

**Notes:**

### Task 2.5: Final verification + index update
**Tests:** `pytest tests/unit/ -q -p no:cacheprovider`

- [ ] Full unit suite green.
- [ ] `python Tools/lint_test_files.py` — 0 violations.
- [ ] Update `Projects/projects_index.md` PROJ-351 → `Awaiting Verification`. Commit: `chore(PROJ-351): mark closeout follow-up awaiting verification`.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] T6.4 commit + chore commit landed
- [ ] plan.md phase table → `Complete`
- [ ] Surface to user
