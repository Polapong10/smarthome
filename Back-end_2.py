import paho.mqtt.client as mqtt
import time
import json
import threading
client1 = mqtt.Client()
client2 = mqtt.Client()  # Declare client2 as a global variable

def mqtt1():
    global client1  # Reference the global variable
    client1.on_message = on_message
    broker_address = "119.59.99.155"
    broker_port = 8883
    client1.connect(broker_address, broker_port)
    client1.subscribe("smarthome_2/sensor")
    client1.loop_forever()

def mqtt2():
    global client2  # Reference the global variable
    client2.on_message = on_message2
    client2.username_pw_set(username="68ebVYmftKJa21GnUlVw", password=None)
    client2.connect("119.59.99.155", 1883)
    client2.subscribe("v1/devices/me/rpc/request/+")
    client2.loop_forever()

def on_message2(client, userdata, message):
    # print(str(message.payload.decode("utf-8")))
    myPL = str(message.payload.decode("utf-8"))
    data_filter1 = json.loads(myPL)
    data_filter2 = data_filter1["method"]
    if data_filter2 == "fan":
        load_fan = data_filter1["params"]
        data = {"fan": load_fan}
        output = json.dumps(data)
        client1.publish("smarthome_2/fan", output)
        client2.publish("v1/devices/me/telemetry", output)
    elif data_filter2 == "R":
        load_RGB = data_filter1["params"]
        data = {"R": load_RGB}
        output = json.dumps(data)
        client1.publish("smarthome_2/fan", output)
        client2.publish("v1/devices/me/telemetry", output)
    elif data_filter2 == "G":
        load_RGB = data_filter1["params"]
        data = {"G": load_RGB}
        output = json.dumps(data)
        client1.publish("smarthome_2/fan", output)
        client2.publish("v1/devices/me/telemetry", output)
    elif data_filter2 == "B":
        load_RGB = data_filter1["params"]
        data = {"B": load_RGB}
        output = json.dumps(data)
        client1.publish("smarthome_2/fan", output)
        client2.publish("v1/devices/me/telemetry", output)
    elif data_filter2 == "bed":
        sts = data_filter1["params"]
        if sts==True:
            data = {"bed":"ON"}
        elif sts==False:
            data = {"bed":"OFF"}
        output = json.dumps(data)
        client1.publish("smarthome_2/fan", output)
        client2.publish("v1/devices/me/telemetry", output)
    elif data_filter2 == "kitchen":
        sts = data_filter1["params"]
        if sts==True:
            data = {"kitchen":"ON"}
        elif sts==False:
            data = {"kitchen":"OFF"}
        output = json.dumps(data)
        client1.publish("smarthome_2/fan", output)
        client2.publish("v1/devices/me/telemetry", output)
    elif data_filter2 == "liv":
        sts = data_filter1["params"]
        if sts==True:
            data = {"liv":"ON"}
        elif sts==False:
            data = {"liv":"OFF"}
        output = json.dumps(data)
        client1.publish("smarthome_2/fan", output)
        client2.publish("v1/devices/me/telemetry", output)
def on_message(client, userdata, message):
    # print(str(message.payload.decode("utf-8")))
    myPL = str(message.payload.decode("utf-8"))
    data_filter1 = json.loads(myPL)
    load_temp = data_filter1["temp"]
    load_humid = data_filter1["humid"]
    load_co2 = data_filter1["co2"]
    data = {"temp": load_temp, "humid": load_humid, "co2": load_co2}
    output = json.dumps(data)

    # Publish the output to client2
    client2.publish("v1/devices/me/telemetry", output)

# Create threads for each MQTT client
thread1 = threading.Thread(target=mqtt1)
thread2 = threading.Thread(target=mqtt2)

# Start the threads
thread1.start()
thread2.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    # thread1.join()
    thread2.join()
