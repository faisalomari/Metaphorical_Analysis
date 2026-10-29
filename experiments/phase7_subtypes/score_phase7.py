"""Step 4 (NO API calls): scoring for all 4 Phase 7 subtypes (استعارة قديمة,
كناية عن صفة, تشبيه قصير, تشبيه مطول) x {zero-shot, few-shot} x 3 models.

Primary metric: verse-level TP/FP/FN/P/R/F1 (CLAUDE.md rule 4 warns
verse-level ALONE produces artifacts for some elements, but here it is the
task's own declared primary metric, with span-level strict/token-overlap
reported alongside as secondary, per rule 4's "always both" requirement).
Reuses span_matching.best_match / pilot_3models.analyze.prf1 /
phase4_e1_v2.scoring_v2.bootstrap_ci_pairwise unchanged -- no new scoring
math invented here.

Ground truth = the exact-subtype annotations in data/ali_poems/poems/*.json
(same census.py convention as every Step 0/1 script in this package), NOT a
separate ground-truth file -- Phase 7 asks the model about EVERY verse in
the 25-poem pool (unlike Phase 3's recall-only design), so TP/FP/FN/P/R/F1
are all honestly defined here.

Reads BOTH run_manifest.json (استعارة قديمة/كناية عن صفة) and
run_manifest_tashbih2.json (تشبيه قصير/تشبيه مطول) -- additive, neither file
touches the other.
"""
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from census import load_manifest, load_poem_json, verse_no_of  # noqa: E402
from phase7_config import EVAL_POOL_25_PATH, PHASE4_DIR, RESULTS_DIR  # noqa: E402

sys.path.insert(0, str(PHASE4_DIR.parents[0] / "pilot_3models"))
from analyze import prf1  # noqa: E402
from span_matching import best_match  # noqa: E402

sys.path.insert(0, str(PHASE4_DIR))
from scoring_v2 import bootstrap_ci_pairwise, per_poem_diff_signs  # noqa: E402

ALL_SUBTYPES = ["استعارة قديمة", "كناية عن صفة", "تشبيه قصير", "تشبيه مطول"]
CONDITIONS = ["zero", "few"]
PROVIDERS = ["anthropic", "openai", "google"]
CRITERIA = ["verse", "strict", "token"]
POOL_POSITIVE_FLOOR = 30
INDICATIVE_ONLY = {"استعارة قديمة": 15, "تشبيه قصير": 13, "تشبيه مطول": 25}  # <30, from Step 0/1

FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def parse_response(raw_text: str) -> dict:
    cleaned = FENCE_RE.sub("", (raw_text or "").strip()).strip()
    try:
        obj = json.loads(cleaned)
        return {"exists": obj.get("exists"), "appearance": obj.get("appearance"), "parse_error": False}
    except json.JSONDecodeError:
        return {"exists": None, "appearance": None, "parse_error": True}


def load_manifests() -> list:
    out = []
    for name in ["run_manifest.json", "run_manifest_tashbih2.json"]:
        p = RESULTS_DIR / name
        if p.exists():
            out.extend(json.loads(p.read_text(encoding="utf-8")))
    return out


def build_cell_index(manifest: list) -> dict:
    """{(subtype, condition, poem_id, verse_no, provider) -> parsed-or-None}"""
    idx = {}
    for r in manifest:
        key = (r["subtype"], r["condition"], r["poem_id"], r["verse_no"], r["provider"])
        if r.get("error"):
            idx[key] = None
            continue
        raw_path = RESULTS_DIR / r["raw_text_file"]
        raw_text = raw_path.read_text(encoding="utf-8") if raw_path.exists() else ""
        idx[key] = parse_response(raw_text)
    return idx


def build_ground_truth(subtype: str, pool_poem_ids: list) -> dict:
    """{poem_id: {verse_no: [span_text, ...]}} -- positives only, single-verse
    scoring unit (verse_no_of takes the span's first verse number, same
    convention as every Step 0/1 script; materiality check already showed
    <=8.4% of spans cross a verse boundary for any of the 4 subtypes)."""
    gt = {}
    for pid in pool_poem_ids:
        pj = load_poem_json(pid)
        n_verses = pj["verse_count"]
        by_verse = {v: [] for v in range(1, n_verses + 1)}
        for a in pj["annotations"]:
            if (a.get("subtype") or "").strip() != subtype:
                continue
            vno = verse_no_of(a)
            if 1 <= vno <= n_verses:
                span = (a.get("span_text") or "").strip()
                if span:
                    by_verse[vno].append(span)
        gt[pid] = {"n_verses": n_verses, "by_verse": by_verse}
    return gt


