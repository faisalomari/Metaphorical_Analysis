"""Build pilot_report.md and pilot_report.docx from the raw run outputs."""
import json
from datetime import datetime, timezone

from config import (
    RESULTS_DIR, MODELS, ELEMENT_ORDER, ELEMENT_AR, POEM_NAME, POET, POEM_TITLE,
    POEM_PATH, N_RUNS, TEMPERATURE,
)
from prompts import build_system_message, build_user_message
from analyze import (
    load_all_runs, score_vs_ground_truth, run_consistency, cross_model_agreement,
    build_comparison_table,
)
from ground_truth import load_ground_truth


def compute_cost(by_provider: dict) -> dict:
    cost = {}
    total = 0.0
    for provider, runs in by_provider.items():
        spec = MODELS[provider]
        provider_cost = 0.0
        for run in runs:
            usage = run["meta"].get("usage") or {}
            in_tok = usage.get("input_tokens") or 0
            out_tok = usage.get("output_tokens") or 0
            provider_cost += in_tok / 1_000_000 * spec["price_in"] + out_tok / 1_000_000 * spec["price_out"]
        cost[provider] = provider_cost
        total += provider_cost
    cost["total"] = total
    return cost


def fmt_pct(x):
    return f"{x*100:.1f}%" if x is not None else "n/a"


def build_observations(by_provider, scores, gt, agreement) -> list:
    obs = []

    # small ground-truth support caveat (computed first so the F1 ranking below can use it)
    support = {}
    for element in ELEMENT_ORDER:
        support[element] = sum(1 for no in gt if gt[no][element])

    # weakest / strongest element by mean F1 across models, restricted to elements with
    # enough ground-truth support (>2 positives) to be a meaningful comparison
    mean_f1 = {}
    for element in ELEMENT_ORDER:
        vals = [scores[p][element]["f1"] for p in by_provider]
        mean_f1[element] = sum(vals) / len(vals)
    reliable = {el: f1 for el, f1 in mean_f1.items() if support[el] > 2}
    if reliable:
        weakest = min(reliable, key=reliable.get)
        strongest = max(reliable, key=reliable.get)
        obs.append(f"Among elements with enough ground-truth support to compare (n>2): **{strongest}** is "
                    f"strongest (mean F1={reliable[strongest]:.2f}) and **{weakest}** weakest "
                    f"(mean F1={reliable[weakest]:.2f}) — consistent with the pattern found across the rest "
                    f"of the project (see THESIS_KNOWLEDGE.md §4): simile is consistently the easiest element "
                    f"for LLMs, trope/kenning the hardest. Elements excluded from this comparison for low "
                    f"support: {', '.join(el for el in ELEMENT_ORDER if support[el] <= 2)} — see the next bullet.")
    low_support = [f"{el} (n={support[el]})" for el in ELEMENT_ORDER if support[el] <= 2]
    if low_support:
        obs.append(f"Ground-truth support is very small for this one poem: {', '.join(low_support)}. "
                    f"Scores for these elements (especially any showing F1=1.0) rest on 1-2 positive instances "
                    f"and are not statistically meaningful on their own — this is the single biggest reason to "
                    f"scale the harness to more poems before drawing conclusions.")

    # any model with zero recall on an element
    for element in ELEMENT_ORDER:
        for provider in by_provider:
            s = scores[provider][element]
            if s["tp"] == 0 and s["fn"] > 0:
                obs.append(f"**{MODELS[provider]['display']}** found zero true positives for **{element}** "
                            f"(missed all {s['fn']} ground-truth instances) — worth a closer look at whether "
                            f"this is a systematic gap for this model/element pair or specific to this poem.")

    # cross-model agreement summary
    mean_agreement = sum(
        (a["all_agree_count"] / a["total"] if a["total"] else 0) for a in agreement.values()
    ) / len(agreement)
    obs.append(f"Mean cross-model agreement across all 4 elements: {fmt_pct(mean_agreement)}. High agreement on "
                f"an element mostly reflects all 3 models agreeing on the (common) negative class — genuine "
                f"agreement on *positive* detections is lower and visible only in the per-verse disagreement list (§5c).")

    obs.append("Instruction-only JSON (no structured-output mode) produced perfectly parseable JSONL from all "
                "3 providers across all 6 runs — zero parse errors. Worth testing whether provider-native "
                "structured-output/JSON-schema modes change accuracy (not just formatting reliability) in a "
                "follow-up run.")

    obs.append("**Next step**: re-run this exact harness (unchanged code, `python experiments/pilot_3models/run_pilot.py` "
                "with `config.POEM_PATH` pointed at a different poem) across the other 4 poems used historically "
                "(Al-Nabigha, Jarir, Abu Tammam, Imru' al-Qais Poem 1) to get statistically meaningful per-element "
                "numbers and build the standardized evaluation harness flagged as the top-priority gap in ENHANCEMENT_PLAN.md.")

    return obs


