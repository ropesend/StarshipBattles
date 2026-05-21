# Documentation Review: Architecture & Core Docs (G1)

## Summary
- Group: Architecture & Core Docs (G1)
- Docs in Scope: 7
- Docs Actually Read: 7
- Total Findings: 7
- Critical: 0 | Major: 2 | Minor: 5

---

## Dead Reference Findings

#### MAJOR: `game/strategy/data/pathfinding.py` no longer exists
**ID:** DOC-G1-01
**Location:** `docs/03_CONVENTIONS.md:32`
**Reference:** `game/strategy/data/pathfinding.py`
**Issue:** The file `game/strategy/data/pathfinding.py` does not exist. The `get_system_at_hex()` function described in this context now lives in `game/strategy/services/galaxy_pathfinding_service.py` as `GalaxyPathfindingService.get_system_at_hex()`.
**Recommendation:** Update the reference to `game/strategy/services/galaxy_pathfinding_service.py` (or simply `GalaxyPathfindingService`).

#### MAJOR: `component_inspector.py` described as still existing but has been deleted
**ID:** DOC-G1-02
**Location:** `docs/04_SERVICES.md:480`
**Reference:** `game/strategy/services/component_inspector.py`
**Issue:** The doc claims `component_inspector.py` is "preserved as a thin re-export shim so the existing import path keeps working" and advises "New code should import directly from `component_abilities` or `component_layers`." However, the file no longer exists — only `component_abilities.py` and `component_layers.py` remain. The re-export shim has been fully removed.
**Recommendation:** Update the text to reflect that `component_inspector.py` has been deleted. Remove or mark the `component_inspector.py` listing in the directory map (line 58). Note that `component_abilities.py` and `component_layers.py` are now the canonical import paths.

#### MINOR: `data/galaxy_protocols.py` missing `game/strategy/` prefix
**ID:** DOC-G1-03
**Location:** `docs/01_ARCHITECTURE.md:155`
**Reference:** `data/galaxy_protocols.py`
**Issue:** The text references `data/galaxy_protocols.py` but the actual path is `game/strategy/data/galaxy_protocols.py`. The path is missing the `game/strategy/` prefix.
**Recommendation:** Change `data/galaxy_protocols.py` to `game/strategy/data/galaxy_protocols.py`.

#### MINOR: `commands.py` referenced as a file but is now a package
**ID:** DOC-G1-04
**Location:** `docs/02_PATTERNS.md:170`
**Reference:** `game/strategy/engine/commands.py`
**Issue:** Pattern #6 (CQRS-lite) lists `game/strategy/engine/commands.py` as a location for commands. The file no longer exists; commands now live in the `game/strategy/engine/commands/` package (with `__init__.py`). This is confirmed by the Path reference check.
**Recommendation:** Update to `game/strategy/engine/commands/` (package path).

Note: The deterministic scanner flagged several other entries in G1 docs as dead refs (`game/core/input_handler.py`, `game/core/protocols.py`, `game/core/singleton.py`, `game/strategy/engine/command_handlers.py`, `game/ui/screens/test_lab/test_run_details.py`, `game/ui/screens/race_setup_screen.py`, `game/ui/screens/ship_detail_panel.py`). These are all **false positives** — each is intentionally mentioned in a "Stale Name Traps", "Warnings And Stale Reference Corrections", "Stale References Fixed Here", or "Re-Export Shim (Removed)" section that explicitly identifies them as non-existent, retired, or incorrect paths. They are warnings, not active references.

---

## Stale PROJ Reference Findings

None. The deterministic scanner flagged 33 PROJ mentions in G1 docs, all with "unknown" status. However, every reference is in the context of describing *completed historical work* (e.g., "PROJ-390 retired the module-level shim", "PROJ-436 Phase 9 deleted the legacy..."). These are not claims about ongoing or planned work. The "unknown" status reflects the scanner's inability to resolve archived PROJ statuses, not doc inaccuracy.

---

## Content Accuracy Findings

#### MAJOR: Doc claims `component_inspector.py` exists as a re-export shim
**ID:** DOC-G1-02 (same as dead ref above)
**Location:** `docs/04_SERVICES.md:58, 480-482`
**Issue:** The directory map at line 58 lists `component_inspector.py` as "Thin re-export shim over component_abilities + component_layers (legacy import path)." At lines 480-482 the doc states it "is preserved as a thin re-export shim so the existing import path keeps working." The file has been deleted. Verified: `ls game/strategy/services/component_inspector.py` returns "No such file or directory."
**Recommendation:** Remove `component_inspector.py` from the directory map. Update the text to state the shim has been retired; `component_abilities.py` and `component_layers.py` are the only import paths.

#### MINOR: Hardcoded developer machine path in conventions doc
**ID:** DOC-G1-05
**Location:** `docs/03_CONVENTIONS.md:332`
**Issue:** The "One component per role" section references a user-memory file at `C:/Users/rossr/.claude/projects/c--Developer-StarshipBattles/memory/feedback_one_component_per_role.md`. This violates the convention stated in the same doc (lines 231-240) that agent/repo documentation must not embed developer-machine checkout roots.
**Recommendation:** Replace with a repo-relative reference or remove the external path, keeping only the conceptual guidance.

