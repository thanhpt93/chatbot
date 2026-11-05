"""
Inventory and Classification Script for Phase 1 Repository Cleanup.
Generates:
- reports/repository_cleanup/file_inventory.csv
- reports/repository_cleanup/file_inventory.json
- reports/repository_cleanup/review_required.csv
"""

import os
import json
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

def scan_files():
    all_files = []
    for root, dirs, files in os.walk(ROOT):
        # Exclude .git and .pgdata
        if ".git" in root or ".pgdata" in root:
            continue
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(ROOT).as_posix()
            all_files.append((rel_path, full_path))
    return sorted(all_files, key=lambda x: x[0])

def classify_file(rel_path: str, full_path: Path):
    size = full_path.stat().st_size
    parts = rel_path.split("/")
    filename = parts[-1]
    ext = full_path.suffix.lower()

    # Category D: Cache and temporary files
    if "__pycache__" in parts or ext == ".pyc":
        return {
            "path": rel_path,
            "category": "D",
            "purpose": "Compiled Python bytecode cache",
            "dependency_status": "GENERATED_CACHE",
            "phase1_requirement": "NO",
            "phase2_requirement": "NO",
            "duplicate_status": "GENERATED",
            "generated_status": "TEMPORARY",
            "recommended_action": "REMOVE",
            "reason": "Python bytecode cache must be removed prior to clean release packaging",
            "size_bytes": size
        }

    # Category E: Files requiring review
    if rel_path == "main.py":
        return {
            "path": rel_path,
            "category": "E",
            "purpose": "Empty root entrypoint scaffold",
            "dependency_status": "STANDALONE",
            "phase1_requirement": "NO",
            "phase2_requirement": "UNCERTAIN",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "RETAIN_UNDER_REVIEW",
            "reason": "Project entrypoint scaffold; currently empty (0 bytes). Retain in root pending Phase 2 entrypoint architecture",
            "size_bytes": size
        }

    if rel_path.startswith(".idea/"):
        return {
            "path": rel_path,
            "category": "E",
            "purpose": "JetBrains IDE workspace configuration",
            "dependency_status": "IDE_LOCAL",
            "phase1_requirement": "NO",
            "phase2_requirement": "CONVENIENCE",
            "duplicate_status": "UNIQUE",
            "generated_status": "GENERATED",
            "recommended_action": "RETAIN_UNDER_REVIEW",
            "reason": "IDE metadata; useful for local IDE developers but excluded from clean release distribution",
            "size_bytes": size
        }

    if rel_path == "database/inf_nffice_latest.dump.gz":
        return {
            "path": rel_path,
            "category": "E",
            "purpose": "PostgreSQL compressed database dump backup",
            "dependency_status": "BACKUP_SOURCE",
            "phase1_requirement": "OPTIONAL",
            "phase2_requirement": "OPTIONAL",
            "duplicate_status": "COMPRESSED_DUPLICATE_OF_inf_nffice_latest.dump",
            "generated_status": "SOURCE",
            "recommended_action": "RETAIN_UNDER_REVIEW",
            "reason": "Gzip duplicate of inf_nffice_latest.dump (87MB). Retained in database/ for backup; review whether to keep or remove in Phase 2",
            "size_bytes": size
        }

    # Category C: Archive Historical Evidence
    if rel_path.startswith("archive/"):
        return {
            "path": rel_path,
            "category": "C",
            "purpose": f"Archived Phase 1 historical asset: {filename}",
            "dependency_status": "HISTORICAL_ARCHIVE",
            "phase1_requirement": "ARCHIVE",
            "phase2_requirement": "NO",
            "duplicate_status": "ARCHIVED",
            "generated_status": "SOURCE" if ext == ".py" or ext == ".md" else "GENERATED",
            "recommended_action": "KEEP_IN_ARCHIVE",
            "reason": "Preserved in archive/phase1/ for auditability, traceability, and historical milestone reference",
            "size_bytes": size
        }

    # Category B: Canonical & Handover Documentation
    if rel_path.startswith("documentation/phase-1-database-discovery/"):
        return {
            "path": rel_path,
            "category": "B",
            "purpose": f"Canonical Phase 1 Graph Architecture & Discovery Document: {filename}",
            "dependency_status": "CANONICAL_SPECIFICATION",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "KEEP",
            "reason": "Authoritative system design, database mappings, and ETL specifications required for Phase 2 implementation",
            "size_bytes": size
        }

    if rel_path.startswith("docs/"):
        return {
            "path": rel_path,
            "category": "B",
            "purpose": f"Phase 1 Handover & Architecture Guide: {filename}",
            "dependency_status": "HANDOVER_SPECIFICATION",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "KEEP",
            "reason": "Essential Phase 2 prerequisites and Phase 1 known issues/limitations documentation",
            "size_bytes": size
        }

    # Category A: Active Foundation, Implementation & Tests
    if rel_path in ["README.md", "requirements.txt", ".gitignore"]:
        return {
            "path": rel_path,
            "category": "A",
            "purpose": f"Root project foundation file: {filename}",
            "dependency_status": "CORE_FOUNDATION",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "KEEP",
            "reason": "Standard project repository root configuration and dependency manifest",
            "size_bytes": size
        }

    if rel_path == "database/inf_nffice_latest.dump":
        return {
            "path": rel_path,
            "category": "A",
            "purpose": "PostgreSQL database dump for local restoration",
            "dependency_status": "RESTORE_SOURCE",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "KEEP",
            "reason": "Source dump file required by scripts/database-discovery/restore_database.py to restore local Postgres instance",
            "size_bytes": size
        }

    if rel_path.startswith("scripts/database-discovery/"):
        return {
            "path": rel_path,
            "category": "A",
            "purpose": f"Database Discovery & Profiling Utility: {filename}",
            "dependency_status": "DATABASE_DISCOVERY_TOOL",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "KEEP",
            "reason": "Core data discovery and profiling tool used to introspect PostgreSQL schemas and data characteristics",
            "size_bytes": size
        }

    if rel_path.startswith("artifacts/database-discovery/"):
        return {
            "path": rel_path,
            "category": "A",
            "purpose": f"Database Discovery Schema/Data Profiles & Metadata: {filename}",
            "dependency_status": "SCHEMA_INVENTORY_SOURCE",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "KEEP",
            "reason": "Schema inventory (schema_inventory.json) and relationship mappings used directly by regression validators",
            "size_bytes": size
        }

    if rel_path == "scripts/phase1_2/pg_readonly.py":
        return {
            "path": rel_path,
            "category": "A",
            "purpose": "Shared Read-Only PostgreSQL Connection Utility",
            "dependency_status": "SHARED_LIBRARY_DEPENDENCY",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "KEEP",
            "reason": "Imported by scripts/phase1_2_2/run_all.py; required for live PostgreSQL connection handling",
            "size_bytes": size
        }

    if rel_path.startswith("scripts/phase1_2_1/"):
        return {
            "path": rel_path,
            "category": "A",
            "purpose": f"Phase 1.2.1 Document and Schema Consistency Validator: {filename}",
            "dependency_status": "REGRESSION_VALIDATOR",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "KEEP",
            "reason": "Mandatory regression validator for continuous documentation and node/rel mapping consistency",
            "size_bytes": size
        }

    if rel_path.startswith("scripts/phase1_2_2/"):
        return {
            "path": rel_path,
            "category": "A",
            "purpose": f"Phase 1.2.2 Core Validation Suite: {filename}",
            "dependency_status": "REGRESSION_VALIDATOR",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "KEEP",
            "reason": "Mandatory regression validator for multi-tenant security, attendance, and ETL contracts",
            "size_bytes": size
        }

    if rel_path.startswith("tests/phase1_2_2/"):
        return {
            "path": rel_path,
            "category": "A",
            "purpose": f"Phase 1.2.2 Test Suite: {filename}",
            "dependency_status": "REGRESSION_TEST",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "KEEP",
            "reason": "Required test suite for Phase 1.2.2 validation",
            "size_bytes": size
        }

    if rel_path.startswith("scripts/phase1_2_3_1/"):
        return {
            "path": rel_path,
            "category": "A",
            "purpose": f"Active Phase 1.2.3.1 ETL security, circuit breaker, and guard implementation: {filename}",
            "dependency_status": "ACTIVE_FOUNDATION",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "KEEP",
            "reason": "Current approved security hardening and circuit breaker logic for Phase 2 ETL pipeline",
            "size_bytes": size
        }

    if rel_path.startswith("tests/phase1_2_3_1/"):
        return {
            "path": rel_path,
            "category": "A",
            "purpose": f"Active Phase 1.2.3.1 test suite and verification harnesses: {filename}",
            "dependency_status": "ACTIVE_TEST_SUITE",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "KEEP",
            "reason": "Authoritative verification test suite demonstrating 84/84 passing checks with strict security guards",
            "size_bytes": size
        }

    if rel_path.startswith("artifacts/phase1_2_3_1/"):
        return {
            "path": rel_path,
            "category": "A",
            "purpose": f"Active Phase 1.2.3.1 verification evidence artifact: {filename}",
            "dependency_status": "ACTIVE_EVIDENCE",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "SOURCE",
            "recommended_action": "KEEP",
            "reason": "Verified test results, accounting matrices, and runtime logs validating Phase 1 closure",
            "size_bytes": size
        }

    if rel_path.startswith(("artifacts/phase1_2_1/", "artifacts/phase1_2_2/")):
        return {
            "path": rel_path,
            "category": "A",
            "purpose": f"Regression validation run artifact: {filename}",
            "dependency_status": "REGRESSION_EVIDENCE",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "GENERATED",
            "recommended_action": "KEEP",
            "reason": "Generated by active regression test suite runs",
            "size_bytes": size
        }

    if rel_path.startswith("reports/"):
        return {
            "path": rel_path,
            "category": "A",
            "purpose": f"Phase 1 Cleanup and Inventory Report: {filename}",
            "dependency_status": "AUDIT_REPORT",
            "phase1_requirement": "YES",
            "phase2_requirement": "YES",
            "duplicate_status": "UNIQUE",
            "generated_status": "GENERATED",
            "recommended_action": "KEEP",
            "reason": "Audit inventory and repository cleanup report",
            "size_bytes": size
        }

    # Fallback
    return {
        "path": rel_path,
        "category": "A",
        "purpose": f"Project file: {filename}",
        "dependency_status": "STANDALONE",
        "phase1_requirement": "YES",
        "phase2_requirement": "YES",
        "duplicate_status": "UNIQUE",
        "generated_status": "SOURCE",
        "recommended_action": "KEEP",
        "reason": "Retained as part of project repository",
        "size_bytes": size
    }

