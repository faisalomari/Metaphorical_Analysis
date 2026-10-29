"""Design-choice analysis: is "GPT-5.4-mini zero-shot (Z) + Claude Sonnet 4.6
few-shot, WITHOUT Gemini" a good production design vs. keeping Gemini?

NO API CALLS. Reads results/phase4_e1_v2/run_manifest.json + raw/*.txt only
(the existing cache-based scorer's inputs -- same files ensemble_v2.py reads),
reuses ensemble_v2.build_parsed_cache/score_poem_single_model/
score_set_single_model and verse_analysis.bootstrap_pair UNCHANGED. New code
is only the 2-voter OR/AND and generalized-3-voter combination rules in
combine.py (see that module's docstring for the declared span-matching
convention). Does not edit any existing file, result, or report.

Scope: the 25-poem pool (`config/eval_pool_25.json`) only -- Z/A/B/C/D/D2/
M1/M2/E1/E2/H1/H2/Q1/Q2 all ran on this exact pool (confirmed in
E1_V2_RESULTS.md / E1_V2_ERAS_FEWSHOT.md). F5/F10 are deliberately excluded
from every combination here: they ran on a DIFFERENT 50-poem pool with only
9/25 poems overlapping eval_pool_25, so they cannot be combined cell-by-cell
with Z/A/B/.../Q2 without silently fabricating an overlap that doesn't exist.
"""
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))  # experiments/phase4_e1_v2
from e1v2_config import EVAL_POOL_25_PATH, RESULTS_DIR, PILOT_DIR, E1V1_DIR  # noqa: E402
from runner import spend_so_far, call_cost, MODELS as PRICING  # noqa: E402
from gt_v2 import gt_spans_for_subtype  # noqa: E402
from ensemble_v2 import build_parsed_cache, score_poem_single_model, score_set_single_model  # noqa: E402
from verse_analysis import bootstrap_pair  # noqa: E402

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_poem_json  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from analyze import prf1  # noqa: E402

from combine import score_poem_two_voter, score_poem_three_voter_majority, agreement_matrix  # noqa: E402

OUT_DIR = Path(__file__).resolve().parents[3] / "results" / "phase4_e1_v2" / "design_choice"
CRITERIA = ["verse", "strict", "token"]
FS_SETS = ["A", "B", "D", "D2", "M1", "M2", "H1", "H2", "Q1", "Q2"]
PRODUCTION_FS_SET = "B"  # FULL_COST_MODEL_V2.md's S2 designation -- used only as the headline
# example; every table below reports the full range across FS_SETS, per the task's
# "do not pick the best set; state the range" instruction.


def build_gt_cache(pool):
    out = {}
    for poem in pool:
        poem_id = poem["poem_id"]
        pj = load_poem_json(poem_id)
        out[poem_id] = {"gt": gt_spans_for_subtype(pj), "n_verses": pj["verse_count"]}
    return out


