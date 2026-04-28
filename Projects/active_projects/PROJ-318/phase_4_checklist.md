# Phase 4: R5 — `Tools/regenerate_ship_portraits/` conventions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-318 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Bring `Tools/regenerate_ship_portraits/` up to the
project's tool conventions (per `Tools/README.md` lines 102-110): a
README in the tool directory, a catalog entry in `Tools/README.md`,
and a project-root bootstrap that lets the tool run via
`python Tools/regenerate_ship_portraits/cli.py` (not just
`python -m Tools.regenerate_ship_portraits.cli`).

---

## Tasks

### Task 4.1: Read precedent README + bootstrap pattern [Simple]
**File:** None (read-only research).
**Tests:** None.

- [ ] Read `Tools/process_components/README.md` to learn the README shape
- [ ] Read `Tools/process_components/check_orphans.py` lines 1-25 for the project-root bootstrap pattern (project-root finder + `sys.path` insertion BEFORE any `from game.X` import)
- [ ] Read `Tools/README.md` to identify which catalog category to put `regenerate_ship_portraits` under (likely Asset Processing, or a new Generative section if no fit)

**Notes:**

### Task 4.2: Create `Tools/regenerate_ship_portraits/README.md` [Simple]
**File:** `Tools/regenerate_ship_portraits/README.md` (NEW)
**Tests:** None.

- [ ] Create the file with the standard sections: `# regenerate_ship_portraits`
- [ ] Section: Purpose (what it does — generate missing ship portraits via OpenAI gpt-image-2)
- [ ] Section: Usage (both invocation forms: `python -m Tools.regenerate_ship_portraits.cli` and `python Tools/regenerate_ship_portraits/cli.py`)
- [ ] Section: Flags (mirror `--help` output: `--theme`, `--ship-class`, `--dry-run`, `--force`, `--cost-cap`, `--model`, `--size`, `--batch`, `--list-themes`, `--list-classes`, `--verbose`)
- [ ] Section: Output (prints to stdout, manifest at `Tools/regenerate_ship_portraits/last_run.json`)
- [ ] Section: Cost (default cap $5.00; default model gpt-image-2; estimated $0.04/image)
- [ ] Section: Examples (3-4 typical invocations)
- [ ] Section: Audit script (mention `python -m Tools.regenerate_ship_portraits.audit` produces a coverage report; cross-link)

**Notes:**

### Task 4.3: Add catalog entry to `Tools/README.md` [Simple]
**File:** `Tools/README.md`
**Tests:** None.

- [ ] Find the appropriate section (Asset Processing, or create new Generative section)
- [ ] Add a one-line entry: `| regenerate_ship_portraits | Generate missing ship portraits via OpenAI gpt-image-2 (deferred AI generation; PROJ-314 Phase 4) | [README](regenerate_ship_portraits/README.md) |` (match the existing table format)
- [ ] Bump `Last verified:` date if the file has one
- [ ] Verify: `grep -n regenerate_ship_portraits Tools/README.md` shows the new entry

**Notes:**

### Task 4.4: Add project-root bootstrap to cli.py [Simple]
**File:** `Tools/regenerate_ship_portraits/cli.py`
**Tests:** Manual + targeted.

- [ ] Read the current top of the file (lines 1-60)
- [ ] Insert a project-root bootstrap BEFORE the `from game.X import` lines, mirroring `Tools/process_components/check_orphans.py:8-19`. Pattern:
  ```python
  import sys
  from pathlib import Path
  REPO_ROOT = Path(__file__).resolve().parent.parent.parent
  if str(REPO_ROOT) not in sys.path:
      sys.path.insert(0, str(REPO_ROOT))
  ```
- [ ] Verify the file still imports cleanly under `python -m Tools.regenerate_ship_portraits.cli --help`
- [ ] Verify it now also runs under `python Tools/regenerate_ship_portraits/cli.py --help` (currently fails with import error)

**Notes:**

### Task 4.5: Add project-root bootstrap to audit.py [Simple]
**File:** `Tools/regenerate_ship_portraits/audit.py`
**Tests:** Manual.

- [ ] Same pattern as Task 4.4
- [ ] Verify both invocation forms work: `python -m Tools.regenerate_ship_portraits.audit` and `python Tools/regenerate_ship_portraits/audit.py`

**Notes:**

### Task 4.6: Verification [Simple]
**File:** None.
**Tests:** Run the tool both ways.

- [ ] Run `python Tools/regenerate_ship_portraits/cli.py --help` from repo root; expect a clean help dump
- [ ] Run `python -m Tools.regenerate_ship_portraits.cli --help`; expect identical output
- [ ] Run `python Tools/regenerate_ship_portraits/audit.py`; expect identical output to the `-m` form
- [ ] `grep -c regenerate_ship_portraits Tools/README.md` returns ≥ 1

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] README exists and is well-formed
- [ ] Catalog entry exists in Tools/README.md
- [ ] Both invocation forms work for both cli.py and audit.py
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
- [ ] Commit: `chore(PROJ-318 Phase 4): regenerate_ship_portraits/ tool conventions`
