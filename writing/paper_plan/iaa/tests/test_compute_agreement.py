"""Dummy-data tests for compute_agreement.py - run directly with
`python test_compute_agreement.py` (no pytest dependency assumed). Exercises
cohens_kappa, krippendorff_alpha_nominal, span_overlap_agreement and
span_prf1/full_report against synthetic data with known properties, plus a
round trip through load_filled_sheet() on a workbook this test writes and
deletes itself. No real annotation data is used or required.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from openpyxl import Workbook

import compute_agreement as ca
from common import POEM_AR_SHORT, config


def check(name, cond):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}")
    if not cond:
        raise AssertionError(name)


def test_cohens_kappa_perfect_agreement():
    labels = [True, False, True, True, False, False, True, False]
    r = ca.cohens_kappa(labels, labels)
    check("perfect agreement -> kappa == 1.0", abs(r["kappa"] - 1.0) < 1e-9)


def test_cohens_kappa_systematic_disagreement():
    a = [True, True, True, True, False, False, False, False]
    b = [False, False, False, False, True, True, True, True]
    r = ca.cohens_kappa(a, b)
    check("total disagreement -> kappa == -1.0", abs(r["kappa"] - (-1.0)) < 1e-9)


def test_cohens_kappa_matches_hand_computed_example():
    # Classic worked example: 2 raters, 50 items, p_o=0.70 overall, with
    # known marginals -> kappa should be a specific hand-computable value.
    # 20 both-yes, 15 both-no, 10 A-yes/B-no, 5 A-no/B-yes.
    a = [True] * 20 + [False] * 15 + [True] * 10 + [False] * 5
    b = [True] * 20 + [False] * 15 + [False] * 10 + [True] * 5
    r = ca.cohens_kappa(a, b)
    n = 50
    p_o = (20 + 15) / n
    p_a_true = (20 + 10) / n
    p_b_true = (20 + 5) / n
    p_e = p_a_true * p_b_true + (1 - p_a_true) * (1 - p_b_true)
    expected = (p_o - p_e) / (1 - p_e)
    check(f"hand-computed kappa matches (expected={expected:.4f}, got={r['kappa']:.4f})",
          abs(r["kappa"] - expected) < 1e-9)


def test_krippendorff_alpha_perfect_agreement():
    units = [[True, True], [False, False], [True, True], [False, False]]
    r = ca.krippendorff_alpha_nominal(units)
    check("perfect agreement -> alpha == 1.0", abs(r["alpha"] - 1.0) < 1e-9)


def test_krippendorff_alpha_chance_level_is_near_zero():
    # Balanced marginals, independent-looking assignment -> alpha near 0,
    # not exactly orthogonal to kappa's p_e logic but should land in a
    # plausible low range for a roughly-random pairing.
    units = [[True, False], [False, True], [True, False], [False, True],
             [True, True], [False, False], [True, False], [False, True]]
    r = ca.krippendorff_alpha_nominal(units)
    check(f"near-chance pairing -> alpha well below 1 (got {r['alpha']:.3f})", r["alpha"] < 0.3)


def test_krippendorff_alpha_three_coders_with_missing():
    # 3 "coders" per unit but one unit only has 2 ratings (simulates missing
    # data) - alpha should still compute without error and stay in [-1, 1].
    units = [["A", "A", "A"], ["B", "B", "A"], ["A", "B"], ["A", "A", "A"]]
    r = ca.krippendorff_alpha_nominal(units)
    check("3-coder + missing-data case computes a value in [-1, 1]", -1.0 <= r["alpha"] <= 1.0)


def test_span_overlap_agreement_strict():
    pairs = [("فُوهَا كُلَّمَا نَبَّهْتُهَا", "فُوهَا كُلَّمَا"),  # one is a substring of the other -> agree
             ("القرا", "جَزَاءِ نَاقَةِ")]  # disjoint -> disagree
    r = ca.span_overlap_agreement(pairs, "strict")
    check("span agreement: 1/2 strict matches", r["n"] == 2 and r["agree"] == 1 and abs(r["rate"] - 0.5) < 1e-9)


def test_span_prf1_symmetric_matcher_gives_sane_counts():
    sheet_a = {
        ("Imru2", 6): {el: (False, "") for el in config.ELEMENT_ORDER},
        ("Imru2", 15): {el: (False, "") for el in config.ELEMENT_ORDER},
    }
    sheet_b = {
        ("Imru2", 6): {el: (False, "") for el in config.ELEMENT_ORDER},
        ("Imru2", 15): {el: (False, "") for el in config.ELEMENT_ORDER},
    }
    sheet_a[("Imru2", 6)]["Kenning"] = (True, "فُوهَا كُلَّمَا نَبَّهْتُهَا")
    sheet_b[("Imru2", 6)]["Kenning"] = (True, "فُوهَا كُلَّمَا")  # substring -> TP
    sheet_a[("Imru2", 15)]["Trope"] = (True, "القرا")
    sheet_b[("Imru2", 15)]["Trope"] = (False, "")  # B missed it -> FN

    prf = ca.span_prf1(sheet_a, sheet_b, "strict")
    check("Kenning: 1 TP, 0 FP, 0 FN",
          prf["Kenning"]["tp"] == 1 and prf["Kenning"]["fp"] == 0 and prf["Kenning"]["fn"] == 0)
    check("Trope: 0 TP, 0 FP, 1 FN",
          prf["Trope"]["tp"] == 0 and prf["Trope"]["fp"] == 0 and prf["Trope"]["fn"] == 1)
    check("Trope precision undefined (0 positive predictions -> None, not a fabricated 0.0)",
          prf["Trope"]["precision"] is None and prf["Trope"]["f1"] is None)


def test_load_filled_sheet_round_trip():
    """Writes a minimal workbook matching build_annotation_sheet.py's column
    layout, loads it back with load_filled_sheet(), and checks the parsed
    values match what was written - catches a column-offset bug without
    needing a real filled annotation file."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Annotation"
    headers = ["#", "Poem", "Verse No.", "Verse Text"]
    for el in config.ELEMENT_ORDER:
        headers += [f"{el}-exists", f"{el}-span"]
    headers.append("Notes")
    ws.append(headers)

    poem_label = POEM_AR_SHORT["Imru2"]
    row = [1, poem_label, 6, "أَزْمَانَ فُوهَا كُلَّمَا نَبَّهْتُهَا"]
    for el in config.ELEMENT_ORDER:
        if el == "Kenning":
            row += ["نعم / Yes", "فُوهَا كُلَّمَا نَبَّهْتُهَا"]
        else:
            row += ["لا / No", ""]
    row.append("")
    ws.append(row)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "dummy_FILLED.xlsx"
        wb.save(path)
        parsed = ca.load_filled_sheet(path)

    key = ("Imru2", 6)
    check("round trip: correct key present", key in parsed)
    check("round trip: Kenning marked present with correct span",
          parsed[key]["Kenning"] == (True, "فُوهَا كُلَّمَا نَبَّهْتُهَا"))
    check("round trip: Trope marked absent",
          parsed[key]["Trope"] == (False, ""))


def main():
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} dummy-data tests passed.")


if __name__ == "__main__":
    main()
