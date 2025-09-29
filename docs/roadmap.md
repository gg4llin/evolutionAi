# evolveAi Roadmap

## Q1: Judgement Loop Hardening
- Finalise persistence bindings for `population_state.judgement_snapshots` and integrate with production storage.
- Automate nightly `revise_egg` dry-runs and archive the resulting YAML patches for audit review.
- Expand anomaly detection thresholds in `tadpole_metadata_judgement_system.txt` with live telemetry data.

## Q2: Execution Readiness
- Deploy the AdaptiveAgent local engine behind a managed ingress with TLS cert rotation.
- Promote the Custom GPT configuration to its dedicated `custom-gpt` branch and wire CI to validate instructions vs. repo state.
- Author scenario tests that replay metrics into `/commands` to validate spawn + retire safety rails.
- Expand quest worker automation to source new protocols/tools from open APIs and MCP servers, updating the symbolic communication dictionary automatically.

## Q3: Distributed Swarm Pilot
- Connect the control-plane to the Kafka topics defined in `inter_system_communication.txt` and exercise multi-node spawning.
- Ship mesh topology visualisation tooling using the parameters in `mesh_networking_protocol.txt`.
- Establish a resilience drill playbook based on the `adaptive_resilience` principle budgets.

## Q4: Production Sign-off
- Complete security assessment against `security_authentication_framework.txt`, including capability revocation propagation.
- Deliver an operator dashboard that surfaces the rubric-derived composite scores for every active worker.
- Produce executive documentation summarising outcomes and lessons learned; publish under `docs/reports/`.

> Update this roadmap quarterly. When milestones are achieved, capture the outputs in `docs/todo.md` and surface the results in the next retrospective.
