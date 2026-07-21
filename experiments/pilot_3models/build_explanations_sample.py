"""Supervisor deliverable 2: explanations_sample.docx - illustrative only,
NOT part of the frozen evaluation. Imru2, v4_combined system message
unchanged, 1 run per model, with a required Arabic "reason" field added to
the schema (see explanation_prompt.py). Reasons are reproduced verbatim -
no paraphrasing, translation, or cleanup - so circular/wrong reasoning is
visible exactly as the model produced it.
"""
import json
import re

from config import ELEMENT_ORDER, ELEMENT_AR, MODELS, RESULTS_DIR, POEMS
from analyze import load_all_runs, per_verse_majority
from ground_truth import load_ground_truth_spans
from span_matching import best_match
from build_detailed_results import get_verse_texts, VERDICT_COLOR, VERDICT_LABEL

SAMPLE_DIR = RESULTS_DIR / "explanations_sample" / "Imru2"
FENCE_RE = re.compile(r"^```(?:json|jsonl)?\s*|\s*```$", re.MULTILINE)


def parse_with_reason(raw_text: str) -> dict:
    """Dedicated one-off parser for this run's extended schema (exists +
    appearance + reason per element). Not part of parsing.py since this
    data is never scored/majority-voted into the main harness."""
    cleaned = FENCE_RE.sub("", raw_text.strip()).strip()
    verses = {}
    for line in cleaned.splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        no = obj["no"]
        entry = {}
        for element in ELEMENT_ORDER:
            ar = ELEMENT_AR[element]
            entry[element] = {
                "exists": bool(obj.get(f"{ar}_exists")),
                "appearance": obj.get(f"{ar}_appearance"),
                "reason": obj.get(f"{ar}_reason"),
            }
        verses[no] = entry
    return verses


def load_sample() -> dict:
    manifest = json.loads((SAMPLE_DIR / "run_manifest.json").read_text(encoding="utf-8"))
    by_provider = {}
    for rec in manifest:
        raw = (SAMPLE_DIR / rec["raw_text_file"]).read_text(encoding="utf-8")
        by_provider[rec["provider"]] = parse_with_reason(raw)
    return by_provider


def classify(exists, appearance, gt_texts):
    if not exists:
        return "FN" if gt_texts else "TN"
    if not gt_texts:
        return "FP"
    match_idx = best_match(appearance or "", gt_texts, "strict", 0.5)
    return "FP" if match_idx is None else "TP"


def sanity_check_flips(by_provider_sample: dict) -> dict:
    """Compares this 1-run reason-augmented decision against the existing
    2-run-majority v4_combined decision on the same poem, per verse+element,
    counting how many decisions flip (exists differs)."""
    v4_by_provider = load_all_runs(RESULTS_DIR / "dev_variants" / "v4_combined" / "Imru2")
    n_verses = POEMS["Imru2"]["n_verses"]
    flips = {}
    for provider in by_provider_sample:
        n_flip = 0
        n_compared = 0
        flip_details = []
        for element in ELEMENT_ORDER:
            for verse_no in range(1, n_verses + 1):
                baseline = per_verse_majority(v4_by_provider[provider], element, verse_no)
                sample_verse = by_provider_sample[provider].get(verse_no)
                if baseline is None or sample_verse is None:
                    continue
                sample_exists = sample_verse[element]["exists"]
                n_compared += 1
                if sample_exists != baseline:
                    n_flip += 1
                    flip_details.append((verse_no, element, baseline, sample_exists))
        n_false_to_true = sum(1 for d in flip_details if d[2] is False and d[3] is True)
        n_true_to_false = sum(1 for d in flip_details if d[2] is True and d[3] is False)
        flips[provider] = {
            "n_flip": n_flip, "n_compared": n_compared, "details": flip_details,
            "n_false_to_true": n_false_to_true, "n_true_to_false": n_true_to_false,
        }
    return flips


