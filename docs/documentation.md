# Documentation Index

Welcome to the evolutionAi knowledge base. Use this index to navigate the materials that describe, operate, and extend the AdaptiveAgent platform.

## Blueprint Library
All canonical specifications reside in `docs/blueprints/`. Each file mirrors a subsystem:
- `agentic_replication_system.txt` — replication thresholds, rubrics, and pre-spawn judgement hooks.
- `agent_spawning_framework.txt` — tadpole egg template, modular capabilities, and learning feedback pipeline.
- `dynamic_rubric_system.txt` — adaptive principle weights and metric ranges.
- `performance_metrics_system.txt` — KPI definitions, retention windows, and scoring methodology.
- `recursive_optimization_engine.txt` — micro/macro/meta optimisation cycles.
- `data_persistence_state_management.txt` — persistence tiers, replication factors, and judgement storage schemas.
- `inter_system_communication.txt` — Kafka topics and delivery guarantees.
- `mesh_networking_protocol.txt` — discovery, topology, and heartbeat cadence.
- `security_authentication_framework.txt` — zero-trust authentication, authorisation, and audit controls.
- `tadpole_metadata_judgement_system.txt` — metadata ingestion, ledger governance, and egg revision workflow.
- `task_orchestration_system.txt` — job intake, resource allocation, and multithreaded execution policy.
- `worker_orchestration_system.txt` — worker questing, tool discovery, and meta feedback routing.

## Operational Playbooks
- `AGENTS.md` — contributor expectations, coding conventions, and review policy.
- `install/linux.md`, `install/docker.md`, `install/windows.md` — platform-specific installation and bootstrap steps.
- `install/debian_setup.sh` — automated Debian setup script (creates a virtual environment, installs dependencies, runs sanity checks).
- `local_engine/README.md` — control-plane API surface, command payloads, and token requirements.

## Strategic Planning
- `docs/roadmap.md` — milestone schedule, sequencing, and dependency risks.
- `docs/todo.md` — actionable backlog items grouped by theme.

## Custom GPT Configuration
- `custom_gpt/system_prompt.md` — production instructions for AdaptiveAgentGPT.
- `custom_gpt/integration_matrix.md` — crosswalk between specs, assistant guidance, and runtime touchpoints.
- `custom_gpt/openai_profile.yaml` — knowledge upload order and deployment checks.
- `docs/custom-gpt-branch.md` — instructions for maintaining the dedicated Custom GPT branch.
- `.env.example` — reference template for local secrets (actual `.env` files must remain untracked).

## Extensibility Guidelines
- `docs/naming-conventions.md` — update when introducing new directories or file types.
- `install/` — contribute new provisioning scripts or platform guides here.
- `docs/` — add domain-specific guides, archived research, or process documentation as the programme evolves.

Keep this index up to date whenever new artefacts are added so operators and reviewers can locate the source of truth quickly.
