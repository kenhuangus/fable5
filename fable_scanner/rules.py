"""Rule set for `scan`: prompt/config anti-patterns for Claude Fable 5.

Each rule is a dict: id, category, severity (error|warn|info), applies
(prompt|config), docs (canonical Anthropic doc it's based on), why, and
check(text) -> list of {line, match, message}.

Independent implementation -- not derived from any third-party tool.
"""
import re

PROMPTING_DOC = "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5"
FALLBACK_DOC = "https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback"
EFFORT_DOC = "https://platform.claude.com/docs/en/build-with-claude/effort"


def _line_of(text, index):
    return text.count("\n", 0, index) + 1


def _regex_rule(pattern, flags=0):
    compiled = re.compile(pattern, flags)

    def check(text):
        return [
            {"line": _line_of(text, m.start()), "match": m.group(0)}
            for m in compiled.finditer(text)
        ]

    return check


RULES = [
    {
        "id": "RX-01",
        "category": "reasoning-extraction",
        "severity": "error",
        "applies": "prompt",
        "docs": PROMPTING_DOC,
        "why": "Asking Fable 5 to echo its internal reasoning as response text is a "
        "documented `reasoning_extraction` refusal trigger. Use adaptive thinking "
        "instead of narrating it in the output.",
        "check": _regex_rule(
            r"\b(?:explain|show|share|walk\s+(?:me|us)\s+through)\s+(?:your|the)\s+"
            r"(?:reasoning|thinking|thought\s+process|chain[- ]?of[- ]?thought)",
            re.IGNORECASE,
        ),
    },
    {
        "id": "RX-02",
        "category": "reasoning-extraction",
        "severity": "error",
        "applies": "prompt",
        "docs": PROMPTING_DOC,
        "why": "\"Think step by step\" / \"think out loud\" asks the model to "
        "externalize thinking as output, another reasoning_extraction trigger.",
        "check": _regex_rule(r"\bthink\s+(?:out\s+loud|aloud|step[- ]by[- ]step)\b", re.IGNORECASE),
    },
    {
        "id": "OT-01",
        "category": "overtriggering",
        "severity": "warn",
        "applies": "prompt",
        "docs": PROMPTING_DOC,
        "why": "IMPORTANT/CRITICAL/WARNING framing compensated for weaker instruction "
        "following on older models. Fable 5 gives the same weight to a plain sentence.",
        "check": _regex_rule(r"^[ \t]*(?:IMPORTANT|CRITICAL|WARNING|ATTENTION):", re.MULTILINE),
    },
    {
        "id": "OT-02",
        "category": "overtriggering",
        "severity": "warn",
        "applies": "prompt",
        "docs": PROMPTING_DOC,
        "why": "\"YOU MUST\" / \"YOU MUST NOT\" shouting. State the constraint plainly.",
        "check": _regex_rule(r"\bYOU\s+MUST(?:\s+NOT)?\b"),
    },
    {
        "id": "OT-03",
        "category": "overtriggering",
        "severity": "warn",
        "applies": "prompt",
        "docs": PROMPTING_DOC,
        "why": "Thoroughness appeals (\"DO NOT MISS/FORGET/SKIP\") push toward the "
        "elaborate-and-cover-everything mode Fable needs to be steered away from.",
        "check": _regex_rule(r"\bDO\s+NOT\s+(?:MISS|FORGET|SKIP|OMIT)\b", re.IGNORECASE),
    },
    {
        "id": "OM-01",
        "category": "old-model",
        "severity": "warn",
        "applies": "prompt",
        "docs": PROMPTING_DOC,
        "why": "12+ enumerated behavior items suggests a skill written for a weaker "
        "model. Fable 5 follows a brief intent statement better than a long list.",
        "check": lambda text: (
            lambda lines: [{"line": lines[0][0], "match": f"{len(lines)} enumerated items"}]
            if len(lines) >= 12
            else []
        )([
            (i + 1, ln)
            for i, ln in enumerate(text.splitlines())
            if re.match(r"^[ \t]*(?:[-*•]|\d+[.)])\s+", ln)
        ]),
    },
    {
        "id": "FS-01",
        "category": "fable-specific",
        "severity": "error",
        "applies": "prompt",
        "docs": PROMPTING_DOC,
        "why": "Surfacing a remaining-token countdown makes Fable 5 wrap up early. "
        "Never show the model its own context budget.",
        "check": _regex_rule(
            r"\b(?:tokens?|context)\s+(?:remaining|left|budget)\b|\b\d+\s*k?\s*tokens?\s+(?:left|remaining)\b",
            re.IGNORECASE,
        ),
    },
    {
        "id": "FS-02",
        "category": "fable-specific",
        "severity": "warn",
        "applies": "config",
        "docs": EFFORT_DOC,
        "why": "temperature/top_p/top_k are not supported on Fable 5 -- the API "
        "returns 400.",
        "check": _regex_rule(r'"(?:temperature|top_p|top_k)"\s*:\s*[^,}\s]+'),
    },
    {
        "id": "FS-03",
        "category": "fable-specific",
        "severity": "warn",
        "applies": "config",
        "docs": EFFORT_DOC,
        "why": "Manual `thinking: {type: \"enabled\", budget_tokens: N}` is rejected "
        "on Fable 5. Thinking is always on; control depth with output_config.effort.",
        "check": _regex_rule(r'"thinking"\s*:\s*\{\s*"type"\s*:\s*"enabled"'),
    },
    {
        "id": "MG-01",
        "category": "missing-guardrails",
        "severity": "warn",
        "applies": "config",
        "docs": FALLBACK_DOC,
        "why": "A claude-fable-5 call with no `fallbacks` dead-ends on refusal: "
        "HTTP 200, stop_reason=refusal, empty content, and nothing recovers it.",
        "check": lambda text: (
            []
            if "claude-fable-5" not in text or '"fallbacks"' in text
            else [{"line": _line_of(text, text.index("claude-fable-5")), "match": "claude-fable-5"}]
        ),
    },
    {
        "id": "MG-02",
        "category": "missing-guardrails",
        "severity": "info",
        "applies": "prompt",
        "docs": PROMPTING_DOC,
        "why": "Long-running agent prompts without a progress-audit line let Fable 5 "
        "fabricate status updates.",
        "check": lambda text: (
            []
            if not (re.search(r"(?:autonomous|long[- ]running|agentic|orchestrat)", text, re.IGNORECASE) and len(text) > 800)
            or re.search(r"audit\s+(?:each|every)\s+claim|verified\s+against\s+a\s+tool\s+result", text, re.IGNORECASE)
            else [{"line": 1, "match": "<missing progress-audit>"}]
        ),
    },
]


def run_rules(text, kind):
    findings = []
    for rule in RULES:
        if rule["applies"] != kind:
            continue
        for hit in rule["check"](text):
            findings.append({**hit, "rule": rule})
    return sorted(findings, key=lambda f: (f["line"], f["rule"]["id"]))