def score_cell_verse(exists) -> str:
    return None  # placeholder, unused -- logic inlined below for clarity with span criteria


def score_poem(cell_index, subtype, condition, provider, poem_id, gt_poem, criterion) -> dict:
    tp = fp = fn = 0
    for verse_no in range(1, gt_poem["n_verses"] + 1):
        parsed = cell_index.get((subtype, condition, poem_id, verse_no, provider))
        gt_texts = gt_poem["by_verse"][verse_no]
        if parsed is None or parsed.get("exists") is None:
            continue
        exists = parsed["exists"]
        if criterion == "verse":
            if exists and gt_texts:
                tp += 1
            elif exists and not gt_texts:
                fp += 1
            elif not exists and gt_texts:
                fn += 1
            continue
        if not exists:
            fn += len(gt_texts)
            continue
        if not gt_texts:
            fp += 1
            continue
        match_idx = best_match(parsed.get("appearance") or "", gt_texts, criterion)
        if match_idx is None:
            fp += 1
            fn += len(gt_texts)
        else:
            tp += 1
            fn += len(gt_texts) - 1
    return {"tp": tp, "fp": fp, "fn": fn}


def score_set(cell_index, subtype, condition, provider, pool_poem_ids, gt, criterion) -> dict:
    per_poem = {}
    for pid in pool_poem_ids:
        per_poem[pid] = score_poem(cell_index, subtype, condition, provider, pid, gt[pid], criterion)
    tp = sum(c["tp"] for c in per_poem.values())
    fp = sum(c["fp"] for c in per_poem.values())
    fn = sum(c["fn"] for c in per_poem.values())
    return {"per_poem": per_poem, "overall": {"tp": tp, "fp": fp, "fn": fn, **prf1(tp, fp, fn)}}


def ensemble_exists_and_appearance(cell_index, subtype, condition, poem_id, verse_no, providers):
    votes = []
    appearances = {}
    for p in providers:
        parsed = cell_index.get((subtype, condition, poem_id, verse_no, p))
        if parsed is not None and parsed.get("exists") is not None:
            votes.append(parsed["exists"])
            appearances[p] = parsed.get("appearance")
    if not votes:
        return None, None
    majority = sum(votes) > len(votes) / 2
    if not majority:
        return False, None
    for p in providers:
        parsed = cell_index.get((subtype, condition, poem_id, verse_no, p))
        if parsed is not None and parsed.get("exists") is True:
            return True, parsed.get("appearance")
    return True, None


def score_ensemble_poem(cell_index, subtype, condition, poem_id, gt_poem, criterion, providers) -> dict:
    tp = fp = fn = 0
    for verse_no in range(1, gt_poem["n_verses"] + 1):
        exists, appearance = ensemble_exists_and_appearance(cell_index, subtype, condition, poem_id, verse_no, providers)
        gt_texts = gt_poem["by_verse"][verse_no]
        if exists is None:
            continue
        if criterion == "verse":
            if exists and gt_texts:
                tp += 1
            elif exists and not gt_texts:
                fp += 1
            elif not exists and gt_texts:
                fn += 1
            continue
        if not exists:
            fn += len(gt_texts)
            continue
        if not gt_texts:
            fp += 1
            continue
        match_idx = best_match(appearance or "", gt_texts, criterion)
        if match_idx is None:
            fp += 1
            fn += len(gt_texts)
        else:
            tp += 1
            fn += len(gt_texts) - 1
    return {"tp": tp, "fp": fp, "fn": fn}


def score_ensemble_set(cell_index, subtype, condition, pool_poem_ids, gt, criterion, providers) -> dict:
    per_poem = {pid: score_ensemble_poem(cell_index, subtype, condition, pid, gt[pid], criterion, providers)
                for pid in pool_poem_ids}
    tp = sum(c["tp"] for c in per_poem.values())
    fp = sum(c["fp"] for c in per_poem.values())
    fn = sum(c["fn"] for c in per_poem.values())
    return {"per_poem": per_poem, "overall": {"tp": tp, "fp": fp, "fn": fn, **prf1(tp, fp, fn)}}


