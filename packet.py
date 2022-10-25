from __future__ import annotations

import hashlib
import hmac
from binascii import hexlify
from enum import IntEnum


class Command(IntEnum):
    DO_ACTION = 0x1
    SET_TIME = 0x8


class UnlockMode(IntEnum):
    TEMP_UNLOCK = 0x0
    UNLOCK = 0x1
    LOCK = 0x2


class Packet:
    def __init__(self, command: Command, mode: int, payload: bytearray = None):
        self.command: Command = command
        self.mode: int = mode
        self.payload: bytearray = payload

    @staticmethod
    def from_byte_array(data: bytearray) -> Packet:
        result = Packet(
            command=Command(data[0]),
            mode=data[1],
            payload=data[2:]
        )

        result.raw = data

        return result

    def hex_string(self) -> bytes:
        return hexlify(self.payload)


class ActionPacket(Packet):
    def __init__(self, timestamp: int, unlock_mode: UnlockMode, signature: bytearray):
        super().__init__(Command.DO_ACTION, 0x50)

        self.timestamp: int = timestamp
        self.unlock_mode: UnlockMode = unlock_mode
        self.signature: bytearray = signature

    @staticmethod
    def from_byte_array(data: bytearray) -> ActionPacket:
        result = ActionPacket(
            timestamp=int.from_bytes(data[2:6], "big"),
            unlock_mode=UnlockMode(data[6]),
            signature=data[7:20]
        )

        result.payload = data

        return result

    def verify_signature(self, sign_key: bytearray) -> bool:
        if self.signature is None:
            raise ValueError("Signature not set")

        expected = bytearray.fromhex(hmac.new(sign_key, self.payload[:7], hashlib.sha1).hexdigest())[:13]

        return expected == self.signature

    def sign(self, sign_key: bytearray) -> None:
        self.update_payload()

        self.signature = bytearray.fromhex(hmac.new(sign_key, self.payload[:7], hashlib.sha1).hexdigest())[:13]

        self.update_payload()

    def update_payload(self) -> None:
        self.payload = self.command.to_bytes(1, "big") \
                       + self.mode.to_bytes(1, "big") \
                       + self.timestamp.to_bytes(4, "big") \
                       + self.unlock_mode.to_bytes(1, "big") \
                       + self.signature


class TimePacket(Packet):
    def __init__(self, timestamp: int, signature: bytearray):
        super().__init__(Command.SET_TIME, 0x40)

        self.timestamp: int = timestamp
        self.signature: bytearray = signature

    @staticmethod
    def from_byte_array(data: bytearray) -> TimePacket:
        result = TimePacket(
            timestamp=int.from_bytes(data[2:6], "big"),
            signature=data[6:20]
        )

        print(result.timestamp, result.signature)

        result.payload = data

        return result

    def verify_signature(self, sign_key: bytearray) -> bool:
        if self.signature is None:
            raise ValueError("Signature not set")

        expected = bytearray.fromhex(hmac.new(sign_key, self.payload[:6], hashlib.sha1).hexdigest())[:14]

        print(self.signature, expected)

        return expected == self.signature

    def sign(self, sign_key: bytearray) -> None:
        self.update_payload()

        self.signature = bytearray.fromhex(hmac.new(sign_key, self.payload[:6], hashlib.sha1).hexdigest())[:14]

        self.update_payload()

    def update_payload(self) -> None:
        self.payload = self.command.to_bytes(1, "big") \
                       + self.mode.to_bytes(1, "big") \
                       + self.timestamp.to_bytes(4, "big") \
                       + self.signature
