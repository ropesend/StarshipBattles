# PROTOCOL 03a: Batch Closing & Archiving
**Role:** Librarian

**Goal:** Archive multiple confirmed tickets in a single operation.

## Configuration

This protocol is parameterized by ticket type. The calling skill sets these values:

| Variable | Bug | Feature |
|----------|-----|---------|
| TYPE | Bug | Feature |
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Debugging/active_bugs | Features/active_features |
| ARCHIVE_DIR | Debugging/archived_tickets | Features/archived_features |
| DASHBOARD | Debugging/debug_plan.md | Features/feature_plan.md |
| INDEX | Debugging/solved_bugs.md | Features/completed_features.md |

**Input:** List of {PREFIX}-IDs (e.g., {PREFIX}-15, {PREFIX}-27, {PREFIX}-30)

**Procedure:**
For EACH ticket in the provided list:
1. **Update Index:** Append entry to `{INDEX}`
   - Format: `## [{PREFIX}-ID] [Title]`
   - Content: Date Completed, Brief Summary, Key Test Case
2. **Archive Ticket:** MOVE `{ACTIVE_DIR}/[{PREFIX}-ID].md` to `{ARCHIVE_DIR}/[{PREFIX}-ID].md`
   - Do not modify the content of the ticket file; preserve the full logs.
3. **Update Dashboard:** Remove row from `{DASHBOARD}` queue table

**Termination:** Report summary table:
| {PREFIX}-ID | Status |
|-------------|--------|
| {PREFIX}-XX | Archived |
| {PREFIX}-YY | Archived |

Confirm total count: "X tickets archived successfully."
