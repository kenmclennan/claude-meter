import json
from dataclasses import asdict, dataclass
from pathlib import Path

SETTINGS_PATH = Path.home() / "Library" / "Application Support" / "claude-meter" / "settings.json"


@dataclass
class Settings:
    """User preferences, persisted as a small JSON file.

    Unknown keys are ignored and a missing or unreadable file yields the defaults, so a
    bad file can never stop the app from starting.
    """

    show_in_dock: bool = True

    @classmethod
    def load(cls, path: Path = SETTINGS_PATH) -> "Settings":
        try:
            raw = json.loads(path.read_text())
        except (OSError, ValueError):
            return cls()
        if not isinstance(raw, dict):
            return cls()
        settings = cls()
        show_in_dock = raw.get("show_in_dock")
        if isinstance(show_in_dock, bool):
            settings.show_in_dock = show_in_dock
        return settings

    def save(self, path: Path = SETTINGS_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2) + "\n")
