# Review Report: GitHub Issues Migration Plan

**Reviewer:** OpenCode (ocode-review-request skill)
**Request ID:** req_20260502_201926_5ac40b
**Date:** 2026-05-02
**Overall Recommendation:** APPROVE-WITH-EDITS

The plan is fundamentally well-structured and correctly identifies the key design dimensions. Its architecture is sound: label-driven status, parallel rollout, preserved authority model, and deliberate out-of-scope decisions. However, it has 2 critical security gaps in the authority model, 6 major omissions that should be resolved before rollout, and ~11 minor/nit issues that improve quality if addressed. The plan should move forward with these edits — no fundamental redesign needed.

---

## CRITICAL Findings

### CRIT-001: Authority bypass — agent can add `verified` label then close

**Location:** "Optional Safety-Net Action" section, the `tracking-guard.yml` workflow

**Issue:** The safety-net action checks for `verified` label presence at close time but does NOT verify WHO added it. As designed:

1. Agent adds `verified` label via `gh issue edit --add-label verified` (violating the convention rule).
2. Agent closes the issue via `gh issue close <#>`.
3. Safety-net action evaluates: `sender != 'ropesend'` (true) AND `!contains(labels, 'verified')` (false — `verified` IS present).
4. Condition evaluates to `false` — action does not fire. Issue stays closed.

The convention rule ("Agents MUST NOT add the 'verified' label") has zero technical enforcement. The safety-net action, which is supposed to be the enforcement layer, does not close this gap. A single actor who adds the label and closes the issue in sequence defeats both protections.

**Suggested fix:** Add a second safety-net action that fires on `issues: [labeled]` events, checks if the `verified` label was added by a non-owner actor, and auto-removes it with a comment:
```yaml
on:
  issues:
    types: [labeled]
jobs:
  guard-verified:
    if: github.event.label.name == 'verified' && github.event.sender.login != 'ropesend'
    runs-on: ubuntu-latest
    steps:
      - run: gh issue edit ${{ github.event.issue.number }} --remove-label verified
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - run: gh issue comment ${{ github.event.issue.number }} --body "The 'verified' label may only be applied by the repo owner."
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
This makes the `verified` label technically impossible for non-owners to hold, closing the bypass.

---

### CRIT-002: Status label invariant has zero enforcement

**Location:** "Label Schema" section, invariant statement: "exactly one `type:*`, one `priority:*`, one `status:*` per open issue."

**Issue:** The plan states this invariant but defers enforcement entirely to agent-prompt discipline with "The new skills enforce this; a future Action can audit it." In practice:

- The `gh issue edit --add-label status:in-progress` command does not remove `status:pending`. The agent must remember a separate `--remove-label status:pending`.
- Nothing prevents adding `status:in-progress` alongside `status:pending` or any other combination.
- Two `status:*` labels on one issue creates ambiguity for every downstream consumer (skills, queries, dashboard views).
- The proposed "one-shot" label application from `gh label create` has no validation logic.

**Suggested fix:** Either:
1. (Preferred) Write a small GitHub Action that fires on `issues: [labeled]` events. If the issue now has 2+ `status:*` labels, remove all but the most recently added one and comment a warning. This is ~15 lines of YAML.
2. (Fallback) In every skill's SKILL.md, hardcode the atomic replace pattern: `gh issue edit <#> --remove-label status:pending --add-label status:in-progress`. Make this a non-negotiable instruction. This reduces but doesn't eliminate the risk.

Given that the labeled-event action is straightforward to implement, option 1 is strongly preferred and should be part of the initial rollout, not deferred.

---

## MAJOR Findings

### MAJ-001: Safety-net action marked optional — should be non-optional for initial rollout

**Location:** "Optional Safety-Net Action" section; "Verification Plan" step 7

**Issue:** The safety-net action is described as "recommended but optional — implement after the main rollout if you want it." The verification plan (step 7) even says "If the safety-net Action is enabled..." — treating it as contingent.

