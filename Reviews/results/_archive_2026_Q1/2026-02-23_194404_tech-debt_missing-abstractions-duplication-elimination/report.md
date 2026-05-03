# Review Report: Missing Abstractions & Duplication Elimination

## Metadata
- **Date:** 2026-02-23 19:44
- **Type:** Technical Debt Review
- **Description:** Deep investigation of 11 duplication clusters with concrete abstraction designs
- **Agents Used:** 7 (ABS-SIM, ABS-VAL, ABS-UI, ABS-LOAD, CENSUS, DESIGN, PRIORITY)
- **Prior Art:** Deliberate Design Debt Audit (Theme 4), Duplication-Consolidation Analysis

## Executive Summary
- **Total Findings:** 69 across 7 agents
- **Critical:** 9 | **Major:** 27 | **Minor:** 15 | **Info:** 5 | **Census/Data:** 11 | **Prioritization:** 11
- **Total Pattern Instances Counted:** 3,564 across 11 clusters
- **Recommended Action:** 3-phase project (~4-6 days total)
- **Estimated Net Line Savings:** ~206 lines (296 eliminated, 90 added)
- **Overall Assessment:** Actionable — well-scoped extraction opportunities with clear dependency order

### Key Corrections to Prior Art
| Prior Art Claim | Actual Finding |
|----------------|---------------|
| CQ-001: 15+ classes need `_parse_primary_value()` | Only 1 class (CrewRequired) remains — 93% already done |
| CQ-013: 36 ValidationResult creations | 83+ actual — underestimated by 2.3x |
| UI CQ-103: Section header duplication (19x) | Already resolved — `create_section_header()` has 26+ adoptions |
| DRY-STRAT-GEN: Hex math duplication (7 files) | Already resolved — PROJ-168 extracted `hex_axial_to_cartesian()` |
| DUP-001/002: UITheme "highest line savings" | Impact significantly lower than estimated after prior work |

---

## Top 10 Priority Issues (Actionable)

### 1. ValidationResult Factory Methods (Cluster 5)
**IDs:** PRIORITY-001, ABS-VAL-001
**Category:** QUICK WIN | **Risk:** VERY LOW | **Effort:** Simple (~4 hrs)
**Location:** `game/core/validation.py` + 10 consumer files
**Impact:** 83 verbose constructor calls → clean factory methods. Foundation for all other validation work.

Add 3 factory methods to `ValidationResult`:
```python
@staticmethod
def success() -> 'ValidationResult': ...
@staticmethod
def error(message: str) -> 'ValidationResult': ...
@staticmethod
def errors(messages: list[str]) -> 'ValidationResult': ...
```
**Lines saved:** ~81 lines from multi-line patterns + major consistency improvement

---

### 2. CrewRequired Legacy Pattern Fix (Cluster 3)
**IDs:** PRIORITY-005, ABS-SIM-001
**Category:** QUICK WIN | **Risk:** LOW | **Effort:** Simple (~15 min)
**Location:** `game/simulation/components/abilities/crew.py:73`
**Impact:** Last surviving legacy value extraction pattern. 1 line change.

```python
# Before: val = data if isinstance(data, (int, float)) else data.get('value', data.get('amount', 0))
# After:  self.amount = int(self._parse_primary_value(data))
```

---

### 3. Validator Shared Primitives (Cluster 10)
**IDs:** PRIORITY-004, ABS-VAL-003
**Category:** QUICK WIN | **Risk:** LOW | **Effort:** Simple (~3 hrs)
**Location:** `game/strategy/validation/` (3 validators, 777 total lines)
**Impact:** Extract composable guard-clause helpers (NOT a base class). SuperweaponValidator shrinks ~29%.

---

### 4. BaseCommandHandler Resolution Helpers (Cluster 6)
**IDs:** PRIORITY-002, ABS-VAL-002
**Category:** SMALL PROJECT | **Risk:** LOW | **Effort:** Medium (~1 day)
**Location:** `game/strategy/engine/command_handlers.py`, `superweapon_command_handlers.py` (828 lines, 19 handlers)
**Impact:** Fleet resolution repeated 19x, planet resolution 7x. Mixin with `_resolve_fleet()`, `_resolve_planet()`.

---

