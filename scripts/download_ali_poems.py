"""Download Dr. Ali Hussein's manually-analysed poem corpus from arabic-rhetoric.haifa.ac.il.

Source: the site's public, unauthenticated REST API at /api/*. No login is performed;
the "Visitor Access" button on the site's own /login page makes zero backend calls, so
this script talks to the same backend an anonymous visitor reaches by clicking it.

Endpoints used (all confirmed against the live site, see docs/phase4/SESSION_LOG.md):
  - /api/poets, /api/periods, /api/places, /api/themas, /api/retoricals
      -> lookup tables (id -> name), fetched once.
  - /api/searchRetoricalsByPoemsPoets?selectedPoet=<comma-separated poet ids>&...
      -> flat list of annotation records; batched over all poet ids to enumerate
         every poem that has manual analysis (a poem with none returns no records).
  - /api/poem/{poemId}
      -> per-poem bibliographic metadata (name, source citation, rhyme id, ...).
  - /api/getWordsPoem?poetid=<id>&poemid=<id>
      -> full poem text, word by word, with colomn (verse index, same numbering as
         the annotation records' colomn field) and fl (0=sadr/1=ajuz hemistich).
         Reconstructed by grouping on (colomn, fl) and joining words in array order.

Licensing status of this corpus is UNCONFIRMED - see data/ali_poems/README.md and
writing/paper_plan/TOP_5_BLOCKERS.md item 1. This script only downloads; it does not
resolve that blocker.
"""
from __future__ import annotations

import csv
import hashlib
import json
import logging
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests

BASE = "https://arabic-rhetoric.haifa.ac.il"
API = f"{BASE}/api"
USER_AGENT = (
    "Metaphorical-Analysis-Research-Scraper/1.0 "
    "(academic corpus collection; contact: faisalomari321@gmail.com)"
)
REQUEST_DELAY_S = 1.5
MAX_RETRIES = 5
RETRY_BACKOFF_BASE_S = 2.0
POET_BATCH_SIZE = 80

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = REPO_ROOT / "data" / "ali_poems"
RAW_DIR = OUT_ROOT / "raw"
POEMS_DIR = OUT_ROOT / "poems"
LOG_PATH = OUT_ROOT / "download.log"

# poems already used elsewhere in this project (poemId -> label), for the manifest flag.
# see experiments/pilot_3models/config.py and docs/phase4/SESSION_LOG.md's 5-poem
# consistency check (2026-10-10T04:05-04:35).
ALREADY_USED_POEM_IDS = {
    3205: "Imru1",
    2196: "Imru2",
    3218: "Nabigha",
    10539: "Jarir",
    2127: "Abu_Tammam",
}


def setup_logging() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )


def get_json(url: str, params: dict | None = None) -> dict[str, Any]:
    """GET with retry-with-backoff. Returns the parsed JSON body."""
    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # noqa: BLE001 - log and retry any failure
            last_exc = exc
            wait = RETRY_BACKOFF_BASE_S ** attempt
            logging.warning(
                "request failed (attempt %d/%d) for %s %s: %s - retrying in %.1fs",
                attempt, MAX_RETRIES, url, params, exc, wait,
            )
            time.sleep(wait)
    assert last_exc is not None
    raise last_exc


def polite_sleep() -> None:
    time.sleep(REQUEST_DELAY_S)


