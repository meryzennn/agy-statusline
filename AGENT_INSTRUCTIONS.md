# 🤖 Agent Instructions: How to Install Antigravity CLI Statusline

This document is specifically crafted for **AI Coding Agents** (such as Google Antigravity CLI, Claude Code, Cursor, Copilot, Roo Code, Aider, etc.) that have been asked to install or configure this statusline for the user.

---

## 🎯 Goal
Install the custom Python statusline into the user's Google Antigravity CLI (`agy`) configuration directory on their machine (Windows, Linux, or macOS).

---

## 📋 Requirements
- **Python 3.7+** available on the user's system (`python` or `python3`).
- No external packages or `pip install` needed (zero external dependencies).

---

## ⚡ Option 1: Automated Agent Installation (Recommended)

Run the included automated installer script in the user's terminal/shell:

### On Windows (PowerShell or CMD)
```powershell
python install.py
```

### On Linux or macOS (Bash/Zsh)
```bash
python3 install.py
```

The script will automatically:
1. Locate the Antigravity CLI configuration directory (`~/.gemini/antigravity-cli`).
2. Copy `statusline.py` into that directory.
3. Backup `settings.json` to `settings.json.bak`.
4. Update or add the `statusLine` configuration key.
5. Perform an end-to-end self-test rendering with sample JSON.

---

## 🛠️ Option 2: Step-by-Step Manual Agent Installation

If you cannot run `install.py` or prefer to perform the steps individually:

### 1. Identify Target Path
- **Windows**: `C:\Users\<Username>\.gemini\antigravity-cli` (or `%USERPROFILE%\.gemini\antigravity-cli`)
- **Linux / macOS**: `/home/<user>/.gemini/antigravity-cli` (or `~/.gemini/antigravity-cli`)

Ensure this directory exists (create it if missing).

### 2. Copy Script
Copy `statusline.py` from this repository into the target directory:
- Destination: `<agy_dir>/statusline.py`
- On Linux/macOS, ensure execute permission: `chmod +x <agy_dir>/statusline.py`

### 3. Update `settings.json`
Open `<agy_dir>/settings.json` (create if it doesn't exist).
Merge or add the following `statusLine` block:

#### Windows Example:
```json
{
  "statusLine": {
    "type": "command",
    "command": "python C:/Users/<Username>/.gemini/antigravity-cli/statusline.py"
  }
}
```
*(Tip: Use forward slashes `/` in JSON paths on Windows to avoid backslash escaping issues)*

#### Linux / macOS Example:
```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.gemini/antigravity-cli/statusline.py"
  }
}
```

### 4. Verify Output
Test the script by piping `sample_payload.json` into the target script:

**Windows**:
```powershell
Get-Content sample_payload.json -Raw | python C:/Users/<Username>/.gemini/antigravity-cli/statusline.py
```

**Linux / macOS**:
```bash
cat sample_payload.json | python3 ~/.gemini/antigravity-cli/statusline.py
```

**Expected verification output:**
```
╭─ ● READY │ ✦ Gemini 2.5 Pro │  main* │ 📄2a
╰─ ctx: ▍░░░░░░░ 4.9% (55.9k/1.0M) │ 5h: █████▉░ 85% (3h 27m) │ wk: 72% (2d 2h)
```

### 5. Final Confirmation to User
Inform the user that the installation is complete. Tell them they can verify in an active Antigravity CLI session with:
```
/statusline on
```
or by restarting their `agy` session.
