# Example-vs-Test Gap Analysis — `data/elements/*.txt`

**Purpose**: in response to the 2026-07-23 supervisor question "what are the differences
between the examples used in the few-shot prompt and the testing — why is it missing?",
this document characterizes the 4 canonical element-definition files' worked examples
against the ground-truth instance population. **Zero new API calls** — pure analysis of
already-existing files. Code: `experiments/phase2_chatlike/example_gap_analysis.py`.

---

## 0. Headline finding (not what was expected going in)

**Every single one of the 19 worked examples across all 4 files is a real, annotated verse
from this project's own 5-poem corpus — not a synthetic or external example — and each
file draws exactly one example per poem, in the fixed order Imru1 → Imru2 → Nabigha →
Jarir → Abu_Tammam:**

| # | Trope.txt | Simile.txt | Kenning.txt | Antonymy.txt |
|---|---|---|---|---|
| 1 | Imru1 v22 (**TEST**) | Imru1 v25 (**TEST**) | Imru1 v23 (**TEST**) | Imru1 v38 (**TEST**) |
| 2 | Imru2 v15 (DEV) | Imru2 v6 (DEV) | Imru2 v20 (DEV) | Imru2 v20 (DEV) |
| 3 | Nabigha v7 (DEV) | Nabigha v14 (DEV) | Nabigha v8 (DEV) | Nabigha v20 (DEV) |
| 4 | Jarir v12 (**TEST**) | Jarir v9 (**TEST**) | Jarir v11 (**TEST**) | Jarir v26 (**TEST**) |
| 5 | — | Abu_Tammam v6 (**TEST**) | Abu_Tammam v7 (**TEST**) | Abu_Tammam v8 (**TEST**) |

Verified exactly (byte-for-byte, modulo quote-mark style) against the poem text files —
e.g. Trope.txt example #1 ("وَمَا ذَرَفَتْ عَيْنَاكِ...") is Imru1 v22 verbatim; example #4
("لَحِقْتُ وأَصحابي...") is Jarir v12 verbatim.

