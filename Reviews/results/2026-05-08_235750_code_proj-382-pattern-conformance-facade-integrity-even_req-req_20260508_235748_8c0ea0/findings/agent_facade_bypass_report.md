# PROJ-382 Pattern #5 Facade Bypass — Conformance Review

**Review scope:** Static-guard effectiveness, `get_registries()` on facade, `BuildQueuePortraitLoader`/`portrait_session` scrutiny.
**Date:** 2026-05-08

---

### FINDING-01: CRITICAL — Static guard has syntactic blind spot for `self._session.handle_command(...)`

**File:** `tests/static_guards/test_facade_bypass_guard.py:58-68`
**Evidence:**
```python
def _is_session_handle_command(node: ast.Call) -> bool:
    """Match ``<expr>.session.handle_command(...)`` calls."""
    ...
    return inner.attr == "session"
```
The guard matches the literal attribute name `session`. It does **not** catch `self._session.handle_command(...)` because the private attribute name `_session` does not equal `"session"`.
**Assessment:** The guard was designed to catch the original violation pattern (`<expr>.session.handle_command(...)`) where `session` was a public attribute name on `StrategyScreen` prior to Phase 1. After Phase 1 privatized `self.session` → `self._session`, code inside `strategy_screen.py` or any file that acquires a reference to the private `_session` could call `self._session.handle_command(...)` or `screen._session.handle_command(...)` and the static guard would **decline to fire**. The guard fails on the private-attribute form of the same violation.
**Recommendation:** Extend `_is_session_handle_command` to also match `_session` as the attribute name:
```python
return inner.attr in ("session", "_session")
```
Additionally, add a dedicated check for `self._session.handle_command(...)` inside `game/ui/screens/strategy_screen.py` since it's the one file that owns `_session` as a private attr.

---

### FINDING-02: MAJOR — `session` property setter allows reassignment without facade rebuild

**File:** `game/ui/screens/strategy_screen.py:231-234`
**Evidence:**
```python
@session.setter
def session(self, value: Any) -> None:
    """PROJ-382 Phase 1: write-through setter for test session swap."""
    self._session = value
```
The setter updates `self._session` but does **not** rebuild `self._facade` (constructed at line 93 with the original session). After `screen.session = new_session`:
- `screen.facade.handle_command(...)` dispatches through the **old** session (split-brain).
- `screen.galaxy`, `screen.empires`, etc. read from the **new** session.
**Assessment:** The docstring says "test session swap" — this is legitimate for test infrastructure but the setter is a public writable property with no guardrail. A production code bug or future developer mistake could call this setter (or an attribute-reassignment via `setattr`) producing a silent split-brain scenario where commands execute against the wrong `GameSession`. The static guard cannot prevent the SET operation — it only catches `.session.handle_command(...)` reads.
**Recommendation:** Mark the setter with a deprecation warning or convert to `_internal_test_set_session(value)` method not accessible as a property. Alternatively, have the setter rebuild the facade:
```python
@session.setter
def session(self, value: Any) -> None:
    self._session = value
    self._facade = StrategySessionFacade(value)
```

---

### FINDING-03: MAJOR — `portrait_session=` kwarg is a renamed full-session backdoor

**File:** `game/ui/screens/build_queue_screen.py:62,96,121` → `game/ui/panels/build_queue_portraits.py:77-86,100-102`
**Evidence:**
```python
# build_queue_screen.py:62
portrait_session=None,  # keyword-only

# build_queue_screen.py:96
self._portrait_session = portrait_session

# build_queue_portraits.py:77-86
def __init__(self, design_library: DesignLibrary, session):
    self.session = session  # stored as `session` internally!

# build_queue_portraits.py:100-102
if hasattr(self.session, 'active_empire') and hasattr(self.session.active_empire, 'empire_theme_id'):
    theme = self.session.active_empire.empire_theme_id
```
The actual data needed is a single string: `empire_theme_id`. Instead, the entire `GameSession` object is passed, renamed `portrait_session` at the call site but stored as `self.session` inside the loader class. The loader reaches through the session to `active_empire.empire_theme_id`.
**Assessment:** This is a **backdoor**, not a narrow handle. The entire `GameSession` (with all its mutation methods, `handle_command`, `galaxy`, `registries`, etc.) is available to `BuildQueuePortraitLoader` and any code that receives it. The `portrait_session` naming is misleading — it suggests a narrow scope that does not exist. The class itself still names it `self.session`, creating naming confusion with the facade's private `_session`. However, this is **not** a Pattern #36 violation (Re-Export Shim) — it's a straight Pattern #5 violation (facade bypass) under a cosmetic rename. The static guard does NOT catch this because: (a) the kwarg is named `portrait_session`, not `session` (evades the `_has_session_kwarg` check), and (b) `BuildQueuePortraitLoader` accesses `session.active_empire.empire_theme_id`, not `session.handle_command(...)` (evades the `_is_session_handle_command` check).
**Recommendation:** Replace with a narrow value type — pass `empire_theme_id: str` directly. Remove `session` parameter from `BuildQueuePortraitLoader.__init__`. Change `load_design_portrait` to accept `theme_id: str` parameter instead of reaching into session. This is acknowledged as "deferred U2 cleanup" in comments but should be prioritized as it perpetuates the facade-bypass architecture.