def score_combo_poem(cell_index, subtype, cond_a, provider_a, cond_b, provider_b, poem_id, gt_poem,
                      criterion, op) -> dict:
    """op: 'or' or 'and' combining provider_a@cond_a with provider_b@cond_b."""
    tp = fp = fn = 0
    for verse_no in range(1, gt_poem["n_verses"] + 1):
        pa = cell_index.get((subtype, cond_a, poem_id, verse_no, provider_a))
        pb = cell_index.get((subtype, cond_b, poem_id, verse_no, provider_b))
        if pa is None or pb is None or pa.get("exists") is None or pb.get("exists") is None:
            continue
        ea, eb = pa["exists"], pb["exists"]
        exists = (ea or eb) if op == "or" else (ea and eb)
        appearance = pa.get("appearance") if ea else pb.get("appearance")
        gt_texts = gt_poem["by_verse"][verse_no]
        if criterion == "verse":
            if exists and gt_texts:
                tp += 1
            elif exists and not gt_texts:
                fp += 1
            elif not exists and gt_texts:
                fn += 1
            continue
        if not exists:
            fn += len(gt_texts)
            continue
        if not gt_texts:
            fp += 1
            continue
        match_idx = best_match(appearance or "", gt_texts, criterion)
        if match_idx is None:
            fp += 1
            fn += len(gt_texts)
        else:
            tp += 1
            fn += len(gt_texts) - 1
    return {"tp": tp, "fp": fp, "fn": fn}


def score_combo_set(cell_index, subtype, cond_a, provider_a, cond_b, provider_b, pool_poem_ids, gt,
                     criterion, op) -> dict:
    per_poem = {pid: score_combo_poem(cell_index, subtype, cond_a, provider_a, cond_b, provider_b, pid,
                                       gt[pid], criterion, op) for pid in pool_poem_ids}
    tp = sum(c["tp"] for c in per_poem.values())
    fp = sum(c["fp"] for c in per_poem.values())
    fn = sum(c["fn"] for c in per_poem.values())
    return {"per_poem": per_poem, "overall": {"tp": tp, "fp": fp, "fn": fn, **prf1(tp, fp, fn)}}


