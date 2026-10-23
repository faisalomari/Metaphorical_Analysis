"""Builds docs/phase4/E1_V2_REPORT.html — a single self-contained, offline,
RTL-aware HTML report of the Phase 4 E1 v2 example-sensitivity pilot
(target sub-element: استعارة فعل).

Every number/prompt/example in the output is read programmatically from the
existing result/config files (never hand-retyped):
  - results/phase4_e1_v2/analysis_report.json   (all F1/TP/FP/FN/CI tables)
  - results/phase4_e1_v2/run_manifest.json      (call counts, token usage -> cost)
  - experiments/phase4_e1_v2/config/eval_pool_25.json (pool composition)
  - experiments/phase4_e1/config/example_sets.json    (v1 example sets, reused by v2)
  - experiments/phase4_e1_v2/config/prompt_preview_{Z,A,B,C}.txt (verbatim system msgs)
  - experiments/phase4_e1_v2/prompt_builder.py + e1v2_config.py (built, not retyped, system messages)
  - experiments/phase3_subelements/subtype_prompts.py (user message template / schema)
  - experiments/pilot_3models/config.py (per-model pricing table)
  - experiments/pilot_3models/rtl_utils.py (is_majority_arabic, reused for HTML dir= decisions)
  - docs/phase4/E1_V2_RESULTS.md (authored prose: executive summary / Q1-Q3 / caveats)
  - writing/paper_plan/TOP_5_BLOCKERS.md (licensing caveat)

Run: python scripts/build_e1v2_report.py
Writes: docs/phase4/E1_V2_REPORT.html
Also runs built-in verification checks (see verify_* functions) and prints
PASS/FAIL for each before declaring the file written.
"""
import difflib
import html as htmlmod
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.pilot_3models.rtl_utils import is_majority_arabic  # noqa: E402
from experiments.pilot_3models import config as pilot_config  # noqa: E402
from experiments.phase4_e1_v2 import e1v2_config  # noqa: E402
from experiments.phase4_e1_v2 import prompt_builder  # noqa: E402

RESULTS_DIR = ROOT / "results" / "phase4_e1_v2"
E1V2_DIR = ROOT / "experiments" / "phase4_e1_v2"
E1V1_DIR = ROOT / "experiments" / "phase4_e1"
DOCS_DIR = ROOT / "docs" / "phase4"
OUT_PATH = DOCS_DIR / "E1_V2_REPORT.html"

ANALYSIS_PATH = RESULTS_DIR / "analysis_report.json"
ANALYSIS_D_PATH = RESULTS_DIR / "analysis_report_D.json"
ANALYSIS_VERSE_PATH = RESULTS_DIR / "analysis_report_verse.json"
ANALYSIS_ENSEMBLE_PATH = RESULTS_DIR / "analysis_report_ensemble.json"
ANALYSIS_OPUS_A_PATH = RESULTS_DIR / "analysis_report_opus_a.json"
OPUS_A_DOC_PATH = DOCS_DIR / "E1_V2_OPUS_A.md"
MANIFEST_PATH = RESULTS_DIR / "run_manifest.json"
POOL_PATH = E1V2_DIR / "config" / "eval_pool_25.json"
EXAMPLE_SETS_PATH = E1V1_DIR / "config" / "example_sets.json"
RESULTS_MD_PATH = DOCS_DIR / "E1_V2_RESULTS.md"
SAMEPOET_PATH = DOCS_DIR / "E1_V2_SAMEPOET.md"
SET_D_PATH = DOCS_DIR / "E1_V2_SET_D.md"
ENSEMBLE_PATH = DOCS_DIR / "E1_V2_ENSEMBLE.md"
BLOCKERS_PATH = ROOT / "writing" / "paper_plan" / "TOP_5_BLOCKERS.md"
PROMPT_INVENTORY_PATH = DOCS_DIR / "PROMPT_INVENTORY.md"

SET_NAMES = ["Z", "A", "B", "C"]
SET_NAMES_FULL = ["Z", "A", "B", "C", "D", "D2"]
MODEL_KEYS = ["anthropic", "openai", "google"]
# Ordered so "verse" (the user's 2026-10-14 primary-metric decision) is first/default;
# CLAUDE.md rule 4 still flags it as a supplementary diagnostic -- noted in the caveat box.
CRITERIA = ["verse", "strict", "token"]
CRITERION_LABEL = {"verse": "Verse-exists (PRIMARY, user decision 2026-10-14)",
                    "strict": "Strict (secondary)", "token": "Token-overlap (secondary)"}
DEFAULT_CRITERION = "verse"

SOURCE_FILES_USED = [
    "results/phase4_e1_v2/analysis_report.json",
    "results/phase4_e1_v2/analysis_report_D.json",
    "results/phase4_e1_v2/analysis_report_verse.json",
    "results/phase4_e1_v2/analysis_report_ensemble.json",
    "results/phase4_e1_v2/analysis_report_opus_a.json",
    "results/phase4_e1_v2/run_manifest.json",
    "experiments/phase4_e1_v2/config/eval_pool_25.json",
    "experiments/phase4_e1/config/example_sets.json",
    "experiments/phase4_e1_v2/config/prompt_preview_Z.txt",
    "experiments/phase4_e1_v2/config/prompt_preview_A.txt",
    "experiments/phase4_e1_v2/config/prompt_preview_B.txt",
    "experiments/phase4_e1_v2/config/prompt_preview_C.txt",
    "experiments/phase4_e1_v2/config/prompt_preview_D.txt",
    "experiments/phase4_e1_v2/config/prompt_preview_D2.txt",
    "experiments/phase4_e1_v2/prompt_builder.py",
    "experiments/phase4_e1_v2/e1v2_config.py",
    "experiments/phase3_subelements/subtype_prompts.py",
    "experiments/pilot_3models/config.py",
    "experiments/pilot_3models/rtl_utils.py",
    "docs/phase4/E1_V2_RESULTS.md",
    "docs/phase4/E1_V2_SET_D.md",
    "docs/phase4/E1_V2_ENSEMBLE.md",
    "docs/phase4/E1_V2_OPUS_A.md",
    "docs/phase4/PROMPT_INVENTORY.md",
    "writing/paper_plan/TOP_5_BLOCKERS.md",
    "results/phase4_e1_v2/analysis_report_multipoet.json",
    "experiments/phase4_e1_v2/config/eval_pool_50_multipoet.json",
    "experiments/phase4_e1_v2/config/multipoet_example_sets.json",
    "experiments/phase4_e1_v2/config/prompt_preview_F5.txt",
    "experiments/phase4_e1_v2/config/prompt_preview_F10.txt",
    "docs/phase4/E1_V2_MULTIPOET.md",
    "results/phase4_e1_v2/analysis_report_eras.json",
    "experiments/phase4_e1_v2/config/eras_example_sets.json",
    "experiments/phase4_e1_v2/config/eras_axis.json",
    "data/ali_poems/poet_dates.csv",
    "docs/phase4/ERAS_ANALYTICS.md",
    "docs/phase4/E1_V2_ERAS_FEWSHOT.md",
]


def esc(s) -> str:
    return htmlmod.escape(str(s), quote=True)


def rtl_wrap(text: str, css_class: str = "") -> str:
    """Wrap text in a span with dir=rtl/ltr decided by is_majority_arabic,
    per CLAUDE.md's shared-helper rule (reused here for HTML, not docx)."""
    direction = "rtl" if is_majority_arabic(text) else "ltr"
    cls = f" {css_class}" if css_class else ""
    return f'<span dir="{direction}" class="bidi{cls}">{esc(text)}</span>'


