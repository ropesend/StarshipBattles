# Doc Consolidation Staging

`docs/01_ARCHITECTURE.md` and `docs/02_PATTERNS.md` are touched by PROJ-457
(Group B), PROJ-459 (Group A), and PROJ-460 (Group C). To avoid three-way merge
conflicts across machines, each project stages its intended doc edits as
`PROJ-<N>_pending.md` in this directory rather than editing the docs directly.

The last of the three projects to close (detected via
`git ls-tree origin/main Projects/active_projects/_doc_consolidation/` —
all three pending files present) is responsible for merging the staged edits
into a single coordinated commit and deleting the pending files.

Full protocol: `AgentCoordination/protocols/group_execution_protocol.md` §9.
