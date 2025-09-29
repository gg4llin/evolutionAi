# evolutionAi

AdaptiveAgent is a blueprint-driven ecosystem for orchestrating self-optimising swarm agents. This repository captures the canonical specifications, a tooling harness for a Custom GPT assistant, and a runnable local control-plane to exercise the designs.

## Repository Layout
- `docs/blueprints/` — canonical subsystem specifications (replication, spawning, metrics, security, metadata judgement, task orchestration, worker orchestration, etc.).
- `docs/documentation.md` — entry point to the broader documentation set, including roadmap and day-to-day operator notes.
- `docs/roadmap.md` — high-level delivery milestones and sequencing.
- `docs/todo.md` — granular backlog items aligned to the roadmap themes.
- `docs/naming-conventions.md` — rules that keep file names, IDs, and directory labels consistent across the stack.
- `custom_gpt/` — configuration bundle that powers the hosted AdaptiveAgentGPT instance.
- `local_engine/` — Python control-plane stub for spawning, scoring, and revising tadpole workers.
- `install/` — platform-specific installation guides for Linux, Docker, and Windows 11 environments.
- `AGENTS.md` — contributor guidelines for working day-to-day inside the repo.

## Naming Convention
1. **Specifications** live under `docs/blueprints/` and follow `snake_case` filenames that mirror their primary system names (e.g., `agentic_replication_system.txt`).
2. **Directories** use lower-case words separated by underscores for parity with the specs (`local_engine`, `custom_gpt`).
3. **High-level systems** retain PascalCase within documents (e.g., `AdaptiveAgentSwarm`) to highlight globally recognised entities.
4. **Generated artefacts** (patches, configs, installers) should adopt descriptive kebab-case (e.g., `install/linux.md`) to stay grep-friendly.
5. New content must update `docs/naming-conventions.md` and `custom_gpt/module_manifest.yaml` so AdaptiveAgentGPT reflects the latest vocabulary.

## Getting Started
1. Review `install/linux.md`, `install/docker.md`, or `install/windows.md` based on your environment.
2. On Debian systems run `install/debian_setup.sh` to create a virtual environment and install dependencies automatically, or manually:
   ```bash
   pip install -r requirements.txt
   ```
3. Export secrets (for example `cp .env.example .env` and populate it, then `export $(grep -v '^#' .env | xargs)`), and start the local control plane with Uvicorn:
   ```bash
   uvicorn local_engine.asgi:app --host 127.0.0.1 --port 8080
   ```
   A synchronous fallback exists via `python -m local_engine.main`, but the ASGI entrypoint plus `uvicorn` is the recommended development path.
4. (Optional) Expose the API securely via ngrok, following the guidance in `custom_gpt/connectivity_config.yaml` and keeping tokens outside version control.
5. Submit jobs through `/commands` (`action: "assign_job"`) to exercise tadpole orchestration. Include resource requests (`compute_units`, `memory_mb`, `bandwidth_mbps`) and a `reward_signal`; the engine will spawn multithreaded tadpoles, allocate chunks from the shared resource pool, and monitor progress via `job_status`/`list_jobs`. Use `assign_worker` / `worker_status` to scaffold quest workers that explore new tools and protocols on behalf of the engine.
6. Validate the environment via `tests/setup_check.sh` (after activating the venv). This compiles the engine, ensures Uvicorn is available, and performs a dry-run job submission.
7. Attach the knowledge bundle listed in `custom_gpt/openai_profile.yaml` when configuring the Custom GPT; plan to host those assets on a dedicated branch (recommended name: `custom-gpt`).

## Documentation Map
- Architectural overviews, roadmaps, and work logs all live under `docs/`. Start with `docs/documentation.md` for curated links.
- Blueprint specs are authoritative—treat them as the single source of truth and update the integration matrix (`custom_gpt/integration_matrix.md`) whenever dependencies shift.
- Operational procedures and review workflows are tracked in `AGENTS.md`.

## Contributing
Adhere to the Conventional Commits style described in `AGENTS.md`, validate YAML formatting with `yamllint`, and submit updates alongside tests or reproducible scripts where possible. For Custom GPT changes, stage them on the proposed `custom-gpt` branch before merging to `main` to keep hosted instructions in lock-step with the repo.

## Support & Feedback
Open issues for missing specs or inconsistencies, and document follow-up actions in `docs/todo.md`. Pull requests that touch the judgement system should include the output from `POST /commands` → `revise_egg` to prove the metadata loop continues to function.
