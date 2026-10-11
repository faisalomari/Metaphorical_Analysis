# Prompt Inventory — every prompt-building code path in this repo

**Purpose**: a read-only audit of E1's prompt problem (`experiments/phase4_e1` reused the OLD Phase 1
system message, old terminology, leaking TEST/DEV examples) and what the NEWEST/canonical prompt
actually is. No API calls, no code changes. See `docs/phase4/SESSION_LOG.md` for the step-by-step log
of how this was produced.

---

## 1. Every prompt-building code path found

Searched `experiments/{pilot_3models,phase2_chatlike,phase3_subelements,phase3_crossmodel,phase4_e1}`
for every function that assembles a system or user message. Seven distinct builders found.

### 1.1 `experiments/pilot_3models/prompts.py` — `build_system_message()` / `build_user_message()`

- **Last commit**: `3228554`, 2026-07-21 (Phase 1, frozen, never touched since).
- **Models used**: Claude Sonnet 4.6, GPT-5.4-mini, Gemini 3.5 Flash (Phase 1's 3-model pilot/TEST/DEV).
- **Terminology**: OLD — "Antonymy" (طباق), "Kenning" (كناية). No مجاز subtype language at all.
- **Element definitions included?** Yes — all 4 elements, concatenated verbatim from
  `data/elements/{Trope,Simile,Kenning,Antonymy}.txt`.
- **Example provenance**: each element file's 4-5 worked example verses. Per
  `results/phase2_chatlike/example_gap_analysis.md` §0 (byte-verified): **3 of every element file's
  4-5 examples are literal TEST-poem verses** (one per poem in the fixed order
  Imru1→Imru2→Nabigha→Jarir→Abu_Tammam — TEST poems are Imru1, Jarir, Abu_Tammam). **This file is the
  one every downstream builder below (including E1) inherits the leakage from**, either by importing
  `data/elements/*.txt` directly or by calling this function.
- **23-subtype taxonomy?** No — only the 4 top-level elements.
- **Output format**: JSONL, one object per verse, 9 fixed keys (`no` + 4 elements × `_exists`/
  `_appearance`), Arabic-prefixed keys, no reasoning field.
- **Scope**: all 4 elements, whole poem, no subtype targeting.

### 1.2 `experiments/pilot_3models/prompt_variants.py` — `build_system_message_variant("v4_combined")`

- **Last commit**: `3228554`, 2026-07-21 (Phase 1, frozen).
- **Models used**: same 3 models, frozen TEST numbers (§3a of `PROJECT_STATE.md`) — **this is Phase 1's
  selected/winning prompt for the frozen thesis numbers**.
- **Terminology**: OLD (inherits §1.1's header/elements verbatim) + its own rule blocks explicitly name
  "Kenning" in the Trope/Kenning boundary rule (RULE_1_BOUNDARY).
- **Element definitions**: same as §1.1 (same leakage), plus 3 added rule blocks (boundary,
  marker-independence, multi-figure) — prose rules, not new worked examples.
- **23-subtype taxonomy?** No.
- **Output format**: identical schema to §1.1 (imports `SYSTEM_HEADER` from `prompts.py`; analysis
  instructions/schema untouched).
- **Scope**: all 4 elements, whole poem.

### 1.3 `experiments/pilot_3models/decompose_prompts.py` / `per_verse_prompts.py` / `explanation_prompt.py`

- **Last commit**: `3228554`, 2026-07-21 (Phase 1, frozen, supplementary/negative-result experiments
  per `PROJECT_STATE.md` §3f/§3g/§3i).
- Same terminology, same element-file leakage as §1.1/§1.2 — these only change granularity
  (single-element vs. whole-poem vs. per-verse) or add a `reason` field, not terminology or examples.
  Not pursued further here since none of them is a terminology/example-sensitivity candidate and none
  is newer than §1.1/§1.2.

### 1.4 `experiments/phase2_chatlike/prompt_config_b.py` — `build_config_b_system_message()` (Config B)

- **Last commit**: `b1dd17a`, 2026-10-10 (despite `PROJECT_STATE.md` dating this work "2026-07-23" —
  see §3 below, the docs' dates and the actual commit dates disagree).
- **Models used**: Claude Sonnet 4.6 only.
- **Terminology**: **NEW/corrected** — post-processes `prompt_variants.build_system_message_variant
  ("v4_combined")`'s output with string replacement: `Antonymy→Antithesis`, `Kenning`/`kenning`→
  `Periphrasis`/`periphrasis`, and inserts a مجاز-subtype note (استعارة/تمثيل/مجاز مرسل + the two
  GLOSSARY.md canonical examples) right after the Trope block.
- **Element definitions**: same underlying `data/elements/*.txt` text as §1.1/§1.2 (same TEST-poem
  example leakage — the leakage is in the source `.txt` files, which this builder does not edit, per
  GLOSSARY.md's explicit instruction not to edit them in place) + the new مجاز-subtype note's own 2
  examples (السماء تمطر / أراني أعصر خمراً — these are NOT poem verses, they are GLOSSARY.md's abstract
  canonical examples, so they don't carry the TEST-leakage problem).
- **23-subtype taxonomy?** No — only the 3 مجاز subtypes are named, not the full 23/25-entry taxonomy.
- **Output format**: unchanged from §1.1 — same 9-key JSONL schema.
- **Scope**: all 4 elements (terminology-corrected), whole poem.

### 1.5 `experiments/phase2_chatlike/prompt_config_c.py` — Config C (two-stage)

- **Last commit**: `b1dd17a`, 2026-10-10.
- **Models used**: Stage 1 = Fable 5 (free-form Arabic reasoning); Stage 2 = GPT-5.4-mini (extraction
  into the strict schema).
- **Terminology**: Stage 1's user prompt is **new/Arabic-native** — lists المجاز بأنواعه (الاستعارة/
  التمثيل/المجاز المرسل), التشبيه, الكناية, الطباق, with the same السماء تمطر / أراني أعصر خمراً
  examples. No English "Antonymy"/"Kenning" terms appear anywhere in Config C (it's Arabic-only and
  free-form, not instruction-only-JSON).
- **Element definitions included?** Only the one-paragraph Arabic prompt above — no `data/elements/
  *.txt` concatenation, no TEST-poem example leakage at all in Stage 1. Stage 2 has no element
  definitions, only the extraction schema.
- **23-subtype taxonomy?** No — only the مجاز 3-subtype split, same as Config B.
- **Output format**: Stage 1 = free-form Arabic prose (no schema). Stage 2 = same 9-key JSONL schema as
  §1.1, extracted faithfully from Stage 1's prose.
- **Scope**: all 4 elements, per-verse (whole poem given as context, one verse analyzed per call).

### 1.6 `experiments/phase3_subelements/subtype_prompts.py` / `fewshot_prompts.py`

- **Last commit**: `9a9365f`, 2026-10-10.
- **Models used**: Gemini 3.5 Flash (`phase3_config.MODEL_KEY = "google"`, chosen per that file's
  comment: best/near-best Phase 1 F1 on 3/4 elements, half Claude's price, highest consistency; Fable 5
  excluded for cost). `phase3_crossmodel` (§1.7 below) later adds Claude Sonnet 4.6 + GPT-5.4-mini on
  top of this same prompt shape.
- **Terminology**: **NEW/corrected** — `subtype_defs.py`'s `SUBTYPE_DEFS` keys and parent labels use
  "طباق (Antithesis)" and "كناية (Periphrasis)" throughout.
- **Element definitions included?** Only **one** sub-element's own Arabic definition + exactly 1 worked
  example per call (`SYSTEM_TEMPLATE`) — not the full 4-element block, not the other sibling subtypes.
  The one example per subtype in `subtype_defs.py` is drawn from Haifa University course slides / Dr.
  Hussein's 2025 JAL glossary paper (named in that file's docstring), **not** from this project's
  annotated poem corpus — no TEST/DEV leakage here.
- **23-subtype taxonomy?** **Yes** — this is the taxonomy's home. `subtype_defs.py` defines 25 entries
  (طباق: 4, تشبيه: 5, مجاز: 9, كناية: 7) covering the subtypes confirmed with the user (5 subtypes with
  no source-table definition were explicitly excluded per the docstring); `fewshot_prompts.py`
  (`build_messages_fewshot`) extends this to a 3-shot version (1 original + 2 more drawn from that
  subtype's own held-out ground truth, per `run_fewshot_check.py`).
- **Output format**: ONE JSON object (not JSONL) — `{"exists", "appearance", "reasoning"}` — a
  **different schema** from §1.1-§1.5 (adds a mandatory Arabic `reasoning` field, every call).
- **Scope**: **one subtype only** per call, not "all elements."

### 1.7 `experiments/phase3_crossmodel/crossmodel_config.py` + `run_crossmodel.py`

- **Last commit**: `9a9365f`, 2026-10-10.
- **Models used**: adds Claude Sonnet 4.6 (`anthropic`) + GPT-5.4-mini (`openai`) on top of §1.6's
  existing Gemini data (re-scored, not re-run); explicitly excludes Fable 5 again on cost grounds.
- Reuses §1.6's `subtype_prompts`/`subtype_defs` unchanged — no new prompt-building code, listed here
  only because it's a distinct run with its own config file.

### 1.8 `experiments/phase4_e1/fewshot_examples.py` — `build_system_message_e1()` (**E1, the subject of this audit**)

- **Last commit**: `c0f08e2`, 2026-10-10 (dry-run harness); `e1_config.py` `7906d02`, 2026-10-10;
  `runner.py` `8b4459c`, 2026-10-10 (the actual run).
- **Models used**: GPT-5.4-mini (complete, 150/150 calls, $1.28) + Gemini 3.5 Flash (partial, per
  `E1_RESULTS.md`).
- **Terminology**: **OLD** — `build_system_message_e1()` calls `pilot_3models.prompts.
  build_system_message()` (§1.1) **completely unmodified** and appends a few-shot block on top. Every
  instance of "Kenning"/"Antonymy" from §1.1 is sent verbatim in every E1 call. Confirmed verbatim in
  `docs/phase4/PROMPT_ANATOMY.md` §1 (full system message reproduced, `ELEMENT_3: English name: Kenning`,
  `ELEMENT_4: English name: Antonymy`).
- **Element definitions included?** Yes, unmodified §1.1 — **same TEST-poem-leaking examples as every
  Phase 1 prompt**, plus E1's own few-shot block (2 extra examples per set A/B/C, drawn from 3 Abu Nuwas
  poems that are NOT in the Phase 1/2/3 DEV or TEST sets — the few-shot examples themselves are clean of
  DEV/TEST leakage, but the base system message they're appended to is not).
- **23-subtype taxonomy?** No — only one named subtype (استعارة فعل) gets extra few-shot examples; the
  other 24 subtypes and the other 3 elements get no subtype-level treatment at all, same flat 4-element
  scope as §1.1.
- **Output format**: unchanged §1.1 schema — 9-key JSONL, no `reasoning` field (unlike §1.6's schema).
- **Scope**: all 4 elements (old names), whole poem, with few-shot emphasis on exactly one مجاز subtype.

---

## 2. Which is NEWEST, and which does the documentation call canonical — do they agree?

**By commit date, the newest *prompt-building* code is tied between four files committed the same day
(2026-10-10)**: `phase2_chatlike/prompt_config_c.py` (`b1dd17a`), `phase3_subelements/subtype_prompts.py`
+ `fewshot_prompts.py` (`9a9365f`), and `phase4_e1/fewshot_examples.py` (`c0f08e2`/newer). Ignoring E1
(which is explicitly the thing under audit, not a competing "canonical" candidate), **the newest
substantive prompt design is Phase 3's subtype-level prompt (§1.6, `subtype_prompts.py`/
`fewshot_prompts.py`)** — it is the only builder that (a) uses corrected terminology, (b) is scored
against the full 23/25-subtype ground truth, and (c) has its own few-shot variant already built and run
(`run_fewshot_check.py`, results in `results/phase3_subelements/`).

**What the docs say is canonical:**
- `CLAUDE.md` / `GLOSSARY.md` mandate corrected terminology for "all new writing" / "new Phase 2+ code"
  but do not name one single prompt file as *the* canonical builder — they state a terminology rule, not
  a prompt-selection rule.
- `NEW_SESSION_HANDOFF.md` frames Phase 2's Config A/B/C (§1.4/§1.5 here) as the most recent *closed*
  experimental finding, and lists the few-shot proposal (`PROPOSAL_fewshot.md`) as "designed but needs
  rework" — i.e. the handoff's own last word on "what's newest and usable" points at Phase 2, with a
  known caveat.
- `PROJECT_STATE.md` **does not mention Phase 3 or Phase 4 anywhere** — it stops at "Phase 2 §7,
  2026-07-26" (confirmed: `git log` shows Phase 3's commit `9a9365f` and all of Phase 4's commits are
  dated 2026-10-10, three months after `PROJECT_STATE.md`'s last recorded update, and nothing in
  `PROJECT_STATE.md`'s text references `phase3_subelements`, `phase3_crossmodel`, or `phase4_e1` by
  name or path).

**Do the docs and the code agree? No — and the disagreement is exactly the gap that let E1 happen.**
`PROJECT_STATE.md`'s own words ("single source of truth... if it conflicts with your memory of a past
conversation, trust this file") describe a file that is three months stale against the actual repo:
Phase 3's subtype taxonomy and corrected-terminology prompt (§1.6, the best candidate for "newest
canonical prompt") exists in the codebase but is **not documented anywhere in `PROJECT_STATE.md`,
`CLAUDE.md`, `GLOSSARY.md`, or `NEW_SESSION_HANDOFF.md`** — there was no written pointer for a future
session (including whoever built E1) to find it. E1's `fewshot_examples.py` docstring explicitly says
it builds on top of `pilot_3models.prompts.build_system_message()` "frozen" — a deliberate choice to
reuse Phase 1's prompt for E1's specific question (isolating few-shot example sensitivity on top of an
*unchanged* base, matching Phase 1's own frozen numbers for comparability) — but neither `e1_config.py`
nor `fewshot_examples.py` nor `docs/phase4/COST_PLAN.md`/`INFO_REPORT.md` (not yet re-read in full here)
states that this means E1 ships with old terminology and leaked examples as a known, accepted
trade-off, versus an oversight. That framing gap, not the code itself, is the documentation failure.

---

## 3. The newest prompt, verbatim — Phase 3's subtype-level prompt (§1.6)

Reproduced from `experiments/phase3_subelements/subtype_prompts.py`, with a placeholder poem substituted
for `{verse}` and a real subtype (`كناية عن صفة`) substituted into the template, exactly as
`build_messages()` would render it. Section boundaries marked with `[...]`.

```
[SECTION: SYSTEM MESSAGE — subtype_prompts.py SYSTEM_TEMPLATE, formatted for one subtype]
You are an Arabic rhetoric analysis engine. Follow instructions strictly.

================================
SUB-ELEMENT DEFINITION (REFERENCE)
================================
Below is EXACTLY ONE rhetorical sub-element (a specific branch of a broader
Arabic rhetorical element). Learn it deeply using ONLY the definition and
example given here. Do NOT use outside knowledge, and do NOT confuse it with
sibling sub-elements under the same parent element. You will apply this
definition to ONE verse given in the user's message.

--------------------------------
SUB-ELEMENT
--------------------------------
Parent element: كناية (Periphrasis)
Arabic name: كناية عن صفة
Definition (Arabic): كناية عن صفة: يُشار بها إلى صفة أو خُلُق معيّن دون ذكر الصفة مباشرة، بذكر أمر يلازمها عادة.
Example: «طَوِيلُ النِّجَادِ رَفِيعُ العِمَادِ كَثيرُ الرَّمادِ إذا ما شَتَا» — كثرة الرماد كناية عن الكرم (كثرة الطبخ للضيوف).
[END SYSTEM MESSAGE]

[SECTION: USER MESSAGE — subtype_prompts.py ANALYSIS_INSTRUCTIONS, formatted with a placeholder verse]
================================
ANALYSIS PHASE (OUTPUT REQUIRED)
================================
Analyze the verse(s) below for the existence of ONLY the sub-element defined
above (not the broader parent element, not any other sub-element). Usually
there is one verse; occasionally there are two or more consecutive verses
because this specific rhetorical instance spans across them - treat them as
one unit and answer for the whole passage.

Return ONE JSON object only. No text before or after.

Schema (MUST MATCH EXACTLY):
{
  "exists": <true|false>,
  "appearance": <string|null>,
  "reasoning": <string>
}

Rules:
- If exists is false -> appearance MUST be null
- If exists is true -> appearance MUST be a literal substring from the text below
- reasoning is ALWAYS required (both when true and false): 1-3 sentences, in
  Arabic, explaining WHY the sub-element's definition does or does not match
  this text - reference the specific word(s)/phrase you based the decision on
- Be conservative: if unsure -> exists=false
- Do NOT add fields beyond the schema
- Do NOT use markdown

--------------------------------
VERSE(S)
--------------------------------
هذا بيت توضيحي يُستخدم فقط لإظهار شكل الرسالة، وليس بيتاً حقيقياً من القصائد المُحَلَّلة.
[END USER MESSAGE]
```

**Output schema**: single JSON object (not JSONL — one call = one subtype × one verse-unit),
`{"exists": bool, "appearance": string|null, "reasoning": string}` — the `reasoning` field is mandatory
on every call, true or false, which is new relative to every Phase 1/E1 schema (§1.1-§1.5, §1.8) that
has no reasoning field at all.

The 3-shot variant (`fewshot_prompts.build_messages_fewshot`) uses the same user message but expands the
system message's `SUB-ELEMENT` block with "Example 2"/"Example 3" lines drawn from two more real,
held-out ground-truth instances of that subtype (verse text + span + Dr. Hussein's own analysis note).

---

## 4. How to inject 2 few-shot examples (one set of A/B/C) into this prompt for E1, and what must change

**Recommended scope for E1 if redesigned on top of §1.6 instead of §1.1**: keep the subtype focus
narrow and already-validated — **استعارة فعل** (the subtype E1 already targets) under its parent
**مجاز (Trope)**, using `subtype_defs.SUBTYPE_DEFS["استعارة فعل"]`'s existing definition/example. This
is a direct swap of E1's prompt engine, not a new design: Phase 3 already has a working few-shot
mechanism (`fewshot_prompts.build_messages_fewshot`) built for exactly this subtype-isolation shape, and
E1's own `fewshot_examples.py` already draws clean, non-leaking example verses from 3 Abu Nuwas poems —
the only thing that needs to change is *which base prompt* those examples get appended to.

**Concretely, injecting E1's 2-example sets (A/B/C) into §1.6's schema instead of §1.1's:**
1. Use `subtype_prompts.SYSTEM_TEMPLATE` (or a near-identical adaptation) as the base system message
   instead of `pilot_3models.prompts.build_system_message()` — this removes the old-terminology
   4-element block and the TEST-poem-leaking examples in one move, and narrows the task to the one
   subtype E1 is actually studying.
2. Add the few-shot block as "Example 2" / "Example 3" lines inside that same `SUB-ELEMENT` block
   (exactly `fewshot_prompts.py`'s existing `SYSTEM_TEMPLATE_FEWSHOT` shape), using E1's own set
   A/B/C verses (`e1_config.EXAMPLE_POEM_IDS`) as the 2 extra examples — each set contributing its own
   Example 2 + Example 3, so sets A/B/C stay a true single-variable manipulation on top of an *otherwise
   identical, already-clean* base (no TEST/DEV leakage anywhere in the base this time, since §1.6 never
   touches `data/elements/*.txt`).
3. Switch the user message and output schema from JSONL/9-key (§1.1's whole-poem-all-4-elements shape)
   to §1.6's one-subtype-per-verse shape (`ANALYSIS_INSTRUCTIONS` from `subtype_prompts.py`, with its
   mandatory `reasoning` field) — this also changes what "a call" means, from one call per poem to one
   call per (verse, subtype) pair, matching Phase 3's granularity, not Phase 1's.

**What must change in `experiments/phase4_e1/` (without changing anything yet):**
- **`e1_config.py`**: `ELEMENT`/`ELEMENT_AR` stay (`Trope`/`مجاز`), but the config needs to import
  `phase3_subelements.subtype_defs.SUBTYPE_DEFS` and `phase3_config` conventions instead of only
  `pilot_3models.config`/`prompts`; `SUBTYPE_FOCUS = "استعارة فعل"` already matches §1.6's taxonomy key
  exactly, so no renaming needed there.
- **`fewshot_examples.py`**: `build_system_message_e1()` must call a §1.6-style single-subtype system
  template instead of `pilot_3models.prompts.build_system_message()`; `build_fewshot_block()`'s format
  (bare numbered verse + span + note) needs to become "Example 2"/"Example 3" lines matching
  `fewshot_prompts.SYSTEM_TEMPLATE_FEWSHOT`'s exact slots, not an appended trailing block.
- **`runner.py`**: `build_user_message()` currently builds one whole-poem JSONL call
  (`ANALYSIS_INSTRUCTIONS` from `pilot_3models.prompts`); it would need to become a per-verse loop over
  each eval poem's verses (like `per_verse_prompts.get_verses()`/§1.5's per-verse mechanism), calling
  §1.6's `ANALYSIS_INSTRUCTIONS` once per verse instead of once per poem — a real shape change, not a
  config tweak, and it changes the call count (and therefore the cost estimate) substantially.
- **`scoring.py`**: currently expects to parse E1's output with the Phase 1 9-key JSONL parser
  (`pilot_3models.parsing.parse_response`, per the old schema). It would need the single-object
  `{"exists","appearance","reasoning"}` parser Phase 3 uses (`phase3_subelements/score_subtypes.py`'s
  conventions) instead, and ground-truth comparison would need to key off the single
  `استعارة فعل`-subtype ground-truth file (`data/ground_truth/by_subtype/`) rather than the 4-element
  mapped ground truth `pilot_3models.ground_truth` currently provides.
- **Cost estimate**: must be fully redone once the call shape moves from whole-poem to per-verse (more,
  smaller calls) — the existing `$1.28` GPT figure (whole-poem, all 4 elements, 150 calls) does not
  carry over; nothing above should be treated as cost-estimated until a new `dryrun.py`-equivalent is
  built and re-confirmed with the user, per CLAUDE.md rule 5.

---

## 5. Are the existing GPT E1 results ($1.28) usable at all?

**Usable only if explicitly re-labeled as "run on Phase 1's old prompt/terminology," not as a clean
read of the new-terminology/new-taxonomy design the user actually wants.** The $1.28 GPT-5.4-mini run
(150/150 calls, 0 errors, per `E1_RESULTS.md`) is real data from a real, well-executed pilot — nothing
about the run itself is broken, and it answers a genuine question (does adding 2 few-shot استعارة فعل
examples to Phase 1's *unmodified* system message move recall/precision on a fresh poet). But it answers
that question for the OLD prompt (English "Kenning"/"Antonymy," TEST-poem-leaking base examples, no
23-subtype taxonomy, no reasoning field) — not for the terminology-corrected, subtype-native prompt
design in §1.6/§3/§4 above, which is what the user expects "the newest prompt" to mean. If these numbers
are cited anywhere going forward, they need the same kind of explicit historical-framing caveat
`GLOSSARY.md` already prescribes for Phase 1 citations (e.g. "E1's GPT result was obtained on Phase 1's
frozen base prompt — Antonymy/Kenning naming, TEST-poem example leakage intact — not on the Phase 2/3
terminology-corrected, subtype-level prompt"). They should not be discarded, but they also should not be
presented as evidence about the corrected-prompt design, and the pending/partial Gemini run should not
be completed on the current prompt without the same caveat being decided first.

---

## 6. Facts vs. recommendations — summary

**Facts** (§1-§3, §5): seven prompt-building code paths exist; E1 (§1.8) reused §1.1 unmodified, old
terminology and TEST-leaking examples confirmed byte-for-byte via `PROMPT_ANATOMY.md`; the newest,
most-fitting candidate for "canonical" is Phase 3's subtype-level prompt (§1.6), terminology-corrected,
23/25-subtype taxonomy, no TEST/DEV leakage in its own example source, but it is **not mentioned
anywhere in `PROJECT_STATE.md`, `CLAUDE.md`, `GLOSSARY.md`, or `NEW_SESSION_HANDOFF.md`** — those docs
are three months stale relative to the actual repo (confirmed via commit dates) and do not single out
one canonical prompt by name.

**Recommendations** (§4): redesign E1 on top of §1.6's subtype-level prompt/schema rather than §1.1's
whole-poem/4-element one; keep the استعارة فعل subtype focus; treat the config/runner/scoring changes
as a real shape change (per-verse calls, different output schema, different ground-truth join), not a
drop-in swap; re-estimate and re-confirm cost before any new API call.
