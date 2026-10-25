# E1 v2 — Poet-Era Few-Shot Experiment (M1/M2/E1/E2/H1/H2)

**Supervisor-style question**: when choosing few-shot example poets by where they fall on the
corpus's death-year timeline, does it matter whether they come from the **middle** of the
distribution, the **extremes**, or the **middle of each half**? Target subtype, prompt scaffold,
and schema are unchanged from every other E1 v2 set: **استعارة فعل** (verbal metaphor, parent
مجاز), Phase 3's subtype prompt, `multipoet_prompt_builder.build_system_message_n` with N=2
(the same scaffold A/B/C/D/D2/F5/F10 already use — verified byte-identical header + Example 1,
`experiments/phase4_e1_v2/unit_checks_eras.py`).

**Pool: the SAME `eval_pool_25.json`** Z/A/B/C/D/D2 already ran on (25 poems, 327 verse-units) —
unlike F5/F10 (which needed their own 50-poem pool and a thin 9-poem-overlap correction to
compare against Z/A/B/C/D), every number below is a clean, full-overlap comparison.

**Models**: Claude Sonnet 4.6 (anthropic), GPT-5.4-mini (openai), Gemini (google, served as
`gemini-3.5-flash` per this run's logged `model_id`). **Runs**: 1 run per (set, poem, verse,
model) cell, no replication — per CLAUDE.md rule 2, every comparison below is indicative only.

**Completeness**: 5,886/5,886 cells complete (6 sets × 327 verse-units × 3 models), 0 errors in
the final manifest, verified programmatically (`analyze_eras.py`) that every (set, provider) pair
has exactly 327/327 ok cells. **Actual cost: $16.7459** (manifest total spend before this task's
run: $48.3560; after: $65.1019) — under the $17.3096 pre-run estimate.

One incident during the run, same precedent as the multipoet task
(`docs/phase4/SESSION_LOG.md`, 2026-10-22 entry): Anthropic's credit balance ran dry partway
through (167 cells across all 6 sets errored with "credit balance too low"). Unlike the earlier
incident, the runner's interleaved per-verse call order (anthropic → openai → google for each
verse) meant the existing 5-consecutive-error stop rule never fired — each anthropic failure was
immediately followed by successful openai/google calls that reset the counter, so the run
continued and completed openai/google in full while silently accumulating 167 anthropic gaps
(0 of them actually silent — all recorded in the manifest with their error). After the user
topped up credits, a plain resume (`run_eras.py --confirm`, no `--force`) picked up exactly the
167 missing cells and completed them with 0 further errors, confirmed 327/327 for every
(set, provider) pair.

---

## 1. Design and selection (declared before any API call, seed=42)

### 1.1 Death-year research and analytics (Part 1)

`data/ali_poems/poet_dates.csv`: death years for all 52 corpus poets, researched via
WebSearch/WebFetch (36/52 dated: 14 high confidence, 10 medium, 12 low; 16 blank — 2
non-individuals + القرآن الكريم and the anonymous مجهول entry — and 14 genuinely undocumented
minor poets). Full corpus analytics in `docs/phase4/ERAS_ANALYTICS.md` /
`docs/phase4/ERAS_ANALYTICS.html` (`scripts/build_eras_report.py`): verse-weighted median death
year **784.0 CE** (PRIMARY — consistent with this project's verse-primary convention), axis
midpoint (min+max)/2 = **917.5 CE** (range 544–1291), middle band = median ±75 years, halves
split at the median, extremes = earliest/latest 15% of dated poets by rank.

### 1.2 Note-quality filter

`experiments/phase4_e1_v2/eras_config.py`'s `note_quality()`: excludes a candidate
استعارة فعل annotation's note if it contains a question mark (؟/?, the annotator's own
uncertainty) or — absent a diacritic-insensitive metaphor-reasoning keyword stem
(ستعار/مجاز/كناية/شبه/تشبيه/تشابه/كأن) — if it has ≤3 whitespace tokens or matches a leading
"word(s): definition" colon-gloss pattern (a bare dictionary definition, not an analysis).
Calibrated against the full 858-note candidate pool: question_mark removes 203, colon_gloss
removes 66, too_short removes 68 (337 removed); keyword keeps 418, a longer non-colon-shaped
note with no explicit keyword (treated as a genuine interpretive paraphrase) keeps 103 (521
kept before the eras-specific poem exclusions below further reduce the pool).