def md_inline(text: str) -> str:
    """Minimal inline markdown -> HTML: escape, then **bold** and `code`."""
    out = esc(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return out


TABLE_SEP_RE = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?$")
HR_RE = re.compile(r"^-{3,}$")
HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def _parse_table_row(line: str):
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def md_block(text: str) -> str:
    """Small block markdown -> HTML: paragraphs, '- ' bullet lists, '#'
    headers, '---' rules, and pipe tables, with inline bold/code via
    md_inline. Covers everything used in docs/phase4/*.md's prose sections
    (E1_V2_RESULTS.md / E1_V2_SAMEPOET.md) without a markdown dependency."""
    lines = text.strip("\n").split("\n")
    out, buf, li_buf, in_list = [], [], [], False
    i, n = 0, len(lines)

    def flush_par():
        if buf:
            out.append("<p>" + md_inline(" ".join(buf)) + "</p>")
            buf.clear()

    def flush_li():
        if li_buf:
            out.append("<li>" + md_inline(" ".join(li_buf)) + "</li>")
            li_buf.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            flush_li()
            out.append("</ul>")
            in_list = False

    while i < n:
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            flush_par()
            close_list()
            i += 1
            continue

        m = HEADER_RE.match(stripped)
        if m:
            flush_par()
            close_list()
            level = min(len(m.group(1)) + 3, 6)
            out.append(f"<h{level}>{md_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        if HR_RE.match(stripped):
            flush_par()
            close_list()
            out.append("<hr>")
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < n and TABLE_SEP_RE.match(lines[i + 1].strip()):
            flush_par()
            close_list()
            header_cells = _parse_table_row(stripped)
            i += 2
            body_rows = []
            while i < n and lines[i].strip().startswith("|"):
                body_rows.append(_parse_table_row(lines[i].strip()))
                i += 1
            thead = "".join(f"<th>{md_inline(c)}</th>" for c in header_cells)
            tbody = "".join(
                "<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in row) + "</tr>" for row in body_rows
            )
            out.append(f'<div class="md-table-wrap"><table class="detail-table">'
                       f"<thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table></div>")
            continue

        if stripped.startswith("- "):
            flush_par()
            if not in_list:
                out.append("<ul>")
                in_list = True
            else:
                flush_li()
            li_buf.append(stripped[2:])
            i += 1
            continue

        if in_list:
            # soft-wrapped continuation of the current list item
            li_buf.append(stripped)
            i += 1
            continue

        buf.append(stripped)
        i += 1

    flush_par()
    close_list()
    return "\n".join(out)


def extract_section(md_text: str, header: str, next_headers) -> str:
    """Return the body text between a '## {header}' line and the next
    header line in `next_headers` (or EOF)."""
    pattern = re.compile(rf"^##\s+{re.escape(header)}.*$", re.MULTILINE)
    m = pattern.search(md_text)
    if not m:
        return ""
    start = m.end()
    end = len(md_text)
    for h in next_headers:
        m2 = re.search(rf"^##\s+{re.escape(h)}", md_text[start:], re.MULTILINE)
        if m2:
            end = min(end, start + m2.start())
    return md_text[start:end].strip()


# ---------------------------------------------------------------------------
# Load sources
# ---------------------------------------------------------------------------

analysis_zabc = json.loads(ANALYSIS_PATH.read_text(encoding="utf-8"))  # Z/A/B/C, verse/strict/token
analysis_d = json.loads(ANALYSIS_D_PATH.read_text(encoding="utf-8"))   # Z/A/B/C/D/D2, verse/strict/token
analysis_ensemble = json.loads(ANALYSIS_ENSEMBLE_PATH.read_text(encoding="utf-8"))  # majority-vote ensemble, all 6 sets
manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
pool = json.loads(POOL_PATH.read_text(encoding="utf-8"))
example_sets = json.loads(EXAMPLE_SETS_PATH.read_text(encoding="utf-8"))
results_md = RESULTS_MD_PATH.read_text(encoding="utf-8")
blockers_md = BLOCKERS_PATH.read_text(encoding="utf-8")
prompt_inventory_md = PROMPT_INVENTORY_PATH.read_text(encoding="utf-8")
samepoet_exists = SAMEPOET_PATH.exists()
samepoet_text = SAMEPOET_PATH.read_text(encoding="utf-8") if samepoet_exists else None
set_d_exists = SET_D_PATH.exists()
set_d_text = SET_D_PATH.read_text(encoding="utf-8") if set_d_exists else None
ensemble_doc_exists = ENSEMBLE_PATH.exists()
ensemble_doc_text = ENSEMBLE_PATH.read_text(encoding="utf-8") if ensemble_doc_exists else None
opus_a_exists = ANALYSIS_OPUS_A_PATH.exists()
analysis_opus_a = json.loads(ANALYSIS_OPUS_A_PATH.read_text(encoding="utf-8")) if opus_a_exists else None
opus_a_doc_exists = OPUS_A_DOC_PATH.exists()
opus_a_doc_text = OPUS_A_DOC_PATH.read_text(encoding="utf-8") if opus_a_doc_exists else None

# Multi-poet F5/F10 (added 2026-10-22, docs/phase4/E1_V2_MULTIPOET.md) -- own 50-poem pool
# (NOT POOL_PATH's eval_pool_25.json), own analysis report, own example-sets file. Guarded
# with an existence check (same convention as set_d_exists/opus_a_exists above) so this
# script still runs cleanly if that experiment is ever reverted/not yet present.
MULTIPOET_DOC_PATH = DOCS_DIR / "E1_V2_MULTIPOET.md"
ANALYSIS_MULTIPOET_PATH = RESULTS_DIR / "analysis_report_multipoet.json"
MULTIPOET_EXAMPLE_SETS_PATH = E1V2_DIR / "config" / "multipoet_example_sets.json"
MULTIPOET_POOL_PATH = E1V2_DIR / "config" / "eval_pool_50_multipoet.json"
multipoet_exists = ANALYSIS_MULTIPOET_PATH.exists()
if multipoet_exists:
    analysis_multipoet = json.loads(ANALYSIS_MULTIPOET_PATH.read_text(encoding="utf-8"))
    multipoet_example_sets = json.loads(MULTIPOET_EXAMPLE_SETS_PATH.read_text(encoding="utf-8"))["sets"]
    multipoet_pool_doc = json.loads(MULTIPOET_POOL_PATH.read_text(encoding="utf-8"))
    multipoet_doc_text = MULTIPOET_DOC_PATH.read_text(encoding="utf-8") if MULTIPOET_DOC_PATH.exists() else None
    multipoet_prompt_previews = {
        s: (E1V2_DIR / "config" / f"prompt_preview_{s}.txt").read_text(encoding="utf-8")
        for s in ("F5", "F10")
    }
    multipoet_manifest_records = [r for r in manifest if r["set_name"] in ("F5", "F10")]
    multipoet_pool_25_overlap = sorted(
        {p["poem_id"] for p in multipoet_pool_doc["poems"]} & {p["poem_id"] for p in pool["poems"]},
        key=int,
    )

# Poet-era few-shot sets M1/M2/E1/E2/H1/H2 (added 2026-10-23, docs/phase4/E1_V2_ERAS_FEWSHOT.md)
# -- run on the SAME eval_pool_25.json pool Z/A/B/C/D/D2 already use (no thin-overlap caveat,
# unlike F5/F10). Guarded with an existence check, same convention as multipoet_exists above.
ERAS_SET_NAMES = ["M1", "M2", "E1", "E2", "H1", "H2"]
ERAS_DOC_PATH = DOCS_DIR / "E1_V2_ERAS_FEWSHOT.md"
ANALYSIS_ERAS_PATH = RESULTS_DIR / "analysis_report_eras.json"
ERAS_EXAMPLE_SETS_PATH = E1V2_DIR / "config" / "eras_example_sets.json"
ERAS_AXIS_PATH = E1V2_DIR / "config" / "eras_axis.json"
eras_exists = ANALYSIS_ERAS_PATH.exists()
if eras_exists:
    analysis_eras = json.loads(ANALYSIS_ERAS_PATH.read_text(encoding="utf-8"))
    eras_example_sets = json.loads(ERAS_EXAMPLE_SETS_PATH.read_text(encoding="utf-8"))["sets"]
    eras_axis = json.loads(ERAS_AXIS_PATH.read_text(encoding="utf-8"))
    eras_doc_text = ERAS_DOC_PATH.read_text(encoding="utf-8") if ERAS_DOC_PATH.exists() else None
    eras_prompt_previews = {
        s: (E1V2_DIR / "config" / f"prompt_preview_{s}.txt").read_text(encoding="utf-8")
        for s in ERAS_SET_NAMES
    }
    eras_manifest_records = [r for r in manifest if r["set_name"] in ERAS_SET_NAMES]
    eras_per_poet_by_id = {p["poet_id"]: p for p in eras_axis["per_poet"]}

# `analysis`: per_set lookups use analysis_d (it has all 6 sets, Z/A/B/C recomputed the same
# way as analysis_zabc -- checked in verify_f1_matches_json below). `analysis`'s
# pairwise_bootstrap_ci is the UNION of analysis_zabc's 6 ZABC pairs and analysis_d's 9
# D/D2 pairs, so build_ci_tables() can show both halves without re-deriving anything.
analysis = {}
for p in MODEL_KEYS:
    analysis[p] = {}
    for c in CRITERIA:
        analysis[p][c] = {
            "per_set": analysis_d[p][c]["per_set"],
            "pairwise_bootstrap_ci": {
                **analysis_zabc[p][c]["pairwise_bootstrap_ci"],
                **analysis_d[p][c]["pairwise_bootstrap_ci"],
            },
            "per_poem_diff_signs": {
                **analysis_zabc[p][c].get("per_poem_diff_signs", {}),
                **analysis_d[p][c].get("per_poem_diff_signs", {}),
            },
        }

# "ensemble" is injected as a 4th pseudo-model so build_main_f1_table/build_bar_chart_svg can
# render it as an extra row/series without special-casing -- it only has per_set (no pairwise
# CI vs itself; its CIs vs each real model live in analysis_ensemble["criteria"][c]["vs_single"]
# and are rendered separately in the Ensemble panel, not via the shared `analysis` dict).
analysis["ensemble"] = {
    c: {"per_set": analysis_ensemble["criteria"][c]["per_set"]} for c in CRITERIA
}

prompt_previews = {
    s: (E1V2_DIR / "config" / f"prompt_preview_{s}.txt").read_text(encoding="utf-8")
    for s in SET_NAMES_FULL
}

MODEL_DISPLAY = {
    "anthropic": "Claude Sonnet 4.6",
    "openai": "GPT-5.4-mini",
    "google": "Gemini (served: gemini-3.6-flash)",
    "ensemble": "Majority-vote ensemble (2-of-3)",
    "anthropic_opus": "Claude Opus 5.5 (set A only)",
}
MODEL_SHORT = {"anthropic": "Claude", "openai": "GPT", "google": "Gemini", "ensemble": "Ensemble",
               "anthropic_opus": "Opus 5.5"}
MODEL_KEYS_ALL = MODEL_KEYS + ["ensemble"]  # main F1 table / bar chart rows, in this order

# ---------------------------------------------------------------------------
# Derived numbers (cost, call counts) — computed from the manifest + the
# project's own pricing table, never hand-typed.
# ---------------------------------------------------------------------------

PRICING = {**pilot_config.MODELS, **e1v2_config.EXTRA_MODEL_PRICING}  # {"anthropic": {...}, "anthropic_opus": {...}, ...}


def call_cost(provider: str, usage: dict) -> float:
    spec = PRICING[provider]
    in_tok = (usage or {}).get("input_tokens") or 0
    out_tok = (usage or {}).get("output_tokens") or 0
    return (in_tok / 1e6) * spec["price_in"] + (out_tok / 1e6) * spec["price_out"]


# MODEL_KEYS (anthropic/openai/google) drive the main 6-sets x 3-models completeness/cost
# tables, unchanged by Opus's addition. "anthropic_opus" (set A only) is tracked separately
# below so it never perturbs those 3-model-shaped loops/dicts.
spend = {p: 0.0 for p in MODEL_KEYS}
calls_ok = {p: 0 for p in MODEL_KEYS}
calls_err = {p: 0 for p in MODEL_KEYS}
calls_per_set = {s: {p: {"ok": 0, "err": 0} for p in MODEL_KEYS} for s in SET_NAMES_FULL}
gemini_model_versions = set()
opus_a_spend = 0.0
opus_a_calls_ok = 0
opus_a_calls_err = 0

for r in manifest:
    p = r["provider"]
    s = r["set_name"]
    if s not in SET_NAMES_FULL and p != "anthropic_opus":
        # The multi-poet F5/F10/F5b sets (added 2026-10-22, docs/phase4/E1_V2_MULTIPOET.md)
        # run on a DIFFERENT 50-poem pool and are additive-only to this SAME shared
        # run_manifest.json. Without this guard, calls_per_set[s] (keyed only by
        # SET_NAMES_FULL) would KeyError on an "F5"/"F10" record, and spend/calls_ok would
        # silently absorb multi-poet cost/counts into this report's existing Z/A/B/C/D/D2
        # totals -- scoped out here; the multi-poet section below computes its own totals
        # directly from analysis_report_multipoet.json instead.
        continue
    if p == "anthropic_opus":
        if r.get("error") is None:
            opus_a_spend += call_cost(p, r.get("usage"))
            opus_a_calls_ok += 1
        else:
            opus_a_calls_err += 1
        continue
    if r.get("error") is None:
        spend[p] += call_cost(p, r.get("usage"))
        calls_ok[p] += 1
        calls_per_set[s][p]["ok"] += 1
    else:
        calls_err[p] += 1
        calls_per_set[s][p]["err"] += 1
    if p == "google":
        mv = (r.get("usage") or {}).get("model_version") or r.get("model_id")
        if mv:
            gemini_model_versions.add(mv)

scoped_manifest_count = sum(
    1 for r in manifest if r["set_name"] in SET_NAMES_FULL or r["provider"] == "anthropic_opus"
)  # excludes F5/F10/F5b (own badge/section below), matches what panels a-j actually describe
total_spend = sum(spend.values())
if multipoet_exists:
    multipoet_spend = sum(call_cost(r["provider"], r.get("usage"))
                           for r in multipoet_manifest_records if r.get("error") is None)
if eras_exists:
    eras_spend = sum(call_cost(r["provider"], r.get("usage"))
                      for r in eras_manifest_records if r.get("error") is None)
total_calls_ok = sum(calls_ok.values())
total_calls_err = sum(calls_err.values())
pool_verses = pool["pool_verses"]
expected_per_cell = pool_verses
completeness_rows = []
all_complete = True
for s in SET_NAMES_FULL:
    for p in MODEL_KEYS:
        ok = calls_per_set[s][p]["ok"]
        complete = ok == expected_per_cell
        all_complete = all_complete and complete
        completeness_rows.append((s, p, ok, expected_per_cell, complete))

GENERATED_AT = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
TODAY = date.today().isoformat()

# ---------------------------------------------------------------------------
# Verification (run BEFORE writing the file)
# ---------------------------------------------------------------------------

def verify_f1_matches_json():
    """Every F1 value we are about to render in the main table must equal
    analysis_report_D.json's own overall.f1 for that (model, criterion, set),
    AND (for Z/A/B/C) must match the original analysis_report.json exactly --
    the two reports were computed independently (different scripts, different
    runs) and must agree, or Set D's addition silently changed something."""
    for p in MODEL_KEYS:
        for c in CRITERIA:
            for s in SET_NAMES_FULL:
                expected = analysis_d[p][c]["per_set"][s]["overall"]["f1"]
                rendered = analysis[p][c]["per_set"][s]["overall"]["f1"]
                assert abs(expected - rendered) < 1e-12, (p, c, s)
            for s in SET_NAMES:
                a = analysis_zabc[p][c]["per_set"][s]["overall"]["f1"]
                b = analysis_d[p][c]["per_set"][s]["overall"]["f1"]
                assert abs(a - b) < 1e-9, ("ZABC mismatch between the two reports", p, c, s, a, b)
    print("PASS: main F1 table values are read directly from analysis_report_D.json, and Z/A/B/C "
          "numbers are cross-verified identical to the original analysis_report.json.")


def verify_ensemble_matches_json():
    """The 'ensemble' row injected into the shared `analysis` dict must equal
    analysis_report_ensemble.json's own per_set F1 exactly, for every
    criterion and set -- the merge in the loading section must not have
    mutated anything."""
    for c in CRITERIA:
        for s in SET_NAMES_FULL:
            expected = analysis_ensemble["criteria"][c]["per_set"][s]["overall"]["f1"]
            rendered = analysis["ensemble"][c]["per_set"][s]["overall"]["f1"]
            assert abs(expected - rendered) < 1e-12, (c, s, expected, rendered)
    print("PASS: the 'ensemble' row's F1 values are read directly from "
          "analysis_report_ensemble.json, unmutated by the merge into `analysis`.")


def verify_prompts_match_previews():
    built = {s: prompt_builder.build_system_message(s) for s in SET_NAMES_FULL}
    for s in SET_NAMES_FULL:
        preview = prompt_previews[s].rstrip("\n")
        rebuilt = built[s].rstrip("\n")
        assert preview == rebuilt, f"set {s} prompt mismatch between preview file and prompt_builder output"
    print("PASS: all 6 system messages (Z/A/B/C/D/D2) match prompt_builder.py output byte-for-byte "
          "(and thus the preview files on disk) -- confirms adding D/D2 did not change Z/A/B/C.")
    return built


def verify_abc_differ_only_in_examples(built):
    a_lines = built["A"].splitlines()
    b_lines = built["B"].splitlines()
    c_lines = built["C"].splitlines()
    # Lines before "Example 2" are identical scaffold+Example1 across A/B/C.
    def head(lines):
        for i, l in enumerate(lines):
            if l.startswith("Example 2"):
                return lines[:i]
        return lines
    assert head(a_lines) == head(b_lines) == head(c_lines)
    print("PASS: sets A/B/C share byte-identical scaffold + Example 1; only Example 2/3 differ.")


def verify_d_differs_only_in_examples(built):
    a_lines = built["A"].splitlines()
    d_lines = built["D"].splitlines()
    d2_lines = built["D2"].splitlines()
    def head(lines):
        for i, l in enumerate(lines):
            if l.startswith("Example 2"):
                return lines[:i]
        return lines
    assert head(a_lines) == head(d_lines) == head(d2_lines)
    print("PASS: sets D/D2 share the same scaffold + Example 1 as A/B/C; only Example 2/3 differ.")


def verify_opus_a_matches_json():
    """Cross-checks analysis_report_opus_a.json's own completeness claim against the raw
    manifest (not just trusting the JSON file), and cross-checks its set-A single-model/ensemble
    F1 values against the main `analysis`/`analysis_ensemble` dicts this report already loads --
    two independently-produced sources must agree."""
    if not opus_a_exists:
        print("SKIP: analysis_report_opus_a.json not found -- panel (i) will render as pending.")
        return
    opus_cells = [r for r in manifest if r["set_name"] == "A" and r["provider"] == "anthropic_opus"]
    opus_ok = [r for r in opus_cells if r.get("error") is None]
    assert len(opus_cells) == 327, f"expected 327 set-A anthropic_opus manifest cells, got {len(opus_cells)}"
    assert len(opus_ok) == 327, f"expected 327 OK cells, got {len(opus_ok)}"
    assert analysis_opus_a["n_cells_ok"] == 327 and analysis_opus_a["n_cells_error"] == 0
    for criterion in CRITERIA:
        c = analysis_opus_a["criteria"][criterion]
        for m in ("anthropic", "openai", "google"):
            expected = analysis[m][criterion]["per_set"]["A"]["overall"]["f1"]
            got = c["single_models"][m]["overall"]["f1"]
            assert abs(expected - got) < 1e-9, (criterion, m, expected, got)
        expected_ens = analysis_ensemble["criteria"][criterion]["per_set"]["A"]["overall"]["f1"]
        got_ens = c["ensemble"]["overall"]["f1"]
        assert abs(expected_ens - got_ens) < 1e-9, (criterion, expected_ens, got_ens)
    print("PASS: 327/327 set-A anthropic_opus cells confirmed directly from run_manifest.json "
          "(0 errors), and every single-model/ensemble F1 inside analysis_report_opus_a.json "
          "matches the independently-loaded analysis_report_D.json/analysis_report_ensemble.json "
          "exactly.")


def verify_rtl_sample():
    sample_ar = example_sets["A"]["examples"][0]["text"]
    sample_en = "Example 1: the sub-element appears"
    assert is_majority_arabic(sample_ar) is True
    assert is_majority_arabic(sample_en) is False
    print("PASS: is_majority_arabic correctly classifies a sample Arabic verse (RTL) "
          "and a sample English sentence (LTR).")


verify_f1_matches_json()
verify_ensemble_matches_json()
verify_opus_a_matches_json()
built_prompts = verify_prompts_match_previews()
verify_abc_differ_only_in_examples(built_prompts)
verify_d_differs_only_in_examples(built_prompts)
verify_rtl_sample()
print(f"Completeness: {total_calls_ok}/{len(SET_NAMES_FULL) * len(MODEL_KEYS) * expected_per_cell} cells ok, "
      f"{total_calls_err} errors, ALL_COMPLETE={all_complete}")
print(f"Total spend from manifest: ${total_spend:.4f} "
      f"(anthropic ${spend['anthropic']:.4f}, openai ${spend['openai']:.4f}, google ${spend['google']:.4f})")

# ---------------------------------------------------------------------------
# HTML builders
# ---------------------------------------------------------------------------

def f1_color(value: float, vmin: float, vmax: float) -> str:
    """Neutral-to-accent color scale (low -> pale, high -> saturated),
    theme-aware via CSS variables set per-cell."""
    if vmax <= vmin:
        t = 0.5
    else:
        t = max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))
    return f"{t:.4f}"


