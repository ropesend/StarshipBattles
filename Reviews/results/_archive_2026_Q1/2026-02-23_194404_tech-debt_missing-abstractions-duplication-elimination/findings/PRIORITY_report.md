# PRIORITY: Prioritization & Roadmap Report

## Summary
- **Total issues found:** 11 (the 11 duplication clusters from scope)
- **Critical:** 2, **Major:** 5, **Minor:** 3, **Info:** 1

---

## Methodology

This report independently verified each of the 11 duplication clusters using direct codebase searches (grep, glob, line counts) rather than relying solely on prior art estimates. Key corrections to prior art are noted where found.

**Codebase Baseline (verified):**
- 12,024 tests collected
- Ability test coverage: 943 ability-related tests
- Strategy test coverage: 1,911 strategy tests
- UI test coverage: 2,827 UI tests
- Validation test coverage: 1,059 validation tests

---

## Independent Cluster Assessments

### CRITICAL: Cluster 5 — ValidationResult Factory Methods

**ID:** PRIORITY-001
**Location:** `game/core/validation.py` + 10 consumer files
**Issue:** 83 verbose `ValidationResult(is_valid=False, errors=[...])` constructor calls. The single most-repeated pattern in the strategy layer. 43 single-error, 27 multi-line single-error, 27+ success patterns with 3 inconsistent styles.
**Impact:** Every error-result construction requires 1-4 lines of boilerplate. Inconsistent success pattern (`ValidationResult()` vs `ValidationResult(True)` vs `ValidationResult(is_valid=True)`).

**Independent Verification:**
- `ValidationResult(` constructor: 124 total occurrences across 11 files (confirmed)
- `.add_error(` calls: 20 occurrences across 4 files
- Prior art (DRY-STRAT-SYS CQ-013) said 36; actual count is 83+ (underestimated by 2.3x)

**Size:** 1 file modified (validation.py), 10 files migrated, ~83 call sites
**Risk:** VERY LOW -- factory methods are purely additive; existing constructor still works
**Complexity:** Trivial -- add 3 static methods to an existing dataclass
**Payoff:** ~81 lines saved from multi-line patterns + major consistency improvement
**Dependencies:** NONE -- this is a foundation that every other cluster benefits from

**Category:** Quick Win
**Effort:** Simple (~2 hours including migration of all call sites)
**Recommendation:** Do FIRST. Every other validation/command cluster depends on this.

---

### CRITICAL: Cluster 6 — Command Handler BaseClass + Resolution Helpers

**ID:** PRIORITY-002
**Location:** `game/strategy/engine/command_handlers.py` (485 lines), `game/strategy/engine/superweapon_command_handlers.py` (343 lines)
**Issue:** 19 command handler classes repeat identical fleet resolution (19x), planet resolution (7x), and fleet-not-found error return (19x). The 3-line fleet-resolve block appears 19 times verbatim.
**Impact:** 57 lines of fleet-resolution boilerplate + 21 lines of planet-resolution boilerplate. Inconsistency between error messages across handlers.

**Independent Verification:**
- 19 handler classes confirmed (8 in command_handlers.py, 11 in superweapon_command_handlers.py)
- `session._get_fleet_by_id` appears in both command handler files
- Total handler code: 828 lines across 2 files

**Size:** 2 files modified, 19 handler classes updated, 1 base class created
**Risk:** LOW -- helpers are opt-in, ICommandHandler protocol unchanged
**Complexity:** Straightforward -- mixin/base class with resolution helpers
**Payoff:** ~26 lines directly, but the consistency and readability improvement is substantial
**Dependencies:** Benefits from Cluster 5 (ValidationResult.error() in helpers)

**Category:** Small Project
**Effort:** Medium (~1 day)
**Recommendation:** Do after Cluster 5. Combine migration with factory method adoption.

---

### MAJOR: Cluster 4 — SimpleMultiplierAbility Base Class (recalculate + get_ui_rows + get_primary_value)

