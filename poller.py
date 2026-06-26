"""Background poll worker: reads device measurements and puts them on a queue."""

import logging
import queue
import threading
from dataclasses import dataclass
from datetime import datetime

from device import UDP1306C

log = logging.getLogger(__name__)


@dataclass
class Sample:
    ts: datetime
    voltage: float
    current: float
    power: float
    mode: str
    output: bool
    ovp: bool
    ocp: bool


@dataclass
class PollError:
    message: str


class PollWorker:
    def __init__(self, device: UDP1306C, out: queue.Queue, interval: float) -> None:
        self._device = device
        self._out = out
        self._interval = interval
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    @property
    def interval(self) -> float:
        return self._interval

    @interval.setter
    def interval(self, value: float) -> None:
        self._interval = value

    def start(self) -> None:
        self._thread.start()

    def stop(self, timeout: float = 5.0) -> None:
        self._stop.set()
        self._thread.join(timeout=timeout)

    def _run(self) -> None:
        log.debug("Poll thread started")
        while not self._stop.is_set():
            try:
                v = self._device.measure_voltage()
                a = self._device.measure_current()
                w = self._device.measure_power()
                st = self._device.status()
                log.debug("Poll: %.2f V  %.3f A  %.1f W  %s", v, a, w, st["mode"])
                self._out.put(
                    Sample(
                        ts=datetime.now(),
                        voltage=v,
                        current=a,
                        power=w,
                        mode=st["mode"],
                        output=st.get("output", False),
                        ovp=st.get("ovp", False),
                        ocp=st.get("ocp", False),
                    )
                )
            except Exception:
                log.exception("Poll error")
                self._out.put(PollError("Poll error — see terminal"))
                break
            self._stop.wait(self._interval)
        log.debug("Poll thread stopped")
