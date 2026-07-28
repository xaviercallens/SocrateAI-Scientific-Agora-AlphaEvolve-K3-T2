#!/usr/bin/env python3
"""
CLI Launcher for Auto-Commit Mode.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.utils.auto_commit import auto_commit

if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Auto-commit mode snapshot"
    res = auto_commit(workspace_dir=PROJECT_ROOT, message=msg)
    print("=" * 60)
    print("           SOCRATEAI AUTO-COMMIT MODE ENABLED            ")
    print("=" * 60)
    print(f"  Mode:          {res.get('mode')}")
    print(f"  Status:        {res.get('status')}")
    if "snapshot_id" in res:
        print(f"  Snapshot ID:   {res['snapshot_id']}")
        print(f"  Tracked Files: {res['tracked_files']}")
        print(f"  Manifest:      {res['manifest_path']}")
    elif "commit_message" in res:
        print(f"  Commit Msg:    {res['commit_message']}")
    print("=" * 60)
