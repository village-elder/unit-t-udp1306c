"""Memory slots (M1–M5), OVP, OCP and OUTPUT controls."""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from gui.widgets import C_GRN, Debounce, HoldButton, I_MAX, V_MAX
from i18n import Translator


class MemCtrlPanel(ttk.Frame):
    """Left column: M1–M5 hold-buttons.
    Right column: OVP toggle + value, OCP toggle + value, OUTPUT toggle.

    All user actions are forwarded via callbacks; the panel never talks to
    the device directly.
    """

    def __init__(
        self,
        parent: tk.Widget,
        t: Translator,
        *,
        on_recall: Callable[[int], None],
        on_save: Callable[[int], None],
        on_ovp_toggle: Callable[[], None],
        on_ocp_toggle: Callable[[], None],
        on_output_toggle: Callable[[], None],
        on_ovp_value: Callable[[float], None],
        on_ocp_value: Callable[[float], None],
    ) -> None:
        super().__init__(parent)
        self._dbc = Debounce(self)
        self._on_ovp_val = on_ovp_value
        self._on_ocp_val = on_ocp_value

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        for i in range(1, 6):
            HoldButton(
                self,
                text=f"M{i}",
                width=5,
                on_short=lambda s=i: on_recall(s),
                on_long=lambda s=i: on_save(s),
            ).grid(row=i - 1, column=0, padx=4, pady=2, sticky="ew")

        # OVP
        self._ovp_btn = tk.Button(self, text="OVP", command=on_ovp_toggle)
        self._ovp_btn.grid(row=0, column=1, padx=4, pady=2, sticky="ew")

        self._ovp_val = tk.DoubleVar(value=0.0)
        ovp_sp = tk.Spinbox(
            self,
            textvariable=self._ovp_val,
            from_=0.0,
            to=V_MAX,
            increment=0.01,
            format="%.2f",
            width=8,
        )
        ovp_sp.grid(row=1, column=1, padx=4, pady=2, sticky="ew")
        ovp_sp.config(command=self._fire_ovp)
        ovp_sp.bind("<Return>", lambda e: self._fire_ovp())
        ovp_sp.bind("<FocusOut>", lambda e: self._fire_ovp())

        # OCP
        self._ocp_btn = tk.Button(self, text="OCP", command=on_ocp_toggle)
        self._ocp_btn.grid(row=2, column=1, padx=4, pady=2, sticky="ew")

        self._ocp_val = tk.DoubleVar(value=0.0)
        ocp_sp = tk.Spinbox(
            self,
            textvariable=self._ocp_val,
            from_=0.0,
            to=I_MAX,
            increment=0.001,
            format="%.3f",
            width=8,
        )
        ocp_sp.grid(row=3, column=1, padx=4, pady=2, sticky="ew")
        ocp_sp.config(command=self._fire_ocp)
        ocp_sp.bind("<Return>", lambda e: self._fire_ocp())
        ocp_sp.bind("<FocusOut>", lambda e: self._fire_ocp())

        # OUTPUT
        self._out_btn = tk.Button(self, text="OUTPUT", command=on_output_toggle)
        self._out_btn.grid(row=4, column=1, padx=4, pady=2, sticky="ew")

        self._btn_bg = self._ovp_btn.cget("bg")

    def _fire_ovp(self) -> None:
        self._dbc("ovp", lambda: self._on_ovp_val(round(self._ovp_val.get(), 2)))

    def _fire_ocp(self) -> None:
        self._dbc("ocp", lambda: self._on_ocp_val(round(self._ocp_val.get(), 3)))

    def set_states(self, *, ovp: bool, ocp: bool, output: bool) -> None:
        self._ovp_btn.config(bg=C_GRN if ovp else self._btn_bg)
        self._ocp_btn.config(bg=C_GRN if ocp else self._btn_bg)
        self._out_btn.config(bg=C_GRN if output else self._btn_bg)

    def set_ovp_val(self, v: float) -> None:
        self._ovp_val.set(round(v, 2))

    def set_ocp_val(self, a: float) -> None:
        self._ocp_val.set(round(a, 3))

    def apply_lang(self, strings: dict) -> None:
        pass  # OVP / OCP / OUTPUT are fixed technical labels
