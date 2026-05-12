---
protocol: consult/v1
from: claude
to: codex
mode: planning
allow_tests: false
created_at_utc: 2026-05-12T01:09:17Z
repo_root: C:/Dev/Starship Battles
consult_leaf: C:\Dev\Starship Battles\AgentCoordination\Scratchpad\Consult\20260512T010825Z_gp-create-about-author
complete: true
---

## Question

Please review this draft project plan for the new claude-gp-* system's first real invocation. This is the smoke test the user requested; treat it as a normal consult, not a softball.

## Project meta
- Title: Add "About the Author" button to main menu
- Source: manual
- Type: feature
- Priority: low

## Overview
Add a new button labeled "About the Author" to the main menu (MenuScene). When clicked, display the text "The author is Ross McLean." in a small dismissible dialog/overlay, then return to the menu.

## Goals
- Add a clickable button "About the Author" on the main menu
- Clicking the button displays attribution text: "The author is Ross McLean."
- The display is dismissible (returns the user to the main menu cleanly)
- No regressions in the existing 10 main-menu buttons

## Scope
**In:**
- New tuple entry in game/app.py:_get_menu_button_config() (currently lines 141-154)
- New callback method on GameApp (e.g., _show_about_author) that opens the about display
- Minimal about-display surface — either a small modal overlay or reuse of an existing overlay pattern
- Test coverage that the new button is present in the menu config and that clicking invokes the callback

**Out:**
- Multi-author / contributor list
- Localization / i18n
- Persistent dismissed state
- A wider Settings or About-this-game menu
- Theme / styling changes beyond what the existing button system provides

## Key Files
- game/app.py — adds button config entry + callback. Lines 141-154 today.
- game/ui/screens/menu_scene.py — already config-driven via button_config: List[Tuple[str, Callable]] — no source changes expected unless layout needs adjustment for an 11th button
- game/ui/screens/about_author_dialog.py (NEW, tentative) — the dialog overlay
- tests/unit/ui/test_menu_button_config.py (NEW, tentative) — failing test then verify

## Phase breakdown

### Phase 1 — Implement button + callback + display
Checklist:
- Write failing test asserting "About the Author" appears in _get_menu_button_config() return value
- Add ("About the Author", self._show_about_author) tuple to the list
- Implement _show_about_author method on GameApp
- If creating a new dialog: write game/ui/screens/about_author_dialog.py with a minimal pygame_gui overlay
- Manual smoke: launch app, click button, verify text appears, verify dismiss returns to menu
- All targeted tests passing

### Phase 2 — Verification + doc sync
Checklist:
- Sharded suite or targeted UI tests pass
- Verify all 10 pre-existing menu buttons still functional
- Verify menu layout with 11 buttons still fits at minimum 2560x1600 resolution
- If any doc enumerates the menu buttons, update it
- Update parent's Quick Status before stopping

## Design notes
MenuScene.__init__ accepts button_config: List[Tuple[str, Callable]]. _create_buttons() iterates and creates UIButton instances at vertically-stacked positions: self.height // 2 - 320 + i * 70. Adding an 11th button is a single tuple addition; layout math places it 70px below "Galaxy Test". At 1600px height, button stack starts at y=480 and 11th button lands at y=1180. Comfortable at the 2560x1600 minimum target.

## What I'm asking
1. Scope sanity — is the in/out scope coherent? Anything else this should explicitly NOT do?
2. Phase ordering — is implement + verify the right cut, or should phase 2 just be a verification section inside phase 1?
3. Risks not yet listed — what could go wrong that the draft doesn't acknowledge?
4. Reuse vs new dialog — should the plan commit upfront to either reusing an existing overlay pattern OR creating about_author_dialog.py, rather than leaving it as a Phase-1 decision?

Constraints:
- This is a real run of the new claude-gp-* system, not a hypothetical. Whatever you advise lands in the parent issue body.
- Sequential execution only in v1.


## Repo state

Branch: main

```
 M AgentCoordination/generated/skill_usage/by_install/21f3651f7ffa42f8acdab05bd0a3c1bf.json


```

## Constraints

Read and honor the canonical consult prompt block. The file's verbatim content follows; the source of truth is `C:\Dev\Starship Battles\AgentCoordination\protocols\consult_prompt_block.md`.

---
protocol_version: 1.0
last_verified_utc: 2026-05-09T19:11:30Z
status: canonical
---

# Standard Consult Prompt Block

This is the canonical Starship Battles consult constraints text. Both
initiator and responder skills (Claude, Codex, OpenCode) read this file
verbatim and embed it into the request body's `## Constraints` section.
Skills MUST NOT inline a separate copy.

Reference: `AgentCoordination/Scratchpad/Discussion/20260509T170814Z_consult-discuss-harmonize/plans/consult_harmonization_r002.md`
and the smoke-driven follow-up plan at `AgentCoordination/Scratchpad/Discussion/20260509T190300Z_smoke-findings-merge/plans/consult_v1_smoke_fixes_r001.md`.

## Constraints

- Strict TDD: identify failing tests first; don't propose code that bypasses this.
- Documentation first: reference `docs/` as source of truth; never read or cite `docs/_ignore/`.
- No backward-compat shims, monkey patches, fallback systems, or save-file migrations.
- Respect layer boundaries (per `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`).
- Do NOT revert unrelated user changes; work around existing dirty state.
- Evidence standard: cite `file:line`, command output, or transcript. Label unverified claims `[unverified]`.
- Final ownership: the initiator owns synthesis. You advise; you do NOT implement.
- Follow-up rule: the initiator may ask follow-ups. You stop when advice converges or repeats.
- Permission contract: read repo, run tests only when `allow_tests: true` AND the mode is `pre-final-check` or `deep-dive`, write only inside the directory named by `consult_leaf` in the request frontmatter. Do NOT edit production code, docs, tickets, projects, configs, commits, branches, or PRs.

## Update procedure

When this block changes:

1. Edit the bullet list above.
2. Bump `last_verified_utc` in frontmatter.
3. Both Claude and Codex initiator/responder skills will pick up the new text on next invocation since they read the file at runtime.
4. No skill-file edits required for content-only changes.


## Specific asks

Reply by writing `response.md` in this consult leaf (path in `consult_leaf` frontmatter) with the schema:

```yaml
---
protocol: consult/v1
from: codex
to: claude
mode: planning
created_at_utc: <ISO 8601 UTC>
complete: true
exit_status: ok            # or: partial (with explanation in ## Open questions) | error (with error_kind)
---
```

Body sections, in order:

1. `## Findings` — direct answers to the question above, evidence-cited (`file:line`).
2. `## Risks` — what the initiator might miss.
3. `## Open questions` — what you lack information to advise on (do NOT speculate). REQUIRED if `exit_status: partial`.