"""Reusable tkinter widgets and helpers."""

import tkinter as tk
from typing import Callable

# ── layout constants ──────────────────────────────────────────────────────────

V_MAX = 32.0
I_MAX = 6.0
DEBOUNCE_MS = 400
LONG_PRESS_MS = 600

# ── theme colours ─────────────────────────────────────────────────────────────

C_BG = "#0d0d0d"
C_RED = "#ff3333"
C_CYN = "#00aaff"
C_GRN = "#00cc44"
C_DIM = "#666666"


# ── Debounce ──────────────────────────────────────────────────────────────────


class Debounce:
    """Cancel-and-reschedule debouncer backed by a tkinter widget's after().

    Usage:
        dbc = Debounce(self)          # self is any tk widget
        dbc("key", lambda: send(v))   # re-arms on every call
    """

    def __init__(self, widget: tk.Widget, delay_ms: int = DEBOUNCE_MS) -> None:
        self._widget = widget
        self._delay = delay_ms
        self._jobs: dict[str, str | None] = {}

    def __call__(self, key: str, callback: Callable[[], None]) -> None:
        if self._jobs.get(key):
            self._widget.after_cancel(self._jobs[key])

        def run() -> None:
            self._jobs[key] = None
            callback()

        self._jobs[key] = self._widget.after(self._delay, run)


# ── HoldButton ────────────────────────────────────────────────────────────────


class HoldButton(tk.Button):
    """Button with two actions: short click → on_short; long press → on_long."""

    def __init__(
        self,
        *args,
        on_short: Callable | None = None,
        on_long: Callable | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._short = on_short
        self._long = on_long
        self._job = None
        self._fired = False
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<ButtonRelease-1>", self._release)

    def _press(self, _: tk.Event) -> None:
        self._fired = False
        self._job = self.after(LONG_PRESS_MS, self._do_long)

    def _do_long(self) -> None:
        self._fired = True
        if self._long:
            self._long()

    def _release(self, _: tk.Event) -> None:
        if self._job:
            self.after_cancel(self._job)
            self._job = None
        if not self._fired and self._short:
            self._short()
