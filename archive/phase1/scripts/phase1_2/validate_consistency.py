#!/usr/bin/env python3
"""
Phase 1.2 / 1.2.1 Automated Consistency Validation Script (Work Package 8).
Delegates to and synchronizes with scripts/phase1_2_1/validate_phase1_2_1.py so both
artifacts/phase1_2/phase1_2_consistency_report.{json,md} and
artifacts/phase1_2_1/phase1_2_1_consistency_report.{json,md} remain 100% consistent.
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:\Project\chatbot")
P121_SCRIPT = ROOT / "scripts" / "phase1_2_1" / "validate_phase1_2_1.py"
P121_JSON = ROOT / "artifacts" / "phase1_2_1" / "phase1_2_1_consistency_report.json"
P121_MD = ROOT / "artifacts" / "phase1_2_1" / "phase1_2_1_consistency_report.md"
P12_JSON = ROOT / "artifacts" / "phase1_2" / "phase1_2_consistency_report.json"
P12_MD = ROOT / "artifacts" / "phase1_2" / "phase1_2_consistency_report.md"


def main():
    res = subprocess.run([sys.executable, str(P121_SCRIPT)], check=True)
    P12_JSON.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(P121_JSON, P12_JSON)
    shutil.copyfile(P121_MD, P12_MD)
    print("Synchronized Phase 1.2 and Phase 1.2.1 consistency reports: PASS")
    return res.returncode


if __name__ == "__main__":
    raise SystemExit(main())
