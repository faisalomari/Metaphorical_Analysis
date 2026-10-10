# Number reconciliation: category counts and the استعارة تمثيلية join

Read-only audit. No file other than this one was modified. No API call was made.
Everything below was computed directly from already-archived repository files;
every number is reproducible from the script invocations noted inline.

Sources read: `changes_v2.md` §8, `significance_results.md`, `crosswalk_audit_sheet.xlsx`,
`crosswalk_audit_builder.py`, `significance_analysis.py`, the five
`data/ground_truth/ali_ana/original/*.xlsx` files, all 28
`data/ground_truth/by_subtype/*.xlsx` files plus `_manifest.xlsx`,
`results/phase3_crossmodel/raw/` (openai + `crossmodel_scoring_snapshot.json`),
`results/phase3_subelements/raw/`, `PROJECT_STATE.md`, and `paper_v2.md`.

---

## 1. The category count: 53 vs. 59

**Both numbers are real and both are correctly reported — they just count two
different things, and the paper's own text already (unintentionally) conflates
them by using "taxonomy" for both.**

### Where 53 comes from

`archive/ThirdStep/elements1.csv` is a 53-row master catalog: one numbered row
per classical-rhetoric category, with an Arabic name, an English name, and a
bilingual definition (`رقم` 1–53). This is the *defined taxonomy* — the fixed
list of categories Prof. Hussein's annotation scheme is built on, independent
of which categories actually get used in any particular poem. This is the
file `paper_v2.md` (Data and Methods, "a fifty-three-category classical
rhetoric taxonomy") and `PROJECT_STATE.md:233` / `ground_truth.py` are
describing. **53 is correct** as a description of this file.

Some of its 53 rows pack two or three alias names into one cell, separated by
"/" (e.g. row 5: "استعارة قديمة / استعارة مكنية / استعارة تخييلية"). Splitting
every row on "/" yields 59 individual alias strings — a coincidence worth
flagging so nobody mistakes it for the source of the other "59" below: it
is a different 59, arrived at a different way, and only 31 of its strings
actually correspond (even loosely) to labels used in the annotation data (see
below). Do not cite this alias-expansion 59 anywhere; it has no independent
meaning.

### Where 59 comes from

`crosswalk_audit_builder.py` (lines 65–80) enumerates the five poems'
*actual annotation sheets* (`data/ground_truth/ali_ana/original/*.xlsx`,
columns `العنصر البلاغي المستعمل` [primary] and `العنصر البلاغي الثانوي`
[secondary]) and counts **distinct (primary, secondary) label pairs actually
written by the annotator**, pooled across all five poems, out of 776
non-empty annotation rows. That count is 59. This is a direct, reproducible
enumeration (`crosswalk_audit_sheet.xlsx`'s own instrument is built from it);
re-running the same logic in this audit reproduces exactly 59 pairs with the
same per-poem distribution `crosswalk_audit_builder.py` uses.

**Counting rule, stated precisely:** 59 = the number of distinct (primary
label, secondary label) string pairs appearing anywhere in the five original
annotation spreadsheets' own primary/secondary columns, with poem identity
and verse number discarded (i.e., the same pair used in two different poems
counts once, not twice — cross-poem duplication is *not* what inflates this
number past 53; the raw 776 annotation rows collapse down to 59, not up).

### Why 59 ≠ 53: matching each of the 59 against the 53-row catalog

Matching each of the 59 annotation pairs' display label (secondary label, or
primary if no secondary) against the 53-row catalog, allowing for diacritics,
parentheses, and the definite article "ال" (e.g. catalog "كناية عن الصفة"
≈ annotation "كناية عن صفة"; catalog "استعارة فعلية" ≈ annotation "استعارة فعل"):

| | count |
|---|---|
| Annotation pairs that match a catalog row/alias (loosely, ignoring diacritics/الـ) | 31 |
| Annotation pairs with **no match anywhere in the 53-row catalog** | 28 |

The 28 unmatched labels are not spelling noise — they are genuinely new,
finer-grained subtype labels Prof. Hussein introduced *during the actual
annotation of these five poems* that are not among the master list's 53
entries at all, e.g. `استعارة فعل مرشحة`, `استعارة قديمة مرشحة`, `تشبيه الشيء
بنفسه`, `تشبيه غريب`, `تشبيه مركب غريب`, `تشبيه مركب مطول`, `تشبيه مطول غريب`,
`كناية بسيطة`, `كناية فنية`, `كناية نسبة`, `طباق في المعنى`, `مقابلة تضاد
بالمعنى`, `جناس الاشتقاق`, `جناس التصحيف`, `تجاهل العارف`, `المراجعة`,
`الرجوع`, `الحذف`, `التهكم`, `المشاكلة`, `تورية`, `موازن مماثل`, and others
(full list reproducible from `compare_catalog.py`-style matching against
`elements1.csv`; not re-shipped here since the task asked for the rule, not a
re-derivation artifact).

No mojibake (replacement characters, "?" glyphs, or Latin-encoded-as-Arabic
byte garbage) was found in either the five original annotation sheets or
`crosswalk_audit_sheet.xlsx`'s own text; "mojibake" is not a contributor to
this discrepancy in the data actually checked. The one dual-mapped case
(`استعارة تمثيلية مبنية على الكناية`, primary `استعارة`) is real and already
flagged with a `*` in `crosswalk_audit_sheet.xlsx` row 38 — it maps to *both*
Trope and Periphrasis under the project's substring rule, because it contains
both `استعارة` and `كناية`. It is one of the 28 catalog-unmatched labels: it
does not correspond to any single row of `elements1.csv`, but looks like an
annotator-coined hybrid of catalog row 1 (`استعارة تمثيلية`) and row 2
(`استعارة بالكناية`).

**One further, smaller inconsistency surfaced in passing, not asked for but
worth a human author's attention**: `data/ground_truth/by_subtype/_manifest.xlsx`
assigns `مقابلة (تضاد)` and `مقابلة تضاد بالمعنى` to top-level category
"`الطباق`" (Antithesis), but the SUBSTRING_MAP rule actually used for scoring
(`ground_truth.py` / `crosswalk_audit_builder.py`) would **not** map
`مقابلة` to Antithesis, since it doesn't contain the substring `طباق`. This
is a second, independent mapping definition that disagrees with the one the
paper documents and the one the scoring pipeline runs on. Not investigated
further here — out of this task's scope — but flagged for the human authors
alongside the crosswalk audit already pending.

### The correct number, and the wording the paper should use

Both 53 and 59 are correct for what they each describe; the paper's current
single sentence collapses them into one undifferentiated "taxonomy," which is
the actual source of the discrepancy `changes_v2.md` §8 flags. Recommended
replacement text for `paper_v2.md` line 103 (Data and Methods), replacing
"against a fifty-three-category classical rhetoric taxonomy, mapped down to
the four top-level elements evaluated here by substring matching on the
taxonomy's primary and secondary labels" with:

> against a fifty-three-category classical rhetoric taxonomy (Hussein's own
> master catalog of named rhetorical figures); in practice, the five poems'
> own annotation sheets use 59 distinct primary/secondary label combinations
> (31 of which correspond to one of the taxonomy's 53 entries and 28 of which
> are finer-grained subtype labels introduced during this specific annotation
> pass and not present in the master catalog), mapped down to the four
> top-level elements evaluated here by substring matching on the annotation
> sheets' own primary and secondary labels

And replace `paper_v2.md` line 274's "the 53-category-to-4-element crosswalk
itself" with "the 53-category-taxonomy-to-4-element crosswalk itself (applied,
in practice, to the 59 distinct labels the annotation sheets actually use —
see Data and Methods)" so Limitations doesn't repeat the same conflation.

`crosswalk_audit_sheet.xlsx`'s own framing ("more than fifty rhetorical
sub-categories... 59 distinct category labels") is already consistent with
this finding and needs no change.

---

## 2. The استعارة تمثيلية n: the missing 2 rows, located

**Root cause found. It is a join bug in `significance_analysis.py`, not a
data-loss problem, and it does not change any number already published in
`paper_v2.md`.**

`significance_analysis.py:231–243` (`load_phase3_rows`) keys each row by
`rec["row_id"]` **alone**, discarding `poem_key`:

```python
rows.setdefault(rec["row_id"], {})[rec["run_idx"]] = hit
```

The docstring's claim that "row_id is identical across the Gemini file... and
the GPT file... verified by direct inspection" is true but answers the wrong
question — it confirms the two *models'* files use the same row_id scheme for
the same subtype, not that row_id is unique *within* a subtype's own 28 gold
rows. It is not: `data/ground_truth/by_subtype/استعارة_تمثيلية.xlsx`'s own
`#` column reuses **27** for both `Abu_Tammam` and `Jarir`, and reuses **39**
for both `Abu_Tammam` and `Jarir` as well (confirmed by `#`/`القصيدة_مفتاح`
pairs in that file). Keying by `row_id` alone collapses each pair of poems
into one dict entry, silently dropping `Abu_Tammam`#27 and `Abu_Tammam`#39 and
keeping only `Jarir`#27 and `Jarir`#39 (verified directly against the raw
`.jsonl`: each of `Abu_Tammam` and `Jarir`'s rows for #27/#39 appear at
`run_idx` 0 and 1 in both models' files, and whichever poem's record for a
given `run_idx` is read later in the file silently overwrites the earlier
one — here, `Jarir`'s). That is exactly how 28 real gold rows become 26
distinct dict keys.

**Full join (keyed by `(poem_key, row_id)`, both models' raw `.jsonl`
re-read directly), strict-overlap criterion (same criterion
`significance_analysis.py` itself uses, i.e. `exists AND strict_overlap`):**

| | n | TP | recall |
|---|---|---|---|
| Gemini 3.5 Flash (`results/phase3_subelements/raw/استعارة_تمثيلية_all.jsonl`) | 28 | 4 | 0.143 |
| GPT-5.4-mini (`results/phase3_crossmodel/raw/openai/استعارة_تمثيلية_all.jsonl`) | 28 | 16 | 0.571 |

This reproduces `results/phase3_crossmodel/raw/crossmodel_scoring_snapshot.json`'s
published `n=28`, `gemini_tp_strict=4`, `gpt_tp_strict=16` **exactly**. The
two files were never actually missing any rows — all 28 gold `(poem_key,
row_id)` keys are present in both raw `.jsonl` files when joined correctly.

**Answering the question directly: the 2 rows are not lost "in the raw
files" or in "the scoring join" that produced the paper's published numbers —
they are lost specifically in `significance_analysis.py`'s own supplementary
bootstrap-CI script, via the row_id-collision mechanism above.** The
official per-subtype scoring pipeline behind `crossmodel_scoring_snapshot.json`
and `results/phase3_crossmodel/summary.md` already joins by poem+row and is
unaffected.

**Do the published recall figures change?** No. **Gemini 0.143 and GPT 0.571
are already correct on the right (full, 28-row) set** and need no correction
in `paper_v2.md`. What *is* wrong is the supplementary bootstrap confidence
interval `paper_v2.md` cites from the buggy 26-row analysis.

**Recomputing the paired bootstrap CI on the correct 28-row join** (same
method as `significance_analysis.py::phase3_paired_recall`: resample
row-pairs with replacement, B=10,000, seed 20261007):

| | buggy (n=26, as currently in `significance_results.md` / cited by `paper_v2.md`) | corrected (n=28) |
|---|---|---|
| Gemini recall [95% CI] | 0.154 [0.038, 0.308] | **0.143 [0.036, 0.286]** |
| GPT recall [95% CI] | 0.577 [0.385, 0.769] | **0.571 [0.393, 0.750]** |
| Diff (Gemini−GPT) [95% CI] | −0.423 [−0.654, −0.192] | **−0.429 [−0.643, −0.179]** |
| P(Gemini>GPT) | 0.001 | **0.0002 (≈0.000)** |

The direction and statistical clarity of the finding are unchanged — this is
not a reversal — but the exact CI bounds `paper_v2.md` line 236 currently
cites ("95% CI for the Gemini−GPT difference: [−0.654, −0.192]") are the
buggy 26-row figures, not the correct 28-row ones.

**Exact replacement for `paper_v2.md` line 236**, where it currently reads
"...a gap also confirmed non-noise by the same paired-bootstrap approach (95%
CI for the Gemini−GPT difference: [−0.654, −0.192])...", replace the
parenthetical with:

