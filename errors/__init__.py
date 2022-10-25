class DeviceNotFoundError(Exception):
    def __init__(self, sn: str):
        super().__init__("Could not found device with SN \"%s\"" % sn)


class InvalidSignKeyError(Exception):
    pass
