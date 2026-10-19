# 🚀 FossilSoloMCP v1.0.1 — Feature & Maintenance Release

> **Model Context Protocol (MCP) server for Fossil SCM with 31 specialized tools for AI agents.**  
> *Server MCP robust și autonom cu 31 de unelte dedicate pentru depozitele Fossil SCM.*

Release **v1.0.1** introduces two essential repository management tools (`fossil_close` and `fossil_clone`), `--workdir` flag support in `fossil_open`, zero-install execution via `uvx`, absolute GitHub links across documentation to prevent PyPI 404 errors, and full Python 3.14 compatibility (`pywin32 >= 312`).

---

## 🌟 Key Highlights & Enhancements (31 MCP Tools)

* **New `fossil_close` Tool:** Safely closes the active checkout in the current workspace or specified `cwd`, removing the `_FOSSIL_` (or `.fslckout`) bookkeeping database. Supports `force=True` (`-f`) when local uncommitted changes exist.
* **New `fossil_clone` Tool:** Clones a repository from a remote URL (HTTP/HTTPS/SSH) or a local path directly into a target `.fossil` database file, without forcing a working directory checkout.
* **`--workdir` Support in `fossil_open`:** Allows specifying a target checkout directory directly without changing the process's working directory.
* **Zero-Install Execution via `uvx`:** AI agents and users (Claude Desktop, Cursor, Antigravity) can now run the server instantly using `uvx fossil-scm-mcp`, without needing to manually clone or manage source repositories.
* **PyPI Link Resolution:** All documentation links in package metadata now resolve to absolute GitHub URLs, eliminating 404 errors on PyPI and downstream registries.
* **Python 3.14 & Windows Compatibility:** Dependency updated to `pywin32 >= 312` ensuring seamless execution on latest Windows builds and Python 3.14 environments.

---

## 🛠️ Complete Toolset Inventory (31 Tools)

1. **Version Control (20 tools):** `fossil_status`, `fossil_diff`, `fossil_cat`, `fossil_finfo`, `fossil_revert`, `fossil_mv`, `fossil_clean`, `fossil_merge`, `fossil_stash`, `fossil_tag`, `fossil_add`, `fossil_rm`, `fossil_addremove`, `fossil_extras`, `fossil_branch`, `fossil_commit`, `fossil_timeline`, `fossil_info`, `fossil_undo`, `fossil_update`.
2. **Repository Administration (5 tools):** `fossil_init`, `fossil_open`, `fossil_close`, `fossil_clone`, `fossil_settings`.
3. **Ticketing & Bug Tracking (3 tools):** `fossil_ticket_list`, `fossil_ticket_create`, `fossil_ticket_update`.
4. **Wiki & Knowledge Base (3 tools):** `fossil_wiki_ls`, `fossil_wiki_read`, `fossil_wiki_write`.

---

## 📦 Distribution Packages & Verification

| Package File | Distribution Type | Architecture | SHA-256 Checksum |
| :--- | :--- | :--- | :--- |
| `fossil_scm_mcp-1.0.1-py3-none-any.whl` | Python Wheel | Universal (`py3-none-any`) | `5523fe73afa8b97eb7ae54be9b85c523fc8c4612485c5ef049a01bf9b94f29b8` |
| `fossil_scm_mcp-1.0.1.tar.gz` | Source Distribution (sdist) | Complete Source | `e84b9af52bb80076418fa9d918501219addf560de8634426bad90669b177ac2c` |

---

## 📄 License

This project is licensed under the **MIT License**. For complete details, see [LICENSE](https://github.com/ReluPercan/FossilSoloMCP/blob/master/LICENSE).
