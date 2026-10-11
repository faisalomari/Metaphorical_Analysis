# Phase 4 E1 — Prompt Anatomy

Facts only, no code changes. Shows exactly what is sent to the API in the E1 runs (sets A/B/C,
Gemini 3.5 Flash + GPT-5.4-mini), using the real system/user messages the resumable runner built and the
real raw outputs already saved under `results/phase4_e1/raw/`.

---

## 1. Full system message for Set B, verbatim

Source: `experiments/phase4_e1/config/prompt_preview_B.txt` (76 lines), produced by
`fewshot_examples.build_system_message_e1()`, which is `pilot_3models.prompts.build_system_message()`
(unmodified) with a few-shot block appended. Reproduced verbatim below with section boundaries marked.

```
[SECTION: SYSTEM_HEADER — pilot_3models/prompts.py, lines 1-16, frozen/unmodified]
You are an Arabic rhetoric analysis engine. Follow instructions strictly.

================================
ELEMENT DEFINITIONS (REFERENCE)
================================
Below are EXACTLY 4 rhetorical elements. Learn them deeply using ONLY the
definitions and examples provided here. Do NOT use outside knowledge. Build
your internal detection rules from these examples. You will apply these
definitions to the poem given in the user's message.

--------------------------------
ELEMENTS_BLOCK
--------------------------------

[SECTION: ELEMENTS_BLOCK — concatenation of data/elements/{Trope,Simile,Kenning,Antonymy}.txt,
 in experiments/pilot_3models/config.py's ELEMENT_ORDER; frozen since Phase 1, byte-identical]

ELEMENT_1:
Arabic name: مجاز
English name: Trope
Arabic explanation: المجاز هو استخدام اللفظ في غير معناه الأصلي لعلاقة بين المعنيين مع وجود قرينة تمنع إرادة المعنى الحقيقي، فيمنح الكلام قوة إيحائية واتساعًا في الدلالة. وهو أسلوب يُعيد تشكيل المعنى بطريقة غير مباشرة لخلق صورة أعمق وأكثر تأثيرًا.
English explanation: A trope (figurative expression) uses a word in a non-literal sense based on an associative relationship, accompanied by a contextual clue that prevents the literal meaning. It enriches the language by expanding meaning and creating more expressive, nuanced imagery.
Examples:
1) وَمَا ذَرَفَتْ عَيْنَاكِ إلَّا لتَضْرِبي	بِسَهْمَيْكِ في أعشَارِ قَلْبٍ مُقَتَّلِ
2) فَجُزِيتِ خَيْرَ جَزَاءِ نَاقَةِ وَاحِدٍ	وَرَجَعْتِ سَالِمَةَ القَرَا بِسَلامِ
3) فعَدّ عَمّا ترى ، إذ لا ارتجاع له،	وانمِ القُتُودَ على عَيْرانة ٍ أُجُدِ
4)  لَحِقْتُ وأَصحابي على كل حُرَّةٍ	مَرُوح تُبارِي الأَحْبَشِيَّ المُكارِيَا

ELEMENT_2:
Arabic name: تشبيه
English name: Simile
Arabic explanation: التشبيه هو عقد مقارنة صريحة بين شيئين يشتركان في صفة ما، باستخدام أداة تُظهر هذا الربط مثل كأنّ أو مثل. يهدف إلى توضيح المعنى وتقريبه للقارئ من خلال إبراز وجه الشبه بين الطرفين
English explanation: A simile is an explicit comparison between two things that share a similar quality, using a comparative marker such as "like" or "as." It serves to clarify an idea and make it more vivid by highlighting the similarity between the compared elements.
Examples:
1) إذا ما الثُّرَيَّا في السَّمَاءِ تَعَرَّضَتْ تَعَرَّضَ أثْنَاءِ الوِشَاحِ المُفَصَّلِ
2) أَزْمَانَ فُوهَا كُلَّمَا نَبَّهْتُهَا	كَالمِسْكِ بَاتَ وَظَلَّ فِي الفَدّامِ
3) وكان ضُمْران منه حيث يوزعهُ،	طعن المُعارك عند المُحجر النّجُدِ
4) دُنُوَّ عتاق الطير للزجر بعدما	شَمَسْنَ وولَّيْنَ الخدود العواصيا
5) عُنِيَ الرَبيعُ بِرَوضِهِ فَكَأَنَّما	أَهدى إِلَيهِ الوَشيَ مِن صَنعاءِ

ELEMENT_3:
Arabic name: كناية
English name: Kenning
Arabic explanation: الكناية هي تعبير يُراد به معنى غير ظاهر من اللفظ، دون ذكره مباشرة، مع إمكان إرادة المعنى الحقيقي أيضًا، مما يمنح الكلام عمقًا وإيحاءً. تعتمد على الإشارة غير المباشرة لصفة أو معنى، فيفهم السامع المقصود من خلال الدلالة والسياق
English explanation: A kenning (metonymic or euphemistic expression) conveys an indirect meaning by using words whose literal sense is not the intended purpose, while still allowing the literal meaning to remain possible. It relies on hinting at a quality or idea rather than stating it directly, giving the language subtlety and layered meaning.
Examples:
1) وبَيْضَةِ خِدْرٍ لا يُرَامُ خَبَاؤُهَا	تَمَتَّعْتُ منْ لَهْوٍ بها غَيْرَ مُعْجَلِ
2) وَأنَا المُنَبِّهُ بَعْدَمَا قَدْ نَوَّمُوا	وَأنَا المُعَالِنُ صَفْحَة َ النُّوّامِ
3) مقذوفة ٍ بدخيس النحض، بازِلُها	له صريفٌ، صريف القَعْوِ بالمسَدِ
4) فما أَبصر النارَ التي وضحت له	وراءَ جُفاف الطير إِلا تماريا
5) صَبَّحتُهُ بِسُلافَةٍ صَبَّحتُها	بِسُلافَةِ الخُلَطاءِ وَالنُّدَمَاءِ

ELEMENT_4:
Arabic name: طباق
English name: Antonymy
Arabic explanation: الطباق هو الجمع بين لفظين متضادين في المعنى داخل سياق واحد، لإبراز التباين وتقوية الدلالة من خلال التضاد الواضح بينهما. يُستخدم لإضفاء إيقاع معنوي وزيادة التأثير عبر شدّ انتباه القارئ إلى المفارقة بين الكلمتين
English explanation: Antonymy (or oxymoronic pairing) is the use of two words with opposite meanings within the same context to emphasize contrast and enhance the overall message. It creates a stronger expressive effect by drawing attention to the semantic opposition between the paired terms.
Examples:
1) تُضِيءُ الظَّلامَ بالعِشَاءِ كَأنَّهَا	مَنَارَة ُ مُمْسَى رَاهِبٍ مُتَبَتِّلِ
2) وَأنَا المُنَبِّهُ بَعْدَمَا قَدْ نَوَّمُوا	وَأنَا المُعَالِنُ صَفْحَة َ النُّوّامِ
3) فتلك تُبْلغني النعمانَ ، إن له	فضلاً على الناس في الأدنى ، وفي البَعَدِ
4) دعوتُ إِلى ذي العرش ربِّ محمد	لِيَجْمَعَ شعبًا أَو يُقَرِّبَ نائيًا
5) بِمُدامَةٍ تَغدو المُنى لِكُؤوسِها	خَوَلاً عَلى السَرّاءِ وَالضََرَّاءِ

[SECTION: FEW-SHOT EXAMPLES — new in Phase 4/E1, experiments/phase4_e1/fewshot_examples.py
 build_fewshot_block(), appended by build_system_message_e1(); THIS is the only section
 that differs between sets A/B/C — see §2]
--------------------------------
FEW-SHOT EXAMPLES (مجاز / استعارة فعل)
--------------------------------
Additional worked examples of ONLY the استعارة فعل (verbal metaphor) subtype
of مجاز (Trope), beyond the element definitions above. Each example gives the
full verse and the annotated span(s) within it.

1) يا كَبيرَ الذَّنْب عَفْوُ الـ    ـله من ذَنْبك أَكْبَرْ
   span: كَبيرَ الذَّنْب (استعارة ميتة)
   span: ـله من ذَنْبك أَكْبَرْ عَفْوُ الـ (استعارة ميتة)
2) أَكبرُ الأَشياء في أَصـ    ـغر عَفْوِ الله يصغَرْ
   span: أَصـ عَفْوِ الله ـغر (استعارة ميتة)
   span: أَكبرُ الأَشياء (يقصد أكبر الآثام؛ استعار الكبر لها. استعارة ميتة)
   span: يصغَرْ الأَشياء (يقصد أنّ الآثام تصغر. استعارة ميتة.)
[END OF SYSTEM MESSAGE]
```

