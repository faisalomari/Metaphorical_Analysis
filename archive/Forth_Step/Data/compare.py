# compare_analysations.py
# Compare two analysis outputs (JSONL or JSON array) by verse number ("no").
# Produces: (1) console summary, (2) per-verse diff JSONL, (3) mismatch CSV.

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _load_records(path: Path) -> List[Dict[str, Any]]:
    """
    Loads:
      - JSONL: one JSON object per line
      - JSON array: [ {...}, {...} ]
    """
    raw = _read_text(path).strip()
    if not raw:
        return []

    # JSON array
    if raw[0] == "[":
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError(f"{path} looks like JSON but not a list.")
        return [x for x in data if isinstance(x, dict)]

    # JSONL
    records: List[Dict[str, Any]] = []
    for i, line in enumerate(raw.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON decode error in {path} at line {i}: {e}\nLine: {line[:200]}") from e
        if isinstance(obj, dict):
            records.append(obj)
        else:
            raise ValueError(f"Non-object JSON at {path} line {i}. Expected dict/object.")
    return records


def _to_int_no(x: Any) -> Optional[int]:
    if x is None:
        return None
    if isinstance(x, int):
        return x
    if isinstance(x, str):
        x = x.strip()
        if x.isdigit():
            return int(x)
    return None


def _norm_bool(x: Any) -> Optional[bool]:
    if x is None:
        return None
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, float)):
        if x == 1:
            return True
        if x == 0:
            return False
    if isinstance(x, str):
        s = x.strip().lower()
        if s in {"true", "t", "yes", "y", "1"}:
            return True
        if s in {"false", "f", "no", "n", "0"}:
            return False
    return None


_ARABIC_DIACRITICS_RE = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")


def _norm_text(x: Any, *, strip_diacritics: bool = True) -> Optional[str]:
    if x is None:
        return None
    if not isinstance(x, str):
        x = str(x)
    s = x.strip()
    if not s:
        return None
    # collapse whitespace
    s = re.sub(r"\s+", " ", s)
    if strip_diacritics:
        s = _ARABIC_DIACRITICS_RE.sub("", s)
    return s


def _discover_elements(records: Iterable[Dict[str, Any]]) -> List[str]:
    """
    Discovers rhetorical elements by keys like:
      <name>_exists, <name>_appearance
    Returns unique <name> list.
    """
    elems = set()
    for r in records:
        for k in r.keys():
            if k.endswith("_exists"):
                elems.add(k[: -len("_exists")])
            elif k.endswith("_appearance"):
                elems.add(k[: -len("_appearance")])
    return sorted(elems)


def _index_by_no(records: List[Dict[str, Any]]) -> Tuple[Dict[int, Dict[str, Any]], List[str]]:
    idx: Dict[int, Dict[str, Any]] = {}
    warnings: List[str] = []
    seen = set()

    for r in records:
        no = _to_int_no(r.get("no"))
        if no is None:
            warnings.append(f"Record missing/invalid 'no': {r}")
            continue
        if no in seen:
            warnings.append(f"Duplicate 'no'={no} encountered. Keeping the last one.")
        seen.add(no)
        idx[no] = r
    return idx, warnings


@dataclass
class FieldDiff:
    element: str
    field: str  # "exists" or "appearance"
    a: Any
    b: Any


@dataclass
class VerseDiff:
    no: int
    diffs: List[FieldDiff]
    missing_in_a: bool = False
    missing_in_b: bool = False


def compare(
    a_idx: Dict[int, Dict[str, Any]],
    b_idx: Dict[int, Dict[str, Any]],
    elements: List[str],
    *,
    strip_diacritics: bool = True,
    compare_appearance_when_false: bool = False,
) -> List[VerseDiff]:
    all_nos = sorted(set(a_idx.keys()) | set(b_idx.keys()))
    out: List[VerseDiff] = []

    for no in all_nos:
        ra = a_idx.get(no)
        rb = b_idx.get(no)

        if ra is None:
            out.append(VerseDiff(no=no, diffs=[], missing_in_a=True, missing_in_b=False))
            continue
        if rb is None:
            out.append(VerseDiff(no=no, diffs=[], missing_in_a=False, missing_in_b=True))
            continue

        diffs: List[FieldDiff] = []
        for el in elements:
            a_exists = _norm_bool(ra.get(f"{el}_exists"))
            b_exists = _norm_bool(rb.get(f"{el}_exists"))
            if a_exists != b_exists:
                diffs.append(FieldDiff(element=el, field="exists", a=a_exists, b=b_exists))

            # appearance compare logic
            a_app = _norm_text(ra.get(f"{el}_appearance"), strip_diacritics=strip_diacritics)
            b_app = _norm_text(rb.get(f"{el}_appearance"), strip_diacritics=strip_diacritics)

            if compare_appearance_when_false:
                if a_app != b_app:
                    diffs.append(FieldDiff(element=el, field="appearance", a=a_app, b=b_app))
            else:
                # compare appearance only if both say it exists (True)
                if a_exists is True and b_exists is True and a_app != b_app:
                    diffs.append(FieldDiff(element=el, field="appearance", a=a_app, b=b_app))

        if diffs:
            out.append(VerseDiff(no=no, diffs=diffs))

    return out


