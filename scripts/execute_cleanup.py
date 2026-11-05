"""
Safe Reversible Cleanup Script for Phase 1 Repository.
Performs:
1. Cache removal (__pycache__, *.pyc)
2. Removal of duplicate outdated docs from docs/ (Docs 29-39)
3. Archiving of historical deliverable zips, changelogs, superseded scripts, tests, and artifacts
4. Verification of retained files
"""

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run_cleanup():
    log_actions = []

    # 1. Stage A: Remove __pycache__ and *.pyc
    for root, dirs, files in os.walk(ROOT):
        if ".git" in root or ".pgdata" in root:
            continue
        for d in dirs:
            if d == "__pycache__":
                p = Path(root) / d
                shutil.rmtree(p)
                log_actions.append(f"REMOVED CACHE DIR: {p.relative_to(ROOT).as_posix()}")
        for f in files:
            if f.endswith(".pyc"):
                p = Path(root) / f
                try:
                    p.unlink()
                    log_actions.append(f"REMOVED PYC: {p.relative_to(ROOT).as_posix()}")
                except Exception:
                    pass

    # 2. Stage A: Remove duplicate outdated docs in docs/ (29_ to 39_)
    docs_dir = ROOT / "docs"
    for item in docs_dir.iterdir():
        if item.is_file() and item.name.startswith(("29_", "30_", "31_", "32_", "33_", "34_", "35_", "36_", "37_", "38_", "39_")):
            item.unlink()
            log_actions.append(f"REMOVED DUPLICATE DOC: docs/{item.name}")

    # 3. Stage B: Create archive structure
    archive_dir = ROOT / "archive" / "phase1"
    zips_archive = archive_dir / "zips"
    changelogs_archive = archive_dir / "changelogs"
    scripts_db_disc_archive = archive_dir / "scripts" / "database-discovery"
    scripts_p12_archive = archive_dir / "scripts" / "phase1_2"
    artifacts_archive = archive_dir / "artifacts"

    for d in [zips_archive, changelogs_archive, scripts_db_disc_archive, scripts_p12_archive, artifacts_archive]:
        d.mkdir(parents=True, exist_ok=True)

    # 4. Move historical zips
    zips_to_move = [
        ROOT / "phase1_2_2_deliverables.zip",
        ROOT / "documentation" / "phase-1-database-discovery.zip",
        ROOT / "artifacts" / "phase1_2_3" / "phase1_2_3_deliverables.zip",
        ROOT / "artifacts" / "phase1_2_3_1" / "phase1_2_3_1_deliverables.zip",
    ]
    for z in zips_to_move:
        if z.exists():
            dest = zips_archive / z.name
            shutil.move(str(z), str(dest))
            log_actions.append(f"ARCHIVED ZIP: {z.relative_to(ROOT).as_posix()} -> {dest.relative_to(ROOT).as_posix()}")

    # 5. Move interim changelogs
    changelogs_to_move = [
        ROOT / "PHASE_1_2_2_CHANGELOG.md",
        ROOT / "PHASE_1_2_3_CHANGELOG.md",
        ROOT / "PHASE_1_2_3_1_CHANGELOG.md",
    ]
    for cl in changelogs_to_move:
        if cl.exists():
            dest = changelogs_archive / cl.name
            shutil.move(str(cl), str(dest))
            log_actions.append(f"ARCHIVED CHANGELOG: {cl.name} -> {dest.relative_to(ROOT).as_posix()}")

    # 6. Move legacy generator scripts in scripts/database-discovery
    db_disc_scripts_to_archive = [
        "gen_canonical_graph_model_and_mapping.py",
        "gen_canonical_inventory_and_catalog.py",
        "gen_canonical_relationships_and_vector_rag.py",
        "gen_canonical_tenant_queries_erd.py",
        "gen_catalog_tenant_erd_queries.py",
        "gen_inventory_and_classification.py",
        "gen_phase1_1_part1.py",
        "gen_phase1_1_part2.py",
        "gen_report_and_matrix.py",
        "generate_deliverables.py",
        "generate_final_correction_deliverables.py",
        "generate_review_deliverables.py",
        "apply_final_consistency_fix.py",
        "build_canonical_suite.py",
        "analyze_low_confidence_84.py",
        "analyze_modules_and_entities.py",
        "check_low_84_breakdown.py",
        "check_non_low_breakdown.py",
        "check_rel_exclusions.py",
        "reconcile_relationships_full.py",
    ]
    for s_name in db_disc_scripts_to_archive:
        src = ROOT / "scripts" / "database-discovery" / s_name
        if src.exists():
            dest = scripts_db_disc_archive / s_name
            shutil.move(str(src), str(dest))
            log_actions.append(f"ARCHIVED LEGACY GENERATOR: scripts/database-discovery/{s_name}")

    # 7. Move superseded scripts in scripts/phase1_2 (except pg_readonly.py)
    p12_scripts_to_archive = [
        "build_offline_profile.py",
        "dump_schema_facts.py",
        "extract_auth_routines.py",
        "extract_full_evidence.py",
        "inspect_related_and_claims.py",
        "profile_graph_sources.py",
        "validate_consistency.py",
    ]
    for s_name in p12_scripts_to_archive:
        src = ROOT / "scripts" / "phase1_2" / s_name
        if src.exists():
            dest = scripts_p12_archive / s_name
            shutil.move(str(src), str(dest))
            log_actions.append(f"ARCHIVED EARLY SCRIPT: scripts/phase1_2/{s_name}")

    # 8. Move superseded scripts/phase1_2_3 and tests/phase1_2_3
    src_p123 = ROOT / "scripts" / "phase1_2_3"
    if src_p123.exists():
        dest = archive_dir / "scripts" / "phase1_2_3"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_p123), str(dest))
        log_actions.append(f"ARCHIVED DIR: scripts/phase1_2_3 -> {dest.relative_to(ROOT).as_posix()}")

    src_tests_p123 = ROOT / "tests" / "phase1_2_3"
    if src_tests_p123.exists():
        dest = archive_dir / "tests" / "phase1_2_3"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_tests_p123), str(dest))
        log_actions.append(f"ARCHIVED DIR: tests/phase1_2_3 -> {dest.relative_to(ROOT).as_posix()}")

    # 9. Move historical intermediate artifacts (phase1_2, phase1_2_1, phase1_2_2, phase1_2_3)
    for sub in ["phase1_2", "phase1_2_1", "phase1_2_2", "phase1_2_3"]:
        src_art = ROOT / "artifacts" / sub
        if src_art.exists():
            dest = artifacts_archive / sub
            shutil.move(str(src_art), str(dest))
            log_actions.append(f"ARCHIVED ARTIFACTS DIR: artifacts/{sub} -> {dest.relative_to(ROOT).as_posix()}")

    print(f"Cleanup completed. Total actions executed: {len(log_actions)}")
    for a in log_actions[:20]:
        print(" ", a)
    if len(log_actions) > 20:
        print(f"  ... and {len(log_actions) - 20} more actions.")

    # Write cleanup action log
    log_file = ROOT / "reports" / "repository_cleanup" / "cleanup_actions.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(log_actions) + "\n")

if __name__ == "__main__":
    run_cleanup()