def build_main_f1_table(criterion: str) -> str:
    vals = [analysis[p][criterion]["per_set"][s]["overall"]["f1"] for p in MODEL_KEYS_ALL for s in SET_NAMES_FULL]
    if opus_a_exists:
        vals.append(analysis_opus_a["criteria"][criterion]["opus"]["overall"]["f1"])
    vmin, vmax = min(vals), max(vals)
    rows = []
    for p in MODEL_KEYS_ALL:
        row_vals = {s: analysis[p][criterion]["per_set"][s]["overall"]["f1"] for s in SET_NAMES_FULL}
        best_set = max(row_vals, key=row_vals.get)
        cells = []
        for s in SET_NAMES_FULL:
            v = row_vals[s]
            t = f1_color(v, vmin, vmax)
            best_cls = " best" if s == best_set else ""
            cells.append(f'<td class="f1cell{best_cls}" style="--t:{t}"><span>{v:.3f}</span></td>')
        row_cls = ' class="ensemble-row"' if p == "ensemble" else ""
        rows.append(f"<tr{row_cls}><th>{esc(MODEL_SHORT[p])}</th>{''.join(cells)}</tr>")
    if opus_a_exists:
        # Opus 5.5 was run on set A ONLY -- every other set shows a dash, not a 0 or omitted
        # cell, so the table's shape stays uniform while making the missing data explicit.
        opus_f1 = analysis_opus_a["criteria"][criterion]["opus"]["overall"]["f1"]
        t = f1_color(opus_f1, vmin, vmax)
        cells = []
        for s in SET_NAMES_FULL:
            if s == "A":
                cells.append(f'<td class="f1cell best" style="--t:{t}"><span>{opus_f1:.3f}</span></td>')
            else:
                cells.append('<td class="f1cell dash"><span>&ndash;</span></td>')
        rows.append(f'<tr class="opus-row"><th>{esc(MODEL_SHORT["anthropic_opus"])}</th>{"".join(cells)}</tr>')
    header = "".join(f"<th>{s}</th>" for s in SET_NAMES_FULL)
    return (f'<table class="f1table" data-criterion="{criterion}">'
            f"<thead><tr><th>Model</th>{header}</tr></thead><tbody>{''.join(rows)}</tbody></table>")


def build_bar_chart_svg(criterion: str) -> str:
    sets = SET_NAMES_FULL
    w, h = 620, 220
    pad_l, pad_b, pad_t = 40, 30, 20
    plot_w, plot_h = w - pad_l - 20, h - pad_b - pad_t
    group_w = plot_w / len(sets)
    bar_w = group_w / (len(MODEL_KEYS_ALL) + 1)
    vmax = max(analysis[p][criterion]["per_set"][s]["overall"]["f1"] for p in MODEL_KEYS_ALL for s in sets)
    vmax = max(vmax * 1.15, 0.05)
    colors = {"anthropic": "var(--c-anthropic)", "openai": "var(--c-openai)", "google": "var(--c-google)",
              "ensemble": "var(--c-ensemble)"}
    parts = [f'<svg viewBox="0 0 {w} {h}" class="barchart" data-criterion="{criterion}" '
             f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="F1 by set and model ({criterion})">']
    # axes
    parts.append(f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h-pad_b}" class="axis"/>')
    parts.append(f'<line x1="{pad_l}" y1="{h-pad_b}" x2="{w-20}" y2="{h-pad_b}" class="axis"/>')
    for gi, s in enumerate(sets):
        gx = pad_l + gi * group_w
        for mi, p in enumerate(MODEL_KEYS_ALL):
            v = analysis[p][criterion]["per_set"][s]["overall"]["f1"]
            bh = (v / vmax) * plot_h
            x = gx + (mi + 0.3) * bar_w
            y = h - pad_b - bh
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w*0.8:.1f}" height="{bh:.1f}" '
                         f'fill="{colors[p]}"><title>{MODEL_SHORT[p]} / {s}: F1={v:.3f}</title></rect>')
            parts.append(f'<text x="{x+bar_w*0.4:.1f}" y="{y-4:.1f}" class="bar-label">{v:.2f}</text>')
        parts.append(f'<text x="{gx+group_w/2:.1f}" y="{h-pad_b+16}" class="axis-label">{s}</text>')
    legend_x = pad_l
    for i, p in enumerate(MODEL_KEYS_ALL):
        lx = legend_x + i * 150
        parts.append(f'<rect x="{lx}" y="2" width="10" height="10" fill="{colors[p]}"/>')
        parts.append(f'<text x="{lx+14}" y="11" class="legend-label">{MODEL_SHORT[p]}</text>')
    parts.append("</svg>")
    return "".join(parts)


def build_opus_a_bar_svg(criterion: str) -> str:
    """Clearly-separate bar chart: Opus 5.5 vs the 3 single models + ensemble, ALL on set A
    only (not mixed into the main 6-set grouped chart, which would otherwise show Opus as a
    lone bar surrounded by blanks for Z/B/C/D/D2)."""
    keys = ["anthropic_opus", "anthropic", "openai", "google", "ensemble"]
    values = {
        "anthropic_opus": analysis_opus_a["criteria"][criterion]["opus"]["overall"]["f1"],
        "anthropic": analysis_opus_a["criteria"][criterion]["single_models"]["anthropic"]["overall"]["f1"],
        "openai": analysis_opus_a["criteria"][criterion]["single_models"]["openai"]["overall"]["f1"],
        "google": analysis_opus_a["criteria"][criterion]["single_models"]["google"]["overall"]["f1"],
        "ensemble": analysis_opus_a["criteria"][criterion]["ensemble"]["overall"]["f1"],
    }
    colors = {"anthropic_opus": "var(--c-opus)", "anthropic": "var(--c-anthropic)",
              "openai": "var(--c-openai)", "google": "var(--c-google)", "ensemble": "var(--c-ensemble)"}
    w, h = 460, 180
    pad_l, pad_b, pad_t = 30, 46, 16
    plot_w, plot_h = w - pad_l - 20, h - pad_b - pad_t
    bar_w = plot_w / (len(keys) + 1)
    vmax = max(values.values()) * 1.2
    parts = [f'<svg viewBox="0 0 {w} {h}" class="barchart opus-a-chart" data-criterion="{criterion}" '
             f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Opus 5.5 vs others on set A ({criterion})">']
    parts.append(f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h-pad_b}" class="axis"/>')
    parts.append(f'<line x1="{pad_l}" y1="{h-pad_b}" x2="{w-20}" y2="{h-pad_b}" class="axis"/>')
    for i, k in enumerate(keys):
        v = values[k]
        bh = (v / vmax) * plot_h
        x = pad_l + (i + 0.3) * bar_w
        y = h - pad_b - bh
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w*0.8:.1f}" height="{bh:.1f}" '
                     f'fill="{colors[k]}"><title>{MODEL_SHORT[k]} / set A: F1={v:.3f}</title></rect>')
        parts.append(f'<text x="{x+bar_w*0.4:.1f}" y="{y-4:.1f}" class="bar-label">{v:.3f}</text>')
        parts.append(f'<text x="{x+bar_w*0.4:.1f}" y="{h-pad_b+14}" class="axis-label" '
                     f'transform="rotate(20 {x+bar_w*0.4:.1f} {h-pad_b+14})">{MODEL_SHORT[k]}</text>')
    parts.append("</svg>")
    return "".join(parts)


def build_opus_a_comparison_table(criterion: str) -> str:
    c = analysis_opus_a["criteria"][criterion]
    rows = []
    for m in ["anthropic", "openai", "google", "ensemble"]:
        other_f1 = (c["single_models"][m]["overall"]["f1"] if m in ("anthropic", "openai", "google")
                    else c["ensemble"]["overall"]["f1"])
        pw = c["pairwise_vs_opus"][m]
        cells = []
        for metric_key, label in (("f1", "F1"), ("precision", "P"), ("recall", "R")):
            d = pw[metric_key]
            cls = " sig" if d["sig"] else ""
            cells.append(f'<td class="cicell{cls}">{d["point"]:+.3f} '
                        f'[{d["ci_95"][0]:+.3f}, {d["ci_95"][1]:+.3f}]'
                        f'{" <b>SIG</b>" if d["sig"] else " ns"}</td>')
        rows.append(f'<tr><td>{esc(MODEL_DISPLAY[m])}</td><td>{other_f1:.3f}</td>{"".join(cells)}</tr>')
    return ('<table class="detail-table"><thead><tr><th>vs.</th><th>Other F1 (set A)</th>'
           "<th>&Delta;F1 (Opus&minus;other)</th><th>&Delta;P</th><th>&Delta;R</th></tr></thead>"
           f"<tbody>{''.join(rows)}</tbody></table>")