def main():
    pool_doc = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))
    pool_poem_ids = pool_doc["poem_ids"]

    manifest = load_manifests()
    print(f"Loaded {len(manifest)} manifest records (both files combined)")
    cell_index = build_cell_index(manifest)

    coverage_ok = True
    for subtype in ALL_SUBTYPES:
        for condition in CONDITIONS:
            for provider in PROVIDERS:
                n_ok = sum(1 for r in manifest if r["subtype"] == subtype and r["condition"] == condition
                           and r["provider"] == provider and r.get("error") is None)
                if n_ok != 327:
                    coverage_ok = False
                    print(f"  INCOMPLETE: {subtype}/{condition}/{provider}: {n_ok}/327 ok")
    print(f"Full identical coverage per (subtype, condition, model)? {coverage_ok}")

    report = {"coverage_ok": coverage_ok, "subtypes": {}, "indicative_only": INDICATIVE_ONLY,
              "pool_positive_floor": POOL_POSITIVE_FLOOR}

    for subtype in ALL_SUBTYPES:
        gt = build_ground_truth(subtype, pool_poem_ids)
        n_pool_positives = sum(1 for pid in pool_poem_ids for v in gt[pid]["by_verse"].values() if v)
        print(f"\n{'=' * 78}\n{subtype} (pool positives={n_pool_positives}"
              f"{' -- INDICATIVE ONLY, n<30' if subtype in INDICATIVE_ONLY else ''})\n{'=' * 78}")

        sub_report = {"n_pool_positives": n_pool_positives, "by_model": {}, "ensemble": {},
                      "bootstrap_few_minus_zero": {}, "design_choice": {}}

        per_model_per_cond = {}  # (provider, condition, criterion) -> score_set result
        for provider in PROVIDERS:
            sub_report["by_model"][provider] = {}
            for condition in CONDITIONS:
                sub_report["by_model"][provider][condition] = {}
                for criterion in CRITERIA:
                    res = score_set(cell_index, subtype, condition, provider, pool_poem_ids, gt, criterion)
                    per_model_per_cond[(provider, condition, criterion)] = res
                    sub_report["by_model"][provider][condition][criterion] = {
                        k: v for k, v in res["overall"].items()}
                    o = res["overall"]
                    print(f"  {provider:10s}/{condition:4s}/{criterion:6s}: TP={o['tp']:3d} FP={o['fp']:3d} "
                          f"FN={o['fn']:3d} P={o['precision']:.3f} R={o['recall']:.3f} F1={o['f1']:.3f}")

            for criterion in CRITERIA:
                ci = bootstrap_ci_pairwise(per_model_per_cond[(provider, "few", criterion)]["per_poem"],
                                            per_model_per_cond[(provider, "zero", criterion)]["per_poem"])
                sub_report["bootstrap_few_minus_zero"].setdefault(provider, {})[criterion] = ci

        # 3-model ensemble, both conditions
        for condition in CONDITIONS:
            sub_report["ensemble"][condition] = {}
            for criterion in CRITERIA:
                res = score_ensemble_set(cell_index, subtype, condition, pool_poem_ids, gt, criterion, PROVIDERS)
                per_model_per_cond[("ensemble3", condition, criterion)] = res
                sub_report["ensemble"][condition][criterion] = dict(res["overall"])
                o = res["overall"]
                print(f"  ENSEMBLE3  /{condition:4s}/{criterion:6s}: TP={o['tp']:3d} FP={o['fp']:3d} "
                      f"FN={o['fn']:3d} P={o['precision']:.3f} R={o['recall']:.3f} F1={o['f1']:.3f}")

        # Gemini leave-one-out (2-model ensemble anthropic+openai, "few") vs 3-model ensemble, "few"
        loo = score_ensemble_set(cell_index, subtype, "few", pool_poem_ids, gt, "verse", ["anthropic", "openai"])
        ens3 = per_model_per_cond[("ensemble3", "few", "verse")]
        loo_ci = bootstrap_ci_pairwise(ens3["per_poem"], loo["per_poem"])
        sub_report["design_choice"]["gemini_leave_one_out_verse"] = {
            "ensemble3_f1": ens3["overall"]["f1"], "loo_2model_f1": loo["overall"]["f1"],
            "ci_3model_minus_loo": loo_ci,
        }
        print(f"  Gemini LOO (verse, few): ensemble3 F1={ens3['overall']['f1']:.3f}, "
              f"2-model(no-Gemini) F1={loo['overall']['f1']:.3f}, "
              f"diff CI95={loo_ci['ci_95']}")

        # GPT-Z alone, Claude-FS alone, OR/AND combo (verse criterion, the task's named combo)
        gptz = per_model_per_cond[("openai", "zero", "verse")]
        claudefs = per_model_per_cond[("anthropic", "few", "verse")]
        combo_or = score_combo_set(cell_index, subtype, "zero", "openai", "few", "anthropic", pool_poem_ids, gt, "verse", "or")
        combo_and = score_combo_set(cell_index, subtype, "zero", "openai", "few", "anthropic", pool_poem_ids, gt, "verse", "and")
        sub_report["design_choice"]["gptz_alone_verse"] = dict(gptz["overall"])
        sub_report["design_choice"]["claudefs_alone_verse"] = dict(claudefs["overall"])
        sub_report["design_choice"]["gptz_or_claudefs_verse"] = dict(combo_or["overall"])
        sub_report["design_choice"]["gptz_and_claudefs_verse"] = dict(combo_and["overall"])
        print(f"  GPT-Z alone F1={gptz['overall']['f1']:.3f}  Claude-FS alone F1={claudefs['overall']['f1']:.3f}  "
              f"OR F1={combo_or['overall']['f1']:.3f}  AND F1={combo_and['overall']['f1']:.3f}  "
              f"3-vote(few) F1={ens3['overall']['f1']:.3f}")

        report["subtypes"][subtype] = sub_report

    out_path = RESULTS_DIR / "analysis_report_phase7.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
