"""Task 2 (2026-07-26 session) - recall/FN decomposition over the frozen TEST
results (v4_combined, strict criterion, 2-run majority).

Zero new API calls: reconstructs per-instance TP/FP/FN classifications from
results/pilot_3models/test_final/v4_combined/ (already-collected raw model
output) plus Dr. Ali Hussein's ground truth, using the existing scoring
primitives (span_scoring.majority_exists_and_appearance, span_matching) so the
totals reproduce PROJECT_STATE.md SS3a's frozen TP/FP/FN table exactly before
any decomposition is layered on top.

Bucket priority (an FN instance gets exactly one bucket - first match wins),
per the 2026-07-26 session's explicit sign-off:
  (b)  schema-structural   - objective: k-1 of any k>=2 same-verse-element GT
                              group are a hard schema ceiling, independent of
                              model quality (prompts.py's schema allows one
                              appearance string per element per verse).
  (c)  subtype-knowledge   - GT secondary label contains مجاز مرسل or
                              استعارة قديمة ("similar lexicalized" per §3c).
  (d1) boundary-confusion  - MECHANICAL scan: this FN's GT span token-overlaps
                              a same-verse/same-provider FP span from the
                              OTHER element of the Trope<->Kenning pair.
  (d2) annotation-sensitive - ONLY the 6 already-vetted TEST verses from
                              ali_adjudication_shortlist.md. Never auto-tagged
                              beyond that list - deciding an annotation is
                              questionable is Dr. Hussein's call, not ours.
  (e)  model-capability    - Trope only, subtype استعارة فعل or مجاز عقلي:
                              §3c/§3i show Config A (same strict format,
                              stronger model) already improves these WITHOUT
                              a format change - a model-tier story.
  (a)  format-suppression  - Kenning only: the only element where the DEV
                              evidence shows the specific "Config A static/
                              worse, Config C dramatically better" pattern
                              (Imru2 v6 anchor; Imru2-only Existing=0.111,
                              Config A=0.095, Config C=0.316). Trope's DEV
                              gain came via Config A (model effect), which is
                              why Trope routes to (e), not (a), per the
                              2026-07-26 sign-off.
  unclassified              - everything else (mostly Simile/Antonymy, plus
                              residual Trope subtypes with no DEV evidence
                              either way: استعارة تمثيلية, استعارة حديثة).

CAVEAT stated throughout the output: (e) and (a) are DEV-pattern projections
onto TEST instances - inferences, not observations. Config A/B/C were never
run on Imru1/Jarir/Abu_Tammam and, per standing TEST discipline, never will
be. (b)/(c)/(d1)/(d2) are the only buckets computed from TEST data itself.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "pilot_3models"))

from config import POEMS, TEST_POEMS, RESULTS_DIR as PILOT_RESULTS
from ground_truth import load_ground_truth_spans
from analyze import load_all_runs, prf1
from span_scoring import majority_exists_and_appearance
from span_matching import best_match, token_match

OUT_MD = ROOT / "results" / "phase2_chatlike" / "recall_decomposition.md"

V4_DIR = PILOT_RESULTS / "test_final" / "v4_combined"
PROVIDERS = ["anthropic", "openai", "google"]
PROVIDER_DISPLAY = {"anthropic": "Claude Sonnet 4.6", "openai": "GPT-5.4-mini", "google": "Gemini 3.5 Flash"}
ELEMENT_ORDER = ["Trope", "Simile", "Kenning", "Antonymy"]
ELEMENT_DISPLAY = {"Trope": "Trope (مجاز)", "Simile": "Simile (تشبيه)",
                   "Kenning": "Periphrasis (كناية)", "Antonymy": "Antithesis (طباق)"}

CENTONYMY_LEXICALIZED = ["مجاز مرسل", "استعارة قديمة"]
CAP_SUBTYPES = ["استعارة فعل", "مجاز عقلي"]

# ali_adjudication_shortlist.md, TEST-poem rows only (# refers to that file's row numbering).
SHORTLIST_TEST = [
    {"shortlist_no": 4, "poem": "Imru1", "verse": 2, "element": "Kenning",
     "note": "all 3 models miss both wind-name instances"},
    {"shortlist_no": 5, "poem": "Imru1", "verse": 4, "element": "Kenning",
     "note": "all 3 models miss"},
    {"shortlist_no": 6, "poem": "Imru1", "verse": 25, "element": "Kenning",
     "note": "this couplet is also data/elements/Simile.txt's canonical Simile example #1 - Kenning/Simile adjacency, flagged for Dr. Hussein"},
    {"shortlist_no": 10, "poem": "Imru1", "verse": 43, "element": "Trope",
     "note": "cross-model disagreement (FP/FN/TP across the 3 models on the same verse)"},
    {"shortlist_no": 11, "poem": "Imru1", "verse": 45, "element": "Trope",
     "note": "cross-model disagreement, two GT instances"},
    {"shortlist_no": 12, "poem": "Imru1", "verse": 34, "element": "Trope",
     "note": "cross-model disagreement, two GT instances (Claude alone caught one)"},
]
SHORTLIST_LOOKUP = {(s["poem"], s["verse"], s["element"]) for s in SHORTLIST_TEST}

# Full ali_adjudication_shortlist.md, ALL 13 rows (including the FP-direction Antonymy
# group and the DEV-poem Kenning row), used only to avoid re-proposing an already-known
# item in scan_shared_fp_candidates - NOT used for (d2) FN classification above.
ALL_SHORTLIST_LOOKUP = SHORTLIST_LOOKUP | {
    ("Jarir", 37, "Antonymy"), ("Abu_Tammam", 16, "Antonymy"), ("Nabigha", 48, "Antonymy"),
    ("Imru2", 6, "Kenning"),
}


def build_verse_element_info(poem_key, by_provider, gt_spans):
    """Returns info[provider][verse_no][element] = {
        'exists', 'appearance', 'matched_gt_idx' (or None), 'is_fp' (bool)
    }"""
    n_verses = POEMS[poem_key]["n_verses"]
    info = {p: defaultdict(dict) for p in PROVIDERS}
    for provider in PROVIDERS:
        runs = by_provider[provider]
        for verse_no in range(1, n_verses + 1):
            for element in ELEMENT_ORDER:
                exists, appearance = majority_exists_and_appearance(runs, element, verse_no)
                gt_instances = gt_spans[verse_no][element]
                gt_texts = [g["span"] for g in gt_instances]
                matched_idx, is_fp = None, False
                if exists:
                    if not gt_texts:
                        is_fp = True
                    else:
                        matched_idx = best_match(appearance or "", gt_texts, "strict")
                        if matched_idx is None:
                            is_fp = True
                info[provider][verse_no][element] = {
                    "exists": exists, "appearance": appearance,
                    "matched_gt_idx": matched_idx, "is_fp": is_fp,
                }
    return info


def collect_fn_events(poem_key, by_provider, gt_spans, info):
    """Returns list of FN event dicts: one per (provider, verse, element, gt-instance-index)
    where that GT instance was NOT the matched one for that provider (or exists=False)."""
    n_verses = POEMS[poem_key]["n_verses"]
    events = []
    for provider in PROVIDERS:
        for verse_no in range(1, n_verses + 1):
            for element in ELEMENT_ORDER:
                v = info[provider][verse_no][element]
                if v["exists"] is None:
                    continue  # unparseable, excluded from scoring exactly like span_scoring.py
                gt_instances = gt_spans[verse_no][element]
                if not gt_instances:
                    continue
                for gi, inst in enumerate(gt_instances):
                    if v["exists"] and v["matched_gt_idx"] == gi:
                        continue  # this one was the TP
                    events.append({
                        "poem": poem_key, "provider": provider, "verse": verse_no,
                        "element": element, "gt_index": gi, "span": inst["span"],
                        "primary": inst["primary"], "secondary": inst["secondary"],
                        "group_size": len(gt_instances),
                    })
    return events


def sanity_check_totals(poem_results):
    """Reproduce PROJECT_STATE.md §3a's pooled TP/FP/FN per element/provider from
    our own info[] reconstruction, as a check that nothing was mis-wired."""
    totals = defaultdict(lambda: defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0}))
    for poem_key, (by_provider, gt_spans, info) in poem_results.items():
        n_verses = POEMS[poem_key]["n_verses"]
        for provider in PROVIDERS:
            for element in ELEMENT_ORDER:
                tp = fp = fn = 0
                for verse_no in range(1, n_verses + 1):
                    v = info[provider][verse_no][element]
                    gt_instances = gt_spans[verse_no][element]
                    if v["exists"] is None:
                        continue
                    if not v["exists"]:
                        fn += len(gt_instances)
                        continue
                    if not gt_instances:
                        fp += 1
                        continue
                    if v["matched_gt_idx"] is None:
                        fp += 1
                        fn += len(gt_instances)
                    else:
                        tp += 1
                        fn += len(gt_instances) - 1
                totals[element][provider]["tp"] += tp
                totals[element][provider]["fp"] += fp
                totals[element][provider]["fn"] += fn
    return totals


def other_element(element):
    return {"Trope": "Kenning", "Kenning": "Trope"}.get(element)


def classify(events, info_by_poem):
    # --- (b) schema-structural: within each (poem,verse,element,provider) group
    # with k>=2 GT instances, cap (k-1) of the FN events there as schema-structural,
    # leaving open (preferentially) whichever instance(s) already qualify for a more
    # specific tag (c/d1/d2/e/a), computed first below.
    by_group = defaultdict(list)
    for ev in events:
        by_group[(ev["poem"], ev["verse"], ev["element"], ev["provider"])].append(ev)

    # Precompute content-based candidate tags for every FN event (independent of b).
    for ev in events:
        ev["candidate_c"] = None
        for lex in CENTONYMY_LEXICALIZED:
            if lex in ev["secondary"] or lex in ev["primary"]:
                ev["candidate_c"] = lex
                break
        ev["candidate_d1"] = None
        other = other_element(ev["element"])
        if other:
            other_info = info_by_poem[ev["poem"]][ev["provider"]][ev["verse"]][other]
            if other_info["is_fp"] and other_info["appearance"] and token_match(other_info["appearance"], ev["span"]):
                ev["candidate_d1"] = other_info["appearance"]
        ev["candidate_d2"] = SHORTLIST_LOOKUP.__contains__((ev["poem"], ev["verse"], ev["element"]))
        ev["candidate_e"] = ev["element"] == "Trope" and any(s in ev["secondary"] for s in CAP_SUBTYPES)
        ev["candidate_a"] = ev["element"] == "Kenning"

    for key, group_events in by_group.items():
        k = group_events[0]["group_size"]
        if k < 2:
            continue
        n_fn_here = len(group_events)  # k if total miss, k-1 if 1 was matched (TP)
        n_open = max(0, n_fn_here - (k - 1))  # 1 if total miss, 0 if partial match
        # Rank: keep open the ones with the strongest candidate tag; cap the rest as (b).
        def specificity(ev):
            if ev["candidate_c"]:
                return 4
            if ev["candidate_d1"]:
                return 3
            if ev["candidate_d2"]:
                return 2
            if ev["candidate_e"] or ev["candidate_a"]:
                return 1
            return 0
        ordered = sorted(group_events, key=specificity, reverse=True)
        for ev in ordered[:n_open]:
            ev["bucket"] = None  # left open, evaluated below
        for ev in ordered[n_open:]:
            ev["bucket"] = "b"
            ev["evidence"] = f"schema-structural: verse has {k} GT {ev['element']} instances, schema allows 1 appearance/element/verse"

    # Final pass: for every event not already capped as (b), apply c -> d1 -> d2 -> e -> a -> unclassified.
    for ev in events:
        if ev.get("bucket"):
            continue
        if ev["candidate_c"]:
            ev["bucket"] = "c"
            ev["evidence"] = f"GT secondary label contains '{ev['candidate_c']}' (§3c: flat/near-flat under every Phase 1 intervention)"
        elif ev["candidate_d1"]:
            ev["bucket"] = "d1"
            ev["evidence"] = (f"{ev['provider']}'s {other_element(ev['element'])} prediction "
                               f"«{ev['candidate_d1']}» in the same verse is an FP that token-overlaps this GT span "
                               f"- mechanical Trope<->Kenning boundary-confusion signature")
        elif ev["candidate_d2"]:
            entry = next(s for s in SHORTLIST_TEST if (s["poem"], s["verse"], s["element"]) == (ev["poem"], ev["verse"], ev["element"]))
            ev["bucket"] = "d2"
            ev["evidence"] = f"ali_adjudication_shortlist.md #{entry['shortlist_no']}: {entry['note']}"
        elif ev["candidate_e"]:
            ev["bucket"] = "e"
            ev["evidence"] = (f"subtype {ev['secondary']}: pooled-DEV Config A (same strict format, Fable 5) moved Trope "
                               f"0.059->0.200 with NO precision cost (§3i q1) - model-tier, not format, DEV-inferred")
        elif ev["candidate_a"]:
            ev["bucket"] = "a"
            ev["evidence"] = ("Kenning: Imru2 v6 anchor pattern (Config A F1=0.095, static/worse; Config C F1=0.316, "
                               "catches it in both runs) - format-specific, DEV-inferred, never verified on this TEST instance")
        else:
            ev["bucket"] = "unclassified"
            ev["evidence"] = "no b/c/d1/d2/e/a criterion matched"

    return events


def scan_shared_fp_candidates(poem_results):
    """Bonus scan (not part of the FN decomposition): verses where all 3 providers
    agree on an FP for the same element - a signature that MAY indicate an
    annotation gap (the Jarir v37 pattern), listed separately as proposed
    additions to Ali's shortlist. NOT auto-classified into (d2)."""
    proposals = []
    for poem_key, (by_provider, gt_spans, info) in poem_results.items():
        n_verses = POEMS[poem_key]["n_verses"]
        for verse_no in range(1, n_verses + 1):
            for element in ELEMENT_ORDER:
                if (poem_key, verse_no, element) in ALL_SHORTLIST_LOOKUP:
                    continue
                fps = []
                for provider in PROVIDERS:
                    v = info[provider][verse_no][element]
                    if v["exists"] and v["is_fp"]:
                        fps.append((provider, v["appearance"]))
                if len(fps) == 3:
                    spans = [a for _, a in fps]
                    mutually_overlap = all(token_match(spans[i], spans[j])
                                            for i in range(3) for j in range(i + 1, 3))
                    if mutually_overlap:
                        proposals.append({"poem": poem_key, "verse": verse_no, "element": element, "fps": fps})
    return proposals


