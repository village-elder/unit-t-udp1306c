"""Real-time chart panel (matplotlib) with channel selector and image export."""

import tkinter as tk
from collections import deque
from datetime import datetime
from tkinter import filedialog
from typing import Callable

import matplotlib

matplotlib.use("TkAgg")
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from i18n import Translator
from poller import Sample

# Internal channel key → (i18n string key, SI unit)
_CH = {
    "Voltage": ("ch_voltage", "V"),
    "Current": ("ch_current", "A"),
    "Power": ("ch_power", "W"),
}


class _DataSeries:
    """Four parallel deques kept in sync."""

    def __init__(self) -> None:
        self.times: deque = deque()
        self.volts: deque = deque()
        self.amps: deque = deque()
        self.watts: deque = deque()

    def append(self, ts: datetime, v: float, a: float, w: float) -> None:
        self.times.append(ts)
        self.volts.append(v)
        self.amps.append(a)
        self.watts.append(w)

    def clear(self) -> None:
        self.times.clear()
        self.volts.clear()
        self.amps.clear()
        self.watts.clear()

    def __len__(self) -> int:
        return len(self.times)

    def by_channel(self, ch: str) -> deque:
        return {"Voltage": self.volts, "Current": self.amps, "Power": self.watts}[ch]


class ChartPanel(tk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        t: Translator,
        max_points: int = 10_000,
        infinite: bool = True,
    ) -> None:
        super().__init__(parent)
        self._t = t
        self._max_points = max_points
        self._infinite = infinite
        self._series = _DataSeries()
        self._i18n: list[Callable] = []
        self._build()

    def _build(self) -> None:
        sel = tk.Frame(self)
        sel.pack(fill="x")

        self._ch = tk.StringVar(value="Voltage")
        for ch_key, str_key in _CH.items():
            rb = tk.Radiobutton(
                sel,
                text=self._t(str_key[0]),
                variable=self._ch,
                value=ch_key,
                command=self._redraw,
            )
            rb.pack(side="left", padx=8)
            self._i18n.append(lambda d, w=rb, k=str_key[0]: w.config(text=d[k]))

        btn = tk.Button(sel, text=self._t("save_image"), command=self._save)
        btn.pack(side="right", padx=6)
        self._i18n.append(lambda d, w=btn: w.config(text=d["save_image"]))

        self._fig = Figure(tight_layout=True)
        self._ax = self._fig.add_subplot(111)
        self._ax.set_xlabel("Time")
        self._ax.grid(True, linestyle="--", alpha=0.4)
        self._ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        (self._line,) = self._ax.plot([], [], color="#2196F3", linewidth=1.2)

        canvas = FigureCanvasTkAgg(self._fig, master=self)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._canvas = canvas

    def add_sample(self, sample: Sample) -> None:
        if self._infinite or len(self._series) < self._max_points:
            self._series.append(sample.ts, sample.voltage, sample.current, sample.power)
        self._redraw()

    def clear(self) -> None:
        self._series.clear()
        self._ax.cla()
        self._ax.set_xlabel("Time")
        self._ax.grid(True, linestyle="--", alpha=0.4)
        self._ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        (self._line,) = self._ax.plot([], [], color="#2196F3", linewidth=1.2)
        self._canvas.draw_idle()

    def configure(self, max_points: int, infinite: bool) -> None:
        self._max_points = max_points
        self._infinite = infinite

    def _redraw(self) -> None:
        if not self._series.times:
            return
        ch = self._ch.get()
        str_key, unit = _CH[ch]
        self._line.set_data(list(self._series.times), list(self._series.by_channel(ch)))
        self._ax.set_ylabel(f"{self._t(str_key)} ({unit})")
        self._ax.relim()
        self._ax.autoscale_view()
        self._fig.autofmt_xdate(rotation=30)
        self._canvas.draw_idle()

    def _save(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("SVG", "*.svg"),
                ("PDF", "*.pdf"),
                ("All files", "*.*"),
            ],
            initialfile=f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        )
        if path:
            self._fig.savefig(path, dpi=150, bbox_inches="tight")

    def apply_lang(self, strings: dict) -> None:
        for fn in self._i18n:
            fn(strings)
        self._redraw()
