# SHT3x-MicroPython
What you will find here is a MicroPython module for the Sensirion SHT3x series of temperature humidity sensors. It's designed for taking measurements in one-shot mode (on demand as opposed to continuous.)

[![Build SHT3x-MicroPython](https://github.com/DavesCodeMusings/SHT3x-MicroPython/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/DavesCodeMusings/SHT3x-MicroPython/actions/workflows/build.yml)

## Why should I care?
There are other modules for using the SHT3x sensor with MicroPython. This one is a little different in that it splits apart the sensor measurement command and data reading functions, while also leaving out the delay required for the measurement to take place.

This is done to facilitate use with asynchronous code.

Rather than having a built-in `time.sleep_ms()` wasting time inside the module, your async program can do `await asyncio.sleep_ms()` instead. This lets other tasks run while waiting for the sensor.

## How can I use it?
First, if you're using asyncio, do this:

```
from asyncio import sleep_ms 
```

Otherwise, for traditional, do this:

```
from time import sleep_ms
```

Next, create a new instance of the SHT3x sensor class like this:

```
from machine import Pin, SoftI2C
from sht3x import SHT3x

i2c = SoftI2C(scl=Pin(I2C_CLOCK), sda=Pin(I2C_DATA))
sht3x = SHT3x(i2c, addr=I2C_ADDR, debug=True)
```

>Or at minimum, you can rely on defaults of address 0x44 and debug=False, like this: `sht3x = SHT3x(i2c)`

Then, you can request a measurement, wait for the sensor to finish, and read the results.

```
sht3x.measure()
sleep_ms(SHT3x.MEASUREMENT_WAIT_TIME_mS)
sht3x.read()
print(f"{sht3x.temperature} C")
print(f"{sht3x.humidity}% RH")
```

For a more detailed example, see the `demo()` function inside the `sht3x.py` module.

### Sample output
Running the module's demo, you'll see something like the following (which includes debugging output.)

```
RESET requested.
Sending 0x30a2 to: bus=SoftI2C(scl=22, sda=21, freq=500000); addr=0x44
CLEAR_STATUS requested.
Sending 0x3041 to: bus=SoftI2C(scl=22, sda=21, freq=500000); addr=0x44
MEASURE requested.
Sending 0x2400 to: bus=SoftI2C(scl=22, sda=21, freq=500000); addr=0x44
Reading measurement data from: bus=SoftI2C(scl=22, sda=21, freq=500000); addr=0x44
Device data (MSB, LSB, CRC): 0x60be746ccd6b
21.13 C
42.11% RH
```

Without debug=True, it looks like this:

```
21.13 C
42.11% RH
```

### Exceptions
If something does not go as planned, the class methods will raise an OSError exception. Besides the exceptions possibly raised by the underlying I2C function calls, there are also exceptions when the sensor's CRC does not match the expected value (indicating corrupt data) and when sending a command does not result in the correct number of ACKnowledgements (indicating failure to receive the command.)

### Precision, accuracy, and decimal places
The values returned by the SHT3x class properties of temperature and humidity are rounded to two decimal places. This does not mean the sensor is accurate down to hundredths of a degree Celsius or hundredths of a percent relative humidity. See the Sensor Performance section of the manufacturer datasheet to determine actual accuracy of the various sensor models.

## Did you find a bug?
If something's not quite right, use the GitHub issues to report it. Please include:

* The behavior you saw and what caused it
* What it should have done instead
* Theories on what might fix the problem

I am a part-time development team of one, so any helpful details you can give are appreciated.