Note: the analysis-instructions block (schema/output rules, §3-4 below) is **not** part of the system
message — it's prepended to the **user** message by `runner.py:build_user_message()`, per
`pilot_3models.prompts.build_user_message()`'s original convention. The system message above is sent
once per call via each provider's `system`/`system_instruction` parameter (OpenAI: a `role: "system"`
message).

---

## 2. Diff summary: what differs between Sets A, B, C

`diff` across all three `config/prompt_preview_{A,B,C}.txt` files: **identical through line 69** (the
entire `SYSTEM_HEADER` + `ELEMENTS_BLOCK` + the "FEW-SHOT EXAMPLES" section header/intro paragraph).
The only differing lines are the 2 worked examples themselves (lines 70-76), each drawn from a different
Abu Nuwas source poem:

| Set | Source poem | Example 1 | Example 2 |
|---|---|---|---|
| A | 16251 | v1: "أيا رُبَّ وَجْهٍ..." — span رَقيقِ حُسْنٍ | v5: "إِذا امتحن الدُّنْيا..." — 2 spans (الدُّنْيا لَبيبٌ امتحن; تكشَّفتْ له) |
| B | 17234 | v3: "يا كَبيرَ الذَّنْب..." — 2 spans | v4: "أَكبرُ الأَشياء..." — 3 spans |
| C | 21337 | v1: "ومترَّفٍ عقل الحَياءُُ..." — span عقل لِسانَه الحَياءُُ | v2: "لمّا نظرتُ إِلى الكَرَى..." — span الكَرَى قد عقّل الجَفْنَيْن بالإِغماءِ |

