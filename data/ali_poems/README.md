# Ali Hussein manually-analysed poem corpus — downloaded snapshot

## ⚠️ Licensing status: UNCONFIRMED — do not redistribute without clearing this first

This directory is a downloaded snapshot of data served by a public, unauthenticated API at
`https://arabic-rhetoric.haifa.ac.il/api/*`. No robots.txt disallow rules and no terms/license/
privacy/copyright page exist anywhere on the site (confirmed by direct inspection on
2026-10-10 — every such path serves the same Angular SPA shell, and `/api/*` is the only set
of routes that gives real responses). **The absence of a stated restriction is not a license.**
This is **blocker #1** in [`writing/paper_plan/TOP_5_BLOCKERS.md`](../../writing/paper_plan/TOP_5_BLOCKERS.md):
the licensing/rights status of this corpus is undocumented, and downloading it does **not**
resolve that — it still needs an explicit answer from Dr. Ali Hussein / the supervisor before
any of this data (beyond what the project already licenses under the existing 5-poem ground
truth) is shared, redistributed, or included in a public release/paper appendix.

## Source

- Site: `https://arabic-rhetoric.haifa.ac.il` ("The Rhetorical Element Identifier" / محرك البحث
  البلاغي, idea: Prof. Ali Hussein, development: Fawzi Abu Elhija, University of Haifa).
- Download date: **2026-10-10**.
- Access method: the site's public REST API at `/api/*`. No login/credentials were used — the
  API responds identically to an anonymous request as it does after clicking the site's own
  "Visitor Access (no user/password needed)" button, which itself makes zero backend calls (it
  is pure client-side UI state). This was confirmed by direct `fetch()` calls from a fresh
  browser context before any visitor-access interaction.

## Method

`scripts/download_ali_poems.py` (repo root) does the following:

1. Fetches lookup tables once: `/api/poets` (1,042 poets — the site's full poet catalogue, not
   just annotated ones), `/api/periods` (16 periods), `/api/places` (56 places), `/api/themas`
   (79 themes), `/api/retoricals` (157 rhetorical element/subtype labels).
2. Batches over all 1,042 poet ids (80 ids per request) against
   `/api/searchRetoricalsByPoemsPoets` to collect every manual-annotation record in the corpus
   (a poem with zero manual annotations returns none). This enumerates the set of poems that
   actually have manual rhetorical analysis — 167 poems across 52 poets.
3. For each of the 167 poems:
   - `/api/poem/{poemId}` — bibliographic metadata (title, source citation, rhyme id).
   - `/api/getWordsPoem?poetid=<id>&poemid=<id>` — the full poem text, **word by word**, each
     word tagged with `colomn` (verse index — the same numbering the annotation records' own
     `colomn` field uses) and `fl` (0 = صدر/first hemistich, 1 = عجز/second hemistich). The
     script reconstructs each verse by grouping words on `(colomn, fl)` and joining them in
     array order.
4. Period (الفترة) and place (المكان) are **poet-level** attributes in this database (each poet
   record carries one `period` id and a `places` array), not per-poem fields, and are resolved
   via the lookup tables. Theme (الثيمة) and rhetorical element (العنصر البلاغي) are
   per-annotation-record fields.
5. Raw API responses are saved **unchanged** under `raw/` (lookup tables, per-poet-batch
   annotation sweeps, and per-poem `poem_meta/` + `poem_words/` responses). Normalized per-poem
   JSON is written to `poems/`. `manifest.csv` indexes everything.

Politeness: 1.5s delay between every request, a descriptive `User-Agent`
(`Metaphorical-Analysis-Research-Scraper/1.0`, contact email included), retry-with-backoff (5
attempts, exponential) on any request failure, full logging to `download.log`, and resumability
(every raw response is cached to disk and reused on a re-run rather than re-fetched).

### Why `/api/getWordsPoem` and not page-scraping

Before writing the scraper, the manual-analysis page, the automatic-analysis page, and the
rhetorical-analysis (per-poet "has this been run" list) pages were all driven directly in a
browser to check whether any of them render full verse text beyond what the API already
returns — none do; they only ever show the annotation-span table (span text + verse index +
explanation). The site's own "search engine" page (`/search-engine/poems`) *does* render full
verse text (split into صدر/عجز) via `/api/getLineWordsBySearchWord`, but only for lines matching
a searched word, not an entire poem. Grepping the Angular bundle's route-name string constants
(rather than just literal `/api/...` path strings, which Angular's lazy route construction can
evade) surfaced `getWordsPoem`, which returns a poem's full word list directly. Full detail of
this investigation is logged in `docs/phase4/SESSION_LOG.md` (2026-10-10T04:05–04:35).

## Consistency check against the project's existing frozen ground truth

The project already has 5 manually-analysed poems from this same source, entered by hand into
`data/ground_truth/ali_ana/original/*.xlsx` and used as the frozen Phase 1 ground truth
(`archive/Forth_Step/Data/{Imru1,Imru2,Nabigha,Jarir,Abu_Tammam}/poetry.txt`). Before writing the
scraper, all 5 were checked against the live API:

| Project label | poem_id | poet_id | poet | Annotation count (xlsx) | Annotation count (API) | Full-text check |
|---|---|---|---|---|---|---|
| Imru1 | 3205 | 58 | امرؤ القيس | 305 | 305 | not re-verified verse-by-verse (count only) |
| Imru2 | 2196 | 58 | امرؤ القيس | 44 | 44 | **verse-by-verse identical** to `poetry.txt` (23/23 verses, diacritics included) |
| Jarir | 10539 | 1385 | جرير بن عطيّة | 166 | 166 | not re-verified verse-by-verse (count only) |
| Nabigha | 3218 | 1070 | النابغة الذبياني | 167 | 167 | not re-verified verse-by-verse (count only) |
| Abu_Tammam | 2127 | 33 | أبو تمّام | 94 | 94 | not re-verified verse-by-verse (count only) |

All 5 annotation counts match exactly. Full verse-by-verse text was spot-checked for Imru2 only
(the others were not re-verified character-by-character, only by annotation count) — see the
session log for the exact comparison.

## Schema

`manifest.csv` columns: `poem_id, poet_id, poet_name, period, places, theme, title,
source_citation, file_path, sha256, verse_count, annotation_count,
annotation_counts_per_element, download_time, already_used_in_project`.

Each `poems/{poemId}_{poet}_{period}.json` file:

```json
{
  "poem_id": 2196,
  "poet_id": 58,
  "poet_name": "امرؤ القيس",
  "period": "العصر الجاهلي",
  "places": [],
  "poem_name": "قصيدة رقم 8",
  "source_citation": "امرؤ القيس. ديوان امرئ القيس وملحقاته بشرح أبي سعيد السكري. ...",
  "rhyme_id": 9,
  "num_of_dewan": "8",
  "themes": ["الاعتذار", "الرحلة", "المدح", "النسيب", "الهجاء", "فخر شخصي"],
  "rhetorical_elements": ["استعارة", "اشتقاق", "تجاهل العارف", "تجريد", "تشبيه", "..."],
  "element_counts": {"تشبيه": 7, "كناية": 8, "...": "..."},
  "verse_count": 23,
  "annotation_count": 44,
  "verses": [
    {"verse_index": 1, "sadr": "لِمَنِ الدّيَارُ غَشِيتُهَا بِسُحَامِ",
     "ajuz": "فَعَمَايَتَينِ فَهَضْبِ ذِي أقْدَامِ",
     "text": "لِمَنِ الدّيَارُ غَشِيتُهَا بِسُحَامِ    فَعَمَايَتَينِ فَهَضْبِ ذِي أقْدَامِ"}
  ],
  "annotations": [
    {"span_text": "...", "verse_index": "1,1,1,40,40", "element": "تجاهل العارف",
     "subtype": "تجاهل العارف", "theme": "النسيب", "analysis": "", "raw_key": 37}
  ],
  "source_url": "https://arabic-rhetoric.haifa.ac.il/manual-analysis/poems",
  "already_used_in_project": null
}
```

Notes:
- `annotations[].verse_index` is the raw `colomn` field from the API, which can be a
  comma-separated list of verse indices when a span crosses multiple verses (e.g. `"9,10,11"`).
- `annotations[].analysis` is frequently empty — the site's own الشرح (explanation) field is
  not filled in for every annotation (confirmed already in Phase A: this is a site-data
  property, not a scraper omission).
- `already_used_in_project` names the 5 poems already in `experiments/pilot_3models/config.py`
  (`Imru1`, `Imru2`, `Nabigha`, `Jarir`, `Abu_Tammam` — see table above for ids).

## Validation results (2026-10-10)

- **Poem/poet counts**: 167 unique poems, 52 unique poets — matches Phase A's census exactly.
- **No empty files, no duplicate `poem_id`s.**
- **Arabic encoding**: spot-checked intact (UTF-8, diacritics preserved) across sampled files.
- **Total**: 3,470 reconstructed verses, 10,430 annotation records across all 167 poems —
  matches Phase A's corpus-wide annotation count exactly.
- **Missing fields** (6 poems, all genuine gaps in the *source site's own data*, not scraper
  bugs):
  - 5 poems missing `period`: 4 belong to poet id 1400 (الحمدوي), whose `period` id (27) is not
    present in the site's own `/api/periods` lookup table (max id there is 26) — a gap in the
    site's reference data, not ours; 1 poem (poem_id 7408) belongs to poet id 1263 (مُليح بن
    الحكم), who has no `period` set at all on the site.
  - 1 poem (poem_id 28601, "قصيدة شعراء عباسيون منسيون 9") has 29 manual annotations but **zero**
    words returned by `/api/getWordsPoem` (`{"success":true,"data":[]}`) — the site has no
    word-level text entered for this poem at all, so its full verse text is genuinely
    unobtainable from this source. Its annotations (span text only, no surrounding verse
    context) are still saved.
- Total size on disk: ~20 MB (well under the 50 MB commit threshold).

## File layout

```
data/ali_poems/
  README.md              (this file)
  manifest.csv
  download.log
  poems/                 167 normalized per-poem JSON files
  raw/
    lookups/              poets.json, periods.json, places.json, themas.json, retoricals.json
    annotation_batches/   batch_000.json ... batch_013.json (raw searchRetoricalsByPoemsPoets responses)
    poem_meta/             {poemId}.json  (raw /api/poem/{id} responses)
    poem_words/             {poemId}.json  (raw /api/getWordsPoem responses)
```