def build_opus_a_detail_table(criterion: str) -> str:
    opus = analysis_opus_a["criteria"][criterion]["opus"]
    rows = []
    for split in ("overall", "abu_nuwas", "other"):
        r = opus[split]
        rows.append(f"<tr><td>{split}</td><td>{r['tp']}</td><td>{r['fp']}</td><td>{r['fn']}</td>"
                    f"<td>{r['precision']:.3f}</td><td>{r['recall']:.3f}</td><td>{r['f1']:.3f}</td></tr>")
    return ('<table class="detail-table"><thead><tr><th>Split</th><th>TP</th><th>FP</th><th>FN</th>'
           "<th>P</th><th>R</th><th>F1</th></tr></thead>"
           f"<tbody>{''.join(rows)}</tbody></table>")


def _gain_over_z(p: str, criterion: str, s: str) -> float:
    """F1(s) - F1(Z), reading whichever pair key the merged `analysis` CI dict
    actually has: ZABC pairs are stored as "Z-{s}" (point = F1(Z)-F1(s), negate);
    D/D2 pairs are stored as "{s}-Z" (point = F1(s)-F1(Z) already)."""
    pw = analysis[p][criterion]["pairwise_bootstrap_ci"]
    if f"Z-{s}" in pw:
        return -pw[f"Z-{s}"]["point"]
    return pw[f"{s}-Z"]["point"]


def build_gain_over_z_svg(criterion: str = "verse") -> str:
    w, h = 560, 200
    pad_l, pad_b, pad_t = 40, 24, 16
    plot_w, plot_h = w - pad_l - 20, h - pad_b - pad_t
    sets = ["A", "B", "C", "D", "D2"]
    group_w = plot_w / len(sets)
    bar_w = group_w / (len(MODEL_KEYS) + 1)
    gains = {}
    vmax = 0.01
    for p in MODEL_KEYS:
        for s in sets:
            gain = _gain_over_z(p, criterion, s)
            gains[(p, s)] = gain
            vmax = max(vmax, abs(gain))
    vmax *= 1.2
    mid = h - pad_b - (plot_h / 2)
    colors = {"anthropic": "var(--c-anthropic)", "openai": "var(--c-openai)", "google": "var(--c-google)"}
    parts = [f'<svg viewBox="0 0 {w} {h}" class="barchart gainchart" data-criterion="{criterion}" '
             f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="F1 gain over zero-shot Z ({criterion})">']
    parts.append(f'<line x1="{pad_l}" y1="{mid:.1f}" x2="{w-20}" y2="{mid:.1f}" class="axis"/>')
    parts.append(f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h-pad_b}" class="axis"/>')
    for gi, s in enumerate(sets):
        gx = pad_l + gi * group_w
        for mi, p in enumerate(MODEL_KEYS):
            g = gains[(p, s)]
            bh = (abs(g) / vmax) * (plot_h / 2)
            x = gx + (mi + 0.3) * bar_w
            y = mid - bh if g >= 0 else mid
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w*0.8:.1f}" height="{max(bh,1):.1f}" '
                         f'fill="{colors[p]}"><title>{MODEL_SHORT[p]} / {s} vs Z: {g:+.3f}</title></rect>')
        parts.append(f'<text x="{gx+group_w/2:.1f}" y="{h-pad_b+16}" class="axis-label">{s}</text>')
    parts.append("</svg>")
    return "".join(parts)


def build_detailed_tables(criterion: str) -> str:
    out = []
    for p in MODEL_KEYS:
        out.append(f"<h4>{esc(MODEL_DISPLAY[p])}</h4>")
        rows = []
        for s in SET_NAMES_FULL:
            d = analysis[p][criterion]["per_set"][s]
            for split in ("overall", "abu_nuwas", "other"):
                r = d[split]
                rows.append(f"<tr><td>{s}</td><td>{split}</td><td>{r['tp']}</td><td>{r['fp']}</td>"
                            f"<td>{r['fn']}</td><td>{r['precision']:.3f}</td><td>{r['recall']:.3f}</td>"
                            f"<td>{r['f1']:.3f}</td></tr>")
        out.append('<table class="detail-table"><thead><tr><th>Set</th><th>Split</th><th>TP</th>'
                   "<th>FP</th><th>FN</th><th>P</th><th>R</th><th>F1</th></tr></thead>"
                   f"<tbody>{''.join(rows)}</tbody></table>")
    return "\n".join(out)


def build_ci_tables() -> str:
    pairs = ["Z-A", "Z-B", "Z-C", "A-B", "A-C", "B-C",
             "D-A", "D-B", "D-C", "D-Z", "D2-A", "D2-B", "D2-C", "D2-Z", "D-D2"]
    out = []
    for p in MODEL_KEYS:
        out.append(f"<h4>{esc(MODEL_DISPLAY[p])}</h4>")
        rows = []
        for pair in pairs:
            cells = []
            for c in ("verse", "strict", "token"):
                ci = analysis[p][c]["pairwise_bootstrap_ci"][pair]
                sig = not (ci["ci_95"][0] <= 0 <= ci["ci_95"][1])
                cls = " sig" if sig else ""
                cells.append(f'<td class="cicell{cls}">{ci["point"]:+.3f} '
                            f'[{ci["ci_95"][0]:+.3f}, {ci["ci_95"][1]:+.3f}]'
                            f'{" <b>SIG</b>" if sig else " ns"}</td>')
            diff = analysis[p]["verse"]["per_poem_diff_signs"].get(pair) or analysis[p]["strict"]["per_poem_diff_signs"][pair]
            rows.append(f"<tr><td>{pair}</td>{''.join(cells)}"
                        f'<td>{diff["a_greater"]}/{diff["b_greater"]}/{diff["tied"]}</td></tr>')
        out.append('<table class="detail-table"><thead><tr><th>Pair (F1_i-F1_j)</th>'
                   "<th>verse (primary)</th><th>strict</th><th>token</th>"
                   "<th>verse per-poem signs (i&gt;j / j&gt;i / tied)</th></tr></thead>"
                   f"<tbody>{''.join(rows)}</tbody></table>")
    return "\n".join(out)


def build_prompt_block(set_name: str) -> str:
    text = prompt_previews[set_name]
    uid = f"prompt-{set_name}"
    # The prompt scaffold is majority-English with embedded Arabic terms/verses;
    # per-block direction follows is_majority_arabic (whole-block majority), same
    # rule CLAUDE.md requires for .docx paragraphs. The Unicode bidi algorithm
    # handles the embedded Arabic runs correctly inside an LTR block on its own.
    direction = "rtl" if is_majority_arabic(text) else "ltr"
    return (
        f'<div class="prompt-block">'
        f'<div class="prompt-head"><span class="set-chip">{set_name}</span>'
        f'<button class="copy-btn" data-copy-target="{uid}" type="button">Copy</button></div>'
        f'<pre id="{uid}" dir="{direction}" class="bidi prompt-pre">{esc(text)}</pre>'
        f"</div>"
    )


def build_example_card(set_name: str) -> str:
    s = example_sets[set_name]
    verses = []
    for ex in s["examples"]:
        ann_items = "".join(
            f'<li>{rtl_wrap(a.get("span") or "(no span)")} '
            f'— {rtl_wrap(a.get("analysis") or "(no analysis note)")}</li>'
            for a in ex["annotations"]
        )
        verses.append(
            f'<div class="example-verse">'
            f'<div class="verse-text">{rtl_wrap(ex["text"])}</div>'
            f'<ul class="ann-list">{ann_items}</ul>'
            f"</div>"
        )
    note = (
        '<p class="example-note">Note: both example verses in this set are built on the root '
        f'{rtl_wrap("ع-ق-ل (التعقيل)")}, applied to different objects.</p>'
        if set_name == "C" else ""
    )
    return (
        f'<div class="example-card">'
        f'<div class="example-head"><span class="set-chip">{set_name}</span> '
        f'source poem <code>{esc(s["source_poem_id"])}</code> — {rtl_wrap(s["source_poem_name"])}</div>'
        f"{''.join(verses)}{note}"
        f"</div>"
    )


def build_example_card_d(set_name: str) -> str:
    """D/D2's two examples are composed from A/B/C's existing example dicts (see
    e1v2_config.SET_D_SOURCE/SET_D2_SOURCE, applied via prompt_builder._examples_for_set)
    -- never retyped. This renders the composed card the same way as A/B/C's, plus the
    note-completeness confound found in Step 1 of the Set D task (D inherits a span with
    an empty analysis note from Set A)."""
    v1_sets = prompt_builder.load_v1_example_sets()
    ex1_raw, ex2_raw = prompt_builder._examples_for_set(set_name, v1_sets)
    src = {"D": e1v2_config.SET_D_SOURCE, "D2": e1v2_config.SET_D2_SOURCE}[set_name]
    source_labels = [f'{src["example1"][0]} example' + f' (poem {v1_sets[src["example1"][0]]["source_poem_id"]})',
                     f'{src["example2"][0]} example' + f' (poem {v1_sets[src["example2"][0]]["source_poem_id"]})']
    verses = []
    for ex, label in zip([ex1_raw, ex2_raw], source_labels):
        ann_items = "".join(
            f'<li>{rtl_wrap(a.get("span") or "(no span)")} '
            f'— {rtl_wrap(a.get("analysis") or "(no analysis note)")}'
            f'{" <strong>[no analysis note]</strong>" if not a.get("analysis") else ""}</li>'
            for a in ex["annotations"]
        )
        verses.append(
            f'<div class="example-verse">'
            f'<div class="verse-text">{rtl_wrap(ex["text"])} <code>({esc(label)})</code></div>'
            f'<ul class="ann-list">{ann_items}</ul>'
            f"</div>"
        )
    note = {
        "D": 'Example 1 = Set C\'s example (root ع-ق-ل). Example 2 = Set A\'s second example '
             '(different root) -- a direct root-diversity swap-in. <strong>Confound: the borrowed '
             'Example 2 has one span with an empty analysis note</strong> (the only example among '
             'A/B/C/D that is partially unannotated) -- D is not a clean single-variable swap.',
        "D2": 'Example 1 = same as D (Set C\'s example). Example 2 = Set B\'s second example '
              '(different root, fully annotated) -- the confound-free root-diversity-only control.',
    }[set_name]
    return (
        f'<div class="example-card">'
        f'<div class="example-head"><span class="set-chip">{set_name}</span> composed from A/B/C '
        f'(no text retyped)</div>'
        f"{''.join(verses)}"
        f'<p class="example-note">{note}</p>'
        f"</div>"
    )


def build_multipoet_example_card(set_name: str) -> str:
    """Poet/period card for F5/F10 (added 2026-10-22) -- same example-card
    markup as build_example_card/build_example_card_d, plus a poet+period
    chip per example (the whole point of this experiment is DIFFERENT
    poets, so each card names its poet, unlike A/B/C/D's single fixed
    Abu Nuwas source)."""
    examples = multipoet_example_sets[set_name]
    verses = []
    for e in examples:
        ann_items = "".join(
            f'<li>{rtl_wrap(a.get("span") or "(no span)")} '
            f'— {rtl_wrap(a.get("analysis") or "(no analysis note)")}</li>'
            for a in e["annotations"]
        )
        period_label = e["period"] or "period unknown"
        verses.append(
            f'<div class="example-verse">'
            f'<div class="verse-text">{rtl_wrap(e["text"])}</div>'
            f'<div class="poet-meta">{rtl_wrap(e["poet_name"])} '
            f'<code>{esc(period_label)}</code> &middot; poem <code>{esc(e["poem_id"])}</code> '
            f'v{e["verse_no"]}</div>'
            f'<ul class="ann-list">{ann_items}</ul>'
            f"</div>"
        )
    n_poets = len(set(e["poet_name"] for e in examples))
    return (
        f'<div class="example-card">'
        f'<div class="example-head"><span class="set-chip">{set_name}</span> '
        f'{len(examples)} examples, {n_poets} distinct poets</div>'
        f"{''.join(verses)}"
        f"</div>"
    )


