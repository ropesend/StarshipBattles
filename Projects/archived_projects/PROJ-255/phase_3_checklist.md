# Phase 3: Component Definition Flyweight (CONDITIONAL)

**Objective:** Share immutable definition data across Component instances via flyweight pattern, reserving per-instance state for mutable runtime fields only.

**IMPORTANT:** This phase is CONDITIONAL. Only proceed if memory profiling of fleet-scale scenarios shows significant pressure from Component deep-copies. PROJ-241 (Component God Class Decomposition) already extracted 5 delegate classes, significantly reducing the per-instance footprint.

---

## Gate Check

Before starting this phase:
- [ ] Profile memory usage in a fleet-scale scenario (50+ ships, 20+ components each)
- [ ] Measure per-Component memory footprint (deep-copy vs shared definition)
- [ ] If deep-copy overhead is < 10% of total memory, SKIP this phase — the optimization isn't worth the complexity

---

## Design (if proceeding)

1. Create `ComponentDefinition` class — immutable, shared, keyed by component ID
2. `ComponentDefinitionCache` holds one `ComponentDefinition` per unique component type
3. `Component.__init__` receives a `ComponentDefinition` reference instead of deep-copying data
4. Per-instance state (current_hp, is_active, modifier values) stays on Component
5. `clone()` shares the definition, copies only mutable state

---

## Checklist (if proceeding)

### Tests First
- [ ] Write test: two Components with same type share the same `ComponentDefinition` instance (identity check)
- [ ] Write test: modifying one Component's runtime state doesn't affect another sharing the definition
- [ ] Write test: `clone()` produces independent runtime state but shared definition
- [ ] Run tests — confirm they fail

### Implementation
- [ ] Create `ComponentDefinition` frozen dataclass with immutable definition fields
- [ ] Create `ComponentDefinitionCache` (dict-based, keyed by component ID)
- [ ] Update `Component.__init__` to accept `ComponentDefinition` reference
- [ ] Move immutable fields (base_stats, ability_definitions, formulas) to `ComponentDefinition`
- [ ] Keep mutable fields (current_hp, is_active, modifier state) on Component instance
- [ ] Update `clone()` to share definition, copy mutable state
- [ ] Remove `copy.deepcopy(data)` call from Component construction
- [ ] Run tests — confirm they pass

### Verification
- [ ] Run full test suite — no regressions
- [ ] Run simulation tests — all pass
- [ ] Re-profile: measure memory improvement vs baseline