**This means 3 of every element file's 4-5 examples (60-75%) are drawn from TEST poems —
the exact poems the frozen TEST evaluation scores.** `data/elements/*.txt` is loaded into
the system message of **every** prompt variant this project has ever run (baseline, v1-v4,
decomposed, per-verse, Config A/B — the file is explicitly "not edited," per `GLOSSARY.md`,
"since Phase 1 reproducibility depends on these files staying byte-identical"). So the
frozen TEST run (`PROJECT_STATE.md` §3a) has, since Phase 1, shown the model Imru1 v22 (with
its Trope answer implicit in the fact it's presented as a Trope example) **in the very same
call** that later asks the model to analyze Imru1's full 81 verses — including verse 22
itself. The same holds for Jarir and Abu_Tammam.

**This is not primarily a subtype-coverage problem — it's a held-out-set contamination
problem, present in every frozen number this project has ever reported.** It also directly
contradicts `experiments/phase2_chatlike/PROPOSAL_fewshot.md`'s stated premise (line 19):
*"Reuse `data/elements/{Kenning,Trope}.txt`'s own existing canonical example couplets
(already shipped with the element definitions, **never drawn from the 5 annotated
poems**)"* — that claim is factually wrong per the table above, and the proposal's
demonstration-selection plan needs to be redesigned before that experiment is ever run,
since demonstrating with (e.g.) Trope.txt's existing Jarir v12 example, then scoring Jarir,
would be direct TEST leakage rather than the "zero DEV/TEST leakage" the proposal claims.

**Practical impact on frozen numbers is likely small but non-zero and unquantified**: each
example shows only 1 verse per poem (not the specific instance being scored at any given
moment), the model still misses the *majority* of TEST instances despite this exposure
(§3a), and no experiment in this project has isolated how much of any score is attributable
to this. This is flagged here as a methodology gap for the write-up (`limitations_future_work.md`
is the natural home for it), not re-litigated against any frozen number — per standing
discipline, TEST stays spent regardless.

---

## 1. Trope subtype coverage — examples vs. ground truth

| Subtype | In examples (n=9 instances across 4 example verses) | Full corpus (n=237) | TEST-only (n=179) |
|---|---|---|---|
| استعارة فعل (verbal metaphor) | 2 (22.2%) | 111 (**46.8%**) | 78 (**43.6%**) |
| مجاز عقلي (rational trope) | 3 (33.3%) | 52 (21.9%) | 41 (22.9%) |
| استعارة تمثيلية (extended/whole-clause) | 1 (11.1%) | 29 (12.2%) | 26 (14.5%) |
| مجاز مرسل (metonymy) | 3 (33.3%) | 24 (10.1%) | 13 (7.3%) |
| استعارة قديمة (archaic/lexicalized) | **0 (0%)** | 19 (8.0%) | 17 (9.5%) |
| استعارة حديثة | **0 (0%)** | 4 (1.7%) | 4 (2.2%) |

**Two different stories, both real, and they point in opposite directions**:

1. **مجاز مرسل is *not* absent from the example verses by raw instance count** — it's
   actually the joint-largest represented subtype (33.3%, tied with مجاز عقلي), because 2 of
   the 4 example verses (Imru2 v15, Nabigha v7) happen to be multi-figure verses that
   include a مجاز مرسل instance among others. This is the opposite of what was expected
   going in.
2. **But مجاز مرسل is never *named* anywhere in Trope.txt** — confirmed by direct search:
   the file contains zero occurrences of the strings "استعارة", "تمثيل", or "مجاز مرسل"
   (only the unified، subtype-blind explanation from `GLOSSARY.md`'s already-documented
   finding). So even though the raw text of a مجاز مرسل instance sits inside an example
   verse, nothing in the file tells a reader (model or human) *that* it's مجاز مرسل, *where*
   the span is, or *why* — the same problem exists for all 3 other subtypes too (no example
   in this file has ANY span highlighting, subtype label, or explanation attached; they are
   4 bare verse lines). Multi-figure entanglement compounds this: example #1 (Imru1 v22) and
   #3 (Nabigha v7) each contain 2-3 *simultaneous* Trope instances of *different* subtypes
   with no indication which one the example is meant to illustrate.
3. **استعارة فعل — the single largest and best-detected subtype (§3c: 62% missed after
   v4, still the "best" of a bad set) — is the most under-represented by *proportional
   share*** (22.2% of example instances vs. 43-47% of the real corpus). استعارة قديمة gets
   zero representation entirely, consistent with its being the second-flattest subtype
   in §3c (80%→60% missed).

**Reading these together**: representation-by-instance-count in the raw example text does
not straightforwardly predict subtype performance (استعارة فعل does best despite being
under-represented; مجاز مرسل does worst despite tying for best-represented) — the more
load-bearing gap is the **complete absence of subtype naming/labeling**, which is exactly
what `PROPOSAL_fewshot.md` and Config B (§3i) already target, and what this analysis now
independently confirms from the example-file side rather than the prompt-design side.

---

## 2. Marker explicitness

| Element | Examples with an explicit marker | Detail |
|---|---|---|
| Simile | 2 of 5 (40%) | Imru2 v6 («كَالمِسْكِ»), Abu_Tammam v6 («كَأَنَّما») carry an explicit كـ/كأن particle. The other 3 (Imru1 v25 — تشبيه مطول, Nabigha v14 — تشبيه مطول, Jarir v9 — تشبيه تمثيلي) are all **extended/analogical** similes with no standalone particle — exactly the "silent construction" subtype. |
| Trope | 0 of 4 (0%) | Expected — Trope's definition explicitly requires the *absence* of a comparative marker (a contextual clue blocking the literal reading instead). |
| Kenning | 0 of 5 (0%) | Same — periphrasis relies on plausible-literal-reading ambiguity, not an overt particle. |
| Antonymy | 1 of 5 (20%, Imru1 v38) | The marker found there belongs to that verse's *co-occurring Simile* instance («كَأنَّهَا»), not to the Antonymy pair itself — Antonymy's own signal is always lexical opposition (بات/ظلّ, الأدنى/البعد), never a particle. |

**Simile's own examples are majority-implicit (60% no standalone particle)**, despite
Simile.txt's explanation naming كأنّ/مثل as *the* defining marker — a mismatch between the
explanation (marker-centric) and 3 of 5 worked examples (marker-free, analogical/extended
type). This mirrors §3c's own subtype story for Trope: the *explicit* forms are the ones
every intervention already handles well; the *implicit/extended* forms are where the
project's difficulty concentrates, and Simile.txt's own example mix already skews toward
the harder, implicit end without saying so.

---

## 3. Multi-figure verses: examples vs. corpus

| Element | Corpus multi-figure share | Example multi-figure share |
|---|---|---|
| Trope | 119/140 (85%) | 3/4 (75%) |
| Simile | 54/61 (89%) | 5/5 (100%) |
| Kenning | 114/123 (93%) | 5/5 (100%) |
| Antonymy | 39/44 (89%) | 4/5 (80%) |

**Multi-figure verses are the corpus norm (85-93% of all annotated verses), not an
example-specific artifact** — classical Arabic poetry is rhetorically dense by nature, so
the examples' multi-figure rate (75-100%) is roughly proportional to, if anything slightly
below, the corpus baseline. The gap this creates isn't "unrepresentative sampling" so much
as **the examples never disambiguate which of several simultaneous instances they're
illustrating** (§1 above) — a labeling problem that the corpus's inherent density makes
almost unavoidable unless the example format is changed to isolate a span explicitly (which
none of the 4 files currently do).

---

## 4. Span length: examples vs. corpus

| Element | Corpus avg span length (words) | Example-verse span length (words) |
|---|---|---|
| Trope | 2.8 (n=239) | 2.6 (n=9) |
| Simile | 7.0 (n=72) | 8.2 (n=5) |
| Kenning | 3.2 (n=216) | 4.5 (n=10) |
| Antonymy | 2.7 (n=48) | 2.0 (n=6) |

No dramatic mismatch for Trope/Antonymy. Simile and Kenning's example-verse spans run
somewhat *longer* than the corpus average (8.2 vs 7.0; 4.5 vs 3.2) — consistent with §1-§3's
finding that the example verses skew toward the "extended/analogical, multi-word" end of
each element's range rather than the shortest, most lexically-anchored instances.

---

## 5. Summary gap table

| Dimension | What the examples demonstrate | What TEST demands | Gap |
|---|---|---|---|
| Trope subtype naming | Zero subtypes named or exemplified as such anywhere in Trope.txt | 6 distinct subtypes, unevenly hard (§3c) | **Total** — confirms and sharpens GLOSSARY.md's finding |
| Trope subtype instance-count | مجاز مرسل tied for most-represented (33%) by raw count, but unlabeled; استعارة فعل under-represented (22% vs 44-47% actual share) | استعارة فعل dominates by volume and is the best-performing subtype | Representation ≠ labeling ≠ performance — three separate axes, easy to conflate |
| Span/subtype isolation | Zero spans highlighted, zero rationale, in all 4 files | Model must extract one specific span per element per verse | **Total** — every example is a bare, unannotated verse |
| Marker explicitness (Simile) | 60% implicit/extended (تشبيه مطول/تمثيلي), no particle | Explicit-marker similes are already near-ceiling; implicit ones are exactly where the harder end of the range lives | Examples already skew toward the harder sub-form without saying so |
| Multi-figure entanglement | 75-100% of examples are multi-figure verses with no disambiguation | 85-93% of the real corpus is multi-figure too (not example-specific) | Corpus-inherent, but examples never resolve which instance is "the point" |
| **DEV/TEST provenance** | **3 of every 4-5 examples per file are literal TEST-poem verses (Imru1, Jarir, Abu_Tammam)** | TEST is supposed to be a held-out, never-tuned-against set | **Contradicts the project's own TEST discipline at the example-file level** — present since Phase 1, still true today, and factually contradicts `PROPOSAL_fewshot.md`'s "never drawn from the 5 annotated poems" claim |

**Recommendation for `PROPOSAL_fewshot.md`** (not implemented here, flagged for whoever
picks that proposal up next): its demonstration-selection plan needs new source material —
either genuinely external/synthetic worked examples, or verses from a poem outside this
project's 5-poem corpus entirely — since the current plan to "reuse `data/elements/*.txt`'s
existing canonical examples" would demonstrate with the exact verses TEST later scores.