### 5. SimpleMultiplierAbility Base Class (Cluster 4)
**IDs:** PRIORITY-003, ABS-SIM-002
**Category:** MEDIUM PROJECT | **Risk:** MEDIUM | **Effort:** Medium (~2-3 days)
**Location:** `game/simulation/components/abilities/` (7 classes)
**Impact:** 7 ability classes with identical `__init__`/`recalculate()`/`get_ui_rows()`/`get_primary_value()`. Class-attribute-driven configuration eliminates boilerplate.

Candidates: ShieldProjection, ShieldRegeneration, CombatPropulsion, ManeuveringThruster, StrategicMovement, CrewCapacity, LifeSupportCapacity
NOT candidates: 13 classes with multi-field or complex logic

---

### 6. SuperweaponMarker Base Class (Cluster 4 bonus)
**ID:** ABS-SIM-004
**Category:** QUICK WIN | **Risk:** VERY LOW | **Effort:** Simple
**Location:** `game/simulation/components/abilities/superweapons.py`
**Impact:** 6 identical classes (~110 lines) → 1 base + 6 two-line subclasses (~35 lines). Saves ~75 lines.

---

### 7. UITheme Singleton with Cached Fonts (Cluster 1)
**IDs:** ABS-UI-001, ABS-UI-002
**Category:** MEDIUM PROJECT | **Risk:** LOW | **Effort:** Medium
**Location:** 24 UI files, 60+ font creation statements, 253 inline color definitions
**Impact:** Centralized type scale + semantic color palette. Eliminates redundant font object creation.

---

### 8. Drawing Utility Functions (Cluster 2 — partial)
**IDs:** ABS-UI-003, ABS-UI-004, ABS-UI-005
**Category:** MEDIUM PROJECT | **Risk:** LOW | **Effort:** Medium
**Functions:** `draw_text()`, `draw_labeled_value()`, `draw_panel()`, `draw_button()`, `draw_scrollbar()`
**Impact:** 146 fill+border pairs, 275 render calls, 5 identical scrollbar implementations

---

### 9. Strategy Generation Loader Template (Cluster 7)
**ID:** ABS-LOAD-001
**Category:** SMALL PROJECT | **Risk:** LOW | **Effort:** Simple
**Location:** 3 loaders in `game/strategy/generation/loaders/`
**Impact:** Three loaders repeat identical open-validate-return pattern. Template method base class.

---

### 10. Dataclass Serialization Utility (Cluster 8)
**ID:** ABS-LOAD-005
**Category:** MEDIUM PROJECT | **Risk:** MEDIUM | **Effort:** Medium
**Location:** 14 dataclass types across 8 files
**Impact:** ~221 net lines saved via `dataclass_to_dict()`/`dataclass_from_dict()` standalone functions.
**Note:** 7 complex serializers intentionally remain hand-written (ABS-LOAD-007).

---

## Census Data (CENSUS Agent)

| Cluster | Pattern | Instances | Files | Severity |
|---------|---------|-----------|-------|----------|
| 1. Font/Color Init | Font + Color creation | 708 | ~50 | HIGH |
| 2. Drawing Boilerplate | Pygame draw/blit/render | 1,598 | 95 | HIGH |
| 3. Ability Value Extract | isinstance checks | 31 | 8 | MEDIUM |
| 4. recalculate/get_ui_rows | Repeated methods | 56 | 10 | MEDIUM |
| 5. ValidationResult | Constructor calls | 221 | 20 | HIGH |
| 6. Command Handlers | Handler classes + patterns | 76 | 2 | MEDIUM |
| 7. JSON Loaders | json.load calls | 9 | 5 | LOW |
| 8. DTO Serialization | to_dict/from_dict | 153 | 51 | MEDIUM |
| 9. Event Handling | Event type checks | 73 | 30 | MEDIUM |
| 10. Validators | Validator classes | 39 methods | 6 | MEDIUM |
| 11. Test Fixtures | @pytest.fixture | 1,080 | 348 | HIGH |
| **TOTALS** | | **3,564** | | |

---

## Design Principles (DESIGN Agent)

