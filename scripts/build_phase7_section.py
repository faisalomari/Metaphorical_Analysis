"""Builds the Phase 7 (subtype-level, 4 subtypes) collapsible <details>
section inserted into docs/phase4/E1_V2_REPORT.html by build_e1v2_report.py.

Standalone module (not merged into that 2664-line script's own body) so
build_e1v2_report.py only needs one import line + one insertion line added
-- additive, not an edit of any existing section's logic.

Reads (never edits):
  - results/phase7_subtypes/analysis_report_phase7.json (score_phase7.py)
  - results/phase7_subtypes/census.json / census_tashbih2.json
  - results/phase7_subtypes/dryrun_cost.json / dryrun_cost_tashbih2.json
  - experiments/phase7_subtypes/config/phase7_example_sets.json / _tashbih2.json

Reuses the same `<details>`/`.crit-toggle`/`data-criterion` HTML convention
as every other panel in that report, so the page's existing global
`toggleCriterion()` JS and CSS (defined once in build_e1v2_report.py) drive
this section's verse/strict/token toggle too -- no new CSS/JS needed.
"""
import html as htmlmod
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.pilot_3models.rtl_utils import is_majority_arabic  # noqa: E402

RESULTS_DIR = ROOT / "results" / "phase7_subtypes"
CONFIG_DIR = ROOT / "experiments" / "phase7_subtypes" / "config"

ANALYSIS_PATH = RESULTS_DIR / "analysis_report_phase7.json"
CENSUS_PATH = RESULTS_DIR / "census.json"
CENSUS_T2_PATH = RESULTS_DIR / "census_tashbih2.json"
DRYRUN_PATH = RESULTS_DIR / "dryrun_cost.json"
DRYRUN_T2_PATH = RESULTS_DIR / "dryrun_cost_tashbih2.json"
SETS_PATH = CONFIG_DIR / "phase7_example_sets.json"
SETS_T2_PATH = CONFIG_DIR / "phase7_example_sets_tashbih2.json"

ALL_SUBTYPES = ["استعارة قديمة", "كناية عن صفة", "تشبيه قصير", "تشبيه مطول"]
SUBTYPE_PARENT = {
    "استعارة قديمة": "مجاز (Trope) — الاستعارة", "كناية عن صفة": "كناية (Periphrasis)",
    "تشبيه قصير": "تشبيه (Simile)", "تشبيه مطول": "تشبيه (Simile)",
}
PROVIDERS = ["anthropic", "openai", "google"]
DISPLAY = {"anthropic": "Claude Sonnet 4.6", "openai": "GPT-5.4-mini", "google": "Gemini 3.5 Flash"}
CRITERIA = ["verse", "strict", "token"]


def esc(s) -> str:
    return htmlmod.escape(str(s), quote=True)


def rtl_wrap(text: str, css_class: str = "") -> str:
    direction = "rtl" if is_majority_arabic(text) else "ltr"
    cls = f" {css_class}" if css_class else ""
    return f'<span dir="{direction}" class="bidi{cls}">{esc(text)}</span>'


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def build_census_table(census, census_t2) -> str:
    rows = []
    for s in ALL_SUBTYPES:
        if census and s in census.get("per_subtype", {}):
            t = census["per_subtype"][s]
        elif census_t2 and s in census_t2.get("per_subtype", {}):
            t = census_t2["per_subtype"][s]
        else:
            continue
        rows.append(t)
    out = ['<table><tr><th>Subtype</th><th>Positive verses (corpus)</th><th>Poems</th><th>Poets</th>'
           '<th>Eligible example verses</th><th>Pool positives (25-poem pool)</th></tr>']
    for t in rows:
        flag = ' style="color:var(--bad);font-weight:600"' if t["positives_in_eval_pool_25"] < 30 else ""
        out.append(f'<tr><td>{rtl_wrap(t["subtype"])}</td><td>{t["positive_verses_corpus"]}</td>'
                   f'<td>{t["poems_with_positive"]}</td><td>{t["poets_with_positive"]}</td>'
                   f'<td>{t["eligible_example_verses"]}</td>'
                   f'<td{flag}>{t["positives_in_eval_pool_25"]}{" (indicative-only, n<30)" if t["positives_in_eval_pool_25"] < 30 else ""}</td></tr>')
    out.append("</table>")
    return "".join(out)