**ID:** PRIORITY-003
**Location:** `game/simulation/components/abilities/` (base.py + 6 ability files)
**Issue:** 7 ability classes implement identical `__init__` / `recalculate()` / `get_ui_rows()` / `get_primary_value()` / `sync_data()` patterns. Each has a single numeric value modified by one multiplier stat key.
**Impact:** ~105 lines of boilerplate across 7 classes. Adding a new simple ability requires copying 15-17 lines and changing 5 values.

**Independent Verification:**
- `def recalculate`: 21 methods across 9 ability files
- `self._base_.*\* self.get_effective_stat`: 14 occurrences across 5 files
- `def get_ui_rows`: 35 methods across 11 ability files
- ABS-SIM report verified: 7 classes can migrate (ShieldProjection, ShieldRegeneration, CombatPropulsion, ManeuveringThruster, StrategicMovement, CrewCapacity, LifeSupportCapacity)
- 13 other classes with recalculate() have multi-field or complex logic -- NOT candidates

**Size:** 1 new base class (~30 lines) + 7 classes refactored, ~2,309 total lines in ability files
**Risk:** HIGH -- simulation-core code touched by 943 ability tests. Attribute access via setattr/getattr means typos fail silently.
**Complexity:** Medium -- needs `__init_subclass__` validation, careful attribute mapping
**Payoff:** ~37 lines saved directly, but primary value is consistency, reduced cognitive load, and faster creation of new abilities. Net line change: ~7 lines saved (30 added in base, 37 removed from classes).
**Dependencies:** NONE -- independent of all other clusters

**Category:** Medium Project
**Effort:** Medium (~2-3 days including new base class tests)
**Recommendation:** Do in Phase 3. Requires extra care with simulation tests. Run full test suite after each class migration.

---

### MAJOR: Cluster 10 — Validator Shared Primitives

**ID:** PRIORITY-004
**Location:** `game/strategy/validation/` (3 validators, 777 total lines)
**Issue:** ColonizeValidator (246 lines), SuperweaponValidator (308 lines), TransferValidator (223 lines) repeat entity-existence checks, system-location checks, and early-return error patterns.
**Impact:** ~20-30 lines of pure guard-clause duplication. SuperweaponValidator alone has 18 error returns.

**Independent Verification:**
- 3 validator classes confirmed, no shared base or primitives
- `ValidationResult(is_valid=False` appears 8 times in colonize_validator, 18 in superweapon_validator, 14 in transfer_validator
- `galaxy.get_system_at_location` check repeated 4+ times across superweapon methods

**Size:** 1 new file (~30 lines), 3 validators modified
**Risk:** LOW -- primitives are pure functions, no state, no inheritance
**Complexity:** Straightforward -- extract guard clauses to helper functions
**Payoff:** ~25 lines directly + SuperweaponValidator shrinks from 309 to ~220 lines (29% reduction)
**Dependencies:** Benefits from Cluster 5 (uses ValidationResult.error() factory)

**Category:** Quick Win
**Effort:** Simple (~3-4 hours)
**Recommendation:** Do alongside or immediately after Cluster 5.

---

### MAJOR: Cluster 3 — Ability Value Extraction (CrewRequired Legacy Pattern)

**ID:** PRIORITY-005
**Location:** `game/simulation/components/abilities/crew.py:73`
**Issue:** CrewRequired is the **only** ability class still using legacy inline value extraction pattern. All other 10 abilities have been migrated to `_parse_primary_value()`.
**Impact:** Minor inconsistency -- CrewRequired accepts both 'value' and 'amount' keys, diverging from all other abilities.

**Independent Verification:**
- `self._parse_primary_value`: 13 usages across 3 files (all migrated)
- Legacy pattern `data if isinstance(data, (int, float)) else data.get`: exactly 1 occurrence in crew.py
- Prior art (CQ-001) claimed 15+ classes needed migration -- actual remaining: 1 class

**CORRECTION TO PRIOR ART:** The DRY-SIM-COMP report (CQ-001) claimed 15+ classes need migration. In reality, `_parse_primary_value()` already exists in the base class and 10 of 11 classes have been migrated. Only 1 class remains. This cluster is 93% complete.

**Size:** 1 line changed in 1 file
**Risk:** LOW (verify no component JSON uses `"amount"` key for CrewRequired first)
**Complexity:** Trivial
**Payoff:** Eliminates last inconsistency in value extraction pattern
**Dependencies:** NONE

