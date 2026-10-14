#!/usr/bin/env python3
"""
Cross-Platform Installer for Antigravity CLI (agy) Statusline
Supports: Windows, Linux, macOS

Usage:
  python install.py              # Install or update statusline
  python install.py --uninstall  # Remove custom statusline config
"""

import sys
import os
import shutil
import json
import subprocess
from pathlib import Path

# Ensure UTF-8 on Windows terminal output without charmap crashes
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def get_agy_dir():
    home = Path.home()
    agy_dir = home / ".gemini" / "antigravity-cli"
    return agy_dir


def install():
    print("=" * 60)
    print("🚀 Installing Antigravity CLI Statusline")
    print("=" * 60)

    repo_dir = Path(__file__).resolve().parent
    src_script = repo_dir / "statusline.py"
    sample_payload = repo_dir / "sample_payload.json"

    if not src_script.exists():
        print(f"❌ Error: Cannot find {src_script}")
        sys.exit(1)

    agy_dir = get_agy_dir()
    agy_dir.mkdir(parents=True, exist_ok=True)

    dest_script = agy_dir / "statusline.py"

    # 1. Copy statusline.py
    print(f"📦 Copying statusline.py to:\n   {dest_script}")
    shutil.copy2(src_script, dest_script)

    # Make executable on Unix
    if os.name != "nt":
        try:
            dest_script.chmod(dest_script.stat().st_mode | 0o755)
        except Exception:
            pass

    # 2. Determine execution command
    dest_path_str = dest_script.as_posix()
    if os.name == "nt":
        cmd_str = f"python {dest_path_str}"
    else:
        cmd_str = f"python3 {dest_path_str}"

    # 3. Update settings.json
    settings_file = agy_dir / "settings.json"
    settings = {}
    if settings_file.exists():
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
            # Create backup
            backup_file = agy_dir / "settings.json.bak"
            shutil.copy2(settings_file, backup_file)
            print(f"💾 Backed up settings.json to settings.json.bak")
        except Exception as e:
            print(f"⚠️ Warning reading settings.json ({e}), creating fresh configuration.")
            settings = {}

    settings["statusLine"] = {
        "type": "command",
        "command": cmd_str
    }

    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    print(f"✅ Updated configuration in {settings_file}")
    print(f"   Command: \"{cmd_str}\"")

    # 4. Self-test
    print("\n🔍 Running verification self-test...")
    try:
        if sample_payload.exists():
            with open(sample_payload, "rb") as f:
                test_input = f.read()
        else:
            test_input = b'{"agent_state": "ready", "model": {"display_name": "Gemini 2.5 Flash"}}'

        res = subprocess.run(
            [sys.executable, str(dest_script)],
            input=test_input,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        rendered_output = res.stdout.decode("utf-8", errors="replace").strip()
        print("\n--- Preview Result ---")
        print(rendered_output)
        print("----------------------\n")
        print("🎉 Installation successful! Restart your Antigravity CLI session or run /statusline on")
    except Exception as e:
        print(f"⚠️ Self-test encountered an issue: {e}")
        print("   Installation files were written, please check your Python path.")


def uninstall():
    print("=" * 60)
    print("🗑️  Uninstalling Antigravity CLI Statusline")
    print("=" * 60)

    agy_dir = get_agy_dir()
    settings_file = agy_dir / "settings.json"

    if settings_file.exists():
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)
            if "statusLine" in settings:
                del settings["statusLine"]
                with open(settings_file, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                print("✅ Removed 'statusLine' configuration from settings.json")
            else:
                print("ℹ️ No 'statusLine' entry found in settings.json")
        except Exception as e:
            print(f"❌ Failed to update settings.json: {e}")

    dest_script = agy_dir / "statusline.py"
    if dest_script.exists():
        try:
            dest_script.unlink()
            print(f"✅ Removed {dest_script}")
        except Exception as e:
            print(f"⚠️ Could not delete script file: {e}")

    print("🎉 Uninstallation complete.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--uninstall", "-u", "uninstall"):
        uninstall()
    else:
        install()
