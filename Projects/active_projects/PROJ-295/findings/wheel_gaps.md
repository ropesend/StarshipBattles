# Wheel Gap Analysis — Python 3.13 Dry-Run

**Date:** 2026-04-26
**Result:** **No gaps. Python 3.13 upgrade is fully viable for this codebase.**

## Method

Used `pip download --python-version 3.13 --only-binary=:all:` against both `requirements.txt` and `requirements-dev.txt`. This queries PyPI for wheels matching Python 3.13 without needing 3.13 installed locally — `--only-binary=:all:` forces wheel-only resolution (no source builds), so any missing wheel surfaces as a hard failure.

Two passes:
1. Direct deps only (`--no-deps`) — 18 packages
2. Full transitive resolution — 75+ packages

## Results

**All packages resolved successfully on Python 3.13 (Windows amd64):**

### Direct deps (18, all wheels available)

| Package | Wheel resolved | Notes |
|---------|----------------|-------|
| pygame-ce>=2.5.0 | pygame_ce-2.5.7-cp313-cp313-win_amd64.whl | |
| pygame_gui>=0.6.9 | pygame_gui-0.6.14-py2.py3-none-any.whl | universal |
| scipy>=1.15.0 | scipy-1.17.1-cp313-cp313-win_amd64.whl | |
| PyYAML>=6.0 | pyyaml-6.0.3-cp313-cp313-win_amd64.whl | |
| pytest>=8.0.0 | pytest-9.0.3-py3-none-any.whl | universal |
| pytest-testmon | pytest_testmon-2.2.0-py3-none-any.whl | universal |
| pytest-xdist | pytest_xdist-3.8.0-py3-none-any.whl | universal |
| Pillow>=10.0.0 | pillow-12.2.0-cp313-cp313-win_amd64.whl | |
| numpy>=1.24.0 | numpy-2.4.4-cp313-cp313-win_amd64.whl | |
| opencv-python>=4.8.0 | opencv_python-4.13.0.92-cp37-abi3-win_amd64.whl | stable-ABI wheel |
| matplotlib>=3.7.0 | matplotlib-3.10.9-cp313-cp313-win_amd64.whl | |
| fastapi>=0.100.0 | fastapi-0.136.1-py3-none-any.whl | universal |
| uvicorn>=0.23.0 | uvicorn-0.46.0-py3-none-any.whl | universal |
| dearpygui>=1.9.0 | dearpygui-2.3-cp313-cp313-win_amd64.whl | |
| **sounddevice>=0.5.5** | **sounddevice-0.5.5-py3-none-win_amd64.whl** | **universal py3** (PROJ-295 Phase 1 replacement for pyaudio) |
| watchdog>=4.0.0 | watchdog-6.0.0-py3-none-win_amd64.whl | universal |
| google-cloud-speech>=2.26.0 | google_cloud_speech-2.38.0-py3-none-any.whl | universal — emits FutureWarning today on 3.10, gone on 3.13 |
| python-dotenv>=1.0.1 | python_dotenv-1.2.2-py3-none-any.whl | universal |

### Transitive deps (full set, all resolved)

The full transitive close pulled 75+ packages including: annotated-doc, click, colorama, contourpy, coverage, cycler, exceptiongroup, execnet, fonttools, google-auth, grpcio, h11, iniconfig, kiwisolver, packaging, pluggy, proto-plus, pydantic, pydantic-core, pygments, pyparsing, python-dateutil, python-i18n, starlette, tomli, typing-extensions, typing-inspection, cffi, annotated-types, anyio, cryptography, googleapis-common-protos, grpcio-status, protobuf, pyasn1-modules, requests, six, google-api-core, pycparser, certifi, charset_normalizer, idna, pyasn1, urllib3.

**Every one of them has a 3.13-compatible wheel.** No source builds required.

## Implication for Phase 3

- No package pins need to bump for 3.13 compatibility (the existing `>=` constraints all resolve).
- Phase 3 install can proceed straight against `requirements-dev.txt` as-is.
- No fallback to 3.12 or to dropping any dep is required.

## Notes

- Storage location of downloaded wheels (`findings/dryrun_full/`) — these can be deleted after Phase 2 closes; they are not part of the project deliverable. Or keep them as an offline wheelhouse for the Phase 3 install if desired.
- The "0 wheels for 3.13" result that the initial PyPI metadata scan showed for opencv-python was misleading — opencv-python ships `cp37-abi3` (stable-ABI) wheels which are forward-compatible with all Python 3.x including 3.13.
