import os
import sys
import subprocess
import tempfile
from typing import List, Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP
mcp = FastMCP(
    "fossil",
    instructions="MCP server providing 31 tools for complete Fossil SCM automation and integration.",
    website_url="https://github.com/ReluPercan/FossilSoloMCP"
)

# Global fallback working directory, initialized from environment variables if present
DEFAULT_CWD: Optional[str] = os.environ.get("FOSSIL_WORKSPACE") or os.environ.get("FOSSIL_CWD")

AUTO_SETTINGS = [
    ("crlf-glob", "*"),
    ("dotfiles", "1"),
    ("ignore-glob", "deschide-ui-fossil.bat,Thumbs.db,.suo,.user,bin/,obj/,*__pycache__*,*.pyc,.venv/"),
    ("binary-glob", "*.pcsave,*.png,*.jpg,*.zip,*.exe,*.dll,*.tar.gz")
]

def run_fossil_cmd(command: list[str], extra_cwd: str = None, input_data: str = None, timeout: int = 30) -> str:
    """Helper to execute fossil commands safely with anti-hang safeguards."""
    target_cwd = extra_cwd if extra_cwd is not None else DEFAULT_CWD
    if target_cwd is None:
        target_cwd = os.getcwd()
    try:
        kwargs = {
            "cwd": target_cwd,
            "capture_output": True,
            "text": True,
            "timeout": timeout,
            "check": True,
            "encoding": "utf-8"
        }
        if input_data is not None:
            kwargs["input"] = input_data
        else:
            kwargs["stdin"] = subprocess.DEVNULL

        result = subprocess.run(["fossil"] + command, **kwargs)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return f"ERROR: Comanda Fossil a expirat (Timeout dupa {timeout}s, CWD: '{target_cwd}')."
    except subprocess.CalledProcessError as e:
        stdout_msg = (e.stdout or "").strip()
        stderr_msg = (e.stderr or "").strip()
        if stdout_msg and stderr_msg:
            details = f"STDOUT:\n{stdout_msg}\nSTDERR:\n{stderr_msg}"
        else:
            details = stderr_msg or stdout_msg or "No output returned by fossil."
        return f"ERROR: Fossil command failed (Exit Code: {e.returncode}, CWD: '{target_cwd}'):\n{details}"
    except FileNotFoundError:
        return f"ERROR: fossil.exe not found in system PATH (CWD: '{target_cwd}')."

def apply_auto_settings(db_name: Optional[str] = None, extra_cwd: Optional[str] = None) -> List[str]:
    """Applies standard auto-configurations (crlf-glob, dotfiles, ignore-glob, binary-glob) directly via SQL bypass."""
    warnings = []
    for setting_name, value in AUTO_SETTINGS:
        if db_name:
            settings_cmd = ["sql", "-R", db_name, f"REPLACE INTO config(name,value) VALUES('{setting_name}','{value}')"]
        else:
            settings_cmd = ["sql", f"REPLACE INTO config(name,value) VALUES('{setting_name}','{value}')"]
            
        res = run_fossil_cmd(settings_cmd, extra_cwd=extra_cwd)
        if "ERROR:" in res:
            warnings.append(f"Failed setting {setting_name}: {res}")
    return warnings

def resolve_repo_paths(db_name: Optional[str] = None, cwd: Optional[str] = None) -> tuple[str, str, str]:
    """Helper to automatically resolve workspace directory, repository database path, and project name.
    
    Returns:
        (workspace_dir, repo_db_path, project_name)
    """
    target_workspace = cwd if cwd is not None else DEFAULT_CWD
    if target_workspace is None:
        target_workspace = os.getcwd()
    target_workspace = os.path.abspath(target_workspace)
    project_name = os.path.basename(target_workspace)
    
    # If db_name contains path separators or is absolute, use it directly
    if db_name and ("/" in db_name or "\\" in db_name or os.path.isabs(db_name)):
        repo_db_path = os.path.abspath(db_name) if os.path.isabs(db_name) else os.path.abspath(os.path.join(target_workspace, db_name))
    else:
        # Automated resolution: place in '.fossil_repositories' directory under workspace parent
        parent_dir = os.path.dirname(target_workspace)
        repos_dir = os.path.join(parent_dir, ".fossil_repositories")
        os.makedirs(repos_dir, exist_ok=True)
        
        if db_name:
            filename = db_name if db_name.endswith(".fossil") else f"{db_name}.fossil"
        else:
            filename = f"{project_name}.fossil"
            
        repo_db_path = os.path.join(repos_dir, filename)
        
    return target_workspace, repo_db_path, project_name

