# 🧬 Fusion — Always the right model for the job

> **[→ Visit the Fusion website](https://fusion-router.pages.dev/)** — live demo, install guides, and the full model.

Fusion is a **model-routing orchestration layer** that runs as a single plugin across **Hermes, Claude Code, Grok Build / Grok Bot, Codex, and Cursor**. It turns one goal into a team of model-pinned subagents — a middle manager keeps the handoff lossless while every artifact is attested to what actually ran.

```
plan.json   →  team roster, phases, scope, verification
team.json   →  the executed roster + audit counters
harness.json→  per-dispatch receipts (actual model/provider/seconds) — the attestation
out-<role>.md → one artifact per worker
header.txt  →  provenance line, built only from what actually ran
```

---

## Why Fusion exists

Model routing so far was thought out in terms of *sessions* as the unit. Bots and subagents change that: a conversation is a **team of models flowing together**. Intelligence level is one axis; Claude writes cleaner prose, GPT is the numbers analyst, Grok counterbalances dynamic variables. Fusion picks character, not just IQ — and compensates for cost, availability, and subscription-vs-API. It never asks a model to do what it's bad at, and it never switches models mid-turn. Tier boundaries are session boundaries.

The middle-manager structure is deliberate: a genius planner with a dumb doer is lossy (that's how 1970s management decayed). Fusion's fix is boring, correctness-preserving middle managers and a feedback loop that escalates **decisions**, not struggles.

## Install

| Harness | Command |
|---|---|
| **Hermes** | `hermes plugins install BoredSexyJordan/fusion-router#hermes` → `hermes plugins enable fusion` → `hermes fusion run fusion/packet.json` |
| **Claude Code** | `claude plugin marketplace add BoredSexyJordan/fusion-router` → `claude plugin install fusion-orchestrator@boredsexy-hermes` → `/fusion-run` |
| **Grok Build / Grok Bot** | `grok plugin marketplace add BoredSexyJordan/fusion-router` → `grok plugin install fusion-orchestrator --trust` |
| **Codex** | worker lane (see the site) |

## Layout

```
fusion-orchestrator/      the plugin (multi-skin: .claude-plugin, .grok-plugin, plugin.json)
hermes/                   the Hermes plugin (install via ...#hermes subdir)
site/                     the website (src: single index.html, dark + light)
.claude-plugin/           Claude Code marketplace index
.grok-plugin/             Grok marketplace index
```

## License

Private / closed until publication; distribution scaffolds out once the marketplace goes public.

---

Built by [BoredSexyJordan](https://github.com/BoredSexyJordan).
