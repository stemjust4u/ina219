import time, logging
from time import perf_counter_ns
import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
 
logging.info("Adafruit ina219 test")

i2c_bus = board.I2C()
ina219 = INA219(i2c_bus)
 
# display some of the advanced field (just to test)
logging.info("Config register:")
logging.info("  bus_voltage_range:    0x%1X" % ina219.bus_voltage_range)
logging.info("  gain:                 0x%1X" % ina219.gain)
logging.info("  bus_adc_resolution:   0x%1X" % ina219.bus_adc_resolution)
logging.info("  shunt_adc_resolution: 0x%1X" % ina219.shunt_adc_resolution)
logging.info("  mode:                 0x%1X" % ina219.mode)
logging.info("")
 
# INA219 measure bus voltage on the load side. So PSU voltage = bus_voltage + shunt_voltage
#logging.info("Voltage (VIN+) : {:6.3f}   V".format(bus_voltage + shunt_voltage))
#logging.info("Voltage (VIN-) : {:6.3f}   V".format(bus_voltage))
#logging.info("Shunt Voltage  : {:8.5f} V".format(shunt_voltage))
#logging.info("Shunt Current  : {:7.4f}  A".format(current / 1000))
#logging.info("Power Calc.    : {:8.5f} W".format(bus_voltage * (current / 1000)))
#logging.info("Power Register : {:6.3f}   W".format(power))
#logging.info("")

# optional : change configuration to use 32 samples averaging for both bus voltage and shunt voltage
ina219.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina219.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
# optional : change voltage range to 16V
ina219.bus_voltage_range = BusVoltageRange.RANGE_16V

def read():
    Vbus = ina219.bus_voltage  # voltage on V- (load side)
     # Check internal calculations haven't overflowed (doesn't detect ADC overflows)
    if ina219.overflow:
        logging.info("Internal Math Overflow Detected!")
        logging.info("")
    Vshunt = ina219.shunt_voltage  # voltage between V+ and V- across the shunt
    Ibus = ina219.current  # current in mA
    Pwr = ina219.power  # power in watts
    return Vbus, Ibus, Pwr, Vshunt
    
# measure and display loop
if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO) # Set to CRITICAL to turn logging off. Set to DEBUG to get variables. Set to INFO for status messages.

    while True:
        t0 = perf_counter_ns()
        Vbus, Ibus, Pwr, Vshunt = read()
        tdelta = perf_counter_ns() - t0
        logging.info("Vbus:{0:1.2f}V Ibus:{1}mA  Power:{2:.2f}W Vshunt:{3:1.2} Time:{4}ms".format(Vbus, int(Ibus), Pwr, Vshunt, tdelta/1000000))
        time.sleep(1)