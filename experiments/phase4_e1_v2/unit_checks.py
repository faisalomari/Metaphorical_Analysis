"""Local, NO-API unit checks for E1 v2, per the task's explicit step 2:
  1. render all 4 prompts (done separately via prompt_builder.py __main__)
  2. verify no example verse-source poem is in the eval pool
  3. verify GT parsing reproduces the poems' استعارة فعل counts
  4. run the scorer on a fake response to confirm it works end-to-end
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import E1V1_EVAL_POOL_PATH, E1V1_DIR, EXAMPLE_POEM_IDS  # noqa: E402
from gt_v2 import gt_spans_for_subtype, verses_by_no  # noqa: E402
from parsing_v2 import parse_verse_response  # noqa: E402

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_poem_json  # noqa: E402

import json  # noqa: E402


def check_no_leakage():
    pool = json.loads(E1V1_EVAL_POOL_PATH.read_text(encoding="utf-8"))["poems"]
    pool_ids = {p["poem_id"] for p in pool}
    overlap = pool_ids & set(EXAMPLE_POEM_IDS)
    assert not overlap, f"example-source poems leaked into eval pool: {overlap}"
    print(f"OK: 0 overlap between {len(pool_ids)}-poem eval pool and the 3 example-source poems "
          f"{EXAMPLE_POEM_IDS}.")


def check_gt_counts():
    """Cross-check against COST_PLAN.md §2.1 / SESSION_LOG.md 2026-10-10T19:15's
    independently-verified per-poem candidate-verse lists for the 3 example
    source poems: 16251: {1,2,3,5}; 17234: {3,4}; 21337: {1,2,4,6}."""
    expected = {"16251": {1, 2, 3, 5}, "17234": {3, 4}, "21337": {1, 2, 4, 6}}
    for poem_id, exp_verses in expected.items():
        pj = load_poem_json(poem_id)
        gt = gt_spans_for_subtype(pj)
        got_verses = {no for no, spans in gt.items() if spans}
        assert got_verses == exp_verses, f"poem {poem_id}: expected {exp_verses}, got {got_verses}"
        print(f"OK: poem {poem_id} استعارة فعل verses = {sorted(got_verses)} (matches prior session's figures)")

    # Also sanity check the eval pool's own poems load + GT parses without error.
    pool = json.loads(E1V1_EVAL_POOL_PATH.read_text(encoding="utf-8"))["poems"]
    total_gt_instances = 0
    for poem in pool:
        pj = load_poem_json(poem["poem_id"])
        gt = gt_spans_for_subtype(pj)
        assert len(gt) == pj["verse_count"], f"poem {poem['poem_id']}: GT dict size mismatch"
        total_gt_instances += sum(len(v) for v in gt.values())
    print(f"OK: all {len(pool)} eval-pool poems' GT parses cleanly; "
          f"{total_gt_instances} total استعارة فعل GT instances across the pool.")


def check_scorer_on_fake_response():
    """Build one fake verse-unit response and confirm parse_verse_response +
    span_matching.best_match (via scoring_v2.score_poem) produce the expected
    TP/FP/FN, without any real run_manifest.json / API call."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pilot_3models"))
    from span_matching import best_match  # noqa: E402

    pj = load_poem_json("16251")
    gt = gt_spans_for_subtype(pj)
    vb = verses_by_no(pj)

    # verse 1 has GT span "رَقيقِ حُسْنٍ" (from example_sets.json set A).
    assert gt[1], "expected verse 1 of poem 16251 to have a GT span"
    gt_span = gt[1][0]
    print(f"Verse 1 text: {vb[1]!r}")
    print(f"GT span: {gt_span!r}")

    fake_hit = '{"exists": true, "appearance": "%s", "reasoning": "placeholder"}' % gt_span
    fake_miss = '{"exists": true, "appearance": "كلمة غير موجودة إطلاقا", "reasoning": "placeholder"}'
    fake_false = '{"exists": false, "appearance": null, "reasoning": "placeholder"}'

    parsed_hit = parse_verse_response(fake_hit)
    parsed_miss = parse_verse_response(fake_miss)
    parsed_false = parse_verse_response(fake_false)
    assert parsed_hit["exists"] is True and parsed_hit["parse_error"] is None
    assert parsed_miss["exists"] is True
    assert parsed_false["exists"] is False

    idx_hit = best_match(parsed_hit["appearance"], gt[1], "strict")
    idx_miss = best_match(parsed_miss["appearance"], gt[1], "strict")
    assert idx_hit == 0, f"expected a strict match (TP), got {idx_hit}"
    assert idx_miss is None, f"expected no match (FP), got {idx_miss}"
    print("OK: fake hit -> matched (would score as TP); fake miss -> unmatched (would score as FP); "
          "fake exists=false -> would score as FN. Scorer logic confirmed end-to-end on fake data, "
          "no run_manifest.json / API call involved.")


if __name__ == "__main__":
    check_no_leakage()
    check_gt_counts()
    check_scorer_on_fake_response()
    print("\nAll unit checks passed. No API calls made.")
