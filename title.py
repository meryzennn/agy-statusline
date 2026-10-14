#!/usr/bin/env python3
"""
Dynamic Terminal Title for Google Antigravity CLI (agy)
Updates the terminal window/tab title bar based on agent status.
"""

import sys
import json
import os

# Ensure UTF-8 on Windows stdin/stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def get_git_branch(cwd):
    """Fast git branch reader directly from .git/HEAD"""
    if not cwd or not os.path.exists(cwd):
        return ""
    try:
        git_dir = os.path.join(cwd, ".git")
        if os.path.isfile(git_dir):
            with open(git_dir, "r", encoding="utf-8", errors="ignore") as f:
                line = f.read().strip()
                if line.startswith("gitdir:"):
                    git_dir = line.split(":", 1)[1].strip()
        head_path = os.path.join(git_dir, "HEAD")
        if os.path.exists(head_path):
            with open(head_path, "r", encoding="utf-8", errors="ignore") as f:
                ref = f.read().strip()
                if ref.startswith("ref: refs/heads/"):
                    return ref[16:]
                return ref[:7]
    except Exception:
        pass
    return ""


def format_title(data):
    # 1. State indicator
    raw_state = (data.get("agent_state") or "idle").lower()
    if data.get("tool_confirmation_pending"):
        state_badge = "⚠️ CONFIRM"
    elif raw_state == "idle":
        state_badge = "● READY"
    elif raw_state == "thinking":
        state_badge = "◆ THINKING"
    elif raw_state == "working":
        state_badge = "⚙ WORKING"
    elif raw_state == "tool_use":
        state_badge = "⚡ TOOL"
    elif raw_state == "initializing":
        state_badge = "⏳ INIT"
    else:
        state_badge = f"● {raw_state.upper()}"

    # 2. Project folder name
    cwd = data.get("cwd") or (data.get("workspace") or {}).get("project_dir") or ""
    project_name = os.path.basename(os.path.normpath(cwd)) if cwd else "Antigravity"
    if not project_name:
        project_name = "Antigravity"

    # 3. Git branch & dirty flag
    vcs = data.get("vcs") or {}
    branch = vcs.get("branch") or get_git_branch(cwd)
    dirty = vcs.get("dirty", False)
    git_tag = ""
    if branch:
        dirty_flag = "*" if dirty else ""
        git_tag = f" ({branch}{dirty_flag})"

    # 4. Model name (clean / compact)
    model_obj = data.get("model")
    if isinstance(model_obj, dict):
        model_name = model_obj.get("display_name") or model_obj.get("id") or "Gemini"
    elif isinstance(model_obj, str):
        model_name = model_obj
    else:
        model_name = "Gemini"

    # 5. Extras (Tasks or queued inputs)
    extras = []
    task_count = data.get("task_count", 0)
    if task_count and task_count > 0:
        extras.append(f"⚡{task_count}t")
    pending = data.get("pending_input_count", 0)
    if pending and pending > 0:
        extras.append(f"📥{pending}")

    extra_str = f" [{' '.join(extras)}]" if extras else ""

    # Composition: State | Project(branch) - Model [extras]
    return f"{state_badge} | {project_name}{git_tag} - {model_name}{extra_str}"


def main():
    try:
        raw_bytes = sys.stdin.buffer.read()
        if not raw_bytes:
            return
        raw_text = raw_bytes.decode("utf-8-sig", errors="replace").strip()
        if not raw_text:
            return

        data = json.loads(raw_text)
        title = format_title(data)
        print(title)
    except Exception:
        print("Antigravity")


if __name__ == "__main__":
    main()
