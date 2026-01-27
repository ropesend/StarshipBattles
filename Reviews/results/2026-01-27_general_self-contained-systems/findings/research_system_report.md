# Research System Analysis Report

## Summary
- **Total issues found:** 3
- **Critical:** 1, **Major:** 1, **Minor:** 1, **Info:** 0

---

## LARGEST ISSUE

### CRITICAL: Control Panel State Mutation on Reset

**ID:** RES-01

**Location:** `game/research/ui/research_scene.py:343-349` (in `_on_reset()` method)

**Issue:**
The reset flow directly assigns references to the control panel's instance variables:
```python
self.control_panel.tracker = self.tracker
self.control_panel.tech_tree = self.tech_tree
```

This bypasses the control panel's constructor and creates hidden state dependencies.

**Impact on Maintenance/Extensibility:**
1. **State Synchronization Risk**: Control panel's state assumptions are violated
2. **Reference Coupling**: Control panel tightly coupled to external state mutation
3. **Extensibility Barrier**: Adding initialization logic requires updates in multiple locations
4. **Documentation Mismatch**: Constructor interface is bypassed on reset

**Recommendation:**
Create a `reset()` method in ResearchControlPanel that takes tracker and tech_tree as parameters, or create a factory method for reinitializing the panel.

**Effort:** Simple (method extraction)

---

## Secondary Findings

### MAJOR: Depth Cache Not Invalidated on Requirements Resolution

**ID:** RES-02

**Location:** `game/research/data/tech_tree.py:95-145`

**Issue:**
The `_depth_cache` is populated during `calculate_depth()` calls, but `resolve_all_requirements()` doesn't clear the cache.

**Impact:**
- If future features add dynamic tree structure modifications, depth calculations would become stale
- Cache behavior is implicit

**Recommendation:**
Add `self._depth_cache.clear()` to the end of `resolve_all_requirements()`.

**Effort:** Simple

---

### MINOR: Tightly Coupled Status Logic in Control Panel

**ID:** RES-03

**Location:** `game/research/ui/research_controls.py:283-310`

**Issue:**
Control panel calls `node.get_status()` and performs business logic calculations directly, rather than receiving pre-computed state from the scene.

**Impact:**
- Node status determination logic is split between layers
- Testing control panel requires testing research logic too

**Recommendation:**
Pass pre-computed node status from ResearchTreeScene to control panel.

**Effort:** Medium

---

## Assessment

**System Health: Good with Maintenance Concerns**

The research system demonstrates solid architectural layering (data/systems/ui) and clear separation of concerns. The core simulation logic (leaky bucket algorithm) is well-isolated and mathematically clean.

However, the system has a **state mutation pattern** that creates maintenance debt. The most critical issue (RES-01) is the `_on_reset()` method bypassing proper initialization.

**Recommendations:**
1. Extract proper initialization/reset methods in ResearchControlPanel
2. Clear the depth cache on requirements resolution
3. Move status computations into the service/scene layer

**Overall:** This is the cleanest subsystem in the codebase. Issues are minor relative to other systems.
