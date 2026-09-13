---
description: Show the status of the most recent Fusion run in this workspace - attested provenance, per-member receipts, escalations
allowed-tools: Read, Bash, Glob, Grep
---

# Fusion status

1. Find the newest Fusion run directory (search for the most recent dir under `fusion/runs/`, `.fusion/runs/`, or the workspace containing both `plan.json` and `harness.json`).
2. If none: say so plainly and show `hermes fusion status` output instead if the Hermes CLI is available.
3. Otherwise read `harness.json`, `team.json`, `header.txt` and present:
   - Provenance header (verbatim from header.txt)
   - Table: role | pinned model | actual model | status | seconds | artifact
   - Audit violations count + escalation list
   - Any member whose actual_model ≠ pinned model, flagged as FALLBACK
4. Read-only. Never fix, rewrite, or re-dispatch from this command.