**Category:** Quick Win
**Effort:** Simple (~15 minutes)
**Recommendation:** Do immediately. Verify JSON data first with a quick grep.

---

### MAJOR: Cluster 1 — UI Font/Color Initialization Boilerplate

**ID:** PRIORITY-006
**Location:** 10+ UI panel/screen files
**Issue:** Font and color initialization boilerplate repeated across UI files. Missing UITheme abstraction.
**Impact:** Scattered magic values for fonts, colors, and spacing. Changes to visual theme require touching many files.

**Independent Verification:**
- `create_section_header` utility already exists in `game/ui/utils.py` with 26+ adoption sites
- Color constants consolidated to `game/simulation/components/abilities/ui_colors.py` (PROJ-167)
- The section header pattern is largely RESOLVED

**CORRECTION TO PRIOR ART:** The duplication report (DUP-001/UI CQ-103) identified section header duplication. This has been substantially addressed -- `create_section_header()` exists and is adopted across 9+ files with 26+ call sites. The remaining duplication is in font/color initialization beyond section headers.

**Size:** Depends on scope -- could be 1 theme file + 10+ consumers
**Risk:** LOW -- UI-only, no simulation impact
**Complexity:** Medium -- needs design discussion on what belongs in a theme vs local config
**Payoff:** Moderate -- prevents scatter of magic values, but section headers already done
**Dependencies:** NONE

**Category:** Small Project (reduced scope from original estimate)
**Effort:** Medium (~1-2 days)
**Recommendation:** Defer to Phase 2. Partial consolidation already done. Remaining work is less impactful than originally estimated.

---

### MAJOR: Cluster 2 — Pygame Drawing Utilities

**ID:** PRIORITY-007
**Location:** 86+ UI files
**Issue:** Missing DrawingUtils abstraction for common pygame drawing patterns (Rect creation, blit, surface creation).
**Impact:** High duplication count but individual patterns are small and idiomatic pygame.

**Independent Verification:**
- `create_centered_rect` already exists in `game/ui/utils.py`
- `calculate_ship_image_scale` already exists in `game/ui/utils.py`
- The utils.py file is growing as a consolidation point

**Size:** Very large -- 86+ files theoretically affected
**Risk:** LOW -- UI-only
**Complexity:** HIGH -- deciding which pygame patterns warrant extraction vs which are idiomatic is subjective. Over-abstraction risk.
**Payoff:** Uncertain -- some patterns (Rect, blit) are 1-2 lines and idiomatic pygame. Wrapping them may reduce readability.
**Dependencies:** Cluster 1 (UITheme) should exist first

**Category:** Large Project (but questionable ROI)
**Effort:** Complex (~1-2 weeks if fully pursued)
**Recommendation:** DEPRIORITIZE. The most impactful patterns have already been extracted to utils.py. Remaining patterns are mostly idiomatic pygame and wrapping them adds abstraction without clear benefit. Cherry-pick only patterns that repeat 5+ times identically.

---

### MINOR: Cluster 7 — JSON Loader Template

**ID:** PRIORITY-008
**Location:** 9 loader classes across game/
**Issue:** JSON loading classes repeat: open file, parse JSON, validate schema, return objects.
**Impact:** Moderate -- 9 loaders with similar structure but different schemas and output types.

**Independent Verification:**
- `json.load` and `load_json` patterns confirmed across multiple files
- Each loader handles different data structures (components, ships, planets, etc.)

**Size:** 9 loader classes, potentially 1 base class
**Risk:** LOW -- loader code is well-tested
**Complexity:** Medium -- loaders differ in validation, error handling, and return types
**Payoff:** Moderate -- reduces boilerplate but loaders are already working correctly
**Dependencies:** NONE

**Category:** Small Project
**Effort:** Medium (~1-2 days)
**Recommendation:** Defer to Phase 3. Loaders work fine. The duplication is structural, not logical.

---

### MINOR: Cluster 8 — DTO to_dict/from_dict Serialization

