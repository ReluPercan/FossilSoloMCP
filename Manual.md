[🇬🇧 English Version](Manual.md) | [🇷🇴 Versiunea în limba română](doc/MANUAL_UTILIZARE.md)

---

⚠️ **Note:**  
✨ **100% AI‑powered project 🪄** — concept, analysis, code, testing, documentation — with the **human** 👨‍💻 in the loop as the **big boss** 👨‍💼 for **control**, **fine‑tuning**, and **decisions** 🤔😉🤫.  

---

# User Manual & Technical Reference: Fossil SCM MCP (FossilSoloMCP)

Professional-grade Model Context Protocol (MCP) server for comprehensive integration of the **Fossil SCM** version control system with AI assistants and modern development environments.

---

## 1. Introduction & Project Philosophy

### What is Fossil SCM?
[Fossil](https://fossil-scm.org/) is a distributed version control system created by D. Richard Hipp (author of the SQLite database engine). Unlike other systems (such as Git), Fossil includes natively within a single compact and self-contained executable:
* **File tree version control** (Version Control).
* **Integrated bug and task tracking** (Bug & Task Ticketing).
* **Distributed project encyclopedia** (Built-in Wiki system).
* **Full-featured graphical web interface** (`fossil ui` / `fossil server`), instantly accessible from any browser.
* **Single-file storage format:** The entire repository, complete commit history, tickets, and wiki articles are stored physically inside a single SQLite database file (`.fossil`).

### Why Fossil for Solo Human + AI Development?
In modern development workflows where a developer collaborates closely with AI assistants (such as agents in Google Antigravity, Claude Desktop, Cursor, Continue, etc.), Fossil provides decisive advantages:
1. **Zero External Infrastructure Dependencies:** No need for cloud accounts, third-party API keys, external tokens, or database servers. Everything is 100% local, private, and autonomous on your machine.
2. **Native Persistent Memory for AI:** The Wiki and Ticketing systems embedded directly inside the repository database allow the AI agent to read and record project status, architectural decisions, and bug history without polluting the source code directory.
3. **Atomic Transactional Integrity:** Powered by the SQLite engine, all operations are atomic, consistent, and resilient against accidental power failures or process crashes.

### Ideal for Small Teams (Without Git's Complexity)
While optimized for solo AI-assisted development, Fossil is also an outstanding choice for **small teams (2–10 collaborators)** seeking simplicity, clarity, and the elimination of Git's frequently overwhelming bureaucracy:
1. **Complete "All-in-One" Solution:** In a small team, configuring and maintaining separate services such as GitHub/GitLab, Jira/Trello (task tracking), Confluence/Notion (wiki documentation), or forum servers consumes unnecessary time and resources. Fossil bundles all these tools natively, organically tied to each commit and stored in the same SQLite repository.
2. **Elimination of Git's Complex "Ceremonies":** Concepts like *detached HEAD*, a separate staging index, confusing interactive *rebase* conflicts, hazardous *force push* operations, or lost orphaned commits are either absent or radically simplified in Fossil. Fossil's history is designed to be traceable, clean, and free of surprises.
3. **Native Autosync Mechanism:** Fossil features `autosync` enabled by default. On every `commit` or `update`, the repository automatically synchronizes with the central repository if configured, eliminating the repetitive routine of `git fetch -> git stash -> git rebase -> git stash pop -> git push`.
4. **Zero-Configuration Built-in Web Server:** Any team member can instantly launch `fossil server` on a local network machine or a modest VPS. The entire team instantly benefits from a full, secure web interface (with users, role-based permissions, code review, ticketing, and wiki pages) without needing Nginx, Docker, or external databases.

### The Role of the FossilSoloMCP Server
This MCP server acts as a high-speed communication bridge between Large Language Models (LLMs) and Fossil repositories, exposing **31 specialized tools** via the standardized Model Context Protocol (MCP).

---

## 2. History, Origin, and Comparison with `agent-vc-mcp`

### The Starting Point: `agent-vc-mcp`
The development of this server originally began with exploring the open-source project [agent-vc-mcp](https://github.com/ManbotHQ/agent-vc-mcp) (created by ManBotHQ on GitHub), an early attempt to provide an MCP server for Fossil written in **TypeScript / Node.js**.

While the concept of giving AI assistants control over a version control system was sound, source code analysis revealed severe architectural limitations:

### Major Limitations of `agent-vc-mcp`:
1. **Rigid, Enforced Sandbox Model:**
   - `agent-vc-mcp` forced a single fixed workspace at `~/.agent-vc/workspace/` and a single database at `~/.agent-vc/version_control.fossil`.
   - Projects were forcibly treated as mere subfolders (`workspace/project-1/`, `workspace/project-2/`) inside the same massive repository. There was no ability to manage independent repositories for actual projects already residing across the disk.
2. **Redundant Duplication of Filesystem Operations:**
   - `agent-vc-mcp` intermingled version control with basic filesystem operations (`write_file`, `read_file`, `list_files`). These were redundant and frequently conflicted with native, advanced file tools already provided by IDEs and AI assistants.
3. **Severely Limited Toolset (Exactly 10 Tools):**
   - It only offered rudimentary capabilities: `vc_init_project`, `vc_commit`, `vc_status`, `vc_diff`, 3 file tools, and a simplistic task module (`task_create`, `task_update`, `task_list`).
   - **Critical Omissions:** No branch support (`branch`), no tags (`tag`), no `stash`, no granular per-file history inspection (`finfo`), no historical content extraction (`cat`), no safe undo (`undo`, `revert`), no repository configuration (`settings`), and zero support for the **Wiki** system!
4. **Instability and Frequent Freezes on Windows:**
   - Process spawning used `spawn` without timeouts and without closing/redirecting standard input (`stdin`). Whenever `fossil.exe` requested interactive confirmation (e.g., for new binary files or CRLF line ending warnings), the process froze indefinitely (hung).
   - The command setting `crlf-glob *` failed due to wildcard expansion by the Windows runtime.
5. **Lack of Dynamic CWD Flexibility:**
   - The workspace path was determined statically at server startup (via the `AGENT_VC_WORKSPACE` environment variable). No tool accepted a path parameter, preventing the server from dynamically managing multiple projects.
6. **Node.js / TypeScript Ecosystem Overhead:**
   - It required Node.js, `npx`, and bulky `node_modules` packages, complicating integration in environments built around Python and modern AI automation.

---

### Transition to `FossilSoloMCP`: Redesign and Rewrite

The strategic decision was made to rewrite the server entirely from scratch in **Python**, utilizing the high-performance **FastMCP** framework.

| Feature / Aspect | `agent-vc-mcp` (Original) | `FossilSoloMCP` (Current Project) |
| :--- | :--- | :--- |
| **Language & Runtime** | TypeScript / Node.js (`npx`) | **Python 3.14+ (FastMCP)** managed ultrarapidly via `uv` |
| **Number of Tools Exposed** | Exactly 10 tools | **31 complete, specialized tools** |
| **Directory Management (CWD)** | Static, fixed at startup via env vars | **Dynamic per call (`cwd`)** across all 31 tools |
| **Repository Organization** | Single shared repo in `~/.agent-vc/` | **Independent repositories**, cleanly stored in `.fossil_repositories/` |
| **File Operations** | Forced rigid wrappers (`write_file`, etc.) | **Completely decoupled:** relies on agent's native file tools |
| **Advanced History Inspection** | None (only global `vc_diff`) | **`fossil_timeline` (with filters), `fossil_finfo`, historical `fossil_cat`** |
| **Branches & Tags** | Non-existent | **Full support (`fossil_branch`, `fossil_tag`)** |
| **Stashing & Revert** | Non-existent | **Full management (`fossil_stash`, `fossil_revert`, `fossil_undo`)** |
| **Wiki System (AI Memory)** | Non-existent | **Fully integrated (`fossil_wiki_ls`, `wiki_read`, `wiki_write`)** |
| **Ticketing System** | Simplistic proprietary module | **Natively integrated Fossil ticketing with smart SQL fallback** |
| **Windows Resilience & Anti-Hang** | Frequent console hangs/freezes | **`stdin=DEVNULL`, auto-response `a` on prompts, 30s timeout** |
| **CRLF / LF Line Endings** | Errors on setting command | **Direct SQLite SQL injection + auto-generated `.editorconfig`** |

---

## 3. Prerequisites and Installation

### 1. System Prerequisites
1. **Fossil SCM CLI Utility:**
   - Download the official precompiled binary for your operating system (Windows, Linux, or macOS) from [https://fossil-scm.org/](https://fossil-scm.org/).
   - Place the executable in a directory on your machine (e.g., `C:\Program Files\Fossil\` on Windows or `/usr/local/bin/` on Linux/macOS).
   - Ensure the directory is added to your system's `PATH` environment variable.
   - Verify availability in your terminal:
     ```bash
     fossil version
     ```
2. **Python & `uv`:**
   - **Python 3.14 or newer** is recommended.
   - The modern Python package and project manager `uv` installed on your system (or standard Python).

---

### 2. Configuration in MCP Clients

Configuration is performed by adding the server definition to your MCP client's configuration file (`mcp_config.json`, `claude_desktop_config.json`, etc.).

#### Universal Configuration for Windows:
```json
{
  "mcpServers": {
    "fossil-scm": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:/Path/To/FossilSoloMCP",
        "fossil-scm-mcp"
      ]
    }
  }
}
```

#### Universal Configuration for Linux / macOS:
```json
{
  "mcpServers": {
    "fossil-scm": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/user/projects/FossilSoloMCP",
        "fossil-scm-mcp"
      ]
    }
  }
}
```

> [!TIP]
> **Path Replacement:** Replace `"C:/Path/To/FossilSoloMCP"` or `"/home/user/projects/FossilSoloMCP"` with the actual absolute path where this repository is located on your machine.
> 
> **Regarding the `--repository` Argument:** The server operates fully dynamically based on the `cwd` parameter passed to each tool call. Therefore, specifying a static fallback repository at startup is optional.

---

## 4. Repository Architecture and Organization

### The `.fossil_repositories` Convention
To keep project root directories tidy and prevent large database files from cluttering the working tree, the server automatically enforces a clean convention:

1. **Repository Database (`.fossil`):**
   - Saved in a hidden directory `.fossil_repositories/` automatically created in the parent folder of the workspace (e.g., `../.fossil_repositories/ProjectName.fossil`).
2. **Working Directory (Checkout):**
   - Contains source code, documentation, and Fossil's hidden checkout tracking file named `_FOSSIL_` (on Windows) or `.fslckout` (on Linux/macOS).
   - This file links the working directory to its associated SQLite repository database.

### Opening the Graphical Web Interface
Fossil natively bundles an HTTP server and a rich web interface. To visually explore the repository in your browser, simply execute in your terminal inside the project directory:
```bash
fossil ui
```
*(Optionally, on Windows, you can launch the convenience script `open-ui-fossil.bat` included in the root directory).*

The command automatically opens your default browser at `http://localhost:8080`, providing instant visual access to:
- **Timeline:** Interactive graphical DAG tree of all branches, tags, and commits.
- **Files:** Historical file browser at any revision, with visual diffs and annotation (blame).
- **Tickets:** Viewing, searching, and editing bug reports and tasks.
- **Wiki:** Rich navigation and authoring of project articles and documentation.

