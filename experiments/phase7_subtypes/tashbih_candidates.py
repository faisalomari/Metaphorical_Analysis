"""Follow-up to census.py's STOP finding: neither 'تشبيه بليغ' nor
'تشبيه مؤكد' exist anywhere in the corpus's annotation scheme (0 occurrences,
not in subtype_defs.py -- this annotator classifies تشبيه by
length/completeness: مطول/قصير/تمثيلي/مركب/الشيء بنفسه/ضمني/غريب, not by
the traditional eloquent/confirmed distinction). This script computes the
same per-subtype table for every تشبيه variant that (a) already has a
definition+example in subtype_defs.py and (b) has >=10 annotations, so the
user has real candidate data to pick a substitute from, no API calls.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from census import load_manifest, load_poem_json, verse_no_of  # noqa: E402
from phase7_config import ALREADY_USED_POEM_IDS, EVAL_POOL_25_PATH, NO_TEXT_POEM_ID  # noqa: E402
from eras_config import note_quality  # noqa: E402
from subtype_defs import SUBTYPE_DEFS  # noqa: E402
import json

CANDIDATES = ["تشبيه مطول", "تشبيه قصير", "تشبيه تمثيلي", "تشبيه مركب", "تشبيه الشيء بنفسه"]


def main():
    manifest = load_manifest()
    poem_ids_all = [row["poem_id"] for row in manifest]
    poet_of_poem = {row["poem_id"]: row["poet_name"] for row in manifest}
    pool_doc = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))
    pool_poem_ids = set(pool_doc["poem_ids"])

    all_poems = {pid: load_poem_json(pid) for pid in poem_ids_all}
    total_verses_corpus = sum(pj["verse_count"] for pj in all_poems.values())

    # Phase 3 crossmodel strict/token recall reference, hand-copied from
    # results/phase3_crossmodel/summary.md's headline table (read, not re-run).
    PHASE3_RECALL = {
        "تشبيه مطول": {"n": 30, "gemini_strict": 0.833, "gpt_strict": 0.667, "gemini_token": 0.933, "gpt_token": 0.767},
        "تشبيه قصير": {"n": 13, "gemini_strict": 0.615, "gpt_strict": 0.769, "gemini_token": 0.769, "gpt_token": 0.846},
        "تشبيه تمثيلي": {"n": 4, "gemini_strict": 0.250, "gpt_strict": 0.500, "gemini_token": None, "gpt_token": None},
        "تشبيه مركب": {"n": 3, "gemini_strict": 0.667, "gpt_strict": 0.667, "gemini_token": None, "gpt_token": None},
        "تشبيه الشيء بنفسه": {"n": 4, "gemini_strict": 0.750, "gpt_strict": 0.250, "gemini_token": None, "gpt_token": None},
    }

    print(f"{'subtype':<20}{'def_len':>8}{'pos_v':>7}{'poems':>7}{'poets':>7}{'rate':>8}"
          f"{'elig_ex':>9}{'elig_pts':>9}{'pool25':>8}{'n_ph3':>7}{'gem_strict':>11}{'gpt_strict':>11}")
    for sub in CANDIDATES:
        pos_verse_keys = set()
        poems_with_pos = set()
        poets_with_pos = set()
        eligible = 0
        eligible_poets = set()
        pool_pos = set()
        for pid, pj in all_poems.items():
            n_verses = pj["verse_count"]
            for a in pj["annotations"]:
                if (a.get("subtype") or "").strip() != sub:
                    continue
                vno = verse_no_of(a)
                if not (1 <= vno <= n_verses):
                    continue
                pos_verse_keys.add((pid, vno))
                poems_with_pos.add(pid)
                poets_with_pos.add(poet_of_poem.get(pid, pj.get("poet_name")))
                if pid in pool_poem_ids:
                    pool_pos.add((pid, vno))
                note = (a.get("analysis") or "").strip()
                if note and note_quality(note)[0] and pid not in ALREADY_USED_POEM_IDS and pid != NO_TEXT_POEM_ID:
                    eligible += 1
                    eligible_poets.add(poet_of_poem.get(pid, pj.get("poet_name")))
        d = SUBTYPE_DEFS.get(sub)
        def_len = len(d["definition_ar"] + " " + d["example"]) if d else None
        rate = len(pos_verse_keys) / total_verses_corpus
        p3 = PHASE3_RECALL.get(sub, {})
        print(f"{sub:<20}{def_len or 0:>8}{len(pos_verse_keys):>7}{len(poems_with_pos):>7}"
              f"{len(poets_with_pos):>7}{rate:>8.4f}{eligible:>9}{len(eligible_poets):>9}"
              f"{len(pool_pos):>8}{p3.get('n', '-'):>7}{p3.get('gemini_strict', '-'):>11}"
              f"{p3.get('gpt_strict', '-'):>11}")


if __name__ == "__main__":
    main()
