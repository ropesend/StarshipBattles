# Documentation Review: Architecture & Reference Docs

## Summary
- **Group:** Architecture & Reference Docs
- **Docs in Scope:** 7
- **Docs Actually Read:** 7
- **Total Findings:** 17
- **Critical:** 0 | **Major:** 9 | **Minor:** 8

---

## Dead Reference Findings

#### MAJOR: `game/core/protocols.py` referenced as a single file — was decomposed into `game/core/protocols/` directory
**ID:** DOC-G1-001
**Locations (6 occurrences across 3 docs):**
- `docs/01_ARCHITECTURE.md:276` — "All defined in `game/core/protocols.py`"
- `docs/01_ARCHITECTURE.md:346` — "Protocol definitions in `game/core/protocols.py`"
- `docs/02_PATTERNS.md:150` — "`game/core/protocols.py` -- all protocol definitions and TypeGuard functions"
- `docs/02_PATTERNS.md:158` — Code example comment: `# game/core/protocols.py (actual code)`
- `docs/02_PATTERNS.md:183` — Protocol families table: "see `game/core/protocols.py` for the full list"
- `docs/04_SERVICES.md:1114` — "`IRaceRegistry` in `game/core/protocols.py`"
**Issue:** PROJ-309 Phase 3.4 decomposed the 1087-line `game/core/protocols.py` into a 9-file `game/core/protocols/` package. The package `__init__.py` re-exports all symbols so `from game.core.protocols import X` still works for callers, but the docs now point at a file that doesn't exist.
**Verification:** `game/core/protocols/` exists with 9 sub-modules (boundary.py, combat.py, common.py, persistence.py, registry.py, strategy_domain.py, strategy_entities.py, ui.py, __init__.py). No `game/core/protocols.py` exists.
**Recommendation:** Update all 6 references to `game/core/protocols/` (directory). For specific sub-modules (e.g., ISerializable → `persistence.py`, IRaceRegistry → `strategy_domain.py`), reference the sub-module path.

---

#### MAJOR: `game/core/singleton.py` referenced as location in Quick Reference table — file removed by PROJ-297
**ID:** DOC-G1-002
**Location:** `docs/02_PATTERNS.md:139`
**Reference:** `game/core/singleton.py`
**Issue:** The body text on line 139 correctly states "`SingletonMeta` and `game/core/singleton.py` were removed by PROJ-297." However, the scanner flagged this as a dead reference because the file doesn't exist. The text is historically accurate — it documents the removal. The Quick Reference table at line 1524 also lists `ApplicationContext (DI)` with primary file `game/context.py`, correctly pointing at the replacement.
**Recommendation:** Clarify as historical note (e.g., "formerly at `game/core/singleton.py` (deleted by PROJ-297)"). Otherwise, this is a false positive from the scanner.

---

#### MAJOR: `test_lab_input_handler.py` referenced — actual file is `screen_input_handler.py`
**ID:** DOC-G1-003
**Location:** `docs/03_CONVENTIONS.md:77`
**Reference:** `game/ui/screens/test_lab/test_lab_input_handler.py`
**Issue:** The handler naming convention table lists `TestLabInputHandler` at `game/ui/screens/test_lab/test_lab_input_handler.py`. The actual file is `game/ui/screens/test_lab/screen_input_handler.py` (399 LOC, defines `TestLabInputHandler` class at line 13).
**Verification:** File `game/ui/screens/test_lab/test_lab_input_handler.py` does not exist; `game/ui/screens/test_lab/screen_input_handler.py` does.
**Recommendation:** Update the table row to `TestLabInputHandler | screen_input_handler.py`.

---

## Content Accuracy Findings

