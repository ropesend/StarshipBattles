# PROJ-466: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit directory:** `Reviews/results/2026-05-20_065518_error-audit/`
- **Bundle counts:** Audit verified: 12 CRITICAL/MAJOR (per audit summary) + scattered MINOR | This bundle: 27 verified (26 firm + 1 promoted from uncertain), 0 uncertain unresolved, 3 deferred | Project siblings: none (single project this run).
- **Layer coverage:** ui, strategy, simulation, services, core, assets.
- **Severity breakdown:** 1 CRITICAL (Phase 1), 11 MAJOR (1 coupled into Phase 1, 10 in Phase 2), 15 MINOR (Phase 3).

### Risk Notes (CRITICAL boundary findings)

The single CRITICAL is a session-initialization boundary gap. When galaxy generation fails (e.g. planet shortage at N=1 after all retries), `GameInitializer.initialize()` raises `ValidationException`, which `SessionBootstrap.new_game_state()` re-raises as `SessionInitializationError`, which `GameSession.__init__()` re-raises after setting null-object state. None of the UI-layer construction sites — `screen_router.py:209` (`_on_new_game_start`), `screen_router.py:266` (`_start_quickstart`), or the `new_game_setup_controller.py:186` callback — catch it. The exception propagates through the pygame event pipeline to the top-level `main()` crash handler at `app.py:518`, producing a hard "CRITICAL CRASH" with `crash.log` instead of a recoverable error dialog (e.g. "try a different seed"). The controller additionally calls `self._screen.kill()` immediately after the bare callback, so any future caught error would leave the setup window in an indeterminate state — Phase 1 must keep the window alive on the failure path. This finding and the coupled MAJOR (`new_game_setup_controller.py:186`) share the same root cause and are fixed together in Phase 1.

## Initial Analysis
Independent third-pass verification (a different reader than the OpenCode audit) read every cited `file:line` in the live source on branch `group-b`. All 12 CRITICAL/MAJOR findings and all kept MINOR findings reproduced exactly against current code; line numbers matched except the audit's own verifier had already corrected `battle_runner.py` from 2 sites to 1 (line 314). The audit's broad-except scanner has a known 100% false-positive bug (all 128 sites carry valid `# Intentional` comments) — those are correctly excluded.

## Swarm Findings Summary
Combined analysis from individual agent reports in `findings/`.

### Architecture
[Key architecture points relevant to implementation]

### Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

### Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

### Opportunities Discovered
- [Opportunity 1]

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
