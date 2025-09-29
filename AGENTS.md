# Repository Guidelines

## Project Structure & Module Organization
All system blueprints live at the repository root as focused `.txt` specs. Key files include `agentic_replication_system.txt`, `dynamic_rubric_system.txt`, `recursive_optimization_engine.txt`, the metadata ledger in `tadpole_metadata_judgement_system.txt`, and complementary modules for networking, security, and persistence. Each document follows a YAML-inspired hierarchy with comment headers that describe the subsystem. Add new subsystem specs alongside the existing files and keep related assets in dedicated subdirectories named `<module>_assets/` when binary data is required.

## Build, Test, and Development Commands
This repository distributes architectural specifications rather than executable code, so no formal build pipeline exists. Use `rg "metric" *.txt` to locate cross-cutting definitions quickly, and run `python -m yamllint agentic_replication_system.txt` (or another lint target) to validate structured blocks before submitting updates. To exercise the control-plane stub, export `ADAPTIVE_CAPABILITY_SECRET=<32+ chars>` and run `python -m local_engine.main --host 127.0.0.1 --port 8080`; pair it with `ngrok http 8080` when remote access is required. When scripts are introduced, place helper commands in a `Makefile` and document them here.

## Coding Style & Naming Conventions
Maintain two-space indentation inside structured blocks and align colons for readability. Keep keys and filenames in `snake_case`, reserve `PascalCase` for high-level system names, and prefix narrative context with `#` comments. When inserting lists, prefer dash-prefixed arrays and keep scalar values wrapped in quotes only when necessary for parsing.

## Testing Guidelines
Because the content is declarative, thorough peer review and schema validation are the primary safeguards. When altering parameter ranges or thresholds, include a short rationale comment and cross-check dependent modules (for example, confirm that `performance_metrics_system.txt` still references the same metric ids). If executable harnesses are added later, pair each with lightweight unit tests stored under `tests/` and mirror the filename of the spec they cover.

## Commit & Pull Request Guidelines
The current snapshot lacks `.git` metadata, so mirror the Conventional Commits style used by the upstream project: `docs: expand dynamic rubric weights`. Keep subject lines under 72 characters, describe what changed and why in the body, and link to tracking issues. Pull requests should summarize the affected modules, flag any cascading changes consumers must make, and provide before/after snippets when altering numeric thresholds.
