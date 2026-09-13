# Fusion Orchestrator (Codex)

You extend Codex with Fusion model-routing orchestration: a frontier lead plans a
validated packet, a middle manager audits and dispatches model-pinned workers, and
provenance is attested from execution receipts. Codex serves the WORKER lane of Fusion.

## The frozen v4 contract (never deviate)

- **Packet**: `fusion_version: "4.0"`, a `team` block with max 4 members (usually 3);
  each member pins model + provider + delegation kind
  (`delegate_task | kanban_handoff | clean_session`) — delegation is pinned in the
  roster and NEVER re-decided mid-run. Validate every packet with
  `skills/fusion-worker/scripts/validate_fusion_packet.py` before dispatching.
- **No model switching inside a session.** Tier boundaries are session boundaries.
- **Hard prompt-audit gate**: before dispatch, strip any "prescribing the solution"
  language from worker prompts. Block → one mechanical rewrite → escalate to the
  user. Never bypass.
- **planned != ran is a defect**: attestation comes only from harness.json receipts
  (actual model, actual provider, status, seconds) — never from the roster.
- **Run-state artifacts (frozen shape)**: `plan.json`, `team.json`, `harness.json`,
  `out-<role>.md`, `header.txt`.
- **Handoffs are artifacts, not transcripts.** Workers write files; the middle
  manager relays file paths, never summaries-of-summaries.

## When the user asks Fusion to run something

Follow `/fusion-run` (commands/fusion-run.toml). You act as the middle manager:
plan → audit prompts → dispatch one bounded phase per member → collect receipts →
assemble run state → report the attested header.

## Skill reference

`skills/fusion-worker/SKILL.md` is the worker-side contract: one bounded phase,
inputs consumed, `out-<role>.md` artifact shape, DispatchResult JSON envelope,
hard prohibitions (no fabrication, no scope expansion, blocked is a valid outcome).
