# Phase 4: R5 — `Tools/regenerate_ship_portraits/` conventions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-318 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Read `Tools/process_components/README.md` to learn the README shape
- [x] Read `Tools/process_components/check_orphans.py` lines 1-25 for the project-root bootstrap pattern (project-root finder + `sys.path` insertion BEFORE any `from game.X` import)
- [x] Read `Tools/README.md` to identify which catalog category to put `regenerate_ship_portraits` under (likely Asset Processing, or a new Generative section if no fit)

**Notes:** Completed; README and Tools catalog entry added, and both direct-script and `-m` invocation forms work for `cli.py` and `audit.py`.
### Task 4.2: Create `Tools/regenerate_ship_portraits/README.md` [Simple]
**File:** `Tools/regenerate_ship_portraits/README.md` (NEW)
**Tests:** None.

- [x] Create the file with the standard sections: `# regenerate_ship_portraits`
- [x] Section: Purpose (what it does — generate missing ship portraits via OpenAI gpt-image-2)
- [x] Section: Usage (both invocation forms: `python -m Tools.regenerate_ship_portraits.cli` and `python Tools/regenerate_ship_portraits/cli.py`)
- [x] Section: Flags (mirror `--help` output: `--theme`, `--ship-class`, `--dry-run`, `--force`, `--cost-cap`, `--model`, `--size`, `--batch`, `--list-themes`, `--list-classes`, `--verbose`)
- [x] Section: Output (prints to stdout, manifest at `Tools/regenerate_ship_portraits/last_run.json`)
- [x] Section: Cost (default cap $5.00; default model gpt-image-2; estimated $0.04/image)
- [x] Section: Examples (3-4 typical invocations)
- [x] Section: Audit script (mention `python -m Tools.regenerate_ship_portraits.audit` produces a coverage report; cross-link)

**Notes:** Completed; README and Tools catalog entry added, and both direct-script and `-m` invocation forms work for `cli.py` and `audit.py`.
### Task 4.3: Add catalog entry to `Tools/README.md` [Simple]
**File:** `Tools/README.md`
**Tests:** None.

- [x] Find the appropriate section (Asset Processing, or create new Generative section)
- [x] Add a one-line entry: `| regenerate_ship_portraits | Generate missing ship portraits via OpenAI gpt-image-2 (deferred AI generation; PROJ-314 Phase 4) | [README](regenerate_ship_portraits/README.md) |` (match the existing table format)
- [x] Bump `Last verified:` date if the file has one
- [x] Verify: `grep -n regenerate_ship_portraits Tools/README.md` shows the new entry

**Notes:** Completed; README and Tools catalog entry added, and both direct-script and `-m` invocation forms work for `cli.py` and `audit.py`.
### Task 4.4: Add project-root bootstrap to cli.py [Simple]
**File:** `Tools/regenerate_ship_portraits/cli.py`
**Tests:** Manual + targeted.

- [x] Read the current top of the file (lines 1-60)
- [x] Insert a project-root bootstrap BEFORE the `from game.X import` lines, mirroring `Tools/process_components/check_orphans.py:8-19`. Pattern:
  ```python
  import sys
  from pathlib import Path
  REPO_ROOT = Path(__file__).resolve().parent.parent.parent
  if str(REPO_ROOT) not in sys.path:
      sys.path.insert(0, str(REPO_ROOT))
  ```
- [x] Verify the file still imports cleanly under `python -m Tools.regenerate_ship_portraits.cli --help`
- [x] Verify it now also runs under `python Tools/regenerate_ship_portraits/cli.py --help` (currently fails with import error)

**Notes:** Completed; README and Tools catalog entry added, and both direct-script and `-m` invocation forms work for `cli.py` and `audit.py`.
### Task 4.5: Add project-root bootstrap to audit.py [Simple]
**File:** `Tools/regenerate_ship_portraits/audit.py`
**Tests:** Manual.

- [x] Same pattern as Task 4.4
- [x] Verify both invocation forms work: `python -m Tools.regenerate_ship_portraits.audit` and `python Tools/regenerate_ship_portraits/audit.py`

**Notes:** Completed; README and Tools catalog entry added, and both direct-script and `-m` invocation forms work for `cli.py` and `audit.py`.
### Task 4.6: Verification [Simple]
**File:** None.
**Tests:** Run the tool both ways.

- [x] Run `python Tools/regenerate_ship_portraits/cli.py --help` from repo root; expect a clean help dump
- [x] Run `python -m Tools.regenerate_ship_portraits.cli --help`; expect identical output
- [x] Run `python Tools/regenerate_ship_portraits/audit.py`; expect identical output to the `-m` form
- [x] `grep -c regenerate_ship_portraits Tools/README.md` returns ≥ 1

**Notes:** Completed; README and Tools catalog entry added, and both direct-script and `-m` invocation forms work for `cli.py` and `audit.py`.
---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] README exists and is well-formed
- [x] Catalog entry exists in Tools/README.md
- [x] Both invocation forms work for both cli.py and audit.py
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
- [x] Commit: `chore(PROJ-318 Phase 4): regenerate_ship_portraits/ tool conventions`