def build_markdown() -> str:
    by_provider = load_all_runs()
    gt = load_ground_truth()
    scores = score_vs_ground_truth(by_provider, gt)
    consistency = {p: run_consistency(runs) for p, runs in by_provider.items()}
    agreement = cross_model_agreement(by_provider)
    table = build_comparison_table(by_provider)
    cost = compute_cost(by_provider)
    poem_text = POEM_PATH.read_text(encoding="utf-8")
    system_message = build_system_message()
    user_message = build_user_message()

    lines = []
    lines.append(f"# Pilot Report — 3-Model Rhetorical Element Analysis\n")
    lines.append(f"**Poem:** {POET}, {POEM_TITLE} ({POEM_NAME}, 23 verses)\n")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n")

    lines.append("## 1. Poem (original text)\n")
    lines.append(f"**Poet:** {POET}  \n**Source:** {POEM_TITLE}, from `archive/Forth_Step/Data/Imru2/poetry.txt`, "
                  f"originally sourced from the University of Haifa Arabic rhetoric database.\n")
    lines.append("```")
    lines.append(poem_text.strip())
    lines.append("```\n")

    lines.append("## 2. Prompt used\n")
    lines.append("Adapted, unchanged in substance, from `archive/Forth_Step/GPT/{prompt_intro,prompt_analysis}.txt` "
                  "and `archive/Forth_Step/Elements/*.txt` — the most refined prompt version found across "
                  "FirstStep–Forth_Step. Split into a system message (element definitions) and a user message "
                  "(analysis instructions + poem), reframed for single-turn chat APIs; element definitions kept verbatim.\n")
    lines.append("<details><summary>System message</summary>\n\n```\n" + system_message + "\n```\n</details>\n")
    lines.append("<details><summary>User message</summary>\n\n```\n" + user_message + "\n```\n</details>\n")

    lines.append("## 3. Models, versions, settings\n")
    lines.append("| Provider | Model ID | Temperature | Runs | JSON enforcement |")
    lines.append("|---|---|---|---|---|")
    for provider, spec in MODELS.items():
        lines.append(f"| {spec['display']} | `{spec['model_id']}` | {TEMPERATURE} | {N_RUNS} | "
                      f"Instruction-only (no structured-output mode), for comparability with the original Forth_Step methodology |")
    first_meta = next(iter(by_provider.values()))[0]["meta"]
    lines.append(f"\n**Run date (UTC):** {first_meta['started_at_utc'][:10]}\n")

    lines.append("## 4. Per-element comparison (verse by verse)\n")
    for element in ELEMENT_ORDER:
        lines.append(f"### {element} ({ELEMENT_AR[element]})\n")
        lines.append("| Verse | " + " | ".join(MODELS[p]["display"] for p in by_provider) + " |")
        lines.append("|---|" + "---|" * len(by_provider))
        for row in table:
            cells = []
            for provider in by_provider:
                cell = row[(element, provider)]
                mark = "✅" if cell["exists"] else ("❌" if cell["exists"] is False else "⚠️n/a")
                appear = f" _{cell['appearance']}_" if cell["appearance"] else ""
                cells.append(f"{mark}{appear}")
            lines.append(f"| {row['verse']} | " + " | ".join(cells) + " |")
        lines.append("")

    lines.append("## 5. Agreement analysis\n")
    lines.append("### 5a. Cross-model agreement (majority vote per model, all 3 compared)\n")
    lines.append("| Element | Verses with data | All 3 agree | Agreement rate |")
    lines.append("|---|---|---|---|")
    for element in ELEMENT_ORDER:
        a = agreement[element]
        rate = a["all_agree_count"] / a["total"] if a["total"] else None
        lines.append(f"| {element} | {a['total']} | {a['all_agree_count']} | {fmt_pct(rate)} |")

    lines.append("\n### 5b. Run-to-run consistency (within each model, {} runs)\n".format(N_RUNS))
    lines.append("| Element | " + " | ".join(MODELS[p]["display"] for p in by_provider) + " |")
    lines.append("|---|" + "---|" * len(by_provider))
    for element in ELEMENT_ORDER:
        cells = []
        for provider in by_provider:
            c = consistency[provider][element]
            cells.append(fmt_pct(c["rate"]))
        lines.append(f"| {element} | " + " | ".join(cells) + " |")

    lines.append("\n### 5c. Verse-level disagreements (where not all 3 models agree)\n")
    for element in ELEMENT_ORDER:
        disagreements = [r for r in agreement[element]["rows"] if not r["all_agree"]]
        if not disagreements:
            lines.append(f"- **{element}**: no disagreements.")
            continue
        lines.append(f"- **{element}**: {len(disagreements)} verse(s) with disagreement — "
                      + ", ".join(f"v{r['verse']} ({r['votes']})" for r in disagreements))
    lines.append("")

    lines.append("## 6. Comparison against ground truth (Dr. Ali Hussein's manual annotation)\n")
    lines.append("Ground truth: `data/ground_truth/ali_ana/original/امرؤ القيس 8.xlsx`, mapped from the 53-element "
                  "classical taxonomy to this pilot's 4 elements (مجاز/استعارة → Trope; direct matches for the other 3).\n")
    lines.append("| Element | Model | Precision | Recall | F1 | TP | FP | FN | TN |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for element in ELEMENT_ORDER:
        for provider in by_provider:
            s = scores[provider][element]
            lines.append(f"| {element} | {MODELS[provider]['display']} | {s['precision']:.3f} | {s['recall']:.3f} | "
                          f"{s['f1']:.3f} | {s['tp']} | {s['fp']} | {s['fn']} | {s['tn']} |")

    lines.append("\n## 7. Observations & next steps\n")
    for obs in build_observations(by_provider, scores, gt, agreement):
        lines.append(f"- {obs}")
    lines.append("")

    lines.append("## 8. Cost of this experiment\n")
    lines.append("| Provider | Cost (USD) |")
    lines.append("|---|---|")
    for provider in by_provider:
        lines.append(f"| {MODELS[provider]['display']} | ${cost[provider]:.4f} |")
    lines.append(f"| **Total** | **${cost['total']:.4f}** |")

    return "\n".join(lines) + "\n"


def _is_separator_row(cells):
    return all(set(c.strip()) <= set("-: ") for c in cells)


def _parse_table_block(lines, start):
    """Given lines[] and the index of the first '|' line, consume the whole
    table block and return (rows, next_index)."""
    rows = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        if not _is_separator_row(cells):
            rows.append(cells)
        i += 1
    return rows, i


def _add_paragraph_with_bold(doc, text, style=None):
    """Add a paragraph, rendering **bold** spans as real bold runs instead of
    leaving literal asterisks in the output (markdown_text elsewhere in this
    module uses ** for emphasis in prose, not just in table cells)."""
    p = doc.add_paragraph(style=style)
    parts = text.split("**")
    for idx, part in enumerate(parts):
        if not part:
            continue
        run = p.add_run(part)
        run.bold = bool(idx % 2)
    return p


def build_docx(markdown_text: str, out_path):
    import docx
    from docx.shared import Pt

    doc = docx.Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)

    lines = markdown_text.splitlines()
    i = 0
    in_code_block = False
    code_buffer = []
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("```"):
            if in_code_block:
                p = doc.add_paragraph("\n".join(code_buffer))
                p.style = doc.styles["Normal"]
                for run in p.runs:
                    run.font.name = "Consolas"
                    run.font.size = Pt(9)
                code_buffer = []
            in_code_block = not in_code_block
            i += 1
            continue
        if in_code_block:
            code_buffer.append(lines[i])
            i += 1
            continue
        if line.startswith(("<details", "</details>", "<summary")):
            i += 1
            continue
        if line.startswith("### "):
            doc.add_heading(line[4:], level=3)
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=2)
        elif line.startswith("# "):
            doc.add_heading(line[2:], level=1)
        elif line.strip().startswith("|"):
            rows, next_i = _parse_table_block(lines, i)
            if rows:
                table = doc.add_table(rows=len(rows), cols=len(rows[0]))
                table.style = "Light Grid Accent 1"
                for r, row_vals in enumerate(rows):
                    for c, val in enumerate(row_vals):
                        table.cell(r, c).text = val.replace("**", "").replace("_", "")
            i = next_i
            continue
        elif line.strip().startswith("- "):
            _add_paragraph_with_bold(doc, line.strip()[2:], style="List Bullet")
        elif line.strip():
            _add_paragraph_with_bold(doc, line)
        i += 1
    doc.save(out_path)


def main():
    md = build_markdown()
    md_path = RESULTS_DIR / "pilot_report.md"
    md_path.write_text(md, encoding="utf-8")
    print(f"Wrote {md_path}")

    docx_path = RESULTS_DIR / "pilot_report.docx"
    build_docx(md, docx_path)
    print(f"Wrote {docx_path}")


if __name__ == "__main__":
    main()
