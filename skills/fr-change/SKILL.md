---
name: fr-change
description: Manage a FineReport project change from JSX source through MJS build and CPT regeneration, with Git version control and release readiness checks.
---

# FineReport version change

Use this skill when a user asks to modify an existing FineReport project, prepare a version change, or make a change ready for internal release.

For any failure, read `shared/KNOWLEDGE/ERROR_HANDLING.md` and follow its classification, retry, and stop rules.

## Required source chain

1. Work only in the named project under `$FR_PROJECTS_DIR`.
2. Treat `.jsx` as the editable source of truth.
3. Build `.jsx` to `.mjs` with the project/plugin toolchain and run syntax checks.
4. Inject the generated MJS into the target `.cpt`; do not hand-edit compiled CPT content.
5. Validate the resulting CPT and run the relevant data/display/QA checks.

## Version control

- Inspect `git status` before changing files and preserve unrelated work.
- Record the change in the project changelog or change document when the project has one.
- Use a semantic version (`MAJOR.MINOR.PATCH`) and create a Git tag only after validation passes.
- Do not create a release tag for an unverified working tree.
- If stored procedures changed, update the project's latest stored-procedure snapshot; otherwise do not manufacture or copy an SQL file.

## Release handoff

When the user asks to publish, hand off to `fr-release` with the exact project name, version, final CPT list, and whether stored procedures changed. Do not include JSX or MJS in the release archive.
