"""Majority-vote (2-of-3 models) ensemble scoring for E1 v2, across every set
Z/A/B/C/D/D2. NO API calls -- reads results/phase4_e1_v2/run_manifest.json +
raw/*.txt only, same inputs as scoring_v2.py / verse_analysis.py.

PRIMARY definition (verse-level, declared per the task's instructions):
  ensemble_exists(set, poem, verse) = True iff >=2 of {anthropic, openai,
  google} returned exists=True for that cell. Ties are impossible with 3
  voters. A model cell with an API error or an unparseable JSON response
  (parse_verse_response -> exists=None) is treated as a non-vote (counted as
  False for the 2-of-3 threshold) -- stated explicitly here because the rule
  is declared whether or not it is ever exercised; see errors_unparseable in
  the written report for how many cells (if any) this rule actually applied
  to (expected 0, per the completed-run completeness check already recorded
  in docs/phase4/E1_V2_RESULTS.md).

SECONDARY (strict/token) ensemble-span rule, declared with its own stated
limitation:
  Among the models that voted exists=True for a verse, compute each one's
  own best_match(appearance, gt_spans, criterion) independently
  (pilot_3models.span_matching.best_match, reused unchanged -- the same
  matcher every single-model score in this project uses). If >=2 of those
  per-model match indices agree on the SAME ground-truth span, the ensemble
  counts 1 TP for that span (remaining GT spans at that verse count as FN,
  the same convention scoring_v2.score_poem already uses for a single
  model's one-match-per-verse scoring). If ensemble_exists is True but no GT
  span gets >=2 agreeing match-votes (including the case where 2+ models
  each correctly spot a DIFFERENT real span), the verse counts as 1 FP plus
  FN for every GT span at that verse.

  LIMITATION (declared, not hidden): this span rule under-counts ensemble TP
  whenever the "yes" models each correctly identify a different real span in
  a multi-span verse -- majority-vote-of-span-IDENTITY is a strictly harder
  bar than majority-vote-of-mere-existence, so the secondary ensemble F1 can
  look worse than the primary verse-level ensemble F1 even when every
  individual model's guess was individually defensible. This is the one rule
  used throughout this script for every set/model/criterion -- not picked
  per cell to make a particular number look better.
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import ALL_SET_NAMES, EVAL_POOL_25_PATH, E1V1_DIR, PILOT_DIR, RESULTS_DIR  # noqa: E402
from runner import spend_so_far  # noqa: E402  (import-order note: see analyze_v2.py --
# must come before gt_v2/scoring_v2, both of which insert experiments/phase4_e1 (v1) onto
# sys.path, which has its own runner.py with no spend_so_far and would shadow this one)
from gt_v2 import gt_spans_for_subtype  # noqa: E402
from parsing_v2 import parse_verse_response  # noqa: E402
from verse_analysis import bootstrap_pair  # noqa: E402

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_poem_json  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from analyze import prf1  # noqa: E402
from span_matching import best_match  # noqa: E402

MODELS = ["anthropic", "openai", "google"]
CRITERIA = ["verse", "strict", "token"]
DISPLAY = {"anthropic": "Claude Sonnet 4.6", "openai": "GPT-5.4-mini",
           "google": "Gemini (served: gemini-3.6-flash)"}


def build_parsed_cache(manifest: list, out_dir: Path) -> dict:
    """{(set_name, poem_id, verse_no, provider): parsed_dict}. An API-level
    error (r['error'] set) is folded into the same exists=None convention
    parse_verse_response already uses for an unparseable JSON body, so both
    kinds of failure are counted together as 'unparseable' below."""
    cache = {}
    for r in manifest:
        key = (r["set_name"], r["poem_id"], r["verse_no"], r["provider"])
        if r.get("error"):
            cache[key] = {"exists": None, "appearance": None, "reasoning": None,
                          "parse_error": f"api_error: {r['error']}"}
            continue
        raw_text = (out_dir / r["raw_text_file"]).read_text(encoding="utf-8")
        cache[key] = parse_verse_response(raw_text)
    return cache


def score_poem_ensemble(cache: dict, set_name: str, poem_id, n_verses: int,
                         gt_spans: dict, criterion: str) -> dict:
    tp = fp = fn = 0
    for verse_no in range(1, n_verses + 1):
        parsed = {m: cache[(set_name, poem_id, verse_no, m)] for m in MODELS}
        votes = sum(1 for m in MODELS if parsed[m]["exists"] is True)
        ensemble_exists = votes >= 2
        gt_texts = gt_spans[verse_no]
        if criterion == "verse":
            if ensemble_exists and gt_texts:
                tp += 1
            elif ensemble_exists and not gt_texts:
                fp += 1
            elif not ensemble_exists and gt_texts:
                fn += 1
            continue
        if not ensemble_exists:
            fn += len(gt_texts)
            continue
        if not gt_texts:
            fp += 1
            continue
        match_idxs = []
        for m in MODELS:
            if parsed[m]["exists"] is True:
                idx = best_match(parsed[m]["appearance"] or "", gt_texts, criterion)
                if idx is not None:
                    match_idxs.append(idx)
        counts = Counter(match_idxs)
        _, freq = counts.most_common(1)[0] if counts else (None, 0)
        if freq >= 2:
            tp += 1
            fn += len(gt_texts) - 1
        else:
            fp += 1
            fn += len(gt_texts)
    return {"tp": tp, "fp": fp, "fn": fn}


def score_poem_single_model(cache: dict, set_name: str, poem_id, provider: str, n_verses: int,
                             gt_spans: dict, criterion: str) -> dict:
    """Same scoring rule as scoring_v2.score_poem, reimplemented against the
    preloaded `cache` instead of re-reading run_manifest.json per verse (that
    function rescans the full 5,886-record manifest on every single lookup,
    which is fine called a handful of times but far too slow called this
    many times here) -- same output shape, verified to agree in `main()`."""
    tp = fp = fn = 0
    for verse_no in range(1, n_verses + 1):
        parsed = cache[(set_name, poem_id, verse_no, provider)]
        gt_texts = gt_spans[verse_no]
        if parsed["exists"] is None:
            continue
        if criterion == "verse":
            if parsed["exists"] and gt_texts:
                tp += 1
            elif parsed["exists"] and not gt_texts:
                fp += 1
            elif not parsed["exists"] and gt_texts:
                fn += 1
            continue
        if not parsed["exists"]:
            fn += len(gt_texts)
            continue
        if not gt_texts:
            fp += 1
            continue
        match_idx = best_match(parsed["appearance"] or "", gt_texts, criterion)
        if match_idx is None:
            fp += 1
            fn += len(gt_texts)
        else:
            tp += 1
            fn += len(gt_texts) - 1
    return {"tp": tp, "fp": fp, "fn": fn}


def score_set_single_model(cache: dict, pool: list, set_name: str, provider: str, criterion: str) -> dict:
    per_poem = {}
    for poem in pool:
        poem_id = poem["poem_id"]
        pj = load_poem_json(poem_id)
        gt_spans = gt_spans_for_subtype(pj)
        counts = score_poem_single_model(cache, set_name, poem_id, provider, pj["verse_count"],
                                          gt_spans, criterion)
        counts["tag"] = poem["tag"]
        per_poem[poem_id] = counts

    def pool_counts(tag=None):
        tp = sum(c["tp"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        fp = sum(c["fp"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        fn = sum(c["fn"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        return {"tp": tp, "fp": fp, "fn": fn, **prf1(tp, fp, fn)}

    return {"per_poem": per_poem, "overall": pool_counts(),
            "abu_nuwas": pool_counts("abu_nuwas"), "other": pool_counts("other")}


def score_set_ensemble(cache: dict, pool: list, set_name: str, criterion: str) -> dict:
    per_poem = {}
    for poem in pool:
        poem_id = poem["poem_id"]
        pj = load_poem_json(poem_id)
        gt_spans = gt_spans_for_subtype(pj)
        counts = score_poem_ensemble(cache, set_name, poem_id, pj["verse_count"], gt_spans, criterion)
        counts["tag"] = poem["tag"]
        per_poem[poem_id] = counts

    def pool_counts(tag=None):
        tp = sum(c["tp"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        fp = sum(c["fp"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        fn = sum(c["fn"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        return {"tp": tp, "fp": fp, "fn": fn, **prf1(tp, fp, fn)}

    return {"per_poem": per_poem, "overall": pool_counts(),
            "abu_nuwas": pool_counts("abu_nuwas"), "other": pool_counts("other")}


def agreement_for_set(cache: dict, pool: list, set_name: str) -> dict:
    """Verse-unit vote-count buckets (3/3, 2/3, 1/3, 0/3 positive votes) and
    each bucket's accuracy against the plain verse-level ground truth
    (gt_spans non-empty = true positive), independent of criterion."""
    buckets = {b: {"n": 0, "gt_pos": 0} for b in (3, 2, 1, 0)}
    by_tag = {"abu_nuwas": {b: {"n": 0, "gt_pos": 0} for b in (3, 2, 1, 0)},
              "other": {b: {"n": 0, "gt_pos": 0} for b in (3, 2, 1, 0)}}
    for poem in pool:
        poem_id = poem["poem_id"]
        tag = poem["tag"]
        pj = load_poem_json(poem_id)
        gt_spans = gt_spans_for_subtype(pj)
        for verse_no in range(1, pj["verse_count"] + 1):
            votes = sum(1 for m in MODELS if cache[(set_name, poem_id, verse_no, m)]["exists"] is True)
            gt_pos = bool(gt_spans[verse_no])
            buckets[votes]["n"] += 1
            by_tag[tag][votes]["n"] += 1
            if gt_pos:
                buckets[votes]["gt_pos"] += 1
                by_tag[tag][votes]["gt_pos"] += 1

    def finalize(b):
        out = {}
        for k, v in b.items():
            n, gt_pos = v["n"], v["gt_pos"]
            gt_pos_rate = (gt_pos / n) if n else None
            predicted_positive = k >= 2
            accuracy = None
            if n:
                accuracy = gt_pos_rate if predicted_positive else (1 - gt_pos_rate)
            out[str(k)] = {"n": n, "gt_positive_rate": gt_pos_rate, "accuracy": accuracy}
        return out

    return {"overall": finalize(buckets), "abu_nuwas": finalize(by_tag["abu_nuwas"]),
            "other": finalize(by_tag["other"])}


def verify_single_model_cache_scorer(cache, pool):
    """score_set_single_model (cache-based, this script) must reproduce the
    existing, independently-computed analysis_report.json (Z/A/B/C) and
    analysis_report_D.json (all 6 sets) exactly for every model/set/criterion
    -- the whole point of being allowed to re-derive it faster."""
    ref_zabc = json.loads((RESULTS_DIR / "analysis_report.json").read_text(encoding="utf-8"))
    ref_d = json.loads((RESULTS_DIR / "analysis_report_D.json").read_text(encoding="utf-8"))
    ref_verse = json.loads((RESULTS_DIR / "analysis_report_verse.json").read_text(encoding="utf-8"))
    n_checked = 0
    for criterion in CRITERIA:
        for s in ALL_SET_NAMES:
            for m in MODELS:
                got = score_set_single_model(cache, pool, s, m, criterion)["overall"]["f1"]
                if criterion == "verse":
                    ref = ref_verse[m]["per_set"][s]["overall"]["f1"]
                elif s in ("Z", "A", "B", "C"):
                    ref = ref_zabc[m][criterion]["per_set"][s]["overall"]["f1"]
                else:
                    ref = ref_d[m][criterion]["per_set"][s]["overall"]["f1"]
                assert abs(got - ref) < 1e-9, (criterion, s, m, got, ref)
                n_checked += 1
    print(f"PASS: single-model cache-based rescoring matches analysis_report.json / "
          f"analysis_report_D.json / analysis_report_verse.json exactly on all {n_checked} "
          f"(criterion, set, model) F1 values checked.")


def main():
    pool = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
    manifest = json.loads((RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
    spend = spend_so_far(manifest)
    cache = build_parsed_cache(manifest, RESULTS_DIR)
    verify_single_model_cache_scorer(cache, pool)

    api_errors = sum(1 for r in manifest if r.get("error"))
    unparseable_json = sum(1 for k, v in cache.items() if v["exists"] is None and "parse_error" in v
                            and v["parse_error"] and not str(v["parse_error"]).startswith("api_error"))
    total_unparseable = sum(1 for v in cache.values() if v["exists"] is None)

    report = {
        "definition_primary": "ensemble_exists(set,poem,verse) = True iff >=2 of "
                               "{anthropic,openai,google} returned exists=True for that cell "
                               "(2-of-3 majority; see module docstring for the unparseable-cell rule)",
        "span_rule_secondary": "a GT span counts as matched (1 ensemble TP) iff >=2 of the models "
                                "that voted exists=True independently best_match() it to the SAME "
                                "GT span index under the strict/token criterion; otherwise the "
                                "verse counts as 1 FP + FN per GT span. LIMITATION: under-counts TP "
                                "when 2+ 'yes' models each correctly identify a DIFFERENT real span "
                                "(see module docstring).",
        "errors_unparseable": {
            "api_errors": api_errors,
            "unparseable_json": unparseable_json,
            "total_unparseable_cells": total_unparseable,
            "total_cells": len(cache),
            "rule": ("none needed -- 0 occurred across all " + str(len(cache)) + " model cells"
                     if total_unparseable == 0 else
                     "an unparseable/errored model cell is treated as a non-vote (exists=False) "
                     "for the 2-of-3 threshold, and excluded from the strict/token match-vote count"),
        },
        "criteria": {},
        "agreement": {},
    }

    for s in ALL_SET_NAMES:
        report["agreement"][s] = agreement_for_set(cache, pool, s)

    for criterion in CRITERIA:
        report["criteria"][criterion] = {"per_set": {}, "vs_single": {}, "oracle": {}}
        single_per_set = {m: {} for m in MODELS}
        for s in ALL_SET_NAMES:
            ens = score_set_ensemble(cache, pool, s, criterion)
            report["criteria"][criterion]["per_set"][s] = {
                k: v for k, v in ens.items() if k != "per_poem"
            }
            for m in MODELS:
                single_per_set[m][s] = score_set_single_model(cache, pool, s, m, criterion)
            f1s = {m: single_per_set[m][s]["overall"]["f1"] for m in MODELS}
            best_model = max(f1s, key=f1s.get)
            report["criteria"][criterion]["oracle"][s] = {
                "best_model": best_model, "best_f1": f1s[best_model],
                "avg_f1": sum(f1s.values()) / 3, "all_f1": f1s,
            }
            report["criteria"][criterion]["vs_single"][s] = {
                m: bootstrap_pair(ens["per_poem"], single_per_set[m][s]["per_poem"]) for m in MODELS
            }

    (RESULTS_DIR / "analysis_report_ensemble.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Manifest: {len(manifest)} records, {api_errors} API errors. "
          f"Cumulative spend: ${spend['_total']:.4f}")
    print(f"Unparseable JSON cells: {unparseable_json}. Total unparseable (errors+unparseable): "
          f"{total_unparseable}/{len(cache)}.")

    print("\n" + "=" * 78)
    print("AGREEMENT BUCKETS (verse-units by vote count, overall)")
    print("=" * 78)
    for s in ALL_SET_NAMES:
        print(f"set {s}:")
        for k in ("3", "2", "1", "0"):
            b = report["agreement"][s]["overall"][k]
            print(f"  {k}/3 votes: n={b['n']:4d}  GT-positive-rate={b['gt_positive_rate']:.3f}  "
                  f"accuracy-vs-GT={b['accuracy']:.3f}")

    for criterion in CRITERIA:
        print(f"\n{'=' * 78}\nEnsemble -- criterion: {criterion}\n{'=' * 78}")
        for s in ALL_SET_NAMES:
            c = report["criteria"][criterion]["per_set"][s]["overall"]
            oracle = report["criteria"][criterion]["oracle"][s]
            print(f"  set {s}: ensemble TP={c['tp']:4d} FP={c['fp']:4d} FN={c['fn']:4d} "
                  f"P={c['precision']:.3f} R={c['recall']:.3f} F1={c['f1']:.3f}  |  "
                  f"best single={oracle['best_model']} F1={oracle['best_f1']:.3f}  "
                  f"avg single F1={oracle['avg_f1']:.3f}")
            for m in MODELS:
                vs = report["criteria"][criterion]["vs_single"][s][m]
                f1 = vs["f1"]
                sig = "SIG" if f1["sig"] else "ns"
                print(f"    ensemble - {m:9s}: F1={f1['point']:+.4f} "
                      f"CI95=[{f1['ci_95'][0]:+.4f},{f1['ci_95'][1]:+.4f}] ({sig})")

    print(f"\n{'=' * 78}\nDone. Full report written to "
          f"{RESULTS_DIR / 'analysis_report_ensemble.json'}\n{'=' * 78}")


if __name__ == "__main__":
    main()