def _summarize(diffs: List[VerseDiff]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "total_verses_union": 0,
        "verses_missing_in_a": 0,
        "verses_missing_in_b": 0,
        "verses_with_any_diff": 0,
        "field_diff_counts": defaultdict(int),
        "element_field_diff_counts": defaultdict(int),
    }

    total = len(diffs)
    # NOTE: diffs list contains only verses with diffs or missing; union size computed elsewhere in main.

    for vd in diffs:
        if vd.missing_in_a:
            summary["verses_missing_in_a"] += 1
        if vd.missing_in_b:
            summary["verses_missing_in_b"] += 1
        if vd.diffs:
            summary["verses_with_any_diff"] += 1
            for d in vd.diffs:
                summary["field_diff_counts"][d.field] += 1
                summary["element_field_diff_counts"][f"{d.element}:{d.field}"] += 1

    # Convert defaultdicts to normal dict for JSON friendliness
    summary["field_diff_counts"] = dict(summary["field_diff_counts"])
    summary["element_field_diff_counts"] = dict(summary["element_field_diff_counts"])
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="Verse-by-verse analysis file (jsonl or json array).")
    ap.add_argument("--b", required=True, help="All-verses analysis file (jsonl or json array).")
    ap.add_argument("--out_dir", default=".", help="Output directory for reports.")
    ap.add_argument("--strip_diacritics", action="store_true", help="Strip Arabic diacritics in appearance compare.")
    ap.add_argument(
        "--compare_appearance_when_false",
        action="store_true",
        help="Also compare appearance even if exists=False (default compares appearance only when both True).",
    )
    ap.add_argument("--show_first", type=int, default=10, help="Print first N mismatching verses.")
    args = ap.parse_args()

    a_path = Path(args.a).resolve()
    b_path = Path(args.b).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    a_recs = _load_records(a_path)
    b_recs = _load_records(b_path)

    a_idx, a_warn = _index_by_no(a_recs)
    b_idx, b_warn = _index_by_no(b_recs)

    # Discover element names from both files (union)
    elements = sorted(set(_discover_elements(a_recs)) | set(_discover_elements(b_recs)))
    if not elements:
        raise ValueError("Could not discover any elements (no *_exists / *_appearance keys found).")

    # Compare
    diffs = compare(
        a_idx,
        b_idx,
        elements,
        strip_diacritics=args.strip_diacritics,
        compare_appearance_when_false=args.compare_appearance_when_false,
    )

    union_nos = sorted(set(a_idx.keys()) | set(b_idx.keys()))
    summary = _summarize(diffs)
    summary["total_verses_union"] = len(union_nos)
    summary["elements"] = elements
    summary["a_path"] = str(a_path)
    summary["b_path"] = str(b_path)

    # Write JSON summary
    summary_path = out_dir / "comparison_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write per-verse diff JSONL
    diffs_jsonl_path = out_dir / "comparison_diffs.jsonl"
    with diffs_jsonl_path.open("w", encoding="utf-8") as f:
        for vd in diffs:
            row = {
                "no": vd.no,
                "missing_in_a": vd.missing_in_a,
                "missing_in_b": vd.missing_in_b,
                "diffs": [
                    {
                        "element": d.element,
                        "field": d.field,
                        "a": d.a,
                        "b": d.b,
                    }
                    for d in vd.diffs
                ],
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Write mismatch CSV (flat)
    csv_path = out_dir / "comparison_mismatches.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["no", "type", "element", "field", "a_value", "b_value"])
        for vd in diffs:
            if vd.missing_in_a:
                w.writerow([vd.no, "missing", "", "missing_in_a", "", ""])
                continue
            if vd.missing_in_b:
                w.writerow([vd.no, "missing", "", "missing_in_b", "", ""])
                continue
            for d in vd.diffs:
                w.writerow([vd.no, "field_mismatch", d.element, d.field, d.a, d.b])

    # Console report
    if a_warn or b_warn:
        print("Warnings:")
        for w_ in (a_warn + b_warn)[:20]:
            print("  -", w_)
        if len(a_warn + b_warn) > 20:
            print("  ... (more warnings omitted)")
        print()

    print("=== Comparison Summary ===")
    print(f"A: {a_path}")
    print(f"B: {b_path}")
    print(f"Verses (union): {summary['total_verses_union']}")
    print(f"Missing in A: {summary['verses_missing_in_a']}")
    print(f"Missing in B: {summary['verses_missing_in_b']}")
    print(f"Verses with differences: {summary['verses_with_any_diff']}")
    print("Field diff counts:", summary["field_diff_counts"])

    # Top element+field mismatches
    ef = summary["element_field_diff_counts"]
    top = sorted(ef.items(), key=lambda kv: kv[1], reverse=True)[:10]
    print("\nTop element/field mismatches:")
    for k, v in top:
        print(f"  {k}: {v}")

    # Show first N mismatching verses
    print(f"\nFirst {args.show_first} mismatching verses:")
    shown = 0
    for vd in diffs:
        if shown >= args.show_first:
            break
        if vd.missing_in_a:
            print(f"  no={vd.no}: missing in A")
            shown += 1
            continue
        if vd.missing_in_b:
            print(f"  no={vd.no}: missing in B")
            shown += 1
            continue
        if vd.diffs:
            print(f"  no={vd.no}:")
            for d in vd.diffs[:20]:
                print(f"    - {d.element}.{d.field}: A={d.a} | B={d.b}")
            if len(vd.diffs) > 20:
                print("    ... (more diffs omitted)")
            shown += 1

    print("\nOutputs written:")
    print(f"  - {summary_path}")
    print(f"  - {diffs_jsonl_path}")
    print(f"  - {csv_path}")


if __name__ == "__main__":
    main()
#python compare.py --a "..\Data\Jareer\Analysation2.jsonl" --b "..\Data\Jareer\Analysation.jsonl" --out_dir "..\Data\Jareer\compare_report" --strip_diacritics