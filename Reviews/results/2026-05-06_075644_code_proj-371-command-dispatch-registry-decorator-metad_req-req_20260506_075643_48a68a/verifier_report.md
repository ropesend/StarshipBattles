# Independent Verifier Report — PROJ-371 Code Review

**Verifier:** Claude (independent verifier)
**Source report:** `report.md` (OpenCode review)
**Verification scope:** 3 MIN findings + spot-check of 3 INFO claims
**Verified at:** 2026-05-05

## Verdict Table

| ID | Severity | Verdict | Notes |
|----|----------|---------|-------|
| MIN-001 | MIN | CONFIRM_REMEDIATION_REVISE | Drift confirmed; recommended fix should also touch `plan.md`, not just `decisions.md` |
| MIN-002 | MIN | CONFIRM_REMEDIATION_REVISE | Missing return type confirmed; suggested annotation is too loose — should preserve `TypeVar` |
| MIN-003 | MIN | REJECT | The `_dispatch` closure ALREADY has `-> ValidationResult`. Finding is factually wrong. |
| INFO (Focus 1) | INFO | CONFIRM | Test bodies match the claim |
| INFO (Focus 2) | INFO | CONFIRM | `test_round_trip_reset_then_seed` exists and asserts what's claimed |
| INFO (Focus 4) | INFO | CONFIRM | AST walker self-tests are real and would catch tuple regressions |

---

## MIN-001 — `__getattr__` → `_install_dispatch_forwarders` drift

**Verdict: CONFIRM_REMEDIATION_REVISE**

**Evidence:**
- `Projects/active_projects/PROJ-371/decisions.md` line 21 still says: *"`strategy_session_facade.py:186-300` (31 hand-written `dispatch_*` forwarders) collapses to `__getattr__` in Phase 2"*. Drift is real.
- `Projects/active_projects/PROJ-371/plan.md` lines 62 (Overview), 78 (Phase 2 goal: *"collapse into `__getattr__` proxying to `self._command_slice.dispatch_*`"*), 124-125 (Scope), 247-248 (Phase 2 status), 298 (Final-verification checklist: *"`strategy_session_facade.py:186-300` (31 forwarders) is gone — replaced by `__getattr__`"*). Drift exists in five places in plan.md.
- Implementation reality at `game/strategy/facade/strategy_session_facade.py:390-434`: module-level `_install_dispatch_forwarders()` iterates `command_registry.all()` and `setattr`s real bound methods on the class. The agent's report description is accurate. Inline comment at lines 400-403 explicitly justifies the deviation: *"Defining the methods on the class (not via `__getattr__`) keeps them visible to `hasattr(StrategySessionFacade, name)`, `inspect.getmembers`, and the public-API contract test"*.

**Why "REVISE":** The report's remediation only adds an entry to `decisions.md`. But `plan.md` references `__getattr__` in 5 spots (Overview line 62, Phase 2 goal, Scope, Phase 2 status, Final Verification checklist). A future archaeologist reading `plan.md` alone gets the wrong picture. The fix should:
1. Add the proposed entry to `decisions.md` documenting the deviation.
2. Update `plan.md` references (or at minimum the Final Verification checklist line 298) to match the implementation.

**Note:** The code itself has the rationale in an inline comment, so the deviation is not undocumented in the source — it is only undocumented in the project artefacts.

---

## MIN-002 — `command_spec()` missing return type at `registry.py:283`

**Verdict: CONFIRM_REMEDIATION_REVISE**

**Evidence:** Confirmed at `game/strategy/engine/commands/registry.py:283`:
```python
def command_spec(**spec_kwargs):
    """..."""
    def _wrap(handler_cls):
        handler_cls.__command_spec_kwargs__ = spec_kwargs
        return handler_cls
    return _wrap
```
No return-type annotation. Inner `_wrap` also lacks one. Repo convention (CLAUDE.md / docs/03_CONVENTIONS.md §8 / PROJ-311) requires non-dunder public functions to be annotated.

**Why "REVISE":** The report suggests `Callable[[type], type]`, which is loose: it discards the input/output identity (the decorator returns the same class it was given). A more faithful annotation preserves that:

