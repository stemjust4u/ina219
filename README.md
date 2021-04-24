<link rel="stylesheet" href="./images/sj4u.css"></link>

# [STEM Just 4 U Home Page](https://stemjust4u.com/)
## This project collects voltage, current, and power from an ina219 power monitor

If you don't have an ina219, (0-3.3V) voltage can be collected using ADC on esp32 (or external ADC boards ADS115/MCP3008 on RPi) but current or higher voltages are not as easy to get to. The ina219 makes higher voltage and current/power collection easy. I did not see libraries for micropython so this project will only be with Raspberry Pi. I2C is used for communication to the RPi, requiring only 2 cables for that portion. Another advantage to the ina219 is that you can connect to the high side, between the power source and load, so you can measure both current and voltage.

[Link to Project Web Site](https://github.com/stemjust4u/ina219)

## Materials 
* Raspberry Pi
* ina219 board  
​
![ina219](images/ina219-front.png#5rad)
![ina219](images/ina219-back.png#5rad) 

# Specs
The ina219 has 12-bit ADC.  
It can measure up to 3.2A with ~ 0.8mA resolution.  
DC voltage goes up to 26V.  

There are 4 measurement pins on the boards I bought. But you can add more boards by bridging the A0/A1 pad.  

>Board 0: Address = 0x40 Offset = binary 00000 (no jumpers required)  
Board 1: Address = 0x41 Offset = binary 00001 (bridge A0)  
Board 2: Address = 0x44 Offset = binary 00100 (bridge A1)  
Board 3: Address = 0x45 Offset = binary 00101 (bridge A0 & A1)  

Use `$ sudo i2cdetect -y 1` to check the address.

The pi-ina219 has wake/sleep modes but it only uses 0.9mA to begin with. In sleep mode it dropped to 0.2mA.

# Pin Connection
​In $ sudo raspi-config make sure I2C is enabled in the interface.
Can confirm in `$ sudo nano /boot/config.txt`  
dtparam=i2c=on  

Pinout shows details on which pins are available for each connection

Vcc will be 3.3V from RPi  
The Vin+ will go to the + side of the power source and Vin- will go to the + side of the load.  
Ground should be common between the power you're measuring, the ina219, and the RPi.  
SDA to I2C data line  
SCL to I2C clock  

### MQTT Explorer  
[MQTT Explorer](http://mqtt-explorer.com/) is a great tool for watching messages between your clients and broker. You can also manually enter a topic and send a msg to test your code. This is useful for initial setup/debugging before implementing a final mqtt setup in node-red.

# Code
MQTT is used to communicate readings to a node-red server.

RPi
/demomqtt.py (can use the dict to use multiple boards)  
|-/piina219   
|    |-Mpiina219.py (ina219 module) 

Code Sections
1. MQTT functions defined (along with other functions required)
2. Logging/debugging control set with level
DEBUG (variables+status prints)
INFO (status prints)
CRITICAL (prints turned off)
3. Hardware Setup (create objects for external hardware)
4. MQTT setup (get server info align topics to match node-red)
    * SUBSCRIBE TOPIC (regex is used to match the topic)
    * PUBLISH TOPIC (dictionary key is used to join Topic)
5. Start/bind MQTT functions
6. Enter main loop
    * Get readings
    * Publish readings to node-red via mqtt broker/server

There is no esp32 setup for this project

# Node Red
Node red flows are in the node-red-flow file in github. Data is sent to an influx db where historical data can be pulled, too.

![ina219](images/nodered-flow.png#)
![ina219](images/nodered-gauges.png#)
![ina219](images/nodered-chart.png#)