---

## 5. AI Agent Workflow Guide (Recommended Universal Flows)

> [!IMPORTANT]
> **Golden Rule for Agents:**
> When calling any tool in the `fossil-scm` server, **always** provide the `cwd` parameter explicitly set to the absolute path of the directory you are operating on (e.g., `cwd="C:/Projects/MyApp"`).

---

### Recommended AI Agent Rule (System Prompt / Custom Instructions)
To enable your AI assistant to automatically and correctly utilize the Fossil MCP server across any client (Claude Desktop, Cursor, Antigravity, etc.), add the following instruction to your system prompt:

```text
For version control, issue ticketing, and persistent documentation, use the fossil-scm MCP tools.
On every call, always pass the 'cwd' parameter set to the current project's absolute working directory.
Before making changes, verify status with fossil_status. Upon completing any task,
stage files with fossil_add and commit the changes with fossil_commit using a clear message.
```

---

### Flow 1: Initializing a New Project
When a user requests creating a new project with Fossil version control:
1. The agent calls `fossil_init`:
   ```json
   {
     "project_name": "MyApp",
     "cwd": "C:/Projects/MyApp"
   }
   ```
   *What the server does automatically:*
   - Creates the `.fossil_repositories/` directory in the parent folder if not present.
   - Initializes `MyApp.fossil`.
   - Opens the repository in the working directory (`fossil open`).
   - Applies anti-CRLF settings directly into SQLite SQL (`crlf-glob = *`).
   - Automatically generates `.editorconfig` (`end_of_line = lf`) and tracks it in version control.

