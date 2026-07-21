from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ELEMENTS_DIR = ROOT / "data" / "elements"
RESULTS_DIR = ROOT / "results" / "pilot_3models"
RAW_DIR = RESULTS_DIR / "raw"

FORTH_STEP_DATA = ROOT / "archive" / "Forth_Step" / "Data"
GT_DIR = ROOT / "data" / "ground_truth" / "ali_ana" / "original"

ELEMENT_ORDER = ["Trope", "Simile", "Kenning", "Antonymy"]
ELEMENT_AR = {"Trope": "مجاز", "Simile": "تشبيه", "Kenning": "كناية", "Antonymy": "طباق"}
ELEMENT_FILES = {"Trope": "Trope.txt", "Simile": "Simile.txt", "Kenning": "Kenning.txt", "Antonymy": "Antonymy.txt"}

# Registry of all 5 poems with ground truth in data/ground_truth/ali_ana.
POEMS = {
    "Imru1": {
        "poetry_path": FORTH_STEP_DATA / "Imru1" / "poetry.txt",
        "ground_truth_path": GT_DIR / "امرؤ القيس 1.xlsx",
        "poet": "امرؤ القيس (Imru' al-Qais)",
        "title": "قصيدة رقم 1 (Poem 1, the Mu'allaqa)",
        "n_verses": 81,
    },
    "Imru2": {
        "poetry_path": FORTH_STEP_DATA / "Imru2" / "poetry.txt",
        "ground_truth_path": GT_DIR / "امرؤ القيس 8.xlsx",
        "poet": "امرؤ القيس (Imru' al-Qais)",
        "title": "قصيدة رقم 8 (Poem 8)",
        "n_verses": 23,
    },
    "Nabigha": {
        "poetry_path": FORTH_STEP_DATA / "Althobyane" / "poetry.txt",
        "ground_truth_path": GT_DIR / "النابغة الذبياني.xlsx",
        "poet": "النابغة الذبياني (Al-Nabigha Al-Dhubyani)",
        "title": "",
        "n_verses": 50,
    },
    "Jarir": {
        "poetry_path": FORTH_STEP_DATA / "Jareer" / "poetry.txt",
        "ground_truth_path": GT_DIR / "جرير.xlsx",
        "poet": "جرير (Jarir)",
        "title": "",
        "n_verses": 40,
    },
    "Abu_Tammam": {
        "poetry_path": FORTH_STEP_DATA / "Abu_tammam" / "poetry.txt",
        "ground_truth_path": GT_DIR / "ابو تمام.xlsx",
        "poet": "ابو تمام (Abu Tammam)",
        "title": "",
        "n_verses": 30,
    },
}

# DEV/TEST split (see analysis in conversation): DEV is small but covers all 4
# elements; TEST is frozen until final evaluation.
DEV_POEMS = ["Imru2", "Nabigha"]
TEST_POEMS = ["Imru1", "Jarir", "Abu_Tammam"]

# --- Backward-compat single-poem pointer used by prompts.py/run_pilot.py/build_report.py ---
# Change ACTIVE_POEM to run the pilot against a different poem.
ACTIVE_POEM = "Imru2"
_active = POEMS[ACTIVE_POEM]
POEM_PATH = _active["poetry_path"]
GROUND_TRUTH_PATH = _active["ground_truth_path"]
POEM_NAME = ACTIVE_POEM
POET = _active["poet"]
POEM_TITLE = _active["title"]
N_VERSES = _active["n_verses"]

N_RUNS = 2
TEMPERATURE = 0.0

MODELS = {
    "anthropic": {"model_id": "claude-sonnet-4-6", "display": "Claude Sonnet 4.6",
                  "price_in": 3.00, "price_out": 15.00},
    "openai": {"model_id": "gpt-5.4-mini", "display": "GPT-5.4 mini",
               "price_in": 0.75, "price_out": 4.50},
    "google": {"model_id": "gemini-3.5-flash", "display": "Gemini 3.5 Flash",
               "price_in": 1.50, "price_out": 9.00},
}