### Mechanism Assignments
| Cluster | Recommended Mechanism | Rationale |
|---------|----------------------|-----------|
| 1. UITheme | Singleton class | Cached fonts need state; semantic colors are class constants |
| 2. DrawingUtils | Module-level functions | Stateless utilities — no class needed |
| 3. Value Extraction | Existing base method | `_parse_primary_value()` already on `Ability` base |
| 4. SimpleMultiplierAbility | ABC subclass | Template method with class-attribute configuration |
| 5. ValidationResult | Static factory methods | Additive — no inheritance, no state |
| 6. BaseCommandHandler | Mixin class | Resolution helpers mixed into existing Protocol |
| 7. BaseJSONLoader | Template method ABC | Load-validate-return pattern with hooks |
| 8. Serialization | Standalone utility functions | NOT a mixin — `dataclass_to_dict()` / `dataclass_from_dict()` |
| 9. Event Handling | **DO NOT ABSTRACT** | Inherently screen-specific — abstraction adds no value |
| 10. Validator Primitives | Composable pure functions | NOT a base class — `require_fleet()`, `require_planet()` |
| 11. Test Fixtures | **SKIP** | Intentional locality for test readability |

### Key Design Rules
- **Naming:** `Base*` prefix for ABCs, `I*` for Protocols, `*_utils.py` for utility modules
- **Migration policy:** ALL-AT-ONCE per abstraction (per CLAUDE.md). No backward compatibility layers.
- **Testing:** Every new base class/mixin gets its own dedicated unit test file
- **Module placement:** Respect layer boundaries (core → simulation → strategy → UI)

---

## Phased Execution Plan (PRIORITY Agent)

### Phase 1: Quick Wins (~4-6 hours)
| Order | Cluster | Task | Time |
|-------|---------|------|------|
| 1a | 5 | Add `ValidationResult.success()/.error()/.errors()` factory methods | 30 min |
| 1b | 3 | Fix CrewRequired to use `_parse_primary_value()` | 15 min |
| 2 | 5 | Migrate all 83 call sites to factory methods | 3-4 hrs |
| 3 | 10 | Create `primitives.py` + adopt in 3 validators | 2-3 hrs |

### Phase 2: Foundation Abstractions (~1-2 days)
| Order | Cluster | Task | Time |
|-------|---------|------|------|
| 1 | 6 | Create `BaseCommandHandler` with resolution helpers | 2 hrs |
| 2 | 6 | Migrate 19 handlers | 5 hrs |
| 3 | 1 | (Optional) Create UITheme constants | 3-4 hrs |

### Phase 3: Simulation Abstraction (~2-3 days)
| Order | Cluster | Task | Time |
|-------|---------|------|------|
| 1 | 4 | Implement `SimpleMultiplierAbility` base class | 3 hrs |
| 2 | 4 | Add `__init_subclass__` validation + unit tests | 3 hrs |
| 3 | 4 | Migrate 7 classes ONE AT A TIME | 4-6 hrs |
| 4 | 4 | SuperweaponMarker base class (independent) | 1 hr |

### Phase 4: Deferred (only if triggered by related work)
| Cluster | Decision Point |
|---------|---------------|
| 7 (JSON Loader) | Only if adding new loaders |
| 8 (Serialization) | Only if major save format change needed |
| 2 (DrawingUtils) | Only cherry-pick patterns repeating 5+ times identically |
| 9 (Event Handling) | SKIP — not recommended |
| 11 (Test Fixtures) | SKIP — separate concern |

### Dependency Graph
```
                    ┌─────────────────────┐
                    │  Cluster 5          │
                    │  ValidationResult   │
                    │  Factory Methods    │
                    │  (QUICK WIN)        │
                    └────────┬────────────┘
                             │
               ┌─────────────┼─────────────┐
               │             │             │
               ▼             ▼             ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  Cluster 10  │ │  Cluster 6   │ │  Cluster 3   │
    │  Validator   │ │  Command     │ │  CrewRequired │
    │  Primitives  │ │  Handler     │ │  Legacy Fix   │
    │  (QUICK WIN) │ │  Base Class  │ │  (QUICK WIN)  │
    └──────────────┘ │  (SMALL)     │ └──────────────┘
                     └──────────────┘
                                            (independent)
                                      ┌──────────────┐
                                      │  Cluster 4   │
                                      │  SimpleMulti │
                                      │  plierAbility│
                                      │  (MEDIUM)    │
                                      └──────────────┘

    ┌──────────────┐         ┌──────────────┐
    │  Cluster 1   │────────▶│  Cluster 2   │
    │  UITheme     │  should │  DrawingUtils│
    │  (SMALL)     │  precede│  (LARGE)     │
    └──────────────┘         └──────────────┘
```

