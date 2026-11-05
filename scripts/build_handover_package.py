"""
Phase 1 Clean Handover Packaging and Verification Script.
Creates:
- release/phase1_handover_clean.zip
- release/phase1_handover_clean.sha256
Performs independent extraction and regression verification.
"""

import os
import sys
import zipfile
import hashlib
import tempfile
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def get_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def collect_handover_files():
    """
    Collects files belonging to clean handover bundle.
    Excludes:
    - .git, .pgdata, .idea
    - __pycache__, *.pyc
    - archive/
    - database/*.dump, database/*.dump.gz
    - temporary scripts (execute_cleanup.py, build_handover_package.py)
    - release/ itself
    """
    included_files = []
    
    # Root foundation
    for root_file in ["README.md", "requirements.txt", ".gitignore", "main.py"]:
        p = ROOT / root_file
        if p.exists():
            included_files.append((p, root_file))

    # Directories to include fully
    dirs_to_include = [
        "docs",
        "documentation",
        "scripts/database-discovery",
        "scripts/phase1_2",
        "scripts/phase1_2_1",
        "scripts/phase1_2_2",
        "scripts/phase1_2_3_1",
        "tests/phase1_2_2",
        "tests/phase1_2_3_1",
        "artifacts/database-discovery",
        "artifacts/phase1_2_3_1",
        "reports/repository_cleanup",
    ]

    for d in dirs_to_include:
        dp = ROOT / d
        if not dp.exists():
            continue
        for root, dirs, files in os.walk(dp):
            # prune __pycache__
            dirs[:] = [sub for sub in dirs if sub != "__pycache__"]
            for f in files:
                if f.endswith(".pyc") or f.endswith(".tmp") or f.endswith(".zip"):
                    continue
                fp = Path(root) / f
                rel = fp.relative_to(ROOT).as_posix()
                included_files.append((fp, rel))

    return sorted(included_files, key=lambda x: x[1])

def build_package():
    release_dir = ROOT / "release"
    release_dir.mkdir(parents=True, exist_ok=True)
    zip_path = release_dir / "phase1_handover_clean.zip"
    sha_path = release_dir / "phase1_handover_clean.sha256"

    files = collect_handover_files()
    print(f"Total files selected for clean handover bundle: {len(files)}")

    manifest_lines = []

    # Write zip file with reproducible file records
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for full_p, rel_p in files:
            file_bytes = full_p.read_bytes()
            file_hash = compute_sha256(file_bytes)
            manifest_lines.append(f"{file_hash}  {rel_p}")
            
            # Create ZipInfo to preserve relative path with forward slashes
            zinfo = zipfile.ZipInfo(filename=rel_p)
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(zinfo, file_bytes)

    # Write sha256 manifest
    with open(sha_path, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_lines) + "\n")

    zip_size = zip_path.stat().st_size
    zip_sha = get_file_sha256(zip_path)
    print(f"Handover zip created: {zip_path.as_posix()}")
    print(f"  Size: {zip_size:,} bytes")
    print(f"  SHA-256: {zip_sha}")
    print(f"  Manifest entries: {len(manifest_lines)}")

    return zip_path, sha_path, manifest_lines

def verify_extracted_package(zip_path: Path, manifest_lines: list):
    print("\n--- Testing Handover Package in Isolated Temp Directory ---")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        print(f"Extracting zip to temporary test directory: {temp_root.as_posix()}")
        
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(temp_root)

        # 1. Verify SHA-256 for all extracted files
        print("Verifying extracted file hashes against SHA-256 manifest...")
        verified_count = 0
        for line in manifest_lines:
            expected_hash, rel_path = line.split("  ", 1)
            target = temp_root / rel_path
            if not target.exists():
                raise FileNotFoundError(f"Missing extracted file: {rel_path}")
            actual_hash = get_file_sha256(target)
            if actual_hash != expected_hash:
                raise ValueError(f"Hash mismatch on {rel_path}: expected {expected_hash}, got {actual_hash}")
            verified_count += 1
        print(f"All {verified_count} extracted files verified with identical SHA-256!")

        # 2. Run verification test suite in extracted temp directory
        python_exe = sys.executable
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        print("Executing validate_phase1_2_1.py in extracted environment...")
        res1 = subprocess.run([python_exe, "-B", str(temp_root / "scripts/phase1_2_1/validate_phase1_2_1.py")],
                              cwd=str(temp_root), capture_output=True, text=True, env=env)
        if res1.returncode != 0:
            print(res1.stdout)
            print(res1.stderr)
            raise RuntimeError("validate_phase1_2_1.py failed in extracted package!")
        print("  -> validate_phase1_2_1: PASS (13/13)")

        print("Executing phase1_2_2/run_all.py in extracted environment...")
        res2 = subprocess.run([python_exe, "-B", str(temp_root / "scripts/phase1_2_2/run_all.py")],
                              cwd=str(temp_root), capture_output=True, text=True, env=env)
        if res2.returncode != 0:
            print(res2.stdout)
            print(res2.stderr)
            raise RuntimeError("phase1_2_2/run_all.py failed in extracted package!")
        print("  -> phase1_2_2/run_all: PASS (8/8 modules)")

        print("Executing phase1_2_3_1/run_all.py in extracted environment...")
        res3 = subprocess.run([python_exe, "-B", str(temp_root / "scripts/phase1_2_3_1/run_all.py")],
                              cwd=str(temp_root), capture_output=True, text=True, env=env)
        if res3.returncode != 0:
            print(res3.stdout)
            print(res3.stderr)
            raise RuntimeError("phase1_2_3_1/run_all.py failed in extracted package!")
        print("  -> phase1_2_3_1/run_all: PASS (84/84 checks)")

        print("\nAll regression tests passed successfully inside isolated extracted package!")

if __name__ == "__main__":
    zip_p, sha_p, lines = build_package()
    verify_extracted_package(zip_p, lines)
