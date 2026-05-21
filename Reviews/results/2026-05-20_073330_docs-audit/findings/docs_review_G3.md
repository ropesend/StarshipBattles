# Documentation Review: Guide Docs (G3)
## Summary
- Group: Guide Docs (G3)
- Docs in Scope: 9
- Docs Actually Read: 9
- Total Findings: 17
- Critical: 4 | Major: 7 | Minor: 6

## Dead Reference Findings

### CRITICAL — Dead Core System Files

| Doc | Line | Dead Reference | Notes |
|-----|------|---------------|-------|
| `adding_abilities.md` | 55 | `game/strategy/services/component_inspector.py` | Canonical strategy/facility ability inspection path. Split by PROJ-433 into `component_abilities.py` (exists) and `component_layers.py` (exists), but the legacy re-export shim no longer exists. |
| `component_system.md` | 23 | `game/strategy/services/component_inspector.py` | Same file — listed in "Primary code" section. |
| `qs_complex_design.md` | 32 | `game/strategy/services/component_inspector.py` | Same file — listed in "Source Files" table. |
| `adding_abilities.md` | 495 | `game/strategy/services/effect_ability_metadata.py` | Doc describes this as "now a shim derived from the unified registry" but the file no longer exists. Replacement `ability_metadata.py` exists. |
| `qs_complex_design.md` | 212 | `game/simulation/components/abilities/planetary.py` | Module has been split into `planetary/` package (terraforming.py, stat_modifiers.py, stabilizers.py, shields.py, resource_modifiers.py, environmental.py). VERIFIED: `planetary.py` does not exist; `planetary/` package does. |

### MAJOR — Dead Test File References

| Doc | Line | Dead Reference | Notes |
|-----|------|---------------|-------|
| `adding_abilities.md` | 434 | `tests/unit/strategy/services/test_effect_ability_metadata.py` | Referenced in "Useful tests" section. |
| `adding_abilities.md` | 539 | `tests/unit/strategy/services/test_effect_ability_metadata.py` | Referenced in targeted test command. |
| `component_system.md` | 347 | `tests/unit/strategy/test_component_inspector.py` | Referenced in "Useful Tests And Commands". |
| `qs_complex_design.md` | 319 | `tests/unit/strategy/test_component_inspector.py` | Referenced in targeted test commands table. |
| `testing_infrastructure.md` | 170 | `tests/unit/simulation/test_damage.py` | Command example `pytest tests/unit/simulation/test_damage.py -n 0` references non-existent file. VERIFIED: file does not exist. |

### MINOR — Placeholders, Intentional Warnings, and False Positives

| Doc | Line | Reference | Notes |
|-----|------|-----------|-------|
| `performance_profiling.md` | 35, 42, 51 | `tests/path/to/test.py` | Intentional template placeholders in CLI command examples — users fill in their own path. Not harmful but flagged by scanner. |
| `testing_infrastructure.md` | 40 | `tests/integration/conftest.py` | Doc explicitly states "There is no top-level `tests/integration/conftest.py`" — this is an intentional dead-path warning. |
| `testing_infrastructure.md` | 144 | `tests/simulation/` | Doc explicitly says "Stale path to avoid: there is no top-level `tests/simulation/`" — intentional. |
| `testing_infrastructure.md` | 304 | `data/assets/test/` | Scanner false positive: the Key Files table describes `tests/fixtures/paths.py` as providing "repo/data/assets/test/combat-lab path helpers" — a descriptive list of helper categories, not a file path. |
| `simulation_testing.md` | 43, 231, 241, 629 | `data/scenario_roles.json` | Scanner false positives: the doc correctly writes `combat_lab/data/scenario_roles.json`. The scanner extracted the `data/` substring. VERIFIED: `combat_lab/data/scenario_roles.json` exists. |
| `simulation_testing.md` | 44, 277, 593 | `data/ships/` | Scanner false positives: the doc correctly writes `combat_lab/data/ships/`. VERIFIED: `combat_lab/data/ships/Test_Target.json` and many other ship files exist. |

## Stale PROJ Reference Findings

