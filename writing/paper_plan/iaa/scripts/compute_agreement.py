"""Compute inter/intra-annotator agreement once two filled copies of
blind_reannotation_sample.xlsx (or an equivalent CSV) exist.

Three measures, as scoped in agreement_protocol.md §4:
  1. Cohen's kappa per element, verse-level binary presence/absence.
  2. Krippendorff's alpha per element, verse-level binary presence/absence
     (general nominal-data algorithm - reduces to a Scott's-pi-like figure
     for the 2-coder, no-missing-data case used here, which is *not*
     identical to Cohen's kappa; both are reported since they differ in how
     "chance agreement" is estimated - see the module docstring note below).
  3. Span-overlap agreement (precision/recall/F1-style, both the "strict"
     and "token" criteria already defined in
     experiments/pilot_3models/span_matching.py - reused here, not
     reimplemented) for the subset of verse x element cells where BOTH
     annotators said the element is present.

No invented numbers: everything here is computed from whatever the two
input files actually contain. Running this file directly (`python
compute_agreement.py`) runs it against the two *_FILLED.xlsx files in
sheets/ if both exist, otherwise prints a message and exits - it never
fabricates a result.
"""
import sys
from pathlib import Path

import openpyxl

from common import ELEMENT_LABELS, IAA_DIR, PILOT_DIR, POEM_AR_SHORT, config

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
import span_matching  # noqa: E402  (experiments/pilot_3models module, reused not duplicated)

YES_VALUES = {"نعم / yes", "نعم", "yes", "y", "true", "1"}


# ---------------------------------------------------------------------------
# Loading a filled annotation sheet
# ---------------------------------------------------------------------------

def load_filled_sheet(path) -> dict:
    """Returns {(poem, verse_no): {element: (exists: bool, span: str)}}.

    Expects the same column layout build_annotation_sheet.py produces:
    #, Poem, Verse No., Verse Text, then (exists, span) pairs per element in
    config.ELEMENT_ORDER, then Notes.
    """
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Annotation"]
    out = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[1] is None or row[2] is None:
            continue
        poem_label, verse_no = row[1], int(row[2])
        # Column 2 (index 1) holds the short poem label from common.POEM_AR_SHORT
        # written by build_annotation_sheet.py - unique per poem (unlike poet
        # name alone, which Imru1/Imru2 share - both are Imru' al-Qais poems).
        poem_key = next((k for k, v in POEM_AR_SHORT.items() if v == poem_label), poem_label)
        by_el = {}
        for ei, el in enumerate(config.ELEMENT_ORDER):
            exists_cell = row[4 + ei * 2]
            span_cell = row[5 + ei * 2]
            exists = str(exists_cell).strip().lower() in YES_VALUES if exists_cell else False
            by_el[el] = (exists, str(span_cell).strip() if span_cell else "")
        out[(poem_key, verse_no)] = by_el
    return out


# ---------------------------------------------------------------------------
# Agreement measures
# ---------------------------------------------------------------------------

def cohens_kappa(labels_a: list, labels_b: list) -> dict:
    """Standard 2x2 Cohen's kappa for binary labels (True/False). Returns
    kappa plus the raw confusion counts so a small denominator is visible
    (CLAUDE.md standing rule: always show raw counts alongside any derived
    statistic)."""
    assert len(labels_a) == len(labels_b)
    n = len(labels_a)
    if n == 0:
        return {"kappa": None, "n": 0}
    both_true = sum(1 for a, b in zip(labels_a, labels_b) if a and b)
    both_false = sum(1 for a, b in zip(labels_a, labels_b) if not a and not b)
    a_true_b_false = sum(1 for a, b in zip(labels_a, labels_b) if a and not b)
    a_false_b_true = sum(1 for a, b in zip(labels_a, labels_b) if not a and b)

    p_o = (both_true + both_false) / n
    p_a_true = (both_true + a_true_b_false) / n
    p_b_true = (both_true + a_false_b_true) / n
    p_e = p_a_true * p_b_true + (1 - p_a_true) * (1 - p_b_true)

    kappa = None if p_e == 1 else (p_o - p_e) / (1 - p_e)
    return {
        "kappa": kappa, "n": n, "p_o": p_o, "p_e": p_e,
        "both_true": both_true, "both_false": both_false,
        "a_true_b_false": a_true_b_false, "a_false_b_true": a_false_b_true,
    }


