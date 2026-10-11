"""Parses one verse-unit's response: single JSON object
{"exists": bool, "appearance": str|null, "reasoning": str} — Phase 3's
schema (subtype_prompts.ANALYSIS_INSTRUCTIONS), NOT pilot_3models's 9-key
JSONL schema (parsing.parse_response), since v2's call shape is one call per
verse, not one call per poem.
"""
import json
import re

FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def parse_verse_response(raw_text: str) -> dict:
    """Returns {"exists": bool|None, "appearance": str|None, "reasoning": str|None,
    "parse_error": str|None}."""
    cleaned = FENCE_RE.sub("", raw_text).strip()
    try:
        obj = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {"exists": None, "appearance": None, "reasoning": None, "parse_error": f"{e}"}
    if not isinstance(obj, dict) or "exists" not in obj:
        return {"exists": None, "appearance": None, "reasoning": None,
                "parse_error": f"missing 'exists' field: {obj!r}"[:300]}
    return {
        "exists": bool(obj["exists"]),
        "appearance": obj.get("appearance"),
        "reasoning": obj.get("reasoning"),
        "parse_error": None,
    }


if __name__ == "__main__":
    print(parse_verse_response('{"exists": true, "appearance": "foo", "reasoning": "bar"}'))
    print(parse_verse_response('```json\n{"exists": false, "appearance": null, "reasoning": "baz"}\n```'))
    print(parse_verse_response('not json'))
