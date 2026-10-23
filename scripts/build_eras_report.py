"""Builds docs/phase4/ERAS_ANALYTICS.md and docs/phase4/ERAS_ANALYTICS.html
-- Part 1 of the poet-death-year / era few-shot task (see
docs/phase4/SESSION_LOG.md for the full task). Every number is read
programmatically from:
  - data/ali_poems/poet_dates.csv (Step 1's researched death years)
  - experiments/phase4_e1_v2/config/eras_axis.json (eras_analytics.py's
    computed bins/medians/bands -- itself built from manifest.csv +
    poems/*.json + poet_dates.csv)
No number in either output is hand-typed.

HTML is a single self-contained file (inline CSS/JS/SVG, no external
dependencies), RTL-aware (Arabic poet names rendered dir="rtl" via
pilot_3models.rtl_utils.is_majority_arabic, the shared helper CLAUDE.md
requires reusing), with collapsible sections and light/dark support.
"""
import csv
import html as htmlmod
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.pilot_3models.rtl_utils import is_majority_arabic  # noqa: E402

DOCS_DIR = ROOT / "docs" / "phase4"
AXIS_PATH = ROOT / "experiments" / "phase4_e1_v2" / "config" / "eras_axis.json"
POET_DATES_PATH = ROOT / "data" / "ali_poems" / "poet_dates.csv"
MD_OUT = DOCS_DIR / "ERAS_ANALYTICS.md"
HTML_OUT = DOCS_DIR / "ERAS_ANALYTICS.html"


def esc(s) -> str:
    return htmlmod.escape(str(s), quote=True)


def rtl_wrap(text: str, cls: str = "") -> str:
    direction = "rtl" if is_majority_arabic(str(text)) else "ltr"
    c = f" {cls}" if cls else ""
    return f'<span dir="{direction}" class="bidi{c}">{esc(text)}</span>'


axis = json.loads(AXIS_PATH.read_text(encoding="utf-8"))
with open(POET_DATES_PATH, encoding="utf-8") as f:
    poet_dates_rows = list(csv.DictReader(f))

GENERATED_AT = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def fmt(x, nd=1):
    if x is None:
        return "n/a"
    return f"{x:.{nd}f}"


