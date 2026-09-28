import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "forecast_merged.json"

# The "memory" of the last good copy of the data
_cache = {"data": None, "mtime": None}


def load_forecast():
    """Return M4's forecast data. Re-reads the file only if it changed."""
    try:
        mtime = DATA_FILE.stat().st_mtime
        if _cache["data"] is None or mtime != _cache["mtime"]:
            with open(DATA_FILE, encoding="utf-8") as f:
                _cache["data"] = json.load(f)
            _cache["mtime"] = mtime
    except Exception:
        # File missing or broken: fall back to the last good copy if we have one
        if _cache["data"] is None:
            raise
    return _cache["data"]