### 1.3 Eligibility and the rank-based band fix

A poem is a candidate example source iff not in: `NO_TEXT_POEM_ID`, the 5 Phase-1-frozen
`ALREADY_USED_POEM_IDS`, the 3 Abu-Nuwas v1 `EXAMPLE_POEM_IDS`, the 10 F5/F10 example-source
poems, or any of `eval_pool_25.json`'s 25 poems (the pool these six sets are themselves
evaluated on). A poet is eligible iff not القرآن الكريم (not an individual), has ≥1 candidate
verse carrying a genuine (`note_quality()`-passing) استعارة فعل annotation, **and** has
confidence high/medium in `poet_dates.csv` ("poets need a reliable death year," per the task).

**Declared deviation**: applying Part 1's full-36-poet-corpus year-threshold bands directly to
this smaller, much-more-restricted selection population crashed (pool exhausted) — most of the
full axis's extreme-dated poets (النابغة الذبياني، الأعشى ميمون، امرؤ القيس, among others) turn
out to have **zero** usable candidate verses in this corpus (their استعارة فعل annotations carry
empty analysis notes, failing eligibility before `note_quality()` even runs). Only **14 poets**
survive (dated + confidence high/medium + eligible), too few for the full-axis bands' roles to
avoid competing for the same 2–3 poets. Fix (`experiments/phase4_e1_v2/eras_examples.py`):
compute bands by **rank** within this 14-poet population instead of by absolute year —
`earliest_extreme`/`latest_extreme` = the first/last `ceil(0.15×14)=3` poets by rank;
`middle_band` = the 4 poets (exactly enough for M1+M2) whose rank is nearest the population's
center; `h1_pool`/`h2_pool` = each half's remaining ranks after the extreme/middle roles are
removed. For this run the five resulting pools came out pairwise disjoint by construction
(verified programmatically) — this changes nothing about Part 1's own full-corpus
`ERAS_ANALYTICS.md` bands.

### 1.4 The six sets

Fixed processing order M1, M2, E1, E2, H1, H2, one global used-poet set (12 distinct poets,
verified), one `random.seed(42)` call then one `random.sample(eligible_verses, 1)` per poet in
selection order (sequential, never reseeded mid-draw, same convention as `multipoet_examples.py`):

| Set | Poet 1 (death CE) | Poet 2 (death CE) | Band |
|---|---|---|---|
| M1 | الكميت بن زيد الأسدي (743) | أبو دلامة (777) | middle band |
| M2 | أبو نواس (814) | أبو تمّام (845) | middle band |
| E1 | طرفة بن العبد (569, earliest) | الصنوبري (945, latest) | extremes |
| E2 | قطري بن الفجاءة المازني (698, earliest) | أبو فراس الحمداني (968, latest) | extremes |
| H1 (same-half variant, not the requested design) | الفرزدق (728) | جرير بن عطيّة (728) | middle of first half |
| H2 (same-half variant, not the requested design) | ديك الجن (849) | ابن الرومي (896) | middle of second half |

**Relabeling note, added 2026-10-25**: a later task asked for the literal "one example near the
25th percentile, one near the 75th" quartile design (0-1000 timeline, examples at ~250/~750).
H1/H2 above are *not* that design — they are each "two examples from the middle of one half of
the axis," a different, earlier-requested variant. H1/H2 and every number built from them are
**unchanged** (frozen, same as every other set in this document); the actual quartile design is
**Q1/Q2**, added in §6 below.

