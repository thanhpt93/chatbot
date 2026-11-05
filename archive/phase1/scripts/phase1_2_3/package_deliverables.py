"""
Packages all Phase 1.2.3 artifacts, scripts, tests, changelog, and documentation
into artifacts/phase1_2_3/phase1_2_3_deliverables.zip.
"""

import zipfile
from pathlib import Path

ROOT = Path(r"C:\Project\chatbot")
ZIP_PATH = ROOT / "artifacts" / "phase1_2_3" / "phase1_2_3_deliverables.zip"


def package_phase1_2_3():
    files_to_pack = []

    # 1. artifacts/phase1_2_3/
    artifacts_dir = ROOT / "artifacts" / "phase1_2_3"
    for p in artifacts_dir.glob("*.md"):
        files_to_pack.append((p, f"artifacts/phase1_2_3/{p.name}"))

    # 2. scripts/phase1_2_3/
    scripts_dir = ROOT / "scripts" / "phase1_2_3"
    for p in scripts_dir.rglob("*.py"):
        files_to_pack.append((p, f"scripts/phase1_2_3/{p.relative_to(scripts_dir)}"))

    # 3. tests/phase1_2_3/
    tests_dir = ROOT / "tests" / "phase1_2_3"
    for p in tests_dir.rglob("*"):
        if p.is_file():
            files_to_pack.append((p, f"tests/phase1_2_3/{p.relative_to(tests_dir)}"))

    # 4. Root changelog
    cl = ROOT / "PHASE_1_2_3_CHANGELOG.md"
    if cl.exists():
        files_to_pack.append((cl, "PHASE_1_2_3_CHANGELOG.md"))

    # 5. Canonical documentation updated in place
    docs_dir = ROOT / "documentation" / "phase-1-database-discovery"
    for doc_name in [
        "18_phase1_1_canonical_document_register.md",
        "33_phase1_2_etl_synchronization_contract.md",
        "34_phase1_2_query_and_security_validation.md",
        "36_phase1_2_automated_consistency_validation.md",
        "37_phase1_2_final_evidence_acceptance_matrix.md",
        "38_phase1_2_master_graph_traceability_matrix.md",
        "39_phase1_2_final_readiness_report.md",
    ]:
        dp = docs_dir / doc_name
        if dp.exists():
            files_to_pack.append((dp, f"documentation/phase-1-database-discovery/{doc_name}"))

    print(f"Packaging {len(files_to_pack)} files into {ZIP_PATH}...")
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path, arcname in files_to_pack:
            zf.write(file_path, arcname)
            print(f"  + {arcname}")

    print(f"Successfully generated {ZIP_PATH} ({ZIP_PATH.stat().st_size:,} bytes)!")


if __name__ == "__main__":
    package_phase1_2_3()