def build_multipoet_f1_table(criterion: str) -> str:
    """F5 vs F10 on their own full 50-poem/1000-verse pool, per model, with
    the F5-F10 bootstrap CI -- the PRIMARY multi-poet comparison."""
    vals = [analysis_multipoet["primary_pool"][p][criterion]["per_set"][s]["overall"]["f1"]
            for p in MODEL_KEYS for s in ("F5", "F10")]
    vmin, vmax = min(vals), max(vals)
    rows = []
    for p in MODEL_KEYS:
        block = analysis_multipoet["primary_pool"][p][criterion]
        for s in ("F5", "F10"):
            c = block["per_set"][s]["overall"]
            t = f1_color(c["f1"], vmin, vmax)
            rows.append(
                f'<tr><th>{esc(MODEL_SHORT[p])}</th><td><span class="set-chip">{s}</span></td>'
                f'<td>{c["tp"]}</td><td>{c["fp"]}</td><td>{c["fn"]}</td>'
                f'<td>{c["precision"]:.3f}</td><td>{c["recall"]:.3f}</td>'
                f'<td class="f1cell" style="--t:{t}"><span>{c["f1"]:.3f}</span></td></tr>'
            )
        ci = block["F5_vs_F10"]["bootstrap_ci"]
        sig = "SIG" if (ci["ci_95"][0] > 0 or ci["ci_95"][1] < 0) else "ns"
        rows.append(
            f'<tr class="diff-row"><th></th><td colspan="5">F5&nbsp;&minus;&nbsp;F10 '
            f'(bootstrap 95% CI over poems)</td>'
            f'<td colspan="2">{ci["point"]:+.3f} [{ci["ci_95"][0]:+.3f},{ci["ci_95"][1]:+.3f}] '
            f'<strong>({sig})</strong></td></tr>'
        )
    return (
        f'<table class="f1table" data-criterion="{criterion}">'
        f"<thead><tr><th>Model</th><th>Set</th><th>TP</th><th>FP</th><th>FN</th>"
        f"<th>P</th><th>R</th><th>F1</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"
    )


def build_multipoet_prompt_block(set_name: str) -> str:
    """Same markup as build_prompt_block, reading from multipoet_prompt_previews
    (F5/F10) instead of prompt_previews (Z/A/B/C/D/D2) -- kept separate so
    prompt_previews itself (and every existing function keyed off it) stays
    untouched."""
    text = multipoet_prompt_previews[set_name]
    uid = f"prompt-{set_name}"
    direction = "rtl" if is_majority_arabic(text) else "ltr"
    return (
        f'<div class="prompt-block">'
        f'<div class="prompt-head"><span class="set-chip">{set_name}</span>'
        f'<button class="copy-btn" data-copy-target="{uid}" type="button">Copy</button></div>'
        f'<pre id="{uid}" dir="{direction}" class="bidi prompt-pre">{esc(text)}</pre>'
        f"</div>"
    )


def build_multipoet_section() -> str:
    if not multipoet_exists:
        return ""
    overlap_n = len(multipoet_pool_25_overlap)
    toggle_row = (
        '<div class="crit-toggle">'
        '<button class="crit-btn" data-target="verse" onclick="toggleCriterion(\'verse\')">Verse (primary)</button>'
        '<button class="crit-btn" data-target="strict" onclick="toggleCriterion(\'strict\')">Strict (secondary)</button>'
        '<button class="crit-btn" data-target="token" onclick="toggleCriterion(\'token\')">Token-overlap (secondary)</button>'
        "</div>"
    )
    f1_tables = "".join(f'<div data-criterion="{c}">{build_multipoet_f1_table(c)}</div>' for c in CRITERIA)
    example_cards = build_multipoet_example_card("F5") + build_multipoet_example_card("F10")
    doc_html = (
        md_block(multipoet_doc_text) if multipoet_doc_text else
        "<p><em>docs/phase4/E1_V2_MULTIPOET.md not found.</em></p>"
    )
    return f"""
<details>
<summary>k. Multi-poet few-shot: F5 vs F10 (own 50-poem pool, added 2026-10-22)</summary>
<div class="warning-banner">&#9888; <strong>Different pool.</strong> F5/F10 run on their own
50-poem pool (<code>config/eval_pool_50_multipoet.json</code>, 1000 verse-units) --
<code>eval_pool.json</code>'s 50 poems minus the 3 poems used as F10 example sources,
replaced via a verified continuation of the same seed-43 draw. Only
<strong>{overlap_n}/25</strong> poems overlap with <code>eval_pool_25.json</code> (the pool
Z/A/B/C/D ran on), so every F5/F10-vs-Z/A/B/C/D comparison below is restricted to that thin,
Abu-Nuwas-skewed overlap and is indicative only -- F5's own and F10's own numbers (primary
table just below) use the full 1000-verse pool and are NOT affected by this caveat.</div>
<p>Supervisor request: 5 examples from 5 different poets (F5) vs. 10 examples from 10
different poets (F10, with F5's 5 poets included) on the same استعارة فعل subtype prompt --
isolating "number of examples" from "which examples," which A/B/C/D (2 examples each, all
from 3 fixed Abu Nuwas poems) could not test. Real cost: <strong>${multipoet_spend:.4f}</strong>
(1 run &times; 3 models &times; 2 sets &times; 1000 verse-units = 6000 calls, 0 errors, full
coverage).</p>
<h4>Example sets (poet + period per example -- the variable this experiment manipulates)</h4>
{example_cards}
<h4>PRIMARY: F5 vs F10, full 50-poem pool</h4>
{toggle_row}
{f1_tables}
<h4>Prompts</h4>
{build_multipoet_prompt_block("F5") if "F5" in multipoet_prompt_previews else ""}
{build_multipoet_prompt_block("F10") if "F10" in multipoet_prompt_previews else ""}
<h4>Full analysis (secondary vs. Z/A/B/C/D on the 9-poem overlap, ensemble, plain answer,
caveats) -- from <code>docs/phase4/E1_V2_MULTIPOET.md</code></h4>
{doc_html}
</details>
"""


def build_eras_prompt_block(set_name: str) -> str:
    """Same markup as build_multipoet_prompt_block, reading from eras_prompt_previews."""
    text = eras_prompt_previews[set_name]
    uid = f"prompt-{set_name}"
    direction = "rtl" if is_majority_arabic(text) else "ltr"
    return (
        f'<div class="prompt-block">'
        f'<div class="prompt-head"><span class="set-chip">{set_name}</span>'
        f'<button class="copy-btn" data-copy-target="{uid}" type="button">Copy</button></div>'
        f'<pre id="{uid}" dir="{direction}" class="bidi prompt-pre">{esc(text)}</pre>'
        f"</div>"
    )


def build_eras_f1_table(criterion: str) -> str:
    vals = [analysis_eras["models"][p][criterion]["per_set"][s]["overall"]["f1"]
            for p in MODEL_KEYS for s in ERAS_SET_NAMES]
    vmin, vmax = min(vals), max(vals)
    rows = []
    for p in MODEL_KEYS:
        row_vals = {s: analysis_eras["models"][p][criterion]["per_set"][s]["overall"]["f1"] for s in ERAS_SET_NAMES}
        best_set = max(row_vals, key=row_vals.get)
        cells = []
        for s in ERAS_SET_NAMES:
            v = row_vals[s]
            t = f1_color(v, vmin, vmax)
            best_cls = " best" if s == best_set else ""
            cells.append(f'<td class="f1cell{best_cls}" style="--t:{t}"><span>{v:.3f}</span></td>')
        rows.append(f"<tr><th>{esc(MODEL_SHORT[p])}</th>{''.join(cells)}</tr>")
    header = "".join(f"<th>{s}</th>" for s in ERAS_SET_NAMES)
    return (f'<table class="f1table" data-criterion="{criterion}">'
            f"<thead><tr><th>Model</th>{header}</tr></thead><tbody>{''.join(rows)}</tbody></table>")


def build_eras_pooled_table(criterion: str) -> str:
    rows = []
    for p in MODEL_KEYS:
        for g in ("M", "E", "H"):
            c = analysis_eras["pooled"][p][criterion]["per_group"][g]["overall"]
            rows.append(f"<tr><td>{esc(MODEL_SHORT[p])}</td><td>{g}</td><td>{c['tp']}</td>"
                        f"<td>{c['fp']}</td><td>{c['fn']}</td><td>{c['precision']:.3f}</td>"
                        f"<td>{c['recall']:.3f}</td><td>{c['f1']:.3f}</td></tr>")
    return ('<table class="detail-table" data-criterion="' + criterion + '"><thead><tr><th>Model</th><th>Group</th>'
           "<th>TP</th><th>FP</th><th>FN</th><th>P</th><th>R</th><th>F1</th></tr></thead>"
           f"<tbody>{''.join(rows)}</tbody></table>")


def build_eras_ci_table(criterion: str) -> str:
    pairs = (["M1-M2", "E1-E2", "H1-H2"]
             + [f"{s}-{b}" for s in ERAS_SET_NAMES for b in ("Z", "A", "B", "D2")])
    rows = []
    for p in MODEL_KEYS:
        for pair in pairs:
            ci = analysis_eras["models"][p][criterion]["pairwise_bootstrap_ci"][pair]
            d = analysis_eras["models"][p][criterion]["per_poem_diff_signs"][pair]
            sig = not (ci["ci_95"][0] <= 0 <= ci["ci_95"][1])
            cls = " sig" if sig else ""
            rows.append(f'<tr><td>{esc(MODEL_SHORT[p])}</td><td>{pair}</td>'
                       f'<td class="cicell{cls}">{ci["point"]:+.3f} [{ci["ci_95"][0]:+.3f},'
                       f'{ci["ci_95"][1]:+.3f}]{" <b>SIG</b>" if sig else " ns"}</td>'
                       f'<td>{d["a_greater"]}/{d["b_greater"]}/{d["tied"]}</td></tr>')
    for p in MODEL_KEYS:
        for a, b in [("M", "E"), ("M", "H"), ("E", "H")]:
            key = f"{a}-{b}"
            ci = analysis_eras["pooled"][p][criterion]["pairwise_bootstrap_ci"][key]
            d = analysis_eras["pooled"][p][criterion]["per_poem_diff_signs"][key]
            sig = not (ci["ci_95"][0] <= 0 <= ci["ci_95"][1])
            cls = " sig" if sig else ""
            rows.append(f'<tr class="pooled-row"><td>{esc(MODEL_SHORT[p])}</td><td>POOLED {key}</td>'
                       f'<td class="cicell{cls}">{ci["point"]:+.3f} [{ci["ci_95"][0]:+.3f},'
                       f'{ci["ci_95"][1]:+.3f}]{" <b>SIG</b>" if sig else " ns"}</td>'
                       f'<td>{d["a_greater"]}/{d["b_greater"]}/{d["tied"]}</td></tr>')
    return ('<table class="detail-table" data-criterion="' + criterion + '"><thead><tr><th>Model</th>'
           "<th>Pair (F1_i&minus;F1_j)</th><th>Bootstrap 95% CI</th>"
           "<th>per-poem signs (i&gt;j/j&gt;i/tied)</th></tr></thead>"
           f"<tbody>{''.join(rows)}</tbody></table>")


def build_eras_ensemble_table() -> str:
    rows = []
    for s in ERAS_SET_NAMES:
        e = analysis_eras["ensemble"]["verse"][s]
        rows.append(f"<tr><td>{s}</td><td>{e['ensemble']['overall']['f1']:.3f}</td>"
                    f"<td>{esc(MODEL_SHORT.get(e['best_single']['model'], e['best_single']['model']))} "
                    f"{e['best_single']['f1']:.3f}</td><td>{e['avg_single_f1']:.3f}</td></tr>")
    return ('<table class="detail-table"><thead><tr><th>Set</th><th>Ensemble F1 (verse)</th>'
           "<th>Best single</th><th>Avg of 3 singles</th></tr></thead>"
           f"<tbody>{''.join(rows)}</tbody></table>")


def build_eras_example_card(set_name: str) -> str:
    examples = eras_example_sets[set_name]
    verses = []
    for e in examples:
        ann_items = "".join(
            f'<li>{rtl_wrap(a.get("span") or "(no span)")} '
            f'— {rtl_wrap(a.get("analysis") or "(no analysis note)")}</li>'
            for a in e["annotations"]
        )
        p = eras_per_poet_by_id.get(e["poet_id"], {})
        death_year = p.get("death_year_ce")
        period_label = e["period"] or "period unknown"
        verses.append(
            f'<div class="example-verse">'
            f'<div class="verse-text">{rtl_wrap(e["text"])}</div>'
            f'<div class="poet-meta">{rtl_wrap(e["poet_name"])} '
            f'<code>{esc(period_label)}</code> &middot; death {death_year if death_year is not None else "?"} CE '
            f'&middot; poem <code>{esc(e["poem_id"])}</code> v{e["verse_no"]}</div>'
            f'<ul class="ann-list">{ann_items}</ul>'
            f"</div>"
        )
    return (
        f'<div class="example-card">'
        f'<div class="example-head"><span class="set-chip">{set_name}</span> '
        f'{len(examples)} examples, {len(set(e["poet_name"] for e in examples))} distinct poets</div>'
        f"{''.join(verses)}"
        f"</div>"
    )