---

### FINDING-04: MAJOR — `BuildQueuePanelFactory` receives raw session and reaches into `registries`, `current_empire`, `turn`

**File:** `game/ui/screens/build_queue_panel_factory.py:96,121,233,543,556`
**Evidence:**
```python
# Constructor stores raw session (line 96, 121)
def __init__(self, ..., session, ...):
    self.session = session

# Accesses registries directly (line 233)
production_rates=compute_planet_production(self.build_context, self.session.registries)

# Accesses current_empire directly (line 543)
empire = getattr(self.session, 'current_empire', None)

# Accesses turn directly (line 556)
turn_number = getattr(self.session, 'turn', 0)
```
**Assessment:** Three distinct read paths bypass the facade to reach into `GameSession`:
1. `self.session.registries` — could use `facade.get_registries()` (exists, canonical)
2. `getattr(self.session, 'current_empire', None)` — could use facade DTO
3. `getattr(self.session, 'turn', 0)` — could use `facade.get_turn_number()` (exists)

The factory receives both a `session` parameter (named `session`, not `portrait_session`) AND a `facade` parameter (line 101). It uses the facade for the per-species `ColonyDemographicView` but bypasses it for registries, empire, and turn. The `session` parameter is passed through from `build_queue_screen.py:200` which receives it from `_portrait_session`.
**Recommendation:** Remove the `session` parameter from `BuildQueuePanelFactory.__init__`. Route all three reads through the already-injected `facade` parameter. The facade already has `get_registries()` and `get_turn_number()`; `current_empire` needs a facade DTO or a new `get_current_empire_dto()` query.

---

### FINDING-05: MAJOR — `StrategyBuildQueueManager` accesses session for domain data through screen property

**File:** `game/ui/screens/strategy_build_queue_manager.py:111,129,148,155,255,279`
**Evidence:**
```python
# Line 111: passes full session as portrait_session
portrait_session=self._screen.session,

# Line 129: passes full session to BuildQueuePortraitLoader
screen.portrait_loader = BuildQueuePortraitLoader(design_library, self._screen.session)

# Lines 148, 255, 279: reads save_path from session
savegame_path = self._screen.session.save_path

# Line 155: reaches through session to galaxy for system lookup
parent_sys = self._screen.session.galaxy.get_system_of_planet(planet)
```
**Assessment:** `StrategyBuildQueueManager` is the primary composition root for `BuildQueueScreen`. It accesses `self._screen.session` (the `StrategyScreen.session` property) in five places to extract `save_path`, `galaxy`, and the session object itself (for forwarding as `portrait_session`). These are all read-accesses, not `handle_command` dispatches, so the static guard does not flag them. However:
- `self._screen.session.galaxy.get_system_of_planet(planet)` bypasses the facade's `get_system_at_hex()` / `get_system_near_hex()` queries
- `self._screen.session.save_path` could be `facade.get_save_path()` (exists)
- The session-forwarding at lines 111/129 enables findings 03 and 04

**Recommendation:** Route `save_path` through `facade.get_save_path()`. Route `galaxy.get_system_of_planet()` through the facade's system query surface (or keep `self._screen.galaxy` which exists on the screen as a property). Eliminate the passing of the full session object into `BuildQueueScreen` and `BuildQueuePortraitLoader` (see finding-03).

---

### FINDING-06: MINOR — `session` property on `StrategyScreen` is an "audit-residue delegate" that masks the true access pattern

**File:** `game/ui/screens/strategy_screen.py:215-229`
**Evidence:**
```python
@property
def session(self) -> Any:
    """Audit-residue delegate for legacy ``c.scene.session.<x>`` reads.
    ...
    """
    return self._session
```
**Assessment:** The docstring acknowledges this as "audit-residue" for deferred UI migrations (U1/U2/U3). While the static guard catches any new `<expr>.session.handle_command(...)` patterns, existing read-accesses through this property (e.g., `c.scene.session.save_path`, `c.scene.session.galaxy`, `c.scene.session.active_empire`) are invisible to the guard. The property naming creates a false sense of compliance — callers that read `.session.galaxy` or `.session.registries` are bypassing the facade just as much as callers that called `.session.handle_command(...)`, but only the latter is blocked.
**Recommendation:** Add a second static guard (or extend the existing one) to flag `<expr>.session.<anything>` access patterns in `game/ui/` — with a per-file allowlist for the composition root `strategy_screen.py` and the `strategy_build_queue_manager.py` (which will shrink as findings 03-05 are addressed). This is a lower priority than fixing the active bypasses in findings 03-05.

