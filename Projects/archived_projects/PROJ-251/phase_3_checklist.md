# Phase 3: DesignLibrary Error Discrimination

**Objective:** Make `DesignLibrary` methods distinguish between failure modes (file missing, file corrupt, schema invalid, permission denied) so callers can react appropriately.

**Key Principle:** DesignLibrary handles user-created content on the filesystem. It should NOT crash the game on corrupt designs — but the caller deserves to know WHY a load failed, not just "None".

**Depends On:** Phase 1 (new exception types)
**Independent Of:** Phases 4-6 (can be done in parallel with turn engine work)

---

## Problem Statement

`DesignLibrary.load_design_data()` catches `JSONDecodeError`, `(PermissionError, OSError)`, and `(KeyError, TypeError, ValueError, AttributeError)` — all returning `None`. The caller (Ship Builder UI, command handlers) cannot distinguish:
- Design file doesn't exist (normal — user hasn't saved one yet)
- Design file exists but JSON is corrupt (actionable — tell user to delete/re-save)
- Design file exists, JSON valid, but schema is wrong (actionable — version mismatch or manual edit)
- Permission denied (actionable — file system issue)

The write methods (`save_design`, `mark_obsolete`, `increment_built_count`) already return `(bool, str)` tuples with descriptive messages — these are adequate and don't need changing.

## Design

### Approach: Typed Return via Result Enum + Optional Data

Replace `load_design_data() -> Optional[dict]` with a result that carries the failure reason.

**Option A: Return `(data_or_none, error_or_none)` tuple**
Simple but stringly-typed. Caller has to check both.

**Option B: Return a `DesignLoadResult` dataclass**
Clean, self-documenting. Carries data on success, error category + message on failure.

**Option C: Raise specific exceptions, let caller catch**
Matches project patterns for critical data. But design loading is non-critical; exceptions would force every caller to wrap in try/except.

**Decision: Option B — `DesignLoadResult` dataclass**

```python
@dataclass(frozen=True)
class DesignLoadResult:
    """Result of attempting to load a ship design."""
    data: Optional[dict] = None          # The design dict, if successful
    error: Optional[str] = None          # Human-readable error message
    error_type: Optional[str] = None     # Category: "not_found", "corrupt_json", 
                                         #   "invalid_schema", "permission_denied", "io_error"
    
    @property
    def success(self) -> bool:
        return self.data is not None
    
    @staticmethod
    def ok(data: dict) -> 'DesignLoadResult': ...
    
    @staticmethod
    def not_found(design_id: str) -> 'DesignLoadResult': ...
    
    @staticmethod
    def corrupt(design_id: str, detail: str) -> 'DesignLoadResult': ...
    
    @staticmethod  
    def permission_denied(design_id: str, detail: str) -> 'DesignLoadResult': ...
```

### Caller Migration

Callers currently do:
```python
data = library.load_design_data(design_id)
if data is None:
    return  # Can't load, give up silently
```

After:
```python
result = library.load_design_data(design_id)
if not result.success:
    if result.error_type == "not_found":
        pass  # Normal — no design saved yet
    else:
        logger.warning(f"Design '{design_id}': {result.error}")
    return
data = result.data
```

### scan_designs() — Keep Resilient

`scan_designs()` iterates all design files on disk. A single corrupt file should NOT prevent scanning the rest. This method keeps its per-file try/except but logs at `logger.warning` (not `logger.error`) for corrupt files, since individual corrupt designs are expected in a user-facing filesystem.

No change to `scan_designs()` exception handling.

---

## Checklist

### Tests First (TDD)

#### DesignLoadResult
- [ ] Write test: `DesignLoadResult.ok(data)` has `success=True`, `data=data`, `error=None`
- [ ] Write test: `DesignLoadResult.not_found(id)` has `success=False`, `error_type="not_found"`
- [ ] Write test: `DesignLoadResult.corrupt(id, detail)` has `success=False`, `error_type="corrupt_json"`
- [ ] Write test: `DesignLoadResult.permission_denied(id, detail)` has `success=False`, `error_type="permission_denied"`
- [ ] Write test: `DesignLoadResult` is frozen (immutable)

#### load_design_data() Error Discrimination
- [ ] Write test: load nonexistent design returns `not_found` result
- [ ] Write test: load design with corrupt JSON returns `corrupt_json` result with detail
- [ ] Write test: load design with valid JSON but missing required schema fields returns `invalid_schema` result
- [ ] Write test: load design with permission error returns `permission_denied` result (mock `open`)
- [ ] Write test: load valid design returns `ok` result with correct data
- [ ] Write test: all failure results include the design_id in the error message

- [ ] Run tests — confirm they fail

### Implementation

#### DesignLoadResult dataclass
- [ ] Create `DesignLoadResult` in `game/strategy/systems/design_library.py` (co-located, not a separate file)
- [ ] Implement factory methods: `ok()`, `not_found()`, `corrupt()`, `invalid_schema()`, `permission_denied()`, `io_error()`

#### load_design_data() Rewrite
- [ ] Change return type from `Optional[dict]` to `DesignLoadResult`
- [ ] Check file existence first — return `not_found()` if missing (no exception needed)
- [ ] Catch `JSONDecodeError` — return `corrupt("corrupt_json", detail)`
- [ ] Catch `(PermissionError)` — return `permission_denied(detail)`
- [ ] Catch `(OSError)` — return `io_error(detail)`
- [ ] After successful JSON load, validate required schema keys — return `invalid_schema(detail)` if missing
- [ ] Remove the broad `(KeyError, TypeError, ValueError, AttributeError)` catch — schema validation handles this explicitly
- [ ] Log at appropriate levels: `debug` for not_found, `warning` for corrupt/invalid, `error` for permission/IO

#### Caller Updates
- [ ] Find all callers of `load_design_data()` (grep for the method name)
- [ ] Update each caller to use `result.success` / `result.data` instead of `is None` check
- [ ] For callers that only need data-or-nothing (e.g., validation helpers): can use `result.data` directly (None on failure, same as before)
- [ ] For callers that can surface errors to UI (e.g., command handlers): use `result.error` for user message

### Verification
- [ ] Run design library tests — all pass
- [ ] Run full test suite — no regressions
- [ ] Verify `scan_designs()` still works (it calls `DesignMetadata.from_design_file`, not `load_design_data`)
- [ ] Verify `save_design()`, `mark_obsolete()`, `increment_built_count()` unchanged
