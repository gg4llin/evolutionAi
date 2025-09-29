# Custom GPT Branch Workflow

The AdaptiveAgent Custom GPT instructions should live on a dedicated branch so hosted deployments can track a stable knowledge bundle without waiting for mainline feature readiness.

## Branch Strategy
- **Branch name:** `custom-gpt`
- **Source:** branch off `main` after each release or when blueprint updates stabilise.
- **Contents:**
  - `custom_gpt/` directory (prompt, profile, integration matrix, connectivity/infrastructure configs).
  - `docs/blueprints/` snapshot matching the deployed knowledge bundle.
  - Any helper scripts required to package or validate the knowledge upload.
- **Exclusions:** experimental code, unreviewed blueprints, or local engine changes that have not shipped to production.

## Sync Process
1. Merge blueprint and tooling updates into `main`.
2. Create or fast-forward `custom-gpt` from `main`:
   ```bash
   git checkout main
   git pull
   git checkout -B custom-gpt
   ```
3. Run validation:
   - Ensure `custom_gpt/openai_profile.yaml` lists every knowledge asset.
   - Re-run local engine smoke tests (`heartbeat`, `revise_egg`).
   - Export the knowledge bundle as per OpenAI UI requirements.
4. Push the branch and configure deployment automation to pull from `custom-gpt`:
   ```bash
   git push origin custom-gpt
   ```

## Release Checklist
- [ ] Blueprint diffs reviewed and reconciled with `custom_gpt/integration_matrix.md`.
- [ ] System prompt verified against the live instructions in the OpenAI dashboard.
- [ ] Knowledge upload order confirmed, including new documentation artefacts.
- [ ] Changelog entry appended to `docs/roadmap.md` or release notes.

Keep this document updated when the deployment pipeline evolves (e.g., automated exports, CI validation jobs).
