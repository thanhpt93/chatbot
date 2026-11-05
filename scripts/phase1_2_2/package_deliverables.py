"""Package Phase 1.2.2 deliverables into docs/ mirror and phase1_2_2_deliverables.zip."""
import shutil
import zipfile
from pathlib import Path

ROOT = Path(r"C:\Project\chatbot")
CANONICAL_DOCS_DIR = ROOT / "documentation" / "phase-1-database-discovery"
DOCS_MIRROR_DIR = ROOT / "docs"
ARTIFACTS_DIR = ROOT / "artifacts" / "phase1_2_2"
SCRIPTS_DIR = ROOT / "scripts" / "phase1_2_2"
TESTS_DIR = ROOT / "tests" / "phase1_2_2"
ZIP_PATH = ROOT / "phase1_2_2_deliverables.zip"

CANONICAL_DOCS = [
    "18_phase1_1_canonical_document_register.md",
    "29_phase1_2_final_user_tenant_model.md",
    "30_phase1_2_complete_node_mapping.md",
    "31_phase1_2_complete_relationship_mapping.md",
    "32_phase1_2_final_graph_architecture.md",
    "33_phase1_2_etl_synchronization_contract.md",
    "34_phase1_2_query_and_security_validation.md",
    "35_phase1_2_final_neo4j_constraints_indexes.md",
    "36_phase1_2_automated_consistency_validation.md",
    "37_phase1_2_final_evidence_acceptance_matrix.md",
    "38_phase1_2_master_graph_traceability_matrix.md",
    "39_phase1_2_final_readiness_report.md",
]


def main() -> None:
    DOCS_MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    for doc in CANONICAL_DOCS:
        src = CANONICAL_DOCS_DIR / doc
        if src.exists() and not doc.startswith("18_"):
            shutil.copy2(src, DOCS_MIRROR_DIR / doc)

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for doc in CANONICAL_DOCS:
            src = CANONICAL_DOCS_DIR / doc
            if src.exists():
                zf.write(src, f"documentation/phase-1-database-discovery/{doc}")
                if not doc.startswith("18_"):
                    zf.write(src, f"docs/{doc}")
        for p in sorted(SCRIPTS_DIR.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                zf.write(p, str(p.relative_to(ROOT)))
        for p in sorted(TESTS_DIR.rglob("*")):
            if p.is_file():
                zf.write(p, str(p.relative_to(ROOT)))
        for p in sorted(ARTIFACTS_DIR.rglob("*")):
            if p.is_file():
                zf.write(p, str(p.relative_to(ROOT)))
        changelog = ROOT / "PHASE_1_2_2_CHANGELOG.md"
        if changelog.exists():
            zf.write(changelog, "PHASE_1_2_2_CHANGELOG.md")

    print(f"Packaged {ZIP_PATH} ({ZIP_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
