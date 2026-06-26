"""Main application window — wires panels together, manages device lifecycle."""

import logging
import queue
import tkinter as tk
from tkinter import messagebox
from typing import Callable

from device import UDP1306C
from i18n import Translator
from poller import PollError, PollWorker, Sample
from settings import AppSettings

from gui.dialogs import ConnectDialog, OptionsDialog
from gui.panels.chart import ChartPanel
from gui.panels.datalog import DataLogPanel
from gui.panels.display import DisplayPanel
from gui.panels.memctrl import MemCtrlPanel
from gui.panels.setpoint import SetpointPanel

log = logging.getLogger(__name__)


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("UNI-T UDP1306C Power Supply")
        self.minsize(960, 680)

        self._settings = AppSettings.load()
        self._t = Translator(self._settings.lang)
        self._device: UDP1306C | None = None
        self._poller: PollWorker | None = None
        self._queue: queue.Queue = queue.Queue()

        # device output state — updated from each Sample, used for toggles
        self._output = False
        self._ovp = False
        self._ocp = False
        self._last_meas: tuple | None = None

        self._build_ui()
        self._drain_id = self.after(200, self._drain)
        self.protocol("WM_DELETE_WINDOW", self._close)
        log.info("Application started")

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        t = self._t
        self._toolbar_i18n: list[tuple[tk.Button, str]] = []
        self._build_toolbar(t)

        mid = tk.Frame(self)
        mid.pack(fill="both", expand=True, padx=6, pady=6)

        left = tk.Frame(mid, width=310)
        left.pack(side="left", fill="y", padx=(0, 6))
        left.pack_propagate(False)

        self._display = DisplayPanel(left)
        self._display.pack(fill="x", pady=(0, 6))

        self._setpoint = SetpointPanel(
            left,
            t,
            on_voltage=lambda v: self._cmd(self._device.set_voltage, v),
            on_current=lambda a: self._cmd(self._device.set_current, a),
        )
        self._setpoint.pack(fill="x")

        self._memctrl = MemCtrlPanel(
            left,
            t,
            on_recall=self._recall,
            on_save=self._save_slot,
            on_ovp_toggle=self._toggle_ovp,
            on_ocp_toggle=self._toggle_ocp,
            on_output_toggle=self._toggle_output,
            on_ovp_value=lambda v: self._cmd(self._device.ovp_set, v),
            on_ocp_value=lambda a: self._cmd(self._device.ocp_set, a),
        )
        self._memctrl.pack(fill="x", pady=(4, 0))

        right = tk.Frame(mid)
        right.pack(side="left", fill="both", expand=True)

        self._chart = ChartPanel(
            right,
            t,
            max_points=self._settings.max_points,
            infinite=self._settings.infinite,
        )
        self._chart.pack(fill="both", expand=True)

        self._datalog = DataLogPanel(self, t, on_clear=self._chart.clear)
        self._datalog.pack(fill="x", padx=6, pady=(0, 6))

        self._panels = [
            self._display,
            self._setpoint,
            self._memctrl,
            self._chart,
            self._datalog,
        ]

    def _build_toolbar(self, t: Translator) -> None:
        tb = tk.Frame(self, relief="raised", bd=1)
        tb.pack(fill="x")

        def _btn(
            text_key: str, cmd: Callable, side: str = "left", state: str = "normal"
        ) -> tk.Button:
            b = tk.Button(tb, text=t(text_key), command=cmd, state=state)
            b.pack(side=side, padx=4, pady=3)
            self._toolbar_i18n.append((b, text_key))
            return b

        self._btn_conn = _btn("connect", self._connect)
        self._btn_disc = _btn("disconnect", self._disconnect, state="disabled")
        _btn("close", self._close, side="right")
        _btn("options", self._open_options, side="right")

    # ── connection ────────────────────────────────────────────────────────────

    def _connect(self) -> None:
        dlg = ConnectDialog(self, self._t)
        if not dlg.result:
            return
        port = dlg.result
        log.info("Connecting to %s ...", port)
        try:
            self._device = UDP1306C(port)
        except Exception:
            log.exception("Connection failed")
            messagebox.showerror(self._t("err_conn"), self._t("err_conn_msg"))
            return

        # Verify this port is actually the PSU before starting the poller.
        try:
            st = self._device.status()
        except Exception:
            log.exception("Device did not respond — wrong port?")
            messagebox.showerror(self._t("err_conn"), self._t("err_conn_msg"))
            self._device.close()
            self._device = None
            return

        self._output = st.get("output", False)
        self._ovp = st.get("ovp", False)
        self._ocp = st.get("ocp", False)
        self._memctrl.set_states(ovp=self._ovp, ocp=self._ocp, output=self._output)

        try:
            self._setpoint.set_voltage(self._device.get_voltage_set())
            self._setpoint.set_current(self._device.get_current_set())
            self._memctrl.set_ovp_val(self._device.ovp_get())
            self._memctrl.set_ocp_val(self._device.ocp_get())
            log.info("Connected. IDN: %s", self._device.idn())
        except Exception:
            log.warning("Some initial readbacks failed (non-critical)", exc_info=True)

        self._settings.last_port = port
        self._btn_conn.config(state="disabled")
        self._btn_disc.config(state="normal")

        self._poller = PollWorker(self._device, self._queue, self._settings.poll_sec)
        self._poller.start()

    def _disconnect(self) -> None:
        log.info("Disconnecting ...")
        if self._poller:
            self._poller.stop()
            self._poller = None
        if self._device:
            self._device.close()
            self._device = None
        self._display.reset()
        self._btn_conn.config(state="normal")
        self._btn_disc.config(state="disabled")
        log.info("Disconnected")

    # ── poll drain ────────────────────────────────────────────────────────────

    def _drain(self) -> None:
        try:
            while True:
                event = self._queue.get_nowait()
                if isinstance(event, Sample):
                    self._on_sample(event)
                elif isinstance(event, PollError):
                    messagebox.showerror(self._t("err_device"), event.message)
                    self._disconnect()
        except queue.Empty:
            pass
        self._drain_id = self.after(200, self._drain)

    def _on_sample(self, sample: Sample) -> None:
        meas = (sample.voltage, sample.current, sample.power)
        if self._settings.skip_repeat and meas == self._last_meas:
            return
        self._last_meas = meas

        self._output = sample.output
        self._ovp = sample.ovp
        self._ocp = sample.ocp

        self._display.update(sample)
        self._memctrl.set_states(ovp=self._ovp, ocp=self._ocp, output=self._output)
        self._chart.add_sample(sample)
        self._datalog.add_sample(sample)

    # ── device commands ───────────────────────────────────────────────────────

    def _cmd(self, fn: Callable, *args) -> bool:
        """Run a device command; log any error. Returns True on success."""
        if not self._device:
            return False
        try:
            fn(*args)
            return True
        except Exception:
            log.exception("Device command failed")
            messagebox.showerror("Error", "Command failed — see terminal")
            return False

    def _toggle_output(self) -> None:
        new = not self._output
        if self._cmd(self._device.output, new):
            self._output = new
            self._memctrl.set_states(ovp=self._ovp, ocp=self._ocp, output=self._output)
            log.info("OUTPUT → %s", "ON" if new else "OFF")

    def _toggle_ovp(self) -> None:
        new = not self._ovp
        if self._cmd(self._device.ovp_enable, new):
            self._ovp = new
            self._memctrl.set_states(ovp=self._ovp, ocp=self._ocp, output=self._output)
            log.info("OVP → %s", "ON" if new else "OFF")

    def _toggle_ocp(self) -> None:
        new = not self._ocp
        if self._cmd(self._device.ocp_enable, new):
            self._ocp = new
            self._memctrl.set_states(ovp=self._ovp, ocp=self._ocp, output=self._output)
            log.info("OCP → %s", "ON" if new else "OFF")

    def _recall(self, slot: int) -> None:
        if not self._cmd(self._device.recall, slot):
            return
        try:
            self._setpoint.set_voltage(self._device.get_voltage_set())
            self._setpoint.set_current(self._device.get_current_set())
            log.info("Recalled M%d", slot)
        except Exception:
            log.exception("Readback after recall M%d failed", slot)

    def _save_slot(self, slot: int) -> None:
        if self._cmd(self._device.save, slot):
            log.info("Saved to M%d", slot)

    # ── options ───────────────────────────────────────────────────────────────

    def _open_options(self) -> None:
        dlg = OptionsDialog(self, self._t, self._settings)
        if not dlg.result:
            return

        old_lang = self._settings.lang
        self._settings = dlg.result
        self._settings.save()

        if self._poller:
            self._poller.interval = self._settings.poll_sec
        self._chart.configure(self._settings.max_points, self._settings.infinite)

        if self._settings.lang != old_lang:
            self._t.lang = self._settings.lang
            self._apply_lang()
            log.info("Language → %s", self._settings.lang)

    def _apply_lang(self) -> None:
        strings = self._t.strings()
        for btn, key in self._toolbar_i18n:
            btn.config(text=strings[key])
        for panel in self._panels:
            panel.apply_lang(strings)

    # ── close ────────────────────────────────────────────────────────────────

    def _close(self) -> None:
        if self._device:
            self._disconnect()
        self.after_cancel(self._drain_id)
        self.destroy()
