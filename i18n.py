"""Internationalisation: string tables and Translator."""

STRINGS: dict[str, dict[str, str]] = {
    "uk": {
        "connect": "Підключити",
        "disconnect": "Відключити",
        "options": "Налаштування",
        "close": "Закрити",
        "voltage_lf": "НАПРУГА (В)",
        "current_lf": "СТРУМ (А)",
        "ch_voltage": "Напруга",
        "ch_current": "Струм",
        "ch_power": "Потужність",
        "save_image": "Зберегти",
        "data_record": "Журнал даних",
        "clear": "Очистити",
        "export": "Експорт",
        "col_no": "№",
        "col_dt": "Дата/Час",
        "col_volt": "Напруга (В)",
        "col_amp": "Струм (А)",
        "col_watt": "Потужність (Вт)",
        "col_flag": "Режим",
        "opt_title": "Налаштування",
        "opt_points": "Кількість точок:",
        "opt_infinite": "Нескінченно",
        "opt_poll": "Інтервал опитування (с):",
        "opt_skip": "Пропускати повтори",
        "opt_lang": "Мова:",
        "ok": "ОК",
        "cancel": "Скасувати",
        "conn_title": "Підключення",
        "conn_port": "Серійний порт:",
        "err_conn": "Помилка підключення",
        "err_conn_msg": "Не вдалося відкрити порт. Детальніше в терміналі.",
        "err_device": "Помилка пристрою",
        "err_poll": "Помилка опитування — дивись термінал",
        "no_data": "Нема даних для експорту.",
        "saved_rows": "Збережено {n} рядків у:\n{path}",
    },
    "en": {
        "connect": "Connect",
        "disconnect": "Disconnect",
        "options": "Options",
        "close": "Close",
        "voltage_lf": "VOLTAGE (V)",
        "current_lf": "CURRENT (A)",
        "ch_voltage": "Voltage",
        "ch_current": "Current",
        "ch_power": "Power",
        "save_image": "Save image",
        "data_record": "Data Record",
        "clear": "Clear",
        "export": "Export",
        "col_no": "No.",
        "col_dt": "Date/Time",
        "col_volt": "Voltage (V)",
        "col_amp": "Current (A)",
        "col_watt": "Power (W)",
        "col_flag": "Flag",
        "opt_title": "Options",
        "opt_points": "Sample points:",
        "opt_infinite": "Infinite",
        "opt_poll": "Poll interval (s):",
        "opt_skip": "Skip repeated readings",
        "opt_lang": "Language:",
        "ok": "OK",
        "cancel": "Cancel",
        "conn_title": "Connect",
        "conn_port": "Serial port:",
        "err_conn": "Connection error",
        "err_conn_msg": "Could not open port. See terminal for details.",
        "err_device": "Device error",
        "err_poll": "Poll error — see terminal",
        "no_data": "No data to export.",
        "saved_rows": "Saved {n} rows to:\n{path}",
    },
}

LANG_NAMES: dict[str, str] = {"uk": "Українська", "en": "English"}


class Translator:
    """Callable that returns translated strings for the current language.

    Shared across all panels; updating `.lang` takes effect immediately
    for any dynamic string lookups (error messages, export headers, etc.).
    Static widget text must be refreshed via `panel.apply_lang(t.strings())`.
    """

    def __init__(self, lang: str = "uk") -> None:
        self.lang = lang

    @property
    def lang(self) -> str:
        return self._lang

    @lang.setter
    def lang(self, value: str) -> None:
        if value not in STRINGS:
            raise ValueError(f"Unknown language: {value!r}")
        self._lang = value

    def __call__(self, key: str) -> str:
        return STRINGS[self._lang][key]

    def strings(self) -> dict[str, str]:
        """Return the full string table for the current language."""
        return STRINGS[self._lang]
