# PROJ-299: Race Description Generator (LLM)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-299` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-299 [phase]` before stopping
> - Update Current State with specific handoff context

---

## Quick Status

| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Caption schemas + Gemini prompts + validation tool | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Caption loader | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Prompt assembly layer | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. RaceDescriptionLLMController (MVVM extract) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Description tab UI integration | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Dialogs + cancel hook + error popups | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Polish, MAX_LENGTH bump, docs | Complete | [phase_7_checklist.md](phase_7_checklist.md) |

---

## Current State

**Last Updated:** 2026-04-26 21:00
**Active Phase:** Complete — awaiting user verification
**Last Action:** All 7 phases implemented and tested. Final sharded suite: **15328/15328 passing** (+55 tests over PROJ-296's 15273 baseline; 0 regressions). Documentation updated: `docs/02_PATTERNS.md` Pattern #28 gets a "Reference consumer (PROJ-299)" section; `docs/systems/strategy_layer.md` §7.x mentions the new caption loader / prompt builder / LLM controller. `MAX_LENGTH` bumped 500 → 5000 with the char-label widened to fit 4-digit values.
**Next Action:** **USER VERIFICATION** — run Phase 7 Task 7.6 manual smoke. The user needs to: (a) run the Gemini capture prompts in `Tools/captioning/prompts/` against each of the 37 visual assets and save the JSON sidecars, then (b) launch the game with `DEEPSEEK_API_KEY` set and try Generate Bio / Generate Socio / Re-roll / Cancel.
**Blockers:** None — implementation done.
**Context for Next Agent:**
- Foundation is PROJ-296 (LLM Service Foundation, landed in the same dev day). This project is the **canonical first consumer** of Pattern #28 (Background Service Call). Future LLM consumers (diplomacy, ad-hoc summaries) should follow the same `Controller + on_change + screen.update()` shape.
- Visual asset captions are pre-baked **externally** by the user via Gemini — this project ships the 3 prompts (`Tools/captioning/prompts/{flag,portrait,theme}_prompt.md`) and a validator (`Tools/captioning/validate_captions.py`), not the captioning code itself. The validator currently reports 37 MISSING (expected — that's the user's task).
- LLM orchestration lives in pygame-free `RaceDescriptionLLMController` (Phase 4). `RaceSetupScreen` only routes button events + polls per-frame + renders. This kept the screen growth manageable despite its existing 1294 lines.
- The 30s/90s dialog uses `LLMConfig.DEFAULT_TIMEOUT_SECONDS` override of `timeout_seconds=90` on the `LLMBackgroundCall`, so the network timeout fires shortly after the second dialog rather than mid-wait.
- The `_block_real_http` autouse fixture in `tests/conftest.py` (from PROJ-296) guarantees no test hits the real DeepSeek API; all controller tests use `_StubProvider` / `_BlockingProvider` / `_RaisingProvider` doubles.

---

## Overview

Add LLM-generated biological + sociological descriptions to the Race Setup screen's Description tab. Two separate "Generate" buttons (one per description) trigger background calls to DeepSeek via the PROJ-296 LLM service. The LLM prompt assembles every prior race choice (identity, aptitudes, environment) plus pre-baked structured captions of the selected visual assets (flag, portrait, ship theme).

Image consistency is achieved without a vision model: the user runs Gemini externally once per asset to produce structured `*.caption.json` sidecars; the runtime DeepSeek call reads those captions as text. This keeps the runtime model cheap and text-only.

---

## Goals

- **First consumer of PROJ-296**, validating the abstraction end-to-end
- **Two independent calls** (bio + socio) that can run in parallel and re-roll independently
- **MVVM-clean** integration — `RaceSetupScreen` doesn't grow further; orchestration lives in a separate Controller
- **30s + 60s = 90s waiting UX** with explicit "still working / stop" dialogs at each stage
- **Editable output** — generated text populates standard text boxes; user can edit, re-roll, or accept as-is
- **Graceful degradation** when caption sidecars are missing (LLM still runs, just less specific)

---

## Scope

### In Scope (v1)

- Three asset-specific JSON caption schemas (flag, portrait, ship theme)
- Three Gemini capture prompts (committed as `Tools/captioning/prompts/*.md` for the user to use externally)
- Validation tool (`Tools/captioning/validate_captions.py`) that scans `assets/` for sidecars, reports missing/invalid
- Caption loader (`game/strategy/data/race_caption_loader.py`) — given asset id, returns parsed sidecar dict or None
- Prompt builder module — pure functions `build_bio_prompt(race_config, captions)` and `build_socio_prompt(race_config, captions)` returning `list[Message]`
- `RaceDescriptionLLMController` — pygame-free; owns LLM call lifecycle, parallel bio+socio dispatch, status state, cancel, re-roll, dialog timing
- UI integration on Description tab: 2 Generate buttons + 2 Re-roll buttons (initially hidden) + status labels (below text boxes) + dual-button cancel pattern
- 30s "still working / stop" dialog (re-armed at 60s; total 90s wall before network timeout)
- Per-error-type popups (`LLMConfigError`, `LLMNetworkError`, `LLMRateLimited`, `LLMTimeoutError`)
- `RaceSetupScreen.kill()` cancel hook (cancels all in-flight calls)
- Text-box lock during generation (prevents edit-conflict)
- Bump `RaceDescriptionPanel.MAX_LENGTH` from 500 to 5000
- Few-shot examples (1 bio + 1 socio) in the system prompt for tone consistency

### Out of Scope (v1)

- In-game image captioning (user runs Gemini externally — this project provides the prompts only)
- Streaming token-by-token UI
- Multi-language generation
- Storing generation history / "previous versions" UI
- Auto-regenerate on every choice change
- Edit-during-generation (user CAN re-trigger after a generation completes; cannot edit while one is running)
- 3rd description type (history, etc.) — see "Future Scaling" in design.md if it ever comes up
- Session-level cost tracking / budget UI

---

## Key Files

### New files (to be created)
| Component | File Path | Phase |
|-----------|-----------|-------|
| Flag caption schema | `Tools/captioning/schemas/flag.schema.json` | 1 |
| Portrait caption schema | `Tools/captioning/schemas/portrait.schema.json` | 1 |
| Theme caption schema | `Tools/captioning/schemas/theme.schema.json` | 1 |
| Flag capture prompt | `Tools/captioning/prompts/flag_prompt.md` | 1 |
| Portrait capture prompt | `Tools/captioning/prompts/portrait_prompt.md` | 1 |
| Theme capture prompt | `Tools/captioning/prompts/theme_prompt.md` | 1 |
| Caption validator tool | `Tools/captioning/validate_captions.py` | 1 |
| Caption loader | `game/strategy/data/race_caption_loader.py` | 2 |
| Prompt builder | `game/strategy/services/race_description_prompt_builder.py` | 3 |
| LLM controller | `game/strategy/services/race_description_llm_controller.py` | 4 |

### Modified files
| Component | File Path | Phase |
|-----------|-----------|-------|
| Description panel (UI) | `game/ui/panels/race_description_panel.py` | 5, 7 |
| Race Setup screen (event routing + kill hook) | `game/ui/screens/race_setup_screen.py` | 5, 6 |

### Triage findings
- [findings/race_description_generation.md](findings/race_description_generation.md)
- `.agent_reports/proj_299_phase_a/*` (ephemeral)
- `.agent_reports/proj_299_phase_b/*` (ephemeral)

---

## Decisions Log (summary; see [decisions.md](decisions.md) for full)

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Two LLM calls (bio + socio) in parallel | Independent re-roll; cleaner error handling; PROJ-296 supports concurrent calls |
| 2026-04-26 | `MAX_LENGTH` bump 500 → 5000 | LLM output exceeds 500; 5000 gives generous headroom; existing `text[:MAX_LENGTH]` truncate path stays |
| 2026-04-26 | Three asset-specific caption schemas | Flag/portrait/theme need different fields; one-size-fits-all produces vague LLM output (Prompt Engineering finding) |
| 2026-04-26 | Pre-bake captions via Gemini externally | Narrative model stays text-only (cheap); user runs 37 Gemini calls once |
| 2026-04-26 | Extract `RaceDescriptionLLMController` (pygame-free) | `RaceSetupScreen` is 1294 lines (MVVM smell); precedent: PROJ-282 `BattleSetupController` |
| 2026-04-26 | Dual-button cancel UX | Disable "Generate" + show "Cancel" beside it; never lose the visual anchor |
| 2026-04-26 | Status label BELOW the text box | "Generating Bio… 12s" as separate label; not placeholder text inside the box (causes "did I lose my edits?" anxiety) |
| 2026-04-26 | Re-roll is a SEPARATE persistent button (initially hidden) | Don't morph "Generate" into "Re-roll"; different actions deserve different buttons |
| 2026-04-26 | Lock text box during generation (no edit) | User chose lock over edit-conflict dialog — simpler |
| 2026-04-26 | 30s + 60s = 90s wait pattern | Dialog at 30s; if "Keep Waiting" clicked, second dialog at 90s; LLM `timeout_seconds=90` so network timeout fires after the second dialog (definitive end) |
| 2026-04-26 | `RaceSetupScreen.kill()` cancels in-flight calls | Risk Assessor HIGH: prevents AttributeError on dead UI elements |
| 2026-04-26 | Generate button disabled while call in flight | Risk Assessor HIGH: prevents double-click race + spam |
| 2026-04-26 | Few-shot examples (1 bio + 1 socio) in system prompt | Cached on provider side; sets tone reliably; <500 token cost |
| 2026-04-26 | Missing caption: explicit `{"note": "..."}` in prompt | Prevents LLM from inventing visual details when sidecar absent |
| 2026-04-26 | Prompt builder = stateless module function | Mirrors `build_test_battle_spec`; not registered on ApplicationContext |
| 2026-04-26 | Caption sidecar layout: per-flag-dir, per-portrait-file, per-theme-dir | Avoids 18-files-per-flag explosion (3 shapes × 6 sizes) |
| 2026-04-26 | Homeworld_type included in prompt but subordinate | Adds texture without forcing consistency constraints |

---

## Phases

### Phase 1: Caption schemas + Gemini prompts + validation tool [Medium]
**Status:** Complete
**Objective:** Three asset-specific JSON schemas. Three Gemini capture prompts the user can copy/paste. A `Tools/` script that scans `assets/` and reports which sidecars are missing or malformed. NO captions generated by code.

Tasks: see [phase_1_checklist.md](phase_1_checklist.md).

### Phase 2: Caption loader [Simple]
**Status:** Complete
**Objective:** `RaceCaptionLoader.load_flag(flag_id) / load_portrait(portrait_id) / load_theme(theme_id)` — returns parsed sidecar dict or None. Graceful degradation on missing/malformed.

Tasks: see [phase_2_checklist.md](phase_2_checklist.md).

### Phase 3: Prompt assembly layer [Medium]
**Status:** Complete
**Objective:** Pure module-level functions `build_bio_prompt(race_config, captions) -> list[Message]` and `build_socio_prompt(...) -> list[Message]`. Includes few-shot examples in system prompt. Handles missing-caption gracefully via `{"note": "no visual reference"}` in the prompt.

Tasks: see [phase_3_checklist.md](phase_3_checklist.md).

### Phase 4: RaceDescriptionLLMController (MVVM extract) [Complex]
**Status:** Complete
**Objective:** Pygame-free controller owning the LLM call lifecycle. Holds two `LLMBackgroundCall`s (bio + socio), tracks status per-field, dispatches calls in parallel, handles cancel + re-roll cancel-and-restart, exposes `on_change` callback for UI rebuild.

Tasks: see [phase_4_checklist.md](phase_4_checklist.md).

### Phase 5: Description tab UI integration [Medium]
**Status:** Complete
**Objective:** Two Generate buttons + two Re-roll buttons (initially hidden) + two status labels (below text boxes) + dual-button cancel UI. Wire `RaceSetupScreen.update()` to poll the controller. Lock text boxes during generation. Inject controller state changes into the panel via the on_change callback.

Tasks: see [phase_5_checklist.md](phase_5_checklist.md).

### Phase 6: Dialogs + cancel hook + error popups [Medium]
**Status:** Complete
**Objective:** 30s "still working" modal (re-armed at 60s). Per-error-type popups. `RaceSetupScreen.kill()` cancel hook for all in-flight calls.

Tasks: see [phase_6_checklist.md](phase_6_checklist.md).

### Phase 7: Polish, MAX_LENGTH bump, docs, full sharded suite [Simple]
**Status:** Complete
**Objective:** Bump `MAX_LENGTH` from 500 to 5000. Widen char-count label to fit 4-digit values. Update `docs/systems/strategy_layer.md` (add prompt builder mention) and `docs/02_PATTERNS.md` (add this project as canonical Pattern #28 consumer). Final sharded suite verification.

Tasks: see [phase_7_checklist.md](phase_7_checklist.md).

---

## Verification Checklist

### Project Start (REQUIRED, completed)
- [x] Read `docs/` foundation docs (already loaded from PROJ-296 work)
- [x] Run full test suite: 15273/15273 passing in 57.7s

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — affected tests pass
- [ ] Update phase status in this plan
- [ ] Update Current State

### Final Verification
- [ ] All Phase 1-7 tasks checked off
- [ ] `Tools/captioning/validate_captions.py` reports 0 missing/invalid sidecars (after user runs Gemini)
- [ ] With `DEEPSEEK_API_KEY` set: launch game → Race Setup → Description tab → click Generate Bio → see status label, then text appears
- [ ] Re-roll Bio → previous text replaced, Socio unaffected
- [ ] Click Cancel mid-call → status clears, text restored to prior value
- [ ] Force a 30s+ delay (e.g. unplug network during call) → 30s dialog appears, "Keep Waiting" → 60s later second dialog, network timeout error popup
- [ ] Run full sharded suite — baseline preserved + ~50 new tests pass
- [ ] User verified

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

---

## Completion Checklist
- [ ] All Phase 1-7 tasks checked off
- [ ] All tests passing (~15323+)
- [ ] No regression
- [ ] Docs updated
- [ ] User verified end-to-end
</content>
</invoke>