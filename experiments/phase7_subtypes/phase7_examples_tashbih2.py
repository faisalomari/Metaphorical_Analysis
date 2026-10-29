"""Step 1 addendum (NO API calls): few-shot example sets for the 2 تشبيه
subtypes from Dr. Ali Hussein's reply (تشبيه قصير, تشبيه مطول). Own script,
own output file (config/phase7_example_sets_tashbih2.json) -- does NOT edit
phase7_examples.py's output or re-touch استعارة قديمة/كناية عن صفة's
already-drawn pairs or already-spent API results, per the task's explicit
"additive only" instruction.

Same anti-"set C" guard, same seed=42 convention, same note-quality filter
as phase7_examples.py (see that file's docstring for the guard's exact
rules) -- reused unchanged, not reinvented.

Eval pool handling differs deliberately from phase7_examples.py: here the
pool exclusion is PER-SUBTYPE (eval_pool_25 minus THIS subtype's own 2
example-source poems), not a cross-subtype union. استعارة قديمة/كناية عن
صفة's Step 3 API calls already ran against the full unchanged 327-verse
pool; a per-subtype exclusion means a new subtype's draw can never shrink
or invalidate a pool other subtypes' real spend already committed to.
"""
import json
import sys
from pathlib import Path

import tiktoken

sys.path.insert(0, str(Path(__file__).resolve().parent))
from census import load_manifest, load_poem_json, verse_no_of  # noqa: E402
from phase7_config import (  # noqa: E402
    ALREADY_USED_POEM_IDS, CONFIG_DIR, EVAL_POOL_25_PATH, NO_TEXT_POEM_ID,
    PHASE4_DIR,
)
from eras_config import note_quality  # noqa: E402
from subtype_prompts import build_messages  # noqa: E402
from fewshot_prompts import build_messages_fewshot  # noqa: E402

sys.path.insert(0, str(PHASE4_DIR.parents[0] / "pilot_3models"))
from span_matching import token_overlap_ratio, TOKEN_THRESHOLD  # noqa: E402

import random

TARGET_SUBTYPES = ["تشبيه قصير", "تشبيه مطول"]
BASE_SEED = 42
MAX_ATTEMPTS = 60
TOKEN_OVERLAP_GUARD_THRESHOLD = TOKEN_THRESHOLD
ENC = tiktoken.get_encoding("cl100k_base")
QURAN_POET_NAME = "القرآن الكريم"
POOL_POSITIVE_FLOOR = 30


def n_tokens(text: str) -> int:
    return len(ENC.encode(text))


def is_in_reading_order(span: str, verse: str) -> bool:
    """True iff span's words appear as a CONTIGUOUS, in-order subsequence of
    verse's words. Guards against a real corpus data-quality issue found
    while drawing تشبيه مطول's examples: span_text is sometimes a scrambled
    word-bag rather than reading-order text, even for a single-verse
    annotation (confirmed on poem 27576 v30: span word order != verse word
    order, same verse_index, no multi-verse crossing involved). A scrambled
    span is harmless for token-overlap scoring but unusable as a few-shot
    example sent to a model."""
    span_words = span.split()
    verse_words = verse.split()
    if not span_words:
        return False
    for i in range(len(verse_words) - len(span_words) + 1):
        if verse_words[i:i + len(span_words)] == span_words:
            return True
    return False


def build_eligible_pool(subtype, all_poems, poet_of_poem, pool_poem_ids):
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
            vi_raw = str(a.get("verse_index"))
            if len({int(x) for x in vi_raw.split(",") if x.strip()}) > 1:
                # multi-verse-crossing span: span_text is a cross-verse word
                # bag reconstructed out of reading order (confirmed on poem
                # 6174 v24-25 -- see SESSION_LOG.md), unusable as a few-shot
                # example even though it's a fine scoring positive.
                continue
            verse_text_full = verses_by_no.get(vno, "")
            if not is_in_reading_order(span, verse_text_full):
                # span_text word order != verse word order even within a
                # single verse (confirmed on poem 27576 v30 -- see
                # SESSION_LOG.md): a pervasive corpus quirk, not limited to
                # multi-verse spans. Same exclusion rationale as above.
                continue
            out.append({
                "poem_id": pid, "poet_name": poet, "verse_no": vno,
                "verse_text": verses_by_no.get(vno, ""), "span": span, "note": note,
                "raw_key": a.get("raw_key"),
            })
    out.sort(key=lambda e: (int(e["poem_id"]), e["verse_no"], e["raw_key"] or 0))
    return out


