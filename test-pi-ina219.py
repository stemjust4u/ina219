#!/usr/bin/env python3

from ina219 import INA219
from ina219 import DeviceRangeError
import time, logging
from time import perf_counter_ns

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.4  # To get highest resoltuion. Max is 400mA
ADDRESS = 0x40
'''
Board 0: Address = 0x40 Offset = binary 00000 (no jumpers required)
Board 1: Address = 0x41 Offset = binary 00001 (bridge A0)
Board 2: Address = 0x44 Offset = binary 00100 (bridge A1)
Board 3: Address = 0x45 Offset = binary 00101 (bridge A0 & A1)

# Can be put in low power mode
ina.sleep()
time.sleep(60)
ina.wake()

ina.reset()               # Reset the INA219 to its default configuration.
ina.is_conversion_ready() # check if conversion was done before reading the next measurement results.

#Debugging mode
ina = INA219(SHUNT_OHMS, log_level=logging.INFO) # See calibration calculation results and automatic gain increases
ina = INA219(SHUNT_OHMS, log_level=logging.DEBUG)


ina.configure(voltage_range=ina.RANGE_16V,
              gain=ina.GAIN_AUTO,
              bus_adc=ina.ADC_128SAMP,
              shunt_adc=ina.ADC_128SAMP)

RANGE*32V: Range zero to 32 volts (default)
RANGE*16V: Range zero to 16 volts

GAIN*AUTO: Automatically calculate the gain (default)
GAIN_1_40MV: Maximum shunt voltage 40mV
GAIN*2_80MV: Maximum shunt voltage 80mV

bus*adc: The bus ADC resolution (9, 10, 11, or 12-bit)
ADC*12BIT: 12 bit, conversion time 532us (default)
ADC*11BIT: 11 bit, conversion time 276us.
ADC*10BIT: 10 bit, conversion time 148us.
ADC*9BIT: 9 bit, conversion time 84us.
or
shunt*adc: The shunt ADC resolution (9, 10, 11, or 12-bit)
ADC*2SAMP: 2 samples at 12 bit, conversion time 1.06ms.
ADC*4SAMP: 4 samples at 12 bit, conversion time 2.13ms.
ADC*8SAMP: 8 samples at 12 bit, conversion time 4.26ms.
ADC*16SAMP: 16 samples at 12 bit, conversion time 8.51ms
ADC*32SAMP: 32 samples at 12 bit, conversion time 17.02ms.
ADC*64SAMP: 64 samples at 12 bit, conversion time 34.05ms.
ADC*128SAMP: 128 samples at 12 bit, conversion time 68.10ms.

'''

def read():
    Vbus =  ina219A.voltage()
    try:
        Ibus = ina219A.current()
        Pwr = ina219A.power()
        Vshunt = ina219A.shunt_voltage()
    except DeviceRangeError as e:
        logging.info("Current overflow")
    return Vbus, Ibus, Pwr, Vshunt

ina219A = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address=ADDRESS, log_level=logging.INFO)

# AUTO GAIN
#ina219A.configure()  # automatically adjusts gain as required until the maximum is reached, when a DeviceRangeError exception
                 # is thrown to avoid invalid readings being taken. Downside is reduced current and power resolution.

# AUTO GAIN, HIGH RESOLUTION
ina219A.configure(ina219A.RANGE_16V)  # Will calculate the best gain to achieve the highest resolution based on the maximum expected current.
                                      # If the current exceeds the maximum specified, the gain will be automatically increased, so a valid reading will still result, but at a lower resolution.

# MANUAL GAIN, HIGH RESOLUTION
#ina219A.configure(ina219A.RANGE_16V, ina219A.GAIN_1_40MV) # Will miss current and power values if a current overflow occurs.

logging.info("pi-ina219 setup on {0}".format(ADDRESS))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) # Set to CRITICAL to turn logging off. Set to DEBUG to get variables. Set to INFO for status messages.

    while True:
        t0 = perf_counter_ns()
        Vbus, Ibus, Pwr, Vshunt = read()
        tdelta = perf_counter_ns() - t0
        logging.info("Vbus:{0:1.2f}V Ibus:{1}mA  Pwr:{2:.2f}W Vshunt:{3:1.2} Time:{4}ms".format(Vbus, int(Ibus), Pwr/1000, Vshunt, tdelta/1000000))
        time.sleep(1)