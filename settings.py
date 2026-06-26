"""Persistent application settings stored as JSON in the user's config dir."""

import dataclasses
import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)

_PATH = Path.home() / ".config" / "udp1306c" / "settings.json"


@dataclasses.dataclass
class AppSettings:
    lang: str = "uk"
    poll_sec: float = 4.0
    max_points: int = 10_000
    infinite: bool = True
    skip_repeat: bool = False
    last_port: str = ""

    def save(self) -> None:
        _PATH.parent.mkdir(parents=True, exist_ok=True)
        _PATH.write_text(
            json.dumps(dataclasses.asdict(self), indent=2, ensure_ascii=False)
        )
        log.debug("Settings saved to %s", _PATH)

    @classmethod
    def load(cls) -> "AppSettings":
        try:
            data = json.loads(_PATH.read_text())
            valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            return cls(**valid)
        except FileNotFoundError:
            return cls()
        except Exception:
            log.warning(
                "Could not load settings from %s, using defaults", _PATH, exc_info=True
            )
            return cls()