**ID:** PRIORITY-009
**Location:** 17 files with `to_dict`, 16 files with `from_dict` (28 + 26 = 54 total methods)
**Issue:** 54 serialization methods implemented independently. Each handles its own field mapping.
**Impact:** 500+ lines of serialization boilerplate across 17 files.

**Independent Verification:**
- `def to_dict(self)`: 28 methods across 17 files
- `def from_dict(`: 26 methods across 16 files
- 488 serialization-related tests exist
- Most complex serialization: `galaxy.py` (21 to_dict/from_dict calls), `battle_state.py` (31 calls)

**Size:** Very large -- 17+ files, deeply embedded in save/load
**Risk:** HIGH -- serialization is critical path for save/load. Auto-serialization can subtly change field ordering or type handling.
**Complexity:** HIGH -- each class has custom nested serialization (ships contain components which contain abilities). A generic `Serializable` base would need to handle arbitrary nesting.
**Payoff:** High line count reduction if successful, but the "saves are disposable" policy reduces urgency
**Dependencies:** NONE, but risky to do alongside other changes

**Category:** Large Project
**Effort:** Complex (~2+ weeks)
**Recommendation:** DEPRIORITIZE. The "saves are disposable" policy means serialization code rarely changes. The complexity of a generic Serializable base that handles the deep nesting in galaxy/battle_state is substantial. Risk-reward ratio is unfavorable.

---

### MINOR: Cluster 9 — Pygame Event Handling

**ID:** PRIORITY-010
**Location:** 16 UI files
**Issue:** Event handling patterns repeated across pygame screens.
**Impact:** UI-only duplication in event dispatch.

**Independent Verification:**
- Each screen has its own event handling loop with similar structure
- Some screens use pygame_gui events, others use raw pygame events

**Size:** 16 files, mixed patterns
**Risk:** LOW -- UI-only
**Complexity:** HIGH -- event handling is tightly coupled to screen-specific logic
**Payoff:** Low -- the "common" part is small relative to the screen-specific logic
**Dependencies:** NONE

**Category:** Large Project (but questionable ROI)
**Effort:** Complex
**Recommendation:** SKIP. Event handling is inherently screen-specific. Attempting to abstract it risks making code harder to understand.

---

### INFO: Cluster 11 — Test Fixture Duplication

**ID:** PRIORITY-011
**Location:** 347 test files
**Issue:** Test fixtures and setup code duplicated across test files.
**Impact:** Test maintenance overhead.

**Independent Verification:**
- 12,024 tests across hundreds of files
- Existing conftest.py hierarchy provides shared fixtures
- Test duplication is expected and acceptable in test code for readability

**Size:** Very large -- 347 files
**Risk:** LOW
**Complexity:** HIGH -- test fixtures are intentionally local for clarity
**Payoff:** Low -- test duplication is a different concern from production code duplication
**Dependencies:** NONE

**Category:** Separate effort (not a production code concern)
**Effort:** N/A
**Recommendation:** SKIP. Test fixture duplication is a conscious tradeoff for test readability and independence. Shared fixtures already exist in conftest.py. Further consolidation risks making tests harder to understand.

---

## Dependency Graph

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

    Independent / Deferred:
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Cluster 7   │  │  Cluster 8   │  │  Cluster 9   │  │  Cluster 11  │
    │  JSON Loader │  │  Serialization│  │  Event Handle│  │  Test Fixture│
    │  (SMALL)     │  │  (LARGE)     │  │  (LARGE)     │  │  (SKIP)      │
    └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

**Critical Path:** Cluster 5 -> Clusters 10 + 6 (parallel) -> Cluster 4 (independent, can start anytime)

**Independent Clusters:** Clusters 3, 4, 7, 8 can be done in any order, independently of the critical path.

---

## Risk Matrix

