from micropython import const

# (C)2025 David Horton 
# BSD 2-clause license
# https://github.com/DavesCodeMusings/SHT3x_MicroPython

class SHT3x:
    """
    Read temperature and humidity from Sensirion SHT-3x sensors.
    https://sensirion.com/media/documents/213E6A3B/63A5A569/Datasheet_SHT3x_DIS.pdf
    """

    # See datasheet for the origin of these values.
    RESET_COMMAND = const(0x30A2)  # Soft reset / re-initialization
    STATUS_COMMAND = const(0xF32D)
    CLEAR_STATUS_COMMAND = const(0x3041)
    MEASURE_COMMAND = const(0x2400)  # High repeatability, no clock stretch
    COMMAND_WAIT_TIME_mS = const(2)  # Max time for most commands to process
    MEASUREMENT_WAIT_TIME_mS = const(16)  # Max time for high repeatability
    CRC8_POLYNOMIAL = const(0x31)
    CRC8_INITIALIZATION = const(0xFF)

    def __init__(self, i2c, addr=0x44, debug=False):
        self._i2c = i2c
        self._i2c_addr = addr
        self._debug = debug
        self._raw_data = bytes(6)  # 2-bytes Temp, 1-byte CRC, 2-bytes Hum, 1-byte CRC

    def _crc8(self, data):
        """
        Calculate the 8-bit checksum for 16-bit data returned from the sensor.

        Args:
            data (bytes): a two-byte value representing either temperature, humidity, or status.

        Returns:
            bytes: CRC8 checksum.
        """
        crc = SHT3x.CRC8_INITIALIZATION
        for byte in data:
            crc ^= byte
            for _ in range(8):  # Shift left through all 8 bits
                if crc & 0x80:  # Only if MSB is set, do we XOR with CRC8_POLYNOMIAL
                    crc = (crc << 1) ^ SHT3x.CRC8_POLYNOMIAL
                else:
                    crc <<= 1
                crc &= 0xFF  # Truncate CRC to 8 bits
        return crc.to_bytes()  # Return as bytes object for easy comparison

    def _send_command(self, command):
        """
        Send a 2-byte command and count ACKs to ensure proper receipt.
        """
        if self._debug:
            print(
                f"Sending {hex(command)} to: bus={self._i2c}; addr={hex(self._i2c_addr)}"
            )
        acks = self._i2c.writeto(self._i2c_addr, command.to_bytes(2))
        if acks != 2:
            OSError("I2C command not acknowledged.")

    def reset(self):
        """
        Send command for soft reset and re-initialization.
        """
        if self._debug:
            print("RESET requested.")
        self._send_command(SHT3x.RESET_COMMAND)

    def clear_status(self):
        """
        Send command to reset status register bits to zero.
        """
        if self._debug:
            print("CLEAR_STATUS requested.")
        self._send_command(SHT3x.CLEAR_STATUS_COMMAND)

    def measure(self):
        """
        Send command for sensor to come out of idle and take readings.
        """
        if self._debug:
            print("MEASURE requested.")
        self._send_command(SHT3x.MEASURE_COMMAND)

    def read(self):
        """
        Fetch raw data from sensor and save it in self._raw_data

        Returns:
            bytes: Six-byte raw data with checksums
        """
        if self._debug:
            print(
                f"Reading measurement data from: bus={self._i2c}; addr={hex(self._i2c_addr)}"
            )
        self._raw_data = self._i2c.readfrom(self._i2c_addr, 6)
        if self._debug:
            print(f"Device data (MSB, LSB, CRC): 0x{self._raw_data.hex()}")
        return self._raw_data

    @property
    def status(self):
        """
        Send command to read the device status register, expecting a 2-byte + 1-byte CRC result.
        """
        if self._debug:
            print("STATUS requested.")
        self._send_command(SHT3x.STATUS_COMMAND)
        if self._debug:
            print(
                f"Reading status register from: bus={self._i2c}; addr={hex(self._i2c_addr)}"
            )
        raw_status = self._i2c.readfrom(self._i2c_addr, 3)
        if self._debug:
            print(f"Raw status (MSB, LSB, CRC): 0x{raw_status.hex()}")
        status_reg = raw_status[0:2]  # First two bytes are status
        status_reg_checksum = raw_status[2:3]  # Third byte is crc8 checksum
        if self._crc8(status_reg) != status_reg_checksum:
            raise OSError("Invalid CRC checksum for SHT3x status register.")
        return status_reg

    @property
    def temperature(self):
        """
        Convert raw data to Celsius temperature according to formula given in datasheet.
        """
        sensor_temperature = self._raw_data[0:2]  # First two bytes are temperature data
        sensor_temperature_crc = self._raw_data[2:3]  # Third is crc8 checksum
        if self._crc8(sensor_temperature) != sensor_temperature_crc:
            raise OSError("Invalid CRC checksum for SHT3x temperature value.")
        else:
            temperature = -45 + 175 * int.from_bytes(sensor_temperature) / 65535
            return round(temperature, 2)

    @property
    def humidity(self):
        sensor_hum = self._raw_data[3:5]  # Fourth and fifth bytes are humidity data
        sensor_hum_checksum = self._raw_data[5:6]  # Sixth is crc8 checksum
        if self._crc8(sensor_hum) != sensor_hum_checksum:
            raise OSError("Invalid CRC checksum for SHT3x humidity value.")
        else:
            temperature = 100 * int.from_bytes(sensor_hum) / 65535
            return round(temperature, 2)


def demo():
    from machine import Pin, SoftI2C
    from time import sleep_ms

    # Values for ESP32 Devkit V1 (30-pin board with four corner mounting holes)
    # Adjust as needed for other boards.
    I2C_CLOCK = const(22)
    I2C_DATA = const(21)

    # This is the default address for SHT30
    I2C_ADDR = const(0x44)

    i2c = SoftI2C(scl=Pin(I2C_CLOCK), sda=Pin(I2C_DATA))
    if I2C_ADDR not in i2c.scan():
        print(f"No device found at {I2C_ADDR}")
        return False
    sht3x = SHT3x(i2c, addr=I2C_ADDR, debug=True)
    sht3x.reset()
    sleep_ms(SHT3x.COMMAND_WAIT_TIME_mS)  # Must wait before sending another command.
    sht3x.clear_status()
    sleep_ms(SHT3x.COMMAND_WAIT_TIME_mS)
    sht3x.measure()
    sleep_ms(SHT3x.MEASUREMENT_WAIT_TIME_mS)  # Measurement wait time is longer.
    try:
        sht3x.read()
    except OSError as ex:
        print(f"Data read failed: {ex}")
    else:
        print(f"{sht3x.temperature} C")
        print(f"{sht3x.humidity}% RH")


if __name__ == "__main__":
    demo()
