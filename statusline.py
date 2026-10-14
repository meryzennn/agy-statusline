#!/usr/bin/env python3
"""
Custom Statusline for Google Antigravity CLI (agy)
Cross-platform support: Windows, Linux, macOS.

Features:
- Live Agent State Badge (READY, THINKING, WORKING, TOOL, INIT)
- Active Model Name & Effort/Mode (Gemini, Claude, GPT, etc.)
- Context Window usage (Smooth Unicode progress bar, Used %, Token counts, >200k alert)
- Quota & Rate Limits (Short-term 5h window & Weekly cap with reset countdowns)
- Git branch & dirty status (zero-subprocess instant .git/HEAD inspection)
- Background task & artifact badges
- Responsive layout (Wide 1-line, Medium 2-line, Narrow compact)
- Zero external dependencies (Pure Python 3 standard library)
"""

import sys
import json
import os
from datetime import timedelta

# Ensure UTF-8 I/O encoding on Windows without crashing
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ==============================================================================
# Configuration Options
# ==============================================================================
# Layout mode: "auto" (adapts to terminal width), "single" (force 1 line), "double" (force 2 lines)
LAYOUT_MODE = "auto"
BAR_WIDTH_CTX = 8
BAR_WIDTH_QUOTA = 7
DEBUG_LOG_PAYLOAD = False  # Set to True to save ~/.gemini/antigravity-cli/last_statusline_payload.json

# ANSI Color Codes (Universal 16-color palette, high contrast on dark & light themes)
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Text Colors
FG_RED = "\033[31;1m"
FG_GREEN = "\033[32;1m"
FG_YELLOW = "\033[33;1m"
FG_BLUE = "\033[34;1m"
FG_MAGENTA = "\033[35;1m"
FG_CYAN = "\033[36;1m"
FG_WHITE = "\033[97;1m"
FG_MUTED = "\033[90m"

# Progress bar sub-block characters for smooth 1/8th resolution
SUB_BLOCKS = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉"]


def format_tokens(num):
    """Format token count into compact human-readable string (e.g. 14.5k, 1.0M)"""
    if num is None:
        return "0"
    try:
        val = float(num)
    except (ValueError, TypeError):
        return "0"
    if val >= 1_000_000:
        return f"{val / 1_000_000:.1f}M"
    elif val >= 1_000:
        return f"{val / 1_000:.1f}k"
    return str(int(val))


def format_duration(seconds):
    """Format seconds into concise human duration (e.g. 6d 11h, 3h 25m, 45m)"""
    if seconds is None:
        return ""
    try:
        sec = int(seconds)
    except (ValueError, TypeError):
        return ""
    if sec <= 0:
        return "now"
    td = timedelta(seconds=sec)
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    if days > 0:
        return f"{days}d {hours}h" if hours > 0 else f"{days}d"
    elif hours > 0:
        return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    return f"{sec}s"


def render_bar(pct, width=8, fill_color=FG_GREEN, empty_color=FG_MUTED):
    """Render a smooth Unicode progress bar with sub-block characters"""
    pct = max(0.0, min(100.0, float(pct)))
    total_val = (pct / 100.0) * width
    full_blocks = int(total_val)
    remainder = total_val - full_blocks
    partial_char = SUB_BLOCKS[int(remainder * 8)] if full_blocks < width else ""

    empty_count = width - full_blocks - (1 if partial_char else 0)
    empty_count = max(0, empty_count)

    bar = fill_color + ("█" * full_blocks) + partial_char + RESET
    if empty_count > 0:
        bar += empty_color + ("░" * empty_count) + RESET
    return bar


def get_git_branch(cwd):
    """Fast, zero-subprocess git branch detection via .git/HEAD"""
    if not cwd or not os.path.exists(cwd):
        return ""
    try:
        git_dir = os.path.join(cwd, ".git")
        if os.path.isfile(git_dir):  # git worktree / submodule pointer
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
                return ref[:7]  # Detached commit hash
    except Exception:
        pass
    return ""


