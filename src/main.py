from micropython import const
from machine import Pin, SoftI2C
from time import sleep_ms
from sht3x import SHT3x


def demo():
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

    # The heater can be used to clear condensation from the sensor, but will
    # affect readings made immediately after.
    sht3x.set_heater(1)
    sleep_ms(2000)
    sht3x.set_heater(0)
    sht3x.measure()
    sleep_ms(SHT3x.MEASUREMENT_WAIT_TIME_mS)
    sht3x.read()
    print(f"{sht3x.temperature} C")
    print(f"{sht3x.humidity}% RH")


if __name__ == "__main__":
    demo()
