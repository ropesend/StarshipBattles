# Style Consistency Analysis Report

**Date:** 2026-03-13
**Scope:** `game/` directory (429 Python files, ~109K lines)
**Layers:** core (21 files), simulation (73 files), strategy (113 files), ai (10 files), ui (197 files)

---

## Summary

- **Total issues found:** 16
- **Critical:** 0
- **Major:** 4
- **Minor:** 8
- **Info:** 4

Overall, the codebase demonstrates strong style discipline. PEP 8 naming (snake_case functions, PascalCase classes) is followed with near-perfect consistency. The project has fully standardized on f-strings (100%), has zero bare `except` clauses, zero mutable default arguments, and clean import separation in 93% of files. The most significant inconsistencies are in string quoting, type hint coverage in the UI layer, boolean naming, and mixed use of `@property` vs `get_` accessor methods.

---

## Style Consistency Scorecard

| Style Aspect | Consistency Level | Dominant Pattern | Variants Found |
|---|---|---|---|
| Class naming (PascalCase) | **Excellent** (99.7%) | PascalCase | 2 private helper classes with underscores |
| Function naming (snake_case) | **Excellent** (99.95%) | snake_case | 2 uppercase pseudo-constants in methods |
| Enum member naming | **Excellent** (100%) | UPPER_SNAKE_CASE | None |
| Module-level constant naming | **Good** (80%) | UPPER_SNAKE_CASE | 156 lowercase (mostly `logger`) |
| String formatting | **Excellent** (100%) | f-strings | 0 `.format()`, 0 `%`-formatting |
| String quoting | **Poor** (split) | Slight single-quote lean (54/46) | Layer-dependent, 149 mixed files |
| Import separation | **Good** (93%) | Blank-line separated groups | 26 files unseparated |
| Type hint coverage | **Mixed** | Varies by layer (56%-95%) | UI layer significantly lower |
| Docstring presence | **Good** (87% overall) | Present on most public APIs | UI functions 86%, sim functions 83% |
| Docstring format | **Good** | Google-style (Args/Returns) | 939 ad-hoc multi-line docstrings |
| Trailing commas | **Low adoption** (22%) | No trailing comma | Some files use them, most don't |
| Boolean naming | **Mixed** | No consistent prefix convention | 57 unprefixed vs 31 prefixed |
| Event handler naming | **Mixed** | handle_ / process_event / on_ | Three conventions coexist |
| Dataclass usage | **Good** | Mutable (78%) | 25 frozen, 88 mutable, 0 slots |
| Nesting depth | **Acceptable** | Depth 0-3 (95%) | 115 functions at depth 5+ |
| Property vs get_ | **Mixed** | Both used equally | 514 @property vs 524 get_ |

---

## Findings

### 1. Naming Style

#### Major: Inconsistent String Quoting Convention
**ID:** SA-001
**Location:** Various (all layers)
**Issue:** The codebase has a near-50/50 split between single quotes (54%) and double quotes (46%), with no clear convention. The preference varies dramatically by layer:
- **ai:** 90% single-quote
- **simulation:** 71% single-quote
- **core:** 63% double-quote (inverted!)
- **strategy:** 50/50 split
- **ui:** 51% single / 49% double

149 out of 366 files with sufficient strings (41%) use a mix of both styles internally, meaning the quoting choice appears arbitrary within many files.
**Impact:** Inconsistent quoting creates visual noise and makes automated formatting harder. It signals no enforced style guide.
**Recommendation:** Standardize on double quotes (Python community norm, matches JSON, avoids apostrophe escaping) and enforce via formatter (e.g., Black or Ruff).
**Effort:** Simple (automated via formatter)

---

#### Minor: Mixed `calc_` / `calculate_` / `compute_` Prefixes
**ID:** SA-002
**Location:** Various
**Issue:** Three different prefixes are used for computation methods:
- `calculate_` : 50 functions (dominant, used across all layers)
- `compute_` : 7 functions (mostly in `strategy/services/` and `ui/`)
- `calc_` : 2 functions (only in `ui/screens/builder/weapons_viewmodel.py`)
**Impact:** Low. `calculate_` is clearly dominant and `calc_`/`compute_` are rare enough to be one-off outliers.
**Recommendation:** Standardize on `calculate_` for all computation methods. Rename the 9 outliers.
**Effort:** Simple

---

#### Minor: Boolean Variables Often Lack Semantic Prefix
**ID:** SA-003
**Location:** Various (57 unprefixed booleans vs 31 prefixed)
**Issue:** Only 35% of type-annotated `bool` variables use a standard boolean prefix (`is_`, `has_`, `can_`, `should_`). The remaining 65% use bare names like `headless`, `start_paused`, `enable_logging`, `auto_spread_enabled`, `negate`.

