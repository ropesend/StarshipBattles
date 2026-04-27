# PROJ-299: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | First consumer of PROJ-296 LLM Service Foundation |
| 2026-04-26 | **Two LLM calls (bio + socio) in parallel** (not one structured call) | Independent re-roll without losing the other; cleaner error handling; PROJ-296 supports `MAX_CONCURRENT_CALLS=3`. Cost difference negligible at single-player rates. |
| 2026-04-26 | **`MAX_LENGTH` bump 500 → 5000** | LLM bio + socio output exceeds 500 chars each. 5000 gives generous headroom; existing `text[:MAX_LENGTH]` truncate path stays intact. |
| 2026-04-26 | **Three asset-specific JSON caption schemas** (flag/portrait/theme) | One-size-fits-all schema produces vague LLM output (Phase B Prompt Engineering finding). Different asset types convey fundamentally different info. |
| 2026-04-26 | **Pre-bake captions externally via Gemini** (NOT in-game) | Narrative model stays text-only and cheap (DeepSeek `deepseek-chat`). User runs 37 Gemini calls once via the prompts shipped in `Tools/captioning/prompts/`. |
| 2026-04-26 | Sidecar layout: per-flag-dir, per-portrait-file, per-theme-dir | Per-flag-dir avoids 18 sidecars per flag (3 shapes × 6 sizes). Each conceptual asset gets one caption. Total: 37 sidecars. |
| 2026-04-26 | **Extract `RaceDescriptionLLMController`** (pygame-free, MVVM) | `RaceSetupScreen` is already 1294 lines (well past 300-line MVVM smell per `docs/03_CONVENTIONS.md` §2.4). Precedent: PROJ-282 `BattleSetupController`. Controller owns LLM lifecycle; screen is reduced to event routing + UI rebuild on `on_change`. |
| 2026-04-26 | **Caption loader in `game/strategy/data/`** | Pure JSON-loading pattern; sibling to `classification_config.py`, `homeworld_presets.py`. Strategy data layer per PROJ-XX `01_ARCHITECTURE.md`. |
| 2026-04-26 | **Prompt builder in `game/strategy/services/`** as stateless module function | Mirrors `build_test_battle_spec` / `build_strategy_battle_spec`. Not registered on ApplicationContext (leaf utility, not long-lived service). |
| 2026-04-26 | **Controller in `game/strategy/services/`** | Pygame-free; depends on Strategy data + Services LLM. UI-side state machine that the UI layer polls. |
| 2026-04-26 | **Dual-button cancel UX** (disable Generate + show Cancel beside) | Phase B UX Reviewer: never lose the visual anchor. Single-button morph confuses users about what state they're in. |
| 2026-04-26 | **Status label BELOW the text box** (not placeholder text inside) | Phase B UX Reviewer: placeholder text inside the box causes "did I lose my edits?" anxiety. Separate label is unambiguous: "Generating Bio… 12s". |
| 2026-04-26 | **Re-roll is a SEPARATE persistent button** (initially hidden) | Phase B UX Reviewer: don't morph "Generate" into "Re-roll" — different actions deserve different buttons. Re-roll appears after first successful generation. |
| 2026-04-26 | **Lock text box during generation** (no edit) | User decision: simpler than implementing the edit-conflict dialog. If user wants to keep their text, they can Cancel and not click Generate. |
| 2026-04-26 | **30s + 60s = 90s wait pattern** | First "still working" dialog at t=30s. If user clicks "Keep Waiting", second dialog at t=90s. LLM call's `timeout_seconds=90` (override of `LLMConfig.DEFAULT_TIMEOUT_SECONDS=60`) so the network timeout fires shortly after the second dialog rather than mid-wait. |
| 2026-04-26 | **`RaceSetupScreen.kill()` cancels in-flight calls** | Risk Assessor HIGH: prevents AttributeError on dead UI elements when user closes the screen mid-call. |
| 2026-04-26 | **Generate button disabled while call in flight** | Risk Assessor HIGH: prevents double-click race condition + spam. Catches `LLMConfigError` from `MAX_CONCURRENT_CALLS` defensively. |
| 2026-04-26 | **Few-shot examples (1 bio + 1 socio) in system prompt** | Phase B Prompt Engineering: cached on provider side; sets tone reliably for ~280 token cost. Cheaper than per-request examples in user prompt. |
| 2026-04-26 | **Missing caption: explicit `{"note": "no visual reference"}` in prompt** | Phase B Prompt Engineering: prevents LLM from inventing visual details when sidecar absent. Better signal than empty omission. |
| 2026-04-26 | **Homeworld_type included in prompt but subordinate** to env preferences/visuals | Phase B Prompt Engineering: adds texture without forcing consistency constraints that could break creative output. |
| 2026-04-26 | **Per-error-type popups** (LLMConfigError, LLMNetworkError, LLMRateLimited, LLMTimeoutError) | Phase B UX Reviewer: each error has distinct meaning; generic "something went wrong" hides actionable info. |
| 2026-04-26 | **Re-roll cancels prior call for that field before starting new** | Risk Assessor MEDIUM: prevents stale results from old call overwriting new ones. PROJ-296 request-ID versioning helps but explicit cancel is cheaper to reason about. |
| 2026-04-26 | **Both calls (bio + socio) start simultaneously on Generate** (not sequential) | Risk Assessor + UX: half the wall-clock time. PROJ-296 supports up to 3 concurrent calls (we use 2). |
| 2026-04-26 | **MAX_LENGTH centralized as `RaceDescriptionPanel.MAX_LENGTH = 5000`** (NOT moved to `game_settings.py`) | Phase B Architecture: technical constraint, not user preference. Keep hardcoded; only this UI consults it. |
| 2026-04-26 | **No new `docs/02_PATTERNS.md` entry** for the 30s dialog flow | Phase B Pattern Scout: it's a composition of Pattern #28 + Modal Dialog, not a fundamentally new pattern. Mention as an example consumer of #28. |
| 2026-04-26 | **`Tools/captioning/` directory layout** | Schemas under `schemas/`, capture prompts under `prompts/`, validator script at root. Self-contained; user can run validator without launching the game. |
| 2026-04-26 | **Validation tool produces a report; does NOT generate captions** | Captioning is the user's job (run Gemini externally). Validator's job is to confirm sidecars are present and well-formed before the runtime tries to use them. |