---

## Risk Matrix

| Cluster | Behavior Risk | Regression Risk | Rollback |
|---------|--------------|-----------------|----------|
| 5 (ValidationResult) | NONE (additive) | NONE | Trivial |
| 3 (CrewRequired) | LOW | LOW | Trivial (1 line) |
| 10 (Validator Primitives) | NONE (pure functions) | LOW | Easy |
| 6 (BaseCommandHandler) | NONE (helpers only) | LOW | Easy |
| 1 (UITheme) | NONE (constants) | LOW | Easy |
| 4 (SimpleMultiplierAbility) | MEDIUM (setattr/getattr) | MEDIUM (943 tests) | Moderate |
| 8 (Serialization) | HIGH | HIGH | Hard |

---

## Estimated Impact (Phases 1-3)

| Phase | Lines Eliminated | Lines Added | Net | Files Modified |
|-------|-----------------|-------------|-----|---------------|
| Phase 1 (Quick Wins) | ~106 | ~35 | -71 | 14 |
| Phase 2 (Foundation) | ~78 | ~25 | -53 | 3 |
| Phase 3 (Simulation) | ~112 | ~30 | -82 | 8 |
| **Total** | **~296** | **~90** | **-206** | **~25** |

---

## Findings by Severity (All Agents)

### Critical (9)
| ID | Title | Agent | Effort |
|----|-------|-------|--------|
| ABS-SIM-001 | CrewRequired Legacy Value Extraction | ABS-SIM | Simple |
| ABS-UI-001 | Font Initialization Boilerplate (60+ statements, 24 files) | ABS-UI | Medium |
| ABS-UI-002 | Inline Color Tuples (253 definitions, 24 files) | ABS-UI | Medium |
| ABS-LOAD-001 | Strategy Generation Loader Template | ABS-LOAD | Simple |
| ABS-LOAD-005 | Dataclass Serialization Boilerplate (14 classes) | ABS-LOAD | Medium |
| DESIGN-005 | Mechanism Assignments for 11 Clusters | DESIGN | Medium |
| DESIGN-010 | Module Placement Map | DESIGN | Simple |
| DESIGN-012 | All-at-Once Migration Policy | DESIGN | Medium |
| DESIGN-015 | Base Classes Need Own Unit Tests | DESIGN | Medium |

### Major (27)
| ID | Title | Agent | Effort |
|----|-------|-------|--------|
| ABS-SIM-002 | SimpleMultiplierAbility Base Class (7 classes) | ABS-SIM | Medium |
| ABS-SIM-003 | STAT_BINDINGS Redundancy with Class Attributes | ABS-SIM | Medium |
| ABS-UI-003 | Labeled Value Rendering (275 render + 302 blit calls) | ABS-UI | Medium |
| ABS-UI-004 | Rounded Panel Drawing (146 fill+border pairs) | ABS-UI | Medium |
| ABS-UI-005 | Scrollbar Drawing (5 identical implementations) | ABS-UI | Simple |
| ABS-VAL-001 | ValidationResult Factory Methods (83 call sites) | ABS-VAL | Simple |
| ABS-VAL-002 | Command Handler Resolution Helpers (19 handlers) | ABS-VAL | Medium |
| ABS-VAL-003 | Validator Shared Primitives (composable functions) | ABS-VAL | Simple |
| ABS-LOAD-002 | Loader Path Resolution Duplication | ABS-LOAD | Simple |
| ABS-LOAD-003 | Raw json.load Bypassing json_utils (2 files) | ABS-LOAD | Simple |
| ABS-LOAD-006 | Non-Dataclass Serialization Boilerplate | ABS-LOAD | Medium |
| ABS-LOAD-007 | Complex Serializers (acceptable — hand-written) | ABS-LOAD | Info |
| DESIGN-001 | Standardize ABC Naming to `Base*` | DESIGN | Simple |
| DESIGN-006 | Avoid Validator Base Class — Use Composition | DESIGN | Simple |
| DESIGN-007 | Declarative Class Attributes + Auto-Apply | DESIGN | Medium |
| DESIGN-008 | Constructor Injection for New Services | DESIGN | Simple |
| DESIGN-009 | Frozen Dataclass for Configuration Objects | DESIGN | Simple |
| DESIGN-011 | Create `game/ui/widgets/` Package | DESIGN | Medium |
| DESIGN-013 | No Backward Compatibility Layers | DESIGN | Simple |
| DESIGN-016 | Migration Tests = Existing Tests | DESIGN | Simple |
| DESIGN-017 | SuperweaponValidator Template Method Pattern | DESIGN | Simple |
| DESIGN-018 | UI Row Generation Typed Objects | DESIGN | Simple |
| PRIORITY-001 | Cluster 5 Highest-Impact Quick Win | PRIORITY | Simple |
| PRIORITY-002 | Cluster 6 Command Handler Foundation | PRIORITY | Medium |
| PRIORITY-003 | Cluster 4 Simulation Abstraction | PRIORITY | Medium |
| PRIORITY-004 | Cluster 10 Validator Primitives | PRIORITY | Simple |
| PRIORITY-006 | Cluster 1 UITheme (partially resolved) | PRIORITY | Medium |

