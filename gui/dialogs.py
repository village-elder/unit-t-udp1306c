"""Modal dialogs: ConnectDialog and OptionsDialog."""

import dataclasses
import tkinter as tk
from tkinter import ttk

import serial.tools.list_ports

from i18n import LANG_NAMES, Translator
from settings import AppSettings


class ConnectDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, t: Translator) -> None:
        super().__init__(parent)
        self.result: str | None = None
        self.title(t("conn_title"))
        self.resizable(False, False)

        ports = [p.device for p in serial.tools.list_ports.comports()]
        f = tk.Frame(self, padx=14, pady=10)
        f.pack()

        tk.Label(f, text=t("conn_port")).grid(row=0, column=0, sticky="w")
        self._pv = tk.StringVar(value=ports[0] if ports else "")
        ttk.Combobox(f, textvariable=self._pv, values=ports, width=24).grid(
            row=0, column=1, padx=(8, 0)
        )

        bf = tk.Frame(f)
        bf.grid(row=1, column=0, columnspan=2, pady=(12, 0))
        tk.Button(bf, text=t("ok"), width=9, command=self._ok).pack(side="left", padx=4)
        tk.Button(bf, text=t("cancel"), width=9, command=self.destroy).pack(
            side="left", padx=4
        )

        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def _ok(self) -> None:
        self.result = self._pv.get()
        self.destroy()


class OptionsDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, t: Translator, settings: AppSettings) -> None:
        super().__init__(parent)
        self._settings = settings
        self.result: AppSettings | None = None
        self.title(t("opt_title"))
        self.resizable(False, False)

        f = tk.Frame(self, padx=14, pady=10)
        f.pack()

        tk.Label(f, text=t("opt_points")).grid(row=0, column=0, sticky="w")
        self._pts = tk.IntVar(value=settings.max_points)
        tk.Spinbox(f, textvariable=self._pts, from_=100, to=1_000_000, width=8).grid(
            row=0, column=1, padx=4
        )
        self._inf = tk.BooleanVar(value=settings.infinite)
        tk.Checkbutton(f, text=t("opt_infinite"), variable=self._inf).grid(
            row=0, column=2
        )

        tk.Label(f, text=t("opt_poll")).grid(row=1, column=0, sticky="w", pady=(6, 0))
        self._poll = tk.DoubleVar(value=settings.poll_sec)
        tk.Spinbox(
            f,
            textvariable=self._poll,
            from_=0.5,
            to=60.0,
            increment=0.5,
            format="%.1f",
            width=8,
        ).grid(row=1, column=1, padx=4)

        self._skip = tk.BooleanVar(value=settings.skip_repeat)
        tk.Checkbutton(f, text=t("opt_skip"), variable=self._skip).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(6, 0)
        )

        tk.Label(f, text=t("opt_lang")).grid(row=3, column=0, sticky="w", pady=(6, 0))
        self._lang_var = tk.StringVar(value=LANG_NAMES[settings.lang])
        ttk.Combobox(
            f,
            textvariable=self._lang_var,
            values=list(LANG_NAMES.values()),
            width=14,
            state="readonly",
        ).grid(row=3, column=1, columnspan=2, sticky="w", padx=4, pady=(6, 0))

        bf = tk.Frame(f)
        bf.grid(row=4, column=0, columnspan=3, pady=(12, 0))
        tk.Button(bf, text=t("ok"), width=9, command=self._ok).pack(side="left", padx=4)
        tk.Button(bf, text=t("cancel"), width=9, command=self.destroy).pack(
            side="left", padx=4
        )

        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def _ok(self) -> None:
        selected = self._lang_var.get()
        lang = next(k for k, v in LANG_NAMES.items() if v == selected)
        # dataclasses.replace preserves fields we don't show (e.g. last_port)
        self.result = dataclasses.replace(
            self._settings,
            lang=lang,
            max_points=self._pts.get(),
            infinite=self._inf.get(),
            skip_repeat=self._skip.get(),
            poll_sec=self._poll.get(),
        )
        self.destroy()
