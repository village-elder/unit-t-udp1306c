"""Unit tests for i18n.py."""

import unittest

from i18n import LANG_NAMES, STRINGS, Translator


class TestStrings(unittest.TestCase):
    def test_both_languages_have_same_keys(self):
        uk_keys = set(STRINGS["uk"])
        en_keys = set(STRINGS["en"])
        only_uk = uk_keys - en_keys
        only_en = en_keys - uk_keys
        self.assertFalse(only_uk, f"Keys only in 'uk': {only_uk}")
        self.assertFalse(only_en, f"Keys only in 'en': {only_en}")

    def test_no_empty_strings(self):
        for lang, table in STRINGS.items():
            for key, val in table.items():
                with self.subTest(lang=lang, key=key):
                    self.assertTrue(val.strip(), f"Empty value for [{lang}][{key!r}]")

    def test_lang_names_covers_all_languages(self):
        for lang in STRINGS:
            with self.subTest(lang=lang):
                self.assertIn(lang, LANG_NAMES)


class TestTranslator(unittest.TestCase):
    def test_default_language_is_uk(self):
        self.assertEqual(Translator().lang, "uk")

    def test_call_returns_correct_string(self):
        t = Translator("uk")
        self.assertEqual(t("connect"), STRINGS["uk"]["connect"])

    def test_call_en(self):
        t = Translator("en")
        self.assertEqual(t("connect"), STRINGS["en"]["connect"])

    def test_switch_language(self):
        t = Translator("uk")
        t.lang = "en"
        self.assertEqual(t.lang, "en")
        self.assertEqual(t("connect"), STRINGS["en"]["connect"])

    def test_invalid_language_raises(self):
        t = Translator()
        with self.assertRaises(ValueError):
            t.lang = "fr"

    def test_invalid_language_in_constructor_raises(self):
        with self.assertRaises(ValueError):
            Translator("de")

    def test_strings_returns_full_dict(self):
        t = Translator("en")
        self.assertEqual(t.strings(), STRINGS["en"])

    def test_strings_changes_after_lang_switch(self):
        t = Translator("uk")
        t.lang = "en"
        self.assertIs(t.strings(), STRINGS["en"])

    def test_missing_key_raises(self):
        t = Translator()
        with self.assertRaises(KeyError):
            _ = t("nonexistent_key_xyz")


if __name__ == "__main__":
    unittest.main()
