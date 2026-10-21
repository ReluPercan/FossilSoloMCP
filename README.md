[🇬🇧 English](README.md) | [🇷🇴 Versiunea în limba română](doc/citeste-ma.md)

---

⚠️ **Note:**  
✨ **100% AI‑powered project 🪄** — concept, analysis, code, testing, documentation — with the **human** 👨‍💻 in the loop as the **big boss** 👨‍💼 for **control**, **fine‑tuning**, and **decisions** 🤔😉🤫.  

---

# Fossil SCM - MCP Server

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-1.3.0+-8A2BE2.svg)](https://modelcontextprotocol.io/)
[![GitHub Release](https://img.shields.io/github/v/release/ReluPercan/FossilSoloMCP?logo=github&logoColor=white)](https://github.com/ReluPercan/FossilSoloMCP/releases)
[![PyPI](https://img.shields.io/pypi/v/fossil-scm-mcp.svg?logo=pypi&logoColor=white)](https://pypi.org/project/fossil-scm-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)
[![Fossil SCM](https://img.shields.io/badge/Fossil_SCM-Compatible-blue.svg)](https://fossil-scm.org/)

A robust Model Context Protocol (MCP) server providing comprehensive, headless programmatic access to **Fossil SCM** repositories. It exposes **31 dedicated tools** covering Version Control, Repository Administration & Settings, Bug/Task Ticketing, and Wiki management, tailored specifically for AI agents (Google Antigravity, Claude Desktop, Cursor, etc.).

## Prerequisites

> [!IMPORTANT]
> **CRITICAL:** This package does NOT install the Fossil executable itself.  
> For this MCP server to function, you MUST have the `fossil` command-line utility installed and available in your system's `PATH` environment variable.

1. Download Fossil from the official website: [https://fossil-scm.org/](https://fossil-scm.org/)
2. Extract and place the executable (`fossil.exe` on Windows, `fossil` on Linux/macOS) in a directory of your choice.
3. Add that directory to your system's `PATH`.

## Installation & Configuration

To integrate this MCP server with Claude Desktop, Google Antigravity, or other MCP-compatible clients, add the following configuration to your MCP configuration file (e.g., `claude_desktop_config.json` or `mcp_config.json`):

### Using `uv` (Recommended)

```json
{
  "mcpServers": {
    "fossil-scm": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/fossil-scm-mcp",
        "fossil-scm-mcp"
      ]
    }
  }
}
```

*Replace `/path/to/fossil-scm-mcp` with the actual path to the repository directory on your system (e.g., `C:/Tools/FossilSCM` or `/home/user/FossilSCM`).*

> [!IMPORTANT]
> **Golden Rule for AI Agents (Dynamic `cwd`):**  
> The server operates completely decoupled and dynamically. To cleanly handle multiple repositories without workspace conflicts, **always instruct your AI assistant to provide the `cwd` parameter** (the absolute path of the current project) on every tool call.  
> 
> *Recommended AI Agent Rule (System Prompt / Custom Instructions):*
> ```text
> When calling any tool in the fossil-scm MCP server, always provide the 'cwd' parameter explicitly set to the current project's absolute working directory.
> ```

> [!TIP]
> The `--repository` CLI parameter can optionally specify a static fallback working directory for calls omitting `cwd`. However, passing `cwd` dynamically on every tool call remains the recommended practice.

## Key Features & Capabilities

- **31 Specialized Tools:**
  - **Version Control (20 tools):** Workspace status (`fossil_status`), diff with revision and branch support (`fossil_diff`), historical file inspection without checkout (`fossil_cat`), per-file commit history (`fossil_finfo`), granular file restoration (`fossil_revert`), DAG-preserving file rename (`fossil_mv`), workspace cleanup (`fossil_clean`), branch merging with auto-close (`fossil_merge`), temporary stash management (`fossil_stash`), symbolic tag management (`fossil_tag`), granular add/remove (`fossil_add`, `fossil_rm`, `fossil_addremove`, `fossil_extras`), branch management (`fossil_branch`), commit with new branch creation (`fossil_commit`), timeline with path and type filters (`fossil_timeline`), and safe undo/update operations (`fossil_undo`, `fossil_update`).
  - **Ticketing & Bug Tracking (3 tools):** List (`fossil_ticket_list`), create (`fossil_ticket_create`), and update tickets (`fossil_ticket_update`) stored directly within the repository database.
  - **Wiki Documentation (3 tools):** List (`fossil_wiki_ls`), export/read (`fossil_wiki_read`), and commit/write (`fossil_wiki_write`) Markdown wiki pages.
  - **Repository Administration & Setup (5 tools):** Initialize new repositories (`fossil_init`), open repositories (`fossil_open`), close active checkouts (`fossil_close`), clone remote or local repositories (`fossil_clone`), and inspect/modify repository configurations (`fossil_settings`).
- **Headless & Anti-Hang Resilience:**
  - Automatically sets `stdin` to `DEVNULL` to instantly fail interactive CLI prompts (`y/N`) instead of hanging.
  - Built-in 30-second timeout mechanism with clean error reporting.
  - Default `--no-warnings` and automatic prompt handling on commits for binary files and CRLF/LF line endings.
  - `fossil_add` uses `force=True` by default, cleanly bypassing `ignore-glob` confirmation prompts when files are explicitly specified.
- **Centralized Repositories:** Automatically organizes repositories into a `.fossil_repositories/` directory outside the active working tree.
- **Safety First:** Destructive operations (`undo`, `update`) are explicitly labeled with warnings so AI agents ask for human confirmation before executing.

---

## 📚 Documentation

For complete architectural details, AI agent workflows, and the in-depth API reference covering all 31 tools, see the [User Manual & Technical Reference](Manual.md).

---

## 📄 License

This project is licensed under the terms of the **MIT** License. See the [LICENSE](LICENSE) file for complete details.

---

## 📝 Warranty

No warranty of any kind is provided!

