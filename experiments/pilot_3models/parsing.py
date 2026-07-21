"""Parse raw model responses into per-verse element records.

Per the pilot spec: if a model returns malformed JSON, the raw response is
already saved as-is by run_pilot.py; here we record the parse failure
explicitly rather than attempting any repair.
"""
import json
import re
from config import ELEMENT_ORDER, ELEMENT_AR

FENCE_RE = re.compile(r"^```(?:json|jsonl)?\s*|\s*```$", re.MULTILINE)


def _strip_fences(text: str) -> str:
    return FENCE_RE.sub("", text).strip()


def parse_response(raw_text: str) -> dict:
    """Returns {"verses": {no: {element: {"exists": bool, "appearance": str|None}}}, "parse_errors": [...]}"""
    verses = {}
    parse_errors = []
    cleaned = _strip_fences(raw_text)

    lines = [ln.strip() for ln in cleaned.splitlines() if ln.strip()]
    if len(lines) <= 1 and cleaned.startswith("["):
        try:
            objs = json.loads(cleaned)
        except json.JSONDecodeError as e:
            parse_errors.append(f"top-level JSON array parse failed: {e}")
            objs = []
    else:
        objs = []
        for i, line in enumerate(lines):
            try:
                objs.append(json.loads(line))
            except json.JSONDecodeError as e:
                parse_errors.append(f"line {i+1} parse failed: {e} | raw: {line[:200]}")

    for obj in objs:
        if not isinstance(obj, dict) or "no" not in obj:
            parse_errors.append(f"object missing 'no' field: {obj!r}"[:300])
            continue
        no = obj["no"]
        entry = {}
        for name in ELEMENT_ORDER:
            ar = ELEMENT_AR[name]
            exists_key, appear_key = f"{ar}_exists", f"{ar}_appearance"
            if exists_key not in obj:
                parse_errors.append(f"verse {no}: missing key {exists_key}")
                entry[name] = {"exists": None, "appearance": None}
                continue
            entry[name] = {"exists": bool(obj[exists_key]), "appearance": obj.get(appear_key)}
        verses[no] = entry

    return {"verses": verses, "parse_errors": parse_errors, "n_verses_parsed": len(verses)}


def parse_response_single_element(raw_text: str, element: str) -> dict:
    """Like parse_response, but for a decomposed single-element response: the
    schema only has {element}'s exists/appearance keys, so only those are
    checked (avoids spurious "missing key" errors for the other 3 elements)."""
    verses = {}
    parse_errors = []
    cleaned = _strip_fences(raw_text)
    ar = ELEMENT_AR[element]
    exists_key, appear_key = f"{ar}_exists", f"{ar}_appearance"

    lines = [ln.strip() for ln in cleaned.splitlines() if ln.strip()]
    if len(lines) <= 1 and cleaned.startswith("["):
        try:
            objs = json.loads(cleaned)
        except json.JSONDecodeError as e:
            parse_errors.append(f"top-level JSON array parse failed: {e}")
            objs = []
    else:
        objs = []
        for i, line in enumerate(lines):
            try:
                objs.append(json.loads(line))
            except json.JSONDecodeError as e:
                parse_errors.append(f"line {i+1} parse failed: {e} | raw: {line[:200]}")

    for obj in objs:
        if not isinstance(obj, dict) or "no" not in obj:
            parse_errors.append(f"object missing 'no' field: {obj!r}"[:300])
            continue
        no = obj["no"]
        if exists_key not in obj:
            parse_errors.append(f"verse {no}: missing key {exists_key}")
            verses[no] = {element: {"exists": None, "appearance": None}}
            continue
        verses[no] = {element: {"exists": bool(obj[exists_key]), "appearance": obj.get(appear_key)}}

    return {"verses": verses, "parse_errors": parse_errors, "n_verses_parsed": len(verses)}
