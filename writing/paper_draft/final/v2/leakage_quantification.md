# Leakage Quantification — Worked Examples vs. Evaluated Rows

Answers reviewer fix items touching `paper_trimmed.md`'s existing, honest-but-partial leakage disclosure (Data and Methods, "The elements and subtypes," final paragraph) and Reviewer 1 §2 of `reviewer_simulation.md`. **Zero new API calls.** Every count below is read directly from already-archived prompt-builder code and the project's own `results/phase2_chatlike/example_gap_analysis.md`, cross-checked against `data/elements/*.txt` and the poem text files in `archive/Forth_Step/Data/`.

This document covers every evaluation in the paper that uses a worked example of any kind, and states, per evaluation, how many of its worked examples coincide with rows it then scores.

---

## 1. Phase 1 (baseline, v4_combined) — TEST-poem leakage, already disclosed in the paper, quantified exactly

**Examples used**: `data/elements/{Trope,Simile,Kenning,Antonymy}.txt`, unchanged since Phase 1, loaded into the system message of every Phase 1 call. Each file holds 4–5 worked example verses, drawn one per poem in the fixed order Imru1 → Imru2 → Nabigha → Jarir → Abu_Tammam.

**Scored on**: all 5 poems' TEST subset (Imru1, Jarir, Abu_Tammam) for the frozen headline table.

| File | Example # | Poem | Verse | In the scored TEST set? |
|---|---|---|---|---|
| `data/elements/Trope.txt` | 1 | Imru1 | v22 | **Yes** |
| `data/elements/Trope.txt` | 4 | Jarir | v12 | **Yes** |
| `data/elements/Simile.txt` | 1 | Imru1 | v25 | **Yes** |
| `data/elements/Simile.txt` | 4 | Jarir | v9 | **Yes** |
| `data/elements/Simile.txt` | 5 | Abu_Tammam | v6 | **Yes** |
| `data/elements/Kenning.txt` | 1 | Imru1 | v23 | **Yes** |
| `data/elements/Kenning.txt` | 4 | Jarir | v11 | **Yes** |
| `data/elements/Kenning.txt` | 5 | Abu_Tammam | v7 | **Yes** |
| `data/elements/Antonymy.txt` | 1 | Imru1 | v38 | **Yes** |
| `data/elements/Antonymy.txt` | 4 | Jarir | v26 | **Yes** |
| `data/elements/Antonymy.txt` | 5 | Abu_Tammam | v8 | **Yes** |

**Count: 11 of the 19 total worked examples across the 4 files (58%) are literal verses from the exact TEST poems the frozen headline table scores** — each one is shown to the model in the same system message that later asks it to analyze that poem's full verse set, including the example verse itself. Source: `results/phase2_chatlike/example_gap_analysis.md` §0 (verified there byte-for-byte against the poem text files; re-confirmed here against the table's own poem/verse references, not re-derived independently).

This is the leakage `paper_trimmed.md` already discloses (Data and Methods, final paragraph of "The elements and subtypes"), restated here with the per-file, per-example breakdown the paper's own prose summarizes but does not table.

---

## 2. Phase 2 Config A and Config B — a second, undisclosed leakage channel: DEV-poem examples

**Examples used**: identical to Phase 1 — Config A (`experiments/phase2_chatlike/run_config_ab.py`, Fable 5 substituted for Claude Sonnet 4.6) and Config B (`experiments/phase2_chatlike/prompt_config_b.py`, terminology-corrected) both build their system message from `build_system_message_variant("v4_combined")` (`experiments/pilot_3models/prompt_variants.py`), the exact same function Phase 1 uses, over the same unedited `data/elements/*.txt` files. Config B's own docstring states explicitly: "Phase 1's `data/elements/*.txt` files are NOT edited."

**Scored on**: DEV only (Imru2, Nabigha) — per `paper_trimmed.md`'s own DEV/TEST discipline, Config A/B never touch TEST.

