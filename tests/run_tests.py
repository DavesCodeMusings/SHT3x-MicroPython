# Run tests using mocked up sensor data. No fancy framework like
# unittest or pytest, but it gets the job done.
#
# See also in this directory:
# machine.py and micropython.py for helper code that mocks up
# i2c and const() to work with CPython.
from sys import path
path.insert(0, 'src')
path.insert(1, 'tests/mock')

from machine import Pin, SoftI2C
from sht3x import SHT3x

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
sht3x = SHT3x(i2c, addr=0x44, debug=True)
sht3x_invalid_addr = SHT3x(i2c, addr=0x42, debug=True)


def test_valid_crc8(sht3x):
    data = bytearray.fromhex("BEEF")  # Example given by SHT3x datasheet
    crc = sht3x._crc8(data)
    assert crc == bytearray.fromhex("92")


def test_invalid_crc8(sht3x):
    data = bytearray.fromhex("BEEE")
    crc = sht3x._crc8(data)
    assert crc != bytearray.fromhex("92")


def test_send_command(sht3x):
    sht3x._send_command(0x30A2)


def test_send_command_invalid_addr(sht3x_invalid_addr):
    try:
        sht3x_invalid_addr._send_command(0x30A2)
    except OSError as ex:
        exception = ex
    assert str(exception) == "I2C command not acknowledged."


def test_reset(sht3x):
    sht3x.reset()


def test_clear_status(sht3x):
    sht3x.clear_status()


def test_measure(sht3x):
    sht3x.measure()


def test_read(sht3x):
    sht3x.read()


def test_status(sht3x):
    status = sht3x.status
    assert status == bytearray.fromhex("0000")


def test_temperature(sht3x):
    sht3x._raw_data = bytearray.fromhex("DEAD98BEEF92")
    temperature = sht3x.temperature
    assert temperature == 107.22


def test_humidity(sht3x):
    sht3x._raw_data = bytearray.fromhex("DEAD98BEEF92")
    humidity = sht3x.humidity
    assert humidity == 74.58


test_valid_crc8(sht3x)
test_invalid_crc8(sht3x)
test_send_command(sht3x)
test_send_command_invalid_addr(sht3x_invalid_addr)
test_reset(sht3x)
test_clear_status(sht3x)
test_measure(sht3x)
test_read(sht3x)
test_status(sht3x)
test_temperature(sht3x)
test_humidity(sht3x)
