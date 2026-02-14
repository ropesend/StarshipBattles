# PROTOCOL 05b: Close Multiple Projects
**Role:** Batch Project Archivist

**Goal:** Simultaneously archive multiple completed projects, skipping individual audits by default.

---

## Batch Archival Process

**Use the batch archive script (skips validation/audits by default):**

```bash
python Projects/scripts/batch_archive_projects.py PROJ-XX PROJ-YY
```

This script will for EACH project:
1. **SKIP** validation and audit checks (default behavior)
2. Create a backup in `Projects/backups/`
3. Move the project (file or directory) to `archived_projects/`
4. Update `projects_index.md` status to "Archived"

---

## Procedure

### 1. Confirm Project List
List the IDs of the projects to be archived and confirm with the user that they should be moved to the archive. Remind the user that audits are skipped by default.

### 2. Run Batch Archive
Execute the following command:
```bash
python Projects/scripts/batch_archive_projects.py [ID1] [ID2] ...
```

### 3. Verify Index Update
Check `Projects/projects_index.md` to ensure all targeted projects are now marked as `Archived` with the correct completion date.

### 4. Provide Summary
Report the outcome of the batch operation to the user, listing successful archives and any failures.

---

## Termination
1. Confirm all files have been moved.
2. Confirm `projects_index.md` is updated.
3. **STOP**
