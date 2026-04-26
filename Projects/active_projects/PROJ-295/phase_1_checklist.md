# Phase 1: Wheel Availability Validation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-295 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Confirm every C-extension dependency in [requirements.txt](../../../requirements.txt) and [requirements-dev.txt](../../../requirements-dev.txt) has a wheel published for the target Python version. Done as `pip install --dry-run` BEFORE migration so we discover gaps without polluting the working environment.

---

## Tasks

### Task 1.1: Install target Python version (does not replace 3.10) [Simple]
**File:** N/A — environment setup
**Tests:** N/A

- [ ] Install Python `<TARGET>` (recorded in Phase 0) alongside 3.10. On Windows, use the official installer; do NOT add to PATH (avoid shadowing the active 3.10).
- [ ] Confirm install: `py -<TARGET> --version` → "Python <TARGET>.x"

**Notes:** Both 3.10 and the target must coexist on the dev machine through Phase 2.

---

### Task 1.2: Create a throwaway venv for dry-run validation [Simple]
**File:** N/A
**Tests:** N/A

- [ ] `py -<TARGET> -m venv .venv-test`
- [ ] `.\.venv-test\Scripts\python.exe -m pip install --upgrade pip`
- [ ] Confirm: `.\.venv-test\Scripts\python.exe -c "import sys; print(sys.version)"`

**Notes:** This venv is throwaway. Phase 2 will create the real `.venv` (if Phase 0 said yes to introducing one).

---

### Task 1.3: Dry-run install runtime requirements [Simple]
**File:** [requirements.txt](../../../requirements.txt)
**Tests:** Inspect dry-run output

- [ ] `.\.venv-test\Scripts\python.exe -m pip install --dry-run -r requirements.txt 2>&1 | tee Projects/active_projects/PROJ-295/findings/dryrun_runtime.log`
- [ ] Inspect `dryrun_runtime.log` for any of:
  - `Could not find a version that satisfies the requirement ...`
  - `error: Microsoft Visual C++ ...` (compilation forced because no wheel)
  - `WARNING: Skipping <pkg> due to ...`
- [ ] Record any failures in the log file. If everything resolves, mark this task green.

**Notes:** Pure-Python deps (pygame_gui, scipy depends on numpy, etc.) are uninteresting; focus on C-extension entries.

---

### Task 1.4: Dry-run install dev requirements [Simple]
**File:** [requirements-dev.txt](../../../requirements-dev.txt)
**Tests:** Inspect dry-run output

- [ ] `.\.venv-test\Scripts\python.exe -m pip install --dry-run -r requirements-dev.txt 2>&1 | tee Projects/active_projects/PROJ-295/findings/dryrun_dev.log`
- [ ] Inspect for the same failure modes as Task 1.3
- [ ] Pay particular attention to: `pyaudio`, `dearpygui`, `opencv-python`. These are the historical wheel-availability culprits.

**Notes:** If `pyaudio` fails AND Phase 0 Q4 said pyaudio fallback is acceptable, record this as a known item (don't block) — Phase 2 will pin a compatible pyaudio version or disable it.

---

### Task 1.5: Decision document on any wheel gaps [Simple]
**File:** [findings/wheel_gaps.md](findings/wheel_gaps.md) (create new)
**Tests:** N/A

For each gap surfaced by Tasks 1.3 / 1.4, write an entry:

```markdown
### <package> - <issue>
- **Current pin:** `<package>>=<version>` (in <requirements file>)
- **Failure mode:** <what dry-run reported>
- **Resolution options:**
  - A) Pin to a known-working version (`<package>==X.Y.Z`)
  - B) Drop the dependency (impact: <which feature breaks>)
  - C) Source-compile (impact: <prerequisites needed>)
- **Chosen resolution:** <fill in after user confirms>
```

- [ ] If `findings/wheel_gaps.md` ends up empty, write a single line: "All dependencies have wheels for Python <TARGET>. No gaps."

**Notes:**

---

### Task 1.6: Clean up throwaway venv [Simple]
**File:** N/A
**Tests:** N/A

- [ ] `rm -rf .venv-test` (or `Remove-Item -Recurse .venv-test` on PowerShell)
- [ ] Confirm Phase 2 starts from a clean slate

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] [findings/wheel_gaps.md](findings/wheel_gaps.md) written (or "No gaps")
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Phase 2 — local migration"