---

### Flow 2: Standard Edit and Commit Cycle
During development or debugging, the agent follows a standard cycle:
1. **Check file status:**
   `fossil_status(cwd="...")`
2. **Inspect exact modifications (diff):**
   `fossil_diff(cwd="...")`
3. **Stage new files:**
   - Specific files: `fossil_add(files=["src/main.py"], cwd="...")`
   - Automatic sync (new files and deletions): `fossil_addremove(cwd="...")`
4. **Commit to the repository:**
   `fossil_commit(message="Implement authentication module", cwd="...")`
   *(The server resolves any interactive prompts automatically without hanging).*

---

### Flow 3: Risk-Free Historical Exploration & Investigation
Unlike other VCS setups where an agent risks overwriting the active workspace when inspecting past code:
- **`fossil_timeline`:** Displays the chronological event history. Supports filtering by specific file (`path="src/main.py"`).
- **`fossil_finfo`:** Displays the complete historical evolution of a single specified file.
- **`fossil_cat` (The Secret Weapon):** Reads the exact content of any file directly from a historical revision, branch, or tag **without touching or modifying local files in the active working directory**:
  ```json
  {
    "file": "src/main.py",
    "revision": "f731ad3851",
    "cwd": "..."
  }
  ```

---

### Flow 4: Task & Bug Tracking (Ticketing)
Fossil provides a full ticketing system stored directly in the repository database:
1. **List existing tickets:**
   `fossil_ticket_list(cwd="...")`
