"""Part 7: diff an Opus-era request config against Fable 5's requirements.

Point it at a JSON request body you already send to Opus 4.8 and it reports
every change you must make before that same body is valid on claude-fable-5.
None of these are style opinions; each one is a hard 400 or a silent
token-cost bug on Fable 5.

    python migration/migration_linter.py migration/sample_opus_request.json
"""
import json
import sys
from pathlib import Path

# Params Fable 5 rejects with a 400 when set to a non-default value.
SAMPLING_PARAMS = ("temperature", "top_p", "top_k")


def lint(req):
    findings = []

    for p in SAMPLING_PARAMS:
        if p in req:
            findings.append(
                (p, "error", f"{p} returns 400 on Fable 5. Remove it; adaptive "
                 "thinking is always on and does not accept sampling params."))

    thinking = req.get("thinking")
    if isinstance(thinking, dict):
        if thinking.get("type") == "disabled":
            findings.append(("thinking", "error",
                             "thinking:{type:'disabled'} is rejected. Thinking is "
                             "always on; omit the field."))
        if "budget_tokens" in thinking:
            findings.append(("thinking.budget_tokens", "error",
                             "Manual budget_tokens is rejected. Use "
                             "output_config.effort instead."))

    for m in req.get("messages", []):
        if m.get("role") == "assistant":
            for block in m.get("content", []) if isinstance(m.get("content"), list) else []:
                if isinstance(block, dict) and block.get("type") in ("thinking", "redacted_thinking"):
                    findings.append(("messages", "warn",
                                     "Assistant turn carries a thinking block. On a "
                                     "cross-model switch (incl. an Opus fallback) strip "
                                     "thinking/redacted_thinking; ignored blocks still "
                                     "bill as input tokens."))
                    break

    if req.get("model") == "claude-fable-5" and "fallbacks" not in req:
        findings.append(("fallbacks", "warn",
                         "No fallbacks wired. A refusal is an HTTP 200 with empty "
                         "content; add fallbacks + the server-side-fallback beta header."))

    if "output_config" not in req or "effort" not in req.get("output_config", {}):
        findings.append(("output_config.effort", "info",
                         "No effort set. Fable 5 defaults to 'high'; set it "
                         "explicitly so a fleet-wide change is one edit, not many."))

    return findings


def main(path):
    req = json.loads(Path(path).read_text(encoding="utf-8"))
    findings = lint(req)
    if not findings:
        print("clean: this request is already Fable-5 valid")
        return 0
    errors = 0
    for field, sev, msg in findings:
        if sev == "error":
            errors += 1
        print(f"  {sev:<5}  {field}\n         {msg}")
    print(f"\n{len(findings)} finding(s), {errors} that 400 on Fable 5")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else
                  str(Path(__file__).with_name("sample_opus_request.json"))))
