"""Validate a Fable/Mythos security-work scope packet.

Fable 5 and Mythos 5 share a capability class, but they do not share the same
safety envelope. Fable workloads should be wired for refusal/fallback
observability. Mythos workloads, available only through approved Project
Glasswing access, need an external scope gate because Fable's cyber classifiers
are not the boundary.

    python mythos_scope/scope_gate.py mythos_scope/sample_mythos_scope.json
"""
import json
import sys
from pathlib import Path

FABLE = "claude-fable-5"
MYTHOS = "claude-mythos-5"

ALLOWED_ACTIONS = {"inspect", "reproduce", "patch", "verify", "report"}
FORBIDDEN_ACTIONS = {
    "public_poc",
    "credential_access",
    "external_targeting",
    "persistence",
    "exfiltration",
}


def _present(packet, field):
    value = packet.get(field)
    return value is not None and value != "" and value != []


def _flag(findings, field, severity, message):
    findings.append((field, severity, message))


def lint_scope(packet):
    """Return (field, severity, message) findings for a scope packet."""
    findings = []
    model = packet.get("model")
    actions = set(packet.get("allowed_actions", []))

    if model not in {FABLE, MYTHOS}:
        _flag(findings, "model", "error",
              "Model must be claude-fable-5 or claude-mythos-5.")

    if not _present(packet, "target_repositories"):
        _flag(findings, "target_repositories", "error",
              "Name the repositories or products in scope.")

    unknown = sorted(actions - ALLOWED_ACTIONS - FORBIDDEN_ACTIONS)
    if unknown:
        _flag(findings, "allowed_actions", "error",
              "Unknown action(s): " + ", ".join(unknown))

    forbidden = sorted(actions & FORBIDDEN_ACTIONS)
    if forbidden:
        _flag(findings, "allowed_actions", "error",
              "Forbidden action(s) cannot be approved here: " + ", ".join(forbidden))

    if model == FABLE:
        if not packet.get("refusal_logging"):
            _flag(findings, "refusal_logging", "warn",
                  "Fable workloads should log stop_reason and stop_details.category.")
        if not packet.get("fallbacks"):
            _flag(findings, "fallbacks", "warn",
                  "Fable workloads should define a refusal fallback path.")

    if model == MYTHOS:
        for field in (
            "authorization_id",
            "glasswing_scope_id",
            "evidence_store",
            "human_patch_owner",
        ):
            if not _present(packet, field):
                _flag(findings, field, "error",
                      "Mythos workloads require this field before the run starts.")

        validation = packet.get("validation", {})
        if not validation.get("required"):
            _flag(findings, "validation.required", "error",
                  "Mythos findings require independent validation.")
        if not validation.get("independent_validator"):
            _flag(findings, "validation.independent_validator", "error",
                  "Name the person or team validating the findings.")

        artifacts = packet.get("artifact_policy", {})
        if artifacts.get("public_poc") is not False:
            _flag(findings, "artifact_policy.public_poc", "error",
                  "Public proof-of-concept artifacts are not allowed by this gate.")
        if artifacts.get("private_store_required") is not True:
            _flag(findings, "artifact_policy.private_store_required", "error",
                  "Mythos artifacts must be stored in a private evidence store.")

        if "reproduce" in actions and not _present(packet, "reproduction_sandbox"):
            _flag(findings, "reproduction_sandbox", "error",
                  "Reproduction work requires an isolated sandbox.")

        if packet.get("network_access") and not _present(packet, "network_access_approval_id"):
            _flag(findings, "network_access", "error",
                  "Network access requires a separate approval id.")

        if packet.get("refusal_logging"):
            _flag(findings, "refusal_logging", "info",
                  "Mythos does not use Fable's classifier refusal signal as its boundary.")

    return findings


def main(path):
    packet = json.loads(Path(path).read_text(encoding="utf-8"))
    findings = lint_scope(packet)
    if not findings:
        print("clean: scope packet is ready")
        return 0

    errors = 0
    for field, severity, message in findings:
        if severity == "error":
            errors += 1
        print(f"  {severity:<5}  {field}\n         {message}")
    print(f"\n{len(findings)} finding(s), {errors} blocking")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else
                  str(Path(__file__).with_name("sample_mythos_scope.json"))))