2. **Create a new task / bug report:**
   ```json
   {
     "title": "Fix async timeout issue during remote calls",
     "status": "open",
     "additional_fields": {
       "type": "Code_Defect",
       "severity": "High"
     },
     "cwd": "..."
   }
   ```
3. **Close or update an existing ticket:**
   ```json
   {
     "ticket_id": "a1b2c3d4",
     "field_name": "status",
     "field_value": "closed",
     "cwd": "..."
   }
   ```

---

### Flow 5: Documentation as Persistent AI Memory (Wiki)
Fossil Wiki pages are stored directly in the repository and do not depend on loose disk files:
1. **List existing wiki pages:**
   `fossil_wiki_ls(cwd="...")`
2. **Read documentation:**
   `fossil_wiki_read(page_name="SystemArchitecture", cwd="...")`
3. **Store architectural decisions for future sessions:**
   `fossil_wiki_write(page_name="DesignDecisions", content="# Architecture...", cwd="...")`

---

## 6. Complete Reference of the 31 MCP Tools

### A. Version Control (20 Tools)

#### 1. `fossil_status`
- **Description:** Displays current workspace file status (modified, added, missing, untracked files).
- **Parameters:**
  - `cwd` *(string, optional)*: Working directory path.
  - `dotfiles` *(boolean, default: false)*: Whether to include hidden files/folders (starting with dot).
  - `brief` *(boolean, default: false)*: Brief output showing only status keywords.
  - `ignore` *(string, optional)*: Comma-separated glob patterns of files to ignore.

