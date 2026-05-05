# PROJ-350 Review: Combat Lab Registry Class Identity Fix

**Review mode:** standard (audit-only verification)
**Scope:** `combat_lab/registry.py`, `combat_lab/spec_compiler.py`, `combat_lab/scenarios/templates.py`, `tests/unit/combat_lab/test_registry_class_identity.py`, `Projects/active_projects/PROJ-350/decisions.md`
**Commit:** `d555e8bd1`
**Limitations:** `combat_lab/runner.py:271-292` explicitly scoped out per decisions.md. Codebase-wide `spec_from_file_location` audit covers all other usages.

---

## Summary

The fix replaces the bespoke `spec_from_file_location` / `module_from_spec` / `exec_module` pipeline in `combat_lab/registry.py` with `importlib.import_module`. This eliminates the class-identity bug where scenario discovery re-executed `templates.py`, creating duplicate class objects that broke `isinstance` checks in `spec_compiler.py`.

**Overall verdict: PASS.** The fix is correct, the regression test is well-constructed and would have caught the original bug, and no other instances of this class-identity pattern exist in the codebase.

---

## Findings

### CRIT-001 — (No critical findings)

No critical severity issues found.

---

### MAJ-001: Regression test correctly pins class-identity invariants

**File:** `tests/unit/combat_lab/test_registry_class_identity.py:30-78`
**Severity:** MAJ (positive finding — test quality)

The regression test exercises three layers of class-identity verification:

1. **`isinstance(instance, ComparisonScenario)`** (line 60) — structural check: would return `False` under the old loader because the registry-discovered class inherits from a *different* `ComparisonScenario` object.

2. **`compiler_cs is ComparisonScenario`** (line 71) — object-identity check via `is`: verifies `spec_compiler`'s imported `ComparisonScenario` is literally the same object as `templates.ComparisonScenario`. This is the strongest check — even if both modules happened to produce the same MRO, `is` would catch the duplication.

3. **`build_test_battle_spec(instance, registries=None)`** (line 78) — functional endpoint: exercises the actual crash site that threw `NotImplementedError`.

**Reproduction analysis:** The test would have failed on the old code. Under the old loader, `runner.py:20` imports `combat_lab.spec_compiler` (caching `ComparisonScenario` from `templates.py`). `TestRegistry.__init__` then re-executes `templates.py` via `exec_module`, creating a new `ComparisonScenario`. The registered scenarios subclass the new class; `spec_compiler` holds the old. `isinstance` fails → `NotImplementedError`.

**Status:** The test is correctly constructed. No remediation needed.

---

### MAJ-002: No remaining `spec_from_file_location` / `module_from_spec` in registry path

**File:** `combat_lab/registry.py:196-204`
**Severity:** MAJ (positive finding — corrective fix)

The `_discover_scenarios` method now uses:

```python
module_name = f"combat_lab.scenarios.{file_path.stem}"
module = importlib.import_module(module_name)
```

This honors `sys.modules` — if `combat_lab.scenarios.templates` was already imported by `runner.py` → `spec_compiler.py`, `import_module` returns the cached module object. No duplicate class objects are created.

**Verification:**
- No `importlib.util` import in `registry.py` (only `import importlib` at line 48).
- No `spec_from_file_location` call in `registry.py`.
- No `module_from_spec` call in `registry.py`.
- No `exec_module` call in `registry.py`.

**Status:** Fix is clean and complete. No remediation needed.

---

### MIN-001: `runner.py:287` uses `spec_from_file_location` — no class-identity risk

**File:** `combat_lab/runner.py:284-289`
**Severity:** MIN (documentation / awareness)

The CLI `__main__` block loads a user-specified file via:

```python
spec = importlib.util.spec_from_file_location("dynamic_scenario", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
```

**Risk assessment:**
- Module name is `"dynamic_scenario"` — never `"combat_lab.scenarios.templates"` or any scenario module path.
- Used only by `python -m combat_lab.runner <path.py>` CLI invocation.
- Does not overwrite any `sys.modules` entry for an existing module.
- Scenarios loaded this way are not registered via `TestRegistry`, so no identity collision with spec compiler dispatch.

**Status:** No class-identity bug. Explicitly scoped out by decisions.md. No remediation needed.

---

### MIN-002: Codebase-wide `spec_from_file_location` audit — all safe

**Severity:** MIN (documentation / awareness)

All 3 remaining production/test uses of `spec_from_file_location` outside `runner.py`:

| File | Module Name | Risk |
|------|-------------|------|
| `tests/unit/tools/test_lint_test_files.py:21` | `"lint_test_files_under_test"` | None — unique name, test-only |
| `tests/unit/research/test_research_renderer_drawing.py:36` | `"research_renderer_isolated_drawing"` | None — unique name, test-only |
| `tests/unit/research/test_research_renderer.py:35` | `"research_renderer_isolated"` | None — unique name, test-only |

All three use descriptive module names that cannot collide with project packages. None are in production code. None load scenario modules. None participate in registry discovery.

**Status:** No latent class-identity bugs from `spec_from_file_location` anywhere in the codebase. No remediation needed.

---

### NIT-001: `combat_lab/scenarios/templates.py` is 1343 lines

**File:** `combat_lab/scenarios/templates.py`
**Severity:** NIT

At 1343 lines, `templates.py` substantially exceeds the 500 LOC ceiling. However:
- The 500 LOC rule per `docs/03_CONVENTIONS.md §2.3` applies to "production-source files under `game/`". `combat_lab/` is test infrastructure, not under `game/`.
- Conventions §2.3 also notes "Test files are exempt." Combat Lab scenarios are test infrastructure.
- The file was the locus of the class-identity bug precisely because it was the one shared module being re-imported — its size is a symptom of consolidation, not scattering.

**Suggested remediation:** None required for this audit. If templates.py grows further, consider splitting by template type (e.g. `templates/duel.py`, `templates/comparison.py`, etc.), preserving a re-export shim in `templates/__init__.py`.

---

### INFO-001: Comment in `registry.py` accurately documents the fix rationale

**File:** `combat_lab/registry.py:197-202`
**Severity:** INFO

The comment block documents both the why (PROJ-350) and what changed (old approach → new approach). This is good practice — future readers understand the original bug without needing archaeology.

---

## Verification Summary

| Instruction | Result |
|-------------|--------|
| Regression test would fail on old code | **CONFIRMED** — test resets registry, forces fresh discovery, asserts isinstance, is, and functional dispatch |
| No remaining `spec_from_file_location` in registry path | **CONFIRMED** — only `importlib.import_module` at line 204 |
| Runner CLI loader has no class-identity problem | **CONFIRMED** — uses module name `"dynamic_scenario"`, never overwrites templates |
| Codebase-wide `spec_from_file_location` audit | **CONFIRMED** — 3 test-only uses with unique module names, zero risk |
| Regression test pins class identity | **CONFIRMED** — isinstance + is + functional dispatch |

**Overall: All instructions verified. No issues found. Fix is correct and complete.**
