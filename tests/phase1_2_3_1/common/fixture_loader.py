"""
Common Fixture Loader for Phase 1.2.3.1 Tests.
Loads synthetic multi-tenant fixture data in an immutable, copy-safe manner.
Contains NO query or security business logic.
"""

import json
import copy
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_multi_tenant_fixture.json"


class FixtureLoader:
    @staticmethod
    def load_fixture(path: Optional[Path] = None) -> Dict[str, Any]:
        target = path or DEFAULT_FIXTURE_PATH
        if not target.exists():
            raise FileNotFoundError(f"Synthetic fixture not found at: {target}")
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        return copy.deepcopy(data)