#### 2. `fossil_diff`
- **Description:** Shows code diffs between workspace changes and repository, or between historical revisions.
- **Parameters:**
  - `cwd` *(string, optional)*: Working directory path.
  - `files` *(array of strings, optional)*: Specific list of files to compare.
  - `from_version` *(string, optional)*: Starting revision (`--from`).
  - `to_version` *(string, optional)*: Destination revision (`--to`).
  - `branch` *(string, optional)*: Compares changes on specified branch.
  - `brief` *(boolean, default: false)*: Lists only modified filenames without full diff.
  - `ignore_whitespace` *(boolean, default: false)*: Ignores whitespace changes (`-w`).

#### 3. `fossil_cat`
- **Description:** Extracts and returns textual content of a file from a specified historical revision without altering the local workspace.
- **Parameters:**
  - `file` *(string, required)*: Relative file path.
  - `revision` *(string, required)*: Commit hash, tag, or branch name.
  - `cwd` *(string, optional)*: Working directory path.

#### 4. `fossil_finfo`
- **Description:** Returns detailed modification history for a single specified file. Transparently follows rename events performed with `fossil_mv`.
- **Parameters:**
  - `file` *(string, required)*: File path.
  - `limit` *(integer, optional)*: Maximum number of revisions to display (`-n`).
  - `cwd` *(string, optional)*: Working directory path.

#### 5. `fossil_add`
- **Description:** Schedules addition of one or more files/directories into version control.
- **Parameters:**
  - `files` *(array of strings, required)*: List of file or directory paths.
  - `force` *(boolean, default: true)*: Forces addition even if matching `ignore-glob` patterns.
  - `dotfiles` *(boolean, default: false)*: Includes hidden files in recursive scan.
  - `cwd` *(string, optional)*: Working directory path.

#### 6. `fossil_rm`
- **Description:** Removes files from version control.
- **Parameters:**
  - `files` *(array of strings, required)*: List of files to remove.
  - `force` *(boolean, default: false)*: Forces deletion without warnings.
  - `keep` *(boolean, default: false)*: Retains files physically on disk, removing them only from VCS.
  - `cwd` *(string, optional)*: Working directory path.

#### 7. `fossil_mv`
- **Description:** Renames or moves a file or directory in both repository and disk. Explicitly records the `RENAME` event in the version DAG, ensuring unbroken history tracking via `fossil_finfo`.
- **Parameters:**
  - `old_name` *(string, required)*: Source file or directory path.
  - `new_name` *(string, required)*: Destination file or directory path.
  - `hard` *(boolean, default: true)*: Physically moves/renames the file on disk (`--hard`). If False, only records rename intention in manifest (`--soft`).
  - `case_sensitive` *(boolean, optional)*: Enforces case sensitivity (`--case-sensitive 1/0`).
  - `cwd` *(string, optional)*: Working directory path.

#### 8. `fossil_addremove`
- **Description:** Scans workspace and automatically adds newly created files while removing files deleted from disk.
- **Parameters:**
  - `dotfiles` *(boolean, default: false)*: Includes dotfiles.
  - `ignore` *(string, optional)*: Glob patterns to ignore.
  - `clean` *(boolean, default: false)*: Deletes untracked extra files.
  - `reset` *(boolean, default: false)*: Resets add/remove state.
  - `cwd` *(string, optional)*: Working directory path.

#### 9. `fossil_extras`
- **Description:** Lists all files in the current working directory that are not tracked under version control.
- **Parameters:**
  - `dotfiles` *(boolean, default: false)*: Includes hidden files.
  - `ignore` *(string, optional)*: Additional glob filter.
  - `cwd` *(string, optional)*: Working directory path.

