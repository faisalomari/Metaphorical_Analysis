"""Step 1 (no API calls): few-shot example sets + eval pool for the 2
approved subtypes (استعارة قديمة, كناية عن صفة). تشبيه بليغ is deliberately
NOT drawn here -- Dr. Hussein's answer on the correct تشبيه substitute is
still pending (see docs/phase4/SESSION_LOG.md's 2026-10-29 Phase 7 entries).
Designed so a 3rd subtype's set can be ADDED later (own SUBTYPE key in
EXAMPLE_SET_DOC["sets"], own file in this same config/ dir) without
touching either of these two sets' already-drawn data.

Anti-"set C" guard (declared, logged every attempt): reject a 2-example
draw if (a) the two examples come from the same poem/poet, (b) either has
no analysis note, (c) the normalized token-overlap ratio
(span_matching.token_overlap_ratio, this project's own existing
token-overlap definition, reused unchanged) between the two examples'
SPANS is >= TOKEN_OVERLAP_GUARD_THRESHOLD, (d) same ratio between the two
examples' full VERSE texts is >= threshold, or (e) same ratio between the
two examples' ANALYSIS NOTES is >= threshold (near-duplicate pattern
check). Threshold = 0.5, the project's own standing token-overlap
criterion threshold (span_matching.TOKEN_THRESHOLD) -- reused, not
reinvented, so "shares a key root/lexeme" means the same thing here as it
already means everywhere else this project scores spans.

On reject: re-draw with seed+1 (declared sequence 42, 43, 44, ... logged
each attempt+reason), same convention eras_examples.py already uses for
its own reject/redraw loop.
"""
import json
import sys
from pathlib import Path

import tiktoken

sys.path.insert(0, str(Path(__file__).resolve().parent))
from census import load_manifest, load_poem_json, verse_no_of  # noqa: E402
from phase7_config import (  # noqa: E402
    ALREADY_USED_POEM_IDS, CONFIG_DIR, EVAL_POOL_25_PATH, NO_TEXT_POEM_ID,
    PHASE4_DIR, PHASE3_DIR,
)
from eras_config import note_quality  # noqa: E402
from subtype_defs import SUBTYPE_DEFS  # noqa: E402
from subtype_prompts import build_messages  # noqa: E402
from fewshot_prompts import build_messages_fewshot  # noqa: E402

sys.path.insert(0, str(PHASE4_DIR.parents[0] / "pilot_3models"))
from span_matching import token_overlap_ratio, TOKEN_THRESHOLD  # noqa: E402

import random

APPROVED_SUBTYPES = ["استعارة قديمة", "كناية عن صفة"]
BASE_SEED = 42
MAX_ATTEMPTS = 60
TOKEN_OVERLAP_GUARD_THRESHOLD = TOKEN_THRESHOLD  # 0.5, reused from span_matching.py
ENC = tiktoken.get_encoding("cl100k_base")

QURAN_POET_NAME = "القرآن الكريم"


def n_tokens(text: str) -> int:
    return len(ENC.encode(text))


def build_eligible_pool(subtype: str, all_poems: dict, poet_of_poem: dict, pool_poem_ids: set) -> list:
    """Eligible example candidates for `subtype`: exact subtype match,
    non-empty span, note passing note_quality(), poem not in the 5 Phase-1
    frozen poems / NO_TEXT_POEM_ID / eval_pool_25 (example-source poems must
    stay OUT of the evaluation pool), poet is a real individual (excludes
    القرآن الكريم, same exclusion eras_config.py applies for the same
    reason)."""
    out = []
    for pid, pj in all_poems.items():
        if pid in ALREADY_USED_POEM_IDS or pid == NO_TEXT_POEM_ID or pid in pool_poem_ids:
            continue
        poet = poet_of_poem.get(pid, pj.get("poet_name"))
        if poet == QURAN_POET_NAME:
            continue
        n_verses = pj["verse_count"]
        verses_by_no = {v["verse_index"]: v["text"] for v in pj["verses"]}
        for a in pj["annotations"]:
            if (a.get("subtype") or "").strip() != subtype:
                continue
            vno = verse_no_of(a)
            if not (1 <= vno <= n_verses):
                continue
            span = (a.get("span_text") or "").strip()
            note = (a.get("analysis") or "").strip()
            if not span or not note:
                continue
            if not note_quality(note)[0]:
                continue
            out.append({
                "poem_id": pid, "poet_name": poet, "verse_no": vno,
                "verse_text": verses_by_no.get(vno, ""), "span": span, "note": note,
                "raw_key": a.get("raw_key"),
            })
    out.sort(key=lambda e: (int(e["poem_id"]), e["verse_no"], e["raw_key"] or 0))
    return out