def guard_reject_reason(ex1, ex2):
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


def draw_pair(subtype, eligible, log):
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
    pool_positive_counts = {}
    final_pools = {}

    for subtype in TARGET_SUBTYPES:
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

        zero_sys, zero_user = build_messages(subtype, c1["verse_text"])
        extra = [
            {"verse_text": c1["verse_text"], "span": c1["span"], "explanation": c1["note"]},
            {"verse_text": c2["verse_text"], "span": c2["span"], "explanation": c2["note"]},
        ]
        few_sys, few_user = build_messages_fewshot(subtype, c1["verse_text"], extra)
        print(f"\n  --- Zero-shot system message ({n_tokens(zero_sys)} tok) ---\n{zero_sys}")
        print(f"\n  --- Few-shot system message ({n_tokens(few_sys)} tok) ---\n{few_sys}")
        sets_doc["sets"][subtype]["zero_shot_system_tokens"] = n_tokens(zero_sys)
        sets_doc["sets"][subtype]["few_shot_system_tokens"] = n_tokens(few_sys)

        # per-subtype eval pool = eval_pool_25 minus THIS subtype's own example poems
        example_poem_ids = {c1["poem_id"], c2["poem_id"]}
        removed = example_poem_ids & pool_poem_ids
        final_pool_poem_ids = pool_poem_ids - example_poem_ids
        pool_verses_total = sum(pj["verse_count"] for pid, pj in all_poems.items() if pid in final_pool_poem_ids)
        print(f"\n  eval pool = eval_pool_25.json ({len(pool_poem_ids)} poems) minus this subtype's example "
              f"poems ({sorted(example_poem_ids)}) -> {len(removed)} removed, {len(final_pool_poem_ids)} poems, "
              f"{pool_verses_total} verse-units remain")

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
        flag = "  *** BELOW 30 -- indicative-only (Option (a) precedent applied, see SESSION_LOG.md) ***" \
            if len(pos) < POOL_POSITIVE_FLOOR else ""
        print(f"  {subtype}: {len(pos)} positive verse-units in its final eval pool{flag}")

        final_pools[subtype] = {
            "example_source_poem_ids": sorted(example_poem_ids),
            "removed_from_pool": sorted(removed),
            "final_eval_pool_poem_ids": sorted(final_pool_poem_ids, key=int),
            "final_eval_pool_verses": pool_verses_total,
            "indicative_only": len(pos) < POOL_POSITIVE_FLOOR,
        }

    print("\n" + "=" * 70)
    print("Draw log (every attempt, including rejects):")
    for row in draw_log:
        status = "ACCEPTED" if row["accepted"] else f"rejected ({row['reject_reason']})"
        print(f"  [{row['subtype']}] attempt {row['attempt']} seed={row['seed']} "
              f"{row['poet1']}/{row['poem1']} + {row['poet2']}/{row['poem2']} -> {status}")

    out = {
        "target_subtypes": TARGET_SUBTYPES,
        "draw_log": draw_log,
        "sets": sets_doc["sets"],
        "base_seed": BASE_SEED,
        "token_overlap_guard_threshold": TOKEN_OVERLAP_GUARD_THRESHOLD,
        "eval_pool_25_poem_ids": sorted(pool_poem_ids),
        "per_subtype_final_pool": final_pools,
        "pool_positive_counts": pool_positive_counts,
        "pool_positive_floor": POOL_POSITIVE_FLOOR,
    }
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CONFIG_DIR / "phase7_example_sets_tashbih2.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
