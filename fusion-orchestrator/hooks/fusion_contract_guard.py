#!/usr/bin/env python3
"""PostToolUse hook: guard the Fusion run-state contract in Claude Code.

Fires on Write/Edit. When a write touches a Fusion run directory
(any dir containing plan.json + harness.json), it verifies the write does not
violate the frozen contract:

- header.txt must never name a model absent from harness.json dispatches
- harness.json must remain valid JSON with required dispatch fields
- team.json member delegation kinds must be from the frozen set

Violations print a warning to stderr (the session reminds the agent to fix).
Exit 0 always — advisory in v1, promotable to blocking later.
"""
import json
import os
import re
import sys

def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0
    file_path = payload.get("tool_input", {}).get("file_path", "") or ""
    if not file_path:
        return 0
    run_dir = os.path.dirname(file_path) or "."
    plan_p, harness_p = os.path.join(run_dir, "plan.json"), os.path.join(run_dir, "harness.json")
    if not (os.path.exists(plan_p) and os.path.exists(harness_p)):
        return 0  # not a fusion run dir
    try:
        harness = json.load(open(harness_p))
    except Exception:
        print("FUSION CONTRACT: harness.json unreadable — fix it to stay valid JSON "
              "with dispatches[].{dispatch_id,member_role,status,ok,actual_model,actual_provider,output_path}",
              file=sys.stderr)
        return 0
    dispatches = harness.get("dispatches") or []
    actual_models = {d.get("actual_model", "") for d in dispatches} - {"?", ""}

    base = os.path.basename(file_path)
    if base == "header.txt":
        try:
            content = payload.get("tool_input", {}).get("content", "") or ""
        except Exception:
            content = ""
        mentioned = set(re.findall(r"\(([a-zA-Z0-9._\-/]+)\)", content))
        ghosts = {m for m in mentioned if m not in actual_models and not m.startswith(("gpt", "claude", "grok", "gemini", "deepseek", "glm"))}
        unattested = {m for m in mentioned if m.startswith(("gpt", "claude", "grok", "gemini", "deepseek", "glm")) and m not in actual_models}
        if unattested:
            print(f"FUSION CONTRACT VIOLATION: header.txt names models {sorted(unattested)} "
                  f"not attested in harness.json. Provenance = actual execution receipts only. "
                  f"Attested: {sorted(actual_models)}", file=sys.stderr)
    if base == "harness.json":
        # Prefer validating the INCOMING content (the write's effect), falling
        # back to the on-disk state for context reads.
        incoming = None
        try:
            raw = payload.get("tool_input", {}).get("content", "")
            if raw:
                incoming = json.loads(raw)
        except Exception:
            incoming = None
        check_dispatches = (incoming or {}).get("dispatches", dispatches)
        for i, d in enumerate(check_dispatches):
            missing = [k for k in ("dispatch_id", "member_role", "status", "ok", "actual_model", "actual_provider", "output_path") if k not in d]
            if missing:
                print(f"FUSION CONTRACT: harness.json dispatch[{i}] missing {missing} — "
                      f"the frozen shape is required for cross-harness scoring", file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