| Cluster | Behavior Change Risk | Regression Risk | Import/Coupling Risk | Rollback Difficulty |
|---------|---------------------|-----------------|---------------------|-------------------|
| 5 (ValidationResult) | NONE (additive) | NONE (existing API unchanged) | NONE (same file) | Trivial (delete methods) |
| 3 (CrewRequired) | LOW (may drop 'amount' alias) | LOW (1 test file affected) | NONE | Trivial (1 line revert) |
| 10 (Validator Primitives) | NONE (pure functions) | LOW (validators well-tested) | LOW (new primitives.py) | Easy (delete file, revert imports) |
| 6 (BaseCommandHandler) | NONE (helpers only) | LOW (19 handler tests exist) | LOW (same module) | Easy (remove base class, inline helpers) |
| 1 (UITheme) | NONE (extract constants) | LOW (UI-only) | LOW (new theme file) | Easy |
| 4 (SimpleMultiplierAbility) | MEDIUM (setattr/getattr) | MEDIUM (943 ability tests) | LOW (same package) | MODERATE (revert 7 classes) |
| 7 (JSON Loader) | LOW | LOW | LOW | Easy |
| 8 (Serialization) | HIGH (subtle type changes) | HIGH (save/load critical) | MEDIUM (new base class) | HARD (deeply integrated) |
| 2 (DrawingUtils) | LOW | LOW | LOW | Easy |
| 9 (Event Handling) | MEDIUM | LOW | MEDIUM | MODERATE |
| 11 (Test Fixtures) | N/A | N/A | N/A | N/A |

---

## Phased Execution Plan

### Phase 1: Quick Wins (do immediately, no project needed)

**Estimated Total Time:** ~4-6 hours
**Can be done in parallel:** Yes (Clusters 3, 5 are independent)

| Order | Cluster | Task | Time | Parallel? |
|-------|---------|------|------|-----------|
| 1a | 5 | Add `ValidationResult.success()`, `.error()`, `.errors()` factory methods | 30 min | Yes |
| 1b | 3 | Fix CrewRequired to use `_parse_primary_value()` | 15 min | Yes |
| 2 | 5 | Migrate all 83 call sites to factory methods (file-by-file) | 3-4 hrs | After 1a |
| 3 | 10 | Create `game/strategy/validation/primitives.py` + adopt in 3 validators | 2-3 hrs | After 1a |

**Test Strategy:** Run targeted tests after each file migration. Full suite before committing.
- After Cluster 3: `pytest tests/ -k "crew" -n 4`
- After Cluster 5: `pytest tests/unit/strategy/ tests/unit/validation/ -n 4`
- After Cluster 10: `pytest tests/unit/strategy/validation/ -n 4`
- Final: `pytest tests/ -n 12`

**Deliverables:**
- `game/core/validation.py` -- 3 new factory methods
- `game/simulation/components/abilities/crew.py` -- 1 line fixed
- `game/strategy/validation/primitives.py` -- NEW (~30 lines)
- 10 files migrated to use factory methods
- 3 validators migrated to use primitives

### Phase 2: Foundation Abstractions (1-2 days)

**Estimated Total Time:** 1-2 days

| Order | Cluster | Task | Time | Dependencies |
|-------|---------|------|------|-------------|
| 1 | 6 | Create `BaseCommandHandler` in command_handlers.py | 2 hrs | Cluster 5 complete |
| 2 | 6 | Migrate 11 superweapon handlers to BaseCommandHandler | 3 hrs | Step 1 |
| 3 | 6 | Migrate 8 core handlers to BaseCommandHandler | 2 hrs | Step 1 |
| 4 | 1 | (Optional) Create UITheme constants file | 3-4 hrs | None |

**Test Strategy:**
- After each handler migration: `pytest tests/unit/strategy/ -n 4`
- After all handlers: `pytest tests/ -k "command or superweapon" -n 4`
- Final: `pytest tests/ -n 12`

### Phase 3: Simulation Abstraction (2-3 days, HIGH CARE)

**Estimated Total Time:** 2-3 days

| Order | Cluster | Task | Time | Dependencies |
|-------|---------|------|------|-------------|
| 1 | 4 | Implement `SimpleMultiplierAbility` base class in base.py | 3 hrs | None |
| 2 | 4 | Add `__init_subclass__` validation | 1 hr | Step 1 |
| 3 | 4 | Write unit tests for SimpleMultiplierAbility itself | 2 hrs | Step 2 |
| 4 | 4 | Migrate 7 classes ONE AT A TIME, full test run after each | 4-6 hrs | Step 3 |
| 5 | 4 | (Optional) Add SuperweaponMarker base class | 1 hr | None |
| 5b | 4 | (Optional) STAT_BINDINGS auto-generation | 2-3 hrs | Step 4 stable |

