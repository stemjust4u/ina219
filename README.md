# ina219

sudo i2cdetect -y 1

The maximum voltage drop that the INA219 can measure is 320 mV or .32 V.  Therefore the maximum current that the INA219 can measure with the default resistor is .32 V / 0.1 Ω = 3.2 A.

The INA219 provides digital reporting using the I2C communication protocol.  Unlike an analog sensor that provides a proportional value, the digital INA219 returns actual numbers for the voltage, current and power in volts, amps and watts.  I2C makes wiring the INA219 adapter to the Raspberry Pi very easy.  The VCC pin is connected to a 3.3 V pin on the Pi. 