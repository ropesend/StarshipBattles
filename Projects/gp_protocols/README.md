# gp_protocols/ — GitHub-backed Project workflow protocols

These protocols are the workflow logic for the `claude-gp-*` skill family,
which manages projects whose state lives on GitHub (Issues + Projects v2
board) rather than under `Projects/active_projects/`.

`gp_protocols/` runs **in parallel** with the legacy `Projects/protocols/`
(01..20). The legacy protocols continue to power the existing `claude-proj-*`
skills for the 12 active local projects (PROJ-401..412). Both systems coexist
until the user signs off on the new one.

## Protocol index

| # | File | Used by | Purpose |
|---|------|---------|---------|
| 01 | [01_create_gp_project.md](01_create_gp_project.md) | `claude-gp-add`, `claude-gp-from-audit`, `claude-gp-revise`, `claude-gp-extract-phase` | Shared creation procedure: draft plan → blocking codex consult → fingerprint → GitHub issue + sub-issues → asset commit → board write |
| 02 | [02_continue_gp_project.md](02_continue_gp_project.md) | `claude-gp-continue` | Sequential TDD work loop on the active phase sub-issue |
| 03 | [03_review_gp_project.md](03_review_gp_project.md) | `claude-gp-review` | Five-agent plan validation; results posted as parent-issue comment |
| 04 | [04_audit_gp_project.md](04_audit_gp_project.md) | `claude-gp-audit` | Skeptical post-completion audit; transitions to `status:awaiting-confirmation` |
| 05 | [05_close_gp_project.md](05_close_gp_project.md) | `claude-gp-close` | Move assets to `tracking-assets/projects/archived/`, close issue tree |
| 06 | [06_revise_gp_project.md](06_revise_gp_project.md) | `claude-gp-revise` | Reopen a closed project, add new phases (uses 01 for the new phases) |
| 07 | [07_extract_phase_gp.md](07_extract_phase_gp.md) | `claude-gp-extract-phase` | Split a phase from one project into its own project (uses 01 for the new project) |

## Per-audit-type bundling protocols

`claude-gp-from-audit --type <kind>` reuses the existing per-audit-type
protocols under `Projects/protocols/` for the verification and bundling logic.
Only the wrapper changes (GitHub issue creation, codex consult, asset commit)
— the per-type verification + bundling stays exactly as it is today.

| `--type` value | Per-type protocol | Notes |
|---|---|---|
| `shrink` | `Projects/protocols/11_create_from_shrink_audit.md` | Fixed category grouping |
| `test-review` | `Projects/protocols/12_create_from_test_review.md` | P0/P1/P2 split |
| `type` | `Projects/protocols/13_create_from_type_audit.md` | Includes strict-mode migration |
| `error` | `Projects/protocols/14_create_from_error_audit.md` | Crash-risk callouts |
| `legacy` | `Projects/protocols/16_create_from_legacy_audit.md` | Removal cluster bundling |
| `docs` | `Projects/protocols/17_create_from_docs_audit.md` | Doc-file-cluster bundling |
| `pattern` | `Projects/protocols/18_create_from_pattern_audit.md` | Layer + pattern-area bundling |
| `state` | `Projects/protocols/19_create_from_state_audit.md` | Singleton-or-mechanism bundling |
| `testcoverage` | `Projects/protocols/20_create_from_testcoverage_audit.md` | Layer + module cluster bundling |

The dispatcher reads the existing protocol's verification + bundling output,
then hands the verified bundle to `01_create_gp_project.md` for the
GitHub-issue creation phase.

## Constraint inheritance

All `gp_protocols/` inherit from `AGENTS.md` and the design-locked plan at
`AgentCoordination/Scratchpad/plans/github_projects_system_proposal.md`.
Key constraints from that plan:

- v1 ships **sequential-only execution**. `02_continue_gp_project.md` does not
  implement phase-aware (`03c` equivalent) or parallel (`03b` /
  `claude-gp-parallel`) execution. Those are deferred to a follow-up design
  pass.
- **Mandatory blocking codex consult** on every creation path
  (`01`, `06`, `07`). User override is allowed only as visible incident
  handling (`consult:overridden` label + parent comment + board field).
- **New project IDs are `GP-<issue-number>`**, not `PROJ-NNN`. The
  `PROJ-NNN` namespace is owned by the legacy system and must not be reused.
- **Decisions live as parent-issue comments**, not in a local `decisions.md`.
- **Tracking-assets directory holds static reference docs only.** Live state
  belongs on GitHub.

## Authority

`claude-gp-*` skills may:
- Create, edit, label, comment on `type:project` and `type:project-phase`
  issues
- Add issues to the GitHub Projects v2 board and set its custom fields
- Commit to `tracking-assets/projects/GP-<n>/`
- Atomically flip `status:*`, `phase:*`, `consult:*`, `asset-state:*` labels

They **may not**:
- Apply the `verified` label
- Close any issue (`gh issue close`) — user-only
- Mutate the legacy `Projects/active_projects/` tree or `projects_index.md`

Override of the mandatory codex consult is **user-owned incident handling**.
Skills cannot select override autonomously; they must HALT and ask.
