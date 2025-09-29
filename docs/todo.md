# TODO Backlog

## Immediate (Sprint)
- [ ] Wire `/commands` responses into a structured log file for population state replay tests.
- [ ] Draft ngrok automation script that respects the rate limits in `custom_gpt/connectivity_config.yaml`.
- [ ] Validate the HMAC capability token examples across Linux, macOS, and Windows shells.

## Near-Term
- [ ] Implement persistence adapters so `MetadataRepository.records()` streams to `population_state.judgement_snapshots`.
- [ ] Enrich `local_engine.judgement_system` with configurable thresholds sourced directly from the blueprint specs.
- [ ] Publish CI jobs that lint YAML/JSON and run smoke tests against the local engine API.

## Long-Term
- [ ] Stand up the proposed `custom-gpt` branch with an automated knowledge bundle export.
- [ ] Develop visual analytics to plot principle averages over time and flag variance.
- [ ] Evaluate container orchestration strategies for large-scale tadpole deployments.

Track execution progress by linking commits or issues next to each item. Move completed tasks into the roadmap deliverables section for historical tracking.