# ==========================================
# 4. GRUPUL ADMINISTRARE
# ==========================================

@mcp.tool()
def fossil_init(db_name: Optional[str] = None, project_name: Optional[str] = None, cwd: Optional[str] = None) -> str:
    """Create a new Fossil repository database from scratch. Automatically places the database in the '.fossil_repositories' parent directory if no explicit path is provided.
    
    Args:
        db_name: Optional filename or path for the repository database (defaults to auto-derived '<project_name>.fossil' in parent '.fossil_repositories').
        project_name: Optional name for the project (defaults to the workspace folder name).
        cwd: Optional path to the directory where the command should be executed.
    """
    workspace_dir, repo_db_path, derived_proj_name = resolve_repo_paths(db_name, cwd)
    final_project_name = project_name or derived_proj_name
    
    cmd = ["init", repo_db_path, "--project-name", final_project_name]
    
    # 1. Rulam initializarea repository-ului
    init_res = run_fossil_cmd(cmd, extra_cwd=workspace_dir)
    if "ERROR:" in init_res:
        return init_res
        
    # 2. Configuram automat setarile recomandate (crlf-glob, dotfiles, ignore-glob, binary-glob) direct in repository prin comenzi SQL
    warnings = apply_auto_settings(db_name=repo_db_path, extra_cwd=workspace_dir)
    
    feedback = f"{init_res}\nRepository created at '{repo_db_path}' and auto-configured with standard settings (crlf-glob='*', dotfiles=1, ignore-glob, binary-glob)."
    if warnings:
        feedback += "\n\nWARNINGS:\n" + "\n".join(warnings)
        
    return feedback

@mcp.tool()
def fossil_open(
    db_name: Optional[str] = None,
    force: bool = False,
    keep: bool = False,
    workdir: Optional[str] = None,
    cwd: Optional[str] = None
) -> str:
    """Open an existing Fossil repository in the specified or current working directory. Automatically resolves database path if omitted.
    
    Args:
        db_name: Optional name or path of the database to open (defaults to auto-detecting '.fossil_repositories/<project_name>.fossil').
        force: If True, uses the -f (--force) option to override directory not empty restrictions.
        keep: If True, uses the -k (--keep) option to keep local files unchanged.
        workdir: Optional target working directory where the check-out should be created (--workdir DIR).
        cwd: Optional path to the workspace directory where the command is executed.
    """
    workspace_dir, repo_db_path, _ = resolve_repo_paths(db_name, cwd)
    
    cmd = ["open", repo_db_path]
    if force:
        cmd.append("-f")
    if keep:
        cmd.append("-k")
    if workdir:
        cmd.extend(["--workdir", workdir])
        
    # 1. Rulam deschiderea repository-ului
    open_res = run_fossil_cmd(cmd, extra_cwd=workspace_dir)
    if "ERROR:" in open_res:
        return open_res
        
    # 2. Configuram automat setarile recomandate in repository-ul proaspat deschis local
    target_checkout_dir = os.path.abspath(workdir) if workdir else workspace_dir
    warnings = apply_auto_settings(extra_cwd=target_checkout_dir)
    
    # 3. Cream si adaugam .editorconfig daca acesta nu exista deja in workspace
    editorconfig_created = False
    if os.path.isdir(target_checkout_dir):
        editorconfig_path = os.path.join(target_checkout_dir, ".editorconfig")
        if not os.path.exists(editorconfig_path):
            try:
                editorconfig_content = (
                    "[*]\n"
                    "end_of_line = lf\n"
                    "insert_final_newline = true\n"
                    "trim_trailing_whitespace = true\n"
                )
                with open(editorconfig_path, "w", encoding="utf-8") as f:
                    f.write(editorconfig_content)
                editorconfig_created = True
                
                # Adaugam .editorconfig nou creat in Fossil pentru a fi versionat
                run_fossil_cmd(["add", ".editorconfig"], extra_cwd=target_checkout_dir)
            except Exception:
                pass

    feedback = open_res
    if warnings:
        feedback += "\n\nWARNINGS:\n" + "\n".join(warnings)
    else:
        feedback += f"\nOpened repository '{repo_db_path}' with standard settings (crlf-glob='*', dotfiles=1, ignore-glob, binary-glob)."
        
    if editorconfig_created:
        feedback += "\nCreated and added '.editorconfig' to workspace (configured for LF lines)."
        
    return feedback