#### 10. `fossil_clean`
- **Description:** Cleans untracked and temporary files from the working tree (`fossil clean`).
- **Parameters:**
  - `all_files` *(boolean, default: false)*: Forces removal without interactive prompts (`-f`).
  - `dry_run` *(boolean, default: false)*: Simulation mode; lists files that would be removed without deleting (`-n`).
  - `cwd` *(string, optional)*: Working directory path.

#### 11. `fossil_revert`
- **Description:** Reverts uncommitted modifications in specified files back to their repository state.
- **Parameters:**
  - `files` *(array of strings, required)*: Files to revert.
  - `revision` *(string, optional)*: Revision to revert to (defaults to current checkout).
  - `cwd` *(string, optional)*: Working directory path.

#### 12. `fossil_stash`
- **Description:** Temporarily saves uncommitted local changes to clear the workspace, allowing subsequent reapplication.
- **Parameters:**
  - `action` *(string, default: "save")*: Stash action: `"save"`, `"snapshot"`, `"list"`, `"pop"`, `"apply"`, `"drop"`, `"diff"`.
  - `comment` *(string, optional)*: Comment describing the stash.
  - `stash_id` *(integer, optional)*: Identification number of the stash.
  - `cwd` *(string, optional)*: Working directory path.

#### 13. `fossil_tag`
- **Description:** Manages symbolic tags attached to specific check-ins.
- **Parameters:**
  - `action` *(string, default: "list")*: `"add"`, `"cancel"`, `"list"`.
  - `tag_name` *(string, optional)*: Tag name (e.g., `"v1.0.0"`).
  - `checkin` *(string, optional)*: Revision check-in to tag.
  - `cwd` *(string, optional)*: Working directory path.

#### 14. `fossil_commit`
- **Description:** Permanently commits staged changes as a new check-in in the repository.
- **Parameters:**
  - `message` *(string, required)*: Commit message.
  - `files` *(array of strings, optional)*: Specific files to commit.
  - `branch` *(string, optional)*: New branch name to place the commit on (`--branch`).
  - `no_warnings` *(boolean, default: true)*: Suppresses CRLF and binary warnings.
  - `allow_empty` *(boolean, default: false)*: Allows commit even if there are no changes.
  - `user_override` *(string, optional)*: Overrides author username.
  - `cwd` *(string, optional)*: Working directory path.

#### 15. `fossil_timeline`
- **Description:** Displays chronological history of check-ins, wiki edits, and project activity.
- **Parameters:**
  - `limit` *(integer, default: 20)*: Maximum number of events to show.
  - `path` *(string, optional)*: Filters timeline to a specific file or folder (`-p`).
  - `type_filter` *(string, optional)*: Type filter: `"ci"` (checkins), `"w"` (wiki), `"t"` (tickets), `"e"` (events) (`-t`).
  - `cwd` *(string, optional)*: Working directory path.

#### 16. `fossil_info`
- **Description:** Shows detailed information about the repository, current checkout, or a specific revision.
- **Parameters:**
  - `target` *(string, optional)*: Revision hash, tag, or filename to inspect.
  - `cwd` *(string, optional)*: Working directory path.

#### 17. `fossil_branch`
- **Description:** Manages parallel development branches.
- **Parameters:**
  - `action` *(string, default: "list")*: `"list"` or `"new"`.
  - `branch_name` *(string, optional)*: Name of the new branch when `action="new"`.
  - `basis` *(string, optional)*: Basis check-in point.
  - `cwd` *(string, optional)*: Working directory path.

#### 18. `fossil_merge`
- **Description:** Merges another branch or specific check-in into the current workspace (`fossil merge`).
- **Parameters:**
  - `branch_or_version` *(string, required)*: Branch name or check-in hash to merge.
  - `integrate` *(boolean, default: false)*: If True (`--integrate`), automatically closes the source branch upon subsequent commit.
  - `dry_run` *(boolean, default: false)*: Simulates merge without altering local files (`-n`).
  - `cwd` *(string, optional)*: Working directory path.

