"""Voltage and current setpoint panel (spinbox + slider)."""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from gui.widgets import Debounce, I_MAX, V_MAX
from i18n import Translator


class SetpointPanel(ttk.Frame):
    """Two rows: VOLTAGE and CURRENT, each with spinbox + slider.

    Sends debounced values via on_voltage / on_current callbacks.
    """

    def __init__(
        self,
        parent: tk.Widget,
        t: Translator,
        *,
        on_voltage: Callable[[float], None],
        on_current: Callable[[float], None],
    ) -> None:
        super().__init__(parent)
        self._dbc = Debounce(self)
        self._i18n: list[Callable] = []

        self._v_set = tk.DoubleVar(value=0.0)
        self._i_set = tk.DoubleVar(value=0.0)

        for lf_key, var, mx, inc, fmt, ndigits, dbc_key, cb in [
            ("voltage_lf", self._v_set, V_MAX, 0.01, "%.2f", 2, "v", on_voltage),
            ("current_lf", self._i_set, I_MAX, 0.001, "%.3f", 3, "i", on_current),
        ]:
            lf = self._build_row(t, lf_key, var, mx, inc, fmt, ndigits, dbc_key, cb)
            self._i18n.append(lambda d, w=lf, k=lf_key: w.config(text=d[k]))

    def _build_row(
        self,
        t: Translator,
        lf_key: str,
        var: tk.DoubleVar,
        mx: float,
        inc: float,
        fmt: str,
        ndigits: int,
        dbc_key: str,
        cb: Callable[[float], None],
    ) -> tk.LabelFrame:
        lf = tk.LabelFrame(self, text=t(lf_key))
        lf.pack(fill="x", pady=2)

        fire = lambda: self._dbc(dbc_key, lambda: cb(round(var.get(), ndigits)))

        sp = tk.Spinbox(
            lf, textvariable=var, from_=0.0, to=mx, increment=inc, format=fmt, width=8
        )
        sp.pack(side="top", anchor="w", padx=4, pady=(2, 0))
        sp.config(command=fire)
        sp.bind("<Return>", lambda e: fire())
        sp.bind("<FocusOut>", lambda e: fire())

        sc = tk.Scale(
            lf,
            from_=0.0,
            to=mx,
            resolution=inc,
            orient="horizontal",
            variable=var,
            showvalue=False,
        )
        sc.pack(fill="x", padx=4, pady=(0, 2))
        sc.bind("<ButtonRelease-1>", lambda e: fire())

        return lf

    def set_voltage(self, v: float) -> None:
        self._v_set.set(round(v, 2))

    def set_current(self, a: float) -> None:
        self._i_set.set(round(a, 3))

    def apply_lang(self, strings: dict) -> None:
        for fn in self._i18n:
            fn(strings)