def build_md() -> str:
    lines = []
    a = lines.append
    a("# Poet Death-Year / Era Analytics\n")
    a(f"Generated {GENERATED_AT} by `scripts/build_eras_report.py` from "
      f"`data/ali_poems/poet_dates.csv` + `experiments/phase4_e1_v2/config/eras_axis.json` "
      f"(itself built from `data/ali_poems/manifest.csv` + `data/ali_poems/poems/*.json` "
      f"by `experiments/phase4_e1_v2/eras_analytics.py`). No number below is hand-typed.\n")
    a("Verse counts exclude poem 28601 (no verse text; the only annotated-but-textless poem "
      "in the corpus, per the task's explicit instruction).\n")

    a("## 1. Corpus coverage\n")
    a(f"- Poets total: **{axis['n_poets_total']}**")
    a(f"- Poets with a reliable death year (any confidence): **{axis['n_poets_dated']}**")
    a(f"- Poets without a reliable death year: **{axis['n_poets_undated']}** (listed in §6, "
      f"excluded from every year-indexed statistic below)\n")

    a("## 2. Central tendency and axis midpoint\n")
    a("| Statistic | Value (CE) |")
    a("|---|---|")
    a(f"| Median, weighted by verses (**PRIMARY** -- see note below) | {fmt(axis['median_by_verses'])} |")
    a(f"| Median, weighted by poems | {fmt(axis['median_by_poems'])} |")
    a(f"| Median, plain per-poet (unweighted) | {fmt(axis['plain_median'])} |")
    a(f"| Mean, weighted by verses | {fmt(axis['mean_by_verses'])} |")
    a(f"| Mean, weighted by poems | {fmt(axis['mean_by_poems'])} |")
    a(f"| Mean, plain per-poet (unweighted) | {fmt(axis['plain_mean'])} |")
    a(f"| **Midpoint of the time axis** ((min+max)/2) | {fmt(axis['midpoint'])} |")
    a(f"| Range | {axis['min_year']} - {axis['max_year']} |\n")
    a("**Why verse-weighted is PRIMARY**: every other metric in this project (CLAUDE.md rule 4, "
      "the 2026-10-14 verse-primary decision) is computed per verse-unit, not per poem or per poet; "
      "the verse-weighted median is the one all band/half/extreme definitions below are built on. "
      "The midpoint is a property of the axis's *range*, not of its *distribution* -- reported "
      "separately because it answers a different question (\"what year is exactly between the "
      "earliest and latest death?\" vs. \"where is the bulk of the corpus's verses centered?\").\n")

    a("## 3. Bands and extremes (relative to the verse-weighted median)\n")
    a(f"- **Middle band**: within ±{axis['middle_band_half_width_years']} years of the median "
      f"({fmt(axis['primary_median'])}), i.e. {fmt(axis['primary_median'] - axis['middle_band_half_width_years'])}"
      f"–{fmt(axis['primary_median'] + axis['middle_band_half_width_years'])} CE.")
    a(f"- **First half**: death_year_ce < {fmt(axis['primary_median'])}. **Second half**: "
      f">= {fmt(axis['primary_median'])}. First-half median = {fmt(axis['first_half_median'])}, "
      f"second-half median = {fmt(axis['second_half_median'])}.")
    a(f"- **Extremes**: earliest/latest {axis['extreme_pct']*100:.0f}% of dated poets by rank, sorted "
      f"by death year (ties at the boundary year are all included, so a group can be slightly larger "
      f"than the exact percentage). Earliest-extreme threshold: <= {axis['earliest_threshold_year']} CE. "
      f"Latest-extreme threshold: >= {axis['latest_threshold_year']} CE.\n")

    a("| Group | Poets | Poems | Verses |")
    a("|---|---|---|---|")
    for label, key in [("First half", "first_half"), ("Second half", "second_half"),
                        ("Middle band", "middle_band"), ("Earliest extreme", "earliest_extreme"),
                        ("Latest extreme", "latest_extreme")]:
        c = axis["counts"][key]
        a(f"| {label} | {c['n_poets']} | {c['n_poems']} | {c['n_verses']} |")
    a("")

    a("## 4. By 100-year death-year bin\n")
    a("| Bin (CE) | Poets | Poems | Verses | استعارة فعل positive verses |")
    a("|---|---|---|---|---|")
    for b, c in axis["bins"].items():
        a(f"| {b} | {c['n_poets']} | {c['n_poems']} | {c['n_verses']} | {c['n_positive_verses']} |")
    a("")

    a("## 5. By site era (الفترة)\n")
    a("| Era | Poets (dated) | Poems | Verses | استعارة فعل positive verses |")
    a("|---|---|---|---|---|")
    for era, c in sorted(axis["by_era"].items(), key=lambda kv: -kv[1]["n_poems"]):
        label = era if era else "(blank)"
        a(f"| {label} | {c['n_poets']} ({c['n_poets_dated']}) | {c['n_poems']} | {c['n_verses']} | "
          f"{c['n_positive_verses']} |")
    a("")

    a("## 6. Poets without a reliable death year\n")
    a("Excluded from every year-indexed statistic above (§2-5); their poems/verses still count "
      "toward corpus totals in §1 and in the by-era table (§5)'s poem/verse columns, just not the "
      "dated-poet columns.\n")
    a("| Poet | Reason |")
    a("|---|---|")
    for p in axis["undated_poets"]:
        a(f"| {p['poet_name']} | {p['note']} |")
    a("")

    a("## 7. Cumulative curve (by death year, ascending)\n")
    a("| Poet | Death year (CE) | Cumulative poets | Cumulative poems | Cumulative verses |")
    a("|---|---|---|---|---|")
    for row in axis["cumulative"]:
        a(f"| {row['poet_name']} | {row['death_year_ce']} | {row['cum_poets']} | {row['cum_poems']} | "
          f"{row['cum_verses']} |")
    a("")

    a("## 8. Full per-poet table\n")
    a("| Poet | Period | Death year (CE) | Death year (AH) | Approx.? | Confidence | Poems | "
      "Verses | استعارة فعل positive |")
    a("|---|---|---|---|---|---|---|---|---|")
    for p in axis["per_poet"]:
        a(f"| {p['poet_name']} | {p['period'] or '(blank)'} | {p['death_year_ce'] if p['death_year_ce'] is not None else ''} | "
          f"{p['death_year_ah'] if p['death_year_ah'] is not None else ''} | "
          f"{'yes' if p['approximate'] else ('no' if p['has_reliable_date'] else '')} | "
          f"{p['confidence'] or ''} | {p['n_poems']} | {p['n_verses']} | {p['n_positive_verses']} |")
    a("")

    return "\n".join(lines)