def render_statusline(data):
    # --------------------------------------------------------------------------
    # 1. Agent State Indicator
    # --------------------------------------------------------------------------
    raw_state = (data.get("agent_state") or "idle").lower()
    if raw_state == "idle":
        state_str = f"{FG_GREEN}● READY{RESET}"
    elif raw_state == "thinking":
        state_str = f"{FG_YELLOW}◆ THINKING{RESET}"
    elif raw_state == "working":
        state_str = f"{FG_CYAN}⚙ WORKING{RESET}"
    elif raw_state == "tool_use":
        state_str = f"{FG_MAGENTA}⚡ TOOL{RESET}"
    elif raw_state == "initializing":
        state_str = f"{FG_BLUE}⏳ INIT{RESET}"
    else:
        state_str = f"{FG_WHITE}● {raw_state.upper()}{RESET}"

    # --------------------------------------------------------------------------
    # 2. Model Name & Execution Mode
    # --------------------------------------------------------------------------
    model_obj = data.get("model")
    if isinstance(model_obj, dict):
        model_name = model_obj.get("display_name") or model_obj.get("id") or "Gemini"
        model_id = (model_obj.get("id") or "").lower()
    elif isinstance(model_obj, str):
        model_name = model_obj
        model_id = model_obj.lower()
    else:
        model_name = "Gemini"
        model_id = "gemini"

    model_str = f"{FG_MAGENTA}✦ {model_name}{RESET}"
    model_compact = f"{FG_MAGENTA}{model_name}{RESET}"

    # --------------------------------------------------------------------------
    # 3. Context Window (Tokens used, limit, percentage, visual bar)
    # --------------------------------------------------------------------------
    ctx = data.get("context_window") or {}
    total_in = ctx.get("total_input_tokens") or 0
    total_out = ctx.get("total_output_tokens") or 0
    curr_usage = ctx.get("current_usage") or {}
    if total_in + total_out > 0:
        used_tokens = total_in + total_out
    else:
        used_tokens = (curr_usage.get("input_tokens") or 0) + (curr_usage.get("output_tokens") or 0)

    ctx_limit = ctx.get("context_window_size") or 1048576
    used_pct = ctx.get("used_percentage")
    if used_pct is None:
        used_pct = (used_tokens / ctx_limit * 100.0) if ctx_limit > 0 else 0.0

    # Dynamic color for context usage
    if used_pct >= 85.0:
        ctx_color = FG_RED
    elif used_pct >= 65.0:
        ctx_color = FG_YELLOW
    else:
        ctx_color = FG_CYAN

    ctx_bar = render_bar(used_pct, width=BAR_WIDTH_CTX, fill_color=ctx_color, empty_color=FG_MUTED)
    tokens_str = f"{format_tokens(used_tokens)}/{format_tokens(ctx_limit)}"
    exceeds_warn = f" {FG_YELLOW}[!>200k]{RESET}" if data.get("exceeds_200k_tokens") else ""

    ctx_full = f"{FG_MUTED}ctx:{RESET} {ctx_bar} {ctx_color}{used_pct:.1f}%{RESET} {FG_MUTED}({tokens_str}){RESET}{exceeds_warn}"
    ctx_compact = f"{FG_MUTED}ctx:{RESET} {ctx_color}{used_pct:.1f}%{RESET} {FG_MUTED}({format_tokens(used_tokens)}){RESET}"

    # --------------------------------------------------------------------------
    # 4. Quota / Rate Limit (Short-term 5h & Weekly cap)
    # --------------------------------------------------------------------------
    quota_obj = data.get("quota") or {}
    quota_parts_full = []
    quota_parts_compact = []

    if isinstance(quota_obj, dict) and quota_obj:
        # Determine prefix based on active model (e.g. gemini vs 3p / claude)
        is_3p = any(tag in model_id for tag in ["claude", "3p", "sonnet", "gpt", "o1", "o3"])
        prefix = "3p" if is_3p else "gemini"

        h5_info = quota_obj.get(f"{prefix}-5h")
        wk_info = quota_obj.get(f"{prefix}-weekly")

        # Fallback to any available bucket if prefix not found
        if not h5_info and not wk_info:
            for k, v in quota_obj.items():
                if "5h" in k:
                    h5_info = v
                elif "weekly" in k:
                    wk_info = v
            if not h5_info and not wk_info:
                # Fallback to first available bucket
                k, v = next(iter(quota_obj.items()))
                h5_info = v

        # Format 5h short-term rolling quota
        if h5_info and isinstance(h5_info, dict) and "remaining_fraction" in h5_info:
            frac = float(h5_info.get("remaining_fraction") or 0.0)
            pct = frac * 100.0
            reset_sec = h5_info.get("reset_in_seconds")
            time_str = format_duration(reset_sec)
            time_badge = f" {FG_MUTED}({time_str}){RESET}" if time_str else ""
            color = FG_RED if pct <= 15.0 else (FG_YELLOW if pct <= 40.0 else FG_GREEN)
            bar = render_bar(pct, width=BAR_WIDTH_QUOTA, fill_color=color, empty_color=FG_MUTED)

            quota_parts_full.append(f"{FG_MUTED}5h:{RESET} {bar} {color}{pct:.0f}%{RESET}{time_badge}")
            quota_parts_compact.append(f"{FG_MUTED}5h:{RESET} {color}{pct:.0f}%{RESET}{time_badge}")

        # Format weekly quota cap
        if wk_info and isinstance(wk_info, dict) and "remaining_fraction" in wk_info:
            frac = float(wk_info.get("remaining_fraction") or 0.0)
            pct = frac * 100.0
            reset_sec = wk_info.get("reset_in_seconds")
            time_str = format_duration(reset_sec)
            time_badge = f" {FG_MUTED}({time_str}){RESET}" if time_str else ""
            color = FG_RED if pct <= 15.0 else (FG_YELLOW if pct <= 40.0 else FG_GREEN)
            bar = render_bar(pct, width=BAR_WIDTH_QUOTA, fill_color=color, empty_color=FG_MUTED)

            quota_parts_full.append(f"{FG_MUTED}wk:{RESET} {color}{pct:.0f}%{RESET}{time_badge}")
            quota_parts_compact.append(f"{FG_MUTED}wk:{RESET} {color}{pct:.0f}%{RESET}{time_badge}")

    # Fallback if quota object not provided
    if not quota_parts_full:
        plan_tier = data.get("plan_tier")
        if plan_tier:
            quota_parts_full.append(f"{FG_MUTED}tier:{RESET} {FG_GREEN}{plan_tier}{RESET}")
            quota_parts_compact.append(f"{FG_GREEN}{plan_tier}{RESET}")
        else:
            quota_parts_full.append(f"{FG_MUTED}quota:{RESET} {FG_GREEN}100%{RESET}")
            quota_parts_compact.append(f"{FG_MUTED}quota:{RESET} {FG_GREEN}100%{RESET}")

    quota_full = f"{FG_MUTED} │ {RESET}".join(quota_parts_full)
    quota_compact = f"{FG_MUTED} · {RESET}".join(quota_parts_compact)

    # --------------------------------------------------------------------------
    # 5. VCS (Git Branch & Dirty status)
    # --------------------------------------------------------------------------
    vcs = data.get("vcs") or {}
    branch = vcs.get("branch")
    dirty = vcs.get("dirty", False)

    # If branch not given in payload, resolve instantly from .git/HEAD
    if not branch:
        cwd = data.get("cwd") or (data.get("workspace") or {}).get("project_dir")
        branch = get_git_branch(cwd)

    vcs_str = ""
    if branch:
        dirty_flag = f"{FG_YELLOW}*" if dirty else ""
        vcs_str = f"{FG_BLUE} {branch}{dirty_flag}{RESET}"

    # --------------------------------------------------------------------------
    # 6. Status Badges & Extras (Mode, Tasks, Vim, Pending Input)
    # --------------------------------------------------------------------------
    badges = []

    exec_mode = data.get("execution_mode")
    if exec_mode and exec_mode.lower() not in ("normal", "fast"):
        badges.append(f"{FG_CYAN}[{exec_mode}]{RESET}")

    vim = data.get("vim")
    if isinstance(vim, dict) and vim.get("mode"):
        badges.append(f"{FG_YELLOW}[{vim['mode']}]{RESET}")

    pending_in = data.get("pending_input_count", 0)
    if pending_in and pending_in > 0:
        badges.append(f"{FG_YELLOW}📥{pending_in}{RESET}")

    if data.get("tool_confirmation_pending"):
        badges.append(f"{FG_RED}[!confirm]{RESET}")

    task_count = data.get("task_count", 0)
    if task_count and task_count > 0:
        badges.append(f"{FG_YELLOW}⚡{task_count}t{RESET}")

    art_count = data.get("artifact_count", 0)
    if art_count and art_count > 0:
        badges.append(f"{FG_MUTED}📄{art_count}a{RESET}")

    badges_str = " ".join(badges)

    # --------------------------------------------------------------------------
    # 7. Responsive Layout Composition
    # --------------------------------------------------------------------------
    term_width = data.get("terminal_width") or 100
    sep = f"{FG_MUTED} │ {RESET}"

    is_wide = (LAYOUT_MODE == "single") or (LAYOUT_MODE == "auto" and term_width >= 125)
    is_medium = (LAYOUT_MODE == "double") or (LAYOUT_MODE == "auto" and term_width >= 78)

    if is_wide:
        # Full Single-Line Layout
        elements = [state_str, model_str, ctx_full, quota_full]
        if vcs_str:
            elements.append(vcs_str)
        if badges_str:
            elements.append(badges_str)
        return sep.join(elements)

    elif is_medium:
        # Balanced 2-Line Layout
        top_line = [state_str, model_str]
        if vcs_str:
            top_line.append(vcs_str)
        if badges_str:
            top_line.append(badges_str)

        bottom_line = [ctx_full, quota_full]

        line1 = f"{FG_MUTED}╭─{RESET} " + sep.join(top_line)
        line2 = f"{FG_MUTED}╰─{RESET} " + sep.join(bottom_line)
        return f"{line1}\n{line2}"

    else:
        # Compact Layout for Narrow Terminals
        line1 = f"{state_str} {sep} {model_compact}"
        if vcs_str:
            line1 += f" {sep} {vcs_str}"
        line2 = f"{ctx_compact} {sep} {quota_compact}"
        return f"{line1}\n{line2}"


def main():
    try:
        raw_bytes = sys.stdin.buffer.read()
        if not raw_bytes:
            return
        # Decode and strip UTF-8 BOM if present
        raw_text = raw_bytes.decode("utf-8-sig", errors="replace").strip()
        if not raw_text:
            return

        # Save live debug payload if enabled
        if DEBUG_LOG_PAYLOAD:
            try:
                dump_path = os.path.expanduser("~/.gemini/antigravity-cli/last_statusline_payload.json")
                with open(dump_path, "w", encoding="utf-8") as f:
                    f.write(raw_text)
            except Exception:
                pass

        data = json.loads(raw_text)
        rendered = render_statusline(data)
        print(rendered)
    except Exception:
        # Silent fallback
        print(f"{FG_GREEN}● READY{RESET}")


if __name__ == "__main__":
    main()