@mcp.tool()
def fossil_close(force: bool = False, cwd: Optional[str] = None) -> str:
    """Close the open Fossil check-out in the current or specified working directory.
    
    Args:
        force: If True, uses the -f (--force) option to close even if there are uncommitted local changes or stash.
        cwd: Optional path to the directory where the check-out is currently open.
    """
    cmd = ["close"]
    if force:
        cmd.append("-f")
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_clone(
    repository_uri: str,
    target_file: str,
    http_proxy: Optional[str] = None,
    cwd: Optional[str] = None
) -> str:
    """Clone a remote or local Fossil repository to a destination .fossil file.
    
    Args:
        repository_uri: The source repository URL (http://, https://, ssh://) or local file path.
        target_file: Path to the destination .fossil repository file to create.
        http_proxy: Optional HTTP proxy server URL to use during the clone.
        cwd: Optional working directory for command execution.
    """
    target_dir = os.path.dirname(os.path.abspath(target_file))
    if target_dir:
        os.makedirs(target_dir, exist_ok=True)
        
    cmd = ["clone", repository_uri, target_file]
    if http_proxy:
        cmd.extend(["--proxy", http_proxy])
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_settings(name: Optional[str] = None, value: Optional[str] = None, cwd: Optional[str] = None) -> str:
    """Read or change Fossil repository settings (e.g. crlf-glob, binary-glob, ignore-glob, autosync).
    
    Args:
        name: Optional name of the setting to view or configure. If omitted, lists all settings and their current values.
        value: Optional value to assign to the setting. If omitted (and name is provided), displays the current value of 'name'.
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["settings"]
    if name:
        cmd.append(name)
        if value is not None:
            cmd.append(value)
    return run_fossil_cmd(cmd, extra_cwd=cwd)


# ==========================================
# 1. GRUPUL VERSION CONTROL
# ==========================================

@mcp.tool()
def fossil_status(
    dotfiles: bool = False,
    brief: bool = False,
    ignore: Optional[str] = None,
    cwd: Optional[str] = None
) -> str:
    """Display the current status of files in the repository (modified, added, un-tracked).
    
    Args:
        dotfiles: Include files/directories beginning with a dot in untracked files list.
        brief: Show a single keyword for the status.
        ignore: Comma-separated list of glob patterns for extra files to be ignored.
        cwd: Optional path to the directory where the command should be executed.
    """
    status_cmd = ["status"]
    if brief:
        status_cmd.append("-b")
    
    extra_cmd = ["extra"]
    if dotfiles:
        extra_cmd.append("--dotfiles")
    if ignore:
        extra_cmd.extend(["--ignore", ignore])
        
    status = run_fossil_cmd(status_cmd, extra_cwd=cwd)
    extra = run_fossil_cmd(extra_cmd, extra_cwd=cwd)
    return f"--- STATUS ---\n{status}\n\n--- UNTRACKED (EXTRA) ---\n{extra}"

@mcp.tool()
def fossil_diff(
    from_version: Optional[str] = None,
    to_version: Optional[str] = None,
    files: Optional[List[str]] = None,
    branch: Optional[str] = None,
    brief: bool = False,
    ignore_whitespace: bool = False,
    cwd: Optional[str] = None
) -> str:
    """Show code differences between revisions or the current workspace.
    
    Args:
        from_version: Starting check-in or revision (--from).
        to_version: Ending check-in or revision (--to).
        files: Optional list of files to diff.
        branch: Show diff across branches (--branch).
        brief: Show only the list of changed files (--brief).
        ignore_whitespace: Ignore whitespace differences (-w).
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["diff"]
    if from_version:
        cmd.extend(["--from", from_version])
    if to_version:
        cmd.extend(["--to", to_version])
    if branch:
        cmd.extend(["--branch", branch])
    if brief:
        cmd.append("--brief")
    if ignore_whitespace:
        cmd.append("-w")
    if files:
        cmd.extend(files)
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_cat(file: str, revision: Optional[str] = None, cwd: Optional[str] = None) -> str:
    """Extract and display the contents of a file from a specified revision without modifying the workspace.
    
    Args:
        file: The file path or name to extract.
        revision: Optional check-in or revision (-r). If omitted, uses the current checkout version.
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["cat", file]
    if revision:
        cmd.extend(["-r", revision])
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_finfo(file: str, limit: int = 20, cwd: Optional[str] = None) -> str:
    """Show the revision history (file info) for a specific file.
    
    Args:
        file: The file name or path to inspect.
        limit: Number of events to show (default: 20).
        cwd: Optional path to the directory where the command should be executed.
    """
    return run_fossil_cmd(["finfo", "-n", str(limit), file], extra_cwd=cwd)

@mcp.tool()
def fossil_revert(files: Optional[List[str]] = None, revision: Optional[str] = None, cwd: Optional[str] = None) -> str:
    """Revert uncommitted local changes for specific files, or all files if omitted.
    
    Args:
        files: Optional list of specific files to revert. If omitted, reverts all modified files.
        revision: Optional revision to revert to (-r).
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["revert"]
    if revision:
        cmd.extend(["-r", revision])
    if files:
        cmd.extend(files)
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_stash(
    action: str = "ls",
    comment: Optional[str] = None,
    stash_id: Optional[str] = None,
    cwd: Optional[str] = None
) -> str:
    """Manage the local Fossil stash (temporary modifications storage).
    
    Args:
        action: Stash sub-command: 'save', 'snapshot', 'ls', 'pop', 'apply', 'drop', 'diff'.
        comment: Optional comment when saving a stash (for 'save' or 'snapshot').
        stash_id: Optional stash ID (for 'pop', 'apply', 'drop', 'diff').
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["stash", action]
    if action in ("save", "snapshot") and comment:
        cmd.extend(["-m", comment])
    elif stash_id:
        cmd.append(stash_id)
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_tag(
    action: str = "ls",
    tag_name: Optional[str] = None,
    checkin: Optional[str] = None,
    cwd: Optional[str] = None
) -> str:
    """Manage Fossil tags (symbolic labels on check-ins).
    
    Args:
        action: 'ls' (list tags), 'add' (add tag), 'cancel' (delete tag).
        tag_name: Name of the tag (required for 'add' and 'cancel').
        checkin: Check-in / commit hash or branch target (required for 'add', optional for 'cancel').
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["tag", action]
    if action == "add":
        if not tag_name or not checkin:
            return "ERROR: tag_name and checkin are required for 'add' action."
        cmd.extend([tag_name, checkin])
    elif action == "cancel":
        if not tag_name:
            return "ERROR: tag_name is required for 'cancel' action."
        cmd.append(tag_name)
        if checkin:
            cmd.append(checkin)
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_addremove(
    dotfiles: bool = False,
    ignore: Optional[str] = None,
    clean: Optional[str] = None,
    reset: bool = False,
    cwd: Optional[str] = None
) -> str:
    """Add new files to tracking and remove deleted files from disk (prepares for commit).
    
    Args:
        dotfiles: Include files/directories beginning with a dot.
        ignore: Comma-separated list of glob patterns for files to be ignored.
        clean: Comma-separated list of glob patterns for clean files to be ignored.
        reset: Reset the ADDED/DELETED state of a check-out (no other options are valid with this option except cwd).
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["addremove"]
    if reset:
        cmd.append("--reset")
    else:
        if dotfiles:
            cmd.append("--dotfiles")
        if ignore:
            cmd.extend(["--ignore", ignore])
        if clean:
            cmd.extend(["--clean", clean])
            
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_commit(
    message: str,
    files: Optional[List[str]] = None,
    branch: Optional[str] = None,
    no_warnings: bool = True,
    allow_empty: bool = False,
    user_override: Optional[str] = None,
    cwd: Optional[str] = None
) -> str:
    """Launch a commit in the repository with current local modifications.
    Automatically handles interactive prompts for new binary files by sending 'a' (all).
    
    Args:
        message: The commit message.
        files: Optional list of specific files to commit. If empty, commits all modified/added files.
        branch: Optional new branch name to place this commit on (--branch).
        no_warnings: Omit all warnings about file contents (default: True).
        allow_empty: Allow a commit with no changes (default: False).
        user_override: Record this user as the login that created the new check-in.
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["commit", "-m", message]
    if branch:
        cmd.extend(["--branch", branch])
    if no_warnings:
        cmd.append("--no-warnings")
    if allow_empty:
        cmd.append("--allow-empty")
    if user_override:
        cmd.extend(["--user-override", user_override])
    if files:
        cmd.extend(files)
    # We pass input_data="a\n" to automatically answer 'a' to 'Commit anyhow (a=all/y/N)?'
    return run_fossil_cmd(cmd, extra_cwd=cwd, input_data="a\n")

