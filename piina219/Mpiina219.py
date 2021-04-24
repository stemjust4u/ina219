#!/usr/bin/env python3

'''
Board 0: Address = 0x40 Offset = binary 00000 (no jumpers required)
Board 1: Address = 0x41 Offset = binary 00001 (bridge A0)
Board 2: Address = 0x44 Offset = binary 00100 (bridge A1)
Board 3: Address = 0x45 Offset = binary 00101 (bridge A0 & A1)
To check address
$ sudo i2cdetect -y 1

Can be put in low power mode
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

from ina219 import INA219
from ina219 import DeviceRangeError
import time, logging
from time import perf_counter, perf_counter_ns

class PiINA219:

    def __init__(self, gainmode="auto", maxamps = 0.4, useraddress=0x40): 
        self.SHUNT_OHMS = 0.1
        self.ina219 = INA219(self.SHUNT_OHMS, maxamps, address=useraddress, log_level=logging.INFO)
        self.output = {}
        if gainmode == "auto":      # AUTO GAIN, HIGH RESOLUTION - Lower precision above max amps specified
            self.ina219.configure(self.ina219.RANGE_16V)
        elif gainmode == "manual":  # MANUAL GAIN, HIGH RESOLUTION - Max amps is 400mA
            self.ina219.configure(self.ina219.RANGE_16V, self.ina219.GAIN_1_40MV)

    def read(self):
        Vbus =  self.ina219.voltage()
        try:
            Ibus = self.ina219.current()
            pwr = self.ina219.power()
            #Vshunt = self.ina219.shunt_voltage()
        except DeviceRangeError as e:
            logging.info("Current overflow")
        self.output['Vbusf'] = Vbus
        self.output['IbusAf'] = Ibus/1000
        self.output['PowerWf'] = pwr/1000
        return self.output

    def sleep(self):
        self.ina219.sleep()

    def wake(self):
        self.ina219.wake()

    def reset(self):
        self.ina219.reset()


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO) # Set to CRITICAL to turn logging off. Set to DEBUG to get variables. Set to INFO for status messages.
    
    ina219A = PiINA219("auto", 0.4, 0x40)
    ina219B = PiINA219("auto", 0.4, 0x41)
    #while True:
    for i in range(5):
        t0 = perf_counter_ns()
        reading = ina219B.read()
        tdelta = perf_counter_ns() - t0
        logging.info("Vbus:{0:1.2f}V Ibus:{1:1.4f}A  Pwr:{2:.2f}W Time:{3}ms".format(reading['Vbusf'], reading['IbusAf'], reading['PowerWf'], tdelta/1000000))
        time.sleep(1)
    ina219A.sleep()
    for i in range(5):
        t0 = perf_counter_ns()
        reading = ina219B.read()
        tdelta = perf_counter_ns() - t0
        logging.info("Vbus:{0:1.2f}V Ibus:{1:1.4f}A  Pwr:{2:.2f}W Time:{3}ms".format(reading['Vbusf'], reading['IbusAf'], reading['PowerWf'], tdelta/1000000))
        time.sleep(1)