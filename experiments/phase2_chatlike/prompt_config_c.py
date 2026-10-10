"""Config C - full chat-like recipe. Two-stage, per-verse (Mode A
granularity, reusing per_verse_prompts.get_verses unchanged), on Fable 5.

Stage 1: free-form Arabic rhetorical analysis, one verse per call, full poem
given as context, extended thinking (automatic on Fable 5 - no config
needed). Uses the user-specified Arabic prompt VERBATIM - do not edit the
prompt text itself; only the poem text and {verse} are substituted in.

Stage 2: extraction call on a cheap model (GPT-5.4-mini) that converts
stage 1's free-form Arabic analysis into the existing strict JSONL schema
(same Arabic-prefixed keys as prompts.py's ANALYSIS_INSTRUCTIONS /
per_verse_prompts.py's Mode A - unchanged) so the unmodified Phase 1 harness
(parsing.py, span_scoring.py) scores it without modification. The extractor
is instructed to be faithful: only what stage 1 actually claimed, nothing
added.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pilot_3models"))
from config import POEMS  # noqa: E402
from per_verse_prompts import get_verses  # noqa: E402  (reused unchanged)

# Verbatim - do not edit. {verse} is the only substitution point.
STAGE1_PROMPT_TEMPLATE = """أنت عالِم بلاغة متخصص في الشعر العربي القديم. أمامك قصيدة كاملة للسياق، \
والمطلوب تحليل البيت المحدد أدناه تحليلاً بلاغياً دقيقاً.

حلّل البيت التالي وبيّن ما فيه من الفنون البلاغية الأربعة الآتية، إن وُجدت، \
مع الاستشهاد بالألفاظ الدقيقة من البيت:

١. المجاز بأنواعه: الاستعارة، والتمثيل، والمجاز المرسل (كإسناد الشيء إلى \
جزئه أو سببه، نحو «السماء تمطر» والممطر هو السحاب، أو «أراني أعصر \
خمراً» والمعصور هو العنب).
٢. التشبيه: عقد المقارنة الصريحة بأداة ظاهرة أو مقدّرة.
٣. الكناية: التعبير الذي يُراد به لازم معناه مع جواز إرادة المعنى الأصلي.
٤. الطباق: الجمع بين المتضادين في سياق واحد.

اذكر لكل فنٍّ وجدته: موضعه بالألفاظ الدقيقة من البيت، ونوعه، ووجه الدلالة \
باختصار. وإن لم تجد فنّاً منها في البيت فقل ذلك صراحةً ولا تتكلّف. لا \
تفترض وجود فنٍّ لمجرد أن السؤال ذكره - التزم ما في البيت فعلاً.

البيت المطلوب تحليله:
{verse}"""

STAGE1_SYSTEM_MESSAGE = ""  # persona + task are entirely inside the verbatim user prompt

STAGE2_SYSTEM_MESSAGE = """أنت أداة استخراج بيانات دقيقة. مهمتك تحويل تحليل بلاغي حر (نص عربي) إلى
كائن JSON واحد يطابق المخطط التالي تماماً - لا تُضِف أي استنتاج أو فنّ لم
يرد ذكره صراحة في التحليل، ولا تحذف فنّاً ذكره التحليل.

Schema (MUST MATCH EXACTLY):
{
  "no": <integer>,
  "مجاز_exists": <true|false>,
  "مجاز_appearance": <string|null>,
  "تشبيه_exists": <true|false>,
  "تشبيه_appearance": <string|null>,
  "كناية_exists": <true|false>,
  "كناية_appearance": <string|null>,
  "طباق_exists": <true|false>,
  "طباق_appearance": <string|null>
}

Rules:
- استخرج فقط ما ورد فعلاً في التحليل أدناه - لا إضافات، لا حذف.
- إذا ذكر التحليل أن الفن غير موجود، أو لم يذكره إطلاقاً -> *_exists=false, *_appearance=null
- إذا ذكر التحليل أن الفن موجود -> *_appearance يجب أن يكون سلسلة نصية حرفية من البيت (كما اقتبسها التحليل)
- طابق أنواع المجاز الثلاثة (الاستعارة، التمثيل، المجاز المرسل) جميعها إلى مفتاح مجاز_exists الواحد
- لا تشرح، أعد كائن JSON واحد فقط بلا نص قبله أو بعده، بلا Markdown
"""


def build_stage1_user_message(poem_key: str, verse_line: str) -> str:
    poem_text = POEMS[poem_key]["poetry_path"].read_text(encoding="utf-8").strip()
    return poem_text + "\n\n" + STAGE1_PROMPT_TEMPLATE.format(verse=verse_line)


def build_stage2_user_message(verse_no: int, verse_line: str, stage1_analysis: str) -> str:
    return (
        f"رقم البيت: {verse_no}\n"
        f"نص البيت: {verse_line}\n\n"
        f"التحليل البلاغي الحر المطلوب تحويله:\n{stage1_analysis}\n"
    )


if __name__ == "__main__":
    verses = get_verses("Imru2")
    msg = build_stage1_user_message("Imru2", verses[4])
    Path("_config_c_stage1_preview.txt").write_text(msg, encoding="utf-8")
    print(f"OK - {len(verses)} verses, stage1 user message for verse 5: {len(msg)} chars")
