# PROJ-182: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source
- **Origin:** Post-refactor audit of PROJ-176 (Missing Abstractions & Duplication Elimination)
- **Audit Date:** 2026-02-24
- **Independent Review:** 5-agent swarm verified all audit findings

## Initial Analysis

### Independent Code Review Findings

A 5-agent swarm independently verified the PROJ-176 audit report. Summary:

**Finding 1: Dead Code — `game/strategy/validation/primitives.py`** — CONFIRMED
- File defines 3 functions: `require_fleet`, `require_planet`, `require_system_at_location`
- Zero imports from any production code in the codebase
- `game/strategy/validation/__init__.py` does NOT export anything from primitives
- All 3 validators (`ColonizeValidator`, `TransferValidator`, `SuperweaponValidator`) use inline logic or `BaseCommandHandler._resolve_*` methods instead
- Test file `tests/unit/strategy/validation/test_primitives.py` exists (20 test methods) but only tests the dead code
- **Root cause:** Phase 2's `BaseCommandHandler` mixin made the Phase 1 primitives redundant. The handler resolution approach is architecturally superior.

**Finding 2: Method Naming Deviation (`errors` → `with_errors`)** — CONFIRMED, NOT ACTIONABLE
- Design specified `@staticmethod def errors(messages)`, implementation uses `with_errors(messages)`
- Only 4 call sites use `with_errors` (3 tests + 1 docstring example)
- The other two methods (`success()`, `error()`) match the spec
- **Decision:** Keep as-is. Renaming would be churn for 4 call sites.

**Finding 3: Outdated Docstrings** — CONFIRMED + EXPANDED
The audit found 2 locations. Independent review found **4 locations**:
1. `game/core/validation.py:72` — Shows `ValidationResult(is_valid=False, errors=[...])`
2. `game/core/validation.py:81` — Shows `ValidationResult()`
3. `game/simulation/validation/base.py:30` — Shows `ValidationResult(True)`
4. `docs/architecture/PATTERNS.md:251-307` — **6 instances** of deprecated patterns PLUS stale field name (`success: bool` should be `is_valid: bool`)

**Finding 4: CrewRequired `fallback_keys`** — CONFIRMED, NOT ACTIONABLE
- `fallback_keys=('amount',)` works correctly
- No JSON data uses `"amount"` key format (all use numeric literals or formulas)
- It's defensive code that causes no harm. Has dedicated test coverage.
- **Decision:** Keep as-is.

**Finding 5: Core Abstractions Verified** — ALL CORRECT
- BaseCommandHandler: 19/19 handlers migrated, zero inline resolution remaining
- SimpleMultiplierAbility: 7/7 ability classes migrated
- SuperweaponMarker: 6/6 superweapon classes migrated

## Swarm Findings Summary

### Architecture
No architectural changes needed. This project is purely cleanup:
- Deleting dead code (2 files)
- Updating documentation strings (3 files)

### Key Patterns to Reuse
- **Factory method pattern**: `ValidationResult.success()`, `.error(msg)`, `.with_errors(msgs)` — these are the canonical patterns all examples should teach

### Dependencies & Risks
1. **Test count change** — Deleting `test_primitives.py` removes ~20 tests. This is expected and correct (testing dead code is waste). Risk: VERY LOW.
2. **Documentation accuracy** — PATTERNS.md snippet is doubly stale (wrong field name + wrong constructor pattern). Must update both.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