Distribution of prefixed bools: `is_` (21), `has_` (6), `can_` (4), `should_` (0).

Some bare names are self-evidently boolean (`headless`, `start_paused`, `allow_retreat`) so this is partly a false positive. But names like `negate`, `DEFAULT_AVOIDANCE`, and `showing_new_game_setup` are ambiguous without context.
**Impact:** Moderate readability impact. Readers must check type annotations to confirm boolean semantics.
**Recommendation:** Add `is_`/`has_`/`can_` prefixes to ambiguous boolean names. Leave clearly boolean names (e.g., `headless`, `start_paused`) as-is.
**Effort:** Medium

---

#### Info: Entity ID Naming is Fully Consistent
**ID:** SA-004
**Location:** Various
**Issue:** None -- this is a positive finding. All entity identifiers consistently use `_id` suffix (`fleet_id`, `ship_id`, `planet_id`, `empire_id`). Zero uses of `_uuid` suffix. This is excellent consistency.
**Impact:** None
**Recommendation:** No action needed
**Effort:** N/A

---

#### Info: Abbreviation Preferences Are Established
**ID:** SA-005
**Location:** Various
**Issue:** The codebase has clear abbreviation preferences that are followed fairly consistently:
- `btn` (746) strongly preferred over `button` (346) in UI
- `pos` (536) strongly preferred over `position` (77)
- `cmd` (196) preferred over `command` (45) in strategy
- `idx` (275) vs `index` (218) -- roughly equal, context-dependent
- `config` (337) strongly preferred over `cfg` (32)
- `manager` (275) strongly preferred over `mgr` (33)
- `ctx` (86) vs `context` (161) -- `context` preferred

These are established conventions rather than inconsistencies.
**Impact:** Low -- most have a clear dominant form
**Recommendation:** Consider documenting the preferred abbreviations in a style guide for new code
**Effort:** Simple (documentation only)

---

### 2. Code Formatting

#### Major: UI Layer Type Hint Coverage is Significantly Lower
**ID:** SA-006
**Location:** `game/ui/` (2,134 functions)
**Issue:** Type hint coverage varies dramatically by layer:

| Layer | Functions | Return Type | Any Type Hint |
|-------|-----------|-------------|---------------|
| core | 294 | 92% | 95% |
| strategy | 839 | 86% | 94% |
| ai | 161 | 89% | 91% |
| simulation | 695 | 77% | 85% |
| ui | 2,134 | **47%** | **56%** |

The UI layer -- which contains nearly half of all functions -- has type hints on only 56% of its functions, compared to 85-95% in other layers. This means ~930 functions in the UI layer lack any type annotations.
**Impact:** Reduced IDE assistance, harder refactoring, and inconsistent code quality expectations across the project.
**Recommendation:** Gradually add type hints to UI functions, prioritizing public methods and event handlers. Consider running `mypy` with per-module strictness.
**Effort:** Complex (ongoing effort, ~930 functions to annotate)

---

#### Minor: Trailing Comma Adoption is Low and Inconsistent
**ID:** SA-007
**Location:** Various
**Issue:** Only 22% of multi-line collections/parameter lists use trailing commas (551 with vs 1,958 without). This makes diff noise when adding items to the end of a collection.
**Impact:** Minor -- affects git diff cleanliness when extending lists/dicts.
**Recommendation:** Adopt trailing commas in multi-line constructs. Enforceable via Ruff rule `COM812`.
**Effort:** Simple (automated via formatter)

---

#### Info: Line Length is Well-Controlled
**ID:** SA-008
**Location:** Various
**Issue:** Line length is well-managed across the codebase:
- core: 0.1% of lines > 100 chars
- simulation: 0.7% > 100 chars
- strategy: 0.6% > 100 chars
- ai: 0.7% > 100 chars
- ui: 0.9% > 100 chars

Only 106 lines across the entire UI layer exceed 120 characters. The maximum line is 215 chars (a few outliers).
**Impact:** Positive finding. No action needed.
**Recommendation:** Consider enforcing a 120-char hard limit.
**Effort:** Simple

---

#### Minor: Import Ordering Not Fully Standardized
**ID:** SA-009
**Location:** 26 files lack blank-line separation between import groups
**Issue:** 93% of files (322/348 with 3+ imports) properly separate import groups with blank lines (stdlib, third-party, local). 26 files have unseparated imports. Examples include: `game/core/math.py`, `game/research/data/tech_node.py`, `game/simulation/combat/__init__.py`.
**Impact:** Low -- the dominant pattern is clear and most files comply.
**Recommendation:** Run `isort` or Ruff import sorting on the 26 non-compliant files.
**Effort:** Simple (automated)

---

### 3. Language Idioms