#### 19. `fossil_update`
- **Description:** Updates workspace files to the latest revision or switches checkout to another branch/version.
- **Parameters:**
  - `target` *(string, optional)*: Version, branch, or tag to switch to.
  - `cwd` *(string, optional)*: Working directory path.

#### 20. `fossil_undo`
- **Description:** Reverses the last `update`, `revert`, or `merge` operation executed in the workspace.
- **Parameters:**
  - `dry_run` *(boolean, default: false)*: Shows what would be reversed without performing action.
  - `cwd` *(string, optional)*: Working directory path.

---

### B. Repository Administration & Setup (5 Tools)

#### 21. `fossil_init`
- **Description:** Creates and initializes a new Fossil repository database and automatically opens it in the specified directory.
- **Parameters:**
  - `db_name` *(string, optional)*: Repository database filename (defaults to current folder name).
  - `project_name` *(string, optional)*: Logical project name.
  - `cwd` *(string, optional)*: Working directory path.

#### 22. `fossil_open`
- **Description:** Opens an existing Fossil repository database in the specified directory.
- **Parameters:**
  - `db_name` *(string, required)*: Repository `.fossil` filename or path.
  - `force` *(boolean, default: false)*: Forces open even if directory is non-empty (`-f`).
  - `keep` *(boolean, default: false)*: Preserves existing local files (`-k`).
  - `workdir` *(string, optional)*: Target directory where the checkout should be opened (defaults to repository parent folder).
  - `cwd` *(string, optional)*: Working directory path.

#### 23. `fossil_close`
- **Description:** Closes the active Fossil checkout in the specified directory, disconnecting the working tree from the repository database.
- **Parameters:**
  - `force` *(boolean, default: false)*: Forces closure even if uncommitted changes exist (`-f`).
  - `cwd` *(string, optional)*: Working directory path.

#### 24. `fossil_clone`
- **Description:** Clones a Fossil repository from a remote URL (HTTP/HTTPS/SSH) or a local file path into a target `.fossil` database file without opening a working directory.
- **Parameters:**
  - `url_or_path` *(string, required)*: Remote URL (HTTP/HTTPS/SSH) or local file path to clone from.
  - `repository_path` *(string, required)*: Target `.fossil` file path.
  - `cwd` *(string, optional)*: Working directory path.

#### 25. `fossil_settings`
- **Description:** Inspects or modifies repository configuration properties (`crlf-glob`, `binary-glob`, `ignore-glob`, `autosync`, etc.).
- **Parameters:**
  - `name` *(string, optional)*: Property name (if omitted, lists all settings).
  - `value` *(string, optional)*: New value to set.
  - `cwd` *(string, optional)*: Working directory path.

---

### C. Ticketing System (3 Tools)

#### 26. `fossil_ticket_list`
- **Description:** Lists existing tickets in the repository (includes automatic fallback to direct SQLite querying if standard Fossil ticket reports are not configured).
- **Parameters:**
  - `report` *(integer, default: 1)*: Standard Fossil report number.
  - `cwd` *(string, optional)*: Working directory path.

#### 27. `fossil_ticket_create`
- **Description:** Opens a new ticket in the repository's tracking database.
- **Parameters:**
  - `title` *(string, required)*: Title or summary of the task/defect.
  - `status` *(string, default: "open")*: Initial status (`"open"`, `"in_progress"`, `"closed"`, etc.).
  - `additional_fields` *(JSON dictionary/object, optional)*: Additional fields (e.g., `type`, `severity`, `subsystem`, `description`).
  - `cwd` *(string, optional)*: Working directory path.

#### 28. `fossil_ticket_update`
- **Description:** Modifies a field or status of an existing ticket.
- **Parameters:**
  - `ticket_id` *(string, required)*: Ticket UUID identifier (or prefix).
  - `field_name` *(string, required)*: Field name to update (e.g., `"status"`, `"comment"`).
  - `field_value` *(string, required)*: New value assigned to field.
  - `cwd` *(string, optional)*: Working directory path.

