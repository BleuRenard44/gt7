from __future__ import annotations

import math
import struct
from time import time

from Crypto.Cipher import Salsa20

KEY = b"Simulator Interface Packet GT7 ver 0.0"
MAGIC = 0x47375330


class PacketDecodeError(Exception):
    pass


def f32(data: bytes, offset: int) -> float:
    return struct.unpack_from("<f", data, offset)[0]


def i32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<i", data, offset)[0]


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def i16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<h", data, offset)[0]


def u8(data: bytes, offset: int) -> int:
    return struct.unpack_from("<B", data, offset)[0]


def decrypt_packet(packet: bytes) -> bytes:
    if len(packet) < 0x128:
        raise PacketDecodeError(f"Packet too small: {len(packet)} bytes")

    iv1 = int.from_bytes(packet[0x40:0x44], byteorder="little")
    iv2 = iv1 ^ 0xDEADBEAF

    nonce = iv2.to_bytes(4, "little") + iv1.to_bytes(4, "little")
    cipher = Salsa20.new(key=KEY[:32], nonce=nonce)
    decoded = cipher.decrypt(packet)

    magic = int.from_bytes(decoded[0:4], byteorder="little")
    if magic != MAGIC:
        raise PacketDecodeError(f"Invalid magic: {hex(magic)}")

    return decoded


def normalize_world_position(world_x: float, world_z: float) -> tuple[float, float]:
    # Sans base de données officielle des tracés, on projette les coordonnées monde
    # dans un viewport dynamique stable. Le dashboard affiche aussi world_x/world_z.
    scale = 900.0
    x = 0.5 + max(-0.48, min(0.48, world_x / scale))
    y = 0.5 + max(-0.48, min(0.48, world_z / scale))
    if not math.isfinite(x):
        x = 0.5
    if not math.isfinite(y):
        y = 0.5
    return x, y


def parse_packet(console_ip: str, packet: bytes) -> dict:
    data = decrypt_packet(packet)

    world_x = f32(data, 0x04)
    world_y = f32(data, 0x08)
    world_z = f32(data, 0x0C)
    x, y = normalize_world_position(world_x, world_z)

    raw_gear = u8(data, 0x90)
    current_gear = raw_gear & 0b00001111
    suggested_gear = raw_gear >> 4
    if current_gear < 1:
        current_gear = "R"
    if suggested_gear > 14:
        suggested_gear = None

    tire_diam_fl = f32(data, 0xB4)
    tire_diam_fr = f32(data, 0xB8)
    tire_diam_rl = f32(data, 0xBC)
    tire_diam_rr = f32(data, 0xC0)

    return {
        "console_ip": console_ip,
        "timestamp": time(),
        "connected": True,
        "packet_id": i32(data, 0x70),
        "car_id": i32(data, 0x124),
        "track_id": "gt7_live",
        "track_name": "GT7 Live",
        "lap": i16(data, 0x74),
        "total_laps": i16(data, 0x76),
        "position": i16(data, 0x84),
        "total_positions": i16(data, 0x86),
        "lap_progress": 0.0,
        "world_x": world_x,
        "world_y": world_y,
        "world_z": world_z,
        "x": x,
        "y": y,
        "speed_kph": round(3.6 * f32(data, 0x4C), 2),
        "rpm": int(f32(data, 0x3C)),
        "gear": current_gear,
        "suggested_gear": suggested_gear,
        "throttle": round(u8(data, 0x91) / 255.0, 4),
        "brake": round(u8(data, 0x92) / 255.0, 4),
        "boost": round(f32(data, 0x50) - 1.0, 4),
        "fuel_liters": round(f32(data, 0x44), 3),
        "fuel_capacity_liters": round(f32(data, 0x48), 3),
        "tire_fl": round(f32(data, 0x60), 2),
        "tire_fr": round(f32(data, 0x64), 2),
        "tire_rl": round(f32(data, 0x68), 2),
        "tire_rr": round(f32(data, 0x6C), 2),
        "tire_speed_fl": round(abs(3.6 * tire_diam_fl * f32(data, 0xA4)), 2),
        "tire_speed_fr": round(abs(3.6 * tire_diam_fr * f32(data, 0xA8)), 2),
        "tire_speed_rl": round(abs(3.6 * tire_diam_rl * f32(data, 0xAC)), 2),
        "tire_speed_rr": round(abs(3.6 * tire_diam_rr * f32(data, 0xB0)), 2),
        "oil_temp": round(f32(data, 0x5C), 2),
        "water_temp": round(f32(data, 0x58), 2),
        "oil_pressure": round(f32(data, 0x54), 4),
        "ride_height_mm": round(1000 * f32(data, 0x38), 2),
    }