@mcp.tool()
def fossil_add(
    files: List[str],
    dotfiles: bool = False,
    force: bool = True,
    cwd: Optional[str] = None
) -> str:
    """Make arrangements to add one or more files or directories to the repository.
    
    Args:
        files: List of file or directory paths to add.
        dotfiles: Include files/directories beginning with a dot when adding recursively.
        force: Add files even if they match ignore-glob patterns without prompting (defaults to True).
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["add"]
    if dotfiles:
        cmd.append("--dotfiles")
    if force:
        cmd.append("-f")
    cmd.extend(files)
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_rm(
    files: List[str],
    force: bool = False,
    keep: bool = False,
    cwd: Optional[str] = None
) -> str:
    """Remove one or more files or directories from the repository.
    
    Args:
        files: List of file or directory paths to remove.
        force: Remove files from the check-out/disk as well (--hard).
        keep: Skip removing files from the check-out/disk (--soft).
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["rm"]
    if force:
        cmd.append("--hard")
    if keep:
        cmd.append("--soft")
    cmd.extend(files)
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_mv(
    old_name: str,
    new_name: str,
    hard: bool = True,
    case_sensitive: Optional[bool] = None,
    cwd: Optional[str] = None
) -> str:
    """Rename or move a file or directory in the Fossil repository and optionally on disk.
    
    Explicitly records the rename event (RENAME), preserving history continuity
    in the Fossil version graph (DAG).

    Args:
        old_name: Source file or directory path/name.
        new_name: Destination file or directory path/name.
        hard: If True (default), moves/renames the file physically on disk as well (--hard).
              If False, only records the rename intention in the manifest (--soft).
        case_sensitive: Override case-sensitive setting (--case-sensitive 1/0).
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["mv"]
    if hard:
        cmd.append("--hard")
    else:
        cmd.append("--soft")
        
    if case_sensitive is not None:
        cmd.extend(["--case-sensitive", "1" if case_sensitive else "0"])
        
    cmd.extend([old_name, new_name])
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_extras(
    dotfiles: bool = False,
    ignore: Optional[str] = None,
    cwd: Optional[str] = None
) -> str:
    """Print a list of all files in the source tree that are not part of the current check-out.
    
    Args:
        dotfiles: Include files/directories beginning with a dot.
        ignore: Comma-separated list of glob patterns to ignore.
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["extras"]
    if dotfiles:
        cmd.append("--dotfiles")
    if ignore:
        cmd.extend(["--ignore", ignore])
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_clean(
    all_files: bool = False,
    dry_run: bool = False,
    cwd: Optional[str] = None
) -> str:
    """Delete untracked files from the working directory.
    
    Args:
        all_files: If True (-f), forces deletion without interactive confirmation.
        dry_run: If True (-n), only displays what files would be deleted, without touching them.
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["clean"]
    if dry_run:
        cmd.append("-n")
    elif all_files:
        cmd.append("-f")
    else:
        cmd.append("--no-prompt")
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_timeline(
    limit: int = 20,
    path: Optional[str] = None,
    type_filter: Optional[str] = None,
    cwd: Optional[str] = None
) -> str:
    """Extract the history (timeline) of actions from the repository.
    
    Args:
        limit: Number of events to show (default: 20).
        path: Optional file or directory path to filter history (-p).
        type_filter: Optional filter for event types, e.g. 'ci' for check-ins, or branch name (-t).
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["timeline", "-n", str(limit)]
    if path:
        cmd.extend(["-p", path])
    if type_filter:
        cmd.extend(["-t", type_filter])
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_info(target: str = "", cwd: Optional[str] = None) -> str:
    """Provide metadata about the repository status, or a specific file/commit if 'target' is given.
    
    Args:
        target: Optional file name, commit ID, or branch to get info about.
        cwd: Optional path to the directory where the command should be executed.
    """
    if target:
        return run_fossil_cmd(["info", target], extra_cwd=cwd)
    return run_fossil_cmd(["info"], extra_cwd=cwd)

