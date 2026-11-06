"""Local AVON commands used by the TB40 brightness script."""

import asyncio
import json
import math
import struct

PORT = 16603
LOGIN = "5152000000000000"
PREPARE = "5152210005040000"
BRIGHTNESS = "5152180004010000"


def packet(sequence, command, payload=None):
    body = b"" if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    header = struct.pack("<4sI8sI2x", b"AVON", sequence, bytes.fromhex(command), len(body))
    checksum = sum(byte if byte < 128 else byte - 256 for byte in header) & 0xFFFF
    return header + struct.pack("<H", checksum) + body


async def async_check_connection(host):
    """Check the TCP port without sending login or brightness messages."""
    _, writer = await asyncio.wait_for(asyncio.open_connection(host, PORT), 2)
    writer.close()


async def set_brightness(host, serial, username, password, value):
    """Send the legacy three-command exchange without assuming an ACK format."""
    if not math.isfinite(value) or not 1 <= value <= 100:
        raise ValueError("Brightness must be between 1 and 100 percent")
    frames = (
        packet(1, LOGIN, {
            "isTCard": True,
            "loginType": 1,
            "password": password,
            "sn": serial,
            "source": {"platform": 15, "type": 0},
            "username": username,
        }),
        packet(2, PREPARE),
        packet(3, BRIGHTNESS, {"ratio": value, "source": {"platform": 1, "type": 0}}),
    )
    reader, writer = await asyncio.wait_for(asyncio.open_connection(host, PORT), 2)
    try:
        for frame in frames:
            writer.write(frame)
            await asyncio.wait_for(writer.drain(), 0.5)
            await asyncio.sleep(0.03)
            try:
                reply = await asyncio.wait_for(reader.read(4096), 0.3)
            except asyncio.TimeoutError:
                continue
            if not reply:
                raise ConnectionError("TB40 closed the connection")
    finally:
        writer.close()
