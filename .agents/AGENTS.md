# Workspace Rules for Antigravity IDE

## Execution & Command Acceptance Policy
- **Auto-Accept Non-Destructive Commands**: Automatically approve and execute all read-only, inspection, testing, compilation, python execution, file manipulation, and non-destructive terminal operations (`python3`, `pytest`, `unittest`, `ls`, `cp`, `mkdir`, `cat`, `grep`, `git status`, `git diff`, `git add`, `git commit`).
- **Destructive Operation Protection**: Require explicit user confirmation before any destructive system commands (`rm -rf /`, dropping databases, formatting disks, or modifying global system root files).
