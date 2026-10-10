# CLAUDE.md — Project Instructions

This file loads into every future session working in this repo. If anything here conflicts with your read of the code, trust the code and `PROJECT_STATE.md` — this file is a pointer/summary, not the source of truth.

**Start here**: [`PROJECT_STATE.md`](PROJECT_STATE.md) is the single source of truth for what's been done, what's frozen, and what's open. Read it before touching any experiment code or result. If it conflicts with your memory of a past conversation, trust the file.

---

## Standing experiment discipline

This applies to every experimental cycle in this repo (Phase 1 pilot, Phase 2, and anything after):

1. **DEV vs TEST is a hard boundary.** `DEV_POEMS`/`TEST_POEMS` in `experiments/pilot_3models/config.py` define it. All prompt/method iteration happens on DEV only. TEST is evaluated once, at the end, and is then **spent** — never re-run, never re-scored with a new variant, never "just check one more thing." If TEST is already spent for a cycle (see `PROJECT_STATE.md` §2), it stays spent regardless of what a later phase finds.
2. **2 runs per configuration minimum, 2-run majority as the primary metric.** A single run's F1 can be noise (a real incident already happened once — see `PROJECT_STATE.md` §6.1, an 8x apparent Kenning/Periphrasis gain that halved on a second run). Never draw a comparative conclusion from one run.
3. **Always report raw TP/FP/FN alongside precision/recall/F1.** Small denominators read very differently once the counts are visible.
4. **Span-level scoring, both strict and token-overlap criteria** (`experiments/pilot_3models/span_scoring.py`) — never plain verse-level exists/not-exists (it produces artifacts, especially for the element currently called Periphrasis/كناية).
5. **Cost estimate + explicit user confirmation BEFORE any API call that spends money**, every time, no exceptions — including a "just checking one more thing" follow-up. If a new model's pricing or request shape is unfamiliar, verify it (e.g. via the current model/pricing reference) before estimating, rather than assuming.
6. **New prompt ideas get evaluated on DEV as a supplementary experiment.** They do not retroactively touch a phase's already-frozen numbers.

## Terminology

See [`GLOSSARY.md`](GLOSSARY.md) for the canonical Arabic↔English mapping for the four rhetorical elements, corrected 2026-07-23:

- طباق = **antithesis** (not "antonymy" — a lexical relation, the wrong category of thing)
- كناية = **periphrasis** (not "kenning" — an unrelated Old Norse/Old English device)
- مجاز is an umbrella term with subtypes: استعارة (metaphor), تمثيل (analogy), مجاز مرسل (metonymy/synecdoche)

**The correction applies to all new writing only.** Phase 1's frozen documents (`PROJECT_STATE.md` §1-§7, `final_report.docx`, `detailed_results.docx`, `explanations_sample.docx`, the already-drafted `/writing/chapters/*.md`) keep the original terms as an accurate historical record — do not retroactively edit them. New reports, new Phase 2+ code, and new thesis sections use the corrected terms.

## RTL / bidi rules for any .docx output

Every `.docx` builder in this project must use the shared helpers in [`experiments/pilot_3models/rtl_utils.py`](experiments/pilot_3models/rtl_utils.py) — don't hand-roll bidi handling in a new script. Summary of the rules (full detail in that file's docstring):

- Arabic text is stored in logical order always — never reversed, never patched with manual bidi control characters.
- Direction is a **paragraph property** (`<w:bidi/>` in `pPr`) plus a **run property** (`<w:rtl/>` in `rPr`) — never a table-level `bidiVisual` flag unless explicitly requested.
- Each paragraph's direction is decided independently via `is_majority_arabic()` (>50% of non-whitespace characters in the Arabic Unicode blocks) — a Latin-majority paragraph stays LTR even if it embeds an isolated Arabic word.
- Use `apply_paragraph_direction(paragraph)` to do all of the above for a paragraph and its runs in one call.

**Mandatory visual render verification**: before shipping any `.docx` deliverable, actually open/render it and visually confirm Arabic paragraphs read right-to-left and Latin/numeric content stays left-to-right — don't rely on the OOXML looking correct in source alone. A prior session already found and fixed real RTL bugs this way (see commit `d8079eb`).

## Repo layout pointers

- `experiments/pilot_3models/` — Phase 1 harness (frozen; reproduces exact frozen numbers, see `REPRODUCIBILITY.md`).
- `experiments/phase2_chatlike/` — Phase 2 code. Imports Phase 1 modules (`config`, `prompts`, `providers`, `parsing`, `span_scoring`, etc.) rather than duplicating them; only adds what Phase 2 needs on top (Fable 5 provider wrapper, terminology-corrected prompts, the two-stage Config C pipeline).
- `results/pilot_3models/` — Phase 1 frozen results.
- `results/phase2_chatlike/` — Phase 2 results.
- `data/elements/*.txt` — canonical element definitions. Not edited for terminology corrections — see `GLOSSARY.md` for why (Phase 1 reproducibility depends on these files staying byte-identical).
- `.env` (gitignored) — `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`. Never commit it, never hardcode a key in source.
