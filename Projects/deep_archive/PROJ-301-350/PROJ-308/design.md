# PROJ-308: Design Document

## Initial Analysis

CLAUDE.md "Long-Term Quality" already says: "Specific exceptions over broad catches." But there are 24 broad `except Exception:` clauses in production code. Most are uncommented — a future maintainer reading them has no way to tell whether the broad catch is intentional (e.g., calling third-party code that can throw anything) or laziness (e.g., the author didn't want to think about error modes).

The 2 already-commented sites give a model:
- [game/ui/services/tkinter_utils.py:100](game/ui/services/tkinter_utils.py#L100): `except Exception:  # Intentional: destroy may fail if already destroyed`
- [game/ui/screens/workshop_data_reloader.py:23](game/ui/screens/workshop_data_reloader.py#L23): `except Exception:  # Intentional broad catch: Tkinter init is platform-dependent`

Both communicate WHY. Future-you can tell instantly that these are deliberate, and what the trigger condition is.

## Triage Methodology

For each of the 24 sites, the implementer makes ONE of three choices:

### Choice 1 — NARROW
The catch is broad because the author didn't enumerate the real exception types. Replace with the actual types.
- Example: `except Exception:` around `json.loads(...)` → `except (json.JSONDecodeError, TypeError):`
- Example: `except Exception:` around file open → `except OSError:`

**When to choose this:** the wrapped block has a small, knowable set of failure modes.

### Choice 2 — JUSTIFY
The catch is genuinely broad because the wrapped block calls into code that can fail in many ways and we want to handle all of them. Add a comment explaining why.
- Format: `except Exception:  # Intentional broad catch: <reason>`
- Reason should answer: what failures are we expecting, and why is fire-and-forget the right response?
- Examples of legitimate broad catches:
  - **Third-party callback dispatch**: handler raises something we can't predict; logging-and-continuing is correct
  - **Platform-dependent init** (Tkinter, audio, GPU): can fail with platform-specific exceptions we don't enumerate
  - **Defensive UI updates**: a failed UI refresh shouldn't crash the game session
  - **Telemetry / event emission**: instrumentation must never break the host

**When to choose this:** the wrapped block legitimately calls into "anything can happen" territory.

### Choice 3 — DELETE
The catch is masking real bugs. Remove the try/except and let the exception propagate.
- Example: `except Exception:` around code we wrote ourselves with a known contract; the catch was added speculatively

**When to choose this:** the wrapped block is internal code with a clear contract; the catch hides assertion-fail-class bugs.

## Architecture

### Pattern: System Migration Policy
Per CLAUDE.md: "DO NOT suppress errors or default behavior — understand why the error occurs and fix the cause." A broad catch without a justification comment is exactly the kind of suppression Rule 3 (Clean-Sheet Design) flags. By the end of this project, every remaining broad catch has a justification — anyone reading future code can tell the difference between intentional handling and silent suppression.

### Why a comment, not a custom exception class
- Lower friction: a one-line comment is easier to write, review, and maintain than introducing custom exceptions
- Lower test burden: no new types to test
- Established pattern in this codebase (the 2 existing comments use this format)

### Convention Format
```python
# Bad — uncommented broad catch:
try:
    do_thing()
except Exception:
    pass

# Good — narrowed:
try:
    do_thing()
except (ValueError, KeyError):
    pass

# Good — broad catch with justification:
try:
    do_thing()
except Exception:  # Intentional broad catch: callback may raise anything from third-party plugin
    logger.warning("plugin callback failed", exc_info=True)
```

The justification line MUST appear within the same line as the `except` clause OR on the line immediately above it.

## Dependencies & Risks

1. **Risk: narrowing breaks production by missing an actual exception type.**
   If the real production failure mode includes an exception type the implementer didn't anticipate, narrowing causes a previously-handled failure to crash.
   **Mitigation:** before narrowing, search the file's recent commit history for any context about which exceptions were actually being seen. Run targeted tests after each narrow. If unsure, choose Choice 2 (justify) instead — broader and safer than mis-narrowing.

2. **Risk: deletion (Choice 3) crashes the game on what was a real-but-rare failure.**
   The catch may have been silently absorbing a failure mode the author dismissed.
   **Mitigation:** Choice 3 should be rare. If unsure, Choice 2 is safer.

3. **Risk: maintainer rubber-stamps every site with "broad catch — legacy" comments.**
   That defeats the purpose: a meaningless justification is worse than none (it implies the author thought about it when they didn't).
   **Mitigation:** Phase 1 is per-site triage with Notes. The implementer must write a SPECIFIC reason, not boilerplate. Phase-3 review verifies comment quality.

## Key Patterns to Reuse
- **PROJ-297 Phase 4 bare-except cleanup** — same shape as this project, smaller scale (2 sites). Used Choice 1 (narrow) for both. Read those notes for migration cadence.

## Opportunities Discovered
- A small `Tools/check_broad_except.py` AST script could detect uncommented `except Exception:` clauses and fail CI. Out of scope for this project; capture as follow-up.
- `pylint`/`flake8` rule `W0703` (catching too general exception) — could enforce in CI. Out of scope; capture as follow-up.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