The close-authority rule is one of the primary constraints from the user ("Today, agents architecturally cannot close tickets — only the user can. This must carry forward."). Making this enforcement optional means the initial rollout has a gap in its primary security requirement.

**Suggested fix:** Make the safety-net action non-optional in the plan. It should be listed under "Critical Files to Create" without the `*(optional)*` qualifier. The verification plan step 7 should read: "The safety-net action MUST be enabled before the first real ticket close." If the user wants no actions at all, the plan should explicitly document that risk acceptance.

---

### MAJ-002: No offline/rate-limit fallback strategy

**Location:** Missing from plan entirely

**Issue:** The plan has no acknowledgment of degraded-mode operation. Four failure domains are unaddressed:

1. **Rate limiting:** GitHub REST API is 5000 req/hr for authenticated users. Agent batch loops (`gi-continue`) doing rapid issue operations could hit this. What happens?
2. **Network down:** `gh` CLI fails all commands. Agent attempts to create/work/update tickets produce errors with no fallback.
3. **GitHub outage:** Same as network-down, but potentially extended (hours).
4. **`gh` CLI not installed/auth'd:** The plan mentions `winget install GitHub.cli` and `gh auth login` but those are manual setup steps. If an agent trys a `gi-*` skill without `gh`, it errors.

The current `Tracking/` system works 100% offline. The plan's migration to GitHub Issues removes that property with no mitigation.

**Suggested fix:** Add a "Degraded Mode" section to the plan:
1. Agents should write a local markdown draft (in `Tracking/bugs/active/` or `Tracking/features/active/`) when `gh` is unavailable, using the old ticket format but recording the intended GitHub issue #.
2. A sync script (or the next agent session) converts the draft to a real GitHub issue when connectivity returns.
3. The old `Tracking/` system serves as the offline fallback during the parallel period — the plan already keeps it running. Explicitly document this role.

---

### MAJ-003: No cutover criteria or sunset checklist

**Location:** "Migration cutover" concept mentioned in Context but never defined operationally

**Issue:** The plan says the old system runs in parallel and "sunset later, on your call" with zero criteria for what "ready" means. Risks:

- The parallel period could extend indefinitely (months/years), doubling operational complexity.
- Without criteria, the user has no checklist to evaluate readiness.
- Ambiguity about when agents should stop using old skills entirely and when old skills should be removed.

