"""Runnable self-check: python -m migration.test_migration_linter"""
from migration.migration_linter import lint


def test_flags_sampling_params_and_manual_thinking():
    req = {
        "model": "claude-fable-5",
        "temperature": 0.7,
        "top_p": 0.9,
        "thinking": {"type": "enabled", "budget_tokens": 8000},
        "output_config": {"effort": "high"},
    }
    fields = {f for f, _, _ in lint(req)}
    assert "temperature" in fields
    assert "top_p" in fields
    assert "thinking.budget_tokens" in fields
    errors = [f for f, sev, _ in lint(req) if sev == "error"]
    assert len(errors) >= 3


def test_flags_carried_thinking_block_on_assistant_turn():
    req = {
        "model": "claude-fable-5",
        "output_config": {"effort": "high"},
        "fallbacks": [{"model": "claude-opus-4-8"}],
        "messages": [
            {"role": "assistant", "content": [
                {"type": "thinking", "thinking": "..."},
                {"type": "text", "text": "hi"},
            ]},
        ],
    }
    assert any(f == "messages" for f, _, _ in lint(req))


def test_clean_request_has_no_errors():
    req = {
        "model": "claude-fable-5",
        "output_config": {"effort": "high"},
        "fallbacks": [{"model": "claude-opus-4-8"}],
        "messages": [{"role": "user", "content": "hi"}],
    }
    assert not [f for f, sev, _ in lint(req) if sev == "error"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok  {name}")
    print("all checks passed")
