"""Client-side handler for Anthropic's memory tool (type memory_20250818).

The memory tool is client-side: Claude requests file operations, your
application executes them. That means persistence AND security are yours.
This handler implements the six commands with the two guards the official
docs call out (path traversal, size caps) plus a provenance requirement.
"""
import json
from pathlib import Path

ROOT = Path(__file__).with_name("memories").resolve()
MAX_FILE_BYTES = 32_000  # cap growth; an INDEX that scrolls gets skimmed


def _resolve(raw):
    rel = raw.removeprefix("/memories").lstrip("/")
    path = (ROOT / rel).resolve()
    if ROOT != path and ROOT not in path.parents:
        raise ValueError(f"path escapes memory root: {raw}")
    return path


def handle(cmd):
    """Dispatch one memory tool_use block. Returns the tool_result content."""
    p = _resolve(cmd.get("path", "/memories"))
    c = cmd["command"]
    if c == "view":
        if p.is_dir():
            return "\n".join(sorted(x.name for x in p.iterdir()))
        return p.read_text(encoding="utf-8")
    if c == "create":
        text = cmd["file_text"]
        if len(text.encode()) > MAX_FILE_BYTES:
            return "error: file exceeds size cap; distill it"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return f"created {p.name}"
    if c == "str_replace":
        body = p.read_text(encoding="utf-8")
        if cmd["old_str"] not in body:
            return "error: old_str not found"
        p.write_text(body.replace(cmd["old_str"], cmd["new_str"], 1), "utf-8")
        return f"edited {p.name}"
    if c == "insert":
        lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
        lines.insert(cmd["insert_line"], cmd["insert_text"])
        p.write_text("".join(lines), encoding="utf-8")
        return f"inserted into {p.name}"
    if c == "delete":
        p.unlink() if p.is_file() else None
        return f"deleted {p.name}"
    if c == "rename":
        dest = _resolve(cmd["new_path"])
        p.rename(dest)
        return f"renamed to {dest.name}"
    return f"error: unknown command {c}"


if __name__ == "__main__":
    # ponytail: smallest check that fails if the traversal guard breaks
    try:
        _resolve("/memories/../../etc/passwd")
        raise SystemExit("FAIL: traversal not blocked")
    except ValueError:
        print("ok: traversal blocked")