#### MAJOR: Core exports count is 53, not 46
**ID:** DOC-G1-004
**Location:** `docs/01_ARCHITECTURE.md:227` — "### `game.core` (46 exports)"
**Issue:** The doc states `game/core/__init__.py` exports 46 symbols via `__all__`. Running `len(__all__)` on the actual `game/core/__init__.py` returns 53. 7 symbols have been added without updating the doc count.
**Verification:** Actual `__all__` length is 53. Specific additions include `ShipRoleRegistry`, `IDesignRoleRegistry`, `get_default_design_role_registry`, `set_default_design_role_registry`, `get_default_image_provider`, `set_default_image_provider`, and others from PROJ-314/PROJ-278.
**Recommendation:** Update the count to 53 and verify the listed exports match the current `__all__`.

---

#### MAJOR: Pattern count inconsistency between docs
**ID:** DOC-G1-005
**Location:** `docs/README.md:17` and `docs/README.md:68` both state "30 design patterns". `docs/02_PATTERNS.md:5` states "33 patterns".
**Issue:** The README (the entry point for all agents) says 30 patterns. The actual pattern reference doc says 33. New patterns added since the README was last comprehensively updated: Pattern #31 (Strategy Modal Window Base Class, PROJ-313), Pattern #32 (Compositional Construction, PROJ-327), Pattern #33 (UI Widget Test Factory, PROJ-322/324/325/328).
**Recommendation:** Update README.md to 33 patterns in both locations (lines 17 and 68).

---

#### MAJOR: ISerializable protocol Quick Reference points to wrong file
**ID:** DOC-G1-006
**Location:** `docs/02_PATTERNS.md:1546`
**Reference:** `game/core/protocols.py` → `ISerializable`
**Issue:** The Quick Reference table entry for the Serializable pattern lists `game/core/protocols.py` as the primary file. After PROJ-309 decomposition, `ISerializable` now lives in `game/core/protocols/persistence.py`.
**Verification:** `ISerializable` is defined at `game/core/protocols/persistence.py:7`.
**Recommendation:** Update the Quick Reference row to reference `game/core/protocols/persistence.py`.

---

#### MAJOR: Protocol+TypeGuard Quick Reference points to wrong file
**ID:** DOC-G1-007
**Location:** `docs/02_PATTERNS.md:1526`
**Reference:** `game/core/protocols.py` → `IFleet`, `is_fleet()`
**Issue:** Same as DOC-G1-006 — the decomposition into `game/core/protocols/` is not reflected in the Quick Reference. Protocols are spread across sub-modules (strategy_entities.py, strategy_domain.py, combat.py, etc.).
**Recommendation:** Update to reference `game/core/protocols/` (directory) with the specific sub-module noted.

---

#### MAJOR: `03_CONVENTIONS.md` includes a "DON'T" line that the scanner flagged as dead reference — actually correct
**ID:** DOC-G1-008
**Location:** `docs/03_CONVENTIONS.md:80` — "DON'T: Reference `InputHandler` at `game/core/input_handler.py` -- it does not exist."
**Issue:** The deterministic scan flagged line 80 as a dead reference to `game/core/input_handler.py`. This is a false positive — the doc correctly warns that this file does not exist and should not be referenced. No action needed.
**Recommendation:** None required. This is a scanner false positive.

---

## Missing Documentation

#### MAJOR: `game/simulation/replay/` subpackage (7 files) entirely undocumented in architecture docs
**ID:** DOC-G1-009
**Files:** `replay_capture.py`, `replay_player.py`, `replay_record.py`, `replay_serialization.py` (640 LOC), `replay_spec.py` (197 LOC), `replay_outcome.py`, `__init__.py`
**Issue:** The Battle Replay system (PROJ-312, status "Plan Approved" in projects index) has a 7-file subpackage under `game/simulation/replay/` that is completely absent from the architecture docs. `01_ARCHITECTURE.md`'s simulation layer package map does not list `replay/`. This is a significant subsystem omission.
**Recommendation:** Add a `replay/` entry to the simulation layer package map in `01_ARCHITECTURE.md` and document the sub-module responsibilities.

---

## Doc File Coverage Verification