def build_example_card(subtype: str, sets_doc, sets_t2_doc) -> str:
    doc = sets_doc if (sets_doc and subtype in sets_doc.get("sets", {})) else sets_t2_doc
    if not doc or subtype not in doc.get("sets", {}):
        return ""
    s = doc["sets"][subtype]
    cards = []
    for i, ex in enumerate(s["examples"], start=2):
        ann = ex["annotations"][0]
        cards.append(f"""
<div class="example-card">
  <p><strong>Example {i}</strong> — poet: {rtl_wrap(ex['poet_name'])}, poem {esc(ex['poem_id'])}, verse {ex['verse_no']}</p>
  <p>{rtl_wrap(ex['text'])}</p>
  <p>span: {rtl_wrap('«' + ann['span'] + '»')}</p>
  <p>note: {rtl_wrap(ann['analysis'])}</p>
</div>""")
    return (f'<p>Zero-shot system tokens: {s["zero_shot_system_tokens"]} &middot; '
            f'Few-shot system tokens: {s["few_shot_system_tokens"]} &middot; seed={s["seed_used"]}, '
            f'{s["attempts"]} attempt(s)</p>' + "".join(cards))


def f1_row(label: str, c: dict) -> str:
    return (f'<tr><td>{esc(label)}</td><td>{c["tp"]}</td><td>{c["fp"]}</td><td>{c["fn"]}</td>'
            f'<td>{c["precision"]:.3f}</td><td>{c["recall"]:.3f}</td><td><strong>{c["f1"]:.3f}</strong></td></tr>')


def build_subtype_f1_table(sub_report: dict, criterion: str) -> str:
    out = ['<table><tr><th>Model/Condition</th><th>TP</th><th>FP</th><th>FN</th><th>P</th><th>R</th><th>F1</th></tr>']
    for provider in PROVIDERS:
        for condition in ["zero", "few"]:
            c = sub_report["by_model"][provider][condition][criterion]
            out.append(f1_row(f"{DISPLAY[provider]} / {condition}", c))
    for condition in ["zero", "few"]:
        c = sub_report["ensemble"][condition][criterion]
        out.append(f1_row(f"ENSEMBLE (2-of-3) / {condition}", c))
    out.append("</table>")
    return "".join(out)


def build_design_choice_table(sub_report: dict) -> str:
    dc = sub_report["design_choice"]
    out = ['<table><tr><th>Design</th><th>TP</th><th>FP</th><th>FN</th><th>P</th><th>R</th><th>F1</th></tr>']
    out.append(f1_row("GPT-Z alone", dc["gptz_alone_verse"]))
    out.append(f1_row("Claude-FS alone", dc["claudefs_alone_verse"]))
    out.append(f1_row("GPT-Z OR Claude-FS", dc["gptz_or_claudefs_verse"]))
    out.append(f1_row("GPT-Z AND Claude-FS", dc["gptz_and_claudefs_verse"]))
    ens3 = sub_report["ensemble"]["few"]["verse"]
    out.append(f1_row("3-model majority vote (few-shot)", ens3))
    out.append("</table>")
    loo = dc["gemini_leave_one_out_verse"]
    ci = loo["ci_3model_minus_loo"]["ci_95"]
    sig = "significant" if not (ci[0] <= 0 <= ci[1]) else "not significant"
    out.append(f'<p>Gemini leave-one-out (verse, few-shot): 3-model F1={loo["ensemble3_f1"]:.3f} vs '
               f'2-model (no Gemini) F1={loo["loo_2model_f1"]:.3f}; bootstrap 95% CI of the difference '
               f'= [{ci[0]:+.3f}, {ci[1]:+.3f}] ({sig}).</p>')
    return "".join(out)


def build_bootstrap_table(sub_report: dict) -> str:
    out = ['<table><tr><th>Model</th><th>Criterion</th><th>F1(few) &minus; F1(zero)</th><th>95% CI</th><th></th></tr>']
    for provider in PROVIDERS:
        for criterion in CRITERIA:
            ci = sub_report["bootstrap_few_minus_zero"][provider][criterion]
            lo, hi = ci["ci_95"]
            sig = "SIG" if not (lo <= 0 <= hi) else "ns"
            out.append(f'<tr><td>{DISPLAY[provider]}</td><td>{criterion}</td>'
                       f'<td>{ci["point"]:+.3f}</td><td>[{lo:+.3f}, {hi:+.3f}]</td><td>{sig}</td></tr>')
    out.append("</table>")
    return "".join(out)


def build_subtype_panel(subtype: str, sub_report: dict) -> str:
    toggle_row = (
        '<div class="crit-toggle">'
        '<button class="crit-btn" data-target="verse" onclick="toggleCriterion(\'verse\')">Verse (primary)</button>'
        '<button class="crit-btn" data-target="strict" onclick="toggleCriterion(\'strict\')">Strict (secondary)</button>'
        '<button class="crit-btn" data-target="token" onclick="toggleCriterion(\'token\')">Token-overlap (secondary)</button>'
        "</div>"
    )
    f1_tables = "".join(f'<div data-criterion="{c}">{build_subtype_f1_table(sub_report, c)}</div>' for c in CRITERIA)
    indicative = sub_report["n_pool_positives"] < 30
    flag_html = (f'<p class="warning-banner">Indicative only: {sub_report["n_pool_positives"]} '
                 f'GT-positive verses in the 25-poem pool, below this task\'s 30-positive floor. '
                 f'Read as a direction, not a precise estimate.</p>') if indicative else ""
    return f"""
<h3>{rtl_wrap(subtype)} <span class="muted">({esc(SUBTYPE_PARENT.get(subtype, ""))})</span></h3>
{flag_html}
<h4>F1 by model and condition</h4>
{toggle_row}
{f1_tables}
<h4>Bootstrap 95% CI: few-shot &minus; zero-shot, per model</h4>
{build_bootstrap_table(sub_report)}
<h4>Design-choice check (GPT-Z, Claude-FS, OR/AND, 3-vote, Gemini leave-one-out)</h4>
{build_design_choice_table(sub_report)}
"""