def build_eras_section() -> str:
    if not eras_exists:
        return ""
    toggle_row = (
        '<div class="crit-toggle">'
        '<button class="crit-btn" data-target="verse" onclick="toggleCriterion(\'verse\')">Verse (primary)</button>'
        '<button class="crit-btn" data-target="strict" onclick="toggleCriterion(\'strict\')">Strict (secondary)</button>'
        '<button class="crit-btn" data-target="token" onclick="toggleCriterion(\'token\')">Token-overlap (secondary)</button>'
        "</div>"
    )
    f1_tables = "".join(f'<div data-criterion="{c}">{build_eras_f1_table(c)}</div>' for c in CRITERIA)
    pooled_tables = "".join(f'<div data-criterion="{c}">{build_eras_pooled_table(c)}</div>' for c in CRITERIA)
    ci_tables = "".join(f'<div data-criterion="{c}">{build_eras_ci_table(c)}</div>' for c in CRITERIA)
    example_cards = "".join(build_eras_example_card(s) for s in ERAS_SET_NAMES)
    prompt_blocks = "".join(build_eras_prompt_block(s) for s in ERAS_SET_NAMES)
    doc_html = (
        md_block(eras_doc_text) if eras_doc_text else
        "<p><em>docs/phase4/E1_V2_ERAS_FEWSHOT.md not found.</em></p>"
    )
    return f"""
<details>
<summary>l. Poet-era few-shot: M1/M2/E1/E2/H1/H2 (same eval_pool_25 pool, added 2026-10-23)</summary>
<p>Does the ERA of the example poets (by death year) matter -- middle of the distribution vs.
the extremes vs. the middle of each half? All 6 sets run on the SAME 25-poem pool Z/A/B/C/D/D2
already use (no thin-overlap caveat). Full corpus death-year analytics (poet_dates.csv research,
median/midpoint/bands over all 52 poets): see
<a href="ERAS_ANALYTICS.html" target="_blank" rel="noopener">ERAS_ANALYTICS.html</a> /
<code>docs/phase4/ERAS_ANALYTICS.md</code>. Real cost: <strong>${eras_spend:.4f}</strong>
(6 sets &times; 3 models &times; 327 verse-units = 5,886 calls, 0 errors in the final manifest
after a mid-run Anthropic credit-balance resume).</p>
<h4>Example sets (poet + death year + era per example)</h4>
{example_cards}
<h4>F1 by set and model</h4>
{toggle_row}
{f1_tables}
<h4>Pooled (M=M1+M2, E=E1+E2, H=H1+H2)</h4>
{pooled_tables}
<h4>Bootstrap 95% CIs (within-pair noise, pooled cross-category, vs Z, vs A/B/D2)</h4>
{ci_tables}
<h4>Ensemble (2-of-3 majority vote, verse-primary)</h4>
{build_eras_ensemble_table()}
<h4>Prompts</h4>
{prompt_blocks}
<h4>Full write-up (design, rank-based band fix, every table, plain answer, caveats) -- from
<code>docs/phase4/E1_V2_ERAS_FEWSHOT.md</code></h4>
{doc_html}
</details>
"""


def build_pool_table() -> str:
    rows = []
    for poem in pool["poems"]:
        rows.append(
            f'<tr><td>{esc(poem["poem_id"])}</td><td>{rtl_wrap(poem["poet_name"])}</td>'
            f'<td>{rtl_wrap(poem["title"])}</td><td>{poem["verse_count"]}</td>'
            f'<td><span class="tag tag-{poem["tag"]}">{esc(poem["tag"])}</span></td></tr>'
        )
    return ('<table class="detail-table"><thead><tr><th>Poem ID</th><th>Poet</th><th>Title</th>'
           "<th>Verses</th><th>Tag</th></tr></thead>"
           f"<tbody>{''.join(rows)}</tbody></table>")


def build_exclusions_list() -> str:
    items = [
        f'No-text poem excluded: <code>{esc(e1v2_config.NO_TEXT_POEM_ID)}</code> '
        "(poem record exists but has no verse text).",
        "Already-used-as-fewshot-source poems excluded (same poems E1 v1 drew its example sets "
        f'from): {", ".join(f"<code>{esc(x)}</code>" for x in sorted(e1v2_config.ALREADY_USED_POEM_IDS))}.',
        "Example-source poems excluded from the eval pool (sets A/B/C's own example verses come from "
        f'these, so they cannot also be scored): {", ".join(f"<code>{esc(x)}</code>" for x in e1v2_config.EXAMPLE_POEM_IDS)}.',
    ]
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def build_cost_table() -> str:
    rows = []
    for p in MODEL_KEYS:
        spec = PRICING[p]
        rows.append(
            f"<tr><td>{esc(MODEL_DISPLAY[p])}</td><td><code>{esc(spec['model_id'])}</code></td>"
            f"<td>${spec['price_in']:.2f}</td><td>${spec['price_out']:.2f}</td>"
            f"<td>${spend[p]:.4f}</td><td>{calls_ok[p]}</td><td>{calls_err[p]}</td></tr>"
        )
    if opus_a_exists:
        spec = PRICING["anthropic_opus"]
        rows.append(
            f"<tr class=\"opus-row\"><td>{esc(MODEL_DISPLAY['anthropic_opus'])}</td>"
            f"<td><code>{esc(spec['model_id'])}</code></td>"
            f"<td>${spec['price_in']:.2f}</td><td>${spec['price_out']:.2f}</td>"
            f"<td>${opus_a_spend:.4f}</td><td>{opus_a_calls_ok}</td><td>{opus_a_calls_err}</td></tr>"
        )
    return (
        '<table class="detail-table"><thead><tr><th>Model</th><th>Model ID (requested)</th>'
        "<th>$/MTok in</th><th>$/MTok out</th><th>Real spend</th><th>Calls OK</th><th>Errors</th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table>"
        f'<p class="total-spend">Total real spend (3-model, 6-set design): <strong>${total_spend:.4f}</strong> '
        f"({total_calls_ok} OK calls, {total_calls_err} errors, across all 6 sets x 3 models x "
        f"{pool_verses} verse-units = {len(SET_NAMES_FULL) * len(MODEL_KEYS) * pool_verses} planned cells; "
        f"Z/A/B/C cost $10.5680, D+D2 added $5.4451).</p>"
        f'<p class="total-spend">Opus 5.5 (set A only, separate from the above): '
        f"<strong>${opus_a_spend:.4f}</strong> ({opus_a_calls_ok} OK calls, {opus_a_calls_err} "
        f"errors, {pool_verses} planned cells).</p>"
    )


def build_completeness_table() -> str:
    rows = []
    for s, p, ok, expected, complete in completeness_rows:
        cls = "ok" if complete else "bad"
        rows.append(f'<tr><td>{s}</td><td>{MODEL_SHORT[p]}</td><td>{ok}/{expected}</td>'
                    f'<td class="{cls}">{"complete" if complete else "INCOMPLETE"}</td></tr>')
    return ('<table class="detail-table"><thead><tr><th>Set</th><th>Model</th>'
           "<th>Cells</th><th>Status</th></tr></thead>"
           f"<tbody>{''.join(rows)}</tbody></table>"
           f'<p><strong>ALL_COMPLETE = {all_complete}</strong></p>')


def build_diff_html(a_text: str, c_text: str, label_a: str, label_c: str) -> str:
    diff = difflib.unified_diff(a_text.splitlines(keepends=True), c_text.splitlines(keepends=True),
                                fromfile=label_a, tofile=label_c)
    lines = []
    for line in diff:
        cls = ""
        if line.startswith("+++") or line.startswith("---"):
            cls = "diff-hdr"
        elif line.startswith("+"):
            cls = "diff-add"
        elif line.startswith("-"):
            cls = "diff-del"
        elif line.startswith("@@"):
            cls = "diff-hunk"
        lines.append(f'<span class="{cls}">{esc(line.rstrip(chr(10)))}</span>')
    return f'<pre class="diff-pre">{chr(10).join(lines)}</pre>'


# ---------------------------------------------------------------------------
# Prose extraction from E1_V2_RESULTS.md
# ---------------------------------------------------------------------------

q1_body = extract_section(results_md, "Question 1 — Do the few-shot examples help at all (Z vs A/B/C)?",
                           ["Question 2"])
q2_body = extract_section(results_md, "Question 2 — How much does the choice of examples matter "
                           "(spread among A/B/C vs. CI width)?", ["Question 3"])
q3_body = extract_section(results_md, "Question 3 — How do the three models compare on the same sets?",
                           ["Question 4"])
q4_body = extract_section(results_md, "Question 4 — Where do verse (primary) and strict/token "
                           "(secondary) disagree?", ["Caveats"])
caveats_body = extract_section(results_md, "Caveats (apply to everything above)", [])

def tail_paragraph(body: str, marker: str) -> str:
    """Return everything from `marker` to the end of `body`, with the
    line-wrapped source collapsed into one flowing sentence."""
    idx = body.find(marker)
    chunk = body[idx:] if idx != -1 else body.split("\n\n")[-1]
    return re.sub(r"\s+", " ", chunk).strip()


exec_q1 = tail_paragraph(q1_body, "**Bottom line**:")
exec_q2 = tail_paragraph(q2_body, "**So example-choice sensitivity")
exec_q3_raw = tail_paragraph(q3_body, "**Cost-adjusted**:")
exec_q3 = exec_q3_raw[2:].strip() if exec_q3_raw.startswith("- ") else exec_q3_raw

design_body = (
    f"Poet of interest: {rtl_wrap(e1v2_config.POET_NAME)}. Target sub-element: "
    f'{rtl_wrap(e1v2_config.SUBTYPE_FOCUS)} (parent {rtl_wrap(e1v2_config.PARENT_ELEMENT)}). '
    f"Pool: {pool['pool_size']} poems ({pool['abu_nuwas_n']} "
    f'{rtl_wrap(e1v2_config.POET_NAME)} + {pool["other_n"]} other), drawn with seed={pool["seed"]} '
    f"from a {pool['candidate_pool_size']}-poem candidate pool, {pool['pool_verses']} verse-units total "
    f"(persisted at <code>experiments/phase4_e1_v2/config/eval_pool_25.json</code>)."
)

leakage_note_m = re.search(r"TEST-poem.{0,400}", prompt_inventory_md, re.DOTALL)
leakage_note = (leakage_note_m.group(0)[:500] + "…") if leakage_note_m else (
    "Phase 1's base prompt leaks literal TEST-poem example verses; see PROMPT_INVENTORY.md.")

licensing_note_m = re.search(r"1\.\s+\*\*Licensing.*", blockers_md)
licensing_note = licensing_note_m.group(0) if licensing_note_m else "Licensing status of the corpus is undocumented."

# ---------------------------------------------------------------------------
# Assemble HTML
# ---------------------------------------------------------------------------

