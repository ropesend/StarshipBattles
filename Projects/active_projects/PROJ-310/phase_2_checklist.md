# Phase 2: Categorize causes (per archetype)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-310 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Classify each top-30 function by the kind of nesting it has. Identify which archetypes are worth refactoring and which are legitimate.

**Prerequisites:** Phase 1 complete; top-30 rankings exist.

---

## Archetype catalog (start with this set; expand as you find more)

| Archetype | What it looks like | Legitimate? |
|-----------|-------------------|-------------|
| `defensive` | `if x: if x.y: if x.y.z:` chains | NO — refactor with early-return guards or null-coalescing |
| `try-ladder` | nested `try` blocks | USUALLY NO — extract or merge handlers |
| `state-machine` | `if state == A: ... elif state == B: ... elif state == C: ...` with sub-cases | DEPENDS — table-driven dispatch usually wins, but explicit ladders are sometimes clearer |
| `parser` | mirrors nested data structure | YES — leave alone |
| `loop-stack` | nested loops over multi-level data (per-player → per-fleet → per-ship → per-component) | YES if iterating real multi-level data; refactor if each level is doing significant inline work (extract helpers) |
| `accretion` | no single root cause; organic growth of patches | NO — refactor by extraction |

---

## Tasks

### Task 2.1: Read each top-30 function and assign archetype [Medium]
**File:** `findings/archetype_assignments.md` (NEW)
**Tests:** None — investigation step.

For each top-30 function from Phase 1.2:
1. Read the function's body
2. Assign one (or sometimes two) archetypes
3. Verdict: **legitimate**, **refactor**, or **borderline**
4. Note: any obvious refactor approach (early-return, extract, table-lookup, ...)

Output format:
```markdown
## <file>::<function>
**Archetype:** defensive
**Verdict:** refactor
**Approach:** Convert to early-return guards. Each `if obj is None: return` instead of nested `if obj is not None:`
**Notes:** ~30 lines collapse to ~15
```

- [ ] Process all 30 functions; save to `findings/archetype_assignments.md`

**Notes:**

---

### Task 2.2: Look for cross-cutting patterns [Simple]
**File:** Update `findings/archetype_assignments.md`
**Tests:** None.

- [ ] Scan the assignments — do specific archetypes cluster in specific subsystems? (e.g., is `defensive` rampant in UI but rare in Simulation?)
- [ ] Are there 2-3 idiom-level fixes that would knock out many sites? (e.g., introducing a `safe_get` helper would defang every `defensive` chain)
- [ ] Add a "Cross-cutting patterns" section to `findings/archetype_assignments.md`

**Notes:**

---

## Phase Completion Checklist
- [ ] All top-30 functions assigned archetypes and verdicts
- [ ] Cross-cutting patterns identified
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3)
