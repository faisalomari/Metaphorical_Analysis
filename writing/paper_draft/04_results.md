# Results

Every number below is cited to its exact source file and marked **final** (frozen TEST, never re-run or re-scored), **preliminary** (DEV or single-poem data, not yet validated at TEST scale), or **incomplete** (partial data by design — missing runs, single-model, recall-only, or precision/F1 structurally unmeasurable).

## Phase 1: frozen TEST results

Ground-truth support on TEST (pooled, deduplicated, across Imru1, Jarir, and Abu Tammam): trope 179, simile 52, periphrasis 147, antithesis 43. Strict-criterion precision/recall/F1, baseline versus the refined prompt (`v4_combined`), two-run majority:

| Element | Model | Baseline P/R/F1 | v4_combined P/R/F1 | Status |
|---|---|---|---|---|
| Trope | Claude Sonnet 4.6 | 0.85/0.09/0.171 | 0.89/0.14/0.242 | **final** |
| Trope | GPT-5.4-mini | 0.86/0.03/0.065 | 0.64/0.16/0.251 | **final** |
| Trope | Gemini 3.5 Flash | 0.89/0.19/0.313 | 0.83/0.25/0.386 | **final** |
| Simile | Claude Sonnet 4.6 | 0.82/0.54/0.651 | 0.82/0.54/0.651 | **final** |
| Simile | GPT-5.4-mini | 0.88/0.58/0.698 | 0.91/0.60/0.721 | **final** |
| Simile | Gemini 3.5 Flash | 0.82/0.62/0.703 | 0.89/0.62/0.727 | **final** |
| Periphrasis | Claude Sonnet 4.6 | 0.80/0.05/0.102 | 0.57/0.05/0.099 | **final** |
| Periphrasis | GPT-5.4-mini | 0.20/0.01/0.013 | 0.36/0.03/0.051 | **final** |
| Periphrasis | Gemini 3.5 Flash | 0.69/0.06/0.113 | 0.65/0.10/0.176 | **final** |
| Antithesis | Claude Sonnet 4.6 | 0.26/0.12/0.161 | 0.33/0.14/0.197 | **final** |
| Antithesis | GPT-5.4-mini | 0.27/0.09/0.138 | 0.23/0.12/0.154 | **final** |
| Antithesis | Gemini 3.5 Flash | 0.17/0.09/0.121 | 0.19/0.12/0.145 | **final** |

