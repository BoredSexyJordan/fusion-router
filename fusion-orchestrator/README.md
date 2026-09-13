# Fusion Orchestrator for Claude Code (v4)

Multi-model orchestration with a middle-manager loop, conforming to the same
frozen contract as the Hermes executor: identical packet schema, identical
run-state shape (`plan.json + team.json + harness.json + out-<role>.md +
header.txt`), identical provenance rules. Runs scored by the same weekly
feedback loop.

## Architecture (T0 / T1 / T2)

- **fusion-lead** (T0, clean session) — frontier decision-maker. Turns a goal
  into a validated v4 packet. Never implements. Never prescribes.
- **fusion-mm** (T1) — owns the dispatch loop: prompt audit (hard gate),
  per-phase dispatch to model-pinned members, artifact collection, run state,
  verification + bounded retry, escalation of decisions-not-struggles.
- **fusion-worker** (T2, genius specialist) — executes ONE bounded phase,
  writes its artifact, reports honest `ATTENDED_AS` model identity.
- **fusion-auditor** — independent second-pass prompt auditor. Never dispatches.

## Iron invariants (same as Hermes)

1. No model switching inside a session; tier boundaries = session boundaries.
2. Delegation kind pinned per member; nobody changes it at dispatch time.
3. Worker prompts carry goal + evidence, never implementation prescriptions.
   The auditor hard-blocks; one rewrite cycle; then T0 escalation. Never bypass.
4. Handoffs are artifacts, never transcripts.
5. Provenance = attestation of what actually ran (harness.json), never the roster.
6. Max 4 team members, usually 3. Model selection as gate — capability fit, not bans.

## Layout

```
.claude-plugin/plugin.json     manifest (v4.0.0)
agents/fusion-lead.md          T0 packet architect (opus)
agents/fusion-mm.md            T1 middle manager (sonnet)
agents/fusion-worker.md        T2 specialist (haiku default; MM pins per-member)
agents/fusion-auditor.md       independent prompt auditor (sonnet)
commands/fusion-run.md         /fusion-run [goal] — full loop or --dry-run
commands/fusion-status.md      /fusion-status — newest run, read-only
hooks/hooks.json + guard       PostToolUse contract guard (header/harness tamper warnings)
scripts/validate_fusion_packet.py  same validator the Hermes plugin uses
scripts/{extract_fusion_json,normalize_fusion_plan,build_fusion_header}.py
```

## Delegation kinds (pinned per member in the packet)

- `delegate_task` — Task-tool subagent, model pinned, in-run. Primary in Claude Code.
- `clean_session` — recorded for the caller to spawn standalone.
- `kanban_handoff` — unsupported inside Claude Code; recorded as escalated.

## Run state (frozen — the Hermes executor consumes the same shape)

```
<run-dir>/plan.json      packet verbatim
<run-dir>/team.json      executed roster + audit counters
<run-dir>/harness.json   {"harness":"claude-code", "mm":{...}, "dispatches":[{dispatch_id, member_role, status, ok, actual_model, actual_provider, output_path, task_ref, seconds, retries}]}
<run-dir>/out-<role>.md  one artifact per member
<run-dir>/header.txt     attested line, built from harness.json only
```

Fallback disclosure: any dispatch whose `actual_model` ≠ pinned model is a
fallback event and must be flagged in the final report.

## Install

```
claude plugin install /path/to/fusion-claude-plugin
# or for development: symlink into ~/.claude/skills/ (auto-loads as <name>@skills-dir)
```

Validate any time with `claude plugin validate <path>`.
