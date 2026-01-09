# Test Isolation Audit & Shielding Plan

**Task:** Exhaustively review all ~500 unit tests to ensure they are shielded from parallel execution pollution (`pytest-xdist`).
**Objective:** Eliminate flaky tests caused by shared state (mocks, `sys.modules`, `pygame`, `RegistryManager`) to enable reliable parallel testing (`-n 16`).
**Strategy:** "Divide and Conquer" using a persistent manifest to track progress across multiple agent sessions.

---

## 1. Central Coordination: The Manifest

A single source of truth, `Refactoring/test_audit_manifest.md`, must be maintained. It tracks the status of every test file.

**Manifest Structure:**
```markdown
# Test Audit Manifest

| Batch | Directory | Status | Agent | Last Updated |
| :--- | :--- | :--- | :--- | :--- |
| B1 | tests/unit/ai | [ ] Pending | - | - |
| B2 | tests/unit/builder | [ ] Pending | - | - |
| ... | ... | ... | ... | ... |

## Findings Log
| File | Issue Type | Description | Remediation |
| :--- | :--- | :--- | :--- |
| `test_foo.py` | Pygame Leak | Initializes pygame without quit | Add `teardown_module` |
```

---

## 2. The Verification Protocol (Agent Script)

Each agent assigned to a batch MUST follow this exact protocol for EACH file in their batch.

### Step 1: Static Analysis
Scan the file for these "Pollution Vectors":

1.  **Global Mocks:**
    *   **Pattern:** `mock.patch` used as a decorator or context manager without explicit stop (rare, but check for manual `start()` without `stop()`).
    *   **Risk:** Leaks into other tests running in the same worker.
    *   **Fix:** Ensure extensive use of `unittest.mock.patch` context managers or `addCleanup`.

2.  **System Module Patching:**
    *   **Pattern:** `sys.modules['module_name'] = ...`
    *   **Risk:** EXTREME. Affects all tests in the process.
    *   **Fix:** Must use `mock.patch.dict(sys.modules, ...)` or manual save/restore in `setUp`/`tearDown`.

3.  **Registry/Singleton State:**
    *   **Pattern:** `RegistryManager.register(...)` or accessing global singletons.
    *   **Risk:** Data pollution between tests.
    *   **Fix:** `RegistryManager._instance = None` or `reset()` in `tearDown`.

4.  **Pygame/UI State:**
    *   **Pattern:** `pygame.init()`, `pygame.display.set_mode()`.
    *   **Risk:** Headless environments fail; parallel workers fight for window focus.
    *   **Fix:** Shield with `if os.environ.get('SDL_VIDEODRIVER') == 'dummy'` or ensure `pygame.quit()` is called.

### Step 2: Isolation Verification (Run Test)
Run the specific test file in isolation using pytest.
`pytest tests/unit/path/to/test_file.py`
*If it fails in isolation, mark as BROKEN.*

### Step 3: Reporting
Update the `Test Audit Manifest`:
1.  Mark the Batch as `[In-Progress]` -> `[Complete]`.
2.  Log any specific "Pollution Vectors" found in the "Findings Log".
3.  **DO NOT FIX THE CODE.** Just log the findings.

---

## 3. Batch Definitions

We divide the 170+ files into logical chunks to fit agent context windows.

| Batch ID | Path / Scope | File Count (Approx) | Risk Level |
| :--- | :--- | :--- | :--- |
| **B01** | `tests/unit/ai/` | 5 files | Low |
| **B02** | `tests/unit/builder/` | 20 files | **High** (UI/State) |
| **B03** | `tests/unit/combat/` | 17 files | Medium |
| **B04** | `tests/unit/data/` | 27 files | Low |
| **B05** | `tests/unit/entities/` (A-M) | ~16 files | Medium |
| **B06** | `tests/unit/entities/` (N-Z) | ~17 files | Medium |
| **B07** | `tests/unit/performance/` | 9 files | Low |
| **B08** | `tests/unit/regressions/` & `repro_issues/` | 6 files | Medium |
| **B09** | `tests/unit/simulation/` | 25 files | Medium |
| **B10** | `tests/unit/systems/` | 12 files | Medium |
| **B11** | `tests/unit/ui/` | 16 files | **Critical** (Pygame) |
| **B12** | `tests/unit/*.py` (Root unit inputs) | ~1 files | Low |

---

## 4. Execution Workflow

1.  **Initialize:** User (or Lead Agent) creates `Refactoring/test_audit_manifest.md` with the table above.
2.  **Iterate:**
    *   Agent checks Manifest for next `[ ] Pending` batch.
    *   Agent "Checkouts" the batch (marks `[In-Progress]`).
    *   Agent performs **The Verification Protocol**.
    *   Agent updates Manifest with findings and marks `[Complete]`.
    *   Agent Stops (or continues if context permits).
3.  **Finalize:** A "Fixer" agent reviews the "Findings Log" and applies standardized patches.

## 5. Next Steps for User
1.  Approve this plan.
2.  Instruct agent to "Initialize the Manifest".
3.  Instruct agent to "Start B01" or "Start Critical Batches (B02, B11)".
