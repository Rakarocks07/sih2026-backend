import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
FORECAST_FILE = DATA_DIR / "forecast_merged.json"
PLUMES_FILE = DATA_DIR / "plumes_merged.geojson"

# Keeps the last good copy of each file in memory, so a broken/missing
# file from a teammate never crashes an endpoint that was already working.
_cache: dict = {}


def _load(path: Path, key: str):
    try:
        mtime = path.stat().st_mtime
        if _cache.get(key) is None or _cache.get(f"{key}_mtime") != mtime:
            with open(path, encoding="utf-8") as f:
                _cache[key] = json.load(f)
            _cache[f"{key}_mtime"] = mtime
    except Exception:
        if _cache.get(key) is None:
            raise
    return _cache[key]


def load_forecast():
    return _load(FORECAST_FILE, "forecast")


def load_plumes():
    return _load(PLUMES_FILE, "plumes")
