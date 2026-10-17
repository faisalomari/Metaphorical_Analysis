"""Section 5: signal hypothesis. For the easy-for-LLM targets (تشبيه مطول,
استعارة تمثيلية): top TF-IDF features, top-15 TP/FN verses by model
probability (verse text + annotation span + subtype), explicit-marker check
(كأن/مثل/كـ...) for تشبيه مطول, pairwise positive-verse overlap between all
5 targets, and a label-noise indicator (same exact span_text annotated with
>1 distinct subtype somewhere in the corpus). No training; reads existing
results/phase5_local_ft/raw/*.json + data/ali_poems/poems/*.json only.
"""
import json
import re
from collections import defaultdict

from common import (ANALYSIS_OUT, TARGETS_BY_LEVEL, get_poem, load_run,
                     split_poem_ids)
from data_io import list_poem_files, load_poem, positive_verses_by_subtype
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

SIGNAL_TARGETS = ["very_easy", "easy"]
MODEL_KEY = "marbert"
SPLIT_NAME = "S2"
SEED = 0

SIMILE_MARKERS = ["كأنّ", "كأن", "مثل", "كما", "شبه", "تشبه"]
# leading-kaf-of-comparison (كـ + word) is notoriously hard to regex cleanly (kaf is also a
# common root letter); flagged as a heuristic, not a clean lexical check.


def verse_text(poem, verse_no):
    for v in poem["verses"]:
        if v["verse_index"] == verse_no:
            return v["text"]
    return None


def annotations_for_verse(poem, verse_no, subtype=None):
    out = []
    n_verses = poem["verse_count"]
    for a in poem.get("annotations", []):
        try:
            vn = int(str(a["verse_index"]).split(",")[0])
        except (ValueError, KeyError):
            continue
        if vn != verse_no or not (1 <= vn <= n_verses):
            continue
        if subtype and a.get("subtype") != subtype:
            continue
        out.append(a)
    return out


def top_tfidf_features(level, top_n=20):
    target_value = TARGETS_BY_LEVEL[level]["value"]
    ids = split_poem_ids(SPLIT_NAME, SEED)
    from dataset import build_examples
    train_ex = build_examples(ids["train"], target_value)
    texts = [e["text"] for e in train_ex]
    labels = [e["label"] for e in train_ex]
    vec = TfidfVectorizer(analyzer="char", ngram_range=(2, 4), min_df=2)
    X = vec.fit_transform(texts)
    clf = LogisticRegression(class_weight="balanced", max_iter=2000)
    clf.fit(X, labels)
    feat_names = vec.get_feature_names_out()
    coefs = clf.coef_[0]
    order = coefs.argsort()[::-1]
    top_pos = [(feat_names[i], float(coefs[i])) for i in order[:top_n]]
    top_neg = [(feat_names[i], float(coefs[i])) for i in order[-top_n:]]
    return {"top_positive_ngrams": top_pos, "top_negative_ngrams": top_neg}


def top_tp_fn_examples(level, k=15):
    target_value = TARGETS_BY_LEVEL[level]["value"]
    run = load_run(level, MODEL_KEY, SPLIT_NAME, SEED)
    tp, fn = [], []
    for p in run["predictions"]:
        poem = get_poem(p["poem_id"])
        text = verse_text(poem, p["verse_no"])
        anns = annotations_for_verse(poem, p["verse_no"], subtype=target_value)
        span = anns[0]["span_text"] if anns else None
        row = {"poem_id": p["poem_id"], "verse_no": p["verse_no"], "prob": p["prob"],
               "text": text, "span_text": span, "label": p["label"], "pred": p["pred"]}
        if p["label"] == 1 and p["pred"] == 1:
            tp.append(row)
        elif p["label"] == 1 and p["pred"] == 0:
            fn.append(row)
    tp.sort(key=lambda r: -r["prob"])
    fn.sort(key=lambda r: r["prob"])  # most confidently missed first
    return tp[:k], fn[:k]


def marker_check(level):
    target_value = TARGETS_BY_LEVEL[level]["value"]
    all_poems = [load_poem(f) for f in list_poem_files()]
    pos_count = 0
    pos_with_marker = 0
    total_verses = 0
    total_with_marker = 0
    for poem in all_poems:
        pos = positive_verses_by_subtype(poem).get(target_value, set())
        for v in poem["verses"]:
            vn = v["verse_index"]
            text = v["text"]
            has_marker = any(m in text for m in SIMILE_MARKERS)
            total_verses += 1
            if has_marker:
                total_with_marker += 1
            if vn in pos:
                pos_count += 1
                if has_marker:
                    pos_with_marker += 1
    return {
        "target": target_value, "markers_checked": SIMILE_MARKERS,
        "n_positive_verses": pos_count, "n_positive_with_marker": pos_with_marker,
        "pct_positive_with_marker": pos_with_marker / pos_count if pos_count else None,
        "corpus_baseline_pct_with_marker": total_with_marker / total_verses if total_verses else None,
    }


def cooccurrence_matrix():
    all_poems = [load_poem(f) for f in list_poem_files()]
    levels = list(TARGETS_BY_LEVEL)
    pos_sets = {lvl: set() for lvl in levels}  # (poem_id, verse_no) pairs
    for poem in all_poems:
        pid = str(poem["poem_id"])
        for lvl in levels:
            tv = TARGETS_BY_LEVEL[lvl]["value"]
            for vn in positive_verses_by_subtype(poem).get(tv, set()):
                pos_sets[lvl].add((pid, vn))
    matrix = {}
    for a in levels:
        matrix[a] = {}
        for b in levels:
            if a == b or not pos_sets[a]:
                matrix[a][b] = None
                continue
            overlap = len(pos_sets[a] & pos_sets[b])
            matrix[a][b] = {"overlap": overlap, "frac_of_a": overlap / len(pos_sets[a])}
    sizes = {lvl: len(pos_sets[lvl]) for lvl in levels}
    return {"sizes": sizes, "matrix": matrix}


