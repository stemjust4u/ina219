import sys, json, logging, re
from time import sleep, perf_counter
import paho.mqtt.client as mqtt
from os import path
from pathlib import Path
from logging.handlers import RotatingFileHandler
import piina219

def setup_logging(log_dir, log_level=logging.INFO, mode=1):
    # Create loggers
    # INFO + mode 1  = info           print only
    # INFO + mode 2  = info           print+logfile output
    # DEBUG + mode 1 = info and debug print only
    # DEBUG + mode 2 = info and debug print+logfile output

    if mode == 1:
        logfile_log_level = logging.CRITICAL
    elif mode == 2:
        logfile_log_level = logging.DEBUG

    main_logger = logging.getLogger(__name__)
    main_logger.setLevel(log_level)
    log_file_format = logging.Formatter("[%(levelname)s] - %(asctime)s - %(name)s - : %(message)s in %(pathname)s:%(lineno)d")
    log_console_format = logging.Formatter("[%(levelname)s]: %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.CRITICAL)
    console_handler.setFormatter(log_console_format)

    exp_file_handler = RotatingFileHandler('{}/debug.log'.format(log_dir), maxBytes=10**6, backupCount=5) # 1MB files
    exp_file_handler.setLevel(logfile_log_level)
    exp_file_handler.setFormatter(log_file_format)

    exp_errors_file_handler = RotatingFileHandler('{}/error.log'.format(log_dir), maxBytes=10**6, backupCount=5) # 1MB files
    exp_errors_file_handler.setLevel(logging.WARNING)
    exp_errors_file_handler.setFormatter(log_file_format)

    main_logger.addHandler(console_handler)
    main_logger.addHandler(exp_file_handler)
    main_logger.addHandler(exp_errors_file_handler)
    return main_logger

def on_connect(client, userdata, flags, rc):
    """ on connect callback verifies a connection established and subscribe to TOPICs"""
    global MQTT_SUB_TOPIC
    logger.info("attempting on_connect")
    if rc==0:
        mqtt_client.connected = True
        for topic in MQTT_SUB_TOPIC:
            client.subscribe(topic)
            logger.info("Subscribed to: {0}\n".format(topic))
        logger.info("Successful Connection: {0}".format(str(rc)))
    else:
        mqtt_client.failed_connection = True  # If rc != 0 then failed to connect. Set flag to stop mqtt loop
        logger.info("Unsuccessful Connection - Code {0}".format(str(rc)))

def on_message(client, userdata, msg):
    """on message callback will receive messages from the server/broker. Must be subscribed to the topic in on_connect"""
    logger.debug("Received: {0} with payload: {1}".format(msg.topic, str(msg.payload)))

def on_publish(client, userdata, mid):
    """on publish will send data to client"""
    #Debugging. Will unpack the dictionary and then the converted JSON payload
    #logger.debug("msg ID: " + str(mid)) 
    #logger.debug("Publish: Unpack outgoing dictionary (Will convert dictionary->JSON)")
    #for key, value in outgoingD.items():
    #    logger.debug("{0}:{1}".format(key, value))
    #logger.debug("Converted msg published on topic: {0} with JSON payload: {1}\n".format(MQTT_PUB_TOPIC1, json.dumps(outgoingD))) # Uncomment for debugging. Will print the JSON incoming msg
    pass 

def on_disconnect(client, userdata,rc=0):
    logger.debug("DisConnected result code "+str(rc))
    mqtt_client.loop_stop()

def mqtt_setup(IPaddress):
    global MQTT_SERVER, MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD, MQTT_SUB_TOPIC, MQTT_PUB_TOPIC, SUBLVL1, MQTT_REGEX
    global mqtt_client, mqtt_outgoingD, deviceD
    home = str(Path.home())                       # Import mqtt and wifi info. Remove if hard coding in python script
    with open(path.join(home, "stem"),"r") as f:
        user_info = f.read().splitlines()
    MQTT_SERVER = IPaddress                    # Replace with IP address of device running mqtt server/broker
    MQTT_USER = user_info[0]                   # Replace with your mqtt user ID
    MQTT_PASSWORD = user_info[1]               # Replace with your mqtt password
    MQTT_SUB_TOPIC = []
    SUBLVL1 = 'nred2' + MQTT_CLIENT_ID
    # lvl2: Specific MQTT_PUB_TOPICS created at time of publishing done using string.join (specifically item.join)
    MQTT_PUB_TOPIC = ['pi2nred/', '/' + MQTT_CLIENT_ID]
    mqtt_outgoingD = {}            # Container for data to be published via mqtt

def setup_device(device, lvl2, data_keys):
    global deviceD, SUBLVL1
    if deviceD.get(device) == None:
        deviceD[device] = {}
        deviceD[device]['data'] = {}
        deviceD[device]['lvl2'] = lvl2 # Sub/Pub lvl2 in topics. Does not have to be unique, can piggy-back on another device lvl2
        topic = f"{SUBLVL1}/{deviceD[device]['lvl2']}ZCMD/+"
        if topic not in MQTT_SUB_TOPIC:
            MQTT_SUB_TOPIC.append(topic)
            for key in data_keys:
                deviceD[device]['data'][key] = 0
        else:
            for key in data_keys:
                for item in deviceD:
                    if deviceD[item]['data'].get(key) != None:
                        print(f'**DUPLICATE WARNING {device} and {item} are both publishing {key} on {topic}')
                deviceD[device]['data'][key] = 0
        deviceD[device]['send'] = False
        print('\n{0} Subscribing to: {1}'.format(device, topic))
        print('   JSON payload keys will be:{0}'.format([*deviceD[device]['data']]))
    else:
        sys.exit(f'Device {device} already in use. Device name should be unique')

def main():
    global deviceD, mqtt_outgoingD      # Containers setup in 'create' functions and used for Publishing mqtt
    global MQTT_SERVER, MQTT_USER, MQTT_PASSWORD, MQTT_CLIENT_ID, mqtt_client, MQTT_PUB_TOPIC
    global logger, logger_log_level

    # Set next 3 variables for different logging options
    logger_log_level= logging.DEBUG # CRITICAL=logging off. DEBUG=get variables. INFO=status messages.
    logger_setup = 1  # 0 for basicConfig, 1 for custom logger with RotatingFileHandler (RFH)
    RFHmode = 2 # If logger_setup ==1 (RotatingFileHandler) then access to modes below
                #Arguments
                #log_level, RFHmode|  logger.x() | output
                #------------------|-------------|-----------
                #      INFO, 1     |  info       | print only
                #      INFO, 2     |  info       | print+logfile
                #      DEBUG,1     |  info+debug | print only
                #      DEBUG,2     |  info+debug | print+logfile
    if logger_setup == 0:
        if len(logging.getLogger().handlers) == 0:      # Root logger does not already exist, will create it
            logging.basicConfig(level=logger_log_level) # Create Root logger
            logger = logging.getLogger(__name__)        # Set logger to root logging
            logger.setLevel(logger_log_level)
        else:
            logger = logging.getLogger(__name__)        # Root logger already exists so just linking logger to it
            logger.setLevel(logger_log_level)
    elif logger_setup == 1:                             # Using custom logger with RotatingFileHandler
        logger = setup_logging(path.dirname(path.abspath(__file__)), logger_log_level, RFHmode ) # dir for creating logfile
    logger.info(logger)

    #==== HARDWARE/MQTT SETUP ===============#
    # AUTO GAIN, HIGH RESOLUTION - Lower precision above max amps specified
    # MANUAL GAIN, HIGH RESOLUTION - Max amps is 400mA
    # Pass gain (auto or manual), max current (400mA for high resolution), and address
    #Board 0: Address = 0x40 Offset = binary 00000 (no jumpers required)
    #Board 1: Address = 0x41 Offset = binary 00001 (bridge A0)
    #Board 2: Address = 0x44 Offset = binary 00100 (bridge A1)
    #Board 3: Address = 0x45 Offset = binary 00101 (bridge A0 & A1)
    #Returns a dictionary with Vbusf, IbusAi, PowerWf
    #Readings take 4-6ms

    MQTT_CLIENT_ID = 'pi' # Can make ID unique if multiple Pi's could be running similar devices (ie servos, ADC's) 
                          # Node red will need to be linked to unique MQTT_CLIENT_ID
    mqtt_setup('10.0.0.115')
    
    deviceD = {}  # Primary container for storing all devices, topics, and data
                  # Device name should be unique, can not duplicate device ID
                  # Topic lvl2 name can be a duplicate, meaning multipple devices publishing data on the same topic
                  # If topic lvl2 name repeats would likely want the data_keys to be unique
    
    ina219Set = {}

    device = "ina219A"  
    lvl2 = "ina219A"
    data_keys = ['Vbusf', 'IbusAf', 'PowerWf']
    setup_device(device, lvl2, data_keys)
    ina219Set[device] = piina219.PiINA219(*data_keys, gainmode="auto", maxA=0.4, address=0x40, mlogger=logger, mlog_level=logger_log_level)

    device = "ina219B"
    lvl2 = "ina219B"
    data_keys = ['Vbusf', 'IbusAf', 'PowerWf']
    setup_device(device, lvl2, data_keys)
    ina219Set[device] = piina219.PiINA219(*data_keys, gainmode="auto", maxA=0.4, address=0x41, mlogger=logger, mlog_level=logger_log_level)
    logger.info("\n")

    #==== START/BIND MQTT FUNCTIONS ====#
    # Create a couple flags to handle a failed attempt at connecting. If user/password is wrong we want to stop the loop.
    mqtt.Client.connected = False             # Flag for initial connection (different than mqtt.Client.is_connected)
    mqtt.Client.failed_connection = False     # Flag for failed initial connection
    # Create our mqtt_client object and bind/link to our callback functions
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID) # Create mqtt_client object
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD) # Need user/password to connect to broker
    mqtt_client.on_connect = on_connect       # Bind on connect
    mqtt_client.on_disconnect = on_disconnect # Bind on disconnect
    mqtt_client.on_message = on_message       # Bind on message
    mqtt_client.on_publish = on_publish       # Bind on publish
    logger.info("Connecting to: {0}".format(MQTT_SERVER))
    mqtt_client.connect(MQTT_SERVER, 1883)    # Connect to mqtt broker. This is a blocking function. Script will stop while connecting.
    mqtt_client.loop_start()                  # Start monitoring loop as asynchronous. Starts a new thread and will process incoming/outgoing messages.
    # Monitor if we're in process of connecting or if the connection failed
    while not mqtt_client.connected and not mqtt_client.failed_connection:
        logger.info("Waiting")
        sleep(1)
    if mqtt_client.failed_connection:         # If connection failed then stop the loop and main program. Use the rc code to trouble shoot
        mqtt_client.loop_stop()
        sys.exit()
    
    #==== MAIN LOOP ====================#
    # MQTT setup is successful. Initialize dictionaries and start the main loop.   
    t0_sec = perf_counter() # sec Counter for getting stepper data. Future feature - update interval in  node-red dashboard to link to perf_counter
    msginterval = 1       # Adjust interval to increase/decrease number of mqtt updates.
    try:
        while True:
            if (perf_counter() - t0_sec) > msginterval: # Get data on a time interval
                for device, ina219 in ina219Set.items():
                    deviceD[device]['data'] = ina219.read()
                    mqtt_client.publish(deviceD[device]['lvl2'].join(MQTT_PUB_TOPIC), json.dumps(deviceD[device]['data']))  # publish voltage values
                t0_sec = perf_counter()
    except KeyboardInterrupt:
        logger.info("Pressed ctrl-C")
    finally:
        logger.info("Exiting")

if __name__ == "__main__":
    main()