**Extra Precautions for Phase 3:**
1. **Never migrate more than 1 class without running full suite** -- simulation changes can have subtle cross-cutting effects
2. **Verify setattr/getattr correctness** -- add `__init_subclass__` validation that all required class attributes are non-empty strings
3. **Test with simulation_tests** -- run `pytest simulation_tests/ -n 4` after each migration
4. **Preserve external behavior exactly** -- same attribute names, same method signatures, same return values
5. **SuperweaponMarker is independent** -- can be done in parallel with SimpleMultiplierAbility since it touches different files (superweapons.py only)

### Phase 4: Optional / Deferred

| Cluster | Task | Decision Point |
|---------|------|---------------|
| 7 (JSON Loader) | Create BaseJSONLoader template | Only if adding new loaders |
| 8 (Serialization) | Create Serializable base class | Only if major save format change needed |
| 2 (DrawingUtils) | Extract common pygame patterns | Only if 5+ identical patterns found |
| 9 (Event Handling) | Abstract event dispatch | SKIP -- not recommended |
| 11 (Test Fixtures) | Consolidate test setup | SKIP -- separate concern |

---

## Estimated Total Impact

### If All Recommended Phases (1-3) Are Completed:

| Metric | Value |
|--------|-------|
| **Total duplicate lines eliminated** | ~250-280 lines |
| **Number of files modified** | ~25 files |
| **Number of new files created** | 2 (primitives.py, possibly ui_theme.py) |
| **New abstraction lines added** | ~90 lines (factory methods + base classes + primitives) |
| **Net line change** | ~-160 to -190 lines |
| **Call sites improved** | ~120+ (83 ValidationResult + 19 handlers + 7 abilities + 10 validator guards) |

### Breakdown by Phase:

| Phase | Lines Eliminated | Lines Added | Net | Files Modified |
|-------|-----------------|-------------|-----|---------------|
| Phase 1 (Quick Wins) | ~106 | ~35 | ~-71 | 14 |
| Phase 2 (Foundation) | ~78 | ~25 | ~-53 | 3 |
| Phase 3 (Simulation) | ~112 | ~30 | ~-82 | 8 |
| **Total** | **~296** | **~90** | **~-206** | **~25** |

### If Phase 4 Deferred Items Were Also Done (NOT RECOMMENDED):

| Metric | Additional Value |
|--------|-----------------|
| Serialization (Cluster 8) | ~500 lines eliminated, ~100 added, but HIGH risk |
| Drawing Utils (Cluster 2) | Unknown -- many patterns are idiomatic, not actually duplicate |
| JSON Loader (Cluster 7) | ~80 lines eliminated, ~40 added |

---

## Project Structure Recommendation

If this becomes a project (PROJ-XXX), I recommend:

### Structure: 3 phases + 1 optional

**Phase 1: Quick Wins** (half-day sprint)
- Cluster 5: ValidationResult factory methods + full migration
- Cluster 3: CrewRequired legacy fix (1 line)
- Cluster 10: Validator primitives + adoption
- **Checkpoint:** `pytest tests/ -n 12` -- all 12,024 tests pass

**Phase 2: Command Handler Foundation** (1 day)
- Cluster 6: BaseCommandHandler + migrate 19 handlers
- **Checkpoint:** `pytest tests/ -n 12` -- all tests pass

**Phase 3: Simulation Abstraction** (2-3 days)
- Cluster 4: SimpleMultiplierAbility + migrate 7 classes
- Cluster 4 bonus: SuperweaponMarker base class (~75 lines saved)
- **Checkpoint:** `pytest tests/ -n 12` + `pytest simulation_tests/ -n 4`

**Phase 4 (Optional/Future): Deferred Items**
- Cluster 1: UITheme if UI refresh happens
- Cluster 7: BaseJSONLoader if new loaders needed
- Others: Only if triggered by related work

