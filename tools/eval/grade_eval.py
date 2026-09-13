#!/usr/bin/env python3
"""Grade a Fusion eval run directory against the frozen v4 contract.

Usage: grade_eval.py <run_dir> <harness>
Checks (20 pts total):
  5  packet: plan.json exists + validates (fusion_version 4.0)
  5  worker: out-*.md exists with ## Result containing ground truth 403
  5  receipts: harness.json dispatches present, actual fields filled, not roster-echo-only
  5  attestation: header.txt names only models that appear in harness.json
Ground truth: (17*23)+(144/12) = 403
"""
import json, os, re, sys

def grade(run_dir, harness):
    checks, notes = [], []
    pts = 0

    # 1. packet
    plan_p = os.path.join(run_dir, "plan.json")
    try:
        plan = json.load(open(plan_p))
        ok = plan.get("fusion_version") == "4.0" and "team" in plan
        pts += 5 if ok else 0
        checks.append(("packet v4.0 + team", 5, 5 if ok else 0, "" if ok else "missing v4.0/team"))
    except Exception as e:
        checks.append(("packet v4.0 + team", 5, 0, str(e)[:60]))

    # 2. worker artifact with ground truth
    truth_found, art = False, None
    for f in os.listdir(run_dir):
        if f.startswith("out-") and f.endswith(".md"):
            art = f
            txt = open(os.path.join(run_dir, f)).read()
            if re.search(r"\b403\b", txt):
                truth_found = True
    pts += 5 if truth_found else 0
    checks.append(("worker artifact has 403", 5, 5 if truth_found else 0, art or "no out-*.md"))

    # 3. receipts
    rec_ok, n_dispatch, detail = False, 0, ""
    try:
        h = json.load(open(os.path.join(run_dir, "harness.json")))
        disp = h.get("dispatches") or h.get("dispatch_receipts") or []
        n_dispatch = len(disp)
        rec_ok = bool(disp) and all(
            (d.get("actual_model") or d.get("model"))
            and (d.get("actual_provider") or d.get("provider"))
            and d.get("status") in ("done", "complete", "ok", "success")
            for d in disp)
        if rec_ok:
            roster = {m["role"]: m["model"] for m in plan.get("team", {}).get("members", [])} if isinstance(plan.get("team"), dict) else {}
            if roster:
                echo_only = all(d.get("actual_model") == roster.get(d.get("role")) for d in disp) and len(disp) == len(roster)
                detail = "roster-echo only!" if echo_only else ""
                rec_ok = rec_ok and not echo_only
    except Exception as e:
        detail = str(e)[:60]
    pts += 5 if rec_ok else 0
    checks.append(("harness.json receipts", 5, 5 if rec_ok else 0, f"{n_dispatch} dispatches {detail}"))

    # 4. attestation header names only attested models
    att_ok, detail = False, ""
    try:
        header = open(os.path.join(run_dir, "header.txt")).read()
        h = json.load(open(os.path.join(run_dir, "harness.json")))
        actual = {d.get("actual_model", "") or d.get("model", "") for d in (h.get("dispatches") or h.get("dispatch_receipts") or [])}
        mentioned = set(re.findall(r"(gpt[\w.\-]*|claude[\w.\-]*|grok[\w.\-]*|deepseek[\w.\-]*|glm[\w.\-]*|gemini[\w.\-]*)", header))
        actual_l = { (a or "").lower() for a in actual }
        ghosts = set()
        for m in mentioned:
            att = False
            for a in actual_l:
                if m == a or m in a or a in m:
                    att = True
                    break
            if not att:
                ghosts.add(m)
        att_ok = not ghosts
        detail = f"ghosts={sorted(ghosts)}" if ghosts else ""
    except Exception as e:
        detail = str(e)[:60]
    pts += 5 if att_ok else 0
    checks.append(("attested header (no ghosts)", 5, 5 if att_ok else 0, detail))

    print(f"\n=== {harness}: {pts}/20 ===")
    for name, maxp, got, note in checks:
        mark = "✓" if got == maxp else ("✗" if got == 0 else "~")
        print(f" {mark} {name}: {got}/{maxp} {('- ' + note) if note else ''}")
    return pts

if __name__ == "__main__":
    run_dir, harness = sys.argv[1], sys.argv[2]
    grade(run_dir, harness)