---

### D. Wiki System (3 Tools)

#### 29. `fossil_wiki_ls`
- **Description:** Returns a list of all wiki pages present in the repository.
- **Parameters:**
  - `cwd` *(string, optional)*: Working directory path.

#### 30. `fossil_wiki_read`
- **Description:** Reads and returns complete text/markdown content of requested wiki page.
- **Parameters:**
  - `page_name` *(string, required)*: Wiki page name.
  - `cwd` *(string, optional)*: Working directory path.

#### 31. `fossil_wiki_write`
- **Description:** Creates a new wiki page or updates content of an existing wiki page in the repository.
- **Parameters:**
  - `page_name` *(string, required)*: Wiki page name.
  - `content` *(string, required)*: Markdown or text content.
  - `cwd` *(string, optional)*: Working directory path.

---

## 7. Windows Specifics & Built-in Technical Solutions

Running tools ported from UNIX on Windows presents specific challenges. `FossilSoloMCP` incorporates dedicated resilience measures:

### 1. Wildcard Expansion Issue with `crlf-glob "*"`
- **The Problem:** On Windows, the MSVC/MinGW runtime of `fossil.exe` automatically expands `*` wildcards before entering `main()`. A command like `fossil settings crlf-glob "*"` reached Fossil as a raw list of all filenames in the directory, causing syntax errors.
- **The Solution:** The server applies this setting directly to the repository database via native SQLite SQL:
  ```sql
  REPLACE INTO config(name,value) VALUES('crlf-glob','*')
  ```
  Bypassing the CLI entirely, this operation is 100% reliable, portable, and atomic.

### 2. Preserving the LF Standard via `.editorconfig`
- Even though `crlf-glob = *` eliminates commit errors, Windows CRLF line endings can introduce artificial diffs across commits.
- Upon `fossil_open`, the server automatically creates an `.editorconfig` file enforcing `end_of_line = lf`, ensuring code editors save clean UNIX-style line endings.

### 3. Anti-Hang Protection & Safety Timeout
- Every spawned CLI process has `stdin` redirected to `subprocess.DEVNULL` when no explicit input is provided, preventing hangs on interactive prompts.
- During `fossil_commit`, the server automatically supplies `a\n` on standard input to validate binary file and warning prompts.
- All process calls are guarded by a strict 30-second timeout, with full capture of `stderr` and exit codes for immediate diagnosis.

---

## 8. Best Practices & Operational Tips

1. **Atomic & Explicit Commits:**
   - Make frequent, focused commits after each working milestone or bug fix. Using `fossil_undo` or `fossil_revert`, you can always roll back cleanly to a verified stable state.
2. **Preserving Project History in Wiki:**
   - Use Wiki pages (`fossil_wiki_write`) to document architectural conclusions, schema designs, or deployment instructions. Stored safely inside `.fossil`, they are never lost and remain directly viewable in your browser via `fossil ui`.
3. **Advanced Optimization: Working on RAM Disk (Optional):**
   - For developers running endurance benchmarks, generating massive temporary scratch files, or running intensive AI automation scripts, using a temporary RAM Disk is an outstanding way to protect SSD write cycles and achieve maximum I/O throughput. Upon completing work sessions, validated changes can be synchronized to the permanent repository.
4. **Advanced Automations with AI Agents:**
   - Depending on your client or IDE (e.g., agent rules in Google Antigravity, `.cursorrules` in Cursor, or System Prompts in Claude Desktop), configure clear instructions so the agent automatically versions important steps without requiring repetitive manual intervention.

---

## 9. License & Disclaimer (No Warranty)

### 📄 License

This project is licensed under the terms of the **MIT** License. See the [LICENSE](LICENSE) file for complete details.

---

### 📝 Warranty

No warranty of any kind is provided!

