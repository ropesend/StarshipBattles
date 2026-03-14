# Debugging — Bug Ticket Data

This directory stores bug ticket data. The protocols and workflows are in [`Tickets/README.md`](../Tickets/README.md).

## Directory Contents

| Path | Purpose |
|------|---------|
| `active_bugs/BUG-XX.md` | Active bug tickets being worked on |
| `archived_tickets/BUG-XX.md` | Resolved and archived bug tickets |
| `debug_plan.md` | Bug queue dashboard with status tracking |
| `solved_bugs.md` | Index of solved bugs (date, summary, test case) |
| `Prompts/` | Legacy prompt files (being replaced by `/ticket-*` skills) |

## Quick Reference

- **Add a bug:** `/ticket-add bug <description>`
- **Fix a bug:** `/ticket-work bug 42` or `/ticket-next bug`
- **Batch fix:** `/ticket-continue bug`
- **Close a bug:** `/ticket-close bug 42`
- **Full documentation:** See [`Tickets/README.md`](../Tickets/README.md)
