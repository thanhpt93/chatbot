"""
Deliverables Packaging & Extraction Verification (Phase 1.2.3.1 WP6).
Packages complete project deliverables (Docs 01–39, scripts, tests, changelogs, manifest)
into artifacts/phase1_2_3_1/phase1_2_3_1_deliverables.zip, and executes self-contained
extraction and validation tests (DEF-P1231-08).
"""

import zipfile
import hashlib
import json
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ZIP_PATH = ROOT / "artifacts" / "phase1_2_3_1" / "phase1_2_3_1_deliverables.zip"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def build_package():
    print("=" * 80)
    print("BUILDING PHASE 1.2.3.1 COMPLETE DELIVERABLES PACKAGE")
    print("=" * 80)

    files_to_pack = []

    # 1. Complete Documentation (Docs 01–39)
    doc_dir = ROOT / "documentation" / "phase-1-database-discovery"
    if doc_dir.exists():
        for p in doc_dir.glob("*.md"):
            files_to_pack.append((p, f"documentation/phase-1-database-discovery/{p.name}"))

    docs_root = ROOT / "docs"
    if docs_root.exists():
        for p in docs_root.glob("*.md"):
            files_to_pack.append((p, f"docs/{p.name}"))

    # 2. All Regression & Validation Scripts
    for phase_dir in ["phase1_2_1", "phase1_2_2", "phase1_2_3_1"]:
        sdir = ROOT / "scripts" / phase_dir
        if sdir.exists():
            for p in sdir.rglob("*.py"):
                files_to_pack.append((p, f"scripts/{phase_dir}/{p.relative_to(sdir)}"))

    # 3. All Test Suites & Fixtures
    for test_dir in ["phase1_2_2", "phase1_2_3_1"]:
        tdir = ROOT / "tests" / test_dir
        if tdir.exists():
            for p in tdir.rglob("*"):
                if p.is_file() and "__pycache__" not in p.parts:
                    files_to_pack.append((p, f"tests/{test_dir}/{p.relative_to(tdir)}"))

    # 4. Phase 1.2.3.1 Evidence Artifacts
    art_dir = ROOT / "artifacts" / "phase1_2_3_1"
    if art_dir.exists():
        for p in art_dir.glob("*"):
            if p.is_file() and not p.name.endswith(".zip") and p.name != "manifest_sha256.json":
                files_to_pack.append((p, f"artifacts/phase1_2_3_1/{p.name}"))

    # 5. Root Documents & Changelogs
    for root_file in [
        "PHASE_1_2_2_CHANGELOG.md",
        "PHASE_1_2_3_CHANGELOG.md",
        "PHASE_1_2_3_1_CHANGELOG.md",
        "README.md",
        "requirements.txt"
    ]:
        rf_path = ROOT / root_file
        if rf_path.exists():
            files_to_pack.append((rf_path, root_file))

    # Compute SHA-256 Manifest
    manifest = {}
    for fpath, arcname in files_to_pack:
        manifest[arcname] = compute_sha256(fpath)

    # Save manifest locally first
    manifest_path = ROOT / "artifacts" / "phase1_2_3_1" / "manifest_sha256.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    files_to_pack.append((manifest_path, "artifacts/phase1_2_3_1/manifest_sha256.json"))

    print(f"Packaging {len(files_to_pack)} verified files into {ZIP_PATH}...")
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path, arcname in files_to_pack:
            zf.write(file_path, arcname)

    zip_size = ZIP_PATH.stat().st_size
    print(f"Archive successfully generated: {ZIP_PATH} ({zip_size:,} bytes, {len(files_to_pack)} entries)!")
    return ZIP_PATH, manifest


def verify_package(zip_path: Path, expected_manifest: dict) -> bool:
    print("\n" + "=" * 80)
    print("EXECUTING AUTOMATED EXTRACTION & SELF-CONTAINED VERIFICATION")
    print("=" * 80)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        print(f"Extracting archive to temporary sandbox: {tmp_root}...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_root)

        # PKG-01: Verify SHA-256 Checksums
        print("[PKG-01] Verifying SHA-256 Checksums across all extracted files...")
        checksum_failures = []
        for arcname, expected_hash in expected_manifest.items():
            extracted_file = tmp_root / arcname
            if not extracted_file.exists():
                checksum_failures.append(f"Missing file: {arcname}")
                continue
            actual_hash = compute_sha256(extracted_file)
            if actual_hash != expected_hash:
                checksum_failures.append(f"Hash mismatch on {arcname}: expected {expected_hash}, got {actual_hash}")

        if checksum_failures:
            print(f"[FAIL] PKG-01: Checksum verification failed ({len(checksum_failures)} errors)!")
            for err in checksum_failures[:5]:
                print(f"  - {err}")
            return False
        else:
            print(f"[PASS] PKG-01: 100% SHA-256 Checksums Verified ({len(expected_manifest)}/{len(expected_manifest)} files match)")

        # PKG-02: Self-Contained Execution Test
        print("\n[PKG-02] Executing self-contained run_all.py in extracted sandbox...")
        runner_script = tmp_root / "scripts" / "phase1_2_3_1" / "run_all.py"
        proc = subprocess.run([sys.executable, str(runner_script)], cwd=str(tmp_root), capture_output=True, text=True)
        
        if proc.returncode == 0 and "Overall Status:    PASS (SYNTHETIC FIXTURE & INDEPENDENT SIMULATION)" in proc.stdout:
            print("[PASS] PKG-02: Self-contained extraction test passed! Master validation suite succeeded inside isolated sandbox.")
            return True
        else:
            print(f"[FAIL] PKG-02: Execution failed in extracted sandbox (returncode {proc.returncode}):")
            print(proc.stdout)
            print(proc.stderr)
            return False


if __name__ == "__main__":
    zpath, manifest = build_package()
    success = verify_package(zpath, manifest)
    if not success:
        sys.exit(1)
    print("\nPhase 1.2.3.1 Deliverables Packaging & Verification: 100% SUCCESS!")
