"""Unit tests for settings.py."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from settings import AppSettings


class TestAppSettingsDefaults(unittest.TestCase):
    def test_default_lang(self):
        self.assertEqual(AppSettings().lang, "uk")

    def test_default_poll_sec(self):
        self.assertEqual(AppSettings().poll_sec, 4.0)

    def test_default_max_points(self):
        self.assertEqual(AppSettings().max_points, 10_000)

    def test_default_infinite(self):
        self.assertTrue(AppSettings().infinite)

    def test_default_skip_repeat(self):
        self.assertFalse(AppSettings().skip_repeat)

    def test_default_last_port(self):
        self.assertEqual(AppSettings().last_port, "")


class TestAppSettingsPersistence(unittest.TestCase):
    def setUp(self):
        import tempfile

        self._tmpdir = tempfile.mkdtemp()
        self._cfg = Path(self._tmpdir) / "settings.json"

    def _patched_load(self):
        with patch("settings._PATH", self._cfg):
            return AppSettings.load()

    def _patched_save(self, s: AppSettings):
        with patch("settings._PATH", self._cfg):
            s.save()

    def test_load_missing_file_returns_defaults(self):
        s = self._patched_load()
        self.assertEqual(s, AppSettings())

    def test_save_creates_file(self):
        self._patched_save(AppSettings(lang="en"))
        self.assertTrue(self._cfg.exists())

    def test_save_writes_correct_json(self):
        self._patched_save(AppSettings(lang="en"))
        data = json.loads(self._cfg.read_text())
        self.assertEqual(data["lang"], "en")

    def test_roundtrip(self):
        original = AppSettings(
            lang="en",
            poll_sec=2.5,
            last_port="/dev/tty0",
            max_points=500,
            infinite=False,
            skip_repeat=True,
        )
        self._patched_save(original)
        loaded = self._patched_load()
        self.assertEqual(loaded, original)

    def test_partial_json_keeps_defaults(self):
        self._cfg.write_text(json.dumps({"lang": "en"}))
        s = self._patched_load()
        self.assertEqual(s.lang, "en")
        self.assertEqual(s.poll_sec, 4.0)

    def test_unknown_keys_are_ignored(self):
        self._cfg.write_text(json.dumps({"lang": "uk", "future_key": 99}))
        s = self._patched_load()
        self.assertEqual(s.lang, "uk")
        self.assertFalse(hasattr(s, "future_key"))

    def test_invalid_json_returns_defaults(self):
        self._cfg.write_text("not json {{{")
        s = self._patched_load()
        self.assertEqual(s, AppSettings())


if __name__ == "__main__":
    unittest.main()