def build_phase7_section() -> str:
    analysis = _load(ANALYSIS_PATH)
    if analysis is None:
        return ""
    census = _load(CENSUS_PATH)
    census_t2 = _load(CENSUS_T2_PATH)
    dryrun = _load(DRYRUN_PATH)
    dryrun_t2 = _load(DRYRUN_T2_PATH)
    sets_doc = _load(SETS_PATH)
    sets_t2_doc = _load(SETS_T2_PATH)

    total_cost = (dryrun.get("grand_total_primary_usd", 0) if dryrun else 0) + \
                 (dryrun_t2.get("grand_total_primary_usd", 0) if dryrun_t2 else 0)
    total_calls = (dryrun.get("total_calls", 0) if dryrun else 0) + \
                  (dryrun_t2.get("total_calls", 0) if dryrun_t2 else 0)

    panels = "".join(build_subtype_panel(s, analysis["subtypes"][s]) for s in ALL_SUBTYPES if s in analysis["subtypes"])
    example_cards = "".join(
        f'<h4>{rtl_wrap(s)}</h4>{build_example_card(s, sets_doc, sets_t2_doc)}' for s in ALL_SUBTYPES
    )
    coverage_line = ("Full identical coverage confirmed (12 cells x 327 verse-units, 0 incomplete)."
                      if analysis.get("coverage_ok") else
                      "<strong>Coverage was INCOMPLETE at scoring time — numbers below may be partial.</strong>")

    return f"""
<details>
<summary>p. Phase 7: subtype-level checks (4 rhetorical subtypes, added 2026-10-29/30)</summary>
<p>Scope: 3 models &times; {{zero-shot, few-shot}} &times; 4 rhetorical subtypes
(استعارة قديمة, كناية عن صفة, تشبيه قصير, تشبيه مطول), 1 run per cell, same unchanged
25-poem/327-verse <code>eval_pool_25.json</code> pool used throughout this report. Dr. Ali
Hussein named تشبيه قصير/طويل for the تشبيه family after confirming his corpus classifies تشبيه by
length (مطول/قصير/تمثيلي/مركب/الشيء بنفسه), not بليغ/مؤكد. Verse-level F1 is the primary metric
here (CLAUDE.md's span-level strict/token-overlap criteria are reported alongside as secondary).
Total: {total_calls} API calls, ~${total_cost:.2f} estimated. {coverage_line}</p>

<h3>Census (all 4 subtypes)</h3>
{build_census_table(census, census_t2)}
<p>Verse-boundary-crossing check (does the annotated span ever cross into a second verse?):
تشبيه قصير 3/160 (1.9%), تشبيه مطول 19/226 (8.4%) — neither exceeds the 20% materiality bar, so
single-verse remains the scoring unit for every subtype.</p>
<p><strong>Data-quality caveat</strong>: a general corpus property, not specific to Phase 7 —
some annotation <code>span_text</code> values are NOT in verse reading order (confirmed on two
تشبيه مطول candidates, one multi-verse, one single-verse). This does not affect this project's own
scoring (token-overlap and verse-level matching are both order-independent) but made two
candidate few-shot examples unusable; both were excluded by an added reading-order filter before
the real example draw.</p>

<h3>Few-shot example sets</h3>
{example_cards}

<h3>Results by subtype</h3>
{panels}

<p>Two of the four subtypes (استعارة قديمة: 15 pool positives, تشبيه قصير: 13, تشبيه مطول: 25)
are <strong>indicative-only</strong> — below this task's own 30-positive floor in the unchanged
25-poem pool; extending the pool was costed and declined (see
<code>docs/phase4/SESSION_LOG.md</code>, 2026-10-29) in favor of running all 4 subtypes on the
same pool everything else in this report already uses. كناية عن صفة (49 pool positives) is the
only one of the four with an adequately-powered sample.</p>
</details>
"""


if __name__ == "__main__":
    html = build_phase7_section()
    print(f"{len(html)} chars generated" if html else "No analysis_report_phase7.json yet -- empty section.")