@mcp.tool()
def fossil_branch(action: str = "ls", branch_name: str = "", basis: str = "", cwd: Optional[str] = None) -> str:
    """Manage branches.
    
    Args:
        action: Can be 'ls' to list or 'new' to create.
        branch_name: Required if action is 'new'.
        basis: Optional starting point for the new branch.
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["branch", action]
    if action == "new":
        if not branch_name:
            return "ERROR: branch_name required for 'new'."
        cmd.append(branch_name)
        if basis:
            cmd.append(basis)
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_merge(
    branch_or_version: str,
    integrate: bool = False,
    dry_run: bool = False,
    cwd: Optional[str] = None
) -> str:
    """Merge another branch or check-in into the current workspace.
    
    Args:
        branch_or_version: Branch name or check-in hash to merge.
        integrate: If True (--integrate), automatically closes the source branch after merging.
        dry_run: If True (-n), simulates the merge without modifying local files.
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["merge"]
    if dry_run:
        cmd.append("-n")
    if integrate:
        cmd.append("--integrate")
    cmd.append(branch_or_version)
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_update(target: str = "", cwd: Optional[str] = None) -> str:
    """WARNING: Destructive action. Switch to the indicated version/branch, or update the current branch if target is empty. This overrides local workspace state! Ensure you have user permission.
    
    Args:
        target: The version/branch to update to.
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["update"]
    if target:
        cmd.append(target)
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_undo(dry_run: bool = False, cwd: Optional[str] = None) -> str:
    """WARNING: Destructive action. Undo the last update, revert, or merge operation in the current workspace. Ensure you have user permission.
    
    Args:
        dry_run: If True, simulates the undo by running with -n flag (does not modify files).
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["undo"]
    if dry_run:
        cmd.append("-n")
    return run_fossil_cmd(cmd, extra_cwd=cwd)