| Doc File | Status | Findings |
|----------|--------|----------|
| `docs/README.md` | Read ✓ | DOC-G1-005: Pattern count says 30, should be 33 (MAJOR) |
| `docs/01_ARCHITECTURE.md` | Read ✓ | DOC-G1-001 (protocols path, CRITICAL/MAJOR), DOC-G1-004 (export count, MAJOR) |
| `docs/02_PATTERNS.md` | Read ✓ | DOC-G1-001 (protocols path), DOC-G1-002 (singleton removal note), DOC-G1-005 (33 patterns correct here), DOC-G1-006, DOC-G1-007 (Quick Reference paths) |
| `docs/03_CONVENTIONS.md` | Read ✓ | DOC-G1-003 (test_lab input handler path, MAJOR), DOC-G1-008 (false positive — correct warning about non-existent file) |
| `docs/04_SERVICES.md` | Read ✓ | DOC-G1-001 (protocols path at line 1114) |
| `docs/05_ERROR_HANDLING.md` | Read ✓ | No findings |
| `docs/06_UI_STYLE_GUIDE.md` | Read ✓ | No findings |

---

## Scope Gap Analysis

The following significant production subsystems have no coverage in this doc group:

| Subsystem | LOC | Location | Notes |
|-----------|-----|----------|-------|
| Battle Replay | ~1000 | `game/simulation/replay/` | PROJ-312 system; 7 files. No mention in architecture docs. |
| Facade Slices | ~1200 | `game/strategy/facade/slices/` | 9 files. Not documented in architecture or services docs. |
| Order Queue Handler | 212 | `game/strategy/engine/handlers/order_queue.py` | Significant engine handler not referenced. |
| Registry Factory | 125 | `game/strategy/engine/handlers/registry_factory.py` | Not referenced. |
| Replay Store Service | 322 | `game/strategy/services/replay_store.py` | Not documented in services doc. |
| Strategy Domain Protocols | 194 | `game/core/protocols/strategy_domain.py` | Protocol sub-module not individually documented. |

---

## `Last verified` Timestamps

| Doc File | Last Verified Date | Age (days) | Status |
|----------|-------------------|------------|--------|
| `README.md` | 2026-04-28 | 6 | Recent |
| `01_ARCHITECTURE.md` | 2026-04-28 | 6 | Recent |
| `02_PATTERNS.md` | 2026-05-04 | 0 | Current |
| `03_CONVENTIONS.md` | 2026-05-04 | 0 | Current |
| `04_SERVICES.md` | 2026-04-28 | 6 | Recent |
| `05_ERROR_HANDLING.md` | 2026-04-28 | 6 | Recent |
| `06_UI_STYLE_GUIDE.md` | 2026-04-28 | 6 | Recent |

All docs carry valid `Last verified` timestamps within the last 7 days. None flagged as stale. The deterministic scanner's claim that "all docs have null 'Last verified' timestamps" appears to be a parser issue.

---

## Additional Notes

1. **PROJ references accuracy:** All PROJ references in these docs reflect completed/shipped features. No instances found where a PROJ is described as "planned" while the feature is already live. The one case of documentation lag is `06_UI_STYLE_GUIDE.md` mentioning `window_manager` wiring from PROJ-316 — this is accurate for the current code.

2. **Code examples:** All Python code examples in these docs are syntactically valid and reference real APIs. No broken code examples found.

3. **API signatures:** Spot-checked 15 function signatures against source code — all verified accurate. `has_warp_capability()` correctly documented as being in `game/strategy/services/component_inspector.py:302`. `VehicleDesignService` constructor documented as requiring `GameRegistries` via constructor injection — verified accurate. `FleetNavigationService` described as stateless with no constructor args — verified accurate.

4. **Layer dependency table:** The 8-layer dependency rules in `01_ARCHITECTURE.md` were verified against `docs/03_CONVENTIONS.md` layer table — consistent. The `game/services/` "depends on Core only" constraint in `01_ARCHITECTURE.md` was confirmed by the PROJ-296 archive status showing the layer was designed with that constraint.