Confirmed no other differences anywhere in the prompt (same element definitions, same instructions,
same schema) — this isolates the pilot's manipulation to exactly the 2 few-shot examples, as designed.

---

## 3. User message template, filled with a real eval poem (first 4 verses)

Built by `runner.py:build_user_message()` = `pilot_3models.prompts.ANALYSIS_INSTRUCTIONS` (frozen,
unmodified) + a blank line + `ali_poems_io.build_poem_text()`'s verse-numbered plain text. Filled here
with the first 4 of eval poem 17373 (أبو نواس, "باب 7 قصيدة رقم 10", `other`-tagged... actually
`abu_nuwas`-tagged, 6 verses total — truncated to 4 here for illustration only; **the real runner sends
the full poem, not a truncation**):

```
================================
ANALYSIS PHASE (OUTPUT REQUIRED)
================================
Analyze each verse INDIVIDUALLY for the existence of ONLY the 4 elements above.

Return JSONL ONLY.
One JSON object per verse.
No text before or after.

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
- If *_exists is false -> *_appearance MUST be null
- If *_exists is true -> *_appearance MUST be a literal substring from the verse
- If ambiguous -> use TOKENS[i:j] (0-based whitespace tokens)
- Be conservative: if unsure -> exists=false
- Do NOT explain
- Do NOT add fields
- Do NOT merge verses
- Do NOT use markdown

--------------------------------
VERSES_BLOCK
--------------------------------

لو صحّ عَقْلي قلّ أَشباهي    أَجَلْ ولم أَلهُ مع اللاهي
أَعوذ بالله وأَسمائه    من عاجز التركيب تيّاهِ
لا تتناهى النَّفْسُ عن غيّها    ما لم يكن منها لها ناهي
لله دَرُّ المَوْت من خُطَّة    فيها استوى الأَحمقُ والداهي
```

Fact worth noting: **the verse number ("no") is never given in the text** — each line is one verse,
and the model is expected to infer `no` purely from 1-based line order. There is no per-line verse-number
prefix anywhere in the prompt.

---

## 4. Required output format + how `parse_response` handles malformed output

Required format (from `ANALYSIS_INSTRUCTIONS`, §3 above): **JSONL only** — one JSON object per verse, no
markdown fences, no prose before/after, 9 fixed keys per object (`no` + 4 elements × `_exists`/
`_appearance`), `*_appearance` must be `null` when `*_exists` is `false` and a literal verse substring
(or `TOKENS[i:j]` notation) when `true`.