# ==========================================
# 2. GRUPUL TICKETS
# ==========================================

@mcp.tool()
def fossil_ticket_list(report: str = "1", cwd: Optional[str] = None) -> str:
    """Extract the list of tickets from the system.
    
    Args:
        report: The ticket report style or ID to show (default: "1").
        cwd: Optional path to the directory where the command should be executed.
    """
    result = run_fossil_cmd(["ticket", "show", report], extra_cwd=cwd)
    if "ERROR:" in result:
        # Fallback to SQL to get a basic list of tickets if the report format doesn't work
        sql_cmd = "SELECT substr(tkt_uuid, 1, 10) as id, title, status FROM ticket"
        sql_result = run_fossil_cmd(["sql", "-header", "-column", sql_cmd], extra_cwd=cwd)
        if "ERROR:" not in sql_result and sql_result.strip():
            return f"--- TICKET LIST (SQL Fallback) ---\n{sql_result.strip()}"
    return result

@mcp.tool()
def fossil_ticket_create(title: str, status: str = "Open", additional_fields: Optional[List[str]] = None, cwd: Optional[str] = None) -> str:
    """Create a new ticket.
    
    Args:
        title: The title of the ticket.
        status: The initial status of the ticket (default: "Open").
        additional_fields: Optional list of field-value pairs, e.g., ['subsystem', 'UI', 'type', 'Bug'].
        cwd: Optional path to the directory where the command should be executed.
    """
    cmd = ["ticket", "add", "title", title, "status", status]
    if additional_fields:
        cmd.extend(additional_fields)
    return run_fossil_cmd(cmd, extra_cwd=cwd)