#### Info: F-String Adoption is Complete
**ID:** SA-010
**Location:** Entire codebase
**Issue:** Positive finding. 100% of string formatting uses f-strings. Zero `.format()` calls and zero `%`-formatting found. This is exemplary consistency.
**Impact:** None -- this is ideal.
**Recommendation:** No action needed.
**Effort:** N/A

---

#### Major: Mixed `@property` vs `get_` Accessor Pattern
**ID:** SA-011
**Location:** Various (514 `@property` vs 524 `get_` methods across all layers)
**Issue:** The codebase uses both `@property` decorators and `get_` prefix methods for attribute access, with nearly equal frequency and no clear separation of concerns:

| Layer | @property | get_ | set_ |
|-------|-----------|------|------|
| core | 118 | 25 | 2 |
| simulation | 121 | 114 | 9 |
| strategy | 44 | 116 | 3 |
| ai | 18 | 53 | 17 |
| ui | 160 | 122 | 44 |

The core layer strongly prefers `@property` (82% vs 18%), while strategy and AI strongly prefer `get_` methods (73% and 75% respectively). Additionally, 55 `get_` methods are simple `return self.attr` wrappers that should ideally be properties -- 20+ of these are concentrated in `game/ai/interfaces/controllable.py`.

The `get_` methods that take parameters are a different case and appropriately use the prefix pattern. But zero-argument `get_` wrappers around `self.attr` are a clear @property candidate.
**Impact:** Inconsistent API style across layers. Callers must remember whether to use `obj.name` or `obj.get_name()` for similar semantics.
**Recommendation:**
1. Convert zero-argument `get_` methods that are simple `self.attr` returns to `@property` (55 methods, concentrated in `controllable.py`)
2. Reserve `get_` for methods that take parameters or perform significant computation
3. Use `@property` for computed values that feel like attributes
**Effort:** Medium (55 simple conversions, plus updating call sites)

---

#### Minor: Ad-Hoc Docstrings Alongside Google-Style
**ID:** SA-012
**Location:** Various (939 ad-hoc vs 1,642 Google-style)
**Issue:** 64% of multi-line docstrings use Google-style sections (`Args:`, `Returns:`, `Raises:`), but 36% (939) are ad-hoc multi-line descriptions without structured sections. The Google-style sections breakdown: `Args:` (1,400), `Returns:` (1,081), `Raises:` (89), `Attributes:` (50).

Ad-hoc docstrings typically describe behavior in prose paragraphs, often including PROJ-XXX migration notes or state machine descriptions. Many of these are class/module docstrings where structured sections aren't needed.
**Impact:** Low. The ad-hoc docstrings are mostly descriptive text where Args/Returns sections would be irrelevant. The function-level docstrings that matter most are well-standardized on Google style.
**Recommendation:** No immediate action. The current split is appropriate: Google-style for functions, prose for classes/modules.
**Effort:** N/A

---

### 4. Event Handler Naming

#### Major: Three Coexisting Event Handler Conventions
**ID:** SA-013
**Location:** `game/ui/` and `game/core/protocols.py`
**Issue:** Event/action handlers use three different naming conventions with no clear delineation:

1. **`handle_`** (110 methods): Used in core protocols (`handle_event`, `handle_resize`) and UI components (`handle_click`, `handle_exit_dialog_click`)
2. **`process_event`** (widespread in UI): Used as the standard event dispatch method in UI panels and windows (`process_event`)
3. **`on_`** (45 methods): Used sporadically (`on_click` in `system_tree_panel.py`)
4. **`_handle_button_pressed`** / **`_handle_keydown`**: Private handler variants

The distinction between `handle_event`, `process_event`, and `on_click` for similar patterns is confusing.
**Impact:** Developers must learn which convention each module uses. New code may pick any of the three.
**Recommendation:** Standardize:
- `process_event()` for the main event dispatch method (already dominant in UI)
- `handle_*` for specific event type handlers called by the dispatcher
- Deprecate `on_*` pattern (least used, only 1 instance in event context)
**Effort:** Medium

---

### 5. Function/Method Style

#### Minor: Deep Nesting in UI Event Handlers
**ID:** SA-014
**Location:** `game/ui/screens/` (primarily)
**Issue:** 115 functions have nesting depth > 4, and 15 functions have nesting depth > 8. The worst offender is `toggle_filter` in `fleet_report_view_model.py` with nesting depth 20. Other extreme cases:

| File | Function | Depth |
|------|----------|-------|
| `fleet_report_view_model.py` | `toggle_filter` | 20 |
| `formation_editor.py` | `_handle_button_pressed` | 14 |
| `strategy_ui_action_router.py` | `handle_ui_action` | 14 |
| `fleet_report_filters.py` | `sort_ships` | 13 |
| `strategy_event_router.py` | `_handle_button_pressed` | 12 |
| `workshop_event_router.py` | `_handle_button_pressed` | 12 |

