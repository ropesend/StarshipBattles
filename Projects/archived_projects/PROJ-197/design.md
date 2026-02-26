# PROJ-197: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Baseline
- **12,734 tests passing**, 1 skipped, 0 failures
- Previous broken regression tests (Windows bash subprocess) already fixed

### Work Area 1: Font Instantiations ✅ COMPLETE
The previous agent successfully centralized fonts from 81 to 13 instances. Remaining 13 are
confined to `scripts/visual_test_galaxy.py` (standalone script) and internal caching implementations
in `game/ui/fonts.py` and `research_renderer.py`. **No further work needed.**

### Work Area 2: ValidationResult in simulation_tests/ ⚠️ PARTIALLY COMPLETE

**Critical finding:** The 25 remaining `ValidationResult` instances are **NOT** the same class
as `game.core.validation.ValidationResult`. There are two completely separate classes:

1. **`simulation_tests/scenarios/validation.ValidationResult`** (21 usages)
   - Fields: `name`, `status` (enum PASS/FAIL/WARN/INFO), `message`, `expected`, `actual`, `p_value`, `tolerance`
   - Purpose: Statistical/exact validation of simulation test outcomes
   - Has `to_dict()` for serialization

2. **`simulation_tests/data/schema_validator.ValidationResult`** (9 usages)
   - Fields: `file_path`, `success`, `errors`
   - Purpose: JSON schema validation for test data files
   - Simple pass/fail with error messages

Neither of these is a duplicate of `game.core.validation.ValidationResult`. They are distinct
domain-specific classes with different fields, different purposes, and different APIs.

### Work Area 3: Color Tuple Consolidation ❌ INCOMPLETE

**Scope of remaining work:**
- 48 files across `game/ui/` still contain raw color tuples
- ~412 raw color tuples to consolidate (482 total minus 70 definitions in colors.py)
- Existing infrastructure: `game/ui/colors.py` (70 tuples) + `game/ui/screens/test_lab/theme.py` (97 constants)

**Top offenders:**
| File | Raw Tuples |
|------|-----------|
| `game/ui/screens/setup_renderer.py` | 40 |
| `game/ui/panels/battle_panels.py` | 38 |
| `game/ui/panels/ship_stats_renderer.py` | 31 |
| `game/ui/screens/strategy_renderer.py` | 28 |
| `game/ui/screens/test_lab/renderer.py` | 24 |
| `game/ui/panels/strategy_widgets.py` | 23 |
| `game/ui/widgets/scrollable_json_panel.py` | 20 |
| `game/ui/screens/builder/weapons_renderer.py` | 18 |
| `game/ui/panels/build_queue_portraits.py` | 17 |
| `game/ui/screens/battle_ui.py` | 15 |

**Most repeated tuples (consolidation priority):**
| Tuple | Count | Existing Constant |
|-------|-------|-------------------|
| (255, 255, 255) | 33 | `WHITE` in colors.py |
| (100, 100, 100) | 23 | `TEXT_DIM` in colors.py |
| (200, 200, 200) | 19 | None - needs new constant |
| (180, 180, 180) | 17 | None - needs new constant |
| (255, 100, 100) | 15 | `COLORS['text_error']` |
| (80, 80, 80) | 9 | `BORDER_DARK` similar |
| (255, 255, 0) | 9 | `RESEARCH_ALLOCATION` |
| (100, 255, 100) | 8 | None - needs new constant |
| (0, 0, 0) | 8 | `BLACK` in colors.py |

**Test Lab sub-issue:** `renderer.py` imports `theme.py` but still has 24 raw tuples that should
reference theme constants. Many already have matching constants defined.

## Swarm Findings Summary
Combined analysis from individual agent reports in `findings/`.

### Architecture
- Color system has two tiers: global `game/ui/colors.py` and local `test_lab/theme.py`
- The global colors.py uses flat module-level constants (good pattern)
- Test Lab theme.py was created in PROJ-196 but substitution was incomplete

### Key Patterns to Reuse
- **Module-level constants**: `game/ui/colors.py` - flat `CONSTANT_NAME = (r, g, b)` pattern
- **Per-screen themes**: `game/ui/screens/test_lab/theme.py` - grouped by purpose
- **Factory methods**: `ValidationResult.success()`, `.error()`, `.with_errors()` in game.core

### Dependencies & Risks
1. **Color tuple identity matters** - Some tuples like `(255, 100, 100)` serve different semantic purposes in different contexts (error text vs team 2 color vs ship class). Constants should be domain-specific.
2. **Test Lab theme incomplete** - 24 raw tuples in renderer.py should use existing theme constants
3. **Naming collisions** - `TEXT_MUTED` exists in both `colors.py` and `test_lab/theme.py` with different values. Need clear import patterns.

### Opportunities Discovered
- Several files use identical color patterns for buttons/panels that could share constants
- Battle-related files share many team color conventions (blue/red) that could be semantic constants

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
