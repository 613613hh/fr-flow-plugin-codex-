# fr-flow-plugin-codex

Codex plugin for FineReport 11 front-end development. It provides shared workflows for PC and mobile projects: requirements planning, CPT/data development, React/Ant Design display development, change management, release packaging, and end-to-end QA.

## Plugin layout

```text
fr-flow-plugin-codex-/
├─ .codex-plugin/plugin.json   # Codex plugin manifest
├─ skills/                     # The only skill source directory
├─ foundation/                 # Shared CPT templates and tools
├─ public_cpt/                 # Public CPT assets
├─ scripts/                    # Shared workflow scripts
├─ hooks/                      # Optional project hooks
├─ schemas/                    # Task/QA JSON schemas
├─ shared/                     # Shared FineReport knowledge
└─ docs/                       # Installation and workflow documentation
```

Business report projects are intentionally not included. Keep them in a separate FineReport `reportlets` workspace and install this plugin into Codex.

## Install from GitHub

Install this repository as a Codex plugin using the Codex plugin installer. Codex places the versioned plugin under its user plugin cache; the source repository does not need to be copied into the FineReport `reportlets` directory.

Available workflows:

```text
/fr
/fr-pm <project>
/fr-data-dev <project>
/fr-display-dev <project>
/fr-qa <project>
/frm
/frm-pm <project>
/frm-display-dev <project>
/frm-qa <project>
```

## Build and release workflow

For a report project, the recommended source/build chain is:

```text
JSX → MJS → CPT
```

MJS is an intermediate build artifact. Once embedded in the CPT, it is not included in the final offline release package.

Each business project owns its release directory. A release archive contains only final CPT files and, when the change includes stored-procedure changes, the latest stored-procedure snapshot:

```text
fr-release-v1.2.0.zip
├─ report-a.cpt
├─ report-b.cpt
└─ procedures.sql   # optional
```

If no stored procedure changed, omit `procedures.sql`. JSX and MJS are development/build artifacts and must not be placed in the final release archive.

## Development and versioning

The plugin repository is independent of FineReport runtime files. Keep environment-specific values in the project workspace, not in this repository. Do not commit credentials or local `.fr.yaml` files; use `.fr.yaml.example` as the template.

Use Git tags for installable releases, for example `v3.2.0`. Update the plugin manifest cachebuster before publishing a changed local plugin.