Most deeply-nested functions are in the UI layer handling button/event dispatch with cascading if/elif chains.
**Impact:** Reduced readability and increased cognitive load. Deep nesting makes it hard to reason about control flow.
**Recommendation:** Refactor deeply-nested handlers using:
1. Dictionary dispatch (mapping action strings to handler functions)
2. Early return guards
3. Extract nested blocks into private methods
**Effort:** Medium-Complex

---

#### Minor: Large Functions in UI and Strategy Layers
**ID:** SA-015
**Location:** Various (262 functions > 50 lines, 55 functions > 100 lines)
**Issue:** Function length varies significantly by layer:

| Layer | Avg Length | >50 lines | >100 lines | Max |
|-------|-----------|-----------|------------|-----|
| core | 7.0 | 1 | 0 | 57 |
| simulation | 16.3 | 42 | 4 | 170 |
| strategy | 24.3 | 85 | 8 | 157 |
| ai | 9.8 | 4 | 1 | 126 |
| ui | 21.9 | 220 | 42 | 285 |

The core layer is exemplary (avg 7 lines). The UI layer has 42 functions over 100 lines, with the worst being `create_strategy_panels` at 285 lines.
**Impact:** Long functions are harder to test, understand, and maintain.
**Recommendation:** Target functions > 100 lines for decomposition. Priority targets:
1. `create_strategy_panels` (285 lines) - extract panel creation into separate builders
2. `build_sidebar` (243 lines) - extract section builders
3. `set_items` (212 lines) - extract item processing logic
**Effort:** Complex (ongoing decomposition effort)

---

#### Minor: 54 Files Exceed 500 Lines
**ID:** SA-016
**Location:** Various
**Issue:** 54 files exceed 500 lines, with the largest being:
- `strategy_renderer.py` (1,102 lines)
- `test_lab/renderer.py` (1,040 lines)
- `command_handlers.py` (1,032 lines)
- `race_setup_screen.py` (1,029 lines)
- `protocols.py` (987 lines)

217 files exceed 200 lines total.
**Impact:** Large files make navigation harder and increase merge conflict risk.
**Recommendation:** Continue the god-class decomposition effort (PROJ-86 through PROJ-89) which is already planned. The largest files align with the planned extraction targets.
**Effort:** Complex (already planned in PROJ-86 through PROJ-89)

---

## Positive Findings

The following areas demonstrate excellent style consistency and deserve recognition:

1. **PEP 8 naming:** 99.7% PascalCase classes, 99.95% snake_case functions. Only 4 deviations total.
2. **F-string adoption:** 100%. Zero legacy formatting patterns.
3. **No mutable defaults:** Zero functions with mutable default arguments (`[]`, `{}`, `set()`).
4. **No bare except clauses:** Zero bare `except:` blocks. Only 20 broad `except Exception:` (8% of all exception handlers).
5. **Enum naming:** 100% consistent UPPER_SNAKE_CASE members across all 18 enums.
6. **Entity ID naming:** 100% consistent `_id` suffix, zero `_uuid` usage.
7. **Module-level constant naming:** 80% UPPER_SNAKE_CASE; the 20% lowercase are mostly `logger` instances (appropriate per convention).
8. **Import separation:** 93% of files properly separate import groups.
9. **Docstring coverage:** 87% overall, with core at 94% and strategy at 92%.
10. **Single `type: ignore`:** Only 1 type suppression in the entire codebase, and it's a specific `[code]` form.

---

## Top 5 Priority Issues

| Rank | ID | Issue | Impact | Effort | Recommendation |
|------|----|-------|--------|--------|----------------|
| 1 | SA-006 | UI layer type hint coverage at 56% vs 85-95% elsewhere | High -- affects 930+ functions | Complex | Gradual annotation campaign |
| 2 | SA-001 | String quoting is 54/46 split with no convention | Medium -- visual noise, no enforceability | **Simple** (automated) | Pick double quotes, run formatter |
| 3 | SA-011 | `@property` vs `get_` used interchangeably | Medium -- inconsistent API style | Medium | Convert 55 simple `get_` wrappers to `@property` |
| 4 | SA-013 | Three event handler naming conventions | Medium -- confusing for contributors | Medium | Standardize on `process_event` + `handle_*` |
| 5 | SA-014 | Deep nesting (15 functions at depth 8+) | Medium -- readability | Medium | Extract and use dispatch tables |

**Quick wins** (high value, low effort):
- SA-001: Enforce quoting style via formatter (1 config change)
- SA-007: Enable trailing comma rule in Ruff (1 config change)
- SA-009: Run isort on 26 files (automated)
- SA-002: Rename 9 `calc_`/`compute_` methods to `calculate_` (find-and-replace)
