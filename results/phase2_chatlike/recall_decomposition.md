# Recall Decomposition — Frozen TEST FNs (v4_combined, strict criterion)

**Purpose**: in response to the 2026-07-23 supervisor request "check and analyze why the
models are missing a lot — recall is too low," this document classifies every FN
(false-negative) instance in the frozen TEST results (`PROJECT_STATE.md` §3a; Imru1 +
Jarir + Abu_Tammam, v4_combined, strict criterion, per model) into one of several
explanatory buckets. **Zero new API calls** — this reconstructs TP/FP/FN classifications
from already-collected raw model output (`results/pilot_3models/test_final/v4_combined/`)
plus Dr. Ali Hussein's ground truth, using the project's existing scoring primitives
(`span_scoring.py`, `span_matching.py`). Code: `experiments/phase2_chatlike/recall_decomposition.py`.

**TEST remains untouched as data-to-be-scored, not re-run** — no model was called again;
this is purely a re-analysis of the frozen predictions already sitting in
`test_final/v4_combined/`.

**Sanity check before any decomposition**: the reconstruction's pooled TP/FP/FN per
element/model reproduces `PROJECT_STATE.md` §3a's frozen table **exactly**:

| Element | Model | TP/FP/FN (reconstructed) | Matches §3a? |
|---|---|---|---|
| Trope | Claude / GPT / Gemini | 25/3/154, 28/16/151, 45/9/134 | ✅ |
| Simile | Claude / GPT / Gemini | 28/6/24, 31/3/21, 32/4/20 | ✅ |
| Kenning | Claude / GPT / Gemini | 8/6/139, 4/7/143, 15/8/132 | ✅ |
| Antonymy | Claude / GPT / Gemini | 6/12/37, 5/17/38, 5/21/38 | ✅ |

**Total FN events classified: 1,031** (Trope 439, Simile 65, Kenning 414, Antonymy 113 — one
event per model per missed ground-truth instance, matching how §3a's own FN column is
built, so an instance missed by all 3 models contributes 3 events).

---

## 1. Methodology — bucket definitions and priority order

Each FN event gets **exactly one** bucket. Buckets are checked in this order (first match
wins), per the 2026-07-26 sign-off on this methodology:

| Order | Bucket | What it means | How it's computed |
|---|---|---|---|
| 1 | **(b) schema-structural** | Objective, model-independent: for any (verse, element) with *k*≥2 ground-truth instances, `prompts.py`'s schema allows exactly one `*_appearance` string per element per verse, so *k*−1 of the *k* are a hard ceiling regardless of model quality. | Computed from ground truth alone. Within a *k*≥2 group, *k*−1 FN slots are tagged (b); if the group was totally missed (not just partially credited), the **1 remaining slot** is left open for a more specific bucket below, preferring to leave open whichever instance already qualifies for the most specific tag. |
| 2 | **(c) subtype-knowledge** | GT secondary label names a lexicalized/enumerable Trope subtype: مجاز مرسل or استعارة قديمة (§3c: both stay flat-to-slightly-improved under every Phase 1 intervention). | String match on the GT `secondary` field. |
| 3 | **(d1) boundary-confusion** | **Mechanical scan**, not manual: this FN's GT span token-overlaps (`span_matching.token_match`, threshold 0.5) a same-verse, same-model FP span from the *other* element of the Trope↔Kenning pair — i.e. the model found *something* in the right place but filed it under the wrong one of these two categories. | Computed from the same raw predictions, both elements, for every verse. |
| 4 | **(d2) annotation-sensitive** | **Only** the 6 already-vetted TEST-poem rows from `ali_adjudication_shortlist.md` (Imru1 v2, v4, v25 [Kenning]; v34, v43, v45 [Trope]). Never auto-tagged beyond that list — whether an annotation itself is questionable is Dr. Hussein's call, not a mechanical one. | Fixed lookup table, reproduced in the script. |
| 5 | **(e) model-capability** | Trope only, subtype استعارة فعل or مجاز عقلي: §3c/§3i show Config A (**same strict JSON format**, only the model changed to Fable 5) already moves these — a model-tier story, not a format one. | String match on GT `secondary`, Trope-restricted. |
| 6 | **(a) format-suppression candidate** | Kenning only: the one element where the DEV evidence shows the specific "Config A static-or-worse, Config C dramatically better" pattern (Imru2 v6 anchor: Config A F1=0.095, Config C F1=0.316; report_3i.md §5, §9). | Element-level: any remaining Kenning FN. Ground truth has no periphrasis subtypes, so no finer-than-element operationalization is available — stated as a limitation below. |
| 7 | **unclassified** | Everything left over — mostly Simile and Antithesis (no Config A/B/C DEV evidence of a recall gain either direction — Simile got flat-to-worse under Config C, Antithesis too thin/noisy in A/B), plus residual Trope subtypes (استعارة تمثيلية, استعارة حديثة) with no DEV evidence either way. | Default. |