md_text = build_md()
MD_OUT.write_text(md_text, encoding="utf-8")
print(f"Wrote {MD_OUT} ({len(md_text)} chars)")


# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

def svg_cumulative_curve() -> str:
    cum = axis["cumulative"]
    if not cum:
        return "<p>No dated poets.</p>"
    w, h = 720, 260
    pad_l, pad_b, pad_t, pad_r = 50, 30, 16, 16
    plot_w, plot_h = w - pad_l - pad_r, h - pad_b - pad_t
    years = [r["death_year_ce"] for r in cum]
    ymin, ymax = min(years), max(years)
    yrange = max(ymax - ymin, 1)
    max_verses = cum[-1]["cum_verses"] or 1
    max_poems = cum[-1]["cum_poems"] or 1

    def x_of(year):
        return pad_l + (year - ymin) / yrange * plot_w

    def y_of(value, vmax):
        return pad_t + plot_h - (value / vmax) * plot_h

    verses_pts = " ".join(f"{x_of(r['death_year_ce']):.1f},{y_of(r['cum_verses'], max_verses):.1f}" for r in cum)
    poems_pts = " ".join(f"{x_of(r['death_year_ce']):.1f},{y_of(r['cum_poems'], max_poems):.1f}" for r in cum)
    median_x = x_of(axis["primary_median"])
    parts = [f'<svg viewBox="0 0 {w} {h}" class="cumchart" xmlns="http://www.w3.org/2000/svg" '
             f'role="img" aria-label="Cumulative poems/verses by death year">']
    parts.append(f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h - pad_b}" class="axis"/>')
    parts.append(f'<line x1="{pad_l}" y1="{h - pad_b}" x2="{w - pad_r}" y2="{h - pad_b}" class="axis"/>')
    parts.append(f'<line x1="{median_x:.1f}" y1="{pad_t}" x2="{median_x:.1f}" y2="{h - pad_b}" class="median-line"/>')
    parts.append(f'<text x="{median_x:.1f}" y="{pad_t - 2}" class="median-label">median {axis["primary_median"]:.0f}</text>')
    parts.append(f'<polyline points="{verses_pts}" class="cum-verses" fill="none"/>')
    parts.append(f'<polyline points="{poems_pts}" class="cum-poems" fill="none"/>')
    for yr in (ymin, ymax):
        parts.append(f'<text x="{x_of(yr):.1f}" y="{h - pad_b + 14}" class="axis-label">{yr}</text>')
    parts.append(f'<text x="{pad_l}" y="{pad_t - 2}" class="legend-label">— cum. verses</text>')
    parts.append(f'<text x="{pad_l + 140}" y="{pad_t - 2}" class="legend-label cum-poems-label">— cum. poems</text>')
    parts.append("</svg>")
    return "".join(parts)


