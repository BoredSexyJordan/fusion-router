"""`hermes fusion ...` CLI — argparse tree + handlers for Fusion v4.

Subcommands are thin: they delegate to the proven skill scripts
(validate_fusion_packet.py, sync_model_index.py, analyze_fusion_feedback.py,
execute_fusion_plan.py) and to this package's team registry. No duplicated
logic lives here — the scripts stay the single source of truth so the skill
and the plugin share one implementation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).parent
HOME = Path.home()
SKILL_SCRIPTS = HOME / ".hermes" / "skills" / "autonomous-ai-agents" / "fusion-orchestration" / "scripts"
INDEX_PATH = HOME / ".hermes" / "fusion" / "model-index.json"
RUNS_BASE = HOME / ".hermes" / "fusion" / "runs"
FEEDBACK_DIR = HOME / ".hermes" / "fusion" / "feedback"

DEFAULT_MM = {"model": "deepseek-v4-flash", "provider": "inferx"}

# Team-template registry (v4). The feedback loop tunes these; the MM loop consumes them.
TEAM_TEMPLATES = {
    "technical-default": {
        "task_type": "technical",
        "middle_manager": {"model": "deepseek-v4-pro", "provider": "inferx"},
        "members": [
            {"role": "implementer", "model": "gpt-5.6-sol", "provider": "openai-codex",
             "delegation": "delegate_task", "thread_policy": "continuous"},
            {"role": "mechanical", "model": "deepseek-v4-flash", "provider": "inferx",
             "delegation": "delegate_task", "thread_policy": "fresh_per_item"},
        ],
        "consults": [
            {"role": "design-judgment", "model": "claude-opus-4-8", "provider": "claude-team",
             "delegation": "clean_session", "trigger": "aesthetic decision"},
        ],
    },
    "research-collect": {
        "task_type": "research",
        "middle_manager": DEFAULT_MM,
        "members": [
            {"role": "collector-1", "model": "deepseek-v4-flash", "provider": "inferx",
             "delegation": "delegate_task", "thread_policy": "fresh_per_item"},
            {"role": "collector-2", "model": "deepseek-v4-flash", "provider": "inferx",
             "delegation": "delegate_task", "thread_policy": "fresh_per_item"},
            {"role": "x-researcher", "model": "grok-4.5", "provider": "xai-oauth",
             "delegation": "delegate_task", "thread_policy": "continuous"},
        ],
        "consults": [
            {"role": "synthesis", "model": "gpt-5.6-sol", "provider": "openai-codex",
             "delegation": "clean_session", "trigger": "final synthesis"},
        ],
    },
    "strategy-panel": {
        "task_type": "strategy",
        "middle_manager": {"model": "deepseek-v4-pro", "provider": "inferx"},
        "members": [
            {"role": "panel-gpt", "model": "gpt-5.6-sol", "provider": "openai-codex",
             "delegation": "delegate_task", "thread_policy": "fresh_per_item"},
            {"role": "panel-claude", "model": "claude-opus-4-8", "provider": "claude-team",
             "delegation": "delegate_task", "thread_policy": "fresh_per_item"},
            {"role": "panel-grok", "model": "grok-4.5", "provider": "xai-oauth",
             "delegation": "delegate_task", "thread_policy": "fresh_per_item"},
        ],
        "consults": [],
    },
    "explicit-grok": {
        "task_type": "explicit",
        "middle_manager": DEFAULT_MM,
        "members": [
            {"role": "writer", "model": "grok-4.5", "provider": "xai-oauth",
             "delegation": "delegate_task", "thread_policy": "continuous"},
            {"role": "structure", "model": "deepseek-v4-flash", "provider": "inferx",
             "delegation": "delegate_task", "thread_policy": "fresh_per_item"},
        ],
        "consults": [
            {"role": "review", "model": "grok-4.5", "provider": "xai-oauth",
             "delegation": "clean_session", "trigger": "final review"},
        ],
    },
    "personal-claude": {
        "task_type": "personal",
        "middle_manager": DEFAULT_MM,
        "members": [
            {"role": "primary", "model": "claude-opus-4-8", "provider": "claude-team",
             "delegation": "delegate_task", "thread_policy": "continuous"},
        ],
        "consults": [
            {"role": "strategy", "model": "gpt-5.6-sol", "provider": "openai-codex",
             "delegation": "clean_session", "trigger": "strategy needed"},
        ],
    },
    "operations-run": {
        "task_type": "operations",
        "middle_manager": DEFAULT_MM,
        "members": [
            {"role": "executor", "model": "deepseek-v4-flash", "provider": "inferx",
             "delegation": "kanban_handoff", "thread_policy": "fresh_per_item"},
        ],
        "consults": [],
    },
}


def _script(name: str) -> str:
    return str(SKILL_SCRIPTS / name)


def _run(args: list, timeout: int = 300) -> int:
    try:
        result = subprocess.run(args, timeout=timeout)
        return result.returncode
    except FileNotFoundError:
        print(f"missing dependency: {args[0]}", file=sys.stderr)
        return 127
    except subprocess.TimeoutExpired:
        print("timed out", file=sys.stderr)
        return 124


def cmd_validate(args) -> int:
    return _run([sys.executable, _script("validate_fusion_packet.py"), args.packet])


def cmd_plan(args) -> int:
    """plan: extract + validate (+ normalize hint on failure). Read-only assist."""
    raw = Path(args.raw)
    out = Path(args.out)
    rc = _run([sys.executable, _script("extract_fusion_json.py"), str(raw), str(out)])
    if rc != 0:
        return rc
    return _run([sys.executable, _script("validate_fusion_packet.py"), str(out)])


def cmd_run(args) -> int:
    argv = [sys.executable, _script("execute_fusion_plan.py"), args.plan]
    if args.budget:
        argv += ["--budget", args.budget]
    return _run(argv, timeout=1800)


def cmd_teams(args) -> int:
    """Print the team-template registry (the gate)."""
    import json

    if args.show:
        tmpl = TEAM_TEMPLATES.get(args.show)
        if not tmpl:
            print(f"unknown template: {args.show}", file=sys.stderr)
            return 1
        print(json.dumps({"template": args.show, **tmpl}, indent=1))
        return 0
    print("Fusion v4 team templates (the model-selection gate):")
    print()
    for name, tmpl in sorted(TEAM_TEMPLATES.items()):
        mm = tmpl.get("middle_manager", {})
        workers = ", ".join(f"{m['role']}={m['model']}" for m in tmpl.get("members", []))
        consults = ", ".join(c["role"] for c in tmpl.get("consults", [])) or "-"
        print(f"  {name}  [{tmpl.get('task_type', '?')}]")
        print(f"    MM:       {mm.get('model')} via {mm.get('provider')}")
        print(f"    members:  {workers}")
        print(f"    consults: {consults}")
    print()
    print("Use `hermes fusion teams --show <name>` for the full roster JSON.")
    return 0


def cmd_index(args) -> int:
    sync = HOME / ".hermes" / "scripts" / "sync_model_index.py"
    rc = _run([sys.executable, str(sync), "--config", str(HOME / ".hermes" / "config.yaml")])
    if rc != 0:
        return rc
    import json

    idx = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    if args.query:
        hits = [m for m in idx.get("models", {}) if args.query.lower() in m.lower()]
        for m in hits:
            entry = idx["models"][m]
            meta = entry.get("metadata") or {}
            print(f"  {m:40s} providers={','.join(entry.get('providers', []))} "
                  f"ctx={meta.get('context', '?')} reasoning={meta.get('reasoning', '?')}")
        if not hits:
            print(f"  no indexed model matches '{args.query}'")
        return 0
    print(f"  {len(idx.get('models', {}))} models across "
          f"{len(idx.get('configured_providers', {}))} providers "
          f"(generated {idx.get('_generated', '?')})")
    return 0


def cmd_report(args) -> int:
    analyzer = HOME / ".hermes" / "scripts" / "analyze_fusion_feedback.py"
    rc = _run([sys.executable, str(analyzer)])
    if rc == 0:
        import datetime as _dt

        name = f"feedback-{_dt.datetime.now(_dt.timezone.utc).strftime('%Y%m%d')}.md"
        path = FEEDBACK_DIR / name
        if path.exists():
            print(path.read_text(encoding="utf-8"))
    return rc


def cmd_status(args) -> int:
    import json

    runs = sorted(p for p in RUNS_BASE.iterdir() if p.is_dir()) if RUNS_BASE.exists() else []
    print(f"Fusion runs: {len(runs)}")
    for run_dir in runs[-5:]:
        plan = {}
        plan_path = run_dir / "plan.json"
        if plan_path.exists():
            try:
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        team_path = run_dir / "team.json"
        team = team_path.read_text(encoding="utf-8")[:40] if team_path.exists() else ""
        print(f"  {run_dir.name}  task={plan.get('task_type', '?'):12s} "
              f"v={plan.get('fusion_version', '?')}  team={'yes' if team else 'legacy'}")
    return 0


def setup_cli(subparser) -> None:
    sub = subparser.add_subparsers(dest="fusion_cmd", required=True)

    p = sub.add_parser("validate", help="Validate a plan packet (v3 or v4)")
    p.add_argument("packet", help="Path to plan packet JSON")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("plan", help="Extract + validate a raw planner output file")
    p.add_argument("raw", help="Raw model output containing the packet JSON")
    p.add_argument("--out", default="plan.json", help="Where to write the extracted packet")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("run", help="Execute a validated packet through the MM loop")
    p.add_argument("plan", help="Path to a VALIDATED plan packet")
    p.add_argument("--budget", choices=["free", "balanced", "premium"], default=None)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("teams", help="Show the team-template registry")
    p.add_argument("--show", help="Show full JSON for one template")
    p.set_defaults(func=cmd_teams)

    p = sub.add_parser("index", help="Sync + query the living model index")
    p.add_argument("--query", help="Substring filter over indexed model ids")
    p.set_defaults(func=cmd_index)

    p = sub.add_parser("report", help="Run the weekly feedback scorer and print the report")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("status", help="Show recent runs and their shape")
    p.set_defaults(func=cmd_status)


def fusion_command(args) -> int:
    return args.func(args)
