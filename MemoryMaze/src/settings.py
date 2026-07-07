"""User-configurable, persisted preferences (control scheme, theme, toggles)."""

from . import storage

SETTINGS_FILE = "settings.json"

CONTROL_OPTIONS = ["ARROWS", "WASD"]
THEME_OPTIONS = ["NEON", "AMBER", "MONO"]

DEFAULTS = {
    "controls": "ARROWS",
    "theme": "NEON",
    "effects": True,
    "sound": True,
}


class Settings:
    """A tiny persisted key/value store with validated cycling."""

    def __init__(self):
        data = storage.load_json(SETTINGS_FILE, {})
        self.values = dict(DEFAULTS)
        if isinstance(data, dict):
            for key in DEFAULTS:
                if key in data:
                    self.values[key] = data[key]

    def __getitem__(self, key):
        return self.values[key]

    def save(self):
        storage.save_json(SETTINGS_FILE, self.values)

    def toggle(self, key):
        self.values[key] = not self.values[key]
        self.save()

    def cycle(self, key, options):
        cur = self.values.get(key, options[0])
        idx = (options.index(cur) + 1) % len(options) if cur in options else 0
        self.values[key] = options[idx]
        self.save()