def svg_bins_bar() -> str:
    bins = axis["bins"]
    if not bins:
        return "<p>No bins.</p>"
    w, h = 720, 220
    pad_l, pad_b, pad_t, pad_r = 50, 40, 16, 16
    plot_w, plot_h = w - pad_l - pad_r, h - pad_b - pad_t
    keys = list(bins.keys())
    bar_w = plot_w / len(keys)
    vmax = max(c["n_verses"] for c in bins.values()) or 1
    parts = [f'<svg viewBox="0 0 {w} {h}" class="binschart" xmlns="http://www.w3.org/2000/svg" '
             f'role="img" aria-label="Verses per 100-year bin">']
    parts.append(f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h - pad_b}" class="axis"/>')
    parts.append(f'<line x1="{pad_l}" y1="{h - pad_b}" x2="{w - pad_r}" y2="{h - pad_b}" class="axis"/>')
    for i, k in enumerate(keys):
        c = bins[k]
        bh = (c["n_verses"] / vmax) * plot_h
        x = pad_l + i * bar_w + bar_w * 0.1
        y = h - pad_b - bh
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w * 0.8:.1f}" height="{max(bh,1):.1f}" '
                     f'class="bin-bar"><title>{esc(k)}: {c["n_verses"]} verses, {c["n_poets"]} poets</title></rect>')
        parts.append(f'<text x="{x + bar_w * 0.4:.1f}" y="{h - pad_b + 14}" class="axis-label" '
                     f'transform="rotate(30 {x + bar_w * 0.4:.1f} {h - pad_b + 14})">{esc(k)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def table(headers, rows) -> str:
    thead = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{c}</td>" for c in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return (f'<div class="table-wrap"><table class="data-table"><thead><tr>{thead}</tr></thead>'
            f'<tbody>{"".join(body_rows)}</tbody></table></div>')


def build_html() -> str:
    counts_rows = []
    for label, key in [("First half", "first_half"), ("Second half", "second_half"),
                        ("Middle band", "middle_band"), ("Earliest extreme", "earliest_extreme"),
                        ("Latest extreme", "latest_extreme")]:
        c = axis["counts"][key]
        counts_rows.append([label, c["n_poets"], c["n_poems"], c["n_verses"]])

    bins_rows = [[b, c["n_poets"], c["n_poems"], c["n_verses"], c["n_positive_verses"]]
                 for b, c in axis["bins"].items()]

    era_rows = []
    for era, c in sorted(axis["by_era"].items(), key=lambda kv: -kv[1]["n_poems"]):
        era_rows.append([rtl_wrap(era or "(blank)"), f"{c['n_poets']} ({c['n_poets_dated']})",
                          c["n_poems"], c["n_verses"], c["n_positive_verses"]])

    undated_rows = [[rtl_wrap(p["poet_name"]), rtl_wrap(p["note"])] for p in axis["undated_poets"]]

    cum_rows = [[rtl_wrap(r["poet_name"]), r["death_year_ce"], r["cum_poets"], r["cum_poems"], r["cum_verses"]]
                for r in axis["cumulative"]]

    per_poet_rows = []
    for p in axis["per_poet"]:
        per_poet_rows.append([
            rtl_wrap(p["poet_name"]), rtl_wrap(p["period"] or "(blank)"),
            p["death_year_ce"] if p["death_year_ce"] is not None else "",
            p["death_year_ah"] if p["death_year_ah"] is not None else "",
            ("yes" if p["approximate"] else ("no" if p["has_reliable_date"] else "")),
            p["confidence"] or "", p["n_poems"], p["n_verses"], p["n_positive_verses"],
        ])

    sources_rows = [[rtl_wrap(r["poet_name"]), r["death_year_ce"], r["confidence"],
                      f'<a href="{esc(r["source_url"])}" target="_blank" rel="noopener">{esc(r["source_url"][:60])}...</a>'
                      if r["source_url"] else "", rtl_wrap(r["note"])]
                     for r in poet_dates_rows]

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Poet Death-Year / Era Analytics</title>
<style>
:root {{
  --bg: #f7f6f3; --fg: #1c1c1a; --muted: #6b6b63; --border: #ddd9d0;
  --accent: #8a5a2b; --accent2: #3a6b8a; --card: #ffffff;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #1a1816; --fg: #ece8e1; --muted: #a39d8f; --border: #3a362f;
    --accent: #d99a5b; --accent2: #7fb4d6; --card: #242019;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #1a1816; --fg: #ece8e1; --muted: #a39d8f; --border: #3a362f;
  --accent: #d99a5b; --accent2: #7fb4d6; --card: #242019;
}}
* {{ box-sizing: border-box; }}
body {{ background: var(--bg); color: var(--fg); font-family: -apple-system, Segoe UI, Tahoma, sans-serif;
       margin: 0; padding: 16px; line-height: 1.5; }}