Every drawn example verse was independently reconfirmed (fresh `gt_v2.gt_spans_for_subtype`
call) to carry a real استعارة فعل GT span matching its drawn annotation
(`unit_checks_eras.py`, all passed). One kept note (H1's الفرزدق poem 3197 v2) reads as a
general discussion of the verse's rhetorical effect rather than a tight gloss of its specific
span — flagged as a real corpus-annotation quirk, not hand-"fixed."

Full poet/death-year/era/poem/verse/span/note detail for all 12 examples and M1's full
rendered prompt (648 tokens, `cl100k_base`) were printed for review before the cost dry-run;
see `SESSION_LOG.md`'s 2026-10-23 entry and `config/prompt_preview_{M1,M2,E1,E2,H1,H2}.txt`.

---

## 2. Verse-level (PRIMARY) results, overall

| Model | Set | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| Claude | M1 | 67 | 66 | 60 | 0.504 | 0.528 | 0.515 |
| Claude | M2 | 94 | 101 | 33 | 0.482 | 0.740 | 0.584 |
| Claude | E1 | 57 | 68 | 70 | 0.456 | 0.449 | 0.452 |
| Claude | E2 | 86 | 106 | 41 | 0.448 | 0.677 | 0.539 |
| Claude | H1 | 94 | 119 | 33 | 0.441 | 0.740 | 0.553 |
| Claude | H2 | 81 | 94 | 46 | 0.463 | 0.638 | 0.536 |
| GPT | M1 | 71 | 106 | 56 | 0.401 | 0.559 | 0.467 |
| GPT | M2 | 98 | 141 | 29 | 0.410 | 0.772 | 0.536 |
| GPT | E1 | 75 | 108 | 52 | 0.410 | 0.591 | 0.484 |
| GPT | E2 | 75 | 100 | 52 | 0.429 | 0.591 | 0.497 |
| GPT | H1 | 88 | 130 | 39 | 0.404 | 0.693 | 0.510 |
| GPT | H2 | 75 | 99 | 52 | 0.431 | 0.591 | 0.498 |
| Gemini | M1 | 58 | 80 | 69 | 0.420 | 0.457 | 0.438 |
| Gemini | M2 | 68 | 94 | 59 | 0.420 | 0.535 | 0.471 |
| Gemini | E1 | 48 | 59 | 79 | 0.449 | 0.378 | 0.410 |
| Gemini | E2 | 89 | 109 | 38 | 0.449 | 0.701 | 0.548 |
| Gemini | H1 | 81 | 97 | 46 | 0.455 | 0.638 | 0.531 |
| Gemini | H2 | 86 | 119 | 41 | 0.420 | 0.677 | 0.518 |

(Every model's `strict`/`token` secondary tables and `abu_nuwas`/`other` splits are in
`results/phase4_e1_v2/analysis_report_eras.json` — omitted here for length; the pooled/CI
tables below cover every model.)

### Pooled (M=M1+M2, E=E1+E2, H=H1+H2), verse-primary

| Model | Group | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| Claude | M | 161 | 167 | 93 | 0.491 | 0.634 | 0.553 |
| Claude | E | 143 | 174 | 111 | 0.451 | 0.563 | 0.501 |
| Claude | H | 175 | 213 | 79 | 0.451 | 0.689 | 0.545 |
| GPT | M | 169 | 247 | 85 | 0.406 | 0.665 | 0.504 |
| GPT | E | 150 | 208 | 104 | 0.419 | 0.591 | 0.490 |
| GPT | H | 163 | 229 | 91 | 0.416 | 0.642 | 0.505 |
| Gemini | M | 126 | 174 | 128 | 0.420 | 0.496 | 0.455 |
| Gemini | E | 137 | 168 | 117 | 0.449 | 0.539 | 0.490 |
| Gemini | H | 167 | 216 | 87 | 0.436 | 0.657 | 0.524 |

**Correction, added 2026-10-25 (quartile-task Step 3 cross-check):** the Gemini row above was
originally published with the **strict-criterion** pooled numbers (TP/FP/FN 82/218/276,
82/223/276, 108/275/250, F1 0.249/0.247/0.291) mislabeled as verse-primary — caught by checking
this table against `results/phase4_e1_v2/analysis_report_eras.json` directly, where the actual
verse-primary pooled values are the ones now shown (126/174/128, 137/168/117, 167/216/87, F1
0.455/0.490/0.524), consistent with Gemini's own per-set verse F1 range (0.410–0.548) directly
above. Claude's and GPT's pooled rows were already correct (verified against the same JSON) —
only Gemini's row had this mislabeling. The underlying `analysis_report_eras.json` itself was
never wrong; this was a write-up/transcription error in this markdown file only. Separately
verified from every `run_manifest.json` google-provider record (M1..H2 and the later Q1/Q2
quartile sets alike): the model actually served throughout is **`gemini-3.5-flash`**, never
`gemini-3.6-flash` — a label used in `analyze_eras.py`'s own `DISPLAY` dict (`"Gemini (served:
gemini-3.6-flash)"`) that this cross-check also found to be incorrect; it is cosmetic
(print-only, does not affect any stored score) and is left as-is per this task's "only ADD, do
not edit existing files" scope, but is flagged here so a future reader does not repeat it.

