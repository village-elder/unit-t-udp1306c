"""Unit tests for device.py (serial.Serial mocked)."""

import unittest
from unittest.mock import MagicMock, patch

import device as dev_module
from device import UDP1306C


class TestUDP1306C(unittest.TestCase):
    """Base: patches serial.Serial and time.sleep for every test."""

    def setUp(self):
        self._sleep_p = patch("device.time.sleep")
        self._sleep_p.start()

        self._serial_p = patch("device.serial.Serial")
        mock_cls = self._serial_p.start()
        self._ser = MagicMock()
        self._ser.is_open = True
        self._ser.readline.return_value = b"OK\n"
        mock_cls.return_value = self._ser
        self.dev = UDP1306C("/dev/ttyUSB0")

    def tearDown(self):
        self._sleep_p.stop()
        self._serial_p.stop()

    def _respond(self, value: bytes):
        """Set next readline response."""
        self._ser.readline.return_value = value


class TestConstructorAndClose(TestUDP1306C):
    def test_opens_serial_with_correct_params(self):
        import device as dm

        dm.serial.Serial.assert_called_once_with(
            port="/dev/ttyUSB0",
            baudrate=9600,
            bytesize=dm.serial.EIGHTBITS,
            parity=dm.serial.PARITY_NONE,
            stopbits=dm.serial.STOPBITS_ONE,
            timeout=3.0,
        )

    def test_close_calls_serial_close(self):
        self.dev.close()
        self._ser.close.assert_called_once()

    def test_close_skipped_when_already_closed(self):
        self._ser.is_open = False
        self.dev.close()
        self._ser.close.assert_not_called()


class TestSend(TestUDP1306C):
    def test_writes_command_with_newline(self):
        self.dev._send("OUTPut ON")
        self._ser.write.assert_called_with(b"OUTPut ON\n")

    def test_resets_input_buffer(self):
        self.dev._send("OUTPut OFF")
        self._ser.reset_input_buffer.assert_called()


class TestQuery(TestUDP1306C):
    def test_returns_stripped_response(self):
        self._respond(b"  5.000  \n")
        self.assertEqual(self.dev._query("VOLTage?"), "5.000")

    def test_raises_on_empty_response(self):
        self._respond(b"")
        with self.assertRaises(IOError):
            self.dev._query("VOLTage?")

    def test_raises_on_whitespace_only(self):
        self._respond(b"   \n")
        with self.assertRaises(IOError):
            self.dev._query("VOLTage?")


class TestIdentity(TestUDP1306C):
    def test_idn_command(self):
        self._respond(b"UNI-T,UDP1306C,v1.0\n")
        result = self.dev.idn()
        self._ser.write.assert_called_with(b"*IDN?\n")
        self.assertEqual(result, "UNI-T,UDP1306C,v1.0")

    def test_version_command(self):
        self._respond(b"1.2.3\n")
        self.dev.version()
        self._ser.write.assert_called_with(b"SYSTem:VERSion?\n")

    def test_error_command(self):
        self._respond(b"0,No error\n")
        result = self.dev.error()
        self._ser.write.assert_called_with(b"SYSTem:ERRor?\n")
        self.assertEqual(result, "0,No error")


class TestStatus(TestUDP1306C):
    _CASES = [
        (
            "00",
            {"raw": "00", "mode": "CV", "output": False, "ovp": False, "ocp": False},
        ),
        (
            "01",
            {"raw": "01", "mode": "CC", "output": False, "ovp": False, "ocp": False},
        ),
        ("02", {"raw": "02", "mode": "CV", "output": True, "ovp": False, "ocp": False}),
        ("04", {"raw": "04", "mode": "CV", "output": False, "ovp": True, "ocp": False}),
        ("08", {"raw": "08", "mode": "CV", "output": False, "ovp": False, "ocp": True}),
        ("0F", {"raw": "0F", "mode": "CC", "output": True, "ovp": True, "ocp": True}),
    ]

    def test_bit_parsing(self):
        for raw, expected in self._CASES:
            with self.subTest(raw=raw):
                self._respond((raw + "\n").encode())
                self.assertEqual(self.dev.status(), expected)

    def test_invalid_hex_returns_error(self):
        self._respond(b"ZZZZ\n")
        result = self.dev.status()
        self.assertTrue(result.get("error"))