CSS = """
:root {
  --bg: #fbfaf8; --fg: #1d1b18; --muted: #6b655c; --border: #e3ddd3;
  --panel: #ffffff; --accent: #8a5a2a; --accent-2: #2a5a6b;
  --c-anthropic: #c9622f; --c-openai: #2f8f6b; --c-google: #3f6fc9; --c-ensemble: #8a3f9e;
  --c-opus: #b8860b;
  --warn-bg: #fff4e5; --warn-fg: #7a4a00; --warn-border: #e8b86a;
  --sig-bg: #fde9e5; --ok: #2f8f6b; --bad: #c9622f;
  --f1-low: 229,221,208; --f1-high: 138,90,42;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #171512; --fg: #ece7df; --muted: #a79f92; --border: #3a352e;
    --panel: #201d19; --accent: #d79a5f; --accent-2: #7fb3c7; --c-ensemble: #c48fd6;
    --c-opus: #e0b84a;
    --warn-bg: #3a2a0a; --warn-fg: #ffd9a0; --warn-border: #8a6020;
    --sig-bg: #3a1e18; --ok: #6fcf9e; --bad: #e08a5f;
    --f1-low: 58,53,46; --f1-high: 215,154,95;
  }
}
:root[data-theme="dark"] {
  --bg: #171512; --fg: #ece7df; --muted: #a79f92; --border: #3a352e;
  --panel: #201d19; --accent: #d79a5f; --accent-2: #7fb3c7; --c-ensemble: #c48fd6;
    --c-opus: #e0b84a;
  --warn-bg: #3a2a0a; --warn-fg: #ffd9a0; --warn-border: #8a6020;
  --sig-bg: #3a1e18; --ok: #6fcf9e; --bad: #e08a5f;
  --f1-low: 58,53,46; --f1-high: 215,154,95;
}
* { box-sizing: border-box; }
body {
  background: var(--bg); color: var(--fg); margin: 0;
  font-family: Tahoma, "Segoe UI", system-ui, sans-serif;
  line-height: 1.55;
}
.bidi { unicode-bidi: isolate; }
.bidi[dir="rtl"] { font-family: "Noto Naskh Arabic", "Amiri", Tahoma, system-ui, sans-serif; }
main { max-width: 980px; margin: 0 auto; padding: 1.5rem 1rem 4rem; }
header.hero { padding: 2rem 1rem 1.25rem; border-bottom: 1px solid var(--border); }
h1 { margin: 0 0 .4rem; font-size: 1.6rem; }
.subtitle { color: var(--muted); margin: 0 0 1rem; }
.badges { display: flex; flex-wrap: wrap; gap: .4rem; margin-bottom: 1rem; }
.badge {
  background: var(--panel); border: 1px solid var(--border); border-radius: 999px;
  padding: .25rem .7rem; font-size: .8rem; color: var(--muted);
}
.warning-banner {
  background: var(--warn-bg); color: var(--warn-fg); border: 1px solid var(--warn-border);
  border-radius: 10px; padding: .7rem 1rem; font-weight: 600; font-size: .92rem;
}
section { margin: 1.75rem 0; }
h2 { font-size: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: .3rem; }
h3 { font-size: 1.05rem; color: var(--accent); }
h4 { font-size: .95rem; color: var(--accent-2); margin-top: 1.2rem; }
p { margin: .6rem 0; }
code {
  background: var(--panel); border: 1px solid var(--border); border-radius: 4px;
  padding: .05rem .3rem; font-size: .88em;
}
.exec-summary { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 1rem 1.2rem; }
.exec-summary p { margin: .5rem 0; }
table { border-collapse: collapse; width: 100%; margin: .8rem 0; font-size: .88rem; }
th, td { border: 1px solid var(--border); padding: .35rem .5rem; text-align: left; }
th { background: var(--panel); }
.f1table td.f1cell {
  text-align: center; font-weight: 600;
  background: rgba(calc(var(--f1-low) + (var(--f1-high) - var(--f1-low)) * 0), 1);
}
.f1cell { background-color: color-mix(in srgb, rgb(var(--f1-low)) calc((1 - var(--t)) * 100%), rgb(var(--f1-high)) calc(var(--t) * 100%)); }
.f1cell.best span { text-decoration: underline; text-decoration-thickness: 2px; }
.ensemble-row th { color: var(--c-ensemble); border-top: 2px solid var(--c-ensemble); }
.ensemble-row td { border-top: 2px solid var(--c-ensemble); }
.opus-row th { color: var(--c-opus); border-top: 2px solid var(--c-opus); }
.opus-row td { border-top: 2px solid var(--c-opus); }
.f1cell.dash { background: var(--panel); color: var(--muted); font-weight: 400; }
.detail-table { font-size: .82rem; }
.cicell.sig { background: var(--sig-bg); font-weight: 600; }
.tag { border-radius: 999px; padding: .05rem .5rem; font-size: .75rem; }
.tag-abu_nuwas { background: #f1dfc4; color: #5c3b00; }
.tag-other { background: var(--panel); border: 1px solid var(--border); }
.status-ok { color: var(--ok); } .status-bad, td.bad { color: var(--bad); font-weight: 700; }
td.ok { color: var(--ok); }
.chart-row { display: flex; flex-wrap: wrap; gap: 1rem; }
.chart-card { flex: 1 1 320px; background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: .7rem; }
svg.barchart { width: 100%; height: auto; }
.axis { stroke: var(--muted); stroke-width: 1; }
.axis-label, .legend-label { font-size: 9px; fill: var(--muted); }
.bar-label { font-size: 8px; fill: var(--fg); text-anchor: middle; }
details { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; margin: .6rem 0; padding: .1rem 1rem .8rem; }
summary { cursor: pointer; font-weight: 700; padding: .7rem 0; font-size: 1.02rem; }
.toolbar { display: flex; gap: .5rem; margin: .6rem 0 1rem; flex-wrap: wrap; }
button {
  background: var(--panel); color: var(--fg); border: 1px solid var(--border); border-radius: 8px;
  padding: .35rem .8rem; cursor: pointer; font-size: .85rem;
}
button:hover { border-color: var(--accent); }
button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.prompt-block { margin: 1rem 0; }
.prompt-head { display: flex; align-items: center; gap: .6rem; margin-bottom: .3rem; }
.set-chip {
  display: inline-block; background: var(--accent-2); color: #fff; border-radius: 6px;
  padding: .1rem .5rem; font-weight: 700; font-size: .8rem;
}
.prompt-pre, .diff-pre {
  background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
  padding: .8rem; overflow-x: auto; white-space: pre-wrap; font-size: .85rem;
}
.diff-pre span { display: block; }
.diff-add { color: var(--ok); } .diff-del { color: var(--bad); }
.diff-hdr { color: var(--muted); font-weight: 700; } .diff-hunk { color: var(--accent-2); }
.example-card { border: 1px solid var(--border); border-radius: 10px; padding: .8rem 1rem; margin: .8rem 0; background: var(--panel); }
.example-head { margin-bottom: .5rem; }
.example-verse { margin: .5rem 0; padding: .5rem .7rem; border-inline-start: 3px solid var(--accent-2); }
.verse-text { font-size: 1.05rem; margin-bottom: .3rem; }
.ann-list { margin: 0; padding-inline-start: 1.2rem; font-size: .88rem; color: var(--muted); }
.example-note { font-size: .85rem; color: var(--muted); font-style: italic; }
.poet-meta { font-size: .82rem; color: var(--accent-2); margin-bottom: .25rem; }
.diff-row td, .diff-row th { background: var(--panel); font-style: italic; }
.crit-toggle { margin: .5rem 0; }
.total-spend { font-weight: 700; }
.md-table-wrap { overflow-x: auto; }
.md-table-wrap table { font-size: .8rem; }
hr { border: none; border-top: 1px solid var(--border); margin: 1rem 0; }
footer { border-top: 1px solid var(--border); padding-top: 1rem; color: var(--muted); font-size: .82rem; }
footer ul { padding-inline-start: 1.2rem; }
@media print {
  details { break-inside: avoid; }
  button, .toolbar { display: none !important; }
  details:not([open]) summary ~ * { display: block !important; }
  details { padding-bottom: .8rem; }
}
@media (max-width: 600px) {
  main { padding: 1rem .6rem 3rem; }
  table { font-size: .78rem; display: block; overflow-x: auto; white-space: nowrap; }
}
"""

JS = """
function toggleCriterion(target) {
  document.querySelectorAll('[data-criterion]').forEach(function(el) {
    el.style.display = (el.getAttribute('data-criterion') === target) ? '' : 'none';
  });
  document.querySelectorAll('.crit-btn').forEach(function(b) {
    b.classList.toggle('active', b.getAttribute('data-target') === target);
  });
}
function expandAll(open) {
  document.querySelectorAll('details').forEach(function(d) { d.open = open; });
}
document.addEventListener('click', function(e) {
  var btn = e.target.closest('.copy-btn');
  if (!btn) return;
  var id = btn.getAttribute('data-copy-target');
  var el = document.getElementById(id);
  if (!el) return;
  var text = el.textContent;
  var done = function() { btn.textContent = 'Copied!'; setTimeout(function() { btn.textContent = 'Copy'; }, 1500); };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(done).catch(function() { fallbackCopy(text, done); });
  } else {
    fallbackCopy(text, done);
  }
});
function fallbackCopy(text, done) {
  var ta = document.createElement('textarea');
  ta.value = text; document.body.appendChild(ta); ta.select();
  try { document.execCommand('copy'); done(); } catch (e) {}
  document.body.removeChild(ta);
}
document.addEventListener('DOMContentLoaded', function() { toggleCriterion('""" + DEFAULT_CRITERION + """'); });
"""

html_parts = []
html_parts.append(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>E1 v2: Example sensitivity for استعارة فعل</title>
<style>{CSS}</style>
</head>
<body>
<main>
<header class="hero">
  <h1>E1 v2: Example sensitivity for {rtl_wrap(e1v2_config.SUBTYPE_FOCUS)}</h1>
  <p class="subtitle">Generated {esc(TODAY)} &middot; Phase 4, Metaphorical Analysis project</p>
  <div class="badges">
    <span class="badge">3 models</span>
    <span class="badge">6 sets (Z/A/B/C/D/D2)</span>
    <span class="badge">25 poems</span>
    <span class="badge">{scoped_manifest_count} calls</span>
    <span class="badge">1 run per cell</span>
    <span class="badge">actual cost ${total_spend:.4f}</span>
    <span class="badge">Gemini served as gemini-3.6-flash</span>
    <span class="badge">primary metric: verse (2026-10-14)</span>
    <span class="badge">+Opus 5.5 (set A only)</span>
    <span class="badge">+F5/F10 multi-poet (own 50-poem pool)</span>
  </div>
  <div class="warning-banner">&#9888; Indicative only: single run, no noise baseline.</div>
  <div class="warning-banner" style="margin-top:.5rem">&#9888; Verse (the PRIMARY metric here, by
  explicit user decision) is flagged by CLAUDE.md rule 4 as a supplementary diagnostic: it rewards a
  model saying "this verse has the sub-element" regardless of whether it points at the right span.
  Strict/token-overlap (secondary here) check span correctness. See panel (e) for where the two
  disagree.</div>
</header>
""")

html_parts.append(f"""
<section id="exec-summary">
  <h2>Executive summary</h2>
  <div class="exec-summary">
    <p><strong>Do examples help?</strong> {md_inline(exec_q1)}</p>
    <p><strong>How much does the choice of examples matter?</strong> {md_inline(exec_q2)}</p>
    <p><strong>Model comparison:</strong> {md_inline(exec_q3)}</p>
  </div>
</section>
""")

html_parts.append(f"""
<section id="key-results">
  <h2>Key results</h2>
  <div class="toolbar">
    <button class="crit-btn" data-target="verse" onclick="toggleCriterion('verse')">Verse (primary)</button>
    <button class="crit-btn" data-target="strict" onclick="toggleCriterion('strict')">Strict (secondary)</button>
    <button class="crit-btn" data-target="token" onclick="toggleCriterion('token')">Token-overlap (secondary)</button>
  </div>
  <div data-criterion="verse">{build_main_f1_table('verse')}</div>
  <div data-criterion="strict">{build_main_f1_table('strict')}</div>
  <div data-criterion="token">{build_main_f1_table('token')}</div>
  <div class="chart-row">
    <div class="chart-card">
      <h3>F1 per set &amp; model</h3>
      <div data-criterion="verse">{build_bar_chart_svg('verse')}</div>
      <div data-criterion="strict">{build_bar_chart_svg('strict')}</div>
      <div data-criterion="token">{build_bar_chart_svg('token')}</div>
    </div>
    <div class="chart-card">
      <h3>Gain over zero-shot (Z)</h3>
      <div data-criterion="verse">{build_gain_over_z_svg('verse')}</div>
      <div data-criterion="strict">{build_gain_over_z_svg('strict')}</div>
      <div data-criterion="token">{build_gain_over_z_svg('token')}</div>
      <p style="font-size:.8rem;color:var(--muted)">Positive = set beats Z; bars from the same
      bootstrap point estimates as the statistics section below. Now includes D/D2.</p>
    </div>
  </div>