| Doc | Line | PROJ | Status | Severity | Notes |
|-----|------|------|--------|----------|-------|
| `adding_abilities.md` | 416 | PROJ-429 | "Strategy tech-debt #08/10: Ability metadata unification (TD-07)" | MINOR | Status is known and current — still active tech debt. Not stale, just in-progress. |
| `component_system.md` | 133 | PROJ-433 | "Strategy tech-debt follow-up: component_inspector split (PROJ-425 consult)" | MINOR | Status known — explains the component_inspector split referenced by CRITICAL finding above. |
| `performance_profiling.md` | 3, 7, 9 | PROJ-411 | **unknown** | MAJOR | Referenced 4 times as a historical lesson/case study about cProfile self-time attribution and the `StarshipUIAppearanceTheme` workaround. The project index has no current status for PROJ-411, making it unverifiable whether the lesson's conclusions still hold. |
| `testing_infrastructure.md` | 3, 197 | PROJ-443 | "Pytest norecursedirs Fix and Hidden-Test Triage" | MINOR | Status known and current. The doc was verified 2026-05-17 and accurately describes the PROJ-443 `norecursedirs` config flip. |

## Content Accuracy Findings

### CRITICAL

**C1. `component_inspector.py` taught as canonical import path but does not exist** — Three G3 docs (`adding_abilities.md:55`, `component_system.md:23`, `qs_complex_design.md:32`) reference `game/strategy/services/component_inspector.py` as the canonical strategy/facility ability inspection path. `component_system.md:130-133` explains it was split by PROJ-433 into `component_abilities.py` and `component_layers.py`, and says "Both are re-exported by the legacy `component_inspector` import path." But the file no longer exists — neither as a re-export shim nor otherwise. All example code snippets using `from game.strategy.services.component_inspector import ...` will fail. Docs should be updated to reference `component_abilities.py` and `component_layers.py` directly.

### MAJOR

**M1. `effect_ability_metadata.py` described as existing shim but is dead** — `adding_abilities.md:422` says "The legacy `EFFECT_ABILITY_METADATA` tuple in `effect_ability_metadata.py` is now a shim derived from the unified registry — adding new entries there directly is not the supported path." This implies the shim still exists. The file does not exist at all. The File Map at line 495 also lists it. Should be removed from the File Map and the shim description updated to reflect complete removal.

**M2. PROJ-411 status unknown (4 references)** — `performance_profiling.md` cites PROJ-411 as evidence for its cProfile self-time attribution lesson and the `StarshipUIAppearanceTheme` workaround. The project index has no current status for PROJ-411 (marked `unknown`). While the doc itself was verified 2026-05-12, the backing project's state is unverifiable.

**M3. `pre_commit_hooks.md` missing "Last verified" date** — Per `docs/03_CONVENTIONS.md` (Documentation Freshness convention), every doc should carry a `> **Last verified:** YYYY-MM-DD` blockquote below the H1. All 8 other G3 docs have this; `pre_commit_hooks.md` is the only one missing it. Without a verification date, the doc's freshness cannot be audited.

**M4. `newdocs/02_PATTERNS.md` dead cross-reference** — `testing_infrastructure.md:129` references `newdocs/02_PATTERNS.md` ("UI construction seams documented in `newdocs/02_PATTERNS.md`"). VERIFIED: `newdocs/` directory does not exist. Should be `docs/02_PATTERNS.md`.

**M5. `planetary.py` module path stale in `qs_complex_design.md`** — `qs_complex_design.md:212` says "See `game/simulation/components/abilities/planetary.py`". VERIFIED: `planetary.py` does not exist; the module has been split into a `planetary/` package. The reference should point to the `planetary/` package or its `__init__.py`.

**M6. `test_damage.py` command example references non-existent file** — `testing_infrastructure.md:170` gives the command `pytest tests/unit/simulation/test_damage.py -n 0` as an example of a targeted single-threaded test. VERIFIED: `tests/unit/simulation/test_damage.py` does not exist.

### MINOR

**M7. Python version mismatch** — `simulation_testing.md:614` says "Python 3.13+ project baseline" but AGENTS.md (canonical conventions) specifies "Python 3.14". While 3.14 satisfies 3.13+, the documented baseline should match the authoritative source.

**M8. Template placeholder paths in `performance_profiling.md`** — Three command examples (lines 35, 42, 51) use `tests/path/to/test.py` as fill-in-the-blank placeholders. These are clearly intentional templates and not harmful, but they do trigger the dead-reference scanner. No fix needed unless the team wants to adopt a distinct placeholder convention (e.g. `<your-test-path>`).