`experiments/pilot_3models/parsing.py:parse_response()` (reused unmodified by `scoring.py`) handles the
raw text as follows:
1. Strips Markdown code fences (`` ```json `` / `` ```jsonl `` / `` ``` ``) via `FENCE_RE`, if present.
2. If what's left is a single line starting with `[`, tries `json.loads` on the whole thing as a JSON
   array; a parse failure here is recorded as `"top-level JSON array parse failed: {err}"` and treated
   as zero objects (not a crash).
3. Otherwise splits on non-blank lines and `json.loads`es each line independently; a line that fails to
   parse is recorded as `"line {i+1} parse failed: {err} | raw: {line[:200]}"` and simply **skipped** —
   every other line is still parsed normally (malformed lines don't invalidate the whole response).
4. For each successfully-parsed object: if it's not a dict or has no `"no"` key, records
   `"object missing 'no' field: {obj!r}"` and skips it. Otherwise, for each of the 4 elements, if the
   expected `{ar}_exists` key is missing, records `"verse {no}: missing key {exists_key}"` and sets that
   element's `exists`/`appearance` to `None`/`None` (not `False`/`None` — a missing key is distinct from
   an explicit `false`). If present, `exists` is coerced with `bool(...)` and `appearance` is read via
   `.get()` (so a missing `_appearance` key quietly becomes `None` with no error logged).
5. Returns `{"verses": {...}, "parse_errors": [...], "n_verses_parsed": len(verses)}` — **no retry, no
   repair attempt, no exception raised**; malformed input degrades to partial data plus a logged reason,
   per the parsing module's own stated design ("record the parse failure explicitly rather than
   attempting any repair").

Downstream, `scoring.py:majority_exists_and_appearance()` only counts a verse's votes from runs where
`v[element]["exists"] is not None` — so a verse whose `_exists` key was missing (parsed as `None`) is
excluded from that run's vote rather than counted as a false negative at the parse layer; it only becomes
an FN at the scoring layer if no run has a valid vote for that verse.

---

## 5. Per-model call settings in `runner.py` — identical or not?

All settings route through `experiments/pilot_3models/providers.py:CALLERS`, called by `runner.py` as
`caller(system_message, user_message, TEMPERATURE)` with `TEMPERATURE = 0.0` (from `e1_config.py`) for
every call, every provider, every set. There is **no retry logic and no JSON/structured-output mode**
anywhere in `runner.py` or `providers.py` — a single attempt per cell; any raised exception is caught by
`runner.py`'s own `try/except Exception`, recorded as that record's `"error"` field, and left for a
**manual** re-run (no automatic backoff/retry loop exists).

| Setting | Anthropic (not used in the real E1 run, costed only) | OpenAI (gpt-5.4-mini) | Google (gemini-3.5-flash) |
|---|---|---|---|
| Temperature | 0.0 | 0.0 | 0.0 |
| `max_tokens` | **explicit 16000** | not set (provider default) | not set (provider default) |
| Reasoning/thinking params | none set | none set | none set |
| JSON/structured-output mode | none — instruction-only JSON | none — instruction-only JSON | none — instruction-only JSON |
| Retries | none (single attempt; caught exception recorded, no auto-retry) | none | none |
| API call shape | `messages.create(system=..., messages=[user])` | `chat.completions.create(messages=[system, user])` | `generate_content(contents=user, config=GenerateContentConfig(system_instruction=..., temperature=...))` |

**Answer: not identical.** Temperature (0.0) and the absence of JSON mode/retries/reasoning params are
the same across all three. The one explicit difference is **`max_tokens`: Anthropic gets a hardcoded
16000-token cap; OpenAI and Google get no explicit cap at all** (whatever each API defaults to). No
provider has any reasoning-effort / extended-thinking configuration set, despite gpt-5.4-mini and
gemini-3.5-flash both being reasoning-capable model families — this pilot does not touch that knob.

---

## 6. One real raw model response vs. ground truth — GPT-5.4-mini, Set B, poem 17373 (6 verses, shortest in the eval pool that isn't trivially 2-4 verses)

Raw file: `results/phase4_e1/raw/B_17373_openai_run1.txt` (verbatim):

```
{"no":1,"مجاز_exists":false,"مجاز_appearance":null,"تشبيه_exists":false,"تشبيه_appearance":null,"كناية_exists":false,"كناية_appearance":null,"طباق_exists":false,"طباق_appearance":null}
{"no":2,"مجاز_exists":false,"مجاز_appearance":null,"تشبيه_exists":false,"تشبيه_appearance":null,"كناية_exists":false,"كناية_appearance":null,"طباق_exists":false,"طباق_appearance":null}
{"no":3,"مجاز_exists":false,"مجاز_appearance":null,"تشبيه_exists":false,"تشبيه_appearance":null,"كناية_exists":false,"كناية_appearance":null,"طباق_exists":false,"طباق_appearance":null}
{"no":4,"مجاز_exists":true,"مجاز_appearance":"لله دَرُّ المَوْت","تشبيه_exists":false,"تشبيه_appearance":null,"كناية_exists":false,"كناية_appearance":null,"طباق_exists":true,"طباق_appearance":"الأَحمقُ والداهي"}
{"no":5,"مجاز_exists":true,"مجاز_appearance":"مُرّنت","تشبيه_exists":false,"تشبيه_appearance":null,"كناية_exists":false,"كناية_appearance":null,"طباق_exists":false,"طباق_appearance":null}
{"no":6,"مجاز_exists":false,"مجاز_appearance":null,"تشبيه_exists":false,"تشبيه_appearance":null,"كناية_exists":false,"كناية_appearance":null,"طباق_exists":false,"طباق_appearance":null}
```

Ground truth for the same poem (Dr. Ali Hussein's own annotations, `data/ali_poems/poems/
17373_أبو_نواس_العصر_العباسي.json`, mapped to this project's 4 elements via
`pilot_3models.ground_truth.SUBSTRING_MAP`, same mapping used by every frozen Phase 1-3 number):

| Verse | Element (mapped) | GT span | GT subtype |
|---|---|---|---|
| 2 | Kenning (كناية) | عاجز التركيب تيّاهِ | كناية عن موصوف |
| 3 | Trope (مجاز) | النَّفْسُ غيّها | استعارة فعل |
| 4 | Trope (مجاز) | لله دَرُّ المَوْت | استعارة فعل مرشحة |
| 4 | Trope (مجاز) | دَرُّ المَوْت لله | استعارة مبنية على الكناية |
| 4 | Kenning (كناية) | دَرُّ المَوْت لله | استعارة مبنية على الكناية *(same span double-counted — its subtype label contains both "استعارة" and "كناية" substrings, so `SUBSTRING_MAP` maps it to both Trope and Kenning)* |
| 4 | Kenning (كناية) | الأَحمقُ | كناية لغوية |
| 4 | Kenning (كناية) | والداهي | كناية لغوية |
| 4 | Antonymy (طباق) | الأَحمقُ والداهي | طباق إيجاب |
| 5 | Trope (مجاز) | مُرّنت منّا وأَفواهِ بأَسماع | مجاز عقلي |
| 6 | Trope (مجاز) | وتصريفِه الأَمْر | استعارة فعل |
| 6 | Trope (مجاز) | الأَمْر | مجاز مرسل |

Verse-by-verse comparison:
- **v1**: model says all-false; GT has no Trope/Simile/Kenning/Antonymy here either (only an unmapped
  اشتقاق annotation) — correct.
- **v2**: model says all-false; GT has a Kenning span (عاجز التركيب تيّاهِ) — **missed (false negative)**.
- **v3**: model says all-false; GT has a Trope span (النَّفْسُ غيّها) — **missed (false negative)**.
- **v4**: model flags Trope with appearance "لله دَرُّ المَوْت" — **exact string match** to one of GT's
  two Trope spans for this verse (a strict-criterion true positive). Model also flags Antonymy with
  "الأَحمقُ والداهي" — **exact match** to the GT Antonymy span (another strict true positive). Model does
  **not** flag Kenning at all for v4, despite GT having 3 Kenning-mapped spans there — missed.
- **v5**: model flags Trope with appearance "مُرّنت" — GT's Trope span is the longer "مُرّنت منّا
  وأَفواهِ بأَسماع"; "مُرّنت" is a true substring of it, so this is a **token-overlap match but fails the
  strict criterion** (not identical strings) — exactly the strict-vs-token distinction `CLAUDE.md` rule 4
  requires reporting both ways for.
- **v6**: model says all-false; GT has two Trope-mapped spans — **missed (false negative)**.

Net for this poem: 2 strict TPs (v4 Trope, v4 Antonymy), 1 token-only TP (v5 Trope), several FNs (v2
Kenning, v3 Trope, v4 Kenning ×3 span-records, v6 Trope ×2 span-records), 0 FPs. No fabricated
appearances were observed in this response — every non-null `_appearance` string is a verbatim substring
of its verse's text.

---

## 7. Does the prompt tell the model about the other 3 rhetorical elements, or only استعارة فعل?

**Both — at two different levels of detail.** The system message's `ELEMENTS_BLOCK` (§1) gives full
definitions + examples for **all 4 elements** (مجاز/Trope, تشبيه/Simile, كناية/Kenning, طباق/Antonymy) —
this is the frozen, unmodified Phase-1 prompt, unrelated to E1. The **few-shot block that E1 adds**
(§1's "FEW-SHOT EXAMPLES" section, §2's diff) covers **only** the استعارة فعل subtype of مجاز/Trope —
its own header says so explicitly ("Additional worked examples of ONLY the استعارة فعل... subtype of
مجاز"). The output schema (§3) still asks the model to judge all 4 elements per verse every time; E1's
manipulation is additional emphasis/examples for one subtype of one element, not a narrowing of what's
asked for.