### Test Strategy Per Phase:
1. **Before starting:** Record baseline: test count, line counts for modified files
2. **During:** Run targeted tests after each file modification
3. **After each phase:** Full suite with `pytest tests/ -n 12`
4. **After Phase 3:** Additionally run `pytest simulation_tests/ -n 4`

### Baselines to Track:
- Test count: 12,024
- Total ability file lines: 2,309
- Total command handler lines: 828
- Total validator lines: 777
- Total validation.py lines: 146

---

## Top 5 Priority Issues

| Rank | ID | Cluster | Category | Impact | Risk | Est. Time |
|------|-----|---------|----------|--------|------|-----------|
| **1** | PRIORITY-001 | 5: ValidationResult Factories | Quick Win | 83 call sites improved, ~81 lines saved | VERY LOW | 4 hrs |
| **2** | PRIORITY-005 | 3: CrewRequired Legacy Fix | Quick Win | Last inconsistency eliminated | LOW | 15 min |
| **3** | PRIORITY-004 | 10: Validator Primitives | Quick Win | 3 validators improved, ~25 lines saved | LOW | 3 hrs |
| **4** | PRIORITY-002 | 6: BaseCommandHandler | Small Project | 19 handlers improved, ~26 lines saved | LOW | 1 day |
| **5** | PRIORITY-003 | 4: SimpleMultiplierAbility | Medium Project | 7 abilities consolidated, pattern for future | MEDIUM | 2-3 days |

### Justification:

1. **Cluster 5 is #1** because it is the single highest-impact quick win in the entire codebase. 83 call sites touched, zero risk, and every other validation/command cluster benefits from having factory methods available.

2. **Cluster 3 is #2** because it is a 15-minute fix that eliminates the last remaining inconsistency in the most-identified duplication pattern (ability value extraction). 93% of this cluster was already done.

3. **Cluster 10 is #3** because it builds naturally on Cluster 5's factory methods and addresses the second-highest duplication in the strategy layer (validator guard clauses).

4. **Cluster 6 is #4** because it provides the foundation for all command handler work. 19 handlers is a significant consolidation that pays ongoing dividends as more handlers are added.

5. **Cluster 4 is #5** because while it has the highest long-term architectural value (establishing the pattern for all future simple abilities), it also has the highest risk (simulation-core code) and requires the most careful testing.

### Clusters NOT in Top 5:

- **Cluster 1 (UITheme):** Partially done via create_section_header. Remaining work is lower-impact.
- **Cluster 2 (DrawingUtils):** Questionable ROI. Most patterns are idiomatic pygame.
- **Cluster 7 (JSON Loader):** Working correctly, duplication is structural not logical.
- **Cluster 8 (Serialization):** Too risky for too little immediate benefit. "Saves are disposable."
- **Cluster 9 (Event Handling):** Not recommended. Event handling is inherently screen-specific.
- **Cluster 11 (Test Fixtures):** Not a production code concern.

---

## Key Corrections to Prior Art

| Prior Art Claim | Actual Finding | Correction |
|----------------|---------------|------------|
| CQ-001: 15+ classes need `_parse_primary_value()` | `_parse_primary_value()` already exists, 10/11 migrated | Only 1 class (CrewRequired) remains |
| DRY-STRAT-SYS CQ-013: 36 ValidationResult creations | 83 total (43 single-error + 27 multi-line + 13 success) | Underestimated by 2.3x |
| UI CQ-103: Section header pattern (19x) needs consolidation | `create_section_header()` already exists with 26+ adoptions | Largely resolved |
| DRY-STRAT-GEN CQ-001-004: Hex math duplication (7 files) | `hex_axial_to_cartesian()` extracted (PROJ-168), `hex_distance` centralized | Largely resolved |
| DUP-001/002: UITheme + DrawingUtils "highest line savings" | Section headers already consolidated. Drawing patterns are idiomatic. | Impact significantly lower than estimated |
| XL-001: 30+ cross-layer numeric type checks | 38 `isinstance(data, (int, float))` across 23 files, but many are legitimate type guards (not duplication) | Many occurrences are intentional (multi-field extraction), only ~5 are true duplication candidates |

---

*Report compiled: 2026-02-23*
*Agent: PRIORITY (Prioritization & Roadmap Agent)*