---

## 3. Bootstrap 95% CIs (per-poem resampling, n=2000, seed=0)

### 3.1 Within-pair noise (same band, different poet pair) — verse-primary

| Model | M1 vs M2 | E1 vs E2 | H1 vs H2 |
|---|---|---|---|
| Claude | **−0.0685 [−0.1361,−0.0003] SIG** | **−0.0868 [−0.1438,−0.0269] SIG** | +0.0165 [−0.0221,+0.0585] ns |
| GPT | **−0.0684 [−0.1339,−0.0159] SIG** | −0.0128 [−0.0556,+0.0413] ns | +0.0118 [−0.0194,+0.0534] ns |
| Gemini | +0.0330 [−0.0250,+0.0948] ns | +0.0107 [−0.0463,+0.0589] ns | +0.0783 [+0.0196,+0.1307] **SIG** |

### 3.2 Pooled cross-category (M vs E, M vs H, E vs H) — verse-primary

| Model | M vs E | M vs H | E vs H |
|---|---|---|---|
| Claude | **+0.0524 [+0.0098,+0.0912] SIG** | +0.0081 [−0.0363,+0.0509] ns | **−0.0443 [−0.0848,−0.0033] SIG** |
| GPT | +0.0143 [−0.0181,+0.0530] ns | −0.0002 [−0.0207,+0.0209] ns | −0.0144 [−0.0486,+0.0155] ns |
| Gemini | +0.0019 [−0.0342,+0.0416] ns | **−0.0423 [−0.0842,−0.0021] SIG** | **−0.0441 [−0.0733,−0.0199] SIG** |

### 3.3 Each set vs Z (zero-shot) — verse-primary

| Model | M1 | M2 | E1 | E2 | H1 | H2 |
|---|---|---|---|---|---|---|
| Claude | **+0.139 SIG** | **+0.207 SIG** | **+0.076 SIG** | **+0.162 SIG** | **+0.176 SIG** | **+0.160 SIG** |
| GPT | **−0.082 SIG** | −0.013 ns | **−0.065 SIG** | −0.052 ns | −0.039 ns | **−0.050 SIG** |
| Gemini | +0.033 ns | +0.039 ns | +0.011 ns | +0.052 ns | **+0.078 SIG** | **+0.079 SIG** |

### 3.4 Each set vs A/B/D2 (existing 2-example sets) — verse-primary, SIG cells only

- **Claude**: E1 significantly worse than A, B, **and** D2 (−0.124, −0.094, −0.116); E2
  significantly worse than A (−0.037). M1/M2/H1/H2 vs A/B/D2 are all `ns`.
- **GPT**: M1 significantly worse than A and B (−0.074, −0.046); E1 significantly worse than A
  (−0.057). Everything else vs A/B/D2 is `ns`.
- **Gemini**: E1 significantly worse than B and D2 (−0.072, −0.043). Everything else — including
  every M/H comparison — is `ns`.

