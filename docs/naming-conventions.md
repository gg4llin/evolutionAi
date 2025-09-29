# Naming Conventions

Consistency allows AdaptiveAgent contributors, automation, and the hosted Custom GPT to reason about the project without guesswork. Follow these rules whenever you add or rename artefacts.

## Directories
- Use lower-case words separated by underscores (e.g., `local_engine`, `custom_gpt`).
- Documentation directories live under `docs/` and may add a second level (e.g., `docs/blueprints/`).
- Installation materials belong in `install/` with the target platform in the filename.

## Files
- Blueprint specs are `.txt` files stored in `docs/blueprints/` with `snake_case` names that describe the subsystem (`agentic_replication_system.txt`).
- Markdown files that provide guides or indexes use kebab-case or descriptive snake_case depending on readability (e.g., `docs/roadmap.md`, `docs/naming-conventions.md`).
- YAML and JSON configs mirror their consuming tool (`custom_gpt/openai_profile.yaml`).

## Identifiers Inside Documents
- Use PascalCase for globally recognised systems (`AdaptiveAgentSwarm`, `RecursiveMetaOptimizer`).
- Use snake_case for configuration keys and metric identifiers (`replication_threshold`, `learning_velocity`).
- When referencing files inside the repository, prefer repository-relative paths (`docs/blueprints/performance_metrics_system.txt`).
- Store sensitive values in `.env` (ignored by git) and distribute redacted templates as `.env.example`.

## Branches (Git)
- Reserve `main` for production-ready blueprints.
- Stage Custom GPT updates on the dedicated branch `custom-gpt` (create once Git is initialised).
- Use feature branches named `feature/<short-description>` for multi-file changes.

Update this document whenever a new artefact class is introduced so downstream tooling remains consistent.