def build_docx(out_path):
    import docx
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    by_provider = load_sample()
    gt_spans = load_ground_truth_spans("Imru2")
    verse_texts = get_verse_texts("Imru2")
    n_verses = POEMS["Imru2"]["n_verses"]
    flips = sanity_check_flips(by_provider)

    doc = docx.Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10)

    banner = doc.add_paragraph()
    r = banner.add_run(
        "ILLUSTRATIVE SAMPLE — explanation-augmented prompt. These outputs are NOT part of the "
        "frozen evaluation numbers. Imru2 (DEV), 1 run per model, v4_combined system message "
        "unchanged, with a required one-sentence Arabic \"reason\" field added to the output "
        "schema for positive decisions only."
    )
    r.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0xB0, 0x20, 0x20)

    doc.add_heading("Reading guide", level=2)
    doc.add_paragraph(
        "Each verse below shows ground truth alongside all 3 models' decisions for all 4 elements. "
        "Reasons are reproduced VERBATIM from the raw model output — no paraphrasing, translation, "
        "or cleanup — so circular or incorrect reasoning is visible exactly as produced. Verdicts "
        "(TP/FP/FN) are computed the same way as the main report (strict span match against ground "
        "truth); '-' means both model and ground truth agree the element is absent."
    )

    doc.add_heading("Sanity check: does adding \"explain yourself\" change decisions?", level=2)
    sc = doc.add_paragraph()
    sc.add_run(
        "Comparison: this run's single-run decisions vs. the existing 2-run-majority v4_combined "
        "decision on the same poem (92 verse×element checks per model)."
    )
    for provider, f in flips.items():
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(f"{MODELS[provider]['display']}: {f['n_flip']}/{f['n_compared']} decisions flipped "
                   f"({f['n_flip']/f['n_compared']*100:.0f}%) — "
                   f"{f['n_false_to_true']} absent→present, {f['n_true_to_false']} present→absent")
    obs = doc.add_paragraph()
    obs.add_run(
        "Observation: every flip across all 3 models went absent→present (0 present→absent in any model). "
        "Requiring a stated reason never made a model retract an existing positive call here — it only "
        "added new ones, most for GPT-5.4-mini (14/92, ~15%). This is consistent with a generative "
        "justification-seeking effect (the model finds *something* to point to once asked to explain), not "
        "a self-correction effect, and is worth flagging as a reason NOT to assume that adding an "
        "explanation requirement would improve precision — on this single-poem sample it moved only recall, "
        "in the direction of more (not necessarily correct) positive calls."
    ).italic = True

    doc.add_heading("Per-verse detail", level=1)

    providers = list(by_provider.keys())
    for verse_no in range(1, n_verses + 1):
        doc.add_heading(f"Verse {verse_no}", level=3)
        vp = doc.add_paragraph()
        vp.add_run(verse_texts.get(verse_no, ""))
        vp.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        table = doc.add_table(rows=1, cols=2 + len(providers))
        table.style = "Light Grid Accent 1"
        hdr = table.rows[0].cells
        hdr[0].text = "Element"
        hdr[1].text = "Ground truth"
        for i, provider in enumerate(providers):
            hdr[2 + i].text = MODELS[provider]["display"]

        for element in ELEMENT_ORDER:
            gt_texts = [g["span"] for g in gt_spans[verse_no][element]]
            row = table.add_row().cells
            row[0].text = f"{element} ({ELEMENT_AR[element]})"
            gtp = row[1].paragraphs[0]
            gtp.add_run("; ".join(gt_texts) if gt_texts else "-")
            gtp.alignment = WD_ALIGN_PARAGRAPH.RIGHT

            for i, provider in enumerate(providers):
                cell = row[2 + i]
                cell.text = ""
                v = by_provider[provider].get(verse_no, {}).get(element, {"exists": False, "appearance": None, "reason": None})
                verdict = classify(v["exists"], v["appearance"], gt_texts)
                p0 = cell.paragraphs[0]
                if verdict in ("TN",):
                    p0.add_run("-")
                    continue
                vr = p0.add_run(VERDICT_LABEL[verdict])
                vr.bold = True
                if verdict in VERDICT_COLOR:
                    vr.font.color.rgb = RGBColor(*VERDICT_COLOR[verdict])
                if v.get("appearance"):
                    p1 = cell.add_paragraph()
                    r1 = p1.add_run(v["appearance"])
                    r1.italic = True
                    p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                if v.get("reason"):
                    p2 = cell.add_paragraph()
                    r2 = p2.add_run(v["reason"])
                    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.save(out_path)
    print(f"Wrote {out_path}")
    return flips


if __name__ == "__main__":
    build_docx(RESULTS_DIR / "explanations_sample.docx")
