import asyncio
import logging
from binascii import hexlify
from time import time

from bleak import BleakClient, BleakGATTCharacteristic

import errors
from packet import TimePacket

UUID_BATTERY_LEVEL = "00002a19-0000-1000-8000-00805f9b34fb"
UUID_COMMAND = "58af3dca-6fc0-4fa3-9464-74662f043a3b"
UUID_NOTIFY = "58af3dca-6fc0-4fa3-9464-74662f043a3a"


class Connection:
    def __init__(self, client: BleakClient, sign_key: bytearray):
        self.client: BleakClient = client
        self.sign_key: bytearray = sign_key
        self.time_sync_req = False

    async def init(self) -> None:
        await self.client.start_notify(UUID_NOTIFY, self.notify_handler)

    async def battery_level(self) -> int:
        return int.from_bytes(await self.client.read_gatt_char(UUID_BATTERY_LEVEL), "big")

    async def write_command(self, command: bytearray) -> None:
        logging.debug("Sending packet...")
        await self.client.write_gatt_char(UUID_COMMAND, command)
        logging.debug("Packet sent.")

        await asyncio.sleep(0.5)

        if self.time_sync_req is True:
            logging.debug("Sending time sync command...")
            packet = TimePacket(int(time()), bytearray())
            packet.sign(self.sign_key)

            await self.write_command(packet.payload)

            self.time_sync_req = False
            logging.debug("Time set.")

            await asyncio.sleep(0.5)

            logging.debug("Re-sending packet after time sync...")
            await self.client.write_gatt_char(UUID_COMMAND, command)

    def notify_handler(self, char: BleakGATTCharacteristic, data: bytearray) -> None:
        if data[0] == 0x09:
            logging.debug("Received time sync request")

            self.time_sync_req = True
        elif data[0] == 0x02:
            logging.debug("Received UNLOCK_START notification")
        elif data[0] == 0x03:
            logging.debug("Received UNLOCK_CMP notification")
        elif data[0] == 0x04:
            logging.debug("Received LOCK_START notification")
        elif data[0] == 0x05:
            logging.debug("Received LOCK_CMP notification")
        elif data[0] == 0x25 and data[1] == 0x40:
            logging.debug("Received INVALID_OPCODE notification")
        elif data[0] == 0xFF:
            raise errors.InvalidSignKeyError("Got TX_SIGN_INVALID, check your sign key")
        else:
            logging.warning("Unknown notification received: %s" % hexlify(data).decode('utf-8'))