**Suggested fix:** Add a "Cutover Criteria" section to the plan with concrete checklist items:
1. All active tickets migrated (or explicitly closed as won't-migrate).
2. `/claude-gi-*` skills have been used end-to-end for ≥5 real tickets (bugs + features).
3. QA-observer is integrated with the new system.
4. Safety-net action has been tested and functions correctly against a non-owner token.
5. The user has not used any old `/claude-ticket-*` skill for ≥1 week.
6. Backups: `Tracking/` directory committed as final state; GitHub Issues exported via `gh issue list --json ... > export.json` for offline archive.
7. Old skills archived (moved to `_marked_for_deletion/`) in a single commit with a dated rationale note.

---

### MAJ-004: QA-observer integration deferred but is primary bug creator

**Location:** "Screenshot & Log Workflow" and "Open Questions / Out-of-Plan Follow-Ups"

**Issue:** The plan states that QA-observer integration is "scoped as out-of-plan follow-up." However, the QA observer (`Tools/qa_observer/`) is described in the Context as the primary creator of bug tickets. Deferring its integration means:

- New bugs automatically created by QA go to the OLD system (`/claude-ticket-add`) while features go to the NEW system — creating the worst-case dual-tracking scenario.
- The parallel period's complexity is amplified because the user must manage bugs in two different systems.
- If the QA observer is manually invoked, it still writes to the old system unless disabled or updated.

**Suggested fix:** Include QA-observer integration in the initial rollout scope. The change is described in the plan as small ("a one-line redirect to copy → `tracking-assets/screenshots/` and invoke `/claude-gi-add`"). This should be done as part of the initial implementation, not deferred. The plan correctly identifies that `anti-qa-triage` needs a small update — just don't defer it.

---

### MAJ-005: No dual-tracking interaction rules during parallel period

**Location:** Missing from plan entirely

**Issue:** During the parallel period, the system has two skill prefixes (`/claude-ticket-*` and `/claude-gi-*`) that create and manage tickets. The plan doesn't describe:

- Which system should agents use for NEW tickets?
- What happens if the user accidentally uses the old prefix?
- How should agents reference tickets across the two systems?
- When should old skills stop being used?

Without explicit rules, agents could create a bug in the old system and a feature in the new system, with cross-references that don't resolve. Or worse, an agent could start working on a ticket in one system and try to close it in the other.

**Suggested fix:** Add an "Interaction Rules" section to the plan:
1. **New tickets:** All new tickets go to GitHub Issues (`/claude-gi-*`). The old skills are for completing in-flight tickets only.
2. **In-flight tickets:** Old `/claude-ticket-*` skills continue to operate on tickets already in `Tracking/bugs/active/` and `Tracking/features/active/`. Once all in-flight tickets are closed, old skills should not be invoked.
3. **No cross-system references:** Old tickets reference old IDs (BUG-XX/FEAT-XX); new tickets reference GitHub #NNN. Do not mix.
4. **Old skill deprecation notice:** Each old skill's prompt should include a header: "This skill is deprecated. Use `/claude-gi-add` for new tickets. This skill is for completing existing in-flight tickets only."

---

### MAJ-006: No backup/export strategy from GitHub Issues

**Location:** Missing from plan entirely

**Issue:** The current markdown-on-disk system is inherently portable — the entire ticket history is just files in a directory, versioned in git alongside the code. Migrating to GitHub Issues creates a vendor dependency: if GitHub Issues is ever abandoned (or the repo moves to another platform), all ticket history must be exported.

The plan has no export strategy. A one-shot export script at sunset time would produce a snapshot but not a live backup. If GitHub's API changes or the repo is deleted, the ticket history is lost.

**Suggested fix:** Add a backup strategy to the plan:
1. **Automated daily export:** A small script that runs `gh issue list --state all --json ... > AgentCoordination/generated/github_issues_export.json`.
2. **Per-issue backup:** A script that exports each issue body + comments as a markdown file (e.g., `gi-export/NNN-slug.md`) — this can be run manually before sunset.
3. **Commit the exports to git:** `AgentCoordination/generated/gi-exports/` as a committed directory, so ticket history exists in the repo even if GitHub goes away.

This aligns with the user's pattern of keeping everything in version control.

---

## MINOR Findings

### MIN-001: Status transition atomicity not documented

**Location:** "Skill Designs" section — each skill that flips status

**Issue:** Skills that transition status (e.g., `gi-work` setting `status:pending` → `status:in-progress` → `status:awaiting-confirmation`) do not explicitly document the atomic replace pattern. `gh issue edit` requires both `--remove-label` and `--add-label` in one invocation to be atomic:
```bash
gh issue edit <#> --remove-label status:pending --add-label status:in-progress
```
Without this, a two-step edit (remove then add) has a window where the issue has zero `status:*` labels.

**Suggested fix:** In each skill's SKILL.md, hardcode the atomic pattern with both flags in one call. Add a note that `gh issue edit` with both flags is a single API call (atomic).

---

### MIN-002: No `--body-file` usage for large comment bodies

**Location:** "Skill Designs" — `gi-work` and `gi-deep-dive` posting comments

**Issue:** The plan uses `gh issue comment <#> --body "..."` for all comment posting. The work-log entries from Protocol 02 are structured, multi-paragraph documents that can be thousands of words. Shell escaping for multi-line bodies with special characters is fragile, especially on Windows PowerShell.

**Suggested fix:** Document `--body-file` as the preferred mechanism for any comment body exceeding ~200 characters:
```bash
gh issue comment <#> --body-file work_log_phase_0.md
```
Agents write the comment body to a temp file first, then attach it. This avoids quoting issues and supports any content that fits in a file.

---

### MIN-003: No pagination strategy for `gh issue list`

**Location:** "Skill Designs" — `gi-next` and any skill that queries issue lists

**Issue:** `gh issue list` defaults to 30 results. The `gi-next` skill needs to find the highest-priority pending issue. If there are more than 30 pending issues, the default query might miss the highest-priority one. Using `gh issue list --limit 100` is trivial but not documented.

**Suggested fix:** Add `--limit 100` (or a higher appropriate number) to all `gh issue list` invocations in the skill designs. Also document `--search` for more complex queries if needed.

---

### MIN-004: Structured work log may lose rigor when scattered across comments

**Location:** "Issue body structure" design decision

**Issue:** Protocol 02 (`02_work_ticket.md`) defines a highly structured work log with named phases (Phase 0, Phase 1, Phase 2, Phase 2.5, Phase 4), mandatory gates, and specific section formats. When this is pushed into GitHub comments instead of a single document:

- Comments feel more informal — agents might skip structured headings or omit gates.
- Reading the full audit trail requires scrolling through multiple comments rather than one linear document.
- GitHub comments don't render with the same visual weight as a dedicated work-log section in a markdown file.

This is a minor concern because GitHub comments DO support full markdown and threading. The same structure can be maintained if each phase gets its own comment with clear `### Phase N` headings. The plan should explicitly carry forward the structured format.

**Suggested fix:** In the `gi-work` skill description, add explicit instruction: "Each work-log phase produces its own comment with a clear `### Phase N: <Name>` heading. The structure from `Tracking/protocols/02_work_ticket.md` is preserved verbatim — only the storage location changes (comment instead of file section)."

---

### MIN-005: Screenshot growth threshold not defined

**Location:** "Screenshots" design decision: "Plain repo folder... No LFS"

**Issue:** Every screenshot committed to the repo is in clone history forever. The plan correctly notes this but sets no threshold for when growth becomes a problem that requires mitigation (LFS, git-lfs migrate, cleanup policy, or external hosting).

At a rough estimate: 4K game screenshots are ~2-8 MB each as PNG. At 10-20 new bugs/month, that's ~50-100 MB/year in screenshot storage. After 2-3 years, `tracking-assets/` could exceed 200-300 MB, making clone times noticeably slower.

**Suggested fix:** Add a growth threshold statement: "Track `tracking-assets/` directory size. Revisit the no-LFS decision if it exceeds 200 MB. Options at that point: migrate to Git LFS for all `tracking-assets/`, add a cleanup policy (delete screenshots older than N months from active tracking, keeping them only in the historical archive), or move to external hosting."

---

### MIN-006: No specific `--repo` flag in skill `gh` command descriptions

**Location:** "Skill Designs" section — all skill descriptions

**Issue:** All `gh` commands in the skill descriptions assume the current working directory is the repo root and `GH_REPO` is set. If an agent is in a different working directory or `GH_REPO` is not set, `gh` commands will fail or target the wrong repo.

**Suggested fix:** Either: (a) specify that each skill should set `GH_REPO=ropesend/StarshipBattles` as an environment variable before issuing `gh` commands, or (b) add `--repo ropesend/StarshipBattles` to every `gh` invocation in the skill descriptions.

---

## NIT Findings

### NIT-001: BUG-/FEAT- prefix loss has no functional impact

**Location:** "ID strategy" design decision

**Issue:** Dropping BUG-/FEAT- prefixes means issue numbers alone don't communicate type. This is addressed by `type:*` labels, which are equally effective. Existing PROJ-XX docs stay frozen with old IDs. New cross-references use `#NNN` (auto-linked by GitHub). No functional degradation.

**Suggested fix:** None needed. Noted for completeness.

---

### NIT-002: Safety-net action uses GITHUB_TOKEN, not user PAT

**Location:** "Authentication/scope" section

**Issue:** The plan correctly states scopes needed are "repo, workflow if Actions are added." The safety-net action uses `${{ secrets.GITHUB_TOKEN }}` (auto-provided), which has repo scope for the current repo. The user's PAT only needs `workflow` scope if they want to manage workflow files or dispatch workflows from the CLI. Small clarification for completeness.

**Suggested fix:** Add a sentence: "Note: the safety-net Action uses `GITHUB_TOKEN` (auto-provided), not your PAT. The `workflow` scope is only needed on your PAT if you plan to manage workflow files or dispatch Actions from the CLI."

---

### NIT-003: Config.yml `blank_issues_enabled: false` syntax not explicitly shown

**Location:** "Issue Templates" section

**Issue:** The plan mentions `config.yml` disables blank issues but doesn't show the exact syntax:
```yaml
blank_issues_enabled: false
```
This is a one-line file. Including it explicitly removes any ambiguity.

**Suggested fix:** Add the full `config.yml` content in the plan.

---

### NIT-004: Skill count mapping conflates bug/feature variants

**Location:** "Skill Designs" table

**Issue:** The old system lists 16 skills in `Tracking/README.md` but there are actually 10 skill names, each accepting `bug` or `feature` as an argument. The new system has 10 skills with the same pattern. The plan's skill table correctly maps 10-to-10 but doesn't clarify that the old system's 16 count includes type-parameterized invocations. This is purely a counting convention — no functional issue.

**Suggested fix:** None needed. Noted for completeness.

---

### NIT-005: Projects-out-of-scope reasoning is comprehensive and sound

**Location:** "Projects System — Out of Scope" section

**Issue:** The plan's reasoning for excluding Projects from migration is thorough: different structure (multi-phase, 11+ files per project), local-first dependencies (manifest conflict detection, handoff prompts, context-threshold awareness, role rotation), mature existing tooling (13 protocols, 10+ scripts, 10 skills), and no public-visibility benefit. The cross-reference convention (`Related: PROJ-313` in issues, `Resolves #127` in project docs) is lightweight and appropriate.

**Suggested fix:** None needed. The reasoning is sound. Noted for completeness.

---

### NIT-006: Issue template syntax and `default labels` mechanism are accurate

**Location:** "Issue Templates" section

**Issue:** The plan describes YAML issue forms with `textarea` and `dropdown` fields. The `labels:` key in the YAML frontmatter to set default labels is correct per current GitHub Issues forms spec. The `type: input` / `type: textarea` / `type: dropdown` field types are all valid for issue forms.

**Suggested fix:** None needed. The template syntax is accurate.

---

## Overall Recommendation

**APPROVE-WITH-EDITS**

The plan's architecture is fundamentally sound: label-driven status model, parallel rollout, preserved authority model, and sensible out-of-scope decisions. The critical path to implementation requires resolving:

1. **CRIT-001 and CRIT-002** (authority bypass + status invariant enforcement) — add labeled-event actions before the first real ticket is closed. These are ~30 lines of YAML total.
2. **MAJ-001 through MAJ-006** — make the safety-net non-optional, add offline fallback, define cutover criteria, include QA-observer integration, define dual-tracking rules, and add an export strategy. These are additions to the plan document, not redesigns.

Once these edits are in the plan, implementation can proceed with no further review needed. The `gh` CLI patterns, template syntax, label schema, and skill designs are all correct as described.

**Verification priority after implementation:**
1. Enforce CRIT-001: attempt to close an issue from a non-owner account after adding `verified` label — must auto-reopen.
2. Enforce CRIT-002: add two `status:*` labels to an issue — must auto-correct.
3. Enforce MAJ-002: run a skill with `gh` unauthenticated — must produce a clear error and fallback path.
4. Enforce MAJ-005: use `/claude-ticket-add` during parallel period — must warn about deprecation.
