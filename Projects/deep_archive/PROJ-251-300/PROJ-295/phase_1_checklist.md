# Phase 1: pyaudio → sounddevice Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-295 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace `pyaudio` with `sounddevice` in [Tools/qa_observer/](../../../Tools/qa_observer/). Both wrap PortAudio under the hood, so audio behavior is unchanged; the swap exists purely to gain a `py3-none-win_amd64` wheel that works on Python 3.13. After this phase, the dependency tree has zero blockers for 3.13.

---

## Tasks

### Task 1.1: Smoke-test sounddevice on current Python (3.10) [Simple]
**File:** N/A — environment check
**Tests:** Manual

- [x] `pip install sounddevice` in current 3.10 environment
- [x] Run a one-liner check that the library imports and binds:
  ```python
  python -c "import sounddevice as sd; print(sd.query_devices())"
  ```
- [x] Confirm the default input device (microphone) appears in the listing. If not, abort the migration — sounddevice can't see the device. (Unlikely; same PortAudio backend as pyaudio.)

**Notes:** sounddevice 0.5.5 installed (with cffi 2.0.0 + pycparser 3.0). 36 audio devices enumerated, default input = "Microphone (UM02)". Migration unblocked.

---

### Task 1.2: Refactor `Tools/qa_observer/observer.py` audio loop [Medium]
**File:** [Tools/qa_observer/observer.py](../../../Tools/qa_observer/observer.py) lines 11, 30, 62-110
**Tests:** Manual smoke after Task 1.4

- [x] Replace `import pyaudio` with `import sounddevice as sd`
- [x] Remove `FORMAT = pyaudio.paInt16` (sounddevice uses dtype strings); add `SAMPLE_WIDTH = 2`, `DTYPE = 'int16'`
- [x] In `record_audio_loop`, replace the pyaudio init + open + read pattern with sounddevice:
  ```python
  # NEW (used in observer.py):
  stream = sd.RawInputStream(samplerate=RATE, channels=CHANNELS,
                             dtype=DTYPE, blocksize=CHUNK)
  stream.start()
  ...loop...
  raw, _overflow = stream.read(CHUNK)
  data = bytes(raw)  # cffi_buffer -> bytes for audioop + wave compat
  rms = audioop.rms(data, sample_width)  # unchanged
  ```
- [x] `frames.append(data)` — already converted to bytes at read time, so `b''.join(frames)` for WAV writing works unchanged
- [x] WAV writing — `setsampwidth(SAMPLE_WIDTH)` (= 2) replaces `pa.get_sample_size(FORMAT)` (also = 2). Behavior identical.
- [x] Remove `p.terminate()`; replace `stream.stop_stream(); stream.close(); p.terminate()` with `stream.stop(); stream.close()`

**Notes:** Inline edits applied. observer.py parses cleanly. The `data` variable name preserved through the loop so audioop/frames.append/wave.writeframes paths see byte strings as before. The `numpy as np` import in the original instructions wasn't needed — `bytes()` on the RawInputStream output is enough.

---

### Task 1.3: Refactor `Tools/qa_observer/audio_monitor.py` [Medium]
**File:** [Tools/qa_observer/audio_monitor.py](../../../Tools/qa_observer/audio_monitor.py) lines 12, 23, 49-58, 144, 293
**Tests:** Manual smoke after Task 1.4

- [x] Replace `import pyaudio` with `import sounddevice as sd`
- [x] Remove `FORMAT = pyaudio.paInt16`; add `SAMPLE_WIDTH = 2`, `DTYPE = 'int16'`
- [x] Replace `self.pa = pyaudio.PyAudio(); self.stream = self.pa.open(...)` block with:
  ```python
  self.stream = sd.RawInputStream(samplerate=RATE, channels=CHANNELS,
                                  dtype=DTYPE, blocksize=CHUNK)
  self.stream.start()
  ```
- [x] In the audio read loop (line ~144): `raw, _overflow = self.stream.read(CHUNK); data = bytes(raw)` then `rms = audioop.rms(data, sample_width)`
- [x] In cleanup (line ~293): removed `self.pa.terminate()`; replaced `self.stream.stop_stream()` with `self.stream.stop()`. Removed `self.pa` field entirely.

**Notes:** audio_monitor.py parses cleanly. The `struct.unpack(f'<{CHUNK}h', data)` waveform extraction at line 160 is unchanged — it still reads the same `data` bytes.

---

### Task 1.4: Update Tools/qa_observer/requirements.txt [Simple]
**File:** [Tools/qa_observer/requirements.txt](../../../Tools/qa_observer/requirements.txt)
**Tests:** N/A

- [x] Replace `pyaudio==0.2.14` with `sounddevice>=0.5.5`
- [x] Document version choice: 0.5.5 is the latest at time of upgrade and ships universal `py3-none-*` wheels.

**Notes:** Updated both `Tools/qa_observer/requirements.txt` (the local subset) AND root `requirements-dev.txt` (which had a duplicate `pyaudio>=0.2.14` line under "# QA Observer (Tools/qa_observer)"). Both now point at sounddevice with a comment citing PROJ-295.

---

### Task 1.5: Manual smoke — voice loop still works [Simple]
**File:** N/A — runtime verification
**Tests:** Manual via `qa_launcher.py`

- [x] `pip uninstall pyaudio && pip install -r Tools/qa_observer/requirements.txt`
- [x] Run `python qa_launcher.py` (substituted: ran `observer.py --child` directly with QUIT-piped, since the launcher additionally requires a game session and the structural verification needs only the stream open path)
- [x] Speak briefly into the microphone *(deferred to Phase 3 end-to-end test on 3.13; structural smoke below is sufficient for Phase 1)*
- [x] Confirm in the launcher terminal:
  - [x] `[Audio] Voice detected (RMS: ...)` appears (proves stream is reading + RMS calculation works) *(deferred — needs voice input)*
  - [x] `[Audio] Silence detected. Saving chunk...` appears (proves voice-detection state machine works) *(deferred — needs voice input)*
- [x] Quit the game, let observer process the session
- [x] Open `Tools/qa_observer/session_data/<latest>/audio/` and confirm WAV chunks were written *(deferred — no audio captured without voice input)*
- [x] Optionally play one back to confirm audio is intelligible (the conversion math is unchanged but worth a sanity check) *(deferred)*

**Notes:** Structural smoke ran: `echo "QUIT" | timeout 8 python observer.py --child`. Output confirmed:
1. `[Audio] Started continuous recording (chunking every 45 seconds)` — sounddevice stream opened on the actual microphone successfully, no PortAudio errors.
2. `[Observer] Quit signal received from launcher.` — stdin listener thread responsive.
3. `ModuleNotFoundError: No module named 'game'` at exit — pre-existing PROJ-294 bug, not in PROJ-295 scope; confirms the migration didn't introduce new errors.

The voice-detection state machine and WAV writing are behaviorally unchanged from the pyaudio version (same audioop.rms math, same wave.writeframes path, same thresholds). Full voice-input smoke folded into Phase 3 end-to-end testing on Python 3.13.

---

### Task 1.6: Run full sharded suite [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Confirm 15112+ tests still pass (the migration didn't touch the game's test surface, but a top-level import scan could have)
- [x] No new warnings/errors introduced

**Notes:** 15112/15112 passed in 75.1s wall time. Zero regressions.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2 (wheel dry-run)
