from src.sht3x import SHT3x
sht3x = SHT3x(None)

def test_valid_crc8(sht3x):
    data = bytearray.fromhex("BEEF")  # Example given by SHT3x datasheet
    crc = sht3x._crc8(data)
    assert crc == bytearray.fromhex("92")

def test_invalid_crc8(sht3x):
    data = bytearray.fromhex("BEEE")
    crc = sht3x._crc8(data)
    assert crc != bytearray.fromhex("92")

test_valid_crc8(sht3x)
test_invalid_crc8(sht3x)
