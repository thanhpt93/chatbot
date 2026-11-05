"""
Result Normalizer & Schema Comparator for Phase 1.2.3.1.
Enforces strict schema compliance, canonical key ordering, and exact JSON equality.
Does NOT convert nulls to empty strings. Does NOT silently ignore missing fields.
"""

from typing import List, Dict, Any, Tuple


class ResultNormalizer:
    Q01_CANONICAL_KEYS = [
        "department_id",
        "department_code",
        "department_name",
        "is_active",
        "manager_id",
        "manager_name",
        "sub_departments",
        "active_employees"
    ]

    Q08_CANONICAL_KEYS = [
        "notice_id",
        "title",
        "notice_type",
        "priority",
        "audience_name",
        "audience_type",
        "is_system_audience",
        "author_name",
        "published_at"
    ]

    @classmethod
    def normalize_q01_record(cls, row: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {}
        for k in cls.Q01_CANONICAL_KEYS:
            if k not in row:
                raise KeyError(f"Q01 row missing canonical field '{k}': {row}")
            val = row[k]
            if k == "sub_departments":
                if not isinstance(val, list):
                    raise TypeError(f"sub_departments must be list, got {type(val)}")
                sorted_subs = sorted(val, key=lambda x: x["id"])
                normalized[k] = [
                    {"id": s["id"], "name": s["name"]} for s in sorted_subs
                ]
            elif k == "active_employees":
                if not isinstance(val, list):
                    raise TypeError(f"active_employees must be list, got {type(val)}")
                sorted_emps = sorted(val, key=lambda x: x["id"])
                normalized[k] = [
                    {
                        "id": e["id"],
                        "display_name": e["display_name"],
                        "role_in_department": e["role_in_department"],
                        "is_primary": e["is_primary"],
                        "effective_from": e["effective_from"]
                    }
                    for e in sorted_emps
                ]
            else:
                normalized[k] = val
        return normalized

    @classmethod
    def normalize_q01_payload(cls, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        norm_rows = [cls.normalize_q01_record(r) for r in rows]
        norm_rows.sort(key=lambda x: x["department_id"])
        return norm_rows

    @classmethod
    def normalize_q08_record(cls, row: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {}
        for k in cls.Q08_CANONICAL_KEYS:
            if k not in row:
                raise KeyError(f"Q08 row missing canonical field '{k}': {row}")
            normalized[k] = row[k]
        return normalized

    @classmethod
    def normalize_q08_payload(cls, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        norm_rows = [cls.normalize_q08_record(r) for r in rows]
        # Order by published_at DESC, then notice_id DESC
        norm_rows.sort(key=lambda x: (x["published_at"], x["notice_id"]), reverse=True)
        # Apply canonical LIMIT 20
        return norm_rows[:20]

    @classmethod
    def compare_payloads(cls, payload_a: Any, payload_b: Any) -> Tuple[bool, str]:
        """
        Deep comparison of two normalized payloads.
        Returns (is_equal, difference_description).
        """
        if payload_a == payload_b:
            return True, "Payloads are identical"
        return False, f"Payload mismatch:\nLeft:  {payload_a}\nRight: {payload_b}"