**The central caveat, stated once here and not repeated at every mention below**: buckets
(e) and (a) are **DEV-pattern projections onto TEST instances — inferences, not
observations**. Config A/B/C were run only on Imru2 and Nabigha (DEV) and, per this
project's standing TEST discipline, will never be run on Imru1/Jarir/Abu_Tammam. Membership
in (e) or (a) means "same element/subtype as where Phase 2 found a DEV gain," not "verified
to be fixable on this specific instance." Buckets (b), (c), (d1), (d2) are computed directly
from TEST data itself and carry no such caveat.

---

## 2. Headline table — bucket share per element

| Bucket | Trope (n=439) | Simile (n=65) | Kenning (n=414) | Antonymy (n=113) |
|---|---|---|---|---|
| (b) schema-structural | 228 (51.9%) | 30 (46.2%) | 201 (48.6%) | 12 (10.6%) |
| (c) subtype-knowledge | 55 (12.5%) | — | — | — |
| (d1) boundary-confusion | 5 (1.1%) | — | 8 (1.9%) | — |
| (d2) annotation-sensitive | 4 (0.9%) | — | 9 (2.2%) | — |
| (e) model-capability | 133 (30.3%) | — | — | — |
| (a) format-suppression candidate | — | — | 196 (47.3%) | — |
| **unclassified** | **14 (3.2%)** | **35 (53.8%)** | **0 (0.0%)** | **101 (89.4%)** |

**Reading this, element by element**:

- **Trope**: 96.8% of FNs get a specific explanation, and it's a genuinely mixed story —
  roughly half are schema-capped multi-instance verses, 30.3% look like a model-tier gap
  (استعارة فعل / مجاز عقلي — Config A already helps these without a format change), 12.5%
  are the two lexicalized subtypes (مجاز مرسل, استعارة قديمة) that resisted every Phase 1
  intervention, and only 3.2% (14 instances) have no candidate explanation at all.
- **Kenning**: the schema cap alone explains 48.6%; of the remainder, 47.3% fall into the
  format-suppression candidate bucket (the Imru2 v6 pattern, projected element-wide since
  Kenning has no annotated subtypes to narrow the claim further) — leaving **zero**
  unclassified, which is a direct consequence of (a) being defined as "whatever Kenning FN
  is left," not evidence that the format-suppression story is confirmed for every one of
  them (see caveat above).
- **Simile**: only the schema cap applies (46.2%); the rest (53.8%) is honestly
  unclassified — Simile is already near-ceiling (F1 ~0.65–0.73) and no Phase 2 config
  showed it a clean recall gain, so there's no DEV-derived story to project.
- **Antithesis**: almost entirely unclassified (89.4%) — consistent with §3d's finding that
  Antithesis's problem is over-claiming (FP > TP everywhere), not a recall-suppression
  story this decomposition's buckets are built to explain. The schema cap (10.6%) is the
  only bucket that applies.

---

## 3. Bucket detail with representative examples

### (b) schema-structural (471 total: Trope 228, Simile 30, Kenning 201, Antonymy 12)

Every multi-instance verse in the ground truth structurally caps credit at 1 regardless of
model quality. Examples:

