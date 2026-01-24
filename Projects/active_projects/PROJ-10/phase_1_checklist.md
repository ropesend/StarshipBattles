# Phase 1: Security Vulnerabilities

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-10 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Address critical security vulnerabilities that could be exploited
**Priority:** CRITICAL - Immediate

---

## Tasks

### Task 1.1: MOD-SIM-04 - Replace eval() in Formula System [Medium]
**File:** `game/simulation/formula_system.py:28-31`
**Tests:** `pytest tests/unit/simulation/test_formula_system.py`

**Issue:** Uses `eval()` for formula evaluation. While sandboxed with `__builtins__: {}`, this is a security risk if formulas ever come from user input or external sources.

**Implementation:**
- [ ] Review current formula_system.py implementation
- [ ] Research safe expression parsers (ast.literal_eval, pyparsing, simpleeval)
- [ ] Create replacement implementation with safe parser
- [ ] Write comprehensive tests for formula evaluation
- [ ] Verify all existing formulas still work
- [ ] Update component definitions if formula syntax changes

**Notes:** Consider using `simpleeval` library or custom AST-based evaluator. Must support basic math (+, -, *, /, min, max) and variable substitution.

---

### Task 1.2: ERR-11 - Fix Shell Command Injection [Simple]
**File:** `game/core/screenshot_manager.py:130`
**Tests:** `pytest tests/unit/core/test_screenshot_manager.py`

**Issue:** Tkinter fallback passes unvalidated text to `os.system()` shell command for clipboard operations. Potential command injection if text contains shell metacharacters.

**Implementation:**
- [ ] Review screenshot_manager.py clipboard code
- [ ] Replace `os.system(f'echo {text}| clip')` with subprocess.run()
- [ ] Use proper argument escaping: `subprocess.run(['clip'], input=text.encode(), shell=False)`
- [ ] Test with text containing special characters: `; & | $ \` etc.
- [ ] Verify clipboard functionality works on Windows

**Notes:** Simple fix - 15 minutes. High priority due to security risk.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Security vulnerabilities verified as fixed
- [ ] No new test failures introduced
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
