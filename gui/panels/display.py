"""LCD-style measurement display panel."""

import tkinter as tk
from tkinter import ttk

from gui.widgets import C_BG, C_CYN, C_DIM, C_GRN, C_RED
from poller import Sample


class DisplayPanel(ttk.Frame):
    """Shows live voltage, current, power, mode, and output state."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        f = tk.Frame(self, bg=C_BG, bd=2, relief="sunken")
        f.pack(fill="x")

        BIG = ("Courier", 36, "bold")
        MED = ("Courier", 18, "bold")
        SM = ("Courier", 11, "bold")

        self._mode_lbl = tk.Label(f, text="---", font=SM, bg=C_BG, fg=C_CYN, anchor="w")
        self._mode_lbl.pack(fill="x", padx=10, pady=(6, 0))

        for attr, unit, font, fg in [
            ("_v_lbl", "V", BIG, C_RED),
            ("_a_lbl", "A", BIG, C_CYN),
            ("_w_lbl", "W", MED, C_CYN),
        ]:
            row = tk.Frame(f, bg=C_BG)
            row.pack(fill="x", padx=8)
            lbl = tk.Label(
                row, text="------", font=font, bg=C_BG, fg=fg, width=7, anchor="e"
            )
            lbl.pack(side="left")
            tk.Label(row, text=f" {unit}", font=font, bg=C_BG, fg=fg).pack(side="left")
            setattr(self, attr, lbl)

        self._out_lbl = tk.Label(f, text="OFF", font=SM, bg=C_BG, fg=C_DIM, anchor="e")
        self._out_lbl.pack(fill="x", padx=10, pady=(0, 6))

    def update(self, sample: Sample) -> None:
        self._v_lbl.config(text=f"{sample.voltage:7.2f}")
        self._a_lbl.config(text=f"{sample.current:7.3f}")
        self._w_lbl.config(text=f"{sample.power:7.1f}")
        self._mode_lbl.config(text=sample.mode)
        on = sample.output
        self._out_lbl.config(text="ON" if on else "OFF", fg=C_GRN if on else C_DIM)

    def reset(self) -> None:
        for lbl in (self._v_lbl, self._a_lbl, self._w_lbl):
            lbl.config(text="------")
        self._mode_lbl.config(text="---")
        self._out_lbl.config(text="OFF", fg=C_DIM)

    def apply_lang(self, strings: dict) -> None:
        pass  # display values are numeric / universal (CV/CC)