@mcp.tool()
def fossil_ticket_update(ticket_id: str, field_name: str, field_value: str, cwd: Optional[str] = None) -> str:
    """Modify an attribute for an existing ticket. Example: field_name="status", field_value="Closed".
    
    Args:
        ticket_id: The ID of the ticket to update.
        field_name: The name of the field to modify.
        field_value: The new value for the field.
        cwd: Optional path to the directory where the command should be executed.
    """
    return run_fossil_cmd(["ticket", "set", ticket_id, field_name, field_value], extra_cwd=cwd)

# ==========================================
# 3. GRUPUL WIKI
# ==========================================

@mcp.tool()
def fossil_wiki_ls(cwd: Optional[str] = None) -> str:
    """Return the list of all existing wiki pages.
    
    Args:
        cwd: Optional path to the directory where the command should be executed.
    """
    return run_fossil_cmd(["wiki", "ls"], extra_cwd=cwd)

@mcp.tool()
def fossil_wiki_read(page_name: str, cwd: Optional[str] = None) -> str:
    """Read the content of a wiki page in raw markdown/wiki format.
    
    Args:
        page_name: The name of the wiki page.
        cwd: Optional path to the directory where the command should be executed.
    """
    return run_fossil_cmd(["wiki", "export", page_name], extra_cwd=cwd)

@mcp.tool()
def fossil_wiki_write(page_name: str, content: str, cwd: Optional[str] = None) -> str:
    """Create or update a wiki page with new content.
    
    Args:
        page_name: The name of the wiki page.
        content: The text content to write.
        cwd: Optional path to the directory where the command should be executed.
    """
    fd, temp_path = tempfile.mkstemp(suffix=".md", text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        # Mai intai incercam sa dam commit in cazul in care pagina exista deja
        result = run_fossil_cmd(["wiki", "commit", page_name, temp_path], extra_cwd=cwd)
        # Ne logam dupa "no such wiki page" daca fossil returneaza eroare
        if "ERROR:" in result and ("no such wiki page" in result.lower() or "not found" in result.lower() or "doesn't exist" in result.lower()):
            # Daca pagina nu exista, folosim "create" in loc de "commit"
            result = run_fossil_cmd(["wiki", "create", page_name, temp_path], extra_cwd=cwd)
        return result
    finally:
        os.remove(temp_path)

def main():
    global DEFAULT_CWD
    # Intercept --repository from sys.argv to use it as default working directory and prevent FastMCP from crashing.
    if "--repository" in sys.argv:
        idx = sys.argv.index("--repository")
        if idx + 1 < len(sys.argv):
            DEFAULT_CWD = sys.argv[idx + 1]
            sys.argv.pop(idx) # pop arg
            sys.argv.pop(idx) # pop val
        else:
            sys.argv.pop(idx)
    
    mcp.run()

if __name__ == "__main__":
    main()