---

### FINDING-07: MINOR — `BuildQueuePortraitLoader` reuses name `self.session` creating namespace collision with facade's private `_session`

**File:** `game/ui/panels/build_queue_portraits.py:86`
**Evidence:**
```python
class BuildQueuePortraitLoader:
    def __init__(self, design_library: DesignLibrary, session):
        self.session = session  # <-- stored under attr name 'session'
```
**Assessment:** Beyond the architectural problem (finding-03), there's a code-clarity issue: `BuildQueuePortraitLoader` stores the session under the public attribute name `session`. This is the same name the static guard monitors for `.session.handle_command(...)`. Any code that has a reference to the portrait loader could, in principle, call `loader.session.handle_command(...)` and the guard would catch it. But more importantly, the name `session` on a class that claims to only need `empire_theme_id` is misleading — it advertises availability of the full session API to any developer reading or maintaining this code.
**Recommendation:** Once finding-03 is resolved (narrow type), this resolves automatically. In the interim, rename the attribute to `_session` to reflect its private, transitional nature.

---

### FINDING-08: INFO — `get_registries()` on `StrategySessionFacade` is canonical and correct

**File:** `game/strategy/facade/strategy_session_facade.py:367-375`
**Evidence:**
```python
def get_registries(self) -> "GameRegistries":
    """Get the session-scoped game registries (PROJ-382 Phase 1).
    ...
    """
    return self._session.registries
```
**Assessment:** This is a legitimate, narrow facade method. It returns `GameRegistries` (an immutable DI container implementing `IRegistryProvider`, per docs/02_PATTERNS.md Pattern #4 line 122: "GameRegistries is a frozen DI container"). The docstring correctly notes "Read-only access — callers must not mutate the returned object." The method is used by `BuildQueueScreen` at lines 203, 228, 286, 512 and by `EmpireBuildQueueWindow` at line 189 — all correct. No issues.

---

### FINDING-09: INFO — Static guard has correct coverage for `session=` kwarg but needs expansion

**File:** `tests/static_guards/test_facade_bypass_guard.py:115-143`
**Evidence:** The guard checks `BuildQueueScreen` and `EmpireBuildQueueWindow` constructors for a `session=` kwarg.
**Assessment:** The guard correctly blocks reintroduction of `session=` to these two constructors. However, `BuildQueuePanelFactory` also accepts `session` as a parameter name (`build_queue_panel_factory.py:96`) — this is not guarded. The guard's `GUARDED_CONSTRUCTORS` set should be expanded to include `BuildQueuePanelFactory` once finding-04 is addressed. Additionally, the `portrait_session` kwarg passes through unchecked (finding-03).
**Recommendation:** After resolving findings 03 and 04, add `BuildQueuePanelFactory` to `GUARDED_CONSTRUCTORS`. Consider a generic check: flag any `session` parameter (positional or kwarg) to ANY constructor in `game/ui/` — with a per-file allowlist for test files and composition roots.

---

## Summary

| Severity | Count | Findings |
|----------|-------|----------|
| CRITICAL | 1 | FINDING-01: Guard blind spot on `_session` attribute name |
| MAJOR    | 4 | FINDING-02: Setter split-brain, FINDING-03: `portrait_session` backdoor, FINDING-04: Panel factory bypass, FINDING-05: Manager session reads |
| MINOR    | 2 | FINDING-06: "Audit-residue" property, FINDING-07: `self.session` naming |
| INFO     | 2 | FINDING-08: `get_registries()` is correct, FINDING-09: Guard expansion needed |

**Total: 9 findings**

**Bottom line:** The static guard correctly closes the primary escape hatch (`<expr>.session.handle_command(...)`) but has a CRITICAL syntactic blind spot on private-attribute access (`._session.handle_command(...)`) and cannot catch the broader category of non-dispatch session reads. The `portrait_session` kwarg is a renamed full-session backdoor that evades all guard checks; it needs to be replaced with a narrow value type (`empire_theme_id: str`). The `BuildQueuePanelFactory` and `StrategyBuildQueueManager` continue to bypass the facade for reads (registries, turn, current_empire, galaxy) despite the facade offering equivalent methods.
