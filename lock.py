from __future__ import annotations

from time import time

from bleak import BleakScanner, BleakClient, BLEDevice, AdvertisementData

from connection import Connection
from errors import DeviceNotFoundError
from packet import ActionPacket, UnlockMode


class Lock:
    def __init__(self, sn: str, sign_key: bytearray):
        self.sn: str = sn
        self.sign_key: bytearray = sign_key
        self.device = None

    @staticmethod
    async def create(sn: str, sign_key: bytearray) -> Lock:
        self = Lock(sn, sign_key)

        await self.__find_mac()

        return self

    async def __find_mac(self) -> None:
        def callback(found: BLEDevice, advertisement_data: AdvertisementData) -> bool:
            return found.name == "EL_" + self.sn

        device = await BleakScanner.find_device_by_filter(callback)

        if device is None:
            raise DeviceNotFoundError(self.sn)

        self.device = device

    async def get_battery(self) -> int:
        async with BleakClient(self.device, timeout=2.0) as client:
            connection = Connection(client, self.sign_key)

            return await connection.battery_level()

    async def lock(self) -> None:
        await self.__do_action(UnlockMode.LOCK)

    async def unlock(self) -> None:
        await self.__do_action(UnlockMode.UNLOCK)

    async def temp_unlock(self) -> None:
        await self.__do_action(UnlockMode.TEMP_UNLOCK)

    async def __do_action(self, mode: UnlockMode) -> None:
        async with BleakClient(self.device, timeout=2.0) as client:
            connection = Connection(client, self.sign_key)

            await connection.init()

            packet = ActionPacket(int(time()), mode, bytearray())
            packet.sign(self.sign_key)

            await connection.write_command(packet.payload)