.container {{ max-width: 980px; margin: 0 auto; }}
h1 {{ font-size: 1.5rem; }}
h2 {{ font-size: 1.15rem; border-bottom: 1px solid var(--border); padding-bottom: 4px; margin-top: 2rem; }}
.meta {{ color: var(--muted); font-size: 0.85rem; }}
details {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px;
          padding: 10px 14px; margin: 10px 0; }}
summary {{ cursor: pointer; font-weight: 600; }}
.table-wrap {{ overflow-x: auto; max-height: 480px; overflow-y: auto; }}
table.data-table {{ border-collapse: collapse; width: 100%; font-size: 0.85rem; }}
table.data-table th, table.data-table td {{ border: 1px solid var(--border); padding: 4px 8px; text-align: left; }}
table.data-table th {{ background: var(--card); position: sticky; top: 0; }}
.stat-table td, .stat-table th {{ border: 1px solid var(--border); padding: 4px 10px; }}
.bidi {{ unicode-bidi: isolate; }}
.axis {{ stroke: var(--muted); stroke-width: 1; }}
.median-line {{ stroke: var(--accent); stroke-width: 1.5; stroke-dasharray: 4 3; }}
.median-label {{ fill: var(--accent); font-size: 10px; }}
.cum-verses {{ stroke: var(--accent2); stroke-width: 2; }}
.cum-poems {{ stroke: var(--accent); stroke-width: 2; }}
.cum-poems-label {{ fill: var(--accent); }}
.legend-label {{ font-size: 10px; fill: var(--accent2); }}
.axis-label {{ font-size: 10px; fill: var(--muted); }}
.bin-bar {{ fill: var(--accent2); }}
svg {{ width: 100%; max-width: 720px; height: auto; display: block; margin: 8px 0; }}
.copy-btn {{ font-size: 0.75rem; padding: 2px 8px; border: 1px solid var(--border); border-radius: 4px;
            background: var(--card); color: var(--fg); cursor: pointer; }}
.themebar {{ position: sticky; top: 0; background: var(--bg); padding: 4px 0; z-index: 2; }}
a {{ color: var(--accent2); }}
</style>
</head>
<body>
<div class="container">
<div class="themebar"><button class="copy-btn" id="theme-toggle" type="button">Toggle theme</button></div>
<h1>Poet Death-Year / Era Analytics</h1>
<p class="meta">Generated {esc(GENERATED_AT)} by <code>scripts/build_eras_report.py</code> from
<code>data/ali_poems/poet_dates.csv</code> + <code>experiments/phase4_e1_v2/config/eras_axis.json</code>.
No number below is hand-typed. Verse counts exclude poem 28601 (no verse text).</p>

<h2>1. Corpus coverage</h2>
<table class="stat-table">
<tr><th>Poets total</th><td>{axis['n_poets_total']}</td></tr>
<tr><th>Poets with a reliable death year</th><td>{axis['n_poets_dated']}</td></tr>
<tr><th>Poets without a reliable death year</th><td>{axis['n_poets_undated']}</td></tr>
</table>

