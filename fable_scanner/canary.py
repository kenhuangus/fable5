"""fable_scanner canary -- regression canary for silent quality drift on Fable 5.

    python -m fable_scanner canary init                 # writes baseline.json
    python -m fable_scanner canary run                   # needs ANTHROPIC_API_KEY
    python -m fable_scanner canary diff                   # compare last run to baseline

Anthropic's own refusals-and-fallback doc recommends a regression canary for
catching silent degradation. This is that canary: a fixed prompt set with
expected-output checks, run periodically, alerting on refusal-rate or
latency drift versus the first captured run.

Reuses the client/model/fallback wiring from job_packet.packet instead of
duplicating it.
"""
import json
import statistics
import sys
import time
from pathlib import Path

from job_packet.packet import client, FABLE, BETAS, FALLBACKS

BASELINE_FILE = Path(".fable-scanner/baseline.json")
LATEST_FILE = Path(".fable-scanner/latest.json")

DEFAULT_PROMPTS = [
    {"id": "code-simple", "prompt": "Write a Python function that reverses a string. Return only the code.",
     "expect": {"contains": ["def ", "return"], "min_len": 20}},
    {"id": "reason-plain", "prompt": "A tank fills at 3L/min and drains at 1L/min. Starting empty, how many "
     "liters after 10 minutes? Answer with a single number.",
     "expect": {"contains": ["20"], "max_len": 200}},
    {"id": "instruction-follow", "prompt": "Reply with EXACTLY three words: alpha bravo charlie",
     "expect": {"exact": "alpha bravo charlie"}},
    {"id": "knowledge", "prompt": "In one sentence, what is a Bloom filter optimized for?",
     "expect": {"contains": ["false positive"], "max_len": 300}},
]


def _score(expect, output):
    if not expect:
        return 1.0
    out = (output or "").lower()
    checks = hits = 0
    for needle in expect.get("contains", []):
        checks += 1
        hits += needle.lower() in out
    if "exact" in expect:
        checks += 1
        hits += output.strip() == expect["exact"]
    if "min_len" in expect:
        checks += 1
        hits += len(output) >= expect["min_len"]
    if "max_len" in expect:
        checks += 1
        hits += len(output) <= expect["max_len"]
    return hits / checks if checks else 1.0


def _call(prompt, effort="high"):
    t0 = time.monotonic()
    msg = client.beta.messages.create(
        model=FABLE,
        max_tokens=2048,
        output_config={"effort": effort},
        betas=BETAS,
        fallbacks=FALLBACKS,
        messages=[{"role": "user", "content": prompt}],
    )
    ms = (time.monotonic() - t0) * 1000
    refused = msg.stop_reason == "refusal"
    category = getattr(msg.stop_details, "category", None) if refused else None
    text = "" if refused else "".join(b.text for b in msg.content if b.type == "text")
    return {"ms": ms, "refused": refused, "category": category, "output": text}


def init_baseline():
    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if BASELINE_FILE.exists():
        print(f"{BASELINE_FILE} already exists -- remove it to reinit")
        return
    BASELINE_FILE.write_text(json.dumps({"prompts": DEFAULT_PROMPTS, "outcomes": {}}, indent=2))
    print(f"wrote {BASELINE_FILE}")


def run_canary(refusal_max=0.2, latency_max=1.5):
    if not BASELINE_FILE.exists():
        print("canary: no baseline. Run: python -m fable_scanner canary init", file=sys.stderr)
        return 2
    baseline = json.loads(BASELINE_FILE.read_text())
    results = []
    for p in baseline["prompts"]:
        r = _call(p["prompt"])
        r["id"] = p["id"]
        r["score"] = _score(p["expect"], r["output"])
        status = f"refusal ({r['category']})" if r["refused"] else "ok"
        print(f"  {p['id']:<20} {status:<20} {r['ms']:.0f}ms  score={r['score']:.0%}")
        results.append(r)

    LATEST_FILE.write_text(json.dumps({"results": results}, indent=2))

    outcomes = baseline.get("outcomes") or {}
    if not outcomes:
        baseline["outcomes"] = {r["id"]: {"refused": r["refused"], "ms": r["ms"], "score": r["score"]} for r in results}
        BASELINE_FILE.write_text(json.dumps(baseline, indent=2))
        print("first run -- snapshot captured as baseline outcomes")
        return 0

    refusal_rate = sum(r["refused"] for r in results) / len(results)
    base_refusal_rate = sum(o["refused"] for o in outcomes.values()) / max(1, len(outcomes))
    median_ms = statistics.median(r["ms"] for r in results)
    base_median_ms = statistics.median(o["ms"] for o in outcomes.values())
    mean_score = statistics.mean(r["score"] for r in results)

    alerts = []
    if refusal_rate - base_refusal_rate > refusal_max:
        alerts.append(f"refusal rate {refusal_rate:.0%} vs baseline {base_refusal_rate:.0%}")
    if base_median_ms and median_ms / base_median_ms > latency_max:
        alerts.append(f"median latency {median_ms:.0f}ms vs baseline {base_median_ms:.0f}ms")
    if mean_score < 0.6:
        alerts.append(f"mean expected-output score {mean_score:.0%} -- outputs diverging from baseline shape")

    if alerts:
        print("\ndrift alerts:")
        for a in alerts:
            print(f"  ! {a}")
        return 1
    print("\nno drift detected")
    return 0


def main(argv):
    sub = argv[0] if argv else "help"
    if sub == "init":
        init_baseline()
        return 0
    if sub == "run":
        return run_canary()
    print("usage: python -m fable_scanner canary <init|run>")
    return 2 if sub != "help" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
