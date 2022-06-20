print("IoT Gateway")
import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports
import enum
BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
mess = ""

class STATE (enum.Enum):
    IDLE = 0
    SEND_ACK = 1
    SEND_DATA = 2
    WAIT_ACK = 3
    ERROR_LOG = 4

#TODO: Add your token and your comport
#Please check the comport in the device manager
THINGS_BOARD_ACCESS_TOKEN = "BgUXZP1U5v1MJ5krGPCt"


bbc_port = "COM4"
class DATA:
    current_state = STATE.IDLE
    counter_failure = 0
    ack_receive_successful = 0
    MAX = 5
    counter = 0
    time_flag = 0
    mqtt_data_available = 0
    serial_data_available = 0
    cmd = 1

if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)

def processData(data):
    
    print('ack')
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")


    if(len(splitData) == 3):
        if (splitData[1] == 'ACK'): DATA.ack_receive_successful = 1
        else: DATA.serial_data_available = 1
        print(data)
        print(splitData)
        #TODO: Add your source code to publish data to the server
        
        collect_data = {}
        collect_data[splitData[1]] = splitData[2]
        client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    # temp_data = {}
    # # temp_data["method"] = 'get' + splitData[1]
    # temp_data[splitData[1]] = True if splitData[0] == 1 else False
    # client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")

def recv_message(client, userdata, message):
    
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    
    #TODO: Update the cmd to control 2 devices
    # collect_data = {}
    # collect_data['method'] = "setValue"
    # collect_data['params'] = None
    # client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['method'] = 'getLED'
            temp_data['value'] = jsonobj['params']
            if jsonobj['params']:
                DATA.cmd = 0
            else:
                DATA.cmd = 1
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
        if jsonobj['method'] == "setFAN":
            temp_data['method'] = 'getFAN'
            temp_data['value'] = jsonobj['params']
            if jsonobj['params']:
                DATA.cmd = 2
            else:
                DATA.cmd = 3
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
    except:
        pass

    if len(bbc_port) > 0:
        DATA.mqtt_data_available = 1
        print('send')
        
            

def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")

def statemachine ():
    if DATA.current_state == STATE.IDLE:
        print('IDLE')
        if DATA.serial_data_available:
            DATA.current_state = STATE.SEND_ACK
            DATA.serial_data_available = 0
        elif DATA.mqtt_data_available:
            DATA.current_state = STATE.SEND_DATA
            DATA.mqtt_data_available = 0

    elif DATA.current_state == STATE.SEND_ACK:
        print('SEND ACK')
        ser.write(("ACK#").encode())
        DATA.current_state = STATE.IDLE

    elif DATA.current_state == STATE.SEND_DATA:
        print('SEND DATA')
        ser.write((str(DATA.cmd) + "#").encode())
        DATA.current_state = STATE.WAIT_ACK

    elif DATA.current_state == STATE.WAIT_ACK:
        print('WAIT ACK')
        if DATA.counter==2: DATA.time_flag = 1 
        if DATA.ack_receive_successful:
            DATA.current_state = STATE.IDLE
            DATA.counter = 0
        
        elif DATA.counter_failure < DATA.MAX:
            if DATA.time_flag:
                DATA.current_state = STATE.SEND_DATA
                DATA.counter = 0
            
            else: DATA.counter+=1
        elif DATA.counter_failure >= DATA.MAX: 
            DATA.current_state = STATE.ERROR_LOG

    elif DATA.current_state == STATE.ERROR_LOG:
        
        print('ERROR LOG')
        current_state = STATE.IDLE

client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message



while True:

    if len(bbc_port) >  0:
        readSerial()
    statemachine()
    time.sleep(1)