def krippendorff_alpha_nominal(unit_label_lists: list) -> dict:
    """General nominal-data Krippendorff's alpha. `unit_label_lists` is a
    list of per-unit label lists (one label per coder who rated that unit;
    a shorter list than the max is allowed - missing data is supported even
    though this project's 2-coder, complete-data case never needs it).

    Standard coincidence-matrix formulation (Hayes & Krippendorff 2007):
      alpha = 1 - Do/De
      Do = (sum over v != v' of n_vv') / n
      De = (sum over v != v' of n_v * n_v') / (n * (n - 1))
    where n_vv' is the pairable-value coincidence count and n_v the marginal.
    """
    from collections import defaultdict

    coincidences = defaultdict(float)
    marginals = defaultdict(float)
    n = 0.0

    for labels in unit_label_lists:
        m = len(labels)
        if m < 2:
            continue  # a unit with <2 ratings contributes no pairs
        weight = 1.0 / (m - 1)
        for i in range(m):
            for j in range(m):
                if i == j:
                    continue
                coincidences[(labels[i], labels[j])] += weight
                marginals[labels[i]] += weight
                n += weight

    if n == 0:
        return {"alpha": None, "n_pairable": 0}

    Do = sum(c for (v, v2), c in coincidences.items() if v != v2) / n
    De = sum(marginals[v] * marginals[v2] for v in marginals for v2 in marginals if v != v2) / (n * (n - 1))

    alpha = None if De == 0 else 1 - Do / De
    return {"alpha": alpha, "n_pairable": n, "Do": Do, "De": De}


def span_overlap_agreement(pairs: list, criterion: str = "strict") -> dict:
    """`pairs` is a list of (span_a, span_b) for verse x element cells where
    BOTH annotators marked the element present. Reuses
    experiments/pilot_3models/span_matching.py's symmetric match functions -
    strict_overlap and token_overlap_ratio are both symmetric in their two
    arguments, so "agreement" here does not depend on an arbitrary
    reference/prediction choice."""
    if not pairs:
        return {"n": 0, "agree": 0, "rate": None}
    if criterion == "strict":
        agree = sum(1 for a, b in pairs if span_matching.strict_overlap(a, b))
    elif criterion == "token":
        agree = sum(1 for a, b in pairs if span_matching.token_match(a, b))
    else:
        raise ValueError(criterion)
    return {"n": len(pairs), "agree": agree, "rate": agree / len(pairs)}


def span_prf1(sheet_a: dict, sheet_b: dict, criterion: str = "strict") -> dict:
    """Precision/recall/F1 per element treating sheet_a as reference,
    sheet_b as the comparison - reported alongside the raw TP/FP/FN per
    CLAUDE.md's standing rule. Because strict_overlap/token_match are
    symmetric, swapping which sheet is "reference" only relabels which
    count is called FP vs FN; it does not change which cells are judged to
    agree."""
    out = {}
    for el in config.ELEMENT_ORDER:
        tp = fp = fn = 0
        for key in sheet_a:
            if key not in sheet_b:
                continue
            exists_a, span_a = sheet_a[key][el]
            exists_b, span_b = sheet_b[key][el]
            if exists_a and exists_b:
                match = (span_matching.strict_overlap(span_a, span_b) if criterion == "strict"
                         else span_matching.token_match(span_a, span_b))
                if match:
                    tp += 1
                else:
                    fp += 1
                    fn += 1
            elif exists_a and not exists_b:
                fn += 1
            elif exists_b and not exists_a:
                fp += 1
        precision = tp / (tp + fp) if (tp + fp) else None
        recall = tp / (tp + fn) if (tp + fn) else None
        f1 = (2 * precision * recall / (precision + recall)) if precision and recall and (precision + recall) else None
        out[el] = {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}
    return out


