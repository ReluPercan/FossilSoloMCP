import os
import sys
import shutil

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, src_dir)
import fossil_scm_mcp.server as s

test_dir = r"R:\test_space"
if os.path.exists(test_dir):
    shutil.rmtree(test_dir, ignore_errors=True)
os.makedirs(test_dir, exist_ok=True)

repo_path = os.path.join(test_dir, "test.fossil")
co1_dir = os.path.join(test_dir, "checkout1")
co2_dir = os.path.join(test_dir, "checkout2")
clone_path = os.path.join(test_dir, "cloned.fossil")
os.makedirs(co1_dir, exist_ok=True)
os.makedirs(co2_dir, exist_ok=True)

print("--- TEST 1: fossil_init ---")
res_init = s.fossil_init(db_name=repo_path, project_name="TestProject", cwd=co1_dir)
print(res_init)
assert os.path.exists(repo_path), "Repository was not created"
print("PASS: fossil_init")

print("\n--- TEST 2: fossil_open (standard) ---")
res_open1 = s.fossil_open(db_name=repo_path, cwd=co1_dir)
print(res_open1)
fossil_co_file = os.path.join(co1_dir, "_FOSSIL_")
assert os.path.exists(fossil_co_file), "_FOSSIL_ missing in co1"
print("PASS: fossil_open standard")

print("\n--- TEST 3: fossil_status ---")
res_status = s.fossil_status(cwd=co1_dir)
print(res_status)
assert "checkout:" in res_status or "tags:" in res_status, "Status output unexpected"
print("PASS: fossil_status")

print("\n--- TEST 4: Commit .editorconfig then fossil_close (clean) ---")
res_commit = s.fossil_commit(message="Initial commit with editorconfig", cwd=co1_dir)
print(res_commit)

res_close1 = s.fossil_close(force=False, cwd=co1_dir)
print("Close clean result:", res_close1)
assert not os.path.exists(fossil_co_file), "_FOSSIL_ still exists after close"
print("PASS: fossil_close clean")

print("\n--- TEST 5: fossil_open with workdir ---")
res_open2 = s.fossil_open(db_name=repo_path, workdir=co2_dir, cwd=test_dir)
print(res_open2)
fossil_co2_file = os.path.join(co2_dir, "_FOSSIL_")
assert os.path.exists(fossil_co2_file), "_FOSSIL_ missing in co2"
assert os.path.exists(os.path.join(co2_dir, ".editorconfig")), ".editorconfig missing in co2"
print("PASS: fossil_open with workdir")

print("\n--- TEST 6: fossil_close with modifications and force=True ---")
# Create uncommitted modification in co2
with open(os.path.join(co2_dir, "new_file.txt"), "w") as f:
    f.write("Hello uncommitted")
s.fossil_add(files=["new_file.txt"], cwd=co2_dir)

# Trying clean close should fail
res_close_fail = s.fossil_close(force=False, cwd=co2_dir)
print("Expected close failure result:", res_close_fail)
assert "ERROR" in res_close_fail or "unsaved changes" in res_close_fail

# Force close should succeed
res_close_force = s.fossil_close(force=True, cwd=co2_dir)
print("Force close result:", res_close_force)
assert not os.path.exists(fossil_co2_file), "_FOSSIL_ still exists after force close"
print("PASS: fossil_close force")

print("\n--- TEST 7: fossil_clone ---")
res_clone = s.fossil_clone(repository_uri=repo_path, target_file=clone_path, cwd=test_dir)
print(res_clone)
assert os.path.exists(clone_path), "Cloned repository file does not exist"
print("PASS: fossil_clone")

# Cleanup test space
shutil.rmtree(test_dir, ignore_errors=True)
print("\n==========================================")
print("ALL TESTS PASSED WITH 100% SUCCESS!")
print("==========================================")