def save_raw(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_filename_component(s: str) -> str:
    """Normalize an Arabic/mixed string into a filesystem-safe filename component.

    Keeps Arabic letters, Latin letters, digits, spaces (turned into underscores), and
    a few punctuation marks; strips everything else (slashes, quotes, control chars).
    """
    s = unicodedata.normalize("NFC", s)
    out = []
    for ch in s:
        if ch.isalnum() or ch in (" ", "-", "_", "."):
            out.append(ch)
    cleaned = "".join(out).strip()
    cleaned = "_".join(cleaned.split())
    return cleaned[:120] if cleaned else "unknown"


@dataclass
class Lookups:
    poets: dict[int, dict] = field(default_factory=dict)
    periods: dict[int, str] = field(default_factory=dict)
    places: dict[int, dict] = field(default_factory=dict)
    themas: dict[int, str] = field(default_factory=dict)
    retoricals: dict[int, dict] = field(default_factory=dict)


def fetch_lookups() -> Lookups:
    logging.info("Fetching lookup tables (poets, periods, places, themas, retoricals)")
    lk = Lookups()

    poets_raw = get_json(f"{API}/poets")
    save_raw(RAW_DIR / "lookups" / "poets.json", poets_raw)
    lk.poets = {p["id"]: p for p in poets_raw["data"]}
    polite_sleep()

    periods_raw = get_json(f"{API}/periods")
    save_raw(RAW_DIR / "lookups" / "periods.json", periods_raw)
    lk.periods = {p["id"]: p["name"] for p in periods_raw["data"]}
    polite_sleep()

    places_raw = get_json(f"{API}/places")
    save_raw(RAW_DIR / "lookups" / "places.json", places_raw)
    lk.places = {p["id"]: p for p in places_raw["data"]}
    polite_sleep()

    themas_raw = get_json(f"{API}/themas")
    save_raw(RAW_DIR / "lookups" / "themas.json", themas_raw)
    lk.themas = {t["id"]: t["name"] for t in themas_raw["data"]}
    polite_sleep()

    retoricals_raw = get_json(f"{API}/retoricals")
    save_raw(RAW_DIR / "lookups" / "retoricals.json", retoricals_raw)
    lk.retoricals = {r["id"]: r for r in retoricals_raw["data"]}
    polite_sleep()

    logging.info(
        "Lookups: %d poets, %d periods, %d places, %d themas, %d retoricals",
        len(lk.poets), len(lk.periods), len(lk.places), len(lk.themas), len(lk.retoricals),
    )
    return lk


def enumerate_annotations(lk: Lookups) -> list[dict]:
    """Batch over every poet id and collect all annotation records (manual analysis)."""
    poet_ids = sorted(lk.poets.keys())
    logging.info("Enumerating annotations across %d poet ids in batches of %d", len(poet_ids), POET_BATCH_SIZE)
    all_records: list[dict] = []
    batch_dir = RAW_DIR / "annotation_batches"
    batch_dir.mkdir(parents=True, exist_ok=True)

    for batch_idx, start in enumerate(range(0, len(poet_ids), POET_BATCH_SIZE)):
        batch = poet_ids[start:start + POET_BATCH_SIZE]
        batch_file = batch_dir / f"batch_{batch_idx:03d}.json"
        if batch_file.exists():
            logging.info("Batch %d already downloaded, loading from disk", batch_idx)
            with open(batch_file, encoding="utf-8") as f:
                payload = json.load(f)
        else:
            ids_param = ",".join(str(i) for i in batch)
            logging.info("Fetching batch %d (%d poet ids)", batch_idx, len(batch))
            payload = get_json(
                f"{API}/searchRetoricalsByPoemsPoets",
                params={
                    "selectedPeriod": 0,
                    "selectedPlace": 0,
                    "selectedPoet": ids_param,
                    "selectedPoemsPoet": 0,
                    "selectedRetorical": 0,
                    "selectedThema": 0,
                },
            )
            save_raw(batch_file, payload)
            polite_sleep()
        records = payload.get("data") or []
        if isinstance(records, list):
            all_records.extend(records)
        logging.info("Batch %d: %d annotation records (running total %d)", batch_idx, len(records) if isinstance(records, list) else 0, len(all_records))

    logging.info("Total annotation records collected: %d", len(all_records))
    return all_records


def group_by_poem(records: list[dict]) -> dict[int, list[dict]]:
    grouped: dict[int, list[dict]] = {}
    for r in records:
        pid = r.get("poemId")
        if pid is None:
            continue
        grouped.setdefault(pid, []).append(r)
    return grouped


def fetch_poem_metadata(poem_id: int) -> dict:
    meta_file = RAW_DIR / "poem_meta" / f"{poem_id}.json"
    if meta_file.exists():
        with open(meta_file, encoding="utf-8") as f:
            return json.load(f)
    payload = get_json(f"{API}/poem/{poem_id}")
    save_raw(meta_file, payload)
    polite_sleep()
    return payload


def fetch_poem_words(poet_id: int, poem_id: int) -> dict:
    words_file = RAW_DIR / "poem_words" / f"{poem_id}.json"
    if words_file.exists():
        with open(words_file, encoding="utf-8") as f:
            return json.load(f)
    payload = get_json(f"{API}/getWordsPoem", params={"poetid": poet_id, "poemid": poem_id})
    save_raw(words_file, payload)
    polite_sleep()
    return payload


def reconstruct_verses(words_payload: dict) -> list[dict]:
    words = words_payload.get("data") or []
    by_colomn: dict[int, dict[int, list[str]]] = {}
    for w in words:
        col = w.get("colomn")
        fl = w.get("fl")
        if col is None or fl is None:
            continue
        by_colomn.setdefault(col, {0: [], 1: []})[fl].append(w.get("name", ""))
    verses = []
    for col in sorted(by_colomn.keys()):
        hemistichs = by_colomn[col]
        sadr = " ".join(hemistichs.get(0, []))
        ajuz = " ".join(hemistichs.get(1, []))
        verses.append({
            "verse_index": col,
            "sadr": sadr,
            "ajuz": ajuz,
            "text": f"{sadr}    {ajuz}".strip(),
        })
    return verses


def build_normalized_poem(
    poem_id: int,
    poet_id: int,
    annotations: list[dict],
    lk: Lookups,
) -> tuple[dict, str, str]:
    """Returns (normalized_record, poet_name, period_name)."""
    meta_payload = fetch_poem_metadata(poem_id)
    meta = meta_payload.get("data") or {}

    words_payload = fetch_poem_words(poet_id, poem_id)
    verses = reconstruct_verses(words_payload)

    poet = lk.poets.get(poet_id, {})
    poet_name = poet.get("name", "unknown")
    period_id = poet.get("period")
    period_name = lk.periods.get(period_id, "") if period_id else ""
    place_ids = poet.get("places") or []
    place_names = []
    for pid in place_ids:
        p = lk.places.get(pid)
        if p:
            name = p.get("name", "")
            sub = p.get("subPlace", "")
            place_names.append(f"{name} ({sub})" if sub and sub != name else name)
    poem_name = meta.get("name") or (annotations[0].get("poemName") if annotations else "") or f"poem_{poem_id}"

    norm_annotations = []
    themes_used = set()
    elements_used = set()
    element_counts: dict[str, int] = {}
    for rec in annotations:
        element = rec.get("retoricalName", "")
        subtype = rec.get("subRetoricalName", "")
        theme = rec.get("themaName", "")
        if theme:
            themes_used.add(theme)
        if element:
            elements_used.add(element)
            element_counts[element] = element_counts.get(element, 0) + 1
        norm_annotations.append({
            "span_text": rec.get("wordName") or rec.get("word") or "",
            "verse_index": rec.get("colomn"),
            "element": element,
            "subtype": subtype,
            "theme": theme,
            "analysis": rec.get("description", ""),
            "raw_key": rec.get("key"),
        })

    normalized = {
        "poem_id": poem_id,
        "poet_id": poet_id,
        "poet_name": poet_name,
        "period": period_name,
        "places": place_names,
        "poem_name": poem_name,
        "source_citation": meta.get("source"),
        "rhyme_id": meta.get("rhyme"),
        "num_of_dewan": meta.get("numOfDewan"),
        "themes": sorted(themes_used),
        "rhetorical_elements": sorted(elements_used),
        "element_counts": element_counts,
        "verse_count": len(verses),
        "annotation_count": len(norm_annotations),
        "verses": verses,
        "annotations": norm_annotations,
        "source_url": f"{BASE}/manual-analysis/poems",
        "already_used_in_project": ALREADY_USED_POEM_IDS.get(poem_id),
    }
    return normalized, poet_name, period_name


def write_poem_file(poem_id: int, poet_name: str, period_name: str, normalized: dict) -> Path:
    fname = f"{poem_id}_{safe_filename_component(poet_name)}_{safe_filename_component(period_name)}.json"
    path = POEMS_DIR / fname
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(normalized, f, ensure_ascii=False, indent=1)
    return path


def main() -> None:
    setup_logging()
    logging.info("=== Starting Ali-poems download ===")

    lk = fetch_lookups()
    records = enumerate_annotations(lk)
    grouped = group_by_poem(records)
    logging.info("Found %d unique poems with manual annotations", len(grouped))

    poet_names_seen = {r.get("poetId") for r in records if r.get("poetId") is not None}
    logging.info("Found %d unique poets among annotated poems", len(poet_names_seen))

    manifest_rows = []
    errors: list[tuple[int, str]] = []

    for i, poem_id in enumerate(sorted(grouped.keys()), start=1):
        anns = grouped[poem_id]
        poet_id = anns[0].get("poetId")
        logging.info("[%d/%d] poem_id=%s poet_id=%s annotations=%d", i, len(grouped), poem_id, poet_id, len(anns))
        try:
            normalized, poet_name, period_name = build_normalized_poem(poem_id, poet_id, anns, lk)
            out_path = write_poem_file(poem_id, poet_name, period_name, normalized)

            elem_summary = ";".join(f"{k}={v}" for k, v in sorted(normalized["element_counts"].items()))
            manifest_rows.append({
                "poem_id": poem_id,
                "poet_id": poet_id,
                "poet_name": poet_name,
                "period": period_name,
                "places": "; ".join(normalized["places"]),
                "theme": "; ".join(normalized["themes"]),
                "title": normalized["poem_name"],
                "source_citation": normalized["source_citation"] or "",
                "file_path": str(out_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "sha256": sha256_of_file(out_path),
                "verse_count": normalized["verse_count"],
                "annotation_count": normalized["annotation_count"],
                "annotation_counts_per_element": elem_summary,
                "download_time": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "already_used_in_project": normalized["already_used_in_project"] or "",
            })
        except Exception as exc:  # noqa: BLE001
            logging.error("FAILED poem_id=%s: %s", poem_id, exc)
            errors.append((poem_id, str(exc)))

    manifest_path = OUT_ROOT / "manifest.csv"
    fieldnames = [
        "poem_id", "poet_id", "poet_name", "period", "places", "theme", "title",
        "source_citation", "file_path", "sha256", "verse_count", "annotation_count",
        "annotation_counts_per_element", "download_time", "already_used_in_project",
    ]
    with open(manifest_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in manifest_rows:
            writer.writerow(row)

    logging.info("=== Done. %d poems written, %d errors ===", len(manifest_rows), len(errors))
    if errors:
        for pid, msg in errors:
            logging.error("  poem_id=%s: %s", pid, msg)


if __name__ == "__main__":
    main()