# ---------------------------------------------------------------------------
# Full report over two filled sheets
# ---------------------------------------------------------------------------

def full_report(sheet_a: dict, sheet_b: dict) -> str:
    common_keys = sorted(set(sheet_a) & set(sheet_b))
    lines = [f"Agreement report over {len(common_keys)} verses common to both sheets", ""]

    for el in config.ELEMENT_ORDER:
        label = f"{ELEMENT_LABELS[el]['ar']} ({ELEMENT_LABELS[el]['en']})"
        labels_a = [sheet_a[k][el][0] for k in common_keys]
        labels_b = [sheet_b[k][el][0] for k in common_keys]

        k = cohens_kappa(labels_a, labels_b)
        alpha = krippendorff_alpha_nominal([[a, b] for a, b in zip(labels_a, labels_b)])

        pairs_strict = [(sheet_a[key][el][1], sheet_b[key][el][1]) for key in common_keys
                         if sheet_a[key][el][0] and sheet_b[key][el][0]]
        span_strict = span_overlap_agreement(pairs_strict, "strict")
        span_token = span_overlap_agreement(pairs_strict, "token")

        lines.append(f"## {label}")
        lines.append(f"  n={k['n']}  both_present={k['both_true']}  both_absent={k['both_false']}  "
                      f"only_A={k['a_true_b_false']}  only_B={k['a_false_b_true']}")
        lines.append(f"  Cohen's kappa = {k['kappa']:.3f}" if k["kappa"] is not None else "  Cohen's kappa = undefined (no variance)")
        lines.append(f"  Krippendorff's alpha = {alpha['alpha']:.3f}" if alpha["alpha"] is not None else "  Krippendorff's alpha = undefined")
        lines.append(f"  Span agreement (both marked present, n={span_strict['n']}): "
                      f"strict={span_strict['rate']:.3f} token={span_token['rate']:.3f}"
                      if span_strict["n"] else "  Span agreement: n=0 (no verse where both marked this element present)")
        lines.append("")

    prf_strict = span_prf1(sheet_a, sheet_b, "strict")
    lines.append("## Span-level precision/recall/F1 (A as reference, strict criterion)")
    for el in config.ELEMENT_ORDER:
        p = prf_strict[el]
        lines.append(f"  {el}: TP={p['tp']} FP={p['fp']} FN={p['fn']} "
                      f"P={p['precision']:.3f} R={p['recall']:.3f} F1={p['f1']:.3f}"
                      if p["precision"] is not None and p["recall"] is not None and p["f1"] is not None
                      else f"  {el}: TP={p['tp']} FP={p['fp']} FN={p['fn']} (P/R/F1 undefined, zero positives)")

    return "\n".join(lines)


def main():
    sheets_dir = IAA_DIR / "sheets"
    candidates = sorted(sheets_dir.glob("*_FILLED.xlsx"))
    if len(candidates) < 2:
        print("Need two filled sheets named e.g. "
              "blind_reannotation_sample_ali_run1_FILLED.xlsx and "
              "blind_reannotation_sample_ali_run2_FILLED.xlsx in sheets/ "
              "before this can compute anything real.")
        print(f"Found: {[p.name for p in candidates]}")
        print("Run `python tests/test_compute_agreement.py` to see this code "
              "exercised against dummy data instead.")
        return
    sheet_a = load_filled_sheet(candidates[0])
    sheet_b = load_filled_sheet(candidates[1])
    print(f"A = {candidates[0].name}\nB = {candidates[1].name}\n")
    print(full_report(sheet_a, sheet_b))


if __name__ == "__main__":
    main()