def guard_reject_reason(ex1: dict, ex2: dict) -> str:
    if ex1["poem_id"] == ex2["poem_id"]:
        return "same_poem"
    if ex1["poet_name"] == ex2["poet_name"]:
        return "same_poet"
    if not ex1["note"] or not ex2["note"]:
        return "missing_note"
    r_span = token_overlap_ratio(ex1["span"], ex2["span"])
    if r_span >= TOKEN_OVERLAP_GUARD_THRESHOLD:
        return f"span_overlap={r_span:.2f}"
    r_verse = token_overlap_ratio(ex1["verse_text"], ex2["verse_text"])
    if r_verse >= TOKEN_OVERLAP_GUARD_THRESHOLD:
        return f"verse_overlap={r_verse:.2f}"
    r_note = token_overlap_ratio(ex1["note"], ex2["note"])
    if r_note >= TOKEN_OVERLAP_GUARD_THRESHOLD:
        return f"note_overlap={r_note:.2f}"
    return ""


def draw_pair(subtype: str, eligible: list, log: list) -> dict:
    poets = sorted({e["poet_name"] for e in eligible})
    if len(poets) < 2:
        raise RuntimeError(f"{subtype}: fewer than 2 eligible poets ({len(poets)})")
    by_poet = {}
    for e in eligible:
        by_poet.setdefault(e["poet_name"], []).append(e)

    for attempt in range(MAX_ATTEMPTS):
        seed = BASE_SEED + attempt
        random.seed(seed)
        p1, p2 = random.sample(poets, 2)
        c1 = random.sample(by_poet[p1], 1)[0]
        c2 = random.sample(by_poet[p2], 1)[0]
        reason = guard_reject_reason(c1, c2)
        log.append({"subtype": subtype, "attempt": attempt, "seed": seed,
                    "poet1": p1, "poet2": p2, "poem1": c1["poem_id"], "poem2": c2["poem_id"],
                    "accepted": not bool(reason), "reject_reason": reason or None})
        if not reason:
            return {"example1": c1, "example2": c2, "seed_used": seed, "attempts": attempt + 1}
    raise RuntimeError(f"{subtype}: no valid pair found in {MAX_ATTEMPTS} attempts")