- Imru1 v23 (Kenning, 4 GT instances in one verse) — at most 1 of the 4 could ever be a TP.
- Imru1 v20 (Trope, 3 instances: «القَلْبَ» مجاز مرسل, «قَاتِلي» استعارة فعل, + one more) —
  even a model that correctly identifies Trope in this verse can bank only 1 TP.
- Imru1 v59 (Simile, 4 instances) — same structural cap.

This is the single largest bucket for 3 of 4 elements, and it is **not a model-quality
finding** — it's an artifact of the one-appearance-per-element-per-verse schema
(`prompts.py`), inherited unchanged from Phase 1 into Phase 2's Config A/B (Config C's
per-verse extraction schema has the identical limitation — noted in `report_3i.md` §8's
footnote on Nabigha v7).

### (c) subtype-knowledge — مجاز مرسل / استعارة قديمة (55, Trope only)

All 13 مجاز مرسل and 15+2 استعارة قديمة(-مرشحة) TEST instances that scored FN. E.g. Imru1
v12 «الدِّمَقْسِ», v14 «عَقَرْتَ بَعِيْرِي», v24 «أهْوالًا», v28 «مِرْطٍ» — all مجاز مرسل,
all missed by v4_combined, consistent with §3c's "85%→85% unchanged" finding and the Phase
2 Nabigha probe's partial (4/10 known-positive, any-of-2-runs) recovery under free-form
reasoning.

### (d1) boundary-confusion — mechanical scan (13: Trope 5, Kenning 8)

Found **8 additional** Trope↔Kenning boundary-confusion instances beyond the 6 manually
shortlisted ones, via the mechanical span-overlap scan alone:

- Imru1 v26: GT Kenning «فَجِئْتُ وقَدْ نَضَتْ لِنَوْمٍ ثِيَابَهَا...» (كناية عن موصوف) missed,
  while GPT's same-verse Trope prediction «نَضَتْ لِنَوْمٍ ثِيَابَهَا» — an FP against Trope's
  own ground truth — sits right on top of it.
- Jarir v14: GT Kenning «...نزوليَ بِالمَوْماةِ ثم ارتحاليا» missed, GPT's Trope FP «رجيعٌ
  أَملها» in the same verse overlaps it.
- Imru1 v66, Jarir v8/v10/v33: GT Trope (استعارة فعل مرشحة / استعارة تمثيلية) missed, while
  Gemini's (or Claude's, v8) same-verse Kenning prediction is an FP overlapping the same
  span.

This confirms the boundary-confusion failure mode documented in
`error_characteristics_summary.md` row 3 is not confined to the hand-picked DEV example —
it recurs on TEST, at a modest but non-trivial rate (13/853 non-schema-capped FNs ≈ 1.5%
pooled across Trope+Kenning).

### (d2) annotation-sensitive — shortlist only (13: Trope 4, Kenning 9)

Exactly the 6 TEST rows from `ali_adjudication_shortlist.md` (Imru1 v2, v4, v25, v34, v43,
v45), expanded to their individual GT-instance level and only for the models/instances that
actually scored FN there (e.g. shortlist #12, Imru1 v34: Claude caught one of the two
instances, so only GPT's and Gemini's misses on that verse are tagged d2, and only the
2 GT instances × the 2 models that missed them = a handful of events, not the full verse ×
3 models).

### (e) model-capability (133, Trope only — استعارة فعل / مجاز عقلي)

The two subtypes §3c already identifies as v4_combined's real, validated wins
(83%→62% and 83%→66% missed respectively) still have a combined 133 FN instances on
TEST — this bucket says: per §3i, Config A (Fable 5, **same strict format**) moves pooled-DEV
Trope recall from F1 0.059→0.200 with **no precision cost**, and these two subtypes are
exactly the "explicit pattern, no free-form reasoning needed" kind Config A's gain plausibly
comes from — so a stronger model within the existing pipeline architecture is the most
likely lever for these 133, not a redesign of the output format.

### (a) format-suppression candidate (196, Kenning only)

