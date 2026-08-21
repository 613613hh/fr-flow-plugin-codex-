---
name: fr-release
description: Create and verify a FineReport internal release ZIP containing the selected CPT files and an optional latest stored-procedure snapshot.
---

# FineReport internal release

Use this skill when a validated FineReport project must be published to an internal network or packaged for copying to another environment.

For any failure, read `shared/KNOWLEDGE/ERROR_HANDLING.md`. Never bypass a release stop condition to produce a partial or unverified ZIP.

## Inputs

Require the project path, release version, and the exact two final CPT files. Confirm whether this change includes stored-procedure changes. Do not guess the CPT list from every file in `pages/`.

## Package rules

Create the release output under the project-local `releases/` directory. Use a versioned ZIP name such as `{project}-{version}.zip`; never overwrite an existing ZIP with the same version.

The archive must contain only:

```text
report-a.cpt
report-b.cpt
procedures.sql   # only when stored procedures changed
```

The SQL file is the latest complete stored-procedure snapshot, not an unrelated database bootstrap script. Omit it when no stored procedure changed. Never include `.jsx`, `.mjs`, backups, logs, mock data, node modules, or documentation in the final archive.

## Verification

Before packaging:

- Confirm both CPT files exist and are the validated outputs of the JSX -> MJS -> CPT chain.
- Confirm the CPT files are the current, Git-committed development/test files that were actually loaded and tested in FineReport. Do not package a separate `.generated` or temporary artifact.
- Confirm no external MJS file is required at runtime; MJS is embedded in CPT for this project.
- If SQL is included, confirm it is the current stored-procedure snapshot.
- Inspect the ZIP listing and fail if any extra file is present.
- Ensure the project Git tree is clean or clearly record any intentional release commit.

After verification, create the project Git tag `v<version>` and report the archive path, version, CPT files, and whether SQL was included. Do not publish or push without the user's explicit request.