def main():
    manifest = load_manifest()
    poem_ids_all = [row["poem_id"] for row in manifest]
    poet_of_poem = {row["poem_id"]: row["poet_name"] for row in manifest}
    all_poems = {pid: load_poem_json(pid) for pid in poem_ids_all}

    pool_doc = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))
    pool_poem_ids = set(pool_doc["poem_ids"])

    draw_log = []
    sets_doc = {"base_seed": BASE_SEED, "token_overlap_guard_threshold": TOKEN_OVERLAP_GUARD_THRESHOLD, "sets": {}}

    for subtype in APPROVED_SUBTYPES:
        eligible = build_eligible_pool(subtype, all_poems, poet_of_poem, pool_poem_ids)
        print(f"\n{'=' * 70}\n{subtype} — {len(eligible)} eligible example candidates, "
              f"{len({e['poet_name'] for e in eligible})} distinct poets")
        pair = draw_pair(subtype, eligible, draw_log)
        c1, c2 = pair["example1"], pair["example2"]
        print(f"  Drawn (seed={pair['seed_used']}, {pair['attempts']} attempt(s)):")
        for tag, c in (("Example 2", c1), ("Example 3", c2)):
            print(f"    {tag}: poet={c['poet_name']!r}, poem={c['poem_id']}, verse={c['verse_no']}")
            print(f"      verse: {c['verse_text']}")
            print(f"      span: «{c['span']}»")
            print(f"      note: {c['note']}")
        sets_doc["sets"][subtype] = {
            "examples": [
                {"text": c1["verse_text"], "annotations": [{"span": c1["span"], "analysis": c1["note"]}],
                 "poem_id": c1["poem_id"], "poet_name": c1["poet_name"], "verse_no": c1["verse_no"]},
                {"text": c2["verse_text"], "annotations": [{"span": c2["span"], "analysis": c2["note"]}],
                 "poem_id": c2["poem_id"], "poet_name": c2["poet_name"], "verse_no": c2["verse_no"]},
            ],
            "seed_used": pair["seed_used"], "attempts": pair["attempts"],
        }

        # full rendered prompts + token counts
        zero_sys, zero_user = build_messages(subtype, c1["verse_text"])
        extra = [
            {"verse_text": c1["verse_text"], "span": c1["span"], "explanation": c1["note"]},
            {"verse_text": c2["verse_text"], "span": c2["span"], "explanation": c2["note"]},
        ]
        few_sys, few_user = build_messages_fewshot(subtype, c1["verse_text"], extra)
        print(f"\n  --- Zero-shot system message ({n_tokens(zero_sys)} tok) ---\n{zero_sys}")
        print(f"\n  --- Few-shot system message ({n_tokens(few_sys)} tok) ---\n{few_sys}")
        print(f"\n  --- User message template ({n_tokens(zero_user.format(verse='<VERSE>') if False else zero_user)} tok, example verse shown) ---")
        sets_doc["sets"][subtype]["zero_shot_system_tokens"] = n_tokens(zero_sys)
        sets_doc["sets"][subtype]["few_shot_system_tokens"] = n_tokens(few_sys)

    print("\n" + "=" * 70)
    print("Draw log (every attempt, including rejects):")
    for row in draw_log:
        status = "ACCEPTED" if row["accepted"] else f"rejected ({row['reject_reason']})"
        print(f"  [{row['subtype']}] attempt {row['attempt']} seed={row['seed']} "
              f"{row['poet1']}/{row['poem1']} + {row['poet2']}/{row['poem2']} -> {status}")

    # ---- eval pool = eval_pool_25 minus example-source poems -------------
    example_poem_ids = set()
    for subtype in APPROVED_SUBTYPES:
        for ex in sets_doc["sets"][subtype]["examples"]:
            example_poem_ids.add(ex["poem_id"])
    removed = example_poem_ids & pool_poem_ids
    final_pool_poem_ids = pool_poem_ids - example_poem_ids
    print(f"\neval pool = eval_pool_25.json ({len(pool_poem_ids)} poems) minus example-source poems "
          f"({sorted(example_poem_ids)}) -> {len(removed)} actually removed, {len(final_pool_poem_ids)} poems remain")

    pool_verses_total = sum(pj["verse_count"] for pid, pj in all_poems.items() if pid in final_pool_poem_ids)
    print(f"Final eval pool: {len(final_pool_poem_ids)} poems, {pool_verses_total} verse-units")

    pool_positive_counts = {}
    for subtype in APPROVED_SUBTYPES:
        pos = set()
        for pid in final_pool_poem_ids:
            pj = all_poems[pid]
            for a in pj["annotations"]:
                if (a.get("subtype") or "").strip() != subtype:
                    continue
                vno = verse_no_of(a)
                if 1 <= vno <= pj["verse_count"]:
                    pos.add((pid, vno))
        pool_positive_counts[subtype] = len(pos)
        flag = "  *** BELOW 30 -- STOP, needs your choice ***" if len(pos) < 30 else ""
        print(f"  {subtype}: {len(pos)} positive verse-units in final eval pool{flag}")

    out = {
        "approved_subtypes": APPROVED_SUBTYPES,
        "draw_log": draw_log,
        "sets": sets_doc["sets"],
        "base_seed": BASE_SEED,
        "token_overlap_guard_threshold": TOKEN_OVERLAP_GUARD_THRESHOLD,
        "eval_pool_25_poem_ids": sorted(pool_poem_ids),
        "example_source_poem_ids": sorted(example_poem_ids),
        "final_eval_pool_poem_ids": sorted(final_pool_poem_ids, key=int),
        "final_eval_pool_verses": pool_verses_total,
        "pool_positive_counts": pool_positive_counts,
    }
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CONFIG_DIR / "phase7_example_sets.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
