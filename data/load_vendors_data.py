import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / "vendors.json"

def load_vendors_data():
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)