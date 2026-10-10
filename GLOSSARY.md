# Glossary — Rhetorical Element Terminology

**Purpose**: canonical Arabic↔English terminology for the four rhetorical elements this project studies. Corrected 2026-07-23 after supervisor feedback (see `PROJECT_STATE.md` → Phase 2 §0 for the full rationale).

**Scope of the correction — read this before citing any number in this repo**: the correction applies to **all new writing** from 2026-07-23 onward (Phase 2 experiments, new thesis sections, new reports). It does **not** retroactively change Phase 1. Every Phase 1 document — `PROJECT_STATE.md` §1-§7, `final_report.docx`, `detailed_results.docx`, `explanations_sample.docx`, and the already-drafted `/writing/chapters/*.md` — used the old (incorrect) English names throughout, and those documents are left as-is: they are an accurate record of what was actually run and reported at the time. When citing Phase 1 numbers in new writing, use the corrected English term but make clear the underlying Phase 1 artifact used the old one (e.g. "Phase 1's frozen antithesis (reported there as 'antonymy') results...").

---

## Corrected terms

| Arabic | Phase 1 English (wrong) | Correct English | Notes |
|---|---|---|---|
| طباق | antonymy | **antithesis** | Antonymy is a lexical relation between two words (opposite meanings). Antithesis is the rhetorical figure: juxtaposing two opposites within one context for contrastive effect. طباق is the rhetorical figure, not the lexical relation — "antonymy" named the wrong category of thing, not just the wrong word for the right category. |
| كناية | kenning | **periphrasis** | A kenning is a specific Old Norse/Old English compounding device (e.g. "whale-road" for "sea") — a real device, but from an unrelated poetic tradition with a different structure (compound noun substitution). كناية is indirect expression: saying something whose *literal* meaning is not the intended point, while the literal reading remains a plausible one (see `data/elements/Kenning.txt` for the full Arabic/English definition, unchanged). Periphrasis (indirect/roundabout expression conveying a meaning without stating it directly) is the correct rhetorical-terminology match. "Kenning" doesn't just under-describe كناية, it points at the wrong structural pattern entirely — this is flagged in Phase 2 §0 as *potentially actively misleading*, not merely imprecise. |

## مجاز — confirmed as an umbrella term with subtypes

مجاز ("trope", English name unchanged) was treated in Phase 1 as one undifferentiated figure. It is actually an umbrella covering (at least) three subtypes:

| Arabic subtype | English | Description |
|---|---|---|
| استعارة | metaphor | A word used in place of another based on a resemblance between the two meanings (the core, most common Trope subtype). |
| تمثيل | analogy / extended metaphor | A whole-clause or whole-scene figurative comparison, not reducible to a single substituted word. |
| مجاز مرسل | metonymy / synecdoche | The word used stands for something connected to it by a relation *other than* resemblance (cause-for-effect, part-for-whole, container-for-contents, etc.) — not analogical like استعارة. |

**Canonical مجاز مرسل examples** (used verbatim in the Phase 2 §3i Config C prompt):

1. «السماء تُمطر» ("the sky is raining") — the verb "rains" is attributed to the sky, but what actually produces the rain is the cloud (a part of the sky, or its cause). This is a cause/part-for-whole relation, not a resemblance — hence مجاز مرسل, not استعارة.
2. «أراني أعصر خمراً» ("I see myself pressing wine") — from Qur'an 12:36 (Yusuf); what is literally pressed is grapes, and the result of pressing is wine — the word "wine" (خمر) is used for what will become wine (the raw material named by its eventual product, a would-be/future-state relation). This is again a non-resemblance relation, hence مجاز مرسل.

Phase 1's `data/elements/Trope.txt` gives one unified مجاز definition and a set of examples but never explicitly names or exemplifies the مجاز مرسل subtype specifically — see `PROJECT_STATE.md` §3c, where مجاز مرسل is the one Trope subtype v4_combined's added rules do nothing for (85%→85% missed, completely flat, unchanged by any Phase 1 intervention). Whether naming and exemplifying this subtype explicitly (as Phase 2 §3i Config C's prompt does) changes that is one of the open questions §3i is designed to answer — not yet confirmed either way.

## Unchanged terms

| Arabic | English | Notes |
|---|---|---|
| تشبيه | simile | No terminology issue identified; carried over unchanged into Phase 2. |
| مجاز | trope | Name unchanged; internal subtype structure clarified above. |

## Where this feeds into code

- `data/elements/{Trope,Simile,Kenning,Antonymy}.txt` — Phase 1's canonical element definitions. **Left unchanged** (Phase 1 frozen artifacts; file names also unchanged to avoid breaking every Phase 1 script that references them by path).
- `experiments/phase2_chatlike/` — any Phase 2 prompt variant that uses the corrected terminology lives here, built from the Phase 1 `.txt` files plus the corrections in this glossary, not by editing the `.txt` files in place.