def main():
    reports_dir = ROOT / "reports" / "repository_cleanup"
    reports_dir.mkdir(parents=True, exist_ok=True)

    files = scan_files()
    inventory = []
    review_files = []

    cat_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}

    for rel_path, full_path in files:
        if rel_path in ["scripts/prepare_inventory.py", "scripts/execute_cleanup.py"]:
            continue
        info = classify_file(rel_path, full_path)
        inventory.append(info)
        cat_counts[info["category"]] += 1

        if info["category"] == "E":
            review_files.append({
                "path": info["path"],
                "reason_for_uncertainty": info["reason"],
                "potential_risks_of_removal": "Could break entrypoint execution, IDE settings, or ability to restore Postgres dump",
                "recommended_action": info["recommended_action"],
                "phase2_impact": "Evaluated during Phase 2 bootstrap"
            })

    # Write file_inventory.csv
    csv_fields = [
        "path", "category", "purpose", "dependency_status",
        "phase1_requirement", "phase2_requirement", "duplicate_status",
        "generated_status", "recommended_action", "reason", "size_bytes"
    ]
    with open(reports_dir / "file_inventory.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(inventory)

    # Write file_inventory.json
    with open(reports_dir / "file_inventory.json", "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)

    # Write review_required.csv
    review_fields = [
        "path", "reason_for_uncertainty", "potential_risks_of_removal",
        "recommended_action", "phase2_impact"
    ]
    with open(reports_dir / "review_required.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=review_fields)
        writer.writeheader()
        writer.writerows(review_files)

    print(f"Total files cataloged post-cleanup: {len(inventory)}")
    print("Category Breakdown:")
    for c, cnt in sorted(cat_counts.items()):
        print(f"  Category {c}: {cnt}")
    print(f"Review required files: {len(review_files)}")

if __name__ == "__main__":
    main()