def score_set(cache, pool, gt_cache, scorer_fn, criterion, **kwargs):
    per_poem = {}
    for poem in pool:
        poem_id = poem["poem_id"]
        counts = scorer_fn(cache, poem_id=poem_id, n_verses=gt_cache[poem_id]["n_verses"],
                            gt_spans=gt_cache[poem_id]["gt"], criterion=criterion, **kwargs)
        counts["tag"] = poem["tag"]
        per_poem[poem_id] = counts

    def pool_counts(tag=None):
        tp = sum(c["tp"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        fp = sum(c["fp"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        fn = sum(c["fn"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        return {"tp": tp, "fp": fp, "fn": fn, **prf1(tp, fp, fn)}

    return {"per_poem": per_poem, "overall": pool_counts(),
            "abu_nuwas": pool_counts("abu_nuwas"), "other": pool_counts("other")}


def _single(cache, poem_id, n_verses, gt_spans, criterion, set_name, provider):
    return score_poem_single_model(cache, set_name, poem_id, provider, n_verses, gt_spans, criterion)


def _two(cache, poem_id, n_verses, gt_spans, criterion, voter_a, voter_b, rule):
    return score_poem_two_voter(cache, voter_a, voter_b, poem_id, n_verses, gt_spans, criterion, rule)


def _three(cache, poem_id, n_verses, gt_spans, criterion, voter_specs):
    return score_poem_three_voter_majority(cache, voter_specs, poem_id, n_verses, gt_spans, criterion)


def real_cost_by_set_provider(manifest):
    cost = {}
    for r in manifest:
        if r.get("error"):
            continue
        key = (r["set_name"], r["provider"])
        cost[key] = cost.get(key, 0.0) + call_cost(r["provider"], r["usage"])
    return cost


def main():
    pool = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
    manifest = json.loads((RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
    cache = build_parsed_cache(manifest, RESULTS_DIR)
    gt_cache = build_gt_cache(pool)
    spend = spend_so_far(manifest)
    costs = real_cost_by_set_provider(manifest)

    report = {
        "pool": "eval_pool_25.json (25 poems, 327 verse-units) -- F5/F10 excluded, different pool",
        "fs_sets": FS_SETS,
        "criteria": {},
        "real_cost_by_set_provider_usd": {f"{s}|{p}": round(c, 4) for (s, p), c in costs.items()},
        "manifest_total_spend_usd": spend["_total"],
    }

    for criterion in CRITERIA:
        crit_report = {}

        # D_A: GPT Z alone
        d_a = score_set(cache, pool, gt_cache, _single, criterion, set_name="Z", provider="openai")
        crit_report["D_A_gpt_z"] = {k: v for k, v in d_a.items() if k != "per_poem"}

        # D_B: Claude FS alone, every set
        d_b = {}
        for fs in FS_SETS:
            d_b[fs] = score_set(cache, pool, gt_cache, _single, criterion, set_name=fs, provider="anthropic")
        d_b_f1s = [d_b[fs]["overall"]["f1"] for fs in FS_SETS]
        crit_report["D_B_claude_fs"] = {
            fs: {k: v for k, v in d_b[fs].items() if k != "per_poem"} for fs in FS_SETS
        }
        crit_report["D_B_claude_fs_summary"] = {
            "mean_f1": sum(d_b_f1s) / len(d_b_f1s), "min_f1": min(d_b_f1s), "max_f1": max(d_b_f1s),
            "range_sets": [FS_SETS[d_b_f1s.index(min(d_b_f1s))], FS_SETS[d_b_f1s.index(max(d_b_f1s))]],
        }

        # D_C: GPT-Z combined with Claude-FS(set), OR and AND, every set
        d_c = {}
        for fs in FS_SETS:
            voter_a, voter_b = ("Z", "openai"), (fs, "anthropic")
            d_c[fs] = {}
            for rule in ("or", "and"):
                d_c[fs][rule] = score_set(cache, pool, gt_cache, _two, criterion,
                                           voter_a=voter_a, voter_b=voter_b, rule=rule)
        crit_report["D_C_gptz_claudefs"] = {
            fs: {rule: {k: v for k, v in d_c[fs][rule].items() if k != "per_poem"}
                 for rule in ("or", "and")}
            for fs in FS_SETS
        }

        # D_D: 3-model design, 2-of-3 majority. Variant 1: GPT Z + Claude FS + Gemini FS (same set).
        # Variant 2: GPT Z + Claude FS + Gemini Z.
        d_d = {}
        for fs in FS_SETS:
            voters_gfs = [("Z", "openai"), (fs, "anthropic"), (fs, "google")]
            voters_gz = [("Z", "openai"), (fs, "anthropic"), ("Z", "google")]
            d_d[fs] = {
                "gemini_fs": score_set(cache, pool, gt_cache, _three, criterion, voter_specs=voters_gfs),
                "gemini_z": score_set(cache, pool, gt_cache, _three, criterion, voter_specs=voters_gz),
            }
        crit_report["D_D_3model_majority"] = {
            fs: {variant: {k: v for k, v in d_d[fs][variant].items() if k != "per_poem"}
                 for variant in ("gemini_fs", "gemini_z")}
            for fs in FS_SETS
        }

        # D_E: GPT-Z + Gemini-FS, and Claude-FS + Gemini-FS, every set, OR/AND
        d_e = {}
        for fs in FS_SETS:
            d_e[fs] = {"gptz_geminifs": {}, "claudefs_geminifs": {}}
            for rule in ("or", "and"):
                d_e[fs]["gptz_geminifs"][rule] = score_set(
                    cache, pool, gt_cache, _two, criterion,
                    voter_a=("Z", "openai"), voter_b=(fs, "google"), rule=rule)
                d_e[fs]["claudefs_geminifs"][rule] = score_set(
                    cache, pool, gt_cache, _two, criterion,
                    voter_a=(fs, "anthropic"), voter_b=(fs, "google"), rule=rule)
        crit_report["D_E_pairs"] = {
            fs: {
                pair: {rule: {k: v for k, v in d_e[fs][pair][rule].items() if k != "per_poem"}
                       for rule in ("or", "and")}
                for pair in ("gptz_geminifs", "claudefs_geminifs")
            }
            for fs in FS_SETS
        }

        # Leave-one-out, per FS set, with bootstrap CI vs. the best 2-model alternative
        loo = {}
        for fs in FS_SETS:
            ens = d_d[fs]["gemini_fs"]
            ens_f1 = ens["overall"]["f1"]

            best_no_gemini_rule = max(("or", "and"), key=lambda r: d_c[fs][r]["overall"]["f1"])
            best_no_gemini = d_c[fs][best_no_gemini_rule]
            marg_gemini = bootstrap_pair(ens["per_poem"], best_no_gemini["per_poem"])

            best_no_claude_rule = max(("or", "and"),
                                       key=lambda r: d_e[fs]["gptz_geminifs"][r]["overall"]["f1"])
            best_no_claude = d_e[fs]["gptz_geminifs"][best_no_claude_rule]
            marg_claude = bootstrap_pair(ens["per_poem"], best_no_claude["per_poem"])

            best_no_gpt_rule = max(("or", "and"),
                                    key=lambda r: d_e[fs]["claudefs_geminifs"][r]["overall"]["f1"])
            best_no_gpt = d_e[fs]["claudefs_geminifs"][best_no_gpt_rule]
            marg_gpt = bootstrap_pair(ens["per_poem"], best_no_gpt["per_poem"])

            loo[fs] = {
                "ensemble_f1": ens_f1,
                "best_2_without_gemini": {"rule": best_no_gemini_rule,
                                           "f1": best_no_gemini["overall"]["f1"]},
                "marginal_gemini_f1": marg_gemini,
                "best_2_without_claude": {"rule": best_no_claude_rule,
                                           "f1": best_no_claude["overall"]["f1"]},
                "marginal_claude_f1": marg_claude,
                "best_2_without_gpt": {"rule": best_no_gpt_rule, "f1": best_no_gpt["overall"]["f1"]},
                "marginal_gpt_f1": marg_gpt,
            }
        crit_report["leave_one_out"] = loo

        report["criteria"][criterion] = crit_report

    # Agreement matrix: GPT-Z vs Claude-FS, every FS set (verse-level existence only)
    report["agreement_gptz_vs_claudefs"] = {}
    for fs in FS_SETS:
        report["agreement_gptz_vs_claudefs"][fs] = agreement_matrix(
            cache, pool, gt_cache, ("Z", "openai"), (fs, "anthropic"))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "analysis_report_design_choice.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- console summary ----
    print(f"Manifest: {len(manifest)} records. Cumulative spend: ${spend['_total']:.4f}")
    print(f"\n{'=' * 78}\nD_A (GPT-Z alone), D_B (Claude-FS alone) -- verse-primary\n{'=' * 78}")
    v = report["criteria"]["verse"]
    print(f"  D_A GPT-Z: F1={v['D_A_gpt_z']['overall']['f1']:.3f}")
    for fs in FS_SETS:
        print(f"  D_B Claude-FS[{fs}]: F1={v['D_B_claude_fs'][fs]['overall']['f1']:.3f}")
    summ = v["D_B_claude_fs_summary"]
    print(f"  D_B mean={summ['mean_f1']:.3f} range=[{summ['min_f1']:.3f},{summ['max_f1']:.3f}] "
          f"({summ['range_sets']})")

    print(f"\n{'=' * 78}\nD_C (GPT-Z + Claude-FS[set], OR/AND) -- verse-primary\n{'=' * 78}")
    for fs in FS_SETS:
        orr = v["D_C_gptz_claudefs"][fs]["or"]["overall"]["f1"]
        andd = v["D_C_gptz_claudefs"][fs]["and"]["overall"]["f1"]
        print(f"  set {fs}: OR F1={orr:.3f}  AND F1={andd:.3f}")

    print(f"\n{'=' * 78}\nD_D (3-model 2-of-3 majority) -- verse-primary\n{'=' * 78}")
    for fs in FS_SETS:
        gfs = v["D_D_3model_majority"][fs]["gemini_fs"]["overall"]["f1"]
        gz = v["D_D_3model_majority"][fs]["gemini_z"]["overall"]["f1"]
        print(f"  set {fs}: Gemini-FS variant F1={gfs:.3f}  Gemini-Z variant F1={gz:.3f}")

    print(f"\n{'=' * 78}\nLeave-one-out marginal F1 contribution (verse-primary)\n{'=' * 78}")
    for fs in FS_SETS:
        loo = v["leave_one_out"][fs]
        mg, mc, mp = loo["marginal_gemini_f1"]["f1"], loo["marginal_claude_f1"]["f1"], loo["marginal_gpt_f1"]["f1"]
        print(f"  set {fs}: ensemble F1={loo['ensemble_f1']:.3f}  "
              f"marg_Gemini={mg['point']:+.4f}({'SIG' if mg['sig'] else 'ns'})  "
              f"marg_Claude={mc['point']:+.4f}({'SIG' if mc['sig'] else 'ns'})  "
              f"marg_GPT={mp['point']:+.4f}({'SIG' if mp['sig'] else 'ns'})")

    print(f"\n{'=' * 78}\nAgreement: GPT-Z vs Claude-FS[{PRODUCTION_FS_SET}]\n{'=' * 78}")
    agr = report["agreement_gptz_vs_claudefs"][PRODUCTION_FS_SET]
    for bucket in ("both", "a_only", "b_only", "none"):
        b = agr[bucket]
        print(f"  {bucket:8s}: n={b['n']:4d} GT-pos-rate={b['gt_positive_rate']:.3f} "
              f"accuracy={b['accuracy']:.3f}")

    print(f"\nDone. Full report: {OUT_DIR / 'analysis_report_design_choice.json'}")


if __name__ == "__main__":
    main()