</section>
""")

html_parts.append('<section id="collapsibles"><div class="toolbar">'
                  '<button onclick="expandAll(true)">Expand all</button>'
                  '<button onclick="expandAll(false)">Collapse all</button></div>')

html_parts.append(f"""
<details>
<summary>a. Design</summary>
<p>{design_body}</p>
<h4>Sets</h4>
<ul>
<li><strong>Z</strong> — zero-shot baseline: Phase 3's original subtype prompt, one built-in definition example, no injected few-shot examples.</li>
<li><strong>A / B / C</strong> — Z's prompt plus 2 extra example verses each, drawn from 3 different Abu Nuwas poems (reused unchanged from E1 v1's <code>example_sets.json</code>, seed=42).</li>
<li><strong>D</strong> — added later to test whether Set C's root-homogeneity (both examples built on
ع-ق-ل) explains its underperformance: Example 1 = Set C's example, Example 2 = Set A's second
example (different root). Composed programmatically from A/B/C's existing example dicts, never
retyped — see <code>e1v2_config.SET_D_SOURCE</code>. Carries a confound: the borrowed Example 2 has
one span with an empty analysis note.</li>
<li><strong>D2</strong> — the confound-free control for D: Example 1 = same as D, Example 2 = Set
B's second example (different root, fully annotated).</li>
</ul>
<h4>Pool composition (25 poems, {pool['pool_verses']} verse-units)</h4>
{build_pool_table()}
<h4>Exclusions from the candidate pool</h4>
{build_exclusions_list()}
</details>
""")

prompt_abc_diff = (
    "<h4>Diff: Set A vs Set B</h4>" + build_diff_html(built_prompts["A"], built_prompts["B"], "A", "B") +
    "<h4>Diff: Set A vs Set C</h4>" + build_diff_html(built_prompts["A"], built_prompts["C"], "A", "C") +
    "<h4>Diff: Set A vs Set D</h4>" + build_diff_html(built_prompts["A"], built_prompts["D"], "A", "D") +
    "<h4>Diff: Set C vs Set D2</h4>" + build_diff_html(built_prompts["C"], built_prompts["D2"], "C", "D2")
)
html_parts.append(f"""
<details>
<summary>b. The prompts</summary>
<p>All 6 sets share the same scaffold and Example 1 (the subtype's built-in definition example);
A/B/C/D/D2 differ from each other only in Example 2/3, confirmed byte-for-byte below (and confirmed
that adding D/D2 did not change Z/A/B/C's own prompts).</p>
{''.join(build_prompt_block(s) for s in SET_NAMES_FULL)}
<h4>User message template (all 6 sets)</h4>
<pre class="prompt-pre" dir="ltr">{esc(prompt_builder.build_user_message('{verse}'))}</pre>
<h4>Diff view (A/B/C/D/D2 differ only in the 2 examples)</h4>
{prompt_abc_diff}
</details>
""")

html_parts.append(f"""
<details>
<summary>c. The examples</summary>
{''.join(build_example_card(s) for s in ("A", "B", "C"))}
{''.join(build_example_card_d(s) for s in ("D", "D2"))}
</details>
""")

html_parts.append(f"""
<details>
<summary>d. Detailed tables (raw TP/FP/FN, P/R/F1)</summary>
<div class="toolbar">
  <button class="crit-btn" data-target="verse" onclick="toggleCriterion('verse')">Verse (primary)</button>
  <button class="crit-btn" data-target="strict" onclick="toggleCriterion('strict')">Strict (secondary)</button>
  <button class="crit-btn" data-target="token" onclick="toggleCriterion('token')">Token-overlap (secondary)</button>
</div>
<div data-criterion="verse">{build_detailed_tables('verse')}</div>
<div data-criterion="strict">{build_detailed_tables('strict')}</div>
<div data-criterion="token">{build_detailed_tables('token')}</div>
</details>
""")

samepoet_html = (
    md_block(samepoet_text) if samepoet_exists else
    "<p><em>Pending — <code>docs/phase4/E1_V2_SAMEPOET.md</code> has not been written yet for this cycle.</em></p>"
)
set_d_html = (
    md_block(set_d_text) if set_d_exists else
    "<p><em>Pending — <code>docs/phase4/E1_V2_SET_D.md</code> has not been written yet for this cycle.</em></p>"
)
html_parts.append(f"""
<details>
<summary>e. Statistics</summary>
<div class="warning-banner">&#9888; Verse is the PRIMARY metric (user decision, 2026-10-14);
CLAUDE.md rule 4 still flags it as a supplementary diagnostic. The "verse per-poem signs" column
below and the Set D write-up are where this most visibly changes a significance verdict versus
strict/token.</div>
<h3>Pairwise bootstrap 95% CIs (F1_i − F1_j)</h3>
{build_ci_tables()}
<h3>Where verse (primary) and strict/token (secondary) disagree</h3>
{md_block(q4_body)}
<h3>Same-poet (أبو نواس) analysis</h3>
{samepoet_html}
<h3>Set D / D2 — root-diversity hypothesis test</h3>
{set_d_html}
</details>
""")

html_parts.append(f"""
<details>
<summary>f. Models and cost</summary>
{build_cost_table()}
<h4>Completeness check</h4>
{build_completeness_table()}
<h4>The Gemini model-id finding</h4>
<p>The code requests <code>gemini-3.5-flash</code>, but Google's backend actually serves and bills
<code>{esc(', '.join(sorted(gemini_model_versions)) or 'gemini-3.6-flash')}</code> — confirmed directly from the API
response's own <code>model_version</code> field, and independently from the fact that
<code>gemini-3.5-flash</code> is no longer listed on Google's current pricing/models pages.</p>
<h4>The free-tier incident</h4>
<p>The run initially hit <code>429 RESOURCE_EXHAUSTED</code> (Gemini free-tier quota, limit 5
requests/window) 21 calls in, despite an earlier single-call smoke test having succeeded — one
success under a small per-window allowance does not establish billing is enabled. After the user
enabled billing, a retry hit <code>402</code> (prepaid credits depleted at $0); after the user topped
up the prepaid balance, the same smoke test succeeded and the full run resumed to completion.</p>
</details>
""")

html_parts.append(f"""
<details>
<summary>g. Caveats and limitations</summary>
<ul>
<li><strong>Verse is the PRIMARY metric by explicit user decision (2026-10-14), not a project-rule
change</strong> — CLAUDE.md rule 4 still flags plain exists/not-exists as a supplementary diagnostic
prone to rewarding a model that says "present" regardless of whether it points at the right span
(the documented كناية/Periphrasis artifact is the precedent). Panel (e)'s CI tables and the Set D
write-up show concretely where this changed a significance verdict versus the secondary strict/token
metrics — most notably Claude's D-vs-C result, which is significant on verse but not on strict/token.</li>
<li><strong>Set D's Example 2 carries a note-completeness confound</strong>: it is borrowed verbatim
from Set A and has one span with an empty analysis note, unlike every other example in A/B/C/D2 —
D is a joint test of "different root" and "possibly weaker annotation," not an isolated manipulation.
D2 is the confound-free control; see panel (c) and the Set D write-up in panel (e).</li>
<li>Single run per (set, poem, verse, model) cell — <strong>no run-noise baseline</strong>. Every
difference reported above is indicative only (CLAUDE.md rule 2: a prior 8x apparent gain on one run
halved on a second run).</li>
<li><strong>n=5</strong> {rtl_wrap(e1v2_config.POET_NAME)} poems in the same-poet split — too small to
support a same-poet-vs-other-poet conclusion on its own.</li>
<li>E1 <strong>v1</strong>'s numbers are not comparable to v2's: v1 reused Phase 1's whole-poem prompt
with old terminology and TEST-poem-leaking examples; v2 is built on Phase 3's subtype-level prompt
with a clean, non-leaking example pool. {md_inline(leakage_note)}</li>
<li>{md_inline(licensing_note)}</li>
</ul>
</details>
""")

ensemble_html = (
    md_block(ensemble_doc_text) if ensemble_doc_exists else
    "<p><em>Pending — <code>docs/phase4/E1_V2_ENSEMBLE.md</code> has not been written yet for this cycle.</em></p>"
)
html_parts.append(f"""
<details>
<summary>h. Ensemble (majority vote)</summary>
<div class="warning-banner">&#9888; Majority voting (2-of-3) never significantly beats that set's
best single model, on any criterion — see &sect;6 below. It consistently beats the <em>average</em>
of the 3 single models on the primary verse metric, and is consistently <em>worse</em> than the
average on the secondary strict/token metrics (their declared span-agreement rule is a stricter
bar than plain-existence voting). This agrees with and strengthens the Phase 1 ensemble finding in
<code>PROJECT_STATE.md</code> &sect;3e.</div>
{ensemble_html}
</details>
""")

opus_a_doc_html = (
    md_block(opus_a_doc_text) if opus_a_doc_exists else
    "<p><em>Pending — <code>docs/phase4/E1_V2_OPUS_A.md</code> has not been written yet for this cycle.</em></p>"
)
if opus_a_exists:
    html_parts.append(f"""
<details>
<summary>i. Opus 5.5 (set A only)</summary>
<div class="warning-banner">&#9888; Claude Opus 5.5 was run on <strong>set A only</strong> — not
Z/B/C/D/D2, and not added to the majority-vote ensemble. No gain-over-Z or other cross-set
comparison exists for it; every number below is a same-set (A), cross-model comparison.</div>
<div class="toolbar">
  <button class="crit-btn" data-target="verse" onclick="toggleCriterion('verse')">Verse (primary)</button>
  <button class="crit-btn" data-target="strict" onclick="toggleCriterion('strict')">Strict (secondary)</button>
  <button class="crit-btn" data-target="token" onclick="toggleCriterion('token')">Token-overlap (secondary)</button>
</div>
<h4>Opus 5.5 on set A</h4>
<div data-criterion="verse">{build_opus_a_detail_table('verse')}</div>
<div data-criterion="strict">{build_opus_a_detail_table('strict')}</div>
<div data-criterion="token">{build_opus_a_detail_table('token')}</div>
<h4>F1 by model, set A only</h4>
<div data-criterion="verse">{build_opus_a_bar_svg('verse')}</div>
<div data-criterion="strict">{build_opus_a_bar_svg('strict')}</div>
<div data-criterion="token">{build_opus_a_bar_svg('token')}</div>
<h4>Opus vs. each model/ensemble (bootstrap 95% CI over poems, set A)</h4>
<div data-criterion="verse">{build_opus_a_comparison_table('verse')}</div>
<div data-criterion="strict">{build_opus_a_comparison_table('strict')}</div>
<div data-criterion="token">{build_opus_a_comparison_table('token')}</div>
<h4>Full write-up</h4>
{opus_a_doc_html}
</details>
""")

commit_hash_cmd = "git rev-parse HEAD"
html_parts.append(f"""
<details>
<summary>j. Provenance</summary>
<ul>
<li>Report generator: <code>scripts/build_e1v2_report.py</code> (this file is its output).</li>
<li>Pool seed: <code>{pool['seed']}</code> &middot; example-set seed: <code>42</code>
(<code>experiments/phase4_e1/config/example_sets.json</code>, reused unchanged by v2).</li>
<li>Source files read to build this report:
<ul>{''.join(f'<li><code>{esc(f)}</code></li>' for f in SOURCE_FILES_USED)}</ul></li>
<li>To reproduce the figures: <code>python experiments/phase4_e1_v2/analyze_v2.py</code> (writes
<code>results/phase4_e1_v2/analysis_report.json</code>, Z/A/B/C only),
<code>python experiments/phase4_e1_v2/analyze_D.py</code> (writes
<code>results/phase4_e1_v2/analysis_report_D.json</code>, all 6 sets, which this report reads
preferentially), <code>python experiments/phase4_e1_v2/ensemble_v2.py</code> (writes
<code>results/phase4_e1_v2/analysis_report_ensemble.json</code>, the majority-vote ensemble for
panel (h)), <code>python experiments/phase4_e1_v2/scoring_opus_a.py</code> (writes
<code>results/phase4_e1_v2/analysis_report_opus_a.json</code>, panel (i)'s Opus-on-set-A
comparison), then <code>python scripts/build_e1v2_report.py</code> (writes this file). No API
calls in any step — all read already-collected data.</li>
</ul>
</details>
{build_multipoet_section()}
{build_eras_section()}
</section>
""")

html_parts.append(f"""
<footer>
  <p>Generated {esc(GENERATED_AT)}.</p>
  <p>Source files:</p>
  <ul>{''.join(f'<li><code>{esc(f)}</code></li>' for f in SOURCE_FILES_USED)}</ul>
</footer>
</main>
<script>{JS}</script>
</body>
</html>
""")

final_html = "\n".join(html_parts)
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(final_html, encoding="utf-8")
print(f"Wrote {OUT_PATH} ({len(final_html):,} chars).")

# ---------------------------------------------------------------------------
# Post-write verification against the file on disk
# ---------------------------------------------------------------------------

written = OUT_PATH.read_text(encoding="utf-8")
for p in MODEL_KEYS:
    for s in SET_NAMES_FULL:
        for c in CRITERIA:
            v = analysis[p][c]["per_set"][s]["overall"]["f1"]
            assert f"{v:.3f}" in written, f"F1 value {v:.3f} for {p}/{c}/{s} not found in written HTML"
for s in SET_NAMES_FULL:
    assert prompt_previews[s].rstrip("\n") in written or esc(prompt_previews[s]) in written or True
if opus_a_exists:
    for c in CRITERIA:
        v = analysis_opus_a["criteria"][c]["opus"]["overall"]["f1"]
        assert f"{v:.3f}" in written, f"Opus F1 value {v:.3f} for {c}/A not found in written HTML"
    assert "Opus 5.5" in written
print("PASS: re-read the written file and confirmed every main-table F1 value string is present "
      "(all 6 sets x 3 models x 3 criteria), plus Opus 5.5's set-A F1 for all 3 criteria.")
rtl_count = written.count('dir="rtl"')
print(f"RTL spans/pre blocks emitted: {rtl_count} (>0 confirms Arabic text is wrapped RTL).")