### Minor (15)
| ID | Title | Agent | Effort |
|----|-------|-------|--------|
| ABS-SIM-004 | SuperweaponMarker Base Class (75 lines saved) | ABS-SIM | Simple |
| ABS-UI-006 | Event Handling — DO NOT ABSTRACT | ABS-UI | N/A |
| ABS-VAL-004 | Superweapon Direct Handler Duplication | ABS-VAL | Medium |
| ABS-VAL-005 | Superweapon Mission Handler Duplication | ABS-VAL | Medium |
| ABS-LOAD-004 | TechPresetLoader Missing Validation | ABS-LOAD | Simple |
| DESIGN-002 | Keep `I*` Prefix for Protocols | DESIGN | Simple |
| DESIGN-003 | Keep `*_utils.py` for Utility Modules | DESIGN | Simple |
| DESIGN-004 | Standardize Factory Methods to `from_*()` | DESIGN | Simple |
| DESIGN-014 | Migration Verification Checklist | DESIGN | Simple |
| DESIGN-019 | EventBus Enum Event Types | DESIGN | Simple |
| DESIGN-022 | Mixin vs ABC for Singletons | DESIGN | Simple |
| DESIGN-023 | SerializableMixin Design | DESIGN | Complex |
| PRIORITY-005 | Cluster 3 is 93% Complete | PRIORITY | Simple |
| PRIORITY-007 | Cluster 2 — Questionable ROI | PRIORITY | Complex |
| PRIORITY-008 | Cluster 7 — Structural Not Logical | PRIORITY | Medium |

### Info (5)
| ID | Title | Agent | Effort |
|----|-------|-------|--------|
| ABS-UI-007 | battle_state_viewer Shadows FONT_MAIN | ABS-UI | Simple |
| ABS-LOAD-008 | ModifierEffect Write-Only Serializers | ABS-LOAD | N/A |
| DESIGN-020 | Positive Pattern: Protocol + TypeGuard | DESIGN | N/A |
| DESIGN-021 | Positive Pattern: Frozen Dataclass + Match | DESIGN | N/A |
| PRIORITY-009 | Cluster 8 — DEPRIORITIZE (high risk) | PRIORITY | Complex |

### Clusters Explicitly NOT Recommended
| ID | Cluster | Reason |
|----|---------|--------|
| PRIORITY-010 | Cluster 9: Event Handling | Inherently screen-specific; abstraction adds no value |
| PRIORITY-011 | Cluster 11: Test Fixtures | Intentional locality; separate concern from production code |

---

## Agent Reports

- [ABS-SIM: Simulation Abstraction Designer](findings/ABS-SIM_report.md) (4 findings)
- [ABS-VAL: Validation & Command Abstraction Designer](findings/ABS-VAL_report.md) (5 findings)
- [ABS-UI: UI Abstraction Designer](findings/ABS-UI_report.md) (7 findings)
- [ABS-LOAD: Loader & Serialization Designer](findings/ABS-LOAD_report.md) (8 findings)
- [CENSUS: Call Site Census](findings/CENSUS_report.md) (11 cluster counts)
- [DESIGN: Cross-Cutting Design Principles](findings/DESIGN_report.md) (23 findings)
- [PRIORITY: Prioritization & Roadmap](findings/PRIORITY_report.md) (11 cluster assessments)

---
*Report compiled: 2026-02-23 (auto-compiled + manually enhanced to include all 7 agents)*