```python
from typing import TypeVar
H = TypeVar("H", bound=type)
def command_spec(**spec_kwargs) -> Callable[[H], H]:
    def _wrap(handler_cls: H) -> H:
        ...
        return handler_cls
    return _wrap
```

`type[ICommandHandler]` would be ideal, but the decorator is also applied to plain marker classes in the seeding test (`Marker = type("Marker", (object,), {"X": 1})`), so a generic `bound=type` is the practical floor. The fix is roughly the same edit cost as the report's suggestion, but more accurate.

---

## MIN-003 — `_dispatch` closure missing `-> ValidationResult`

**Verdict: REJECT**

**Evidence:** Read `game/strategy/facade/strategy_session_facade.py:415`:

```python
def _dispatch(self, **kwargs) -> ValidationResult:
    return getattr(self._command_slice, helper_name)(**kwargs)
```

The annotation is **already present**. The finding is factually incorrect. The agent likely either misread the file or read an earlier revision.

**Sanity check on the underlying type contract** (in case the finding is salvageable as a different concern):
- `self._command_slice` is `CommandDispatchSlice`. Its `__getattr__` returns a closure that calls `self._handle_command(command_class(**kwargs))`.
- `CommandDispatchSlice.__init__` types `_handle_command: Callable[["Command"], "ValidationResult"]` (line 33).
- So `getattr(self._command_slice, helper_name)(**kwargs)` does return `ValidationResult` at runtime, and `-> ValidationResult` is correct.

The annotation is correct AND already present. Nothing to do.

---

## INFO Spot Checks

- **Focus Area 1 (decorator-as-metadata-only):** CONFIRM. `tests/unit/strategy/engine/test_command_registry_seeding.py:85-100` exists, snapshots `_specs` before/after `importlib.import_module("game.strategy.engine.handlers.build")`, and asserts equality. The autouse fixture at lines 35-43 also snapshots/restores. The decorator at `registry.py:317-319` does `handler_cls.__command_spec_kwargs__ = spec_kwargs; return handler_cls` — no `register()` call.
- **Focus Area 2 (round-trip reset):** CONFIRM. `test_round_trip_reset_then_seed` at line 107-112 captures `original_count`, asserts it equals 35, calls `reset_command_registry()`, asserts `len == original_count`. `reset_command_registry()` at `registry.py:362-369` does `_specs.clear()` then `seed_default_commands(...)`. Matches the report's description.
- **Focus Area 4 (AST walker):** CONFIRM. `test_no_specs_tuple_literal.py` lines 77-93: synthetic positive (a `COMMAND_SPECS = (CommandSpec(...),)` source string) is flagged True; unrelated tuple is flagged False; `register(registry.register(CommandSpec(...)))` (Call-not-in-Tuple) is flagged False. Walker logic at lines 27-44 matches: top-level `Assign` → RHS `Tuple` → element is `Call(func=Name(id='CommandSpec'))`.

---

## Recommended Actions for Claude

**Do now (small, mechanical, in scope of this PR):**

1. **MIN-001 (revised)** — Add the proposed `decisions.md` entry **and** update `plan.md` to match implementation reality. Minimum: fix the Final Verification checklist line 298 (`replaced by __getattr__` → `replaced by class-level dispatch forwarders installed via _install_dispatch_forwarders`). Optional but cheap: update lines 62, 78, 125, 248 with the same correction. Total change ~5 lines.
2. **MIN-002 (revised)** — Annotate `command_spec` with `Callable[[H], H]` using a `TypeVar("H", bound=type)`, not the report's looser `Callable[[type], type]`. Annotate the inner `_wrap` too. ~3 LOC.

**Do not act on:**

3. **MIN-003** — REJECT. The annotation is already present at line 415. No edit needed.

**Optional follow-up (out of scope for this fix-up):** The slice's `__getattr__`-resolved `_dispatch` closure at `command_dispatch_slice.py:98` lacks `-> ValidationResult`. This is the closure MIN-003 may have been pointing at — in the **slice**, not the facade. If the user wants annotation parity across both layers, add it there too. But this was not in the report's findings as written, so flag as discretionary.
