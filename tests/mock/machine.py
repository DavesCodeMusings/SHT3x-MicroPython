# Mock up an SHT30 for running tests under CPython
sht3x_command_set = [
    0x2400,  # Measure
    0x3041,  # Clear status register
    0x3066,  # Heater off
    0x306D,  # Heater on
    0x30A2,  # Soft reset
    0xF32D,  # Status
]


def Pin(gpio):
    return f"Pin({gpio})"


class SoftI2C:
    def __init__(self, scl, sda):
        print(f"Mock I2C object created with clock={scl} and data={sda}")
        pass

    def writeto(self, addr, cmd):
        print(f"Mock I2C.writeto() address={hex(addr)} command={cmd.hex()}")
        acks = len(cmd)  # ACK sent for each byte received
        if addr == 0x44 and int.from_bytes(cmd) in sht3x_command_set:
            return acks
        else:
            return 0

    def readfrom(self, addr, num_bytes):
        print(f"Mock I2C.readfrom() address={hex(addr)} of {num_bytes} bytes")
        if addr != 0x44:
            assert OSError("ENODEV")
        if num_bytes == 3:
            return bytearray.fromhex("000081")  # Mockup of status_reg + CRC
        elif num_bytes == 6:
            return bytearray.fromhex("DEAD98BEEF92")  # Temp, CRC, Humid, CRC
