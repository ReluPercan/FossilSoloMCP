# 🚀 FossilSoloMCP v1.0.0 — Official Release

> **Comprehensive, headless Model Context Protocol (MCP) server with 29 specialized tools for Fossil SCM.**  
> *Server MCP robust și non-interactiv cu 29 de unelte dedicate pentru depozitele Fossil SCM.*

The first official release of **FossilSoloMCP** (`v1.0.0`) brings complete programmatic access to Fossil SCM repositories for AI assistants (Google Antigravity, Claude Desktop, Cursor) and modern development environments.

---

## 🌟 Key Highlights & Features

* **29 Dedicated MCP Tools:**
  * **Version Control (20 tools):** `fossil_status`, `fossil_diff`, `fossil_cat`, `fossil_finfo`, `fossil_revert`, `fossil_mv`, `fossil_clean`, `fossil_merge`, `fossil_stash`, `fossil_tag`, `fossil_add`, `fossil_rm`, `fossil_addremove`, `fossil_extras`, `fossil_branch`, `fossil_commit`, `fossil_timeline`, `fossil_info`, `fossil_update`, `fossil_undo`.
  * **Bug & Task Ticketing (3 tools):** `fossil_ticket_list`, `fossil_ticket_create`, `fossil_ticket_update`.
  * **Wiki Knowledge Base (3 tools):** `fossil_wiki_ls`, `fossil_wiki_read`, `fossil_wiki_write`.
  * **Repository Administration (3 tools):** `fossil_init`, `fossil_open`, `fossil_settings`.
* **Headless Anti-Hang Architecture:**
  * Automatic `stdin = DEVNULL` redirection preventing CLI hang on prompts.
  * 30-second safety timeout on all process executions.
  * Automated confirmation handling (`a\n`) for binary files and line ending warnings during commits.
* **Dynamic Workspace Handling:**
  * Universal `cwd` parameter supported dynamically across all 29 tools.
* **Windows & Cross-Platform Resilience:**
  * Direct SQLite config injection bypassing Windows shell wildcard expansion (`crlf-glob = *`).
  * Auto-generation of `.editorconfig` enforcing LF standard line endings.
  * Windows convenience script (`open-ui-fossil.bat`) included in the root bundle for single-click browser UI exploration.
* **Interactive Bilingual HTML Documentation & Offline Access:**
  * Flagship interactive manual (`MANUAL.html`) featuring instant Dark/Light theme switching and Romanian / English toggle.
  * Zero broken links, self-contained and completely operable offline without external CDN dependencies.
  * Complete 1:1 English & Romanian Markdown documentation (`README.md`, `Manual.md`, `doc/citeste-ma.md`, `doc/MANUAL_UTILIZARE.md`).

---

## 📦 Distribution Packages & Verification

| File | Description | SHA-256 Checksum | Size |
| :--- | :--- | :--- | :--- |
| `fossil_scm_mcp-1.0.0-py3-none-any.whl` | Standard Python Wheel (for pip/uv) | `96A402B71B638030FC8D35B0AF2AA0DD36C6415779E44716ADA1C9230FB06025` | 11.9 KB |
| `fossil_scm_mcp-1.0.0.tar.gz` | Standard Source Distribution (sdist) | `33F13B29D94D6EA3C2AADF276CA4B07693DD6976D21372A12FCF7FC017ACC89C` | 122.5 KB |
| `FossilSoloMCP_v1.0.0.zip` | Complete Windows-friendly Bundle | `CCD9EB3BCDEC0F1BEFBFF27CD70AB084ED0825F8A410223F2801BBE7069E6F18` | 161.9 KB |

---

## 🛠️ Quick Installation

### Option 1: Run with `uv` (Recommended)
Add to your client configuration (`claude_desktop_config.json` or `mcp_config.json`):

```json
{
  "mcpServers": {
    "fossil-scm": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/FossilSoloMCP", "fossil-scm-mcp"]
    }
  }
}
```

### Option 2: Install from Wheel
```bash
pip install fossil_scm_mcp-1.0.0-py3-none-any.whl
```

### Option 3: Extract the Windows ZIP Bundle
Extract `FossilSoloMCP_v1.0.0.zip` anywhere on your system and follow `INSTALL.txt`.