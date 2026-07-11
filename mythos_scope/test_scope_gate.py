"""Runnable self-check: python -m mythos_scope.test_scope_gate"""
from mythos_scope.scope_gate import lint_scope


def test_valid_mythos_scope_packet_is_clean():
    packet = {
        "model": "claude-mythos-5",
        "authorization_id": "APPROVED-DEFENSIVE-CHANGE-1234",
        "glasswing_scope_id": "GLASSWING-SCOPE-1",
        "target_repositories": ["internal/service-a"],
        "allowed_actions": ["inspect", "reproduce", "patch", "verify", "report"],
        "network_access": False,
        "reproduction_sandbox": "isolated-container-no-egress",
        "evidence_store": "private-vuln-artifacts",
        "artifact_policy": {"public_poc": False, "private_store_required": True},
        "validation": {
            "required": True,
            "independent_validator": "security-validation",
        },
        "human_patch_owner": "security-engineering",
    }
    assert not [f for f, sev, _ in lint_scope(packet) if sev == "error"]


def test_mythos_requires_authorization_and_private_artifacts():
    packet = {
        "model": "claude-mythos-5",
        "target_repositories": ["internal/service-a"],
        "allowed_actions": ["inspect", "public_poc"],
        "artifact_policy": {"public_poc": True},
        "validation": {"required": False},
    }
    fields = {f for f, sev, _ in lint_scope(packet) if sev == "error"}
    assert "authorization_id" in fields
    assert "glasswing_scope_id" in fields
    assert "allowed_actions" in fields
    assert "artifact_policy.public_poc" in fields
    assert "validation.required" in fields


def test_fable_packet_warns_without_refusal_path():
    packet = {
        "model": "claude-fable-5",
        "target_repositories": ["internal/service-a"],
        "allowed_actions": ["inspect", "report"],
    }
    warnings = {f for f, sev, _ in lint_scope(packet) if sev == "warn"}
    assert "refusal_logging" in warnings
    assert "fallbacks" in warnings


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok  {name}")
    print("all checks passed")