*Source: `PROJECT_STATE.md` §3a; `writing/chapters/results.md` Table 1.* Raw TP/FP/FN (strict, `v4_combined`): Trope — Claude 25/3/154, GPT 28/16/151, Gemini 45/9/134. Simile — Claude 28/6/24, GPT 31/3/21, Gemini 32/4/20. Periphrasis — Claude 8/6/139, GPT 4/7/143, Gemini 15/8/132. Antithesis — Claude 6/12/37, GPT 5/17/38, Gemini 5/21/38. *(These rows use Phase 1's own run output; the underlying frozen artifact used the superseded English names "kenning"/"antonymy." See `GLOSSARY.md` for the citation convention.)*

The refined prompt improves every model on trope, simile, and antithesis, and is essentially flat on periphrasis — periphrasis strict F1 never exceeds 0.176 anywhere in this table, against simile's 0.65–0.73 ceiling. Run-to-run decision agreement is 88–100% under the baseline prompt and 89–100% under `v4_combined`, across all four elements and three models; Gemini's baseline behavior was perfectly deterministic on TEST (100%) and the refined prompt's added rules cost some of that, most visibly on periphrasis (89%). *Source: `PROJECT_STATE.md` §3b.*

**The token-overlap criterion reveals a substantially larger baseline→refined-prompt gap for antithesis specifically**, due to Arabic morphological variation (e.g. النُّوّامِ against the ground truth's نَوَّمُوا): baseline token F1 is 0.419/0.345/0.545 (Claude/GPT/Gemini) against 0.161/0.138/0.121 strict; refined-prompt token F1 is 0.393/0.431/0.609 against 0.197/0.154/0.145 strict. A second, test-scale-only finding is that all three models systematically **over-claim antithesis**: false positives exceed true positives for every model at baseline (Claude TP=5/FP=14, precision 0.263) — the opposite failure mode from trope and periphrasis, which are under-detected rather than over-claimed. *Source: `PROJECT_STATE.md` §3a, §3d.*

## Trope subtype breakdown (final, TEST, pooled across three models)

| Subtype | n | Baseline missed | v4_combined missed |
|---|---|---|---|
| استعارة فعل (verbal metaphor) | 76 | 83% | 62% |
| مجاز عقلي (rational trope) | 41 | 83% | 66% |
| استعارة تمثيلية (whole-clause allegory) | 24 | 33% | 29% |
| استعارة قديمة (archaic/lexicalized) | 15 | 80% | 60% |
| مجاز مرسل (metonymy, single lexicalized word) | 13 | 85% | 85% |
| استعارة حديثة | 4 | 75% | 75% (n=4, too thin to generalize) |

*Source: `PROJECT_STATE.md` §3c.* A two-poem DEV analysis had flagged استعارة تمثيلية as the hardest trope subtype; at TEST scale (three poems, larger n) this reversed — استعارة تمثيلية is in fact the *easiest* subtype in the table, both before and after refinement. The refined prompt's validated wins are استعارة فعل and مجاز عقلي; مجاز مرسل is the one subtype no Phase 1 intervention moves at all (85%→85%, unchanged). A majority-vote ensemble across all three models gives no improvement over the best single model for trope or periphrasis (identical F1 — the models miss the same instances, not independent errors an ensemble could average out), and is worse than the best single model for simile. *Source: `PROJECT_STATE.md` §3e.*

## Phase 2: Config A/B/C disentanglement (preliminary, DEV only)

Pooled DEV (Imru2+Nabigha), strict criterion, TP/FP/FN, F1:

| Element | Existing (Sonnet 4.6 + v4) | Config A (Fable 5 + v4) | Config B (Sonnet 4.6 + v4, terms corrected) | Status |
|---|---|---|---|---|
| Trope | 2/6/58, F1=0.059 | 7/3/53, F1=0.200 | 3/4/57, F1=0.090 | **preliminary** |
| Periphrasis | 5/3/64, F1=0.130 | 8/4/61, F1=0.198 | 5/7/64, F1=0.123 | **preliminary** |

*Source: `results/phase2_chatlike/report_3i.md` §2–§3; `writing/paper_plan/results_for_paper.md` Table 4.* Config A (model substitution alone, same prompt) moves both trope and periphrasis with no precision cost. Config B (terminology correction alone) gives trope a modest genuine boost but leaves periphrasis flat-to-worse — correcting "kenning"→"periphrasis" alone does not unlock periphrasis recall.

**Config C (Imru2 only, two-stage free-form pipeline)**: 6/15/11, F1=0.316 strict (token F1=0.421) on periphrasis, against the same-poem existing-pipeline figure of 1/0/16, F1=0.111 — the largest single periphrasis gain found anywhere in this project, and it catches the exact motivating verse (Imru2 v6, «كُلَّمَا نَبَّهْتُهَا») that every structured-pipeline configuration misses. *Source: `PROJECT_STATE.md` Phase 2 §3i; `report_3i.md` §3.* **This gain is run-to-run unstable, not merely a caveat but part of the finding**: a targeted Nabigha مجاز مرسل recall probe (known-positive verses only, no precision/F1 claim) caught 4 of 10 verses in at least one of two runs, but only 1 of 10 under this project's own two-run-majority convention — most hits came from a single run of the pair. *Source: `report_3i.md` §8–§9; `results_for_paper.md` Table 4.* Config C's full-poem run on Nabigha was never executed (budget-held, ≈$11.9 estimate); only this narrower, known-positive probe exists for a second poem, so Config C's F1 figure above is single-poem and preliminary, not a replicated finding.

## Phase 3: twenty-five-subtype recall screen (incomplete: recall only, by design)

Every row in this screen is a line Prof. Hussein already tagged positive for its own subtype; no model was ever shown a negative example for any subtype, so **false positives, true negatives, precision, and F1 are mathematically undefined by this design, not merely unmeasured**, for every subtype and every model. *Source: `results/phase3_subelements/MEETING_SUMMARY.md` §4; `results/phase3_crossmodel/summary.md`.* Twelve of the twenty-five tested subtypes have fewer than ten ground-truth instances and are flagged as directionally suggestive only, never as a standalone comparative claim.

Reliable subtypes (n≥10), recall by model, span-level (strict criterion), pooled DEV+TEST:

| Subtype | Parent element | n | Gemini 3.5 Flash | GPT-5.4-mini | Status |
|---|---|---|---|---|---|
| استعارة فعل | Trope | 110 | 0.264 | 0.155 | **incomplete** — recall only |
| كناية عن صفة | Periphrasis | 74 | 0.446 | 0.351 | **incomplete** |
| كناية عن موصوف | Periphrasis | 61 | 0.262 | 0.328 | **incomplete** |
| مجاز عقلي | Trope | 54 | 0.463 | 0.426 | **incomplete**, consistent with the TEST-scale finding above that this subtype is a genuine, replicated hard case |
| طباق إيجاب | Antithesis | 38 | 0.237 | 0.053 | **incomplete** |
| كناية لغوية | Periphrasis | 32 | **0.719** | **0.031** | **incomplete** — see prompt-sensitivity discussion below |
| تشبيه مطول | Simile | 30 | 0.833 | 0.667 | **incomplete** |
| استعارة تمثيلية | Trope | 28 | **0.143** | **0.571** | **incomplete** — see prompt-sensitivity discussion below |
| كناية عن فعل | Periphrasis | 27 | 0.333 | 0.148 | **incomplete** |
| مجاز مرسل | Trope | 24 | 0.292 | 0.000 | **incomplete** |
| استعارة قديمة | Trope | 17 | 0.412 | 0.176 | **incomplete** |
| تشبيه قصير | Simile | 13 | 0.615 | 0.769 | **incomplete** |
| كناية فنية | Periphrasis | 10 | 0.300 | 0.200 | **incomplete** |

*Source: `results/phase3_crossmodel/summary.md`, "Headline table."* This re-score is **span-level**, not the original screen's verse-level `exists=true`-by-majority check; re-scoring at the span level pulled recall down substantially for several subtypes (e.g. استعارة فعل: naive verse-level 0.627 → strict span-level 0.264 for Gemini) because a model's "yes" sometimes pointed at a different candidate figure in the same verse than the one Prof. Hussein annotated — a real localization-accuracy finding, not a scoring artifact. Gemini's original, now-superseded recall screen (also recall-only, verse-level) reported higher numbers for several of these subtypes (e.g. كناية لغوية 90.6%, تشبيه مطول 90%, تشبيه قصير 92.3%, استعارة تمثيلية 7.1%, مجاز مرسل 29.2%); the span-level re-score above, not the original verse-level figures, is this paper's reported number. *Source: `MEETING_SUMMARY.md` §6; `results/phase3_crossmodel/summary.md`.*

**استعارة تمثيلية and كناية لغوية are reported here as prompt-sensitivity effects, not as evidence of a fixed model-capability gap.** Both subtypes show large, model-dependent swings rather than a consistent floor: كناية لغوية goes from Gemini's strongest subtype result (0.719, n=32) to GPT's near-total failure (0.031) on the identical prompt and identical lines — a model-specific, not task-intrinsic, collapse (GPT's two runs agree closely at 1/32 and 2/32, so this is not single-run noise). استعارة تمثيلية shows the reverse pattern — Gemini's weakest subtype (0.143) against GPT's strongest relative performance on this subtype (0.571) — and a one-shot-versus-three-shot comparison run separately for this subtype found recall moving from 15.4% to 38.5% with two additional worked examples, one of the few subtypes few-shot helped at all. *Source: `results/phase3_crossmodel/summary.md`, "Two results stand out"; `MEETING_SUMMARY.md` §8b.* استعارة تمثيلية also reproduces, for a third time in this project, the small-sample-to-full-scale reversal already seen in the TEST subtype breakdown above: it looked fine on a four-instance DEV sample and collapsed to 7.1% recall (original verse-level scoring) at n=28. Read together, these are not evidence that either subtype is inherently beyond these models' reach; they are evidence that performance on these two subtypes is unusually sensitive to which model, which prompt format, and how many worked examples are used — exactly the kind of instability a single-model, single-prompt evaluation would never surface.

Twelve subtypes below n=10 (not used for any comparative claim, included for completeness): كناية بسيطة (n=9, Gemini 0.667/GPT 0.333), طباق في المعنى (n=8, 0.000/0.000), طباق سلب (n=5, 0.000/0.200), استعارة حديثة (n=5, 0.400/0.200), مقابلة تضاد (n=4, 0.500/0.250), تشبيه تمثيلي (n=4, 0.250/0.500), تشبيه الشيء بنفسه (n=4, 0.750/0.250), كناية نسبة (n=4, 0.000/0.000), تشبيه مركب (n=3, 0.667/0.667), استعارة قديمة مرشحة (n=2, 1.000/0.500), استعارة فعل مرشحة (n=2, 0.500/0.000), استعارة تمثيلية مبنية على الكناية (n=2, 0.500/0.000). *Source: `results/phase3_crossmodel/summary.md`.* Claude Sonnet 4.6 was not run on this screen; only Gemini 3.5 Flash (the original screen) and GPT-5.4-mini (a later cross-model pass, $0.98, 1,140/1,140 calls succeeded) have been evaluated.

## Reconciling Phase 1 and Phase 2

Phase 1's own frozen reports describe periphrasis as "resistant across every intervention attempted," a true statement about Phase 1's own structural interventions (per-element decomposition helped one of three models and made the other two measurably worse; per-verse granularity produced a real, cross-poem-replicated gain for two of three models but one that costs four to eight times more per unit of F1 than the adopted method and tops out at F1=0.338). That statement is **contradicted, not merely qualified, by Phase 2's Config C finding** (strict F1 0.111→0.316 on the same poem, Imru2) once free-form reasoning replaces the strict no-explanation JSON format. The two findings are reconciled, not in tension, once format is treated as its own variable: periphrasis is reachable under a different output format, but not yet reliably decidable by any configuration tried, given Config C's run-to-run instability (§ above). This paper reports both halves of that finding together, rather than repeating Phase 1's "resistant to every intervention" framing as if Phase 2 did not exist.

## Works Cited

Abd Alhadi, H., Hussein, A. A. and Kuflik, T. (2023) 'Automatic Identification of Rhetorical Elements in classical Arabic Poetry', *Digital Humanities Quarterly*, 17(2).
