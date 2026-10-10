"""Bootstrap confidence intervals and paired model comparisons, computed
entirely from already-archived run outputs in this repository.

Makes ZERO API calls. Touches none of the frozen TEST evaluation's own
numbers -- it only adds an uncertainty estimate around point estimates that
`writing/paper_draft/final/paper_trimmed.md` already reports, and reconstructs
one table (the majority-vote ensemble) that the paper currently asserts
without showing.

Inputs (all pre-existing, read-only):
  - results/pilot_3models/test_final/{baseline,v4_combined}/{Imru1,Jarir,Abu_Tammam}/
    (raw per-run JSON/TXT model outputs + run_manifest.json; the frozen
    Phase 1 TEST evaluation)
  - data/ground_truth/ali_ana/original/*.xlsx (Prof. Hussein's ground truth,
    loaded via experiments/pilot_3models/ground_truth.py, unmodified)
  - results/phase3_subelements/raw/{كناية_لغوية,استعارة_تمثيلية}_all.jsonl
    (Gemini 3.5 Flash's Phase 3 subtype screen, row-level)
  - results/phase3_crossmodel/raw/openai/{same subtypes}_all.jsonl
    (GPT-5.4-mini's cross-model pass over the identical rows)

Method:
  - Phase 1: for each (model, element, prompt), the per-verse (tp, fp, fn)
    contribution is recomputed with the project's own `span_scoring` module
    (strict criterion only -- the criterion Table 1 in the paper reports),
    then pooled across the three TEST poems (Imru1 + Jarir + Abu_Tammam,
    151 verses). A nonparametric bootstrap resamples verses with replacement
    (B=10,000) and recomputes precision/recall/F1 each time; the 2.5th/97.5th
    percentiles of that distribution are reported as a 95% CI. This mirrors
    exactly how the paper's own point estimates are computed -- it does not
    introduce a different scoring rule, only resampling.
  - Paired model comparisons (Phase 1): the three models are scored against
    the *same* 151 verses, so for a fair paired bootstrap the same resampled
    verse indices are applied to all three models' per-verse arrays in each
    draw, and the resulting F1 difference is recorded per draw.
  - Phase 3: row_id is identical across the Gemini file
    (results/phase3_subelements/raw/) and the GPT file
    (results/phase3_crossmodel/raw/openai/) for the same subtype -- verified
    by direct inspection, not assumed. Recall is bootstrapped by resampling
    row_ids (paired across the two models) rather than by poem/verse, since
    Phase 3's unit of analysis is the pre-selected positive row, not the verse.

What this script does NOT do (see significance_results.md for the full list):
  - It does not estimate run-to-run (within-cell) variance beyond what the
    project's existing 2-run-majority protocol already collapsed into a
    single decision per verse; only 2 runs exist per cell, which is too few
    to itself bootstrap.
  - It does not correct for multiple comparisons across the many cells and
    pairs reported below.
  - It does not touch, re-run, or re-score anything -- every number it reads
    was already frozen before this script was written.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
PILOT_DIR = ROOT / "experiments" / "pilot_3models"
sys.path.insert(0, str(PILOT_DIR))

from config import TEST_POEMS, POEMS, RESULTS_DIR, ELEMENT_ORDER  # noqa: E402
from analyze import load_all_runs  # noqa: E402
from ground_truth import load_ground_truth_spans  # noqa: E402
from span_matching import best_match, strict_overlap  # noqa: E402
from span_scoring import majority_exists_and_appearance  # noqa: E402

RNG_SEED = 20261007
N_BOOT = 10000
TEST_FINAL_DIR = RESULTS_DIR / "test_final"
PROVIDERS = ["anthropic", "openai", "google"]
PROVIDER_LABEL = {"anthropic": "Claude Sonnet 4.6", "openai": "GPT-5.4-mini", "google": "Gemini 3.5 Flash"}

PHASE3_SUBELEMENTS_RAW = ROOT / "results" / "phase3_subelements" / "raw"
PHASE3_CROSSMODEL_OPENAI_RAW = ROOT / "results" / "phase3_crossmodel" / "raw" / "openai"
PHASE3_SUBTYPES = ["كناية_لغوية", "استعارة_تمثيلية"]
PHASE3_SUBTYPE_DISPLAY = {"كناية_لغوية": "كناية لغوية", "استعارة_تمثيلية": "استعارة تمثيلية"}


# ---------------------------------------------------------------------------
# Phase 1: per-verse outcome extraction (same scoring rule as span_scoring.py,
# kept at verse granularity instead of pre-aggregated, so it can be resampled)
# ---------------------------------------------------------------------------

def per_verse_outcomes(by_provider_runs, gt_spans, n_verses, element, criterion="strict"):
    """Returns list of (tp, fp, fn) ints, one tuple per verse 1..n_verses."""
    out = []
    for verse_no in range(1, n_verses + 1):
        exists, appearance = majority_exists_and_appearance(by_provider_runs, element, verse_no)
        gt_instances = gt_spans[verse_no][element]
        gt_texts = [g["span"] for g in gt_instances]

        if exists is None:
            out.append((0, 0, 0))
            continue
        if not exists:
            out.append((0, 0, len(gt_texts)))
            continue
        if not gt_texts:
            out.append((0, 1, 0))
            continue
        match_idx = best_match(appearance or "", gt_texts, criterion)
        if match_idx is None:
            out.append((0, 1, len(gt_texts)))
        else:
            out.append((1, 0, len(gt_texts) - 1))
    return out


def load_phase1_pooled_outcomes(prompt_key, element, criterion="strict"):
    """{provider: [(tp,fp,fn), ...]} pooled across the 3 TEST poems, in a
    fixed poem/verse order shared by all 3 providers (so index i means the
    same verse for every provider -- required for paired bootstrapping)."""
    pooled = {p: [] for p in PROVIDERS}
    for poem_key in TEST_POEMS:
        out_dir = TEST_FINAL_DIR / prompt_key / poem_key
        by_provider = load_all_runs(out_dir)
        gt_spans = load_ground_truth_spans(poem_key)
        n_verses = POEMS[poem_key]["n_verses"]
        for provider in PROVIDERS:
            pooled[provider].extend(
                per_verse_outcomes(by_provider[provider], gt_spans, n_verses, element, criterion)
            )
    return pooled


def prf1_from_outcomes(outcomes, idx):
    tp = fp = fn = 0
    for i in idx:
        t, f, n = outcomes[i]
        tp += t
        fp += f
        fn += n
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return precision, recall, f1, tp, fp, fn


def bootstrap_ci_single(outcomes, rng, n_boot=N_BOOT):
    n = len(outcomes)
    full_idx = np.arange(n)
    point = prf1_from_outcomes(outcomes, full_idx)
    boot_p, boot_r, boot_f1 = [], [], []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        p, r, f1, *_ = prf1_from_outcomes(outcomes, idx)
        boot_p.append(p)
        boot_r.append(r)
        boot_f1.append(f1)
    ci = lambda arr: (float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5)))
    return {
        "point": point,  # (precision, recall, f1, tp, fp, fn)
        "precision_ci": ci(boot_p),
        "recall_ci": ci(boot_r),
        "f1_ci": ci(boot_f1),
    }


def bootstrap_paired_diff(outcomes_a, outcomes_b, rng, n_boot=N_BOOT):
    """outcomes_a and outcomes_b must be the SAME length and SAME verse order
    (true for any two Phase 1 providers on the same element/prompt)."""
    n = len(outcomes_a)
    assert n == len(outcomes_b)
    _, _, f1_a0, *_ = prf1_from_outcomes(outcomes_a, np.arange(n))
    _, _, f1_b0, *_ = prf1_from_outcomes(outcomes_b, np.arange(n))
    diffs = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        _, _, f1_a, *_ = prf1_from_outcomes(outcomes_a, idx)
        _, _, f1_b, *_ = prf1_from_outcomes(outcomes_b, idx)
        diffs.append(f1_a - f1_b)
    diffs = np.array(diffs)
    return {
        "point_diff": f1_a0 - f1_b0,
        "ci": (float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))),
        "frac_a_gt_b": float(np.mean(diffs > 0)),
        "frac_b_gt_a": float(np.mean(diffs < 0)),
    }


# ---------------------------------------------------------------------------
# Ensemble (majority-vote-across-3-models) reconstruction, strict criterion,
# v4_combined, pooled TEST -- answers reviewer R2 Sec.3 (no table was ever
# published for this claim).
# ---------------------------------------------------------------------------

def ensemble_outcomes(prompt_key, element, criterion="strict"):
    out = []
    for poem_key in TEST_POEMS:
        out_dir = TEST_FINAL_DIR / prompt_key / poem_key
        by_provider = load_all_runs(out_dir)
        gt_spans = load_ground_truth_spans(poem_key)
        n_verses = POEMS[poem_key]["n_verses"]
        per_provider_votes = {
            p: {v: majority_exists_and_appearance(by_provider[p], element, v) for v in range(1, n_verses + 1)}
            for p in PROVIDERS
        }
        for verse_no in range(1, n_verses + 1):
            votes = [per_provider_votes[p][verse_no][0] for p in PROVIDERS]
            votes_bool = [bool(v) for v in votes if v is not None]
            if not votes_bool:
                out.append((0, 0, 0))
                continue
            ensemble_true = sum(votes_bool) >= 2
            gt_texts = [g["span"] for g in gt_spans[verse_no][element]]
            if not ensemble_true:
                out.append((0, 0, len(gt_texts)))
                continue
            appearance = None
            for p in PROVIDERS:
                exists_p, app_p = per_provider_votes[p][verse_no]
                if exists_p and app_p:
                    appearance = app_p
                    break
            if not gt_texts:
                out.append((0, 1, 0))
                continue
            match_idx = best_match(appearance or "", gt_texts, criterion)
            if match_idx is None:
                out.append((0, 1, len(gt_texts)))
            else:
                out.append((1, 0, len(gt_texts) - 1))
    return out


# ---------------------------------------------------------------------------
# Phase 3: paired recall comparison on identical rows, two models
# ---------------------------------------------------------------------------

def load_phase3_rows(path):
    """{row_id: {run_idx: hit_bool}}, where hit_bool is True only if the run
    both claimed the subtype exists AND its predicted span strictly overlaps
    the row's own annotated ground-truth span -- the same span-level
    criterion `results/phase3_crossmodel/raw/crossmodel_scoring_snapshot.json`
    uses for its own *_strict fields (naive "exists" alone overstates recall;
    see significance_results.md for the gap this closes)."""
    rows = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            hit = bool(rec["exists"]) and strict_overlap(rec.get("appearance") or "", rec.get("span") or "")
            rows.setdefault(rec["row_id"], {})[rec["run_idx"]] = hit
    return rows


def majority_of_2(run_values: dict):
    vals = [run_values[k] for k in sorted(run_values)]
    if len(vals) < 2:
        return vals[0] if vals else False
    return sum(vals) > len(vals) / 2  # ties -> False, matching per_verse_majority's convention


def phase3_paired_recall(subtype, rng, n_boot=N_BOOT):
    gemini_path = PHASE3_SUBELEMENTS_RAW / f"{subtype}_all.jsonl"
    gpt_path = PHASE3_CROSSMODEL_OPENAI_RAW / f"{subtype}_all.jsonl"
    gemini_rows = load_phase3_rows(gemini_path)
    gpt_rows = load_phase3_rows(gpt_path)
    row_ids = sorted(set(gemini_rows) & set(gpt_rows))
    missing_gemini = set(gpt_rows) - set(gemini_rows)
    missing_gpt = set(gemini_rows) - set(gpt_rows)
    gemini_hits = np.array([1 if majority_of_2(gemini_rows[r]) else 0 for r in row_ids])
    gpt_hits = np.array([1 if majority_of_2(gpt_rows[r]) else 0 for r in row_ids])
    n = len(row_ids)
    point_gemini = gemini_hits.mean()
    point_gpt = gpt_hits.mean()
    diffs, gem_boot, gpt_boot = [], [], []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        g = gemini_hits[idx].mean()
        p = gpt_hits[idx].mean()
        gem_boot.append(g)
        gpt_boot.append(p)
        diffs.append(g - p)
    diffs = np.array(diffs)
    ci = lambda arr: (float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5)))
    return {
        "n": n,
        "missing_gemini_rows": sorted(missing_gemini),
        "missing_gpt_rows": sorted(missing_gpt),
        "gemini_recall": point_gemini, "gemini_ci": ci(gem_boot),
        "gpt_recall": point_gpt, "gpt_ci": ci(gpt_boot),
        "diff": point_gemini - point_gpt, "diff_ci": ci(diffs),
        "frac_gemini_gt_gpt": float(np.mean(diffs > 0)),
    }


# ---------------------------------------------------------------------------
# Main: print everything significance_results.md reports, so the .md file's
# numbers can be regenerated and checked against this script's output.
# ---------------------------------------------------------------------------

def main():
    rng = np.random.default_rng(RNG_SEED)

    print("=" * 100)
    print("PHASE 1 -- per-cell bootstrap 95% CIs (strict criterion, pooled TEST, 151 verses)")
    print("=" * 100)
    for prompt_key in ["baseline", "v4_combined"]:
        for element in ELEMENT_ORDER:
            pooled = load_phase1_pooled_outcomes(prompt_key, element)
            for provider in PROVIDERS:
                res = bootstrap_ci_single(pooled[provider], rng)
                p, r, f1, tp, fp, fn = res["point"]
                print(f"{prompt_key:12} {element:10} {PROVIDER_LABEL[provider]:18} "
                      f"TP={tp:3} FP={fp:3} FN={fn:3}  "
                      f"P={p:.3f} [{res['precision_ci'][0]:.3f},{res['precision_ci'][1]:.3f}]  "
                      f"R={r:.3f} [{res['recall_ci'][0]:.3f},{res['recall_ci'][1]:.3f}]  "
                      f"F1={f1:.3f} [{res['f1_ci'][0]:.3f},{res['f1_ci'][1]:.3f}]")

    print()
    print("=" * 100)
    print("PHASE 1 -- paired bootstrap F1 differences across models, v4_combined, strict")
    print("=" * 100)
    for element in ELEMENT_ORDER:
        pooled = load_phase1_pooled_outcomes("v4_combined", element)
        pairs = [("anthropic", "openai"), ("anthropic", "google"), ("openai", "google")]
        for a, b in pairs:
            res = bootstrap_paired_diff(pooled[a], pooled[b], rng)
            print(f"{element:10} {PROVIDER_LABEL[a]:18} - {PROVIDER_LABEL[b]:18} "
                  f"diff={res['point_diff']:+.3f} CI=[{res['ci'][0]:+.3f},{res['ci'][1]:+.3f}] "
                  f"P(a>b)={res['frac_a_gt_b']:.3f} P(b>a)={res['frac_b_gt_a']:.3f}")

    print()
    print("=" * 100)
    print("ENSEMBLE (2-of-3 majority vote across models) -- strict criterion, v4_combined, pooled TEST")
    print("=" * 100)
    for element in ELEMENT_ORDER:
        outcomes = ensemble_outcomes("v4_combined", element)
        p, r, f1, tp, fp, fn = prf1_from_outcomes(outcomes, np.arange(len(outcomes)))
        print(f"{element:10} TP={tp:3} FP={fp:3} FN={fn:3}  P={p:.3f} R={r:.3f} F1={f1:.3f}")

    print()
    print("=" * 100)
    print("PHASE 3 -- paired recall comparison, Gemini 3.5 Flash vs GPT-5.4-mini, identical rows")
    print("=" * 100)
    for subtype in PHASE3_SUBTYPES:
        res = phase3_paired_recall(subtype, rng)
        print(f"{PHASE3_SUBTYPE_DISPLAY[subtype]:20} n={res['n']:3} "
              f"missing_in_gemini_file={res['missing_gemini_rows']} missing_in_gpt_file={res['missing_gpt_rows']}")
        print(f"  Gemini recall={res['gemini_recall']:.3f} CI=[{res['gemini_ci'][0]:.3f},{res['gemini_ci'][1]:.3f}]")
        print(f"  GPT    recall={res['gpt_recall']:.3f} CI=[{res['gpt_ci'][0]:.3f},{res['gpt_ci'][1]:.3f}]")
        print(f"  diff (Gemini-GPT)={res['diff']:+.3f} CI=[{res['diff_ci'][0]:+.3f},{res['diff_ci'][1]:+.3f}] "
              f"P(Gemini>GPT)={res['frac_gemini_gt_gpt']:.3f}")


if __name__ == "__main__":
    main()