Every Kenning FN not otherwise explained. Anchor: Imru2 v6 «فُوهَا كُلَّمَا نَبَّهْتُهَا...»
— Existing/Config A/Config B all miss it, Config C catches it in both runs with a
substantively correct rhetorical justification (`report_3i.md` §5). Since Kenning carries
no annotated subtypes in this project's ground-truth taxonomy, this bucket cannot be
narrowed further than "same element as the anchor pattern" — **this is the least specific
bucket in this report and should be read as the weakest-evidence one**, despite being the
second-largest.

### Unclassified (150: Trope 14, Simile 35, Kenning 0, Antonymy 101)

Reported honestly rather than folded into a nearby bucket. Antithesis dominates this bucket
almost entirely, which is itself informative: this project's existing Antithesis findings
(§3d, over-claiming) are about *precision*, and this decomposition — built to explain
*recall* gaps — correctly has little to say about it. The Simile and residual-Trope
unclassified instances are candidates for a future, more granular error review (e.g. with
Dr. Hussein) rather than something this analysis-only session can explain further.

---

## 4. Bonus finding — proposed additions to the adjudication shortlist

While scanning for (d1), a broader check for verses where **all 3 models agree on the same
FP span** (the Jarir v37 "possible annotation gap" pattern from the existing shortlist) also
turned up **5 new candidates not already on `ali_adjudication_shortlist.md`**. Per the
2026-07-26 session's explicit instruction, these are listed here as proposals for Dr.
Hussein's review — **not** auto-classified into (d2) or counted in any bucket above, since
judging whether an annotation is incomplete is his call, not a mechanical one:

| Poem, verse | Element | All 3 models' claimed span (paraphrased where models differ on extent) |
|---|---|---|
| Imru1 v70 | Simile | «كَلَمْعِ اليَدَيْنِ (في حَبِيٍّ مُكَلَّلِ)» |
| Jarir v14 | Antonymy | «نزوليَ (بِالمَوْماةِ) ... ثم ارتحاليا» |
| Jarir v36 | Trope | «(فقد) كنتُ نارًا (يصطليها عدوُّكم)» |
| Jarir v38 | Antonymy | «(عَفُّ) الفقر ... مُشْتَرَكُ الغِنَى» |
| Abu_Tammam v16 | Simile | «(وَ)كَأَنَّ بَهجَتَها وَبَهجَةَ كَأسِها نارٌ وَنورٌ» — note: the *same* verse already has an existing shortlisted Antithesis entry (#8, «نارٌ وَنورٌ») for a different element |

---

## 5. Limitations

1. **(a) and (e) are DEV→TEST projections, never directly observed on these instances** —
   restated here as the single most important caveat in this document. If a future session
   gets supervisor sign-off to spend budget on it, the only way to *confirm* rather than
   *infer* format-suppression or model-capability on a TEST instance would be a fresh,
   never-annotated poem run through Config A/B/C — not TEST itself, which stays spent
   (`PROJECT_STATE.md` §2).
2. **(a)'s Kenning-wide scope is a resolution limit, not a finding**: this project's ground
   truth has no periphrasis subtype taxonomy (unlike Trope's مجاز مرسل/استعارة فعل/etc.), so
   bucket (a) cannot be narrowed below "this FN is Kenning" — the 47.3% figure should be read
   as an upper bound on how many Kenning FNs *could* plausibly be format-related, not a count
   of confirmed cases.
3. **(d1)'s mechanical scan uses token-overlap (threshold 0.5), the same primitive already
   validated project-wide** — but a genuine boundary confusion could in principle produce a
   non-overlapping span (e.g. the model picks a related but non-overlapping phrase in the
   same verse); this scan is a lower bound on boundary-confusion prevalence, not an exact
   count.
4. **This decomposition is per-model-event, not per-unique-instance** — an instance missed
   by all 3 models contributes 3 events to whichever bucket it lands in (usually the same
   bucket each time, since content-based buckets don't depend on which model missed it, but
   (d1)'s mechanical scan can differ by model since different models produce different FPs).
