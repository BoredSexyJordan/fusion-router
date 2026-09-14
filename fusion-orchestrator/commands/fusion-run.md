---
name: fusion-run
description: Run a Fusion v4 orchestration - plan, validate, dispatch to a model-pinned team, collect attested artifacts
allowed-tools: Task, Read, Write, Bash, Glob, Grep
argument-hint: [goal] (--dry-run to plan only)
---

# Fusion run

Goal: **$ARGUMENTS**

## Procedure

1. If the goal contains "--dry-run" or the user asked to plan only: invoke the **fusion-lead** subagent to produce `fusion/packet.json`, validate it (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_fusion_packet.py fusion/packet.json`), present the roster + phases, and STOP.

2. Otherwise, full run:
   a. Invoke **fusion-lead** → packet at `fusion/packet.json`. Validate; if invalid, return the validator's errors to fusion-lead once, then stop on second failure.
   b. Invoke **fusion-mm** with the packet path. It owns: prompt audit (hard gate), per-phase dispatch to pinned members, artifact collection to the run dir, harness.json receipts, attested header.txt, verification + bounded retry, escalation.
   c. Read the run dir's header.txt + harness.json yourself and present: the provenance line, per-member status table, artifact paths, and any escalations. Flag any dispatch whose actual_model differs from its pinned model — that is a fallback event and matters.

3. Never summarize from transcripts what harness.json does not attest.
4. If every member returned blocked/failed, report the raw failures — do not editorialize a success.