def label_noise_indicator():
    """Exact span_text strings annotated with >1 distinct subtype anywhere in the corpus."""
    all_poems = [load_poem(f) for f in list_poem_files()]
    span_to_subtypes = defaultdict(set)
    span_to_examples = defaultdict(list)
    for poem in all_poems:
        for a in poem.get("annotations", []):
            span = (a.get("span_text") or "").strip()
            subtype = a.get("subtype")
            if not span or not subtype or len(span) < 3:
                continue
            span_to_subtypes[span].add(subtype)
            span_to_examples[span].append((str(poem["poem_id"]), subtype, a.get("element")))
    conflicted = {span: subs for span, subs in span_to_subtypes.items() if len(subs) > 1}
    conflicted_sorted = sorted(conflicted.items(), key=lambda kv: -len(kv[1]))[:25]
    examples = [{"span_text": span, "subtypes": sorted(subs),
                 "occurrences": span_to_examples[span][:5]}
                for span, subs in conflicted_sorted]
    return {"n_unique_spans": len(span_to_subtypes), "n_conflicted_spans": len(conflicted),
            "pct_conflicted": len(conflicted) / len(span_to_subtypes) if span_to_subtypes else None,
            "top_examples": examples}


def build():
    out = {}
    md = ["## Section 5 — Signal hypothesis\n"]

    md.append("### Top TF-IDF features (char 2-4gram + LogReg, S2 seed0 train)\n")
    for level in SIGNAL_TARGETS:
        feats = top_tfidf_features(level)
        out[f"tfidf_{level}"] = feats
        md.append(f"**{level} ({TARGETS_BY_LEVEL[level]['value']})** -- top positive-coef n-grams:")
        md.append(", ".join(f"`{f}`({c:+.2f})" for f, c in feats["top_positive_ngrams"][:15]))
        md.append(f"\ntop negative-coef n-grams:")
        md.append(", ".join(f"`{f}`({c:+.2f})" for f, c in feats["top_negative_ngrams"][:15]))
        md.append("")

    md.append("\n### Top-15 TP / FN verses by MARBERT S2 seed0 probability\n")
    for level in SIGNAL_TARGETS:
        tp, fn = top_tp_fn_examples(level)
        out[f"examples_{level}"] = {"tp": tp, "fn": fn}
        md.append(f"\n**{level} ({TARGETS_BY_LEVEL[level]['value']})** -- top 15 TRUE POSITIVES (highest prob):\n")
        md.append("| poem_id | verse | prob | span_text | verse text |")
        md.append("|---|---|---|---|---|")
        for r in tp:
            md.append(f"| {r['poem_id']} | {r['verse_no']} | {r['prob']:.3f} | {r['span_text'] or '-'} | {r['text']} |")
        md.append(f"\n**{level}** -- top 15 FALSE NEGATIVES (lowest prob = most confidently missed):\n")
        md.append("| poem_id | verse | prob | span_text | verse text |")
        md.append("|---|---|---|---|---|")
        for r in fn:
            md.append(f"| {r['poem_id']} | {r['verse_no']} | {r['prob']:.3f} | {r['span_text'] or '-'} | {r['text']} |")

    md.append("\n### Explicit-marker check (تشبيه مطول)\n")
    mc = marker_check("very_easy")
    out["marker_check"] = mc
    md.append(f"Markers checked: {mc['markers_checked']}")
    md.append(f"Of {mc['n_positive_verses']} positive verses corpus-wide, "
              f"{mc['n_positive_with_marker']} ({mc['pct_positive_with_marker']*100:.1f}%) contain an explicit marker "
              f"vs. a corpus-wide baseline of {mc['corpus_baseline_pct_with_marker']*100:.1f}% of ALL verses "
              f"containing one of these markers.\n")

    md.append("\n### Target co-occurrence (corpus-wide, verse-level)\n")
    co = cooccurrence_matrix()
    out["cooccurrence"] = co
    md.append("| | " + " | ".join(co["sizes"]) + " |")
    md.append("|---|" + "---|" * len(co["sizes"]))
    for a in co["sizes"]:
        row = [a]
        for b in co["sizes"]:
            cell = co["matrix"][a][b]
            row.append("-" if cell is None else f"{cell['overlap']} ({cell['frac_of_a']*100:.0f}%)")
        md.append("| " + " | ".join(row) + " |")
    md.append(f"\n(sizes: {co['sizes']}; cell = count of A's positive verses that are ALSO positive for B, "
              f"with %% of A's own positives in parens)\n")

    md.append("\n### Label-noise indicator: same exact span_text, different subtype, anywhere in corpus\n")
    ln = label_noise_indicator()
    out["label_noise"] = ln
    md.append(f"{ln['n_conflicted_spans']} / {ln['n_unique_spans']} unique span_texts "
              f"({ln['pct_conflicted']*100:.2f}%) are annotated with more than one distinct subtype "
              f"somewhere in the 166-poem corpus. Top 10 by number of distinct subtypes:\n")
    md.append("| span_text | distinct subtypes | example (poem_id, subtype, element) |")
    md.append("|---|---|---|")
    for ex in ln["top_examples"][:10]:
        md.append(f"| {ex['span_text']} | {', '.join(ex['subtypes'])} | {ex['occurrences'][:3]} |")

    (ANALYSIS_OUT / "section5_signal.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    md_text = "\n".join(md)
    (ANALYSIS_OUT / "section5_signal.md").write_text(md_text, encoding="utf-8")
    print(md_text[:6000])


if __name__ == "__main__":
    build()
