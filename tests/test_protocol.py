"""Exercise the AVON exchange using simulated TCP streams."""

import asyncio
import importlib.util
import json
from pathlib import Path
import struct
import unittest
from unittest.mock import AsyncMock, Mock, patch

spec = importlib.util.spec_from_file_location(
    "tb40_protocol",
    Path(__file__).resolve().parents[1] / "custom_components/novastar_tb40/protocol.py",
)
protocol = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protocol)


class TestProtocol(unittest.IsolatedAsyncioTestCase):
    def test_prepare_frame(self):
        self.assertEqual(
            protocol.packet(2, protocol.PREPARE),
            bytes.fromhex("41564f4e0200000051522100050400000000000000000302"),
        )

    async def test_three_commands(self):
        reader = AsyncMock()
        reader.read.side_effect = [b"response", asyncio.TimeoutError(), b"response"]
        writer = Mock(drain=AsyncMock())
        with patch.object(asyncio, "open_connection", return_value=(reader, writer)) as connect:
            await protocol.set_brightness("example.invalid", "TEST", "test", "example", 8.4)
        connect.assert_awaited_once_with("example.invalid", 16603)
        writer.close.assert_called_once()
        received = []
        for call in writer.write.call_args_list:
            (frame,) = call.args
            self.assertEqual(struct.unpack_from("<I", frame, 16)[0], len(frame) - 24)
            received.append((frame[4], frame[8:16].hex(), json.loads(frame[24:]) if frame[24:] else None))
        self.assertEqual(received, [
            (1, protocol.LOGIN, {
                "isTCard": True, "loginType": 1, "password": "example",
                "sn": "TEST", "source": {"platform": 15, "type": 0}, "username": "test",
            }),
            (2, protocol.PREPARE, None),
            (3, protocol.BRIGHTNESS, {"ratio": 8.4, "source": {"platform": 1, "type": 0}}),
        ])

    async def test_invalid_brightness_never_connects(self):
        with patch.object(asyncio, "open_connection", new_callable=AsyncMock) as connect:
            for value in (0, 101, float("nan"), float("inf")):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    await protocol.set_brightness("example.invalid", "TEST", "test", "example", value)
            connect.assert_not_called()

    async def test_connection_failure_surfaces(self):
        with patch.object(asyncio, "open_connection", side_effect=ConnectionRefusedError):
            with self.assertRaises(ConnectionRefusedError):
                await protocol.set_brightness("example.invalid", "TEST", "test", "example", 50)

    async def test_connectivity_check_sends_no_data(self):
        writer = Mock()
        with patch.object(asyncio, "open_connection", return_value=(AsyncMock(), writer)) as connect:
            await protocol.async_check_connection("example.invalid")
        connect.assert_awaited_once_with("example.invalid", 16603)
        writer.write.assert_not_called()
        writer.close.assert_called_once()

    async def test_connectivity_check_reports_refused_connection(self):
        with patch.object(asyncio, "open_connection", side_effect=ConnectionRefusedError):
            with self.assertRaises(ConnectionRefusedError):
                await protocol.async_check_connection("example.invalid")
