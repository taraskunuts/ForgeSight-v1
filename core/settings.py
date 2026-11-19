
import json
from pathlib import Path


# ==========================================
# FORGESIGHT SETTINGS
# ==========================================

SETTINGS_FILE = (
    Path(__file__).resolve().parent.parent
    / "forgesight_settings.json"
)

DEFAULT_SETTINGS = {
    "resolution_width": None,
    "resolution_height": None,
    "show_overlay": True
}


# ==========================================
# LOAD SETTINGS
# ==========================================

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
                saved_settings = json.load(file)

            if isinstance(saved_settings, dict):
                return {
                    **DEFAULT_SETTINGS,
                    **saved_settings
                }

        except (json.JSONDecodeError, OSError):
            pass

    return DEFAULT_SETTINGS.copy()


# ==========================================
# SAVE SETTINGS
# ==========================================

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)
