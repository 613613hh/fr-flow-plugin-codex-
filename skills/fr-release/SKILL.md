---
name: fr-release
description: Create and verify a FineReport internal release ZIP containing the selected CPT files, the latest stored-procedure snapshot, and the project change log.
---

# FineReport internal release

Use this skill when a validated FineReport project must be published to an internal network or packaged for copying to another environment.

For any failure, read `shared/KNOWLEDGE/ERROR_HANDLING.md`. Never bypass a release stop condition to produce a partial or unverified ZIP.

## Inputs

Require the project path, release version, and the exact final CPT files. Every release must include the latest complete stored-procedure snapshot, whether or not the current code change modified it. The project change log is also mandatory and must include the full version history and the latest release change.

## Package rules

Create the release output under the project-local `releases/` directory. Use a versioned ZIP name such as `{project}-{version}.zip`; never overwrite an existing ZIP with the same version.

The archive must contain only:

```text
report-a.cpt
report-b.cpt
sql/存储过程.sql
CHANGELOG.md
```

The SQL file is the latest complete stored-procedure snapshot, not an unrelated database bootstrap script. The change log is the project `docs/CHANGELOG.md`, copied as `CHANGELOG.md` at the archive root. Never include `.jsx`, `.mjs`, backups, logs, mock data, node modules, or other documentation in the final archive.

## Verification

Before packaging:

- Confirm all selected CPT files exist and are the validated outputs of the JSX -> MJS -> CPT chain.
- Confirm the CPT files are the current, Git-committed development/test files that were actually loaded and tested in FineReport. Do not package a separate `.generated` or temporary artifact.
- Confirm no external MJS file is required at runtime; MJS is embedded in CPT for this project.
- Confirm `sql/存储过程.sql` is the latest complete stored-procedure snapshot.
- Confirm `docs/CHANGELOG.md` contains the historical versions and the current release changes.
- Inspect the ZIP listing and fail if any extra file is present.
- Require a Git commit containing the exact tested CPT, JSX, MJS, task contracts, QA report, and changelog before creating the release ZIP. Do not package from uncommitted changes.
- Require the release version to be a semantic-version Git tag (`v<version>`) created from that commit. If the tag already exists, verify it points to the tested commit; never move or overwrite an existing tag.

After verification, report the archive path, version, CPT files, SQL snapshot, change log, commit, and tag. Ask the user whether to push the commit and tag to the configured remote; do not push automatically.
