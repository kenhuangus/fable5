# Template: the memory scaffold loops need

```markdown
memory/
  INDEX.md          # one line per lesson, newest first
  lessons/
    2026-07-04-flaky-auth-test.md   # one lesson per file:
                                    # summary line, then detail,
                                    # then "why it mattered"
Rules: update an existing lesson rather than duplicating it.
Delete lessons proven wrong. Record what worked AND why.
Every memory write gets one provenance line: which cycle,
which evidence.
```

The one-lesson-per-file shape follows Anthropic's Fable 5 prompting guide.
The provenance line is the anti-poisoning measure: a lesson that can't say
what evidence produced it is a lesson you can't audit later. Keep INDEX.md
under a screenful.
