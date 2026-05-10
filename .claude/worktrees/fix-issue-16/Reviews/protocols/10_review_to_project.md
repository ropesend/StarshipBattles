# PROTOCOL 10: Review to Project
**Role:** Review Coordinator
**Purpose:** Interactively create a project from a completed code review's findings.

---

## Overview

This protocol guides the transformation of a completed code review into an actionable project. It provides an interactive workflow where users can select which findings to address, customize the project title, and create a properly structured project.

**Best For:**
- Converting review findings into structured remediation work
- Creating focused projects from specific review findings
- Systematic follow-up on code review results

**Key Differentiator:** Unlike other review protocols that analyze code, this protocol transforms existing review results into actionable projects.

---

## Prerequisites

- A completed review in `Reviews/results/` with a valid `report.md`
- The review must have been compiled (findings in report.md)

---

## Phase A: Review Selection

**Goal:** Validate the provided review folder and display its metadata.

### Step 1: Validate Review Folder

Check that the provided folder exists:
```bash
# If user provided just a folder name
ls Reviews/results/<folder_name>/report.md

# If user provided a full path
ls <provided_path>/report.md
```

If the folder or report.md doesn't exist:
- List available reviews in `Reviews/results/`
- Ask user to select from available reviews or correct the path

### Step 2: Display Review Metadata

Parse the report.md header and present:
```
Review Found: {FOLDER_NAME}
===========================================
Date:         {REVIEW_DATE}
Type:         {REVIEW_TYPE}
Total Findings: {TOTAL_COUNT}
  - Critical: {CRITICAL_COUNT}
  - Major:    {MAJOR_COUNT}
  - Minor:    {MINOR_COUNT}
  - Info:     {INFO_COUNT}
```

### Step 3: Run Dry-Run Analysis

Execute the dry-run to show what would be parsed:
```bash
python Reviews/scripts/review_to_project.py <folder> --dry-run
```

This shows:
- How many findings were parsed
- Breakdown by severity
- Sample findings
- Potential warnings about parsing

Present the dry-run output to the user for verification.

---

## Phase B: Finding Selection

**Goal:** Let the user choose which findings to include in the project.

### Step 1: Present Selection Options

Use AskUserQuestion with these options:

**Question:** "Which findings should be included in the project?"

**Options:**
1. **All findings** - Include Critical, Major, Minor, and Info (comprehensive remediation)
2. **Critical + Major** - Focus on high-impact issues only
3. **Critical only** - Address only the most severe issues
4. **Specific findings** - I'll specify finding IDs

### Step 2: Handle "Specific findings" Choice

If user selects option 4:
- Display the full findings table from the dry-run
- Ask user to provide comma-separated finding IDs
- Example: "SEC-01, SEC-02, IV-01, CQ-05"

### Step 3: Confirm Selection

Display summary:
```
Selected Findings: {COUNT}
  - Critical: {N}
  - Major:    {N}
  - Minor:    {N}
  - Info:     {N}

This will create a project with {PHASE_COUNT} phase(s).
```

---

## Phase C: Project Configuration

**Goal:** Configure the project title and confirm settings.

### Step 1: Present Auto-Generated Title

The script auto-generates a title from the review folder name:
```
Auto-generated title: "{GENERATED_TITLE}"
Example: "General Remediation: Full Codebase Maintainability"
```

### Step 2: Ask About Title

Use AskUserQuestion:

**Question:** "Do you want to customize the project title?"

**Options:**
1. **Use auto-generated title** - Keep: "{GENERATED_TITLE}"
2. **Custom title** - I'll provide my own title

If user selects option 2, ask for the custom title.

### Step 3: Confirm Configuration

Display final configuration:
```
Project Configuration
=====================
Title:     {FINAL_TITLE}
Findings:  {COUNT} selected
Phases:    {PHASE_COUNT} (based on severity grouping)
  - Phase 1: Critical Fixes ({N} tasks) [if applicable]
  - Phase 2: Major Issues ({N} tasks) [if applicable]
  - Phase 3: Cleanup ({N} tasks) [if applicable]

Proceed with project creation?
```

