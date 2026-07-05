"""fable_scanner monitor -- refusal analytics from Anthropic Messages API response logs.

    python -m fable_scanner monitor <log.jsonl>

Input: one JSON object per line, either a raw Messages API response or a
wrapper {"timestamp": ..., "request": ..., "response": ...}. Pure local
file parsing -- no network calls.
"""
import json
import sys
from pathlib import Path

PRICE_PER_M = {
    "claude-fable-5": (10, 50),
    "claude-opus-4-8": (5, 25),
    "claude-sonnet-5": (3, 15),
    "claude-haiku-4-5": (1, 5),
}
CATEGORIES = ["cyber", "bio", "frontier_llm", "reasoning_extraction"]


def _first_user_prompt(request):
    if not request:
        return None
    for m in request.get("messages", []):
        if m.get("role") == "user":
            content = m.get("content")
            return content if isinstance(content, str) else None
    return None


def analyze(lines):
    stats = {
        "total": 0, "refused": 0, "fallback_served": 0,
        "by_category": {c: 0 for c in CATEGORIES},
        "cost_by_model": {},
        "trigger_prefixes": {},
    }
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = obj.get("response", obj)
        req = obj.get("request")
        stats["total"] += 1

        for it in resp.get("usage", {}).get("iterations", []):
            price = PRICE_PER_M.get(it.get("model"))
            if not price:
                continue
            in_price, out_price = price
            cost = it.get("input_tokens", 0) * in_price / 1e6 + it.get("output_tokens", 0) * out_price / 1e6
            stats["cost_by_model"][it["model"]] = stats["cost_by_model"].get(it["model"], 0) + cost
            if it.get("type") == "fallback_message":
                stats["fallback_served"] += 1

        if resp.get("stop_reason") == "refusal":
            stats["refused"] += 1
            cat = (resp.get("stop_details") or {}).get("category")
            if cat in stats["by_category"]:
                stats["by_category"][cat] += 1
            prompt = _first_user_prompt(req)
            if prompt:
                key = prompt[:60]
                entry = stats["trigger_prefixes"].setdefault(key, {"count": 0, "category": cat})
                entry["count"] += 1

    return stats


def print_report(stats):
    print("refusal analytics")
    total, refused = stats["total"], stats["refused"]
    pct = f"{refused / total:.1%}" if total else "0%"
    print(f"total {total}   refused {refused} ({pct})   fallback served {stats['fallback_served']}")

    print("\nby category")
    for cat, count in sorted(stats["by_category"].items(), key=lambda kv: -kv[1]):
        if count:
            print(f"  {cat:<20} {count}")

    print("\ncost by model")
    for model, cost in sorted(stats["cost_by_model"].items(), key=lambda kv: -kv[1]):
        print(f"  {model:<20} ${cost:.4f}")

    print("\ntop refusal-triggering prompt prefixes")
    top = sorted(stats["trigger_prefixes"].items(), key=lambda kv: -kv[1]["count"])[:8]
    for prompt, meta in top:
        print(f"  {meta['count']:<3} {meta['category'] or 'null':<20} {prompt}")


def main(argv):
    if not argv:
        print("usage: python -m fable_scanner monitor <log.jsonl> [--format json]")
        return 2
    path = Path(argv[0])
    if not path.exists():
        print(f"monitor: no such file: {path}", file=sys.stderr)
        return 2
    stats = analyze(path.read_text(encoding="utf-8").splitlines())
    if "--format" in argv and "json" in argv:
        print(json.dumps(stats, indent=2))
    else:
        print_report(stats)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
