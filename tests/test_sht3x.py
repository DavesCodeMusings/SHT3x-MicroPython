import pytest
from machine import Pin, SoftI2C
from sht3x import SHT3x


@pytest.fixture
def i2c():
    return SoftI2C(scl=Pin(22), sda=Pin(21))

@pytest.fixture
def sht3x(i2c):
    return SHT3x(i2c, addr=0x44, debug=True)

@pytest.fixture
def sht3x_invalid_addr(i2c):
    return SHT3x(i2c, addr=0x42, debug=True)

def test_valid_crc8(sht3x):
    data = bytearray.fromhex("BEEF")  # Example given by SHT3x datasheet
    crc = sht3x._crc8(data)
    assert crc == bytearray.fromhex("92")

def test_invalid_crc8(sht3x):
    data = bytearray.fromhex("BEEE")
    crc = sht3x._crc8(data)
    assert crc != bytearray.fromhex("92")

def test_send_command(sht3x):
    # No assertion here, just verifying no exceptions are raised.
    sht3x._send_command(0x30A2)

def test_send_command_invalid_addr(sht3x_invalid_addr):
    with pytest.raises(OSError) as excinfo:
        sht3x_invalid_addr._send_command(0x30A2)
    assert str(excinfo.value) == "I2C command not acknowledged."

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