class TestVoltageCurrentCommands(TestUDP1306C):
    def test_set_voltage_format(self):
        self.dev.set_voltage(5.1)
        self._ser.write.assert_called_with(b"VOLTage 5.100\n")

    def test_get_voltage_set(self):
        self._respond(b"12.500\n")
        self.assertAlmostEqual(self.dev.get_voltage_set(), 12.5)

    def test_set_current_format(self):
        self.dev.set_current(1.234)
        self._ser.write.assert_called_with(b"CURRent 1.234\n")

    def test_get_current_set(self):
        self._respond(b"3.000\n")
        self.assertAlmostEqual(self.dev.get_current_set(), 3.0)


class TestMeasurements(TestUDP1306C):
    def test_measure_voltage(self):
        self._respond(b"12.345\n")
        self.assertAlmostEqual(self.dev.measure_voltage(), 12.345)

    def test_measure_current(self):
        self._respond(b"1.234\n")
        self.assertAlmostEqual(self.dev.measure_current(), 1.234)

    def test_measure_power(self):
        self._respond(b"15.200\n")
        self.assertAlmostEqual(self.dev.measure_power(), 15.2)


class TestOutputCommand(TestUDP1306C):
    def test_output_on(self):
        self.dev.output(True)
        self._ser.write.assert_called_with(b"OUTPut ON\n")

    def test_output_off(self):
        self.dev.output(False)
        self._ser.write.assert_called_with(b"OUTPut OFF\n")


class TestOVP(TestUDP1306C):
    def test_enable_on(self):
        self.dev.ovp_enable(True)
        self._ser.write.assert_called_with(b"OVP:STATus ON\n")

    def test_enable_off(self):
        self.dev.ovp_enable(False)
        self._ser.write.assert_called_with(b"OVP:STATus OFF\n")

    def test_set_format(self):
        self.dev.ovp_set(13.0)
        self._ser.write.assert_called_with(b"OVP:SETting 13.000\n")

    def test_get(self):
        self._respond(b"13.000\n")
        self.assertAlmostEqual(self.dev.ovp_get(), 13.0)


class TestOCP(TestUDP1306C):
    def test_enable_on(self):
        self.dev.ocp_enable(True)
        self._ser.write.assert_called_with(b"OCP:STATus ON\n")

    def test_set_format(self):
        self.dev.ocp_set(2.5)
        self._ser.write.assert_called_with(b"OCP:SETting 2.500\n")

    def test_get(self):
        self._respond(b"2.500\n")
        self.assertAlmostEqual(self.dev.ocp_get(), 2.5)


class TestMemory(TestUDP1306C):
    def test_save_valid_slots(self):
        for slot in range(1, 6):
            with self.subTest(slot=slot):
                self.dev.save(slot)
                self._ser.write.assert_called_with(f"*SAV {slot}\n".encode())

    def test_recall_valid_slots(self):
        for slot in range(1, 6):
            with self.subTest(slot=slot):
                self.dev.recall(slot)
                self._ser.write.assert_called_with(f"*RCL {slot}\n".encode())

    def test_save_invalid_slot_raises(self):
        for slot in (0, 6, -1, 99):
            with self.subTest(slot=slot):
                with self.assertRaises(AssertionError):
                    self.dev.save(slot)

    def test_recall_invalid_slot_raises(self):
        for slot in (0, 6, -1):
            with self.subTest(slot=slot):
                with self.assertRaises(AssertionError):
                    self.dev.recall(slot)


class TestFindPort(unittest.TestCase):
    def _fake_port(self, device, description="", manufacturer=""):
        p = MagicMock()
        p.device = device
        p.description = description
        p.manufacturer = manufacturer
        return p

    def test_matches_uni_t_in_description(self):
        port = self._fake_port("/dev/ttyUSB0", description="UNI-T USB Device")
        with patch("device.serial.tools.list_ports.comports", return_value=[port]):
            self.assertEqual(dev_module.find_port(), "/dev/ttyUSB0")

    def test_matches_usbmodem_device(self):
        port = self._fake_port("/dev/cu.usbmodem1234", description="CDC")
        with patch("device.serial.tools.list_ports.comports", return_value=[port]):
            self.assertEqual(dev_module.find_port(), "/dev/cu.usbmodem1234")

    def test_returns_none_when_no_match(self):
        port = self._fake_port("/dev/ttyUSB1", description="Prolific Serial")
        with patch("device.serial.tools.list_ports.comports", return_value=[port]):
            self.assertIsNone(dev_module.find_port())

    def test_returns_none_for_empty_list(self):
        with patch("device.serial.tools.list_ports.comports", return_value=[]):
            self.assertIsNone(dev_module.find_port())


if __name__ == "__main__":
    unittest.main()
