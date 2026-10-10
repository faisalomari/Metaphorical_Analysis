"""Config B - pure terminology effect.

v4_combined, UNCHANGED except: the English element names are corrected
(antonymy -> antithesis, kenning -> periphrasis, everywhere those words
appear - including inside the v4 rule blocks, which reference "Kenning" by
name in the Trope/Kenning boundary rule) and the Trope block gets an
additional annotated subtype note (استعارة / تمثيل / مجاز مرسل, with the
two canonical examples from GLOSSARY.md). Everything else - baseline
system header, analysis instructions, JSONL schema (Arabic-prefixed keys,
unchanged), v4's RULE_1/2/3 content and structure - is byte-identical to
Phase 1's v4_combined. Runs on Sonnet 4.6 (Phase 1's providers.call_anthropic,
unchanged).

Phase 1's data/elements/*.txt files are NOT edited - the corrected system
message is built by post-processing the assembled Phase 1 v4_combined text,
exactly as GLOSSARY.md prescribes ("built from the Phase 1 .txt files plus
the corrections ... not by editing the .txt files in place").
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pilot_3models"))
from prompt_variants import build_system_message_variant  # noqa: E402

TROPE_SUBTYPE_NOTE = """
--------------------------------
ADDITIONAL NOTE: مجاز subtypes (terminology correction, Phase 2)
--------------------------------
مجاز is an umbrella term covering (at least) three subtypes - treat all
three as valid evidence for مجاز_exists:
  استعارة (metaphor): a word used in place of another based on a
  resemblance between the two meanings.
  تمثيل (analogy / extended metaphor): a whole-clause or whole-scene
  figurative comparison, not reducible to a single substituted word.
  مجاز مرسل (metonymy/synecdoche): the word used stands for something
  connected to it by a relation OTHER than resemblance (cause-for-effect,
  part-for-whole, container-for-contents, etc.). Two canonical examples:
    1) «السماء تمطر» ("the sky is raining") - the verb is attributed to
       the sky, but what actually produces the rain is the cloud (a
       part/cause relation, not resemblance).
    2) «أراني أعصر خمراً» ("I see myself pressing wine") - what is
       literally pressed is grapes; "wine" names the eventual product,
       not what is physically pressed (a would-be/future-state relation,
       not resemblance).
  Do not restrict مجاز detection to استعارة alone - a مجاز مرسل instance
  with no resemblance relation still counts as مجاز_exists=true.
"""


def build_config_b_system_message() -> str:
    msg = build_system_message_variant("v4_combined")
    # Terminology correction - applied to the assembled text, not the source
    # .txt files. Both capitalized (element name / header use) and
    # lowercase (mid-sentence, e.g. "A kenning (metonymic ...)") forms
    # appear in Kenning.txt's English explanation - replace both.
    msg = (
        msg.replace("Antonymy", "Antithesis")
        .replace("Kenning", "Periphrasis")
        .replace("kenning", "periphrasis")
    )
    # Insert the مجاز subtype note right after the Trope block. Trope is
    # always ELEMENT_ORDER[0] in Phase 1's assembly (config.ELEMENT_ORDER =
    # ["Trope", "Simile", "Kenning", "Antonymy"]), so its text runs from
    # after the ELEMENTS_BLOCK header to the first blank-line-separated
    # "ELEMENT_2:" marker (Simile.txt's header line).
    marker = "\n\nELEMENT_2:"
    idx = msg.index(marker)
    msg = msg[:idx] + "\n" + TROPE_SUBTYPE_NOTE.strip() + msg[idx:]
    return msg


if __name__ == "__main__":
    out = build_config_b_system_message()
    assert "Antonymy" not in out and "Kenning" not in out and "kenning" not in out, "terminology correction incomplete"
    assert "مجاز مرسل" in out  # مجاز مرسل
    assert "Antithesis" in out and "Periphrasis" in out
    Path("_config_b_preview.txt").write_text(out, encoding="utf-8")
    print(f"OK - Config B system message: {len(out)} chars, preview written to _config_b_preview.txt")