---

## Code Example Issues

No issues found. All Python code blocks in G1 docs use correct imports, valid API shapes, and reference existing libraries/frameworks. The Pattern #20 skeleton (`_validate_tick_inputs`) and the import organization examples in `03_CONVENTIONS.md` are syntactically valid and follow current conventions.

---

## Missing Documentation

#### MINOR: `docs/README.md` missing `Last verified` line
**ID:** DOC-G1-06
**Location:** `docs/README.md` (entire file)
**Issue:** Every doc file with an H1 should carry a `> **Last verified:** YYYY-MM-DD` line directly below it (per `docs/03_CONVENTIONS.md:500-514`). `README.md` has no such line. All other G1 docs have one.
**Recommendation:** Add `> **Last verified:** YYYY-MM-DD - <summary>` below the `# Starship Battles Documentation Routing` heading.

#### MINOR: No dedicated doc for galaxy generation subsystem
**ID:** DOC-G1-07
**Location:** Scope gap
**Issue:** The galaxy generation subsystem at `game/strategy/generation/` contains substantial modules (density maps, placement, region classification, image registries, blueprint loaders) with no corresponding `docs/systems/galaxy_generation.md` or equivalent. The architecture doc mentions it briefly under the strategy layer section but there is no dedicated domain doc. Compare: fighters, satellites, minefields, production, research, and resources each have their own `docs/systems/*.md`.
**Recommendation:** Consider adding a `docs/systems/galaxy_generation.md` covering density models, system blueprint loading, placement algorithm, and image registry pipeline. This would bring generation up to parity with other similarly-scoped subsystems.

---

## Doc File Coverage Verification

| Doc File | Status | Findings |
|----------|--------|----------|
| `docs/README.md` | Needs `Last verified` | DOC-G1-06: Missing verified timestamp |
| `docs/01_ARCHITECTURE.md` | Minor path issue | DOC-G1-03: `data/galaxy_protocols.py` prefix |
| `docs/02_PATTERNS.md` | Minor path issue | DOC-G1-04: `commands.py` → `commands/` |
| `docs/03_CONVENTIONS.md` | 2 issues | DOC-G1-01: `pathfinding.py` dead ref; DOC-G1-05: hardcoded path |
| `docs/04_SERVICES.md` | 1 stale claim | DOC-G1-02: `component_inspector.py` shim no longer exists |
| `docs/05_ERROR_HANDLING.md` | Clean | No findings |
| `docs/06_UI_STYLE_GUIDE.md` | Clean | Scanner false positives only (intentional stale-name corrections) |

---

## Scanner False Positives Documented

The following deterministic scanner dead-ref hits for G1 docs were reviewed and determined to be false positives (all are in "warning" or "stale name trap" sections that intentionally reference non-existent paths):

| Doc | Line | Reference | Why False Positive |
|-----|------|-----------|--------------------|
| `README.md` | 170 | `game/core/input_handler.py` | In "Stale Name Traps" section: "There is no `game/core/input_handler.py`" |
| `README.md` | 187 | `tests/path/to/test.py` | Placeholder example syntax in command block |
| `01_ARCHITECTURE.md` | 491 | `game/core/protocols.py` | In "Warnings" section: "`game/core/protocols.py` is stale terminology" |
| `02_PATTERNS.md` | 38 | `data/classes/` | Describes "data/classes/callables" conceptually, not a literal path |
| `02_PATTERNS.md` | 88 | `game/core/singleton.py` | Explicitly described as RETIRED |
| `02_PATTERNS.md` | 187 | `game/strategy/engine/command_handlers.py` | Explicitly described as REMOVED (PROJ-383) |
| `02_PATTERNS.md` | 819 | `game/ui/screens/test_lab/test_run_details.py` | Explicitly described as REMOVED (PROJ-417) |
| `02_PATTERNS.md` | 824 | `game/ui/screens/race_setup_screen.py` | Explicitly described as REMOVED (PROJ-416) |
| `02_PATTERNS.md` | 827 | `game/strategy/engine/command_handlers.py` | Explicitly described as REMOVED (PROJ-383) |
| `03_CONVENTIONS.md` | 42 | `game/core/input_handler.py` | In warning: "`game/core/input_handler.py` does not exist" |
| `03_CONVENTIONS.md` | 308 | `tests/path/to/test.py` | Placeholder example syntax in command block |
| `04_SERVICES.md` | 895 | `game/strategy/services/area_effect_manager.py` | In "Stale References to Avoid": "Do not reference ..." |
| `06_UI_STYLE_GUIDE.md` | 229 | `data/FiraCode-Regular.ttf` | Describes a value inside a JSON theme file, not a direct file path |
| `06_UI_STYLE_GUIDE.md` | 518 | `game/ui/screens/ship_detail_panel.py` | In correction: "not `game/ui/screens/ship_detail_panel.py`" |