**M9. `testing_infrastructure.md:304` scanner false positive** — `data/assets/test/` is not a file reference but part of a descriptive phrase in a table. No fix needed.

**M10. `simulation_testing.md` combat_lab path scanner false positives** — 7 dead refs from the scanner (4 for `data/scenario_roles.json`, 3 for `data/ships/`) are all false positives produced by the scanner extracting `data/` substrings from `combat_lab/data/` paths. VERIFIED: all actual `combat_lab/data/` paths exist. No fix needed.

## Code Example Issues

No code example syntax errors detected. However, example code snippets in `adding_abilities.md` and `component_system.md` that import from `game.strategy.services.component_inspector` will fail at runtime since that module no longer exists (see CRITICAL finding C1).

## Missing Documentation

No major subsystems referenced by these 9 guide docs are missing from the docs inventory. However:

- The `pre_commit_hooks.md` guide lists itself as needing CI sync updates (`tests/unit/tools/test_lint_test_files.py`) — this test file exists, but the doc's own stale reference note is from an earlier verification cycle.
- `testing_infrastructure.md:170` references `tests/unit/simulation/test_damage.py` — whatever damage test replaced it (if any) should be documented in that command example.

## Doc File Coverage Verification

| Doc File | Status | Findings |
|----------|--------|----------|
| `adding_abilities.md` | NEEDS UPDATE | 1 CRITICAL (C1: component_inspector dead), 1 CRITICAL (dead effect_ability_metadata.py reference), 1 MAJOR (dead test file ×2 lines), 1 MINOR (PROJ-429 in-progress) |
| `adding_modifiers.md` | CURRENT | No findings. Well-maintained with no dead refs. |
| `component_system.md` | NEEDS UPDATE | 1 CRITICAL (C1: component_inspector dead), 1 MAJOR (dead test file), 1 MINOR (PROJ-433 in-progress) |
| `modifier_system.md` | CURRENT | No findings. Well-maintained with no dead refs. |
| `performance_profiling.md` | NEEDS UPDATE | 1 MAJOR (PROJ-411 unknown status ×4 refs), 1 MINOR (placeholder paths ×3) |
| `pre_commit_hooks.md` | NEEDS MINOR FIX | 1 MAJOR (missing "Last verified" date) |
| `qs_complex_design.md` | NEEDS UPDATE | 1 CRITICAL (C1: component_inspector dead), 1 MAJOR (M5: planetary.py stale path), 1 MAJOR (dead test file) |
| `simulation_testing.md` | MINOR ISSUES | 1 MAJOR (M7: Python version mismatch), 1 MINOR (scanner false positives for combat_lab paths) |
| `testing_infrastructure.md` | NEEDS UPDATE | 1 MAJOR (M4: newdocs/ path wrong), 1 MAJOR (M6: dead test_damage.py command), 2 MINOR (intentional dead-path warnings), 1 MINOR (scanner false positive) |

## Prioritized Remediation Plan

1. **Fix `component_inspector.py` references** — Affects 3 docs (adding_abilities, component_system, qs_complex_design). Update all import examples and file map entries to use `game.strategy.services.component_abilities` and `game.strategy.services.component_layers` directly. Remove references to the non-existent re-export shim.

2. **Fix `effect_ability_metadata.py` references** — Affects `adding_abilities.md`. Remove from File Map (line 495). Update the shim description (line 422) to note the file was fully removed, not just deprecated. Remove or update dead test file references (lines 434, 539).

3. **Fix `planetary.py` reference** — Affects `qs_complex_design.md:212`. Change to reference the `planetary/` package.

4. **Add "Last verified" date to `pre_commit_hooks.md`** — Missing the standard freshness metadata.

5. **Fix `newdocs/02_PATTERNS.md` reference** — `testing_infrastructure.md:129`. Change to `docs/02_PATTERNS.md`.

6. **Fix `test_damage.py` command example** — `testing_infrastructure.md:170`. Replace with an existing test file path or a generic placeholder.

7. **Fix Python version in `simulation_testing.md`** — Update line 614 from "3.13+" to "3.14" to match AGENTS.md.

8. **Investigate PROJ-411 status** — Determine if the project was completed/archived and update the projects index so `performance_profiling.md` references are verifiable.
