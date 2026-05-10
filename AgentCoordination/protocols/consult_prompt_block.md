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