<h2>2. Central tendency and axis midpoint</h2>
<table class="stat-table">
<tr><th>Median, weighted by verses (PRIMARY)</th><td>{fmt(axis['median_by_verses'])}</td></tr>
<tr><th>Median, weighted by poems</th><td>{fmt(axis['median_by_poems'])}</td></tr>
<tr><th>Median, plain per-poet</th><td>{fmt(axis['plain_median'])}</td></tr>
<tr><th>Mean, weighted by verses</th><td>{fmt(axis['mean_by_verses'])}</td></tr>
<tr><th>Mean, weighted by poems</th><td>{fmt(axis['mean_by_poems'])}</td></tr>
<tr><th>Mean, plain per-poet</th><td>{fmt(axis['plain_mean'])}</td></tr>
<tr><th>Midpoint of time axis</th><td>{fmt(axis['midpoint'])}</td></tr>
<tr><th>Range</th><td>{axis['min_year']}&ndash;{axis['max_year']}</td></tr>
</table>
<p>Verse-weighted median is PRIMARY (every other metric in this project is verse-primary, CLAUDE.md rule 4).
The midpoint is a property of the axis's range, distinct from its distribution's center.</p>

<h2>3. Bands and extremes</h2>
<p>Middle band: within &plusmn;{axis['middle_band_half_width_years']} years of the median
({fmt(axis['primary_median'])}). First half: &lt;{fmt(axis['primary_median'])}; second half: &ge;{fmt(axis['primary_median'])}
(first-half median {fmt(axis['first_half_median'])}, second-half median {fmt(axis['second_half_median'])}).
Extremes: earliest/latest {axis['extreme_pct']*100:.0f}% of dated poets by rank
(earliest threshold &le;{axis['earliest_threshold_year']} CE, latest threshold &ge;{axis['latest_threshold_year']} CE).</p>
{table(["Group", "Poets", "Poems", "Verses"], counts_rows)}

<h2>4. Cumulative curve</h2>
{svg_cumulative_curve()}

<h2>5. By 100-year death-year bin</h2>
{svg_bins_bar()}
{table(["Bin (CE)", "Poets", "Poems", "Verses", "استعارة فعل positive verses"], bins_rows)}

<h2>6. By site era (الفترة)</h2>
{table(["Era", "Poets (dated)", "Poems", "Verses", "استعارة فعل positive verses"], era_rows)}

<details>
<summary>7. Poets without a reliable death year ({axis['n_poets_undated']})</summary>
{table(["Poet", "Reason"], undated_rows)}
</details>

<details>
<summary>8. Cumulative table (per poet, by death year)</summary>
{table(["Poet", "Death year (CE)", "Cum. poets", "Cum. poems", "Cum. verses"], cum_rows)}
</details>

<details>
<summary>9. Full per-poet table ({axis['n_poets_total']} poets)</summary>
{table(["Poet", "Period", "Death (CE)", "Death (AH)", "Approx.?", "Confidence", "Poems", "Verses",
        "استعارة فعل positive"], per_poet_rows)}
</details>

<details>
<summary>10. Sources (poet_dates.csv, {len(poet_dates_rows)} rows)</summary>
{table(["Poet", "Death (CE)", "Confidence", "Source", "Note"], sources_rows)}
</details>

</div>
<script>
(function() {{
  var btn = document.getElementById('theme-toggle');
  var root = document.documentElement;
  try {{
    var saved = localStorage.getItem('eras-theme');
    if (saved) root.setAttribute('data-theme', saved);
  }} catch (e) {{}}
  btn.addEventListener('click', function() {{
    var cur = root.getAttribute('data-theme');
    var next = cur === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try {{ localStorage.setItem('eras-theme', next); }} catch (e) {{}}
  }});
}})();
</script>
</body>
</html>
"""


html_text = build_html()
HTML_OUT.write_text(html_text, encoding="utf-8")
print(f"Wrote {HTML_OUT} ({len(html_text)} chars)")
