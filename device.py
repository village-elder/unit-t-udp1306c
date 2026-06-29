"""UDP1306C driver — SCPI over USB virtual serial port."""

import threading
import time
import serial
import serial.tools.list_ports

BAUD = 9600
TIMEOUT = 3.0
CMD_DELAY = 0.15


def find_port() -> str | None:
    for p in serial.tools.list_ports.comports():
        desc = (p.description or "").lower()
        mfr = (p.manufacturer or "").lower()
        dev = p.device.lower()

        # Explicit UNI-T match — works on all platforms if driver reports correctly
        if any(k in desc or k in mfr for k in ("uni-t", "uni_t", "udp")):
            return p.device
        # macOS: /dev/cu.usbmodem*
        if "usbmodem" in dev:
            return p.device
        # Linux: /dev/ttyACM* (USB CDC class)
        if "ttyacm" in dev:
            return p.device
        # Windows: COMx with USB CDC descriptor
        if dev.startswith("com") and "cdc" in desc:
            return p.device

    return None


class UDP1306C:
    def __init__(self, port: str, baud: int = BAUD, timeout: float = TIMEOUT):
        self.ser = serial.Serial(
            port=port,
            baudrate=baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
        )
        self._lock = threading.Lock()
        time.sleep(0.5)

    def close(self):
        if self.ser.is_open:
            self.ser.close()

    def _send(self, cmd: str) -> None:
        with self._lock:
            self.ser.reset_input_buffer()
            self.ser.write((cmd + "\n").encode())
            time.sleep(CMD_DELAY)

    def _query(self, cmd: str) -> str:
        with self._lock:
            self.ser.reset_input_buffer()
            self.ser.write((cmd + "\n").encode())
            time.sleep(CMD_DELAY)
            response = self.ser.readline().decode("ascii", errors="replace").strip()
        if not response:
            raise IOError(f"No response to '{cmd}' (timeout)")
        return response

    # ── identity ──────────────────────────────────────────────────────────────

    def idn(self) -> str:
        return self._query("*IDN?")

    def version(self) -> str:
        return self._query("SYSTem:VERSion?")

    def error(self) -> str:
        return self._query("SYSTem:ERRor?")

    def status(self) -> dict:
        raw = self._query("SYSTem:STATus?")
        try:
            bits = int(raw, 16)
        except ValueError:
            return {"raw": raw, "error": True}
        return {
            "raw": raw,
            "mode": "CC" if bits & 0x01 else "CV",
            "output": bool(bits & 0x02),
            "ovp": bool(bits & 0x04),
            "ocp": bool(bits & 0x08),
        }

    # ── source ────────────────────────────────────────────────────────────────

    def set_voltage(self, v: float) -> None:
        self._send(f"VOLTage {v:.3f}")

    def get_voltage_set(self) -> float:
        return float(self._query("VOLTage?"))

    def set_current(self, a: float) -> None:
        self._send(f"CURRent {a:.3f}")

    def get_current_set(self) -> float:
        return float(self._query("CURRent?"))

    # ── measurements ──────────────────────────────────────────────────────────

    def measure_voltage(self) -> float:
        return float(self._query("MEASure:VOLTage?"))

    def measure_current(self) -> float:
        return float(self._query("MEASure:CURRent?"))

    def measure_power(self) -> float:
        return float(self._query("MEASure:POWEr?"))

    # ── output ────────────────────────────────────────────────────────────────

    def output(self, on: bool) -> None:
        self._send(f"OUTPut {'ON' if on else 'OFF'}")

    # ── OVP ──────────────────────────────────────────────────────────────────

    def ovp_enable(self, on: bool) -> None:
        self._send(f"OVP:STATus {'ON' if on else 'OFF'}")

    def ovp_set(self, v: float) -> None:
        self._send(f"OVP:SETting {v:.3f}")

    def ovp_get(self) -> float:
        return float(self._query("OVP:VALUE?"))

    # ── OCP ──────────────────────────────────────────────────────────────────

    def ocp_enable(self, on: bool) -> None:
        self._send(f"OCP:STATus {'ON' if on else 'OFF'}")

    def ocp_set(self, a: float) -> None:
        self._send(f"OCP:SETting {a:.3f}")

    def ocp_get(self) -> float:
        return float(self._query("OCP:VALUE?"))

    # ── memory ────────────────────────────────────────────────────────────────

    def save(self, slot: int) -> None:
        assert 1 <= slot <= 5, "Slot must be 1-5"
        self._send(f"*SAV {slot}")

    def recall(self, slot: int) -> None:
        assert 1 <= slot <= 5, "Slot must be 1-5"
        self._send(f"*RCL {slot}")
