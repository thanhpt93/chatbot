"""
Pre-commit / CI Guard: Scan and block files larger than 20MB from being committed to Git.
"""

import sys
import subprocess
from pathlib import Path

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

def check_staged_or_tracked_files():
    # Get all untracked and modified files that could be staged
    try:
        res = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            check=True
        )
        files = res.stdout.strip().splitlines()
    except Exception as e:
        print(f"[ERROR] Failed to run git ls-files: {e}")
        sys.exit(1)

    violations = []
    for rel_path in files:
        p = Path(rel_path)
        if p.is_file():
            try:
                sz = p.stat().st_size
                if sz > MAX_FILE_SIZE_BYTES:
                    violations.append((rel_path, sz))
            except Exception:
                pass

    if violations:
        print("=" * 70)
        print("GIT COMMIT REJECTED: Files exceeding 20MB detected!")
        print("=" * 70)
        for f, sz in violations:
            print(f"  BLOCKED: {f} ({sz / (1024*1024):.2f} MB / {sz:,} bytes)")
        print("\nPlease add these files to .gitignore or use Git LFS.")
        print("=" * 70)
        return False

    print(f"[OK] All {len(files)} files checked against 20MB limit: PASS (0 violations).")
    return True

if __name__ == "__main__":
    if not check_staged_or_tracked_files():
        sys.exit(1)
    sys.exit(0)
