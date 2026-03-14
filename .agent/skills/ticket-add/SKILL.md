---
name: ticket-add
description: Create new bug or feature tickets (e.g., /ticket-add bug <descriptions> or /ticket-add feature <descriptions>)
disable-model-invocation: true
argument-hint: bug|feature <descriptions>
---

# Add Ticket

**Protocol:** `Tickets/protocols/01_ingest_ticket.md`

Read and follow the full protocol file.

## Your Role

Adopt the **Project Manager** persona. No coding — data entry only.

## Arguments

Parse the first word of `$ARGUMENTS` as the ticket type. Everything after is the ticket description(s).

**Input:** $ARGUMENTS

## Configuration

Set these values based on ticket type:

| | Bug | Feature |
|--|-----|---------|
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Debugging/active_bugs | Features/active_features |
| DASHBOARD | Debugging/debug_plan.md | Features/feature_plan.md |

## Execution

1. **READ** the DASHBOARD to identify the next sequential {PREFIX}-XX ID.
2. **PARSE** the descriptions into separate tickets.
3. **CREATE** ticket files in `{ACTIVE_DIR}/{PREFIX}-XX.md` for each ticket:
   - Paste the exact, raw description into the file
   - Initialize sections: `## Description`, `## Priority`, `## Status (Pending)`, `## Work Log`
   - Set Priority:
     - **Bugs:** Critical (crashes/blocks), High (feature broken), Medium (minor/visual), Low (polish)
     - **Features:** Critical (required for release), High (significant impact), Medium (nice-to-have), Low (minor enhancement)
4. **UPDATE** DASHBOARD with new entries.
5. **REPORT** the IDs created and exit.

**CONSTRAINT:** DO NOT start analysis or write any code. Just perform the data entry.
