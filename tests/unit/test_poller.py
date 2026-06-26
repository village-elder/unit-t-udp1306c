"""Unit tests for poller.py."""

import queue
import unittest
from datetime import datetime
from unittest.mock import MagicMock

from poller import PollError, PollWorker, Sample


def _mock_device(
    voltage=5.0, current=1.0, power=5.0, mode="CV", output=False, ovp=False, ocp=False
):
    d = MagicMock()
    d.measure_voltage.return_value = voltage
    d.measure_current.return_value = current
    d.measure_power.return_value = power
    d.status.return_value = {"mode": mode, "output": output, "ovp": ovp, "ocp": ocp}
    return d


class TestDataclasses(unittest.TestCase):
    def test_sample_fields(self):
        ts = datetime.now()
        s = Sample(
            ts=ts,
            voltage=5.0,
            current=1.0,
            power=5.0,
            mode="CV",
            output=True,
            ovp=False,
            ocp=False,
        )
        self.assertAlmostEqual(s.voltage, 5.0)
        self.assertEqual(s.mode, "CV")
        self.assertTrue(s.output)

    def test_poll_error_message(self):
        self.assertEqual(PollError("timeout").message, "timeout")


class TestPollWorker(unittest.TestCase):
    def _start(self, device, interval=0.05):
        q = queue.Queue()
        w = PollWorker(device, q, interval=interval)
        w.start()
        return w, q

    def test_puts_sample_in_queue(self):
        dev = _mock_device(voltage=12.0, current=2.0, power=24.0)
        w, q = self._start(dev)
        event = q.get(timeout=2.0)
        w.stop()
        self.assertIsInstance(event, Sample)
        self.assertAlmostEqual(event.voltage, 12.0)
        self.assertAlmostEqual(event.current, 2.0)

    def test_sample_has_timestamp(self):
        before = datetime.now()
        w, q = self._start(_mock_device())
        event = q.get(timeout=2.0)
        after = datetime.now()
        w.stop()
        self.assertIsInstance(event, Sample)
        self.assertGreaterEqual(event.ts, before)
        self.assertLessEqual(event.ts, after)

    def test_propagates_status_flags(self):
        dev = _mock_device(mode="CC", output=True, ovp=True, ocp=False)
        w, q = self._start(dev)
        event = q.get(timeout=2.0)
        w.stop()
        self.assertEqual(event.mode, "CC")
        self.assertTrue(event.output)
        self.assertTrue(event.ovp)
        self.assertFalse(event.ocp)

    def test_puts_error_on_exception(self):
        dev = MagicMock()
        dev.measure_voltage.side_effect = IOError("serial timeout")
        w, q = self._start(dev)
        event = q.get(timeout=2.0)
        w.stop()
        self.assertIsInstance(event, PollError)
        self.assertIn("Poll error", event.message)

    def test_thread_exits_after_error(self):
        dev = MagicMock()
        dev.measure_voltage.side_effect = IOError("broken")
        w, q = self._start(dev)
        q.get(timeout=2.0)
        w._thread.join(timeout=2.0)
        self.assertFalse(w._thread.is_alive())

    def test_stop_joins_thread(self):
        w, _ = self._start(_mock_device())
        w.stop()
        self.assertFalse(w._thread.is_alive())

    def test_interval_change_takes_effect(self):
        w, q = self._start(_mock_device(), interval=60.0)
        w.interval = 0.05
        event = q.get(timeout=3.0)
        w.stop()
        self.assertIsInstance(event, Sample)

    def test_interval_property(self):
        dev = _mock_device()
        w = PollWorker(dev, queue.Queue(), interval=1.0)
        self.assertAlmostEqual(w.interval, 1.0)
        w.interval = 2.5
        self.assertAlmostEqual(w.interval, 2.5)


if __name__ == "__main__":
    unittest.main()
