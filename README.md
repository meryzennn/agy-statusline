# ⚡ agy-statusline

> **A beautiful, lightweight, and responsive statusline for Google Antigravity CLI (`agy`).**  
> Supports **Windows**, **Linux**, and **macOS** with **zero external dependencies** (Pure Python 3 standard library).

---

## 📸 Preview

### 🖥️ Medium / Balanced View (2-Line Responsive Layout)
```text
╭─ ● READY │ ✦ Gemini 3.8 Flash (High) │  main* │ 📄2a
╰─ ctx: ▍░░░░░░░ 4.9% (55.9k/1.0M) │ 5h: █████▉░ 85% (3h 27m) │ wk: 72% (2d 2h)
```

### 📺 Wide View (Single-Line Layout on Terminals ≥ 125 cols)
```text
● READY │ ✦ Gemini 3.8 Flash (High) │ ctx: ▍░░░░░░░ 4.9% (55.9k/1.0M) │ 5h: █████▉░ 85% (3h 27m) │ wk: 72% (2d 2h) │  main*
```

---

## ✨ Features

- **Live Agent State:** Visual badges for `● READY`, `◆ THINKING`, `⚙ WORKING`, `⚡ TOOL`, `⏳ INIT`, and `⚠️ CONFIRM`.
- **Active Model & Mode:** Displays currently selected model (e.g. `Gemini 3.8 Flash (High)`, `Claude 3.7 Sonnet`, etc.).
- **Context Window Metrics:**
  - High-resolution smooth Unicode progress bar (sub-character 1/8th blocks).
  - Used percentage and readable token counts (e.g. `55.9k / 1.0M`).
  - Dynamic color shifting (Cyan ➔ Yellow ➔ Red when nearing context limits).
  - `[!>200k]` indicator when large context threshold is reached.
- **Quota & Rate Limits (5h & Weekly):**
  - Live remaining percentage for short-term 5-hour rolling quotas and weekly limits.
  - Reset countdown timers (e.g., `(3h 27m)`, `(2d 2h)`).
- **Fast Git VCS Branch:**
  - Zero subprocess overhead: inspects `.git/HEAD` directly in milliseconds.
  - Shows current branch and dirty status (`*`).
- **Responsive Layout:**
  - Automatically adapts between 1-line, 2-line, and compact views based on terminal width.
- **Zero Dependencies:**
  - Uses only Python's built-in standard library (`sys`, `json`, `os`, `datetime`).

---

## 🚀 Quick Install (1 Command)

Clone or download this repo, then run the installer:

### Windows (PowerShell or CMD)
```powershell
python install.py
```

### Linux / macOS
```bash
python3 install.py
```

The installer will:
1. Copy `statusline.py` to `~/.gemini/antigravity-cli/statusline.py`.
2. Automatically backup and update `~/.gemini/antigravity-cli/settings.json`.
3. Run a self-test with sample data to verify display rendering.

---

## 🤖 Ask an AI Agent to Install It for You

If you are chatting with an AI Agent (Antigravity CLI, Claude Code, Cursor, Roo Code, Copilot, etc.), just copy-paste this prompt:

```text
Tolong pasangkan statusline Antigravity CLI (agy) dari repo ini ke environment saya.
Repo: https://github.com/<your-username>/agy-statusline (atau folder lokal ini)
Ikuti panduan lengkap di AGENT_INSTRUCTIONS.md dan jalankan self-test untuk memverifikasi.
```

*(See [AGENT_INSTRUCTIONS.md](AGENT_INSTRUCTIONS.md) for full instructions tailored for autonomous agents).*

---

## 🛠️ Manual Installation

If you prefer doing it manually without `install.py`:

1. Copy `statusline.py` to your Antigravity config directory:
   - **Windows:** `C:\Users\<Username>\.gemini\antigravity-cli\statusline.py`
   - **Linux/macOS:** `~/.gemini/antigravity-cli/statusline.py`
2. Open `~/.gemini/antigravity-cli/settings.json` and add:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python C:/Users/<Username>/.gemini/antigravity-cli/statusline.py"
  }
}
```
*(On Linux/macOS, use `"command": "python3 ~/.gemini/antigravity-cli/statusline.py"`)*

3. Restart Antigravity CLI, or run inside the CLI:
```text
/statusline on
```

---

## ⚙️ Configuration & Customization

Open `statusline.py` and adjust the variables near the top:

```python
# Layout mode:
# - "auto"   : automatically picks 1-line or 2-line based on terminal width
# - "single" : always force single-line layout
# - "double" : always force 2-line layout
LAYOUT_MODE = "auto"

# Progress bar lengths
BAR_WIDTH_CTX = 8
BAR_WIDTH_QUOTA = 7

# Log incoming payloads to ~/.gemini/antigravity-cli/last_statusline_payload.json for debugging
DEBUG_LOG_PAYLOAD = False
```

---

## 🧪 Testing Locally

You can test how the statusline renders at any time without launching the full agent:

**PowerShell:**
```powershell
Get-Content sample_payload.json -Raw | python statusline.py
```

**Bash / Zsh:**
```bash
python3 statusline.py < sample_payload.json
```

---

## 💡 Troubleshooting

- **Glyphs or icons look garbled on Windows?**  
  Ensure you are using **Windows Terminal** with a Nerd Font installed (e.g. *JetBrainsMono Nerd Font*, *FiraCode Nerd Font*, or *CaskaydiaCove Nerd Font*).
- **Want to turn off or reset the statusline?**  
  Inside Antigravity CLI, run:
  - `/statusline off` — temporarily disable
  - `/statusline delete` — reset back to default
  - Run `python install.py --uninstall` — completely restore original `settings.json`

---

## 📄 License

MIT License. Feel free to modify and share!