Full numeric CIs for every (model, criterion, pair) combination, plus per-poem diff signs:
`results/phase4_e1_v2/analysis_report_eras.json`.

---

## 4. Ensemble (2-of-3 majority vote), verse-primary

| Set | Ensemble F1 | Best single | Avg of 3 singles |
|---|---|---|---|
| M1 | 0.496 | anthropic 0.515 | 0.473 |
| M2 | 0.557 | anthropic 0.584 | 0.530 |
| E1 | 0.485 | openai 0.484 | 0.449 |
| E2 | 0.549 | google 0.548 | 0.528 |
| H1 | 0.563 | anthropic 0.553 | 0.531 |
| H2 | 0.552 | anthropic 0.536 | 0.518 |

Same pattern as every prior ensemble check in this project (Phase 1 §3e, `E1_V2_ENSEMBLE.md`,
the multipoet F5/F10 ensemble): the majority vote lands close to — slightly above in 3/6 sets
(E1, H1, H2), slightly below in 3/6 (M1, M2, E2) — the best single model, and consistently above
the average of the 3 singles in every set.

---

## 5. Plain answer

**Does the era of the example poets matter (middle vs. extremes vs. halves)?**

**Mixed, and the signal is often no larger than pure example-choice noise.** Looking at the
pooled cross-category comparisons (§3.2) against the within-pair noise from swapping just the
*specific poets* within the same band (§3.1):

- **Claude**: era does matter in one clear sense — the middle band (M, pooled) and the two half-
  middles (H) both significantly beat the extremes (E) on verse (M−E +0.052 SIG, E−H −0.044 SIG,
  i.e. H>E too), while M vs H is not significant. But the within-band noise is *at least as
  large*: M1 vs M2 (−0.069 SIG) and E1 vs E2 (−0.087 SIG) are both themselves significant and
  larger in magnitude than the M−E effect (+0.052) that "era matters" rests on. So for Claude,
  *which 2 specific poets you draw* is at least as consequential as *which band they come from*.
- **GPT**: no era signal at all — every pooled cross-category comparison is `ns` (M−E, M−H, E−H
  all non-significant), while M1 vs M2 (−0.068 SIG) is itself significant. For GPT, the only
  reliable effect in this whole design is plain poet/verse choice noise, not era.
- **Gemini**: the cleanest case for a real era effect — H (half-middles) significantly beats both
  M (−0.042 SIG) and E (−0.044 SIG) on the pooled comparison, and **none** of the three
  within-band noise checks (M1-M2, E1-E2, H1-H2) reach significance except H1 vs H2 itself
  (+0.078 SIG) — ironically the one within-pair gap that *is* significant belongs to the band
  that otherwise looks like the winner, which tempers how clean this "Gemini sees a real era
  effect" read actually is.

