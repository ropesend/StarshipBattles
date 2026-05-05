# Phase 2: Wheel Availability Validation (Python 3.13 dry-run)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-295 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Confirm every dependency in [requirements.txt](../../../requirements.txt) and [requirements-dev.txt](../../../requirements-dev.txt) has a wheel published for Python 3.13. Done as `pip download --python-version 3.13` BEFORE installing 3.13 locally — surfaces gaps without polluting the working environment.

---

## Tasks

### Task 2.1: Run pip download against requirements.txt for Python 3.13 [Simple]
**File:** [requirements.txt](../../../requirements.txt)
**Tests:** Inspect output for any "Could not find a version" / "no matching distribution" errors

- [x] `pip download -r requirements.txt --python-version 3.13 --only-binary=:all: --no-deps --dest Projects/active_projects/PROJ-295/findings/dryrun`
- [x] Confirm all 4 runtime deps resolve: pygame-ce, pygame_gui, scipy, PyYAML
- [x] No "Could not find a version" or "no matching distribution" errors

**Notes:** Successful resolution. pygame-ce 2.5.7 cp313, pygame_gui 0.6.14 universal, scipy 1.17.1 cp313, PyYAML 6.0.3 cp313.

---

### Task 2.2: Run pip download against requirements-dev.txt for Python 3.13 [Simple]
**File:** [requirements-dev.txt](../../../requirements-dev.txt)
**Tests:** Inspect output

- [x] `pip download -r requirements-dev.txt --python-version 3.13 --only-binary=:all: --no-deps --dest Projects/active_projects/PROJ-295/findings/dryrun`
- [x] Confirm all 18 direct deps resolve (pytest, pytest-testmon, pytest-xdist, Pillow, numpy, opencv-python, matplotlib, fastapi, uvicorn, dearpygui, sounddevice, watchdog, google-cloud-speech, python-dotenv)
- [x] Pay particular attention to: `sounddevice`, `dearpygui`, `opencv-python`. These were the wheel-availability candidates flagged in research.

**Notes:** All 18 resolved successfully. opencv-python 4.13.0.92 uses `cp37-abi3` stable-ABI wheels (forward-compatible with all Python 3.x). dearpygui 2.3 has cp313 wheels. sounddevice 0.5.5 universal.

---

### Task 2.3: Run full transitive dry-run [Simple]
**File:** N/A
**Tests:** N/A

- [x] `pip download -r requirements-dev.txt --python-version 3.13 --only-binary=:all: --dest Projects/active_projects/PROJ-295/findings/dryrun_full`
- [x] Confirm 75+ transitive deps all resolve (annotated-doc, click, colorama, contourpy, coverage, cycler, exceptiongroup, execnet, fonttools, google-auth, grpcio, h11, iniconfig, kiwisolver, packaging, pluggy, proto-plus, pydantic, pydantic-core, pygments, pyparsing, python-dateutil, python-i18n, starlette, tomli, typing-extensions, typing-inspection, cffi, annotated-types, anyio, cryptography, googleapis-common-protos, grpcio-status, protobuf, pyasn1-modules, requests, six, google-api-core, pycparser, certifi, charset_normalizer, idna, pyasn1, urllib3, ...)
- [x] No source-build fallbacks (`--only-binary=:all:` would fail if any wheel was missing)

**Notes:** All transitive packages have 3.13 wheels. Zero gaps.

---

### Task 2.4: Write findings/wheel_gaps.md [Simple]
**File:** [findings/wheel_gaps.md](findings/wheel_gaps.md)
**Tests:** N/A

- [x] Write the report — even if "no gaps", document the result for the audit trail
- [x] Include the per-package wheel resolution table (proves every C-ext dep has a 3.13 wheel)

**Notes:** Wrote the full report. Verdict: zero gaps; Phase 3 install can proceed straight against `requirements-dev.txt` as-is.

---

### Task 2.5: Clean up download artifacts (optional) [Simple]
**File:** N/A
**Tests:** N/A

- [x] Decision: keep `findings/dryrun/` and `findings/dryrun_full/` directories. They serve as an offline wheelhouse for Phase 3 install if internet flakes, and as audit-trail evidence. Total ~150 MB; can be deleted post-archive.

**Notes:** Kept for now. Will delete in Phase 5 closeout if disk pressure emerges.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] [findings/wheel_gaps.md](findings/wheel_gaps.md) written ("No gaps")
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Phase 3 — local install"