The TEST-poem examples quantified in §1 (Imru1, Jarir, Abu_Tammam) are therefore *not* leakage for Config A/B, since those poems are never scored by this configuration. **But two of each file's examples are drawn from Imru2 and Nabigha themselves** — the exact poems Config A/B scores:

| File | Example # | Poem | Verse | In Config A/B's scored DEV set? |
|---|---|---|---|---|
| `data/elements/Trope.txt` | 2 | Imru2 | v15 | **Yes** |
| `data/elements/Trope.txt` | 3 | Nabigha | v7 | **Yes** |
| `data/elements/Simile.txt` | 2 | Imru2 | v6 | **Yes** |
| `data/elements/Simile.txt` | 3 | Nabigha | v14 | **Yes** |
| `data/elements/Kenning.txt` | 2 | Imru2 | v20 | **Yes** |
| `data/elements/Kenning.txt` | 3 | Nabigha | v8 | **Yes** |
| `data/elements/Antonymy.txt` | 2 | Imru2 | v20 | **Yes** |
| `data/elements/Antonymy.txt` | 3 | Nabigha | v20 | **Yes** |

**Count: 8 of 8 possible DEV-example slots (every one of the 4 files' Imru2 and Nabigha examples) leak into Config A/B's own scored set — a 100% overlap rate for the examples that are structurally capable of overlapping Config A/B's evaluation**, higher proportionally than the 58% TEST-example overlap rate in §1, because Config A/B's DEV-only scope has only 2 poems for a DEV example to possibly land in, against 3 for TEST.

**This channel is not mentioned anywhere in `paper_trimmed.md`'s current leakage disclosure**, which frames the finding only in terms of TEST exposure ("three of every element file's four or five worked examples are, in fact, literal verses from the three TEST poems," Data and Methods). The DEV-poem examples are the *other* 2 of each file's 4–5 examples, and they leak into Phase 2's Config A/B results by the identical mechanism. Practical impact is, by the same logic the paper already applies to the TEST case, "likely small but non-zero and unquantified" — no experiment in this project isolates how much of Config A's or Config B's DEV-scale F1 (Results, "Phase 2: Config A/B/C disentanglement") is attributable to this.

---

## 3. Config C — zero worked-example leakage, by construction

**Examples used**: none. `experiments/phase2_chatlike/prompt_config_c.py`'s Stage 1 prompt (`STAGE1_PROMPT_TEMPLATE`) is a verbatim Arabic instruction naming the four rhetorical categories and their one-line definitions; it contains no worked example verse of any kind, from this corpus or elsewhere (confirmed by direct reading of the template string, lines 25–43 of that file: it lists the four category names and asks the model to analyze the target verse against them, with no "Example:" field anywhere in either the Stage 1 user-message template or the empty `STAGE1_SYSTEM_MESSAGE`). Stage 2 (`STAGE2_SYSTEM_MESSAGE`) is a pure extraction schema, also with no worked example.

**Count: 0 of 0.** Config C's periphrasis gain on Imru2 (strict F1 0.111→0.316, Results, "Phase 2: Config A/B/C disentanglement") cannot be attributed, even in part, to worked-example exposure, since there is none in its prompt — a point in favor of treating that gain as a genuine format effect rather than a second-order leakage artifact.

**An asymmetry worth stating explicitly**, however: the figure Config C is compared against — "the same-poem existing-pipeline figure of 1/0/16, F1=0.111" (Results, same section) — *is* produced by the standard v4_combined pipeline, which does carry the Kenning.txt leakage quantified in §2 (its own Imru2 example, example #2, `Kenning.txt` v20). The comparison Config C's gain rests on is therefore not example-for-example matched: one side of the comparison has worked-example exposure to Imru2 and the other does not. This does not reverse the direction of the finding, but it means Config C's advantage over the existing pipeline is confounded with a second variable (presence vs. absence of any worked example) in addition to the one the paper names (closed-schema vs. free-form output format).

---

## 4. Phase 3 (twenty-five-subtype recall screen) — one-shot baseline: externally sourced, no corpus leakage found

**Examples used**: `experiments/phase3_subelements/subtype_defs.py`'s `SUBTYPE_DEFS[...]["example"]` field, one per subtype. Direct inspection of this file's `"example"` entries shows citations external to this project's 5-poem corpus — e.g. the طباق إيجاب entry's example is Qur'an 18:18 (الكهف), طباق سلب's is Qur'an 4:108 (النساء), تشبيه مطول's is a verse attributed to Al-Muraqqish al-Akbar. None of the entries inspected cite Imru' al-Qais, Jarir, Abu Tammam, or Al-Nabigha Al-Dhubyani by name or verse number.

**Count: not fully enumerated here — a complete check would require reading all 25 `SUBTYPE_DEFS` entries individually against the 5-poem corpus's full text, which this task did not do line-by-line for every subtype.** What this document confirms is the sourcing pattern (external literary/Qur'anic citations, not this project's own corpus) for the subtypes it did inspect; a human author should spot-check the remaining `SUBTYPE_DEFS` entries before stating "zero leakage" as a completed fact rather than an observed pattern. This is flagged as **unverified beyond a partial check**, not confirmed for all 25 subtypes.

## 5. Phase 3 — three-shot variant: held out by a verified code-level mechanism

**Examples used**: the one-shot example above, plus 2 additional real-corpus examples per subtype (`experiments/phase3_subelements/fewshot_prompts.py`).

**Hold-out mechanism**: `experiments/phase3_subelements/run_fewshot_check.py` (lines 2, 8, 86, 88) selects "the FIRST 2 rows in that subtype's [ground truth]" as the held-out few-shot examples, and its own print statement at scoring time (`held out {len(holdout)} for few-shot`) confirms those same 2 rows are excluded from the test rows subsequently scored for that subtype.

**Count: 0 overlapping rows, by a code-level exclusion this document verified directly** (not merely asserted by the docstring) — the held-out rows are removed from the scored set before scoring runs, not merely labeled as held out. This is the one leakage-adjacent design in this project that was built specifically to avoid the problem found elsewhere, and it is correctly implemented.

---

## Summary table

| Evaluation | Worked examples | Leakage mechanism | Overlap found |
|---|---|---|---|
| Phase 1 baseline/v4_combined (TEST) | `data/elements/*.txt` | TEST-poem examples scored by TEST evaluation | **11/19 examples (58%), already disclosed in the paper** |
| Phase 2 Config A/B (DEV) | same `data/elements/*.txt` | DEV-poem examples scored by DEV evaluation | **8/8 possible slots (100%), not previously disclosed anywhere in the paper** |
| Phase 2 Config C | none | — | **0/0 — no worked examples at all; comparison baseline (existing pipeline) is itself leaky, an asymmetry worth noting** |
| Phase 3 one-shot | `subtype_defs.py` citations | external (Qur'an, named pre-Islamic poets) | **0 found in the subtypes checked; not exhaustively verified across all 25** |
| Phase 3 three-shot | one-shot example + 2 corpus examples | code-level row exclusion | **0 — verified correctly implemented** |

**Net assessment for the human authors**: the paper's existing leakage disclosure is accurate but incomplete — it names the TEST-poem channel (§1) but not the structurally identical DEV-poem channel affecting Phase 2's Config A/B (§2), which this document finds at a numerically higher overlap rate (100% vs. 58%) for the examples capable of overlapping that evaluation's own scope. Config C (§3) and Phase 3 (§4–5) are comparatively clean, with one open verification item (§4, the un-checked remainder of `SUBTYPE_DEFS`) flagged rather than assumed. No number in `paper_trimmed.md` is changed by this document; it supplies exact counts and file paths for a gap the paper's prose already gestures at but does not fully cover, and surfaces one gap (§2) the paper does not mention at all.