> (95% CI for the Gemini−GPT difference: [−0.643, −0.179], n=28)

No other number in that sentence, or in the n=28 table at `paper_v2.md` line
227, needs to change.

---

## 3. The same join check across all 25 subtypes

For every subtype in `crossmodel_scoring_snapshot.json`'s 25-entry list, gold
row count (`data/ground_truth/by_subtype/*.xlsx` row count) was compared
against the snapshot's own `n` field: **all 25 match exactly.** The official
per-subtype scoring pipeline (the one `results/phase3_crossmodel/summary.md`
and `paper_v2.md`'s subtype tables are built from) joins correctly everywhere
checked; استعارة تمثيلية's discrepancy is confined to `significance_analysis.py`'s
own supplementary script, as established in §2.

That said, the **underlying vulnerability — a subtype's own gold `#` row_id
being reused across two different poems — is not unique to استعارة تمثيلية.**
Checking every one of the 25 subtypes' own gold `#` columns for cross-poem
reuse (the exact precondition that broke §2's analysis if anyone keyed by
`row_id` alone):

| Subtype | n | Reused `#` values (across poems) |
|---|---|---|
| استعارة فعل | 110 | 25, 30, 33, 36, 43, 46, 62, 66, 101, 103, 108, 111, 151, 163 (14 values) |
| كناية عن صفة | 74 | 15, 60, 137, 157 |
| كناية عن موصوف | 61 | 5, 38, 68, 96, 153 |
| مجاز عقلي | 54 | 21, 53, 64, 90 |
| طباق إيجاب | 38 | 69, 79 |
| استعارة تمثيلية | 28 | 27, 39 |
| كناية عن فعل | 27 | 119 |
| مجاز مرسل | 24 | 154 |
| تشبيه مطول | 30 | 69 |

(All other subtypes in the 25-entry screen have no cross-poem `#` reuse.
Three further gold files exist outside the 25-subtype screen — `تشبيه`,
`تشبيه_غريب`, `مقابلة_نحوية` — excluded from `crossmodel_scoring_snapshot.json`
per `_manifest.xlsx`'s own "لا — يحتاج تعريف" ["needs a definition"] flag, not
checked further here since they were never scored.)

None of these other reused-`#` subtypes is currently joined by `row_id` alone
anywhere in the repository — `significance_analysis.py`'s `PHASE3_SUBTYPES`
list (line 76) covers only `كناية_لغوية` and `استعارة_تمثيلية`, and `كناية_لغوية`'s
own gold `#` values happen not to repeat across poems, which is why its
section of `significance_results.md` §4 reconciled exactly while
استعارة_تمثيلية's did not. No other currently-published number is at risk from
this specific bug. It is flagged here as a latent hazard for any *future*
per-subtype analysis that joins Phase 3 raw `.jsonl` files by `row_id` without
`poem_key` — particularly if Claude Sonnet 4.6 is later run on this screen
(`paper_v2.md` line 294's listed future work), since that would be exactly
the kind of new row_id-keyed join this bug would recur in silently.

---

## 4. Every sentence in `paper_v2.md` that must change

Only one correction is required; everything else checked in §1–§3 is already
accurate as published.

1. **Line 236** — replace the parenthetical
   `(95% CI for the Gemini−GPT difference: [−0.654, −0.192])` with
   `(95% CI for the Gemini−GPT difference: [−0.643, −0.179], n=28)`.
   *Reason*: the cited CI was computed on `significance_analysis.py`'s buggy
   26-row join (§2 above); the corrected 28-row join changes the bounds
   slightly without changing the direction or the "not noise" conclusion.

Two further changes are recommended, not required (they correct an internal
inconsistency the paper already carries, not a wrong number):

2. **Line 103** — the "fifty-three-category... taxonomy" sentence — replace
   as given in §1's "correct number and wording" subsection, so the sentence
   distinguishes the 53-category master catalog from the 59 labels the
   annotation sheets actually use, rather than implying the annotation data
   has exactly 53 categories.

3. **Line 274** — the Limitations paragraph's "the 53-category-to-4-element
   crosswalk itself" — append the "(applied, in practice, to the 59 distinct
   labels...)" clause given in §1, for the same reason.

No change is needed to: line 190/227's n=28 table and percentages (already
correct, §2); line 238's twelve-subtype completeness list (not re-verified
row-by-row here beyond the §3 join check, which found no other subtype's
published n wrong); line 256/262's prose description of the استعارة تمثيلية /
كناية لغوية reversal (the 0.143/0.571 point estimates it restates are
correct); or any by-subtype count elsewhere in the paper (§3 found all 25
official snapshot counts match gold).

This document does not itself edit `paper_v2.md`, `significance_results.md`,
or `significance_analysis.py` — per the task's read-only scope, that is left
for a human author (or a separate, explicitly-authorized follow-up) to apply.
