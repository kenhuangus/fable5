# fable5-skills

10 Agent Skills written for how Claude Fable 5 actually behaves, independently
designed for this series after auditing (not reusing) a third-party
collection. See Part 6 of the Substack series for the audit and the design
notes.

| # | Skill | What it fixes |
|---|-------|---------------|
| 1 | [`effort-router`](effort-router/SKILL.md) | Picking and re-evaluating `output_config.effort` per workload instead of carrying over an old model's defaults. |
| 2 | [`scope-fence`](scope-fence/SKILL.md) | Unrequested actions -- applying a fix when only asked to diagnose, restarting a service, backup branches nobody asked for. |
| 3 | [`no-gold-plating`](no-gold-plating/SKILL.md) | Diffs bigger than the ask: speculative abstractions, defensive checks for impossible states. |
| 4 | [`evidence-bound-progress`](evidence-bound-progress/SKILL.md) | Status reports on long runs bound to an actual tool result, never a fabricated "tests passing". |
| 5 | [`act-on-sufficiency`](act-on-sufficiency/SKILL.md) | Over-planning and re-deriving settled facts at high effort. |
| 6 | [`verifier-subagent`](verifier-subagent/SKILL.md) | Fresh-context verifier subagents instead of self-critique; the maker never grades its own work. |
| 7 | [`autonomy-contract`](autonomy-contract/SKILL.md) | Unattended runs that stall on a stated intent or a mid-run permission question. |
| 8 | [`lesson-memory`](lesson-memory/SKILL.md) | File-based cross-session memory, with the anti-poisoning gate a shared lesson file needs. |
| 9 | [`reader-first-summary`](reader-first-summary/SKILL.md) | Final reports readable by someone who saw none of the work -- no arrow chains, no invented shorthand. |
| 10 | [`refusal-aware-calling`](refusal-aware-calling/SKILL.md) | `claude-fable-5` calls that degrade gracefully on a classifier refusal instead of dead-ending. |

## Install

**Claude Code, as a plugin:**

```
/plugin marketplace add kenhuangus/fable5
/plugin install fable5-skills@fable5
```

**Manual, per skill:**

```bash
git clone https://github.com/kenhuangus/fable5
cp -r fable5/skills/scope-fence ~/.claude/skills/
```

## How they activate

`effort-router`, `verifier-subagent`, and `lesson-memory` are task-shaped and
trigger automatically when a matching request appears. The rest are standing
behavioral rules -- a model mid-over-planning won't reliably invoke
`act-on-sufficiency` on its own. For those, either invoke explicitly in an
interactive session, or copy the skill body into your system prompt /
`CLAUDE.md` for unattended pipelines (`autonomy-contract` is written for
exactly that case).