def main():
    poem_results = {}
    for poem_key in TEST_POEMS:
        gt_spans = load_ground_truth_spans(poem_key)
        by_provider = load_all_runs(V4_DIR / poem_key)
        info = build_verse_element_info(poem_key, by_provider, gt_spans)
        poem_results[poem_key] = (by_provider, gt_spans, info)

    totals = sanity_check_totals(poem_results)
    print("=== Sanity check: reconstructed pooled TP/FP/FN vs PROJECT_STATE §3a ===")
    for element in ELEMENT_ORDER:
        for provider in PROVIDERS:
            t = totals[element][provider]
            print(f"{element:10s} {provider:10s} TP={t['tp']:3d} FP={t['fp']:3d} FN={t['fn']:3d}")

    all_events = []
    for poem_key, (by_provider, gt_spans, info) in poem_results.items():
        events = collect_fn_events(poem_key, by_provider, gt_spans, info)
        all_events.extend(events)

    classify(all_events, {pk: poem_results[pk][2] for pk in poem_results})

    proposals = scan_shared_fp_candidates(poem_results)

    with open(ROOT / "results" / "phase2_chatlike" / "recall_decomposition_events.json", "w", encoding="utf-8") as f:
        json.dump({"events": all_events, "proposals": proposals}, f, ensure_ascii=False, indent=2)

    print(f"\nTotal FN events classified: {len(all_events)}")
    bucket_counts = Counter(ev["bucket"] for ev in all_events)
    for b, c in bucket_counts.most_common():
        print(b, c)

    print("\n=== Per-element bucket breakdown ===")
    per_element = defaultdict(Counter)
    for ev in all_events:
        per_element[ev["element"]][ev["bucket"]] += 1
    bucket_order = ["b", "c", "d1", "d2", "e", "a", "unclassified"]
    for element in ELEMENT_ORDER:
        total = sum(per_element[element].values())
        print(f"\n{element} (n={total}):")
        for b in bucket_order:
            n = per_element[element][b]
            if n:
                print(f"  {b:14s} {n:4d}  ({100*n/total:.1f}%)")

    print(f"\nShared-FP shortlist proposals found: {len(proposals)}")
    for p in proposals:
        print(p)


if __name__ == "__main__":
    main()