**Bottom line**: there is no model-general answer. Claude and Gemini each show *some* pooled
band-level signal, but by two different, non-overlapping routes (Claude: middle/halves beat
extremes; Gemini: halves beat both middle and extremes), and in both cases at least one
within-band noise check is comparable in size to the signal. GPT shows no era effect whatsoever
— only the ordinary draw-to-draw noise already documented everywhere else in this project
(CLAUDE.md rule 2's Kenning/Periphrasis precedent). None of the six sets catastrophically
underperforms the existing A/B/D2 sets except **E1** specifically (earliest+latest poet pairing:
طرفة بن العبد + الصنوبري), which is significantly worse than A/B/D2 for **all three models** —
the one consistent cross-model finding in this whole design, though it is a single poet pairing,
not a property of "extremes" as a category (E2's different earliest+latest pairing does not show
the same pattern for GPT/Gemini, only partially for Claude).

**Caveats** (same discipline as every other table in this project):
- **One run per cell, one draw of poets/verses, no noise baseline** — every number above,
  significant or not, is indicative only (CLAUDE.md rule 2).
- **One specific rank-based draw** (seed=42, the eligibility/confidence/note-quality filters
  declared in §1.3) — a different seed, a looser note filter, or a different confidence
  threshold could plausibly select different poets and shift the within-band noise estimates
  (which are themselves based on just 2 poets per band) substantially; §3.1's within-pair
  numbers are a single, small-n estimate of that noise, not a stable baseline.
- **Only 14 poets survived the selection-eligibility restriction** out of 36 dated corpus poets —
  this design answers "does era matter among the poets whose annotations happen to carry usable
  analysis notes in this corpus," not "does era matter among all poets in the corpus."
- **Abu Nuwas / other splits, strict/token secondary criteria, and per-poem diff signs** are all
  in `results/phase4_e1_v2/analysis_report_eras.json` but not reproduced in this document for
  length; every verse-primary conclusion above should be read alongside CLAUDE.md rule 4's
  standing caveat that plain exists/not-exists can diverge from span-level correctness.

---

*Full numeric report (every model/criterion/set/pair, abu_nuwas/other splits, per-poem diff
signs): `results/phase4_e1_v2/analysis_report_eras.json`. Raw manifest:
`results/phase4_e1_v2/run_manifest.json` (set_name M1/M2/E1/E2/H1/H2, additive to the existing
Z/A/B/C/D/D2/F5/F10/anthropic_opus records — 18,099 total records, this task's own 5,886 cells
all present and error-free after the credit-outage resume).*

---

# §6 — Quartile few-shot experiment (Q1/Q2), added 2026-10-25

**The literally-requested design**: "timeline from 0 to 1000; take one poem from 250 and one
from 750" — each set = one example near the death-year axis's 25th percentile (P25) + one near
its 75th percentile (P75). H1/H2 above (§1.4) are a *different*, earlier-requested variant
("middle of each half") and are explicitly relabeled in this document's own table as "same-half
variant, not the requested design" — their data is untouched. **Q1 and Q2 are the actual
quartile design.** Same subtype focus (استعارة فعل), same Phase 3 prompt scaffold, same
`eval_pool_25.json` pool as every other set in this document.

## 6.1 Target points and the >100-year STOP

Two axis definitions were computed over the same dated-poet population `ERAS_ANALYTICS.md` uses:

| Axis | P25 | P75 |
|---|---|---|
| Range axis (min + 0.25/0.75 × range, min=544 max=1291) | 730.75 CE | **1104.25 CE** |
| Verse-weighted quantile (25th/75th percentile of death year, weighted by verse count) | 649.0 CE | 845.0 CE |

The range-axis P75's nearest eligible poet (same eligibility as M1..H2) was **108.25 years
away** — over the task's 100-year guard. Per explicit instruction this was presented to the user
as two options rather than resolved silently; **the user chose the verse-weighted-quantile axis**
(P25=649.0, P75=845.0 CE).

## 6.2 Selection and the declared reuse/fallback

User-set rules: H1/H2-poet reuse allowed for the **P75 slot only**; M1/M2/E1/E2 poets never
reused; Q1 and Q2 use 4 distinct poets between them; P75 slot prefers H2's own two poets split
across Q1/Q2; P25 slot prefers poets never used by any existing set.

| Set | P25 slot | P75 slot |
|---|---|---|
| Q1 | جميل بن معمر (701 CE, medium confidence, d=52.0y, 20 candidate verses) | **ديك الجن** (849 CE, d=4.0y, 37 candidate verses) — reused from H2 |
| Q2 | النمر بن تولب العكلي (635 CE, **low confidence — declared fallback**, d=14.0y, 3 candidate verses) | **ابن الرومي** (896 CE, d=51.0y, 35 candidate verses) — reused from H2 |

**Declared deviation**: of the 14-poet selection-eligible population (same eligibility rule as
M1..H2), only **2 poets were never used by any existing set** (جميل بن معمر, محمد بن هاشم
الخالدي) — every other candidate near either quartile point is already an M1/M2/E1/E2 or H1/H2
poet. The P25 slot's standing high/medium-confidence pool has exactly one such poet (جميل بن
معمر); النمر بن تولب العكلي (low confidence) was taken as the declared fallback rather than
silently reusing an H1/H2 or M1/M2/E1/E2 poet. A confidence-tier-first ranking bug was caught and
fixed before any file was written: it let محمد بن هاشم الخالدي (996 CE, medium confidence, but
347 years from P25 — he belongs near P75, where he is only 151 years away) outrank a much closer
low-confidence candidate purely on confidence tier; fixed by requiring a P25 candidate to be
closer to P25 than to P75 (see `eras_quartile_examples.py`'s `pick_p25_candidates` docstring).

**Declared reuse / confound, stated here and repeated in §6.4**: **Q shares its P75-slot poets
with H2** (ديك الجن, ابن الرومي) — any Q-vs-H comparison below is confounded by this shared
example overlap, unlike Q-vs-M/E/Z/A/B/D2, which share no example poets with Q at all.

Drawn example verses (seed=42, own RNG stream; independently cross-checked against
`data/ali_poems/manifest.csv`'s poem→poet mapping):
- Q1 / جميل بن معمر: poem 25685 v11, span «عَطاؤُها».
- Q1 / ديك الجن: poem 18677 v15, span «وَلِدَمْعي مِنْهُمُ سَفَرُ».
- Q2 / النمر بن تولب العكلي: poem 23986 v21, span «أتَى حصنَهُ ما أتَى تُبَّعًا».
- Q2 / ابن الرومي: poem 12331 v9, span «قد بدرتْ سَبة الخطيب فما لجلج في قيله ولا اكترثَا».

Full poet/death-year/span/note detail, unit-check results, and the full rendered prompts (Q1 =
604 tokens, Q2 = 671 tokens, `cl100k_base`) are in `SESSION_LOG.md`'s 2026-10-25 "Quartile
few-shot task" entries and `config/prompt_preview_{Q1,Q2}.txt`.

## 6.3 Verse-level (PRIMARY) results

| Model | Set | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| Claude | Q1 | 57 | 72 | 70 | 0.442 | 0.449 | 0.445 |
| Claude | Q2 | 92 | 94 | 35 | 0.495 | 0.724 | 0.588 |
| Claude | Pooled Q | 149 | 166 | 105 | 0.473 | 0.587 | 0.524 |
| GPT | Q1 | 56 | 64 | 71 | 0.467 | 0.441 | 0.453 |
| GPT | Q2 | 62 | 78 | 65 | 0.443 | 0.488 | 0.464 |
| GPT | Pooled Q | 118 | 142 | 136 | 0.454 | 0.465 | 0.459 |
| Gemini | Q1 | 58 | 73 | 69 | 0.443 | 0.457 | 0.450 |
| Gemini | Q2 | 69 | 83 | 58 | 0.454 | 0.543 | 0.495 |
| Gemini | Pooled Q | 127 | 156 | 127 | 0.449 | 0.500 | 0.473 |

Reference (pooled M/E/H, same pool, same 1-run-per-cell convention as this document's §2):
Claude M=0.553/E=0.501/H=0.545; GPT M=0.504/E=0.490/H=0.505; Gemini M=0.455/E=0.490/H=0.524.

## 6.4 Bootstrap 95% CIs (per-poem resampling, n=2000, seed=0) — verse-primary

| Model | Q1 vs Q2 | Q(pooled) vs M | vs E | vs H *(confounded — shares poets with H2)* | vs Z | vs A | vs B | vs D2 |
|---|---|---|---|---|---|---|---|---|
| Claude | **-0.1425 [-0.2178,-0.0659] SIG** | -0.0295 ns | +0.0229 ns | -0.0214 ns | **+0.1469 SIG** | **-0.0525 SIG** | -0.0228 ns | **-0.0443 SIG** |
| GPT | -0.0110 ns | **-0.0453 SIG** | -0.0311 ns | **-0.0455 SIG** | **-0.0895 SIG** | **-0.0817 SIG** | **-0.0537 SIG** | **-0.0439 SIG** |
| Gemini | -0.0450 ns | +0.0181 ns | -0.0172 ns | **-0.0513 SIG** | **+0.0797 SIG** | **-0.0383 SIG** | -0.0368 ns | -0.0270 ns |

Full numeric CIs, strict/token secondary criteria, and per-poem diff signs:
`results/phase4_e1_v2/analysis_report_quartile.json`.

## 6.5 Ensemble (2-of-3 majority vote), verse-primary

| Set | Ensemble F1 | Best single | Avg of 3 singles |
|---|---|---|---|
| Q1 | 0.486 | openai 0.453 | 0.449 |
| Q2 | 0.557 | anthropic 0.588 | 0.516 |

Same pattern as every other ensemble check in this project: lands near the best single model,
consistently above the average of the 3 singles.

## 6.6 A real write-up bug caught while cross-checking this section against §2

**The "Pooled Gemini" row in §2's verse-primary table was wrong** — it had silently carried the
**strict-criterion** numbers (82/218/276 → F1 0.249, etc.) instead of the verse-primary ones
(now corrected in place there: 126/174/128 → F1 0.455, etc.), caught by comparing that table
against `analysis_report_eras.json` directly while building this section. Claude's and GPT's
pooled rows in that table were already correct — only Gemini's was swapped. The underlying JSON
was never wrong; this was purely a markdown transcription error, now fixed with a marked note in
§2 itself. **Separately verified from every manifest record (M1..H2 and Q1/Q2 alike): Gemini was
served as `gemini-3.5-flash` throughout this entire document's experiments — never
`gemini-3.6-flash`**, correcting a mislabel in `analyze_eras.py`'s own (cosmetic, print-only)
`DISPLAY` dict.

## 6.7 Plain answer

**Does the literal quartile design (one example near the 25th percentile, one near the 75th)
behave differently from the zero-shot baseline or from the other few-shot example-selection
strategies already tried?**

**Mostly no better or worse than ordinary example-choice noise, with one real per-model
signal.** Pooled Q is statistically indistinguishable from pooled M and pooled E for all three
models (every M/E comparison above is `ns`) — the quartile framing itself does not produce a
detectably different result from middle-band or extreme-poet example selection. Against the
zero-shot baseline Z, the familiar per-model split holds: **SIG positive for Claude and Gemini**,
**SIG negative for GPT** — the same fewshot-helps-or-hurts-by-model pattern every other E1 v2
fewshot comparison in this project has already shown, replicated again here. Against the
existing 2-example sets A/B/D2, **GPT is significantly worse than all three**, Claude is
significantly worse than A and D2 (not B), and Gemini is significantly worse than A only — so for
GPT specifically, this few-shot design is a clear net negative relative to every alternative
tried, not just relative to zero-shot. The one within-pair finding worth flagging on its own:
**Q1 vs Q2 is significant for Claude** (Q2/ابن الرومي's example clearly outperforming Q1/ديك
الجن's, +0.14 F1) but not for GPT or Gemini — a single-poet-pairing effect, not a property of
"P75-slot examples" as a category, the same kind of finding §5 already flagged for set E1 at the
M/E/H level.

**Caveats** (same discipline as §5 above, repeated here deliberately rather than only
cross-referenced): one run per cell, one draw of poets/verses, no noise baseline; only 14 poets
in the selection-eligible population, with Q1/Q2 drawing the last 2 truly unused ones (one of
them, النمر بن تولب العكلي, admitted only via the declared low-confidence fallback); **Q-vs-H
comparisons are confounded by shared P75-slot poets and should not be read as an independent
replication the way Q-vs-M/E/Z/A/B/D2 are.**

---

*Full numeric report (every model/criterion/set/pair, abu_nuwas/other splits, per-poem diff
signs): `results/phase4_e1_v2/analysis_report_quartile.json`. Raw manifest:
`results/phase4_e1_v2/run_manifest.json` (set_name Q1/Q2, additive to every existing record —
20,061 total records, this task's own 1,962 cells all present and error-free). Actual cost:
$5.7209 (under the $5.9032 pre-run estimate).*
