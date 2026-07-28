"""
Auto-Commit System for SocrateAI Scientific AutoEvolve K3×T².
Automatically tracks, snapshots, and commits workspace changes and output artifacts
after execution runs or file modifications.
"""

import os
import sys
import json
import time
import shutil
import hashlib
import subprocess
from typing import Dict, Any, List


def get_file_hash(filepath: str) -> str:
    """Calculates SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""


def check_git_available() -> bool:
    """Checks if git CLI tool is available in environment."""
    return shutil.which("git") is not None


def run_git_auto_commit(commit_message: str = None) -> Dict[str, Any]:
    """
    Runs git add and git commit if git is available.
    """
    if commit_message is None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"[AUTO-COMMIT] Automated workspace snapshot - {timestamp}"

    try:
        # Check status
        status_res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        if not status_res.stdout.strip():
            return {"status": "NO_CHANGES", "committed": False, "message": "No changes to commit."}

        # Git add
        subprocess.run(["git", "add", "."], check=True, capture_output=True)

        # Git commit
        commit_res = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True, check=True)
        return {
            "status": "SUCCESS",
            "committed": True,
            "commit_message": commit_message,
            "git_output": commit_res.stdout.strip(),
        }
    except Exception as e:
        return {"status": "ERROR", "committed": False, "error": str(e)}


def record_snapshot_manifest(workspace_dir: str, message: str = "Auto snapshot") -> Dict[str, Any]:
    """
    Fallback auto-commit manifest generator when git binary is not installed in PATH.
    Stores full snapshot manifests in results/auto_commit_manifest.json.
    """
    results_dir = os.path.join(workspace_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    manifest_path = os.path.join(results_dir, "auto_commit_manifest.json")

    manifest = {"snapshots": []}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {"snapshots": []}

    file_states = {}
    for root, _, files in os.walk(workspace_dir):
        if ".git" in root or "__pycache__" in root or ".pytest_cache" in root:
            continue
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, workspace_dir)
            file_states[rel_path] = {
                "hash": get_file_hash(full_path),
                "mtime": os.path.getmtime(full_path),
                "size": os.path.getsize(full_path),
            }

    snapshot_entry = {
        "snapshot_id": f"snap_{int(time.time())}",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "message": message,
        "total_tracked_files": len(file_states),
        "files": file_states,
    }

    manifest["snapshots"].append(snapshot_entry)

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return snapshot_entry


def auto_commit(workspace_dir: str = None, message: str = None) -> Dict[str, Any]:
    """
    Main auto-commit function.
    Attempts git commit first, falls back to snapshot manifest logging if git is absent.
    """
    if workspace_dir is None:
        workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    if check_git_available():
        res = run_git_auto_commit(commit_message=message)
        res["mode"] = "GIT_CLI"
        return res
    else:
        entry = record_snapshot_manifest(workspace_dir, message=message or "Auto-commit snapshot")
        return {
            "status": "SNAPSHOT_RECORDED",
            "mode": "MANIFEST_SNAPSHOT",
            "committed": True,
            "snapshot_id": entry["snapshot_id"],
            "tracked_files": entry["total_tracked_files"],
            "manifest_path": os.path.join(workspace_dir, "results", "auto_commit_manifest.json"),
        }


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    res = auto_commit(message=msg)
    print(f"[AUTO-COMMIT MODE]: {res}")