---

## Phase D: Project Creation

**Goal:** Create the project structure using the script.

### Step 1: Build Command

Construct the appropriate command based on user selections:

```bash
# All Critical + Major (default script behavior)
python Reviews/scripts/review_to_project.py <folder>

# All findings
python Reviews/scripts/review_to_project.py <folder> --findings ALL

# Specific findings
python Reviews/scripts/review_to_project.py <folder> --findings "SEC-01,SEC-02,IV-01"

# With custom title
python Reviews/scripts/review_to_project.py <folder> --title "Custom Title"

# Combined options
python Reviews/scripts/review_to_project.py <folder> --title "Custom Title" --findings "SEC-01,SEC-02"
```

**Note:** For "All findings", you'll need to pass all finding IDs since the script defaults to Critical+Major. Extract all IDs from the dry-run output.

### Step 2: Execute Command

Run the command and capture output:
```bash
python Reviews/scripts/review_to_project.py <folder> [options]
```

### Step 3: Verify Creation

Confirm the project was created:
- Check for the PROJ-XX directory in `Projects/active_projects/`
- Verify key files exist: plan.md, design.md, phase_N_checklist.md

---

## Phase E: Handoff

**Goal:** Present the created project and provide clear next steps.

### Step 1: Display Project Summary

```
PROJECT CREATED SUCCESSFULLY
============================
Project ID:   {PROJ-XX}
Directory:    Projects/active_projects/{PROJ-XX}/

Files Created:
  - plan.md (main project document)
  - design.md (review findings summary)
  - decisions.md (decision log)
  - phase_1_checklist.md
  - phase_2_checklist.md (if applicable)
  - phase_3_checklist.md (if applicable)
  - findings/ (directory for agent reports)
```

### Step 2: Provide Next Steps

```
NEXT STEPS
==========
1. Review the generated plan:
   Open: Projects/active_projects/{PROJ-XX}/plan.md

2. Optionally refine phase checklists:
   - Add more specific subtasks
   - Adjust effort estimates
   - Add relevant test paths

3. Start implementation:
   Use the "Continue Project" prompt with {PROJ-XX}

   Or run directly:
   python Projects/scripts/current_task.py {PROJ-XX}
```

### Step 3: Offer Additional Actions

Use AskUserQuestion:

**Question:** "What would you like to do next?"

**Options:**
1. **Open plan.md** - View the generated project plan
2. **Start working** - Begin with the Continue Project workflow
3. **Done for now** - I'll return to this later

---

## Script Reference

### review_to_project.py Options

| Option | Description |
|--------|-------------|
| `<review_folder>` | Required. Folder name or path to the review |
| `--dry-run`, `-n` | Show what would be parsed without creating files |
| `--title`, `-t` | Custom project title |
| `--findings`, `-f` | Comma-separated finding IDs to include |
| `--no-create-project` | Generate handoff document only (legacy mode) |

### Examples

```bash
# Preview what would be parsed
python Reviews/scripts/review_to_project.py 2026-01-24_general_full-codebase-maintainability --dry-run

# Create project with default settings (Critical + Major)
python Reviews/scripts/review_to_project.py 2026-01-24_general_full-codebase-maintainability

# Create project with custom title
python Reviews/scripts/review_to_project.py 2026-01-24_general_full-codebase-maintainability --title "Maintainability Sprint 1"

# Create project with specific findings
python Reviews/scripts/review_to_project.py 2026-01-24_general_full-codebase-maintainability --findings "AR-01,AR-02,CQ-01,CQ-05"
```

---

## Troubleshooting

### "No findings were parsed"
- Verify the report.md exists and contains a "Findings by" section
- Check report format matches expected table structure
- Use `--dry-run` to see parsing details

### "Projects utilities not available"
- Ensure `Projects/scripts/utils/` directory exists
- Check that index_manager.py and config.py are present

### Project created but phases seem wrong
- Review the findings selection
- Consider using specific finding IDs for precise control
- Manually adjust phase_N_checklist.md files if